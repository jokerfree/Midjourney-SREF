# SREF 风格画廊

![风格画廊](preview.png)

把 Midjourney 的 `--sref`（Style Reference）风格代码整理成一座可检索、可更新、可离线浏览的私人画廊。

- **藏品**：**9,298** 件去重后的风格（已合并 221 件重复），每件都有预览图、编号、中文标签与来源链接
- **来源**：Sref-Midjourney、SrefHunt、Midlibrary 三个公开风格库
- **完全离线**：全部缩略图已本地化到 `assets/thumbs/`，断网也能正常浏览（52 条原图链接在源站已失效，显示占位图）
- **形态**：一个双击即用的 `index.html` 画廊 + JSON / CSV 数据 + 一键更新脚本
- **更新**：支持手动一键更新、只更新单个来源、Windows 计划任务定期自动更新

### 数据构成

| 来源 | 条数 | 特点 |
|---|---|---|
| Sref-Midjourney | 4,949 | 主库：预览图 + 英文关键词 + 点赞热度 + 版本 |
| Midlibrary | 4,462 | 策展式命名风格；详情页的 Look terms 已抓取，参与分类与标签 |
| SrefHunt | 178 | 手工精选，带风格标签 |
| **合计（去重）** | **9,298** | 跨站重复约 70 条；另有 221 件视觉/标题重复的作品被合并，代码保留在详情页 |

所有预览图都已下载为 320px 本地缩略图（`assets/thumbs/<代码>.jpg`），浏览时不依赖外部站点；仅 52 条的原图在源站已 403 失效，保留渐变色占位图。

### Midlibrary 的细分类型

Midlibrary 列表页只给了一个笼统的「SREF codes」分类，但它每个风格详情页都有 10 组人工标注的 **Look terms**：

`Medium`（Drawing / Ink / Collage…）、`Technique`（Fine lines / Flat color / Painterly…）、`Genre`（Surreal / Cinematic / Sci-Fi…）、`Style quality`（Illustrative / Abstract / Minimalist…）、`Theme`、`Mood`、`Subject`、`Colour scheme`、`Composition`、`Visual effects`。

本库把这 4,462 个详情页全部抓取下来，按「画法 → 媒介 → 流派 → 题材」的优先级映射到统一分类，并把 Look terms 翻译成中文标签（如 `细线`、`平涂`、`电影感`、`黑白`、`留白`）。所以 Midlibrary 条目现在也会出现在「素描线稿」「油画绘画」「超现实」「摄影」等分类里，不再是单独一个桶。

分类共 28 类（另有 `other`）；数量较多的有：素描线稿 1,905、油画绘画 850、超现实 763、漫画 728、可爱童话 497、人像 454、暗黑哥特 426、赛博科幻 408、自然风景 347、摄影 345、平面矢量 305。Midlibrary 的 4,400 条已全部分到具体类型，不再堆在一个桶里。

### 去重规则

同一风格常被反复收录：同一张图配不同代码、或标题只差一两个词。构建时会自动合并——

- 缩略图文件完全相同，或
- 感知哈希（dHash）距离 ≤ 4 且标题词重合约 ≥ 50%

合并后保留信息最全的一条（来源数、点赞、提示词优先），其余代码记入 `alt_codes`，在详情页仍可一键复制，不会丢代码。

---

## 1. 快速开始

双击 **`index.html`**，或双击 **`打开资料库.cmd`**（会用默认浏览器打开）。推荐 Edge / Chrome，无需安装、无需服务器。

> ⚠️ 不要在编辑器 / 文件预览面板里看这个页面：预览用的 iframe 会禁用脚本，列表会停在“加载中…”。
> 请用浏览器直接打开文件；如果浏览器限制本地脚本，运行 `scripts\start_server.ps1` 起本地服务后再访问。

> 画廊通过 `data/srefs.js` 读取数据（约 10 MB），首次打开稍等一两秒即可。

## 2. 界面怎么用

| 功能 | 说明 |
|---|---|
| 搜索框 | 支持风格名、代码（`1294827730` 或 `--sref 1294827730`）、中文标签（`水彩`）、英文关键词（`cyberpunk`），也会搜 Midlibrary 的英文风格观察；空格分隔多个词为“同时满足” |
| 分类签 | 按媒介/题材筛选，右侧数字是数量；全部换行展示，不需要横向滚动 |
| 列表加载 | 滚动到底自动加载下一批；若环境不派发滚动事件，点底部「继续浏览 · 还有 N 件」即可 |
| 来源筛选 | 只看某个来源的条目 |
| 排序 | 热度（点赞）/ 最新 / 名称 / 随机 |
| 复制当前结果 | 把当前筛选出的所有 `--sref xxxx` 逐行复制，方便批量整理 |
| 作品卡 | 顶栏有展墙轮播与馆藏统计；卡片带馆藏编号（No. 0001），点开看大图、提示词、风格观察 |

