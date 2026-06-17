# html-ppt-skill 融合方案 — 技术分析

> 分析日期: 2026-06-16
> 来源: https://github.com/lewislulu/html-ppt-skill
> 状态: 已下载核心资产到 D:\hermes\html-ppt-assets\

## 下载到的关键文件

| 文件 | 大小 | 用途 | 是否直接复用 |
|------|------|------|-------------|
| `assets/base.css` | 8KB | 设计 token 系统（颜色/字体/圆角/间距） | ✅ 是 |
| `assets/fonts.css` | 889B | Google WebFonts 加载 | ✅ 是 |
| `assets/runtime.js` | 37KB | 键盘导航+演讲者模式+主题切换+概览 | ✅ 是 |
| `assets/animations.css` | 8KB | 27 种 CSS 入场动画 | ✅ 是 |
| `assets/animations/fx-runtime.js` | 3KB | 20 种 Canvas 粒子动画运行时 | ⚠️ 按需 |
| `assets/themes/*.css` | 36×700B~1.5KB | 36 个主题覆盖 | ⚠️ 精选复用 |
| `templates/deck.html` | 3KB | 最小可用 deck 模板 | ✅ 参考结构 |
| `SKILL.md` | 14KB | 完整技能定义 | ✅ 已归档 |

## runtime.js 核心功能拆解

### 键盘快捷键（audience 窗口）
```
← → / Space / PgUp PgDn / Home End  → 翻页导航
F                                     → 全屏
S                                     → 打开演讲者弹窗（独立窗口）
N                                     → 底部备注抽屉
O                                     → 缩略图概览网格
T                                     → 循环切换主题（读 data-themes）
A                                     → 循环当前页动画
#/N                                   → URL 深链接
```

### 演讲者模式（S 键触发）
- `window.open()` 弹出独立窗口 (1280×820)
- **4 张磁吸卡片**：
  - 🔵 CURRENT — `<iframe src="deck.html?preview=N">` 像素级当前页预览
  - 🟣 NEXT — 同上，下一页预览
  - 🟠 SPEAKER SCRIPT — 大字逐字稿（从 `.notes` div 提取）
  - 🟢 TIMER — 计时器 + 页码 + prev/next/reset 按钮
- 卡片可拖拽（header）和调整大小（右下角 handle）
- 位置/尺寸存 `localStorage`（per deck）
- **iframe 同步机制**：
  - `postMessage({type:'preview-goto', idx:N})` — 翻页同步
  - `postMessage({type:'preview-theme', name:'...'})` — 主题同步
  - `BroadcastChannel('html-ppt-presenter-' + pathname)` — 双向同步
- **preview 模式**：`?preview=N` 参数锁定单页显示，隐藏 chrome

### 主题切换（T 键）
- 读 `<html data-themes="theme1,theme2,...">`
- 遍历切换 `<link id="theme-link">` 的 href
- 每个主题 CSS 只覆盖 `:root {}` 的 CSS 变量

### 动画系统
- CSS 动画：`data-anim="fade-up"` 或 `class="anim-fade-up"`
- 进入动画 27 种（animations.css）
- Canvas FX 20 种（fx-runtime.js 自动初始化 `[data-fx]`）
- 列表：`fade-up, fade-down, fade-left, fade-right, rise-in, drop-in, zoom-pop, blur-in, glitch-in, typewriter, neon-glow, shimmer-sweep, gradient-flow, stagger-list, counter-up, path-draw, parallax-tilt, card-flip-3d, cube-rotate-3d, page-turn-3d, perspective-zoom, marquee-scroll, kenburns, confetti-burst, spotlight, morph-shape, ripple-reveal`

## 与 ppt-master 的对接方案

### 架构决策
- **不合并代码库**，采用"插件式"增强
- ppt-master 负责内容和 SVG→PPTX 管线
- 新增 `scripts/html_export.py` 负责 HTML 生成
- 复用 html-ppt 的 CSS/JS 资源作为静态 assets

### Step 7 新增分支
```
Step 7.1: total_md_split.py → notes/page_N.md  （已有）
         ↓
Step 7.2: finalize_svg.py → svg_output/        （已有）
         ↓
Step 7.X: html_export.py → exports/deck.html + assets/  （新增）
         ↓
Step 7.3: svg_to_pptx.py → exports/*.pptx      （已有）
```

### html_export.py 输入/输出

**输入：**
- `svg_output/slide_N.svg` — 每页 SVG
- `notes/page_N.md` — 每页演讲者备注
- `spec_lock.md` — 颜色/字体/主题配置

**输出：**
```
exports/
├── deck.html                    — 主 HTML 文件
├── assets/
│   ├── base.css                 — 从 html-ppt 复制
│   ├── fonts.css                — 从 html-ppt 复制
│   ├── runtime.js               — 从 html-ppt 复制（精简版）
│   ├── animations.css           — 从 html-ppt 复制
│   ├── themes/
│   │   └── selected-theme.css   — 根据 spec_lock 生成
│   └── slides/
│       ├── slide_01.svg         — 内联 SVG 或引用
│       ├── slide_02.svg
│       └── ...
└── notes/                       — 逐字稿 HTML 副本
```

### HTML 结构映射
```html
<!-- ppt-master SVG → html-ppt slide -->
<section class="slide" data-title="Slide Title" data-theme="selected-theme">
  <img src="assets/slides/slide_01.svg" alt="Slide 1">
  <div class="notes">逐字稿内容（从 notes/page_01.md 提取）</div>
</section>
```

### 主题选择策略
从 36 个主题中精选 8 个最适合 ppt-master 场景的：
| 场景 | 推荐主题 |
|------|---------|
| 正式汇报/政府 | `corporate-clean`, `minimal-white` |
| 技术分享 | `tokyo-night`, `dracula` |
| 学术/教育 | `academic-paper`, `editorial-serif` |
| 创意/营销 | `cyberpunk-neon`, `neo-brutalism` |

## Windows 克隆失败的替代方案

当 GitHub 无法直接 clone 时：
```bash
# 方法1: 通过代理下载 tarball
curl -L --connect-timeout 30 --max-time 120 \
  https://ghproxy.net/https://github.com/lewislulu/html-ppt-skill/archive/refs/heads/master.tar.gz \
  -o html-ppt-skill.tar.gz
tar -xzf html-ppt-skill.tar.gz

# 方法2: 逐个下载关键文件（适合只需要少量文件时）
curl -sL --connect-timeout 30 --max-time 60 \
  https://ghproxy.net/https://raw.githubusercontent.com/lewislulu/html-ppt-skill/main/assets/base.css \
  -o base.css
```

## 注意事项

1. **SVG 嵌入方式**：ppt-master 的 SVG 有精确坐标，html-ppt 的 `.slide` 默认 flex 居中。需要在 base.css 中覆盖 `.slide img` 的样式为 `position:absolute; object-fit:contain;` 或内联 SVG
2. **字体离线**：Google Fonts 需要网络。离线环境用 `--local-fonts` 模式或替换为系统字体
3. **runtime.js 体积**：37KB 偏大。如果只需要演讲者模式，可精简出 `presenter-runtime.js`（去掉主题切换、概览等）
4. **iframe preview 模式**：需要 deck.html 和 preview iframe 同源（同一目录），否则 CORS 可能拦截 postMessage
5. **notes 提取**：ppt-master 的备注在 `.pptx` 的 `<a:notes>` 中，需要通过 `total_md_split.py` 或 `pptx_notes.py` 提取后传给 html_export
