# -*- coding: utf-8 -*-
"""hunt-* skill 端到端检测测试编排器。

对每个 skill：起本地脆弱靶标 → 备好 recon 输入 → 跑 hunt_*.py → 跑 validate.sh →
断言"植入的漏洞被检出（或按设计正确地判负/killed）"，最后汇总检测矩阵。

所有 skill 副本与产物写到 tests/e2e/.run/（gitignored），不污染源 skill。
用法: python tests/e2e/run_e2e.py
"""
import json
import os
import shutil
import socket
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(os.path.dirname(HERE))
SKILLS = os.path.join(REPO, "skills")
RUN = os.path.join(HERE, ".run")
SANDBOX = os.path.join(RUN, "_sandbox")
MARKER = os.path.join(RUN, "secret_marker.txt")
PYBIN = sys.executable
os.environ["PYTHONUTF8"] = "1"
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass


def free_port():
    s = socket.socket()
    s.bind(("127.0.0.1", 0))
    p = s.getsockname()[1]
    s.close()
    return p


def wait_ready(port, timeout=10):
    end = time.time() + timeout
    while time.time() < end:
        try:
            with socket.create_connection(("127.0.0.1", port), timeout=0.5):
                return True
        except OSError:
            time.sleep(0.15)
    return False


def prep_skill(name):
    dst = os.path.join(RUN, name)
    if os.path.exists(dst):
        shutil.rmtree(dst, ignore_errors=True)
    shutil.copytree(os.path.join(SKILLS, name), dst,
                    ignore=shutil.ignore_patterns("__pycache__"))
    return dst


def write_json(path, obj):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)


def run(cmd, cwd, timeout=120):
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True,
                       encoding="utf-8", errors="replace",
                       timeout=timeout, env={**os.environ})
    return p.returncode, p.stdout, p.stderr


