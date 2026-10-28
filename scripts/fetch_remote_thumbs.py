"""下载剩余远程缩略图并压缩到本地，实现完全离线浏览。

- 读取 data/srefs.json，对没有本地缩略图的条目下载第一张预览图
- 统一缩放为 320px 宽的 JPEG（质量 80），存到 assets/thumbs/<code>.jpg
- 可重复执行，已存在的会跳过

用法: python fetch_remote_thumbs.py [--workers 6] [--limit N]
"""
import argparse
import io
import json
import os
import random
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

import requests
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data", "srefs.json")
DEST = os.path.join(ROOT, "assets", "thumbs")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
_local = threading.local()
_lock = threading.Lock()


def session():
    if not hasattr(_local, "s"):
        s = requests.Session()
        s.headers.update({"User-Agent": UA, "Accept": "image/avif,image/webp,image/*,*/*"})
        _local.s = s
    return _local.s


def fetch_image(url, tries=4):
    last = None
    for i in range(tries):
        try:
            r = session().get(url, timeout=40)
            if r.status_code == 200 and len(r.content) > 800:
                return r.content
            last = f"HTTP {r.status_code}"
        except Exception as e:
            last = f"{type(e).__name__}"
            _local.s = requests.Session()
            _local.s.headers.update({"User-Agent": UA})
        time.sleep(0.6 * (i + 1) + random.random() * 0.4)
    raise RuntimeError(last or "unknown")


def save_thumb(raw, path, width, quality):
    im = Image.open(io.BytesIO(raw))
    im.load()
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGB")
    elif im.mode != "RGB":
        im = im.convert("RGB")
    if im.width > width:
        h = max(1, round(im.height * width / im.width))
        im = im.resize((width, h), Image.LANCZOS)
    tmp = path + ".part"
    im.save(tmp, "JPEG", quality=quality, optimize=True, progressive=True)
    os.replace(tmp, path)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--width", type=int, default=320)
    ap.add_argument("--quality", type=int, default=80)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    with open(DATA, encoding="utf-8") as f:
        items = json.load(f)["items"]
    os.makedirs(DEST, exist_ok=True)

    todo = []
    for it in items:
        path = os.path.join(DEST, f"{it['code']}.jpg")
        if os.path.exists(path) and os.path.getsize(path) > 1000:
            continue
        if it.get("images"):
            todo.append((it["code"], it["images"][0]))
    if args.limit:
        todo = todo[: args.limit]
    print(f"待下载 {len(todo)} 张", flush=True)

    def work(item):
        code, url = item
        path = os.path.join(DEST, f"{code}.jpg")
        try:
            raw = fetch_image(url)
            save_thumb(raw, path, args.width, args.quality)
            return code, True, os.path.getsize(path)
        except Exception as e:
            return code, False, str(e)[:60]

    ok = fail = 0
    total_bytes = 0
    failures = []
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = [ex.submit(work, t) for t in todo]
        for i, fut in enumerate(as_completed(futs), 1):
            code, good, info = fut.result()
            if good:
                ok += 1
                total_bytes += info
            else:
                fail += 1
                failures.append((code, info))
            if i % 200 == 0:
                with _lock:
                    print(f"  {i}/{len(todo)} 成功 {ok} 失败 {fail}", flush=True)

    print(f"[done] 成功 {ok} 张（{total_bytes/1024/1024:.1f} MB），失败 {fail} 张", flush=True)
    if failures:
        with open(os.path.join(ROOT, "data", "thumb_failures.json"), "w", encoding="utf-8") as f:
            json.dump(failures, f, ensure_ascii=False, indent=1)
        print(f"失败清单: data/thumb_failures.json", flush=True)


if __name__ == "__main__":
    main()
