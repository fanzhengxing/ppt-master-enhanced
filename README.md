<div align="center">

# 🏗️ PPT Master

> **把文档扔进来，拿走一个真正的、精美的、可编辑的 PowerPoint。**  
> 本地执行，不依赖任何外部 API。SVG→DrawingML 管线，原生形状、动画、演讲备注全保留。

[![Agent Skills](https://img.shields.io/badge/Agent%20Skills-ppt--master-blueviolet)](SKILL.md)
[![Stars](https://img.shields.io/github/stars/fanzhengxing/ppt-master-enhanced?style=flat&color=yellow)](https://github.com/fanzhengxing/ppt-master-enhanced)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

**Hermes · Claude Code · Codex · OpenClaw · 任何 skill-compatible runtime**

[工作原理](#工作原理) · [快速开始](#快速开始) · [模板](#模板) · [它和同类有什么不同](#它和同类有什么不同)

</div>

---

## 你什么时候需要它？

| 场景 | 以前怎么做 | 现在怎么做 |
|------|-----------|-----------|
| 📄 一份 PDF 报告要转成 PPT | 手动复制粘贴，一页一页排版 | 把 PDF 扔过来，拿走 .pptx |
| 🎓 学术答辩/论文汇报 | 用 LaTeX Beamer 或手画 | 论文→Markdown→精美模板 PPT |
| 📊 Excel 数据要变成汇报 | 复制图表，调格式半小时 | XLSX 直接作为源材料 |
| 🌐 网页内容要做演示 | 开浏览器截图，拼到 PPT | 把 URL 扔过来 |

## 它会交付什么？

- ✅ **原生 .pptx** — 可在 PowerPoint / WPS / Keynote 中编辑，不是图片也不是 HTML
- ✅ **原生形状** — 文本框、矩形、圆角、图标、图表，全部是 DrawingML 原生元素
- ✅ **演讲备注** — 自动生成每页备注，演讲时照着念
- ✅ **入场动画** — 默认丰富动画，可定制
- ✅ **多模板** — 学术答辩、政务蓝/红、医学大学、像素复古等 7+ 套布局

## 快速开始

```bash
# Hermes
npx skills add LearnPrompt/luban-skill -g   # 先装鲁班 skill 管理
# 或直接：让 AI 加载 ppt-master skill

# Claude Code
/plugin marketplace add LearnPrompt/ppt-master
# 或直接说：加载 ppt-master skill
```

装完对 AI 说：

```text
帮我把这份文档做成 PPT：[文件路径/URL]
```

## 工作原理

```
源文档 (PDF/DOCX/MD/URL)
    │
    ▼
[Step 1] 内容处理 ──→ 转成 Markdown
    │
    ▼
[Step 2] 项目初始化 ──→ 创建项目目录结构
    │
    ▼
[Step 3] 模板选择 ──→ 自由设计 / 品牌 / 布局 / 全套模板
    │
    ▼
[Step 4] 策略师 ──→ 八项确认 ⛔ → 输出设计规格书
    │
    ▼
[Step 5] 图片获取 ──→ AI 生成 / 网络搜索 / 用户提供
    │
    ▼
[Step 6] 执行师 ──→ 逐页生成 SVG → 质量检查 → 演讲备注
    │
    ▼
[Step 7] 后处理 ──→ 展平 → 嵌入 → 导出原生 PPTX
```

## 模板

| 模板 | 路径 | 适用场景 |
|------|------|----------|
| 自由设计 | (默认) | 任何场景，AI 自动配风格 |
| 学术答辩 | `templates/layouts/academic_defense/` | 论文答辩、学术汇报 |
| AI 运维 | `templates/layouts/ai_ops/` | 技术运维、IT 汇报 |
| 政务蓝色 | `templates/layouts/government_blue/` | 政府汇报、政务公开 |
| 政务红色 | `templates/layouts/government_red/` | 党建、重要会议 |
| 医科大学 | `templates/layouts/medical_university/` | 医学汇报、医院报告 |
| 像素复古 | `templates/layouts/pixel_retro/` | 创意演示、hackathon |
| 心理学 | `templates/layouts/psychology_attachment/` | 心理咨询、教育 |

## 它和同类有什么不同？

| | 普通 Agent 做 PPT | **PPT Master** |
|---|---|---|
| 输出产物 | HTML / Markdown / 文字描述 | **原生 .pptx**（可编辑） |
| 排版引擎 | AI 临时构思 | **SVG→DrawingML 管线** |
| 模板系统 | 无 / 硬编码 | 7+ 套独立布局 + 品牌预设 |
| 演讲备注 | 通常没有 | ✓ 自动生成 |
| 动画 | 无 | ✓ 入场动画 + 页面切换 |
| 外部依赖 | 常需要 API (Gamma/美图) | **纯本地**，无需任何外部服务 |
| 脚本资产 | 无 | 41 个 Python 脚本 + 11 个工作流 |
| 编辑性 | 不可编辑 / 需重新生成 | ✓ 在 PowerPoint 里直接改 |

## 安全边界

- **纯本地执行** — 所有处理和生成在本地完成，不调用任何外部 PPT 生成服务
- **AI 图片生成**（Step 5）可能需要用户配置自己的 API key
- **文件操作范围**限制在项目目录内，不会删除外部文件
- **不收集任何使用数据** — 无遥测、无分析

## 验证与测试

装完用这句验收：

```text
让 ppt-master 帮我把这个 Markdown 做成 PPT：[任意 .md 文件]
```

合格表现：它会先问源文件内容，然后依次执行 8 步管线，产出 .pptx 文件。

或者直接跑 `test-prompts.json` 里的测试场景。

---

## License

MIT — 随便用，随便改，随便集成。