**小技巧**

- 按 `/` 快速聚焦搜索框，`Esc` 清空搜索
- 支持 URL 直达：`index.html#cat=anime`、`index.html#q=水彩`、`index.html#src=midlibrary`
- 在想固定风格时，用 `--sref <code> --sw 100` 控制强度（`--sw` 范围 0–1000，默认 100）
- 同一提示词换不同 `--sref`，是低成本探索风格的最快方式

## 3. 目录结构

```
mj-sref-library/
├─ index.html                # 画廊主页（双击打开）
├─ 打开资料库.cmd            # 用默认浏览器打开
├─ data/
│  ├─ srefs.json             # 主数据（含全部字段）
│  ├─ srefs.csv              # Excel 可直接打开的版本（UTF-8 BOM）
│  ├─ srefs.js               # 给 index.html 用的数据脚本
│  └─ update_log.json        # 历次更新的总量/新增记录
├─ assets/thumbs/            # 全部 9,298 张本地缩略图（离线可用）
├─ sources/                  # 各来源的原始抓取结果（可删除，重抓会重建）
├─ scripts/
│  ├─ update_srefs.py        # ★ 一键更新入口
│  ├─ fetch_srefmj.py        # 抓 Sref-Midjourney
│  ├─ repair_srefmj.py       # 补抓失败页
│  ├─ fetch_srefhunt.py      # 抓 SrefHunt
│  ├─ fetch_midlibrary.py    # 抓 Midlibrary
│  ├─ fetch_midlibrary_terms.py # 抓 Midlibrary 详情页的 Look terms
│  ├─ fetch_thumbs.py        # 下载 Midlibrary 缩略图
│  ├─ fetch_remote_thumbs.py # 下载其余来源的缩略图并压缩到本地
│  ├─ build_library.py       # 合并/去重/分类/生成 CSV+JS
│  ├─ taxonomy.py            # 通用分类规则与中英词典
│  ├─ look_terms.py          # Midlibrary Look terms 的分类映射与中文标签
│  ├─ start_server.ps1       # 起本地 HTTP 服务（浏览器限制本地脚本时用）
│  ├─ run_update.ps1         # PowerShell 更新入口（带日志）
│  └─ register_task.ps1      # 注册 Windows 计划任务
├─ reports/                  # 每次更新生成的新增条目报告
└─ logs/                     # 计划任务运行日志
```

## 4. 定期更新

### 4.1 手动一键更新

```powershell
cd mj-sref-library
python scripts/update_srefs.py
```

全流程约 **20–40 分钟**（取决于网络）：三个站点全量重抓 → 合并去重 → 重建数据 → 补齐新缩略图。

常用参数：

```powershell
python scripts/update_srefs.py --fast            # 跳过 Midlibrary，只更新两个主站（约 10–15 分钟）
python scripts/update_srefs.py --only srefmj     # 只更新 Sref-Midjourney
python scripts/update_srefs.py --skip-thumbs     # 不补缩略图（更快）
```

更新后：

- `data/srefs.json` / `.csv` / `.js` 被覆盖为新版本
- `reports/update-YYYYMMDD-HHmm.md` 列出本次新增的风格（按点赞排序）
- `data/update_log.json` 追加一条记录（总量 / 新增数 / 各来源数量）
- 已有的 `首次收录时间` 会被保留，方便区分新旧条目

### 4.2 每周自动更新（Windows 计划任务）

```powershell
# 注册：每周日 20:00 自动更新
powershell -ExecutionPolicy Bypass -File scripts\register_task.ps1

# 改成每天早上 9:30
powershell -ExecutionPolicy Bypass -File scripts\register_task.ps1 -Time 09:30 -Schedule DAILY

# 删除任务
powershell -ExecutionPolicy Bypass -File scripts\register_task.ps1 -Remove
```

任务名：`MJ-SREF-Library-Update`。立即测试一次：

```powershell
schtasks /Run /TN MJ-SREF-Library-Update
```