def load_cands(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def hunt_py(skill_dir, name):
    return [PYBIN, os.path.join(skill_dir, "tools", name)]


# ---- 每个 skill 的端到端用例 ----
def case_ssrf(d, base):
    write_json(os.path.join(d, "recon", "endpoints.json"),
               {"target": base, "endpoints": [
                   {"url": base + "/fetch", "param": "url", "controllable": True}]})
    with open(os.path.join(d, "evidence", "scope.txt"), "w", encoding="utf-8") as f:
        f.write("allow_internal: yes\nallow_metadata: yes\n")
    run(hunt_py(d, "hunt_ssrf.py") + ["--input", "recon/endpoints.json",
        "--output", "candidates.json", "--oast", "oast.invalid"], d)
    c = load_cands(os.path.join(d, "candidates.json"))
    sigs = " ".join(s for cd in c["candidates"] for s in cd.get("signal", []))
    ok = ("差异" in sigs)
    return ok, "SSRF oracle 信号(响应随注入URL变化): %s" % ("命中" if ok else "未见"), c


def case_openredirect(d, base):
    write_json(os.path.join(d, "recon", "endpoints.json"),
               {"target": base, "endpoints": [
                   {"url": base + "/redirect", "param": "url", "controllable": True}]})
    run(hunt_py(d, "hunt_openredirect.py") + ["--input", "recon/endpoints.json",
        "--output", "candidates.json", "--marker", "evil.example"], d)
    c = load_cands(os.path.join(d, "candidates.json"))
    n = sum(1 for cd in c["candidates"] if cd.get("suspected"))
    return n > 0, "跳向 marker 的变体数=%d" % n, c


def case_pathtrav(d, base):
    write_json(os.path.join(d, "recon", "endpoints.json"),
               {"target": base, "endpoints": [
                   {"url": base + "/download", "param": "file", "controllable": True}]})
    run(hunt_py(d, "hunt_pathtrav.py") + ["--input", "recon/endpoints.json",
        "--output", "candidates.json"], d)
    c = load_cands(os.path.join(d, "candidates.json"))
    hits = [cd["family"] for cd in c["candidates"] if cd.get("suspected")]
    return len(hits) > 0, "读到越权文件指纹的变体=%s" % hits, c


def case_sqli(d, base):
    write_json(os.path.join(d, "recon", "endpoints.json"),
               {"target": base, "endpoints": [
                   {"url": base + "/item", "param": "id", "controllable": True}]})
    run(hunt_py(d, "hunt_sqli.py") + ["--input", "recon/endpoints.json",
        "--output", "candidates.json", "--delay", "3", "--repeat", "1"], d)
    c = load_cands(os.path.join(d, "candidates.json"))
    kinds = [cd.get("kind") for cd in c["candidates"] if cd.get("suspected")]
    return any(kinds), "检出注入类型=%s" % kinds, c


def case_xss(d, base):
    write_json(os.path.join(d, "recon", "endpoints.json"),
               {"target": base, "endpoints": [
                   {"url": base + "/search", "param": "q", "controllable": True}]})
    run(hunt_py(d, "hunt_xss.py") + ["--input", "recon/endpoints.json",
        "--output", "candidates.json"], d)
    c = load_cands(os.path.join(d, "candidates.json"))
    n = sum(1 for cd in c["candidates"] if cd.get("suspected"))
    ctx = [cd.get("context") for cd in c["candidates"] if cd.get("suspected")]
    return n > 0, "疑似可执行反射=%d 上下文=%s" % (n, ctx), c


def case_cache(d, base):
    run(hunt_py(d, "hunt_cache.py") + ["--target", base + "/page",
        "--output", "candidates.json"], d)
    c = load_cands(os.path.join(d, "candidates.json"))
    n = sum(1 for cd in c["candidates"] if cd.get("suspected"))
    return n > 0, "确认被缓存的投毒 header 数=%d" % n, c


def case_csrf(d, base):
    write_json(os.path.join(d, "recon", "endpoints.json"),
               {"target": base + "/account", "forms": 1, "endpoints": []})
    run(hunt_py(d, "hunt_csrf.py") + ["--input", "recon/endpoints.json",
        "--output", "candidates.json"], d)
    c = load_cands(os.path.join(d, "candidates.json"))
    susp = [cd for cd in c["candidates"] if cd.get("suspected")]
    return len(susp) > 0, "防护画像疑似缺陷=%s" % (susp[0]["signal"] if susp else "无"), c


def case_cmdi(d, base):
    write_json(os.path.join(d, "recon", "endpoints.json"),
               {"target": base, "endpoints": [
                   {"url": base + "/ping", "param": "host", "controllable": True}]})
    run(hunt_py(d, "hunt_cmdi.py") + ["--input", "recon/endpoints.json",
        "--output", "candidates.json", "--oast", "oast.invalid",
        "--delay", "3", "--repeat", "1"], d, timeout=180)
    c = load_cands(os.path.join(d, "candidates.json"))
    hits = [cd["family"] for cd in c["candidates"] if cd.get("suspected")]
    return len(hits) > 0, "时序盲注命中族=%s" % hits, c


def case_xxe(d, base):
    write_json(os.path.join(d, "recon", "endpoints.json"),
               {"target": base + "/xml", "endpoints": [
                   {"url": base + "/xml", "controllable": True}]})
    run(hunt_py(d, "hunt_xxe.py") + ["--input", "recon/endpoints.json",
        "--output", "candidates.json", "--oast", "oast.invalid"], d)
    c = load_cands(os.path.join(d, "candidates.json"))
    hits = [cd["family"] for cd in c["candidates"] if cd.get("suspected")]
    return "internal-entity" in hits, "确认实体解析的族=%s" % hits, c


def case_protopollution(d, ppbase):
    write_json(os.path.join(d, "recon", "endpoints.json"),
               {"target": ppbase, "endpoints": [
                   {"url": ppbase + "/", "controllable": True}]})
    run(hunt_py(d, "hunt_protopollution.py") + ["--input", "recon/endpoints.json",
        "--output", "candidates.json", "--probe-url", ppbase + "/"], d)
    c = load_cands(os.path.join(d, "candidates.json"))
    hits = [cd["family"] for cd in c["candidates"] if cd.get("suspected")]
    return len(hits) > 0, "探针属性被反射的向量=%s" % hits, c


def case_authbypass(d, base):
    write_json(os.path.join(d, "recon", "endpoints.json"),
               {"target": base + "/authorize", "endpoints": [
                   {"url": base + "/authorize", "param": "redirect_uri"},
                   {"url": base + "/authorize", "param": "response_type"},
                   {"url": base + "/authorize", "param": "client_id"}]})
    run(hunt_py(d, "hunt_authbypass.py") + ["--input", "recon/endpoints.json",
        "--output", "candidates.json"], d)
    c = load_cands(os.path.join(d, "candidates.json"))
    mechs = c.get("mechanisms", [])
    ok = "oauth" in mechs and len(c["candidates"]) > 0
    return ok, "识别机制=%s 待验证项=%d" % (mechs, len(c["candidates"])), c


def case_deser(d, base):
    write_json(os.path.join(d, "recon", "endpoints.json"),
               {"target": base, "endpoints": [
                   {"url": base + "/app", "param": "session",
                    "sample": 'O:8:"stdClass":1:{s:3:"foo";s:3:"bar";}'},
                   {"url": base + "/app", "param": "state", "sample": "rO0ABXNyABQ="}]})
    run(hunt_py(d, "hunt_deser.py") + ["--input", "recon/endpoints.json",
        "--output", "candidates.json"], d)
    c = load_cands(os.path.join(d, "candidates.json"))
    fmts = [cd["format"] for cd in c["candidates"] if cd.get("suspected")]
    return len(fmts) >= 2, "格式指纹命中=%s" % fmts, c


def case_smuggling(d, base):
    # stdlib 单体服务不该被 desync；正确结果是"无假阳性"
    run(hunt_py(d, "hunt_smuggling.py") + ["--target", base + "/",
        "--output", "candidates.json", "--timeout", "3", "--repeat", "2"], d, timeout=120)
    c = load_cands(os.path.join(d, "candidates.json"))
    fp = sum(1 for cd in c["candidates"] if cd.get("suspected_desync"))
    ran = len(c["candidates"]) > 0
    return ran and fp == 0, "流水线执行且无假阳性 desync (假阳性=%d)" % fp, c


def case_nodeperm(d, base):
    write_json(os.path.join(d, "recon", "node_env.json"),
               {"node_version": "v24", "permission_new_flag": "yes"})
    run(hunt_py(d, "hunt_nodeperm.py") + ["--restricted", MARKER,
        "--output", "candidates.json", "--node", "node", "--allow-dir", d], d, timeout=120)
    c = load_cands(os.path.join(d, "candidates.json"))
    ran = len(c["candidates"]) > 0
    content_leak = sum(1 for cd in c["candidates"]
                       if cd.get("kind") == "read" and cd.get("leaked"))
    meta_leak = sum(1 for cd in c["candidates"]
                    if cd.get("kind") == "meta" and cd.get("suspected"))
    blocked = sum(1 for cd in c["candidates"] if cd.get("blocked"))
    # 安全意义的通过标准：矩阵跑完且无“白名单外文件内容”还原型逃逸
    ok = ran and content_leak == 0
    return ok, "矩阵已跑(内容逃逸=%d 元数据泄露statfs=%d 被拦=%d/%d)" % (
        content_leak, meta_leak, blocked, len(c["candidates"])), c


CASES = [
    ("hunt-ssrf", "hunt_ssrf.py", case_ssrf, "web"),
    ("hunt-open-redirect", "hunt_openredirect.py", case_openredirect, "web"),
    ("hunt-path-traversal", "hunt_pathtrav.py", case_pathtrav, "web"),
    ("hunt-sqli", "hunt_sqli.py", case_sqli, "web"),
    ("hunt-xss", "hunt_xss.py", case_xss, "web"),
    ("hunt-cache-poisoning", "hunt_cache.py", case_cache, "web"),
    ("hunt-csrf", "hunt_csrf.py", case_csrf, "web"),
    ("hunt-command-injection", "hunt_cmdi.py", case_cmdi, "web"),
    ("hunt-xxe", "hunt_xxe.py", case_xxe, "web"),
    ("hunt-prototype-pollution", "hunt_protopollution.py", case_protopollution, "node"),
    ("hunt-auth-bypass", "hunt_authbypass.py", case_authbypass, "heuristic"),
    ("hunt-deserialization", "hunt_deser.py", case_deser, "heuristic"),
    ("hunt-request-smuggling", "hunt_smuggling.py", case_smuggling, "negative"),
    ("hunt-nodejs-permission-bypass", "hunt_nodeperm.py", case_nodeperm, "runtime"),
]


def main():
    os.makedirs(RUN, exist_ok=True)
    with open(MARKER, "w", encoding="utf-8") as f:
        f.write("RESTRICTED_SECRET_9f3a2b_do_not_leak\n")

    vport, ppport = free_port(), free_port()
    base = "http://127.0.0.1:%d" % vport
    ppbase = "http://127.0.0.1:%d" % ppport

    servers = []
    vlog = open(os.path.join(RUN, "vuln_server.log"), "w")
    servers.append(subprocess.Popen([PYBIN, os.path.join(HERE, "vuln_server.py"),
                                     str(vport), SANDBOX], stdout=vlog, stderr=vlog))
    have_node = shutil.which("node") is not None
    if have_node:
        pplog = open(os.path.join(RUN, "pp_app.log"), "w")
        servers.append(subprocess.Popen(["node", os.path.join(HERE, "pp_app.js"),
                                         str(ppport)], stdout=pplog, stderr=pplog))

    try:
        if not wait_ready(vport):
            print("!! 靶标启动失败"); return 2
        if have_node and not wait_ready(ppport):
            print("!! node 靶标启动失败"); have_node = False

        rows = []
        for name, script, fn, kind in CASES:
            if kind == "node" and not have_node:
                rows.append((name, "SKIP", "无 node，跳过", kind)); continue
            if kind == "runtime" and not have_node:
                rows.append((name, "SKIP", "无 node，跳过", kind)); continue
            d = prep_skill(name)
            try:
                target = ppbase if kind == "node" else base
                ok, detail, _ = fn(d, target)
                rows.append((name, "PASS" if ok else "FAIL", detail, kind))
            except Exception as e:
                rows.append((name, "ERROR", "%s: %s" % (type(e).__name__, e), kind))

        print("\n" + "=" * 72)
        print("端到端检测矩阵（靶标 %s）" % base)
        print("=" * 72)
        kindmap = {"web": "真实漏洞检出", "node": "真实漏洞检出",
                   "heuristic": "启发式识别", "negative": "正确判负",
                   "runtime": "运行时矩阵"}
        npass = sum(1 for r in rows if r[1] == "PASS")
        for name, status, detail, kind in rows:
            mark = {"PASS": "✓", "FAIL": "✗", "SKIP": "-", "ERROR": "!"}[status]
            print("%s %-30s [%s] %s" % (mark, name, kindmap.get(kind, kind), detail))
        print("=" * 72)
        print("通过 %d / %d（recognize-attack-surface 为路由 skill，非流水线，见静态测试）"
              % (npass, len(rows)))
        print("=" * 72)
        return 0 if npass == len([r for r in rows if r[1] != "SKIP"]) else 1
    finally:
        for s in servers:
            s.terminate()
        for s in servers:
            try:
                s.wait(timeout=5)
            except Exception:
                s.kill()


if __name__ == "__main__":
    sys.exit(main())
