"""SREF 资料库的分类规则与中文术语词典（可自行扩充）。

- CATEGORIES: 主分类（用于筛选），按关键词打分，取最高分
- ZH_TERMS: 英文风格词 -> 中文，用于生成中文标签
"""

CATEGORIES = [
    {"id": "portrait", "zh": "人像", "en": "Portrait", "kw": [
        "portrait", "selfie", "headshot", "facial", "freckles", "close-up", "model",
        "beauty", "gaze", "face", "eyes", "skin texture", "profile view"]},
    {"id": "anime", "zh": "动漫", "en": "Anime", "kw": [
        "anime", "manga", "chibi", "waifu", "ghibli", "cel shading", "anime style",
        "anime-inspired", "japanese animation", "mecha girl", "seinen", "shonen"]},
    {"id": "illustration", "zh": "插画", "en": "Illustration", "kw": [
        "illustration", "illustrative", "drawing", "storybook", "children's book",
        "picture book", "doodle", "editorial illustration", "book cover"]},
    {"id": "painting", "zh": "油画绘画", "en": "Painting", "kw": [
        "oil painting", "acrylic", "gouache", "impasto", "brushstroke", "brush strokes",
        "painterly", "canvas", "fine art", "impressionism", "impressionistic",
        "expressionism", "expressionist", "fresco", "mural", "palette knife"]},
    {"id": "watercolor", "zh": "水彩水墨", "en": "Watercolor & Ink", "kw": [
        "watercolor", "watercolour", "ink wash", "sumi-e", "ink painting", "chinese ink",
        "wash", "wet on wet", "ink bleed", "guohua"]},
    {"id": "sketch", "zh": "素描线稿", "en": "Sketch & Line Art", "kw": [
        "sketch", "pencil", "charcoal", "line art", "linework", "line drawing",
        "etching", "engraving", "cross-hatching", "blueprint", "technical drawing",
        "contour", "ink line"]},
    {"id": "3d", "zh": "3D渲染", "en": "3D Render", "kw": [
        "3d", "3d render", "cgi", "blender", "octane", "claymation", "clay", "plastic",
        "toy", "pixar", "isometric", "low poly", "low-poly", "voxel", "figurine",
        "render", "unreal engine", "subsurface scattering", "glossy"]},
    {"id": "photography", "zh": "摄影", "en": "Photography", "kw": [
        "photography", "photo", "photographic", "35mm", "film photography", "polaroid",
        "bokeh", "dslr", "lens", "analog", "film grain", "street photography",
        "editorial photo", "documentary", "shallow depth of field", "kodak"]},
    {"id": "cyberpunk", "zh": "赛博科幻", "en": "Cyberpunk & Sci-Fi", "kw": [
        "cyberpunk", "futuristic", "sci-fi", "sci fi", "spaceship", "robot", "mecha",
        "holographic", "dystopian", "synthwave", "vaporwave", "neon city", "space",
        "alien", "cybernetic", "android"]},
    {"id": "fantasy", "zh": "奇幻", "en": "Fantasy", "kw": [
        "fantasy", "magical", "mythical", "dragon", "wizard", "elven", "enchanted",
        "medieval", "fairy", "myth", "castle", "knight", "sorceress", "troll", "rune"]},
    {"id": "surreal", "zh": "超现实", "en": "Surreal", "kw": [
        "surreal", "surrealism", "dreamlike", "dreamscape", "psychedelic",
        "hallucination", "impossible", "otherworldly", "cosmic", "ethereal",
        "floating", "metamorphosis"]},
    {"id": "abstract", "zh": "抽象", "en": "Abstract", "kw": [
        "abstract", "abstraction", "geometric shapes", "non-representational",
        "gestural", "color field", "amorphous", "fractal"]},
    {"id": "retro", "zh": "复古", "en": "Retro & Vintage", "kw": [
        "retro", "vintage", "80s", "90s", "art deco", "art nouveau", "mid-century",
        "nostalgic", "sepia", "pin-up", "70s", "old photograph", "analog", "classic"]},
    {"id": "minimal", "zh": "极简", "en": "Minimal", "kw": [
        "minimalist", "minimalism", "negative space", "flat design", "swiss",
        "clean lines", "simple", "reductive", "monochrome"]},
    {"id": "graphic", "zh": "平面矢量", "en": "Graphic & Vector", "kw": [
        "vector", "graphic design", "poster", "typography", "bauhaus", "branding",
        "logo", "gradient", "flat colors", "infographic", "swiss style", "editorial design"]},
    {"id": "collage", "zh": "拼贴", "en": "Collage", "kw": [
        "collage", "mixed media", "cutout", "scrapbook", "montage", "paper cut",
        "papercraft", "origami", "photomontage"]},
    {"id": "comic", "zh": "漫画", "en": "Comic & Pop", "kw": [
        "comic", "comic book", "halftone", "superhero", "graphic novel", "pop art",
        "cartoon", "cartoonish", "caricature", "manga panel", "speech bubble"]},
    {"id": "architecture", "zh": "建筑场景", "en": "Architecture", "kw": [
        "architecture", "architectural", "building", "interior", "cityscape", "urban",
        "street", "cathedral", "brutalist", "facade", "skyline", "city", "room"]},
    {"id": "nature", "zh": "自然风景", "en": "Nature", "kw": [
        "landscape", "nature", "mountain", "forest", "ocean", "botanical", "floral",
        "garden", "sky", "cloud", "flower", "tree", "underwater", "desert", "sea",
        "field", "plant"]},
    {"id": "fashion", "zh": "时尚", "en": "Fashion", "kw": [
        "fashion", "couture", "runway", "glamour", "jewelry", "outfit", "dress",
        "vogue", "streetwear", "haute couture", "fashion editorial"]},
    {"id": "product", "zh": "产品静物", "en": "Product & Still Life", "kw": [
        "product", "still life", "knolling", "packaging", "food", "drink", "object",
        "bottle", "watch", "sneaker", "perfume", "advertising"]},
    {"id": "character", "zh": "角色设计", "en": "Character", "kw": [
        "character design", "concept art", "creature", "costume", "armor", "warrior",
        "hero", "villain", "character sheet", "portrait character", "rpg"]},
    {"id": "dark", "zh": "暗黑哥特", "en": "Dark & Gothic", "kw": [
        "gothic", "dark", "horror", "eerie", "macabre", "occult", "noir", "ominous",
        "haunting", "skull", "blood", "grunge", "sinister", "melancholic"]},
    {"id": "cute", "zh": "可爱童话", "en": "Cute & Whimsical", "kw": [
        "cute", "kawaii", "whimsical", "childlike", "playful", "cozy", "fairy tale",
        "stuffed animal", "adorable", "pastel", "toylike"]},
    {"id": "neon", "zh": "霓虹光影", "en": "Neon & Glow", "kw": [
        "neon", "glow", "glowing", "luminous", "bioluminescent", "light trails",
        "fluorescent", "led", "light painting", "luminescent"]},
    {"id": "cinematic", "zh": "电影感", "en": "Cinematic", "kw": [
        "cinematic", "film still", "movie", "dramatic lighting", "anamorphic",
        "color grading", "cinematic lighting", "widescreen", "movie poster"]},
    {"id": "texture", "zh": "材质肌理", "en": "Texture & Material", "kw": [
        "texture", "textured", "paper", "fabric", "metallic", "marble", "glass",
        "ceramic", "risograph", "embossed", "woven", "concrete"]},
    {"id": "ethnic", "zh": "民族传统", "en": "Ethnic & Traditional", "kw": [
        "ukiyo-e", "chinese", "japanese", "african", "tribal", "folk art", "byzantine",
        "persian", "islamic", "aboriginal", "batik", "hanfu", "thangka", "artisan"]},
]

