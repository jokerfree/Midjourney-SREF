"""抓取 Midlibrary 每个风格详情页的 Look terms（Subject / Medium / Genre / Mood ...）。

产物: sources/midlibrary_terms.json  { code: {slug, groups:{label:[[term,count],...]}, obs} }

用法: python fetch_midlibrary_terms.py [--workers 5] [--limit N]
可重复执行：已抓过的 code 会跳过。
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
from bs4 import BeautifulSoup

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
SRC = os.path.join(ROOT, "sources", "midlibrary_raw.json")
OUT = os.path.join(ROOT, "sources", "midlibrary_terms.json")
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/126.0 Safari/537.36")
_local = threading.local()
_lock = threading.Lock()


def session():
    if not hasattr(_local, "s"):
        s = requests.Session()
        s.headers.update({"User-Agent": UA, "Accept-Language": "en-US,en;q=0.9",
                          "Accept-Encoding": "gzip, deflate, br"})
        _local.s = s
    return _local.s


def get(url, tries=4):
    last = None
    for i in range(tries):
        try:
            r = session().get(url, timeout=40)
            if r.status_code == 200 and len(r.text) > 20000:
                return r.text
            last = f"HTTP {r.status_code}"
        except Exception as e:
            last = type(e).__name__
            _local.s = requests.Session()
            _local.s.headers.update({"User-Agent": UA})
        time.sleep(1.0 * (i + 1) + random.random())
    raise RuntimeError(last or "unknown")


def parse(html):
    s = BeautifulSoup(html, "html.parser")
    groups = {}
    for g in s.select(".sp-group"):
        lab = g.select_one(".sp-group-label")
        if not lab:
            continue
        label = lab.get_text(" ", strip=True)
        terms = []
        for a in g.select(".sp-term"):
            spans = a.select("span")
            if not spans:
                continue
            name = spans[0].get_text(" ", strip=True)
            cnt = spans[-1].get_text(" ", strip=True) if len(spans) > 1 else ""
            terms.append([name, cnt])
        if terms:
            groups[label] = terms
    obs = ""
    sec = s.select_one("#sp-observations") or s.select_one("section[id*=observation]")
    if sec:
        p = sec.select_one("p")
        if p:
            obs = p.get_text(" ", strip=True)[:600]
    return groups, obs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=5)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    with open(SRC, encoding="utf-8") as f:
        items = json.load(f)["items"]
    store = {}
    if os.path.exists(OUT):
        with open(OUT, encoding="utf-8") as f:
            store = json.load(f)

    todo = [it for it in items if it["code"] not in store and it.get("source_url")]
    if args.limit:
        todo = todo[: args.limit]
    print(f"待抓取 {len(todo)} 页（已有 {len(store)}）", flush=True)

    def work(it):
        html = get(it["source_url"])
        groups, obs = parse(html)
        return it["code"], {"slug": it["source_url"].rsplit("/", 1)[-1],
                            "groups": groups, "obs": obs}

    ok = fail = 0
    with ThreadPoolExecutor(max_workers=args.workers) as ex:
        futs = {ex.submit(work, it): it for it in todo}
        for i, fut in enumerate(as_completed(futs), 1):
            try:
                code, rec = fut.result()
                store[code] = rec
                ok += 1
            except Exception as e:
                fail += 1
            if i % 100 == 0:
                with _lock:
                    print(f"  {i}/{len(todo)} 成功 {ok} 失败 {fail}", flush=True)
                    with open(OUT, "w", encoding="utf-8") as f:
                        json.dump(store, f, ensure_ascii=False)

    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(store, f, ensure_ascii=False)
    with_terms = sum(1 for v in store.values() if v.get("groups"))
    print(f"[done] 共 {len(store)} 条，其中有 Look terms {with_terms} 条，失败 {fail}", flush=True)


if __name__ == "__main__":
    main()
