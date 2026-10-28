"""抓取 midlibrary.io/sref-codes 的 SREF 风格条目（Next.js flight 数据）。

用法: python fetch_midlibrary.py [--max-pages N] [--workers 3]
输出: sources/midlibrary_raw.json
"""
import argparse
import json
import os
import random
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_srefmj import session, HEADERS  # noqa: E402

import requests  # noqa: E402

BASE = "https://midlibrary.io"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "sources", "midlibrary_raw.json")
TOTAL_PAGES = 97

_local = threading.local()
_lock = threading.Lock()


def get(url, tries=7):
    last = None
    for i in range(tries):
        try:
            if not hasattr(_local, "s"):
                _local.s = requests.Session()
                _local.s.headers.update(HEADERS)
            r = _local.s.get(url, timeout=60)
            if r.status_code == 200 and len(r.text) > 10000:
                return r.text
            last = f"HTTP {r.status_code} len={len(r.text)}"
        except Exception as e:
            last = f"{type(e).__name__}: {str(e)[:140]}"
            _local.s = requests.Session()
            _local.s.headers.update(HEADERS)
        time.sleep(1.2 * (i + 1) + random.random())
    raise RuntimeError(f"FAILED {url}: {last}")


def extract_tiles(html):
    # flight 数据里是转义后的 JSON：\"id\":\"...\"  ->  "id":"..."
    t = html.replace('\\"', '"')
    out = []
    for m in re.finditer(r'\{[^{}]*?"kind":"style_code"[^{}]*?\}', t):
        try:
            obj = json.loads(m.group(0))
        except Exception:
            continue
        out.append(obj)
    return out


def normalize(t):
    pr = t.get("prompt") or ""
    m = re.search(r"--sref\s*(\d{1,12})", pr)
    if not m:
        return None
    code = m.group(1)
    slug = t.get("slug") or ""
    v = re.search(r"--v\s*([\d.]+)", pr)
    return {
        "code": code,
        "title": (t.get("name") or "").strip(),
        "prompt": f"--sref {code}" + (f" --v {v.group(1)}" if v else ""),
        "keywords": [],
        "images": [],
        "sheet_url": ("https://midlibrary.io" + t["sheetUrl"]) if t.get("sheetUrl", "").startswith("/") else t.get("sheetUrl", ""),
        "quadrant": t.get("sheetQuadrant"),
        "mj_version": v.group(1) if v else None,
        "likes": 0,
        "favs": 0,
        "author": "Midlibrary",
        "created_at": "",
        "updated_at": "",
        "source": "midlibrary",
        "source_url": f"https://midlibrary.io/library/{slug}" if slug else BASE,
        "pick": bool(t.get("isPick")),
        "_id": t.get("id"),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-pages", type=int, default=TOTAL_PAGES)
    ap.add_argument("--workers", type=int, default=3)
    args = ap.parse_args()

    records = {}

    def work(p):
        html = get(f"{BASE}/sref-codes?page={p}")
        return p, [normalize(t) for t in extract_tiles(html)]

    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(work, p): p for p in range(1, args.max_pages + 1)}
        done = 0
        for fut in as_completed(futs):
            p = futs[fut]
            try:
                _, items = fut.result()
            except Exception as e:
                print(f"  page {p} 失败: {str(e)[:140]}", flush=True)
                continue
            for n in items:
                if n and n["code"]:
                    records.setdefault(n["code"], n)
            done += 1
            if done % 10 == 0:
                with _lock:
                    print(f"  {done} 页，累计 {len(records)} 条", flush=True)

    data = sorted(records.values(), key=lambda x: x["title"].lower())
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                   "count": len(data), "items": data}, f, ensure_ascii=False, indent=1)
    print(f"[done] {OUT}: {len(data)} 条", flush=True)


if __name__ == "__main__":
    main()