运行日志在 `logs/update-*.log`。计划任务需要本机安装 Python 3 并加入 PATH。

### 4.3 只想“按需挑着更新”

- 只关心主流审美 → `--fast`，跳过 Midlibrary
- 只想补新出的 Sref-Midjourney 条目 → `--only srefmj`
- 只想刷新 Midlibrary → `--only midlibrary`
- 不想下载图片 → 加 `--skip-thumbs`，`index.html` 会自动用占位图代替

## 5. 数据字段

`data/srefs.json` 每条记录：

| 字段 | 含义 |
|---|---|
| `code` | 风格代码（使用时拼成 `--sref <code>`） |
| `title` / `title_alt` | 风格名 / 其他来源的别名 |
| `category` | 主分类 id（见 `taxonomy.py`） |
| `tags` | 中文标签（最多 5 个，用于展示与搜索） |
| `zh` | 全部中文关键词（仅用于搜索） |
| `keywords` | 原始英文关键词（按权重排序） |
| `prompt` | 示例提示词 |
| `images` | 预览图 URL（Sref-Midjourney 的 CDN） |
| `thumb` | 本地缩略图相对路径（Midlibrary） |
| `likes` / `favs` | 点赞 / 收藏数 |
| `version` | 适用的 Midjourney 版本（如 4、8.2） |
| `author` | 作者 |
| `sources` | 来源数组（同一代码可能被多个站点收录） |
| `source_url` | 原站详情页 |
| `first_seen` | 本库首次收录日期 |
| `alt_codes` | 被合并的重复风格代码（详情页仍可复制） |
| `look` | Midlibrary 的 Look terms 原始分组（Subject / Medium / Genre / Mood…） |
| `obs` | Midlibrary 的风格观察文本（英文，用于搜索与详情展示） |

分类共 28 类：人像、动漫、插画、油画绘画、水彩水墨、素描线稿、3D渲染、摄影、赛博科幻、奇幻、超现实、抽象、复古、极简、平面矢量、拼贴、漫画、建筑场景、自然风景、时尚、产品静物、角色设计、暗黑哥特、可爱童话、霓虹光影、电影感、材质肌理、民族传统；另有 `Midlibrary`（该站未提供分类）与 `other`。

## 6. 想调整分类或加来源

- **改分类/词典**：编辑 `scripts/taxonomy.py` 的 `CATEGORIES`（关键词列表）与 `ZH_TERMS`（英文→中文）；
  Midlibrary 的 Look terms 映射在 `scripts/look_terms.py`（改完重新运行 `build_library.py` 即可，不用重抓）。
- **加一个新来源**：仿照 `scripts/fetch_srefhunt.py` 写一个抓取器，输出
  `sources/xxx_raw.json`（字段见上），再在 `build_library.py` 的 `put(...)` 部分加一行即可。
- **只要 CSV**：直接打开 `data/srefs.csv`（Excel / Numbers / WPS 均可）。

## 7. 常见问题

**Q：为什么 Sref-Midjourney 站点显示 5,677 条，这里只有 4,949 条？**
站点的计数包含已下线/隐藏或分页重复的条目；逐页抓取并去重后，可实际访问的是 4,949 条（含 1–4 位的短代码）。本库保留可验证的真实条目，不虚报数量。

**Q：图片显示不出来？**
正常情况下不需要联网，所有缩略图都在 `assets/thumbs/`（320px）。如果整页空白，说明浏览器拦截了本地脚本，请用 `打开资料库.cmd` 打开，或运行 `scripts\start_server.ps1`。若个别图缺失，运行 `python scripts\fetch_remote_thumbs.py` 补下载即可。

**Q：会不会抓不到/被限流？**
抓取器内置重试与退避；网络不稳时可重跑 `python scripts/update_srefs.py`，已抓到的数据不会丢（`sources/` 里是原始结果，合并时会去重）。

**Q：Midlibrary 里为什么有 `--sref 10000` 这类短代码？**
Midlibrary 的 4,462 条中有约 100 条使用 5–6 位短编号（其余为 9–10 位），这是该站条目本身的写法。短编号不一定是无效代码，但建议正式出图前先用小图试跑确认；主流 9–10 位代码可直接使用。

## 8. 版权与免责

风格代码、预览图、提示词版权归原作者与原站点所有。本库仅做索引、去重、中文标注与检索，供个人学习与创作参考；请遵守各来源站点的使用条款，不要将图片用于商业再分发。
