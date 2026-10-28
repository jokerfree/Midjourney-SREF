"""合并各来源，生成资料库数据（JSON / CSV / JS）与更新报告。

用法: python build_library.py [--report]
"""
import argparse
import csv
import json
import os
import re
import sys
import time
from collections import Counter, defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
sys.path.insert(0, HERE)
from taxonomy import CATEGORIES, ZH_TERMS, GENERIC  # noqa: E402
from look_terms import probe_category, probe_tags, flat_terms  # noqa: E402

SRC = os.path.join(ROOT, "sources")
DATA = os.path.join(ROOT, "data")
TODAY = time.strftime("%Y-%m-%d")


def load(name):
    p = os.path.join(SRC, name)
    if not os.path.exists(p):
        return []
    with open(p, encoding="utf-8") as f:
        return json.load(f).get("items", [])


def word_in(kw, text):
    if not kw or not text:
        return 0
    if re.search(r"[a-z0-9]", kw[0]) and re.search(r"[a-z0-9]", kw[-1]):
        return 1 if re.search(r"(?<![a-z0-9])" + re.escape(kw) + r"(?![a-z0-9])", text) else 0
    return 1 if kw in text else 0


def build_weights(items):
    """关键词的 IDF 权重：越常见的词区分度越低（如 ethereal / dreamlike）。"""
    import math
    df = Counter()
    n = 0
    for it in items:
        n += 1
        seen = {k.strip().lower() for k in (it.get("keywords") or [])}
        for k in seen:
            df[k] += 1
    max_w = math.log(1 + n / 2)
    w = {k: math.log(1 + n / (1 + c)) for k, c in df.items()}
    return w, max_w


# 媒介/题材类优先于情绪类
TIER1 = {"portrait", "anime", "illustration", "painting", "watercolor", "sketch", "3d",
         "photography", "comic", "graphic", "architecture", "fashion", "product",
         "character", "nature", "texture", "collage", "ethnic", "cyberpunk", "fantasy",
         "dark", "cute"}


def classify(it, weights, max_w):
    title = (it.get("title") or "").lower()
    prompt = (it.get("prompt") or "").lower()
    kwset = {k.lower() for k in (it.get("keywords") or [])}
    scores = {}
    for cat in CATEGORIES:
        s = 0.0
        for kw in cat["kw"]:
            k = kw.lower()
            wt = weights.get(k, max_w)
            if k in kwset:
                s += 2 * wt
            if word_in(k, title):
                s += 3 * wt
            if word_in(k, prompt):
                s += 1 * wt
        scores[cat["id"]] = s
    best = max(scores, key=scores.get)
    t1 = {k: v for k, v in scores.items() if k in TIER1}
    best_t1 = max(t1, key=t1.get) if t1 else None
    if scores[best] < 1.2:
        srcs = it.get("sources") or [it.get("source")]
        return "midlibrary" if "midlibrary" in srcs else "other"
    # 题材/媒介信号足够强时优先，情绪类只在缺乏题材信号时兜底
    if best_t1 and t1[best_t1] >= 3.0 and t1[best_t1] >= scores[best] * 0.55:
        return best_t1
    return best


def make_tags(it, cat_id):
    tags = []
    for k in (it.get("keywords") or []):
        kk = k.strip().lower()
        if kk in GENERIC:
            continue
        zh = ZH_TERMS.get(kk)
        if zh and zh not in tags:
            tags.append(zh)
        if len(tags) >= 5:
            break
    if not tags:
        # 从标题里找已知术语
        t = (it.get("title") or "").lower()
        for en, zh in ZH_TERMS.items():
            if word_in(en, t) and zh not in tags:
                tags.append(zh)
            if len(tags) >= 3:
                break
    if cat_id == "midlibrary" and not tags:
        tags = ["Midlibrary 精选"]
    return tags[:5]


def slug_ok(code):
    return bool(re.fullmatch(r"\d{1,12}", code or ""))


# ---------------- 去重（视觉近重复 + 标题相似） ----------------

_STOP = {"the", "a", "an", "in", "of", "with", "and", "to", "for", "on", "at", "by",
         "style", "art", "artistic", "vibe", "vibes"}


def _tokens(t):
    return {w for w in re.findall(r"[a-z0-9]+", (t or "").lower())
            if len(w) > 2 and w not in _STOP}


