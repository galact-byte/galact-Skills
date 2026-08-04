# -*- coding: utf-8 -*-
"""
LLM 评分运行器（模型无关，OpenAI 兼容 /v1/chat/completions）。

对 pipeline/batches/batch_*.json 逐批调用模型，用 score_prompt.md 作为 system，
批 JSON 作为 user，解析并校验后写入 pipeline/scored/batch_*.json。

特性：
  - 可续跑：已存在且校验通过的批次自动跳过。
  - 逐批校验：输出 id 集合必须与输入完全一致；value_score = 四维之和；字段齐全。
  - 失败重试；重试用尽则把原始响应存 pipeline/failed/ 供排查。

配置（命令行或环境变量）：
  --api-key   / OPENAI_API_KEY
  --base-url  / OPENAI_BASE_URL   (默认 https://api.openai.com/v1)
  --model     / SCORING_MODEL     (默认 gpt-4o-mini，请按需换成更强模型)
用法：
  python run_scoring.py --model gpt-4o [--limit 3] [--temperature 0]
"""
import argparse
import json
import os
import sys
import time
import threading
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor, as_completed

_print_lock = threading.Lock()


def log(msg):
    with _print_lock:
        print(msg, flush=True)


def fmt_dur(sec):
    sec = int(sec)
    if sec < 60:
        return "%ds" % sec
    if sec < 3600:
        return "%dm%02ds" % (sec // 60, sec % 60)
    return "%dh%02dm" % (sec // 3600, (sec % 3600) // 60)


def atomic_write_json(path, obj):
    """先写临时文件再原子替换，避免被 kill 时留下半截文件被误判为已完成。"""
    tmp = "%s.tmp.%d" % (path, os.getpid())
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1)
    os.replace(tmp, path)

REQUIRED_EVAL_FIELDS = {"id", "value_score", "score_breakdown", "verdict",
                        "category", "reasoning", "attack_chain",
                        "bypass_technique", "defensive_insight"}
VERDICTS = {"保留，高优先级", "保留，普通", "丢弃，常见套路", "丢弃，信息不足"}


def load_prompt(path):
    with open(path, encoding="utf-8") as f:
        return f.read()


def call_model(base_url, api_key, model, system, user, temperature, max_tokens,
               disable_thinking=True, timeout=300):
    url = base_url.rstrip("/") + "/chat/completions"
    body = {
        "model": model,
        "temperature": temperature,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "response_format": {"type": "json_object"},
    }
    if disable_thinking:
        # DeepSeek V4 专有：关闭 thinking，避免 reasoning 吃掉 max_tokens 预算
        body["thinking"] = {"type": "disabled"}
    data = json.dumps(body).encode("utf-8")
    req = urllib.request.Request(url, data=data, method="POST")
    req.add_header("Content-Type", "application/json")
    req.add_header("Authorization", "Bearer " + api_key)
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        payload = json.loads(resp.read().decode("utf-8"))
    return payload["choices"][0]["message"]["content"]


def strip_fences(s):
    s = s.strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[1] if "\n" in s else s
        if s.rstrip().endswith("```"):
            s = s.rstrip()[:-3]
    return s.strip()


def normalize_scores(parsed):
    """按 rubric 定义，value_score = 四维之和（四维为权威）。
    模型偶尔心算写错总分，这里自动用四维和覆盖，避免白白重试。
    返回被修正的条数。"""
    fixed = 0
    for e in parsed.get("detailed_evaluations", []):
        b = e.get("score_breakdown")
        if not isinstance(b, dict):
            continue
        try:
            s = int(b["unexpectedness"]) + int(b["elegance"]) + int(b["chain"]) + int(b["reproducibility"])
        except (KeyError, TypeError, ValueError):
            continue
        if e.get("value_score") != s:
            e["value_score"] = s
            fixed += 1
    return fixed


def validate(parsed, input_ids):
    if "detailed_evaluations" not in parsed:
        return "缺少 detailed_evaluations"
    evs = parsed["detailed_evaluations"]
    out_ids = {int(e.get("id")) for e in evs if "id" in e}
    if out_ids != set(input_ids):
        miss = set(input_ids) - out_ids
        extra = out_ids - set(input_ids)
        return "id 集合不匹配 缺失=%s 多余=%s" % (sorted(miss)[:5], sorted(extra)[:5])
    for e in evs:
        missing = REQUIRED_EVAL_FIELDS - set(e)
        if missing:
            return "id=%s 缺字段 %s" % (e.get("id"), missing)
        b = e["score_breakdown"]
        s = b.get("unexpectedness", 0) + b.get("elegance", 0) + b.get("chain", 0) + b.get("reproducibility", 0)
        if e["value_score"] != s:
            return "id=%s value_score(%s)!=四维和(%s)" % (e["id"], e["value_score"], s)
        if e["verdict"] not in VERDICTS:
            return "id=%s 非法 verdict %r" % (e["id"], e["verdict"])
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--api-key", default=os.environ.get("OPENAI_API_KEY", ""))
    ap.add_argument("--base-url", default=os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1"))
    ap.add_argument("--model", default=os.environ.get("SCORING_MODEL", "gpt-4o-mini"))
    ap.add_argument("--prompt", default="score_prompt.md")
    ap.add_argument("--batches", default="batches")
    ap.add_argument("--out", default="scored")
    ap.add_argument("--failed", default="failed")
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--retries", type=int, default=3)
    ap.add_argument("--limit", type=int, default=0, help="仅跑前 N 批(0=全部)，用于试跑")
    ap.add_argument("--sleep", type=float, default=0.0, help="每次请求后 sleep 秒，避免限流")
    ap.add_argument("--shards", type=int, default=1, help="总分片数（多开几个终端就设几）")
    ap.add_argument("--shard", type=int, default=0, help="本进程分片号，0..shards-1")
    ap.add_argument("--concurrency", type=int, default=1, help="单进程内并发请求数")
    ap.add_argument("--max-tokens", type=int, default=8192, help="单次响应最大输出 token（deepseek-v4-flash 上限 384000）")
    ap.add_argument("--enable-thinking", action="store_true", help="开启 v4 thinking（默认关；评分不需要思考，开了会慢且易截断）")
    args = ap.parse_args()

    if not args.api_key:
        sys.exit("缺少 API key：--api-key 或环境变量 OPENAI_API_KEY")
    if not (0 <= args.shard < args.shards):
        sys.exit("--shard 必须在 0..--shards-1 之间")

    system = load_prompt(args.prompt)
    os.makedirs(args.out, exist_ok=True)
    os.makedirs(args.failed, exist_ok=True)

    batch_files = sorted(f for f in os.listdir(args.batches)
                         if f.startswith("batch_") and f.endswith(".json"))
    if args.limit:
        batch_files = batch_files[:args.limit]
    # 分片：按批次序号取模，各进程互不重叠
    batch_files = [bf for i, bf in enumerate(batch_files) if i % args.shards == args.shard]

    total = len(batch_files)
    counters = {"done": 0, "skipped": 0, "failed": 0, "processed": 0}
    clock = threading.Lock()
    t0 = time.time()
    log("[start] 分片 %d/%d 认领 %d 批 | 并发 %d | 模型 %s"
        % (args.shard, args.shards, total, args.concurrency, args.model))

    def progress(tag, bid, extra=""):
        """在锁内调用：打印总进度 + ETA。"""
        p = counters["processed"]
        elapsed = time.time() - t0
        rate = p / elapsed if elapsed > 0 else 0
        eta = (total - p) / rate if rate > 0 else 0
        log("[%s] %s %s | %d/%d %.1f%% (ok=%d skip=%d fail=%d) | 用时 %s 预计剩 %s"
            % (tag, bid, extra, p, total, 100.0 * p / total if total else 100,
               counters["done"], counters["skipped"], counters["failed"],
               fmt_dur(elapsed), fmt_dur(eta)))

    def process_one(bf):
        bid = bf[:-5]
        out_path = os.path.join(args.out, bf)
        if os.path.exists(out_path):
            with clock:
                counters["skipped"] += 1
                counters["processed"] += 1
                progress("SKIP", bid, "(已存在)")
            return
        log("[run ] %s 开始…" % bid)
        t_batch = time.time()
        with open(os.path.join(args.batches, bf), encoding="utf-8") as f:
            batch = json.load(f)
        input_ids = [int(r["id"]) for r in batch["reports"]]
        user = json.dumps(batch, ensure_ascii=False)

        last_raw = ""
        for attempt in range(1, args.retries + 1):
            try:
                content = call_model(args.base_url, args.api_key, args.model,
                                     system, user, args.temperature, args.max_tokens,
                                     disable_thinking=not args.enable_thinking)
                last_raw = content
                parsed = json.loads(strip_fences(content))
                normalize_scores(parsed)  # value_score = 四维和，修正模型心算错
                err = validate(parsed, input_ids)
                if err:
                    raise ValueError(err)
                # 再次检查：可能已被其它分片/进程写好，避免重复覆盖
                if os.path.exists(out_path):
                    with clock:
                        counters["skipped"] += 1
                    return
                atomic_write_json(out_path, parsed)
                with clock:
                    counters["done"] += 1
                    counters["processed"] += 1
                    progress("OK  ", bid, "%d条 用时%s" % (len(input_ids), fmt_dur(time.time() - t_batch)))
                if args.sleep:
                    time.sleep(args.sleep)
                return
            except (urllib.error.URLError, urllib.error.HTTPError) as e:
                log("[NET] %s attempt %d/%d: %s" % (bid, attempt, args.retries, e))
                time.sleep(min(2 ** attempt, 30))
            except Exception as e:
                log("[ERR] %s attempt %d/%d: %s" % (bid, attempt, args.retries, e))
                time.sleep(1)
        with clock:
            counters["failed"] += 1
            counters["processed"] += 1
            progress("FAIL", bid, "-> failed/")
        with open(os.path.join(args.failed, bid + ".raw.txt"), "w", encoding="utf-8") as f:
            f.write(last_raw or "")

    if args.concurrency <= 1:
        for bf in batch_files:
            process_one(bf)
    else:
        with ThreadPoolExecutor(max_workers=args.concurrency) as ex:
            futs = [ex.submit(process_one, bf) for bf in batch_files]
            for _ in as_completed(futs):
                pass

    log("\nDONE[shard %d/%d]. scored=%d skipped=%d failed=%d assigned=%d"
        % (args.shard, args.shards, counters["done"], counters["skipped"],
           counters["failed"], len(batch_files)))

if __name__ == "__main__":
    main()
