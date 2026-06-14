---
name: image-to-pptx
description: >-
  把「图片格式的PPT文档/幻灯片截图/设计稿截图」逆向还原成可编辑的.pptx。
  LLM视觉分析四层（背景/框架/图标/文字）→ 生成layout.json → compose_pptx.py合成。
  当用户说"把这页PPT图片转可编辑PPTX/还原截图PPT/把图片变成可编辑的PPT"时使用。
  输入是图片，输出是可编辑 .pptx。
---

# Image-to-PPTX — 图片PPT → 可编辑PPTX

> 一张一张处理，拆成四层再组装成可编辑 .pptx：
> 背景层 → 框架层（卡片/分割线/图表图形）→ 图标层 → 文字层（真文本框）

## 四层流程（B1-B9）

### B1：创建任务目录
```bash
mkdir -p image2pptx_runs/<时间戳>_<源图slug>/
RUN_ROOT=image2pptx_runs/<时间戳>_<源图slug>
```
任务隔离——每个图片任务独立目录，禁止串文件。

### B2：复刻背景图
用 imagegen 或简单图像处理，提取/复刻干净的背景（去掉前景元素）。保存为 `$RUN_ROOT/01-bg.png`。

### B3：提取整体框架图
框架 = 背景、图标、文字之外的所有图像元素：
- 容器/卡片（含底色填充与标题条）
- 分隔线、连接线
- 图表图形（折线/柱状/饼图/坐标网格/趋势线）
- 缎带、装饰线条与色块

用 imagegen 在纯色抠图底上生成全幅框架层，保存为 `$RUN_ROOT/frame.png`。
**规则**：形状·大小·位置与原图 1:1 一致。默认整张框架图不动（用户要求切分时才切）。

### B4：提取元素图标/装饰
用 imagegen 在纯色抠图底上生成图标表（不画网格分割线），保存为 `$RUN_ROOT/icons_sheet.png`。
然后用 `slice_grid.py` 按透明区域切成独立图标 → `$RUN_ROOT/icons/*.png`。

### B5：GPT视觉提取文字
用 LLM 视觉能力逐页分析图片，输出每页的文字内容、位置、大小、颜色、字体、对齐方式。
注意区分**艺术字**（归入B4图标层）和普通文本。

### B6：生成 layout.json
按以下 schema 编写：

```json
{
  "slide_width_in": 13.333,
  "slide_height_in": 7.5,
  "units": "fraction",
  "assets_dir": "$RUN_ROOT",
  "slides": [
    {
      "background": "01-bg.png",
      "frame": "frame.png",
      "icons": [
        {"file": "icons/icon_01.png", "x": 0.1, "y": 0.2, "w": 0.08, "h": 0.08}
      ],
      "texts": [
        {"text": "标题文字", "x": 0.08, "y": 0.05, "w": 0.6, "h": 0.12,
         "size_ratio": 0.074, "color": "#1A1A1A", "bold": true,
         "align": "left", "font": "Microsoft YaHei"}
      ]
    }
  ]
}
```

`x/y/w/h` 为 0-1 比例值（相对于幻灯片宽高）。

### B7：compose_pptx 合成
```bash
python3 scripts/compose_pptx.py $RUN_ROOT/layout.json $RUN_ROOT/output.pptx
```

### B8：预览检查
```bash
python3 scripts/placement_qa.py $RUN_ROOT/layout.json --preview-dir $RUN_ROOT/preview
```

### B9：交付
```bash
cp $RUN_ROOT/output.pptx exports/<项目名>_<时间戳>.pptx
```

## 与 ppt-master 主管线的关系

| 流程 | Image-to-PPTX | ppt-master 主线 |
|------|--------------|-----------------|
| 输入 | 图片（截图/设计稿） | 文本/文档/Markdown |
| 文字来源 | LLM视觉提取 | 原文直接使用 |
| 图片层 | imagegen生成或提取 | SVG生成 |
| 输出 | 可编辑 .pptx | 可编辑 .pptx |
| 共用脚本 | compose_pptx.py / placement_qa.py | 共用 |

**主要差异**：Image-to-PPTX 不需要 strategist/executor 阶段——直接从图片逆向工程出 layout.json。

## 安全边界
- ✅ 只处理用户提供的图片
- ✅ 所有中间产物在独立的 `RUN_ROOT` 目录
- ❌ 不修改已有文件
- ❌ 不发送图片到外部（imagegen 可选本地或API）