def _jaccard(a, b):
    if not a or not b:
        return 0.0
    return len(a & b) / len(a | b)


def _dhash(path):
    from PIL import Image
    im = Image.open(path).convert("L").resize((9, 8), Image.LANCZOS)
    px = list(im.getdata())
    h = 0
    for r in range(8):
        for c in range(8):
            h = (h << 1) | (1 if px[r * 9 + c] > px[r * 9 + c + 1] else 0)
    return h


def image_hashes(records, cache_path):
    import hashlib
    cache = {}
    if os.path.exists(cache_path):
        try:
            with open(cache_path, encoding="utf-8") as f:
                cache = json.load(f)
        except Exception:
            cache = {}
    out, changed = {}, False
    for rec in records:
        p = os.path.join(ROOT, rec.get("thumb") or "")
        if not rec.get("thumb") or not os.path.exists(p):
            continue
        mt = os.path.getmtime(p)
        c = cache.get(rec["code"])
        if c and abs(c[0] - mt) < 1:
            out[rec["code"]] = (c[1], c[2])
            continue
        with open(p, "rb") as f:
            md5 = hashlib.md5(f.read()).hexdigest()
        out[rec["code"]] = (md5, _dhash(p))
        cache[rec["code"]] = [mt, md5, out[rec["code"]][1]]
        changed = True
    if changed:
        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(cache, f)
    return out


def dedupe(records, cache_path):
    """合并视觉上几乎相同、且标题相似的条目；保留信息最全的一条。"""
    by = {r["code"]: r for r in records}
    hs = image_hashes(records, cache_path)
    if not hs:
        return records, 0
    titles = {c: _tokens(by[c]["title"]) for c in hs}

    bands = {}
    for c, (_, h) in hs.items():
        for i in range(4):
            bands.setdefault((i, (h >> (16 * i)) & 0xFFFF), []).append(c)

    parent = {c: c for c in hs}

    def find(a):
        while parent[a] != a:
            parent[a] = parent[parent[a]]
            a = parent[a]
        return a

    def union(a, b):
        ra, rb = find(a), find(b)
        if ra != rb:
            parent[rb] = ra

    for cs in bands.values():
        if len(cs) < 2:
            continue
        for i in range(len(cs)):
            for j in range(i + 1, len(cs)):
                a, b = cs[i], cs[j]
                if find(a) == find(b):
                    continue
                same_file = hs[a][0] == hs[b][0]
                near = (hs[a][1] ^ hs[b][1]).bit_count() <= 4 and _jaccard(titles[a], titles[b]) >= 0.5
                if same_file or near:
                    union(a, b)

    clusters = {}
    for c in hs:
        clusters.setdefault(find(c), []).append(c)

    removed = 0
    for members in clusters.values():
        if len(members) < 2:
            continue
        keeper = max(members, key=lambda c: (len(by[c]["sources"]), by[c]["likes"] or 0,
                                             bool(by[c].get("prompt")), -int(c) if c.isdigit() else 0))
        k = by[keeper]
        alts = set(k.get("alt_codes") or [])
        for c in members:
            if c == keeper:
                continue
            o = by[c]
            alts.add(c)
            alts.update(o.get("alt_codes") or [])
            for s in o["sources"]:
                if s not in k["sources"]:
                    k["sources"].append(s)
            for t in o.get("tags") or []:
                if t not in k["tags"] and len(k["tags"]) < 6:
                    k["tags"].append(t)
            k["likes"] = max(k["likes"] or 0, o.get("likes") or 0)
            removed += 1
            by.pop(c, None)
        k["alt_codes"] = sorted(alts)
    return list(by.values()), removed


