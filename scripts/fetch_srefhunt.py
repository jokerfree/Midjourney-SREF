"""抓取 srefhunt.com 的 SREF 条目（约 280 条，含风格标签与精选描述）。

输出: sources/srefhunt_raw.json
"""
import json
import os
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fetch_srefmj import get  # noqa: E402

from bs4 import BeautifulSoup  # noqa: E402

BASE = "https://srefhunt.com"
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "sources", "srefhunt_raw.json")


def listing_urls():
    xml = get(BASE + "/hp_listing-sitemap.xml", tries=8)
    locs = re.findall(r"<loc>(.*?)</loc>", xml)
    return [u for u in locs if "/prompt/" in u and u.rstrip("/") != BASE + "/prompt"]


def parse(url):
    html = get(url, tries=8)
    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.select_one("h1")
    title = h1.get_text(" ", strip=True) if h1 else ""
    title = re.sub(r"\s*SREF Code\s*$", "", title, flags=re.I).strip()
    if not title:
        return None
    text = soup.get_text(" ", strip=True)
    m = re.search(r"--sref\s*(\d{1,12})", text)
    if not m:
        return None
    code = m.group(1)
    og = soup.find("meta", attrs={"property": "og:image"})
    img = og.get("content") if og else ""
    tags = []
    for a in soup.select('a[href*="/style/"]'):
        t = a.get_text(" ", strip=True)
        if t and t not in tags:
            tags.append(t)
    desc = soup.find("meta", attrs={"property": "og:description"})
    desc = desc.get("content") if desc else ""
    prompt = ""
    for p in soup.select("p"):
        pt = p.get_text(" ", strip=True)
        if pt and "--sref" in pt and len(pt) < 1200:
            prompt = pt
            break
    date = ""
    for t in soup.select("time"):
        dt = t.get("datetime") or t.get_text(strip=True)
        if "Added on" in (t.get_text(strip=True) or ""):
            date = dt
            break
    return {
        "code": code,
        "title": title,
        "prompt": prompt,
        "keywords": tags[:12],
        "images": [img] if img else [],
        "mj_version": None,
        "likes": 0,
        "favs": 0,
        "author": "",
        "created_at": date,
        "updated_at": "",
        "source": "srefhunt",
        "source_url": url,
        "category_hint": tags[0] if tags else "",
        "desc": desc,
    }


def main():
    urls = listing_urls()
    print(f"发现 {len(urls)} 个条目页", flush=True)
    records = {}

    def work(u):
        return u, parse(u)

    with ThreadPoolExecutor(max_workers=3) as ex:
        futs = {ex.submit(work, u): u for u in urls}
        done = 0
        for fut in as_completed(futs):
            u = futs[fut]
            try:
                _, n = fut.result()
            except Exception as e:
                print(f"  失败 {u}: {str(e)[:120]}", flush=True)
                continue
            if n:
                records.setdefault(n["code"], n)
            done += 1
            if done % 50 == 0:
                print(f"  {done}/{len(urls)}，累计 {len(records)}", flush=True)

    data = sorted(records.values(), key=lambda x: x["title"].lower())
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump({"fetched_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
                   "count": len(data), "items": data}, f, ensure_ascii=False, indent=1)
    print(f"[done] {OUT}: {len(data)} 条", flush=True)


if __name__ == "__main__":
    main()