# 英文风格词 -> 中文标签（用于卡片标签，按需扩充）
ZH_TERMS = {
    # 情绪 / 氛围
    "surreal": "超现实", "surrealism": "超现实主义", "ethereal": "空灵", "dreamlike": "梦境",
    "dreamy": "梦幻", "serene": "宁静", "elegant": "优雅", "expressive": "表现力",
    "dynamic": "动感", "vibrant": "鲜艳", "calm": "平静", "whimsical": "奇趣",
    "mysterious": "神秘", "mystical": "神秘主义", "atmospheric": "氛围感",
    "dramatic": "戏剧性", "moody": "低沉", "bold": "大胆", "emotive": "情绪化",
    "intense": "强烈", "nostalgic": "怀旧", "imaginative": "想象力", "delicate": "细腻",
    "contemplative": "沉思", "energetic": "活力", "introspective": "内省", "tranquil": "安宁",
    "romantic": "浪漫", "melancholic": "忧郁", "peaceful": "平和", "intimate": "亲密",
    "eerie": "诡异", "cozy": "温馨", "charming": "迷人", "joyful": "欢快",
    "cheerful": "愉快", "sophisticated": "精致", "ornate": "华丽", "ominous": "不祥",
    "airy": "轻盈", "edgy": "前卫", "enigmatic": "难解", "gritty": "粗粝",
    "otherworldly": "异世界", "haunting": "萦绕", "timeless": "永恒", "graceful": "优美",
    "magical": "魔法", "chaotic": "混乱", "luxurious": "奢华", "glamorous": "魅惑",
    "heroic": "英雄气", "epic": "史诗", "wholesome": "治愈", "witty": "诙谐",
    "satirical": "讽刺", "romanticized": "浪漫化", "ethereal glow": "空灵光晕",
    # 媒介 / 技法
    "illustration": "插画", "illustrative": "插画感", "digital art": "数字艺术",
    "painting": "绘画", "oil painting": "油画", "watercolor": "水彩", "sketch": "素描",
    "line art": "线稿", "ink": "水墨", "pencil": "铅笔", "charcoal": "炭笔",
    "collage": "拼贴", "mixed media": "综合材料", "vector": "矢量", "3d": "3D",
    "3d render": "3D渲染", "photography": "摄影", "photo": "照片", "film": "胶片",
    "polaroid": "拍立得", "anime": "动漫", "manga": "日漫", "cartoon": "卡通",
    "cartoonish": "卡通化", "comic": "漫画", "comic book": "美漫", "pop art": "波普艺术",
    "pixel art": "像素艺术", "claymation": "黏土动画", "papercraft": "纸艺",
    "isometric": "等距视角", "low poly": "低多边形", "voxel": "体素",
    "typography": "字体设计", "poster": "海报", "graphic design": "平面设计",
    "bauhaus": "包豪斯", "art deco": "装饰艺术", "art nouveau": "新艺术",
    "ukiyo-e": "浮世绘", "impressionism": "印象派", "expressionism": "表现主义",
    "realism": "写实", "photorealism": "超写实", "hyperrealistic": "超写实",
    "cinematic": "电影感", "knolling": "平铺摆拍", "risograph": "孔版印刷",
    "halftone": "半调网点", "gradient": "渐变", "monochrome": "单色",
    "black and white": "黑白", "sepia": "棕褐",
    # 题材
    "portrait": "人像", "landscape": "风景", "cityscape": "城市景观", "nature": "自然",
    "floral": "花卉", "botanical": "植物", "garden": "花园", "forest": "森林",
    "ocean": "海洋", "mountain": "山", "desert": "沙漠", "sky": "天空", "cloud": "云",
    "underwater": "水下", "architecture": "建筑", "interior": "室内", "urban": "都市",
    "street": "街道", "fashion": "时尚", "couture": "高定", "jewelry": "珠宝",
    "food": "食物", "still life": "静物", "product": "产品", "packaging": "包装",
    "character design": "角色设计", "concept art": "概念艺术", "creature": "生物",
    "dragon": "龙", "robot": "机器人", "mecha": "机甲", "spaceship": "飞船",
    "cyberpunk": "赛博朋克", "sci-fi": "科幻", "futuristic": "未来感", "space": "太空",
    "fantasy": "奇幻", "medieval": "中世纪", "gothic": "哥特", "horror": "恐怖",
    "skull": "骷髅", "dark": "暗黑", "noir": "黑色电影", "vintage": "复古",
    "retro": "复古", "80s": "80年代", "90s": "90年代", "mid-century": "中世纪现代",
    "minimalist": "极简", "minimalism": "极简主义", "abstract": "抽象",
    "geometric": "几何", "symmetrical": "对称", "pattern": "图案", "texture": "肌理",
    "textured": "质感", "paper": "纸感", "fabric": "织物", "metallic": "金属",
    "marble": "大理石", "glass": "玻璃", "ceramic": "陶瓷", "concrete": "混凝土",
    "neon": "霓虹", "glow": "发光", "glowing": "发光", "luminous": "明亮",
    "bioluminescent": "生物荧光", "pastel": "柔彩", "soft": "柔和", "warm": "暖色",
    "cool": "冷色", "earthy": "土色", "muted": "低饱和", "saturated": "高饱和",
    "colorful": "多彩", "vivid": "鲜明", "high contrast": "高对比",
    "contrast": "对比", "silhouette": "剪影", "reflection": "倒影", "shadow": "阴影",
    "femine": "女性化", "feminine": "女性化", "masculine": "男性化", "youthful": "青春",
    "childlike": "童趣", "cute": "可爱", "kawaii": "可爱", "playful": "俏皮",
    "adventure": "冒险", "cosmic": "宇宙", "celestial": "天体", "mythical": "神话",
    "mystical creature": "神秘生物", "fairy": "精灵", "witch": "女巫",
    "warrior": "战士", "armor": "盔甲", "samurai": "武士", "ninja": "忍者",
    "steampunk": "蒸汽朋克", "dieselpunk": "柴油朋克", "solarpunk": "太阳能朋克",
    "afrofuturism": "非洲未来主义", "vaporwave": "蒸汽波", "synthwave": "合成器波",
    "glitch": "故障艺术", "grunge": "垃圾摇滚", "punk": "朋克", "gothic architecture": "哥特建筑",
    "brutalist": "粗野主义", "industrial": "工业", "military": "军事",
    "botanical illustration": "植物插画", "scientific illustration": "科学插画",
    "editorial": "编辑风", "advertising": "广告", "branding": "品牌",
    "album cover": "专辑封面", "movie poster": "电影海报", "book cover": "书籍封面",
    "tattoo": "纹身", "graffiti": "涂鸦", "sticker": "贴纸", "emoji": "表情",
    "doodle": "涂鸦", "storybook": "绘本", "children's book": "童书",
    "fantasy art": "奇幻艺术", "concept art": "概念艺术", "matte painting": "接景绘景",
    "key visual": "主视觉", "character sheet": "角色设定图",
}

# 过于泛化、不作为标签展示的词
GENERIC = {"detailed", "artistic", "modern", "stylized", "creative", "beautiful",
           "high quality", "professional", "contemporary", "classic", "traditional",
           "unique", "innovative", "masterpiece", "4k", "8k", "hd", "sharp focus"}
