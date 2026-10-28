"""为 Midlibrary 条目下载本地缩略图（该站图片有 Referer 防盗链，浏览器无法直接热链）。

用法: python fetch_thumbs.py [--workers 5] [--width 320]
输出: assets/thumbs/<code>.jpg
"""
import argparse
import json
import os
import random
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
SRC = os.path.join(ROOT, "sources", "midlibrary_raw.json")
DEST = os.path.join(ROOT, "assets", "thumbs")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
GRAVITY = {1: "northwest", 2: "northeast", 3: "southwest", 4: "southeast"}
_local = threading.local()


def session():
    if not hasattr(_local, "s"):
        s = requests.Session()
        s.headers.update({"User-Agent": UA, "Referer": "https://midlibrary.io/",
                          "Accept": "image/avif,image/webp,image/jpeg,*/*"})
        _local.s = s
    return _local.s


def crop_url(sheet, quad, width):
    if not sheet:
        return ""
    g = GRAVITY.get(int(quad or 1), "northwest")
    sep = "&" if "?" in sheet else "?"
    return f"{sheet}{sep}crop=720,720&crop_gravity={g}&width={width}"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--width", type=int, default=320)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    with open(SRC, encoding="utf-8") as f:
        items = json.load(f)["items"]
    os.makedirs(DEST, exist_ok=True)

    todo = []
    for it in items:
        code = it["code"]
        path = os.path.join(DEST, f"{code}.jpg")
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            continue
        url = crop_url(it.get("sheet_url"), it.get("quadrant"), args.width)
        if url:
            todo.append((code, url))
    if args.limit:
        todo = todo[: args.limit]
    print(f"待下载 {len(todo)} 张", flush=True)

    def work(item):
        code, url = item
        path = os.path.join(DEST, f"{code}.jpg")
        for i in range(4):
            try:
                r = session().get(url, timeout=45)
                if r.status_code == 200 and len(r.content) > 1000 and \
                        r.headers.get("content-type", "").startswith("image"):
                    tmp = path + ".part"
                    with open(tmp, "wb") as f:
                        f.write(r.content)
                    os.replace(tmp, path)
                    return code, True
            except Exception:
                _local.s = requests.Session()
                _local.s.headers.update({"User-Agent": UA, "Referer": "https://midlibrary.io/"})
            time.sleep(0.8 * (i + 1) + random.random())
        return code, False

    ok = fail = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(work, t) for t in todo]
        for i, fut in enumerate(as_completed(futs), 1):
            _, good = fut.result()
            ok += good
            fail += (not good)
            if i % 100 == 0:
                print(f"  {i}/{len(todo)} 成功 {ok} 失败 {fail}", flush=True)
    print(f"[done] 成功 {ok}，失败 {fail}，目录 {DEST}", flush=True)


if __name__ == "__main__":
    main()
