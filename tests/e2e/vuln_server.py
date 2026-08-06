# -*- coding: utf-8 -*-
"""本地脆弱靶标 —— 仅供 hunt-* skill 端到端自测，绑定 127.0.0.1。

每个端点故意植入一类可被对应 hunt skill 客观信号检出的漏洞，且都做了安全约束：
  - 只监听 loopback；
  - SSRF 出站 2s 超时、仅 http/https；
  - 命令注入是"受控延时模拟"，绝不执行攻击者输入（只按 sleep N 语义 sleep）；
  - 路径穿越读取限定在启动时构造的 sandbox 目录内。
用法: python vuln_server.py <port> <sandbox_dir>
"""
import os
import sys
import time
import sqlite3
import threading
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs, unquote

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 8799
SANDBOX = os.path.abspath(sys.argv[2]) if len(sys.argv) > 2 else os.path.abspath("./.sandbox")
WEBROOT = os.path.join(SANDBOX, *(["d%d" % i for i in range(8)]), "webroot")

# path-traversal 植入：默认 payload "../"*8 + "etc/passwd" 从 WEBROOT 精确解析到的位置
# （随嵌套深度自动对齐，避免手算差一层）
PLANTED_PASSWD = os.path.normpath(os.path.join(WEBROOT, *([".."] * 8), "etc", "passwd"))

# 简易 path-keyed 缓存（cache-poisoning 用）：key=path+query，命中返回缓存体 + X-Cache: HIT
_CACHE = {}
_CACHE_LOCK = threading.Lock()

# sqli 用内存库
def _make_db():
    con = sqlite3.connect(":memory:", check_same_thread=False)
    con.execute("CREATE TABLE items(id TEXT, name TEXT)")
    con.execute("INSERT INTO items VALUES('1', 'Premium Widget — long product description used as boolean oracle payload')")
    con.execute("INSERT INTO items VALUES('2', 'Gadget')")
    con.commit()
    return con

_DB = _make_db()
_DB_LOCK = threading.Lock()

XSS_MARK_CTX = "<h1>results</h1>"


def _plant_files():
    os.makedirs(os.path.dirname(PLANTED_PASSWD), exist_ok=True)
    with open(PLANTED_PASSWD, "w", encoding="utf-8") as f:
        f.write("root:x:0:0:root:/root:/bin/bash\ndaemon:x:1:1:daemon:/usr/sbin:/usr/sbin/nologin\n")
    os.makedirs(WEBROOT, exist_ok=True)
    with open(os.path.join(WEBROOT, "index.txt"), "w", encoding="utf-8") as f:
        f.write("public webroot file\n")


INDEX = """<!doctype html><html><head><title>vuln target</title></head><body>
<h1>test target</h1>
<form action="/search" method="get"><input name="q"></form>
<form action="/account" method="post"><input name="email"><input type="submit"></form>
<a href="/fetch?url=http://example.com/">url preview</a>
<a href="/redirect?next=/home">redirect</a>
<a href="/download?file=index.txt">download file</a>
<a href="/item?id=1">item</a>
<a href="/ping?host=127.0.0.1">ping host</a>
<a href="/page">cacheable page</a>
</body></html>"""


