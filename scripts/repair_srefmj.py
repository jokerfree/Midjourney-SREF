"""补齐 sref-midjourney 抓取时因网络波动缺失的页面（可重复执行）。"""
import json
import os
import re
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_srefmj import get, extract, normalize, BASE, OUT


def main():
    with open(OUT, encoding="utf-8") as f:
        raw = json.load(f)
    items = {it["code"]: it for it in raw["items"]}
    total = raw.get("declared_total") or 0
    print(f"现有 {len(items)} / {total}", flush=True)

    pages = 97
    added = 0
    for p in range(1, pages + 1):
        url = BASE + ("/" if p == 1 else f"/{p}")
        try:
            html = get(url, tries=8)
            recs, _ = extract(html)
        except Exception as e:
            print(f"  page {p} 仍失败: {str(e)[:160]}", flush=True)
            continue
        new_here = 0
        for s in recs:
            n = normalize(s)
            if n["code"] and n["code"] not in items:
                items[n["code"]] = n
                new_here += 1
        added += new_here
        if new_here:
            print(f"  page {p}: +{new_here} (总 {len(items)})", flush=True)
        if p % 15 == 0:
            print(f"  ...扫描至 {p}/{pages}，总 {len(items)}", flush=True)

    data = sorted(items.values(), key=lambda x: x["created_at"], reverse=True)
    raw.update(count=len(data), items=data, fetched_at=time.strftime("%Y-%m-%dT%H:%M:%S%z"))
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(raw, f, ensure_ascii=False, indent=1)
    print(f"[done] 补到 {len(data)} 条（新增 {added}）", flush=True)


if __name__ == "__main__":
    main()
