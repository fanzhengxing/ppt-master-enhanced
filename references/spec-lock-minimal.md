---
name: spec-lock-minimal
description: Per-page spec_lock 精简版——只包含 SVG 生成真正需要的字段，用于减少每页 token 消耗
version: 1.0
---

# spec_lock_minimal.md — 精简版执行锁

> **定位**：这是 `spec_lock.md` 的精简投影，只保留 Executor 生成单个 SVG 页面时真正需要的字段。
> **用途**：每页生成前只读这个文件（而非完整 spec_lock.md），可减少 60-80% token 输入。
> **生成时机**：Strategist 在完成 spec_lock.md 后，自动生成对应的 spec_lock_minimal.md。

## 设计原则

1. **只保留 Executor 每页 SVG 生成直接读取的字段**
2. **删除设计叙事、 rationale、推荐说明等非运行时数据**
3. **保持与 spec_lock.md 相同的键名，确保 Executor 无需修改读取逻辑**

## 精简映射表

| spec_lock.md 节 | 保留？ | 说明 |
|----------------|--------|------|
| `## canvas` | ✅ 保留 | viewBox 和 format 是 SVG 根元素必需属性 |
| `## colors` | ✅ 保留 | 所有颜色值直接写入 SVG fill/stroke |
| `## colors.image_*` | ✅ 保留 | 仅在页面需要 AI 图片时用到 |
| `## typography` | ✅ 保留 | 字体族和尺寸直接写入 SVG text 元素 |
| `## icons` | ✅ 保留 | 库名和库存列表决定可用图标 |
| `## images` | ✅ 保留 | 当前页需要的图片路径 |
| `## page_rhythm` | ✅ 保留 | 决定页面布局纪律 |
| `## page_layouts` | ✅ 保留 | 决定模板继承 |
| `## page_charts` | ✅ 保留 | 决定图表结构 |
| `## forbidden` | ✅ 保留 | 质量检查规则 |
| `## design_spec.md` 交叉引用 | ❌ 删除 | 设计叙事不在 SVG 生成时需要 |
| `## 引导性 blockquotes` | ❌ 删除 | 所有 `>` 开头的说明性文字 |

## 输出格式

```markdown
# Execution Lock (Minimal)

## canvas
- viewBox: 0 0 1280 720
- format: PPT 16:9

## colors
- bg: #FFFFFF
- primary: #003366
- accent: #D4AF37
- secondary_accent: #1565C0
- text: #1D1D1F
- text_secondary: #6B7280
- border: #E5E7EB

## typography
- font_family: "Microsoft YaHei", Arial, sans-serif
- title_family: Georgia, SimSun, serif
- body_family: "Microsoft YaHei", "PingFang SC", Arial, sans-serif
- body: 22
- title: 32
- subtitle: 24
- annotation: 14

## icons
- library: chunk-filled
- inventory: target, bolt, shield, users, chart-bar

## images
- cover_bg: images/cover_bg.jpg

## page_rhythm
- P01: anchor
- P02: dense
- P03: breathing

## page_layouts
- P01: 01_cover
- P03: 03a_content_image_text

## page_charts
- P05: bar_chart

## forbidden
- Mixing icon libraries
- rgba()
- <style>, <class>, <foreignObject>, textPath, @font-face, <animate*>
- <g opacity>
- HTML named entities
```

## 注意事项

1. **颜色值**：只保留实际使用的颜色。未使用的行删除，不保留 `#......` 占位符。
2. **字体族**：只保留与 `font_family` 不同的 `*_family` 行。等于 `font_family` 的省略。
3. **图片**：只保留本项目实际引用的图片。
4. **页面节奏**：所有页面都必须有 `page_rhythm` 条目。
5. **模板和图表**：只在有模板继承或图表时使用。
6. **AI 图片**：当 `images` 中有 `ai` 来源的图片时，保留 `image_rendering` 和 `image_palette` 行。
7. **stroke_width**：当 `icons.library` 是 `tabler-outline` 时，保留 `stroke_width` 行。
