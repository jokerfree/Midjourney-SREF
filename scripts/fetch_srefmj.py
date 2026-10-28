"""抓取 sref-midjourney.com 的全部 --sref 风格条目（服务端渲染的 Nuxt 页面）。

用法: python fetch_srefmj.py [--max-pages N] [--workers 3]
输出: sources/sref_midjourney_raw.json
"""
import argparse
import json
import math
import os
import random
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

BASE = "https://sref-midjourney.com"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
HEADERS = {"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9"}
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "sources", "sref_midjourney_raw.json")

_local = threading.local()
_print_lock = threading.Lock()


def session():
    if not hasattr(_local, "s"):
        s = requests.Session()
        s.headers.update(HEADERS)
        _local.s = s
    return _local.s


def get(url, tries=7):
    last = None
    for i in range(tries):
        try:
            r = session().get(url, timeout=60)
            if r.status_code == 200 and len(r.text) > 50000:
                return r.text
            last = f"HTTP {r.status_code} len={len(r.text)}"
            if r.status_code in (403, 404, 429):
                time.sleep(5 * (i + 1))
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:140]}"
            try:
                _local.s = requests.Session()
                _local.s.headers.update(HEADERS)
            except Exception:
                pass
        time.sleep(1.2 * (i + 1) + random.random())
    raise RuntimeError(f"FAILED {url}: {last}")


def parse_devalue(payload):
    data = json.loads(payload)

    def hydrate(i):
        v = data[i]
        if isinstance(v, list):
            if v and isinstance(v[0], str) and v[0] in (
                    "ShallowReactive", "Reactive", "Ref", "ShallowRef"):
                return hydrate(v[1])
            return [hydrate(x) if isinstance(x, int) else x for x in v]
        if isinstance(v, dict):
            return {k: (hydrate(x) if isinstance(x, int) else x) for k, x in v.items()}
        return v

    return hydrate(0)


def extract(html):
    m = re.search(r'<script[^>]*id="__NUXT_DATA__"[^>]*>(.*?)</script>', html, re.S)
    if not m:
        return [], 0
    root = parse_devalue(m.group(1))
    best, count = None, 0
    for v in (root.get("data") or {}).values():
        if isinstance(v, dict) and isinstance(v.get("srefs"), list):
            c = v.get("count") or 0
            if isinstance(c, int) and c >= count:
                best, count = v, c
    if not best:
        return [], 0
    return best["srefs"], count


def normalize(s):
    tweets = s.get("tweets") or []
    images, prompts, versions, authors = [], [], set(), set()
    for t in tweets:
        if not isinstance(t, dict):
            continue
        if t.get("styleReferenceVersion"):
            versions.add(t["styleReferenceVersion"])
        a = (t.get("author") or {}).get("fullName")
        if a:
            authors.add(a)
        txt = (t.get("tweetText") or "").strip()
        if txt:
            prompts.append(txt)
        for im in t.get("images") or []:
            u = im.get("url") or im.get("originalUrl")
            if u and u not in images:
                images.append(u)
    kws = s.get("keywords") or {}
    if isinstance(kws, dict):
        def _w(v):
            try:
                return int(v)
            except Exception:
                return 0
        keywords = [k for k, _ in sorted(kws.items(), key=lambda kv: (-_w(kv[1]), kv[0]))]
    elif isinstance(kws, list):
        keywords = [k for k in kws if isinstance(k, str)]
    else:
        keywords = []
    return {
        "code": str(s.get("sref") or "").strip(),
        "title": (s.get("title") or "").strip(),
        "prompt": " || ".join(prompts[:2]),
        "keywords": keywords[:24],
        "images": images[:4],
        "mj_version": sorted(versions)[-1] if versions else None,
        "likes": s.get("nbLikes") or 0,
        "favs": s.get("nbFavs") or 0,
        "author": ", ".join(sorted(authors)) if authors else "",
        "created_at": s.get("createdAt") or "",
        "updated_at": s.get("updatedAt") or "",
        "source": "sref-midjourney",
        "source_url": f"{BASE}/{s.get('sref')}" if s.get("sref") else BASE,
        "_id": s.get("_id"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-pages", type=int, default=0)
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args()

    print("[1/3] 读取第 1 页确定总数 ...", flush=True)
    first_html = get(BASE + "/")
    first, total = extract(first_html)
    per = len(first)
    pages = math.ceil(total / per) if per else 1
    if args.max_pages:
        pages = min(pages, args.max_pages)
    print(f"    总数 {total}，每页约 {per}，共 {pages} 页", flush=True)

    records = {}
    for r in first:
        n = normalize(r)
        if n["code"]:
            records[n["code"]] = n

    # 已经拿到第 1 页的原始 HTML，第 2 页起并发抓取
    def work(p):
        html = get(f"{BASE}/{p}")
        items, _ = extract(html)
        out = []
        for it in items:
            n = normalize(it)
            if n["code"]:
                out.append(n)
        return p, out

    done = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(work, p): p for p in range(2, pages + 1)}
        for fut in as_completed(futs):
            p = futs[fut]
            try:
                _, items = fut.result()
            except Exception as e:
                with _print_lock:
                    print(f"    page {p} 失败: {e}", flush=True)
                continue
            for n in items:
                records.setdefault(n["code"], n)
            done += 1
            if done % 10 == 0:
                with _print_lock:
                    print(f"    进度 {done}/{pages-1} 页，累计 {len(records)} 条", flush=True)

    data = sorted(records.values(), key=lambda x: x["created_at"], reverse=True)
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                   "declared_total": total, "count": len(data), "items": data},
                  f, ensure_ascii=False, indent=1)
    print(f"[done] 写入 {OUT}：{len(data)} 条（站点声明 {total}）", flush=True)


if __name__ == "__main__":
    main()