class H(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"
    # 读操作 0.5s 超时：健壮服务不会因 undersized/畸形 body 而长时间挂起；
    # 快速失败才能给 hunt-request-smuggling 一个干净的真阴性（无假阳性 desync）。
    timeout = 0.5

    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="text/html; charset=utf-8", extra=None):
        if isinstance(body, str):
            body = body.encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if self.command != "HEAD":
            self.wfile.write(body)

    # ---- SSRF: 服务端按用户 url 发出站请求，响应随目标 URL 变化（真实 SSRF oracle）----
    def _h_fetch(self, qs):
        url = (qs.get("url") or qs.get("uri") or qs.get("target") or [""])[0]
        if not url:
            return self._send(400, "missing url")
        pu = urlparse(url)
        if pu.scheme not in ("http", "https"):
            return self._send(200, "ERR unsupported scheme for %s" % url)
        try:
            with urllib.request.urlopen(url, timeout=2) as r:
                data = r.read(4096)
            return self._send(200, "OK fetched %s bytes=%d head=%s" % (url, len(data), data[:80]))
        except Exception as e:
            return self._send(200, "ERR fetch %s failed: %s" % (url, type(e).__name__))

    # ---- open redirect: 原样把参数值放进 Location ----
    def _h_redirect(self, qs):
        dest = (qs.get("url") or qs.get("next") or qs.get("redirect") or ["/"])[0]
        return self._send(302, "redirecting to %s" % dest, extra={"Location": dest})

    # ---- path traversal: 未净化拼接读取 ----
    def _h_download(self, qs):
        rel = (qs.get("file") or qs.get("path") or [""])[0]
        rel = unquote(rel)
        target = os.path.normpath(os.path.join(WEBROOT, rel))
        try:
            with open(target, "rb") as f:
                return self._send(200, f.read(), ctype="application/octet-stream")
        except Exception as e:
            return self._send(404, "not found: %s (%s)" % (rel, type(e).__name__))

    # ---- SQLi: 字符串拼接进 SQL；报错泄露 + 布尔可控 ----
    def _h_item(self, qs):
        idv = (qs.get("id") or [""])[0]
        sql = "SELECT name FROM items WHERE id = '%s'" % idv
        try:
            with _DB_LOCK:
                rows = _DB.execute(sql).fetchall()
            body = "<h1>item</h1>" + "".join("<p>%s</p>" % r[0] for r in rows)
            return self._send(200, body)
        except sqlite3.Error as e:
            # 冗余报错页：带 SQLSTATE 签名（被 hunt-sqli 的错误签名正则命中）
            return self._send(500, "SQLSTATE[HY000] SQLite error in query: %s" % e)

    # ---- reflected XSS: 原样回显到 HTML body ----
    def _h_search(self, qs):
        q = (qs.get("q") or qs.get("search") or [""])[0]
        return self._send(200, "%s<div>you searched for: %s</div>" % (XSS_MARK_CTX, q))

    # ---- command injection（受控延时模拟，绝不执行输入）----
    def _h_ping(self, qs):
        host = (qs.get("host") or qs.get("cmd") or [""])[0]
        host = unquote(host)
        delay = _parse_injected_sleep(host)
        if delay:
            time.sleep(min(delay, 12))
        return self._send(200, "PING %s: 56 data bytes" % host.split(";")[0].split("|")[0])

    # ---- cache poisoning: 反射 unkeyed X-Forwarded-Host + path-keyed 缓存 ----
    def _h_page(self, path_qs):
        key = path_qs
        xfh = self.headers.get("X-Forwarded-Host") or self.headers.get("X-Host") \
            or self.headers.get("X-Forwarded-Server") or ""
        with _CACHE_LOCK:
            if key in _CACHE:
                return self._send(200, _CACHE[key], extra={"X-Cache": "HIT"})
            body = "<link rel=canonical href=//%s/><h1>page</h1>" % xfh
            _CACHE[key] = body
        return self._send(200, body, extra={"X-Cache": "MISS"})

    # ---- CSRF: 状态变更表单页，会话 cookie 无 SameSite，无 token ----
    def _h_account(self):
        body = ("<h1>account</h1><form method=post action=/account>"
                "<input name=email><input type=submit></form>")
        return self._send(200, body, extra={"Set-Cookie": "sid=abc123; Path=/; HttpOnly"})

    # ---- XXE: 解析 XML 并回显（展开内部实体）----
    def _h_xml(self):
        n = int(self.headers.get("Content-Length") or 0)
        raw = self.rfile.read(n).decode("utf-8", "replace") if n else ""
        try:
            from xml.dom.minidom import parseString
            dom = parseString(raw)
            text = "".join(t.data for t in _iter_text(dom))
            return self._send(200, "<result>%s</result>" % text)
        except Exception as e:
            return self._send(200, "<error>%s</error>" % type(e).__name__)

    def do_GET(self):
        pu = urlparse(self.path)
        qs = parse_qs(pu.query)
        p = pu.path
        if p == "/":
            return self._send(200, INDEX)
        if p == "/fetch":
            return self._h_fetch(qs)
        if p == "/redirect":
            return self._h_redirect(qs)
        if p == "/download":
            return self._h_download(qs)
        if p == "/item":
            return self._h_item(qs)
        if p == "/search":
            return self._h_search(qs)
        if p == "/ping":
            return self._h_ping(qs)
        if p == "/page":
            return self._h_page(self.path)
        if p == "/account":
            return self._h_account()
        return self._send(404, "no route")

    def do_POST(self):
        pu = urlparse(self.path)
        if pu.path == "/xml":
            return self._h_xml()
        if pu.path == "/account":
            return self._send(200, "account updated")
        n = int(self.headers.get("Content-Length") or 0)
        if n:
            self.rfile.read(n)
        return self._send(404, "no route")


def _iter_text(node):
    from xml.dom.minidom import Node
    if node.nodeType == Node.TEXT_NODE:
        yield node
    for c in getattr(node, "childNodes", []):
        yield from _iter_text(c)


def _parse_injected_sleep(s):
    """仅识别注入串里的 sleep N / ping -c N 语义并返回秒数；不执行任何命令。"""
    import re
    if not re.search(r"[;|&`]|\$\(", s):
        return 0
    m = re.search(r"sleep\s+(\d+)", s)
    if m:
        return int(m.group(1))
    m = re.search(r"ping\s+-c\s+(\d+)", s)
    if m:
        return int(m.group(1))
    return 0


def main():
    _plant_files()
    srv = ThreadingHTTPServer(("127.0.0.1", PORT), H)
    print("vuln target on http://127.0.0.1:%d  sandbox=%s" % (PORT, SANDBOX), flush=True)
    srv.serve_forever()


if __name__ == "__main__":
    main()
