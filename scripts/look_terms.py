"""Midlibrary Look terms 的解读：分类映射 + 中文标签。"""

# 组内优先顺序：越靠前越具体（Characters 几乎出现在所有页面，放最后兜底）
SUBJECT_ORDER = ["Letters", "Ethnic", "Portraits", "Still Life", "Fashion",
                 "Patterns", "Urban", "Animals", "Floral", "Landscapes", "Characters"]

# term -> 主分类（大小写不敏感）
LOOK_CATEGORY = {
    # Medium
    "drawing": "sketch",
    "ink": "sketch",
    "collage": "collage",
    "halftone": "comic",
    # Subject
    "characters": "character",
    "portraits": "portrait",
    "landscapes": "nature",
    "floral": "nature",
    "animals": "nature",
    "urban": "architecture",
    "patterns": "texture",
    "fashion": "fashion",
    "still life": "product",
    "letters": "graphic",
    "ethnic": "ethnic",
    # Genre
    "surreal": "surreal",
    "cinematic": "cinematic",
    "sci-fi": "cyberpunk",
    "comics": "comic",
    "documentary": "photography",
    # Technique
    "fine lines": "sketch",
    "bold lines": "comic",
    "crosshatching": "sketch",
    "flat color": "graphic",
    "painterly": "painting",
    "fine brushstrokes": "painting",
    "broad brushstrokes": "painting",
    "grain": "photography",
    "shallow focus": "photography",
    # Theme / quality
    "fantasy": "fantasy",
    "retro": "retro",
    "classical": "painting",
    "abstract": "abstract",
    "minimalist": "minimal",
    "illustrative": "illustration",
}

# 分类映射的组优先级：先看“画法/媒介/流派”，题材只作兜底
# （Midlibrary 的 Subject 几乎每个风格都会标 Characters/Landscapes，不适合当主分类）
GROUP_PRIORITY = ["Medium", "Technique", "Genre", "Style quality", "Theme", "Subject"]

LOOK_ZH = {
    # Style quality
    "Detailed": "细致", "Illustrative": "插画感", "Expressive": "表现力", "Bold": "大胆",
    "Realistic": "写实", "Ornate": "华丽", "Abstract": "抽象", "Sculptural": "雕塑感",
    "Minimalist": "极简",
    # Colour scheme
    "Vivid": "鲜艳", "High contrast": "高对比", "Subdued": "低饱和", "BW": "黑白",
    "Moody": "低沉", "Pastel": "柔彩", "Metallic": "金属色", "Light": "明亮",
    "Psychedelic": "迷幻",
    # Technique
    "Fine lines": "细线", "Flat color": "平涂", "Painterly": "绘画感", "Bold lines": "粗线",
    "Fine brushstrokes": "细笔触", "Grain": "颗粒", "Shallow focus": "浅景深",
    "Broad brushstrokes": "阔笔触", "Crosshatching": "交叉排线",
    # Genre
    "Surreal": "超现实", "Cinematic": "电影感", "Sci-fi": "科幻", "Comics": "漫画",
    "Documentary": "纪实",
    # Composition
    "Geometric": "几何", "Negative space": "留白", "Symmetry": "对称", "Silhouette": "剪影",
    # Visual effects
    "Glow": "辉光", "Motion": "动感", "Mist": "雾气", "Backlighting": "逆光",
    # Mood
    "Dreamy": "梦幻", "Epic": "史诗", "Dark": "暗黑", "Cute": "可爱", "Funny": "趣味",
    # Theme
    "Fantasy": "奇幻", "Retro": "复古", "Classical": "古典", "Religious": "宗教",
    # Subject
    "Characters": "角色", "Landscapes": "风景", "Scenes": "场景", "Floral": "花卉",
    "Animals": "动物", "Portraits": "人像", "Urban": "都市", "Patterns": "图案",
    "Fashion": "时尚", "Still Life": "静物", "Letters": "字体", "Ethnic": "民族",
    # Medium
    "Drawing": "素描", "Ink": "墨线", "Collage": "拼贴", "Halftone": "半调",
}

# 标签优先级：先氛围/题材，再质量/构图
TAG_GROUPS = ["Mood", "Theme", "Genre", "Subject", "Colour scheme",
              "Style quality", "Composition", "Visual effects"]


def probe_category(groups):
    """根据 Look terms 推出一个主分类；推不出返回 None。"""
    for label in GROUP_PRIORITY:
        terms = groups.get(label) or []
        names = [t[0] if isinstance(t, (list, tuple)) else t for t in terms]
        if label == "Subject":
            ordered = [n for n in SUBJECT_ORDER if n in names] + names
        else:
            ordered = names
        for name in ordered:
            cat = LOOK_CATEGORY.get(str(name).lower())
            if cat:
                return cat
    return None


def probe_tags(groups, limit=4):
    """生成中文标签。"""
    tags = []
    for label in TAG_GROUPS:
        for t in groups.get(label) or []:
            name = t[0] if isinstance(t, (list, tuple)) else t
            zh = LOOK_ZH.get(name)
            if zh and zh not in tags:
                tags.append(zh)
            if len(tags) >= limit:
                return tags
    return tags


def flat_terms(groups):
    out = []
    for label, terms in groups.items():
        for t in terms:
            name = t[0] if isinstance(t, (list, tuple)) else t
            if name not in out:
                out.append(name)
    return out