def clean_prompt(p):
    """把抓取时拼接的多条推文，挑出最像“提示词”的那条。"""
    if not p:
        return ""
    parts = [x.strip() for x in p.split("||") if x.strip()]
    cands = [x for x in parts if "--sref" in x] or parts
    best = min(cands, key=len)
    return best[:300]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--report", action="store_true")
    args = ap.parse_args()

    old = {}
    old_path = os.path.join(DATA, "srefs.json")
    if os.path.exists(old_path):
        with open(old_path, encoding="utf-8") as f:
            for rec in json.load(f).get("items", []):
                old[rec["code"]] = rec

    merged = {}

    def put(src_item, source):
        code = str(src_item.get("code") or "").strip()
        if not slug_ok(code):
            return
        rec = merged.get(code)
        if rec is None:
            rec = {
                "code": code,
                "title": src_item.get("title") or "",
                "title_alt": "",
                "prompt": src_item.get("prompt") or "",
                "keywords": list(src_item.get("keywords") or [])[:12],
                "images": list(src_item.get("images") or [])[:4],
                "likes": src_item.get("likes") or 0,
                "favs": src_item.get("favs") or 0,
                "version": src_item.get("mj_version") or "",
                "author": src_item.get("author") or "",
                "created": (src_item.get("created_at") or "")[:10],
                "updated": (src_item.get("updated_at") or "")[:10],
                "sources": [source],
                "source_url": src_item.get("source_url") or "",
                "pick": bool(src_item.get("pick")),
                "title_alt": "",
                "thumb": "",
                "first_seen": TODAY,
            }
            merged[code] = rec
        else:
            if source not in rec["sources"]:
                rec["sources"].append(source)
            if not rec["title"] and src_item.get("title"):
                rec["title"] = src_item["title"]
            elif src_item.get("title") and src_item["title"].lower() != rec["title"].lower():
                if source == "midlibrary" and not rec["title_alt"]:
                    rec["title_alt"] = src_item["title"]
                elif source == "srefhunt" and not rec["title_alt"]:
                    rec["title_alt"] = src_item["title"]
            if not rec["images"] and src_item.get("images"):
                rec["images"] = list(src_item["images"])[:4]
            if not rec["keywords"] and src_item.get("keywords"):
                rec["keywords"] = list(src_item["keywords"])[:12]
            rec["likes"] = max(rec["likes"], src_item.get("likes") or 0)
            rec["favs"] = max(rec["favs"], src_item.get("favs") or 0)
            if not rec["version"] and src_item.get("mj_version"):
                rec["version"] = src_item["mj_version"]
            if not rec["prompt"] and src_item.get("prompt"):
                rec["prompt"] = src_item["prompt"]
            rec["pick"] = rec["pick"] or bool(src_item.get("pick"))
            if not rec["source_url"] or source == "sref-midjourney":
                rec["source_url"] = src_item.get("source_url") or rec["source_url"]

    # 顺序：主库优先，其余补全
    for it in load("sref_midjourney_raw.json"):
        put(it, "sref-midjourney")
    for it in load("srefhunt_raw.json"):
        put(it, "srefhunt")
    for it in load("midlibrary_raw.json"):
        put(it, "midlibrary")

    # Midlibrary 详情页的 Look terms（Subject / Medium / Genre / Mood ...）
    look = {}
    look_path = os.path.join(SRC, "midlibrary_terms.json")
    if os.path.exists(look_path):
        with open(look_path, encoding="utf-8") as f:
            look = json.load(f)

    # 分类 + 标签 + 缩略图
    thumb_dir = os.path.join(ROOT, "assets", "thumbs")
    weights, max_w = build_weights(merged.values())
    for code, rec in merged.items():
        cat = classify(rec, weights, max_w)
        lt = look.get(code)
        if lt and lt.get("groups"):
            rec["look"] = lt["groups"]
            if lt.get("obs"):
                rec["obs"] = lt["obs"][:320]
            names = flat_terms(lt["groups"])
            if not rec.get("keywords"):
                rec["keywords"] = names[:12]
            # 关键词分类失败时，用详情页的 Look terms 兜底
            if cat in ("midlibrary", "other"):
                lc = probe_category(lt["groups"])
                if lc:
                    cat = lc
        rec["category"] = cat
        tags = make_tags(rec, cat)
        if lt and lt.get("groups") and (not tags or "Midlibrary 精选" in tags):
            tags = probe_tags(lt["groups"]) or tags
        rec["tags"] = tags
        rec["prompt"] = clean_prompt(rec.get("prompt"))
        # 全量中文关键词，仅用于搜索（不展示）
        zh = []
        for k in rec.get("keywords") or []:
            z = ZH_TERMS.get(k.strip().lower())
            if z and z not in zh:
                zh.append(z)
        rec["zh"] = " ".join(zh)
        if os.path.exists(os.path.join(thumb_dir, f"{code}.jpg")):
            rec["thumb"] = f"assets/thumbs/{code}.jpg"
        # 保留旧记录的首次收录时间与个人备注
        if code in old:
            rec["first_seen"] = old[code].get("first_seen") or TODAY

    os.makedirs(DATA, exist_ok=True)
    items, deduped = dedupe(list(merged.values()), os.path.join(DATA, "hash_cache.json"))
    items = sorted(items, key=lambda r: (-(r["likes"] or 0), r["code"]))
    new_codes = [c for c in merged if c not in old]

    meta = {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "total": len(items),
        "duplicates_removed": deduped,
        "new_this_run": len(new_codes),
        "with_image": sum(1 for r in items if r["images"] or r["thumb"]),
        "sources": dict(Counter(s for r in items for s in r["sources"])),
        "categories": dict(Counter(r["category"] for r in items)),
        "category_zh": {c["id"]: c["zh"] for c in CATEGORIES},
    }

    os.makedirs(DATA, exist_ok=True)
    with open(os.path.join(DATA, "srefs.json"), "w", encoding="utf-8") as f:
        json.dump({"meta": meta, "items": items}, f, ensure_ascii=False, separators=(",", ":"))

    with open(os.path.join(DATA, "srefs.js"), "w", encoding="utf-8") as f:
        f.write("window.SREF_META=")
        json.dump(meta, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\nwindow.SREF_DATA=")
        json.dump(items, f, ensure_ascii=False, separators=(",", ":"))
        f.write(";\n")

    cols = ["code", "title", "title_alt", "category", "tags", "keywords", "prompt",
            "version", "likes", "author", "sources", "source_url", "created", "first_seen"]
    with open(os.path.join(DATA, "srefs.csv"), "w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f)
        w.writerow(["风格代码", "名称", "别名", "分类", "中文标签", "关键词", "提示词示例",
                    "MJ版本", "点赞", "作者", "来源", "链接", "发布时间", "收录时间"])
        for r in items:
            w.writerow(["--sref " + r["code"], r["title"], r["title_alt"],
                        dict((c["id"], c["zh"]) for c in CATEGORIES).get(r["category"], "其他"),
                        " / ".join(r["tags"]), ", ".join(r["keywords"]), r["prompt"],
                        r["version"], r["likes"], r["author"], "+".join(r["sources"]),
                        r["source_url"], r["created"], r["first_seen"]])

    log_path = os.path.join(DATA, "update_log.json")
    log = []
    if os.path.exists(log_path):
        with open(log_path, encoding="utf-8") as f:
            log = json.load(f)
    log.append({"time": meta["generated_at"], "total": meta["total"],
                "new": len(new_codes), "sources": meta["sources"]})
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log[-60:], f, ensure_ascii=False, indent=1)

    print(f"[build] 总计 {meta['total']} 条，本次新增 {len(new_codes)}，有图 {meta['with_image']}")
    print("[build] 分类:", ", ".join(f"{k}:{v}" for k, v in
                                    sorted(meta["categories"].items(), key=lambda kv: -kv[1])[:12]))

    if args.report and new_codes:
        rdir = os.path.join(ROOT, "reports")
        os.makedirs(rdir, exist_ok=True)
        path = os.path.join(rdir, f"update-{time.strftime('%Y%m%d-%H%M')}.md")
        with open(path, "w", encoding="utf-8") as f:
            f.write(f"# SREF 资料库更新 {meta['generated_at']}\n\n")
            f.write(f"- 总量：**{meta['total']}**\n- 本次新增：**{len(new_codes)}**\n\n")
            f.write("## 新增条目（按点赞排序，最多 80 条）\n\n")
            f.write("| 代码 | 名称 | 分类 | 点赞 |\n|---|---|---|---|\n")
            cat_zh = {c["id"]: c["zh"] for c in CATEGORIES}
            shown = [r for r in items if r["code"] in set(new_codes)][:80]
            for r in shown:
                f.write(f"| `--sref {r['code']}` | {r['title'][:40]} | "
                        f"{cat_zh.get(r['category'], '其他')} | {r['likes']} |\n")
        print(f"[build] 报告: {path}")


if __name__ == "__main__":
    main()
