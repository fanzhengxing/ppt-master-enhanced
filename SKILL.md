---
name: ppt-master
description: >-
  AI-driven PPT generation — converts PDF/DOCX/Markdown/URL/text topic into native editable
  .pptx presentations. SVG→DrawingML pipeline (ppt-master-enhanced).
  Multi-role collaboration: Strategist (content planning) → Executor (SVG authoring)
  → Post-processing (native PPTX export). Works on Hermes, Claude Code, Codex,
  OpenClaw, and any skill-compatible runtime.
  Trigger: "create PPT", "make presentation", "生成PPT", "做PPT", "制作演示文稿",
  "做个PPT", "ppt-master".
  Do NOT use for: quick text→pptx without layout needs (use officecli-pptx instead),
  reading/analyzing existing .pptx content (use the powerpoint skill instead).
---

# PPT Master — Cross-Agent Public Edition

> 🎯 **把文档扔进来，拿走一个真正的、精美的、可编辑的 PowerPoint。**  
> 本地执行，不依赖任何外部 API。SVG→DrawingML 管线，原生形状、动画、演讲备注全保留。  
> 在 Hermes、Claude Code、Codex、OpenClaw 等 skill-compatible runtime 上均可运行。

## 🎯 场景选择指南 — 该走哪条路？

| 你的场景 | 推荐路线 | 输出 |
|---------|---------|------|
| **从文字/文档做正式PPT** | 主线：Step1→Step7（标准7步） | `.pptx` |
| **只有一个话题，没素材** | 先跑 `topic-research` 工作流（标准/深度两档）→ 再进主线 | `.pptx` |
| **有PPT/海报截图，想还原成可编辑PPTX** | 跑 `image-to-pptx` 工作流 | `.pptx` |
| **需要批量生成固定格式的报告** | 主线 + brand/layout模板锁定 | `.pptx` |
| **内部分享/技术演示（不一定要.pptx）** | 主线 + 附带 `presenter-view` 工作流 | `.pptx` + HTML演讲者视图 |
| **已有成品，想检查视觉质量** | 主线结束后跑 `visual-quality-check` 工作流 | 质量报告 |
| **品牌统一、多模板输出** | 主线 + `design-tokens.md` 约束求解 | 风格一致的多版本 |
| **已有.d2/架构图要嵌入PPT** | 主线中 SVG渲染阶段嵌入 | `.pptx`+图表 |
| **需要自定义动画/音乐/旁白** | 主线后跑 `customize-animations`/`generate-audio` 工作流 | `.pptx` 带动画/旁白 |
| **只想读/分析已有的.pptx** | 不要用ppt-master → 用 `powerpoint` skill | 内容提取 |

对比同类工具：
| 场景 | 用别人的？ | 用我们的？ |
|------|-----------|-----------|
| 纯HTML演示（多人在线分享） | **html-ppt-skill** | ppt-master做.pptx + presenter-view做HTML |
| 文档→多格式（含PDF） | **huashu-slides** | ppt-master（.pptx为主，未来加PDF输出） |
| 设计系统化/本地部署 | **Open Design** | ppt-master + design-tokens.md |
| 视觉质量优化 | **guizang-ppt-skill** | ppt-master + visual-quality-check工作流 |
| 批量自动化生成 | — | **ppt-master 主打路线** |

**Core Pipeline**: `Source → Init Project → [Template] → Strategist → [Images] → Executor (SVG) → Quality Check → Post-process → PPTX`

> [!CAUTION]
> ## 🚨 Global Execution Discipline (MANDATORY)
>
> **This workflow is a strict serial pipeline. The following rules have the highest priority — violating any one constitutes execution failure:**
>
> 1. **SERIAL EXECUTION** — Steps MUST execute in order; each step's output is the next step's input. Non-BLOCKING adjacent steps may proceed continuously once prerequisites are met, without waiting for "continue"
> 2. **BLOCKING = HARD STOP** — Steps marked ⛔ BLOCKING require a full stop; MUST wait for explicit user response before proceeding
> 3. **NO CROSS-PHASE BUNDLING** — The Eight Confirmations (Step 4) are ⛔ BLOCKING. After user confirms, all subsequent non-BLOCKING steps proceed automatically
> 4. **GATE BEFORE ENTRY** — Each Step has prerequisites (🚧 GATE); MUST verify before starting that Step
> 5. **NO SPECULATIVE EXECUTION** — "Pre-preparing" content for subsequent Steps is FORBIDDEN (e.g., writing SVG during Strategist phase)
> 6. **NO SUB-AGENT SVG GENERATION** — Executor SVG generation MUST be completed by the current main agent end-to-end
> 7. **SEQUENTIAL PAGE GENERATION** — SVG pages MUST be generated sequentially one-by-one
> 8. **SPEC_LOCK RE-READ PER PAGE** — Before each SVG page, re-read `spec_lock.md`. All colors/fonts/icons/images from this file only
> 9. **SVG MUST BE HAND-WRITTEN** — Every SVG page is written by the main agent directly. NO script-based batch generation

> [!IMPORTANT]
> ## 🌐 Language & Communication
> - **Response language**: match the user's input and source materials
> - **Template format**: `design_spec.md` follows English template structure; content in user's language

> [!IMPORTANT]
> ## 🔌 Cross-Runtime Compatibility
> - `ppt-master` runs on Hermes, Claude Code, Codex, OpenClaw, and any skill-compatible runtime
> - Script paths use `${SKILL_DIR}` (resolved at runtime by each agent)
> - On Hermes: `${SKILL_DIR}` = skill installation directory under `~/.hermes/skills/`
> - On Claude Code: `${SKILL_DIR}` = skill directory under `~/.claude/skills/ppt-master/`
> - On Windows: use `python` instead of `python3` if `python3` not found

## Directory Structure

```
ppt-master/
├── SKILL.md                    ← This file — complete workflow
├── README.md                   ← Public-facing README (sells the skill)
├── test-prompts.json           ← Acceptance test prompts
├── requirements.txt            ← Python dependencies
│
├── scripts/                    ← 42+ Python scripts (pipelines, utilities)
│   ├── source_to_md/           ← Document conversion (pdf, docx, excel, web)
│   ├── project_manager.py      ← Init / validate / manage projects
│   ├── svg_quality_checker.py  ← SVG validation
│   ├── svg_to_pptx.py          ← SVG → native PPTX export
│   ├── finalize_svg.py         ← Post-processing
│   ├── image_gen.py            ← AI image generation
│   ├── image_search.py         ← Web image search
│   ├── ...                     ← 28+ more (see scripts/ directory)
│
├── workflows/                  ← 13 standalone workflows
│   ├── topic-research.md       ← Web research (standard + Deep Research)
│   ├── template-fill-pptx.md   ← Fill existing PPTX template
│   ├── create-template.md      ← Create new layout/brand/deck template
│   ├── resume-execute.md       ← Split-mode execution (Phase A → B)
│   ├── verify-charts.md        ← Chart coordinate calibration
│   ├── customize-animations.md ← Animation tuning
│   ├── live-preview.md         ← Browser preview during gen
│   ├── visual-quality-check.md ← Visual quality inspection
│   ├── presenter-view.md       ← HTML presenter view
│   ├── visual-review.md        ← Per-page rubric check
│   ├── generate-audio.md       ← Voiceover generation
│   ├── create-brand.md         ← Brand-only identity preset
│   └── image-to-pptx.md        ← Image/screenshot → editable PPTX
│
├── references/                 ← Role definitions & technical constraints
│   ├── strategist.md, executor-base.md, shared-standards.md
│   ├── canvas-formats.md, image-layout-patterns.md
│   └── verified-pipeline.md    ← Pipeline verification record
│
├── templates/                  ← Layouts, brands, decks, charts
│   ├── layouts/                ← 7+ page layout templates
│   ├── brands/                 ← Brand identity presets
│   ├── decks/                  ← Full deck templates
│   ├── charts/                 ← Chart SVG templates
│   └── icons/                  ← Icon libraries (README.md for usage)
│
└── projects/                   ← Generated projects (gitignored)
```

## Main Scripts

| Script | Purpose |
|--------|---------|
| `${SKILL_DIR}/scripts/source_to_md/pdf_to_md.py` | PDF → Markdown |
| `${SKILL_DIR}/scripts/source_to_md/doc_to_md.py` | DOCX/HTML/EPUB → Markdown (pandoc fallback for legacy) |
| `${SKILL_DIR}/scripts/source_to_md/excel_to_md.py` | XLSX → Markdown |
| `${SKILL_DIR}/scripts/source_to_md/ppt_to_md.py` | PPTX → Markdown |
| `${SKILL_DIR}/scripts/source_to_md/web_to_md.py` | URL → Markdown (supports WeChat via curl_cffi) |
| `${SKILL_DIR}/scripts/project_manager.py` | Project init / validate / manage |
| `${SKILL_DIR}/scripts/analyze_images.py` | Image analysis |
| `${SKILL_DIR}/scripts/latex_render.py` | LaTeX formula → PNG |
| `${SKILL_DIR}/scripts/image_gen.py` | AI image generation (multi-provider) |
| `${SKILL_DIR}/scripts/image_search.py` | Web image search |
| `${SKILL_DIR}/scripts/svg_quality_checker.py` | SVG quality check |
| `${SKILL_DIR}/scripts/total_md_split.py` | Speaker notes splitting |
| `${SKILL_DIR}/scripts/finalize_svg.py` | SVG post-processing (unified entry) |
| `${SKILL_DIR}/scripts/svg_to_pptx.py` | SVG → native PPTX export |
| `${SKILL_DIR}/scripts/update_spec.py` | Propagate spec_lock color/font changes across SVGs |

> **Windows note**: if `python3` fails (common on python.org installs), use `python`.

## Template Index

| Index | Path | Purpose |
|-------|------|---------|
| Layouts | `${SKILL_DIR}/templates/layouts/layouts_index.json` | Available page layout templates |
| Brands | `${SKILL_DIR}/templates/brands/brands_index.json` | Brand identity presets (color/typography/logo/voice) |
| Charts | `${SKILL_DIR}/templates/charts/charts_index.json` | Chart SVG templates |
| Icons | `${SKILL_DIR}/templates/icons/` | Icon libraries; search with `ls ... \| grep <keyword>` |

## Standalone Workflows

| Workflow | Path | When to Use |
|----------|------|-------------|
| Topic Research | `workflows/topic-research.md` | User supplies only a topic — gather web sources first |
| Template Fill | `workflows/template-fill-pptx.md` | User has an existing PPTX template to fill |
| Create Template | `workflows/create-template.md` | Create a new layout/brand/deck template |
| Create Brand | `workflows/create-brand.md` | Brand-only identity preset |
| Resume Execute | `workflows/resume-execute.md` | Split mode — resume Phase B in a fresh chat |
| Verify Charts | `workflows/verify-charts.md` | Chart coordinate calibration after SVG gen |
| Customize Animations | `workflows/customize-animations.md` | User wants to tune per-object animation order/effects |
| Live Preview | `workflows/live-preview.md` | Browser-based live preview during generation |
| Visual Review | `workflows/visual-review.md` | Per-page rubric visual self-check (opt-in) |
| **Image to PPTX** | **`workflows/image-to-pptx.md`** | **图片/截图 → 可编辑PPTX逆向还原** |
| **Visual Quality Check** | **`workflows/visual-quality-check.md`** | **视觉质量检查（对比度/留白/对齐/层级）** |
| **Presenter View** | **`workflows/presenter-view.md`** | **演讲者视图HTML生成（内部分享/演示用）** |

> ⚡ **Topic Research** 工作流支持两档搜索：**标准模式**（快速覆盖基本信息）和 **Deep Research 模式**（多源交叉→深度抓取→结构化综合），用户说"深入了解/全面调研"时自动触发。

---

## Workflow

### Step 1: Source Content Processing

🚧 **GATE**: User has provided source material (PDF / DOCX / EPUB / URL / Markdown / text description / conversation content).

> **No source content?** If the user supplies only a topic name without files or substantial description, run the [`topic-research`](workflows/topic-research.md) workflow first, then return here with its products.

Convert non-Markdown content immediately:

| User Provides | Command |
|---------------|---------|
| PDF file | `python3 ${SKILL_DIR}/scripts/source_to_md/pdf_to_md.py <file>` |
| DOCX / Word / Office | `python3 ${SKILL_DIR}/scripts/source_to_md/doc_to_md.py <file>` |
| XLSX / XLSM / Excel | `python3 ${SKILL_DIR}/scripts/source_to_md/excel_to_md.py <file>` |
| CSV / TSV | Read directly as plain-text table |
| PPTX / PowerPoint | `python3 ${SKILL_DIR}/scripts/source_to_md/ppt_to_md.py <file>` |
| EPUB / HTML / LaTeX / RST | `python3 ${SKILL_DIR}/scripts/source_to_md/doc_to_md.py <file>` |
| Web link | `python3 ${SKILL_DIR}/scripts/source_to_md/web_to_md.py <URL>` |
| WeChat / high-security site | `python3 ${SKILL_DIR}/scripts/source_to_md/web_to_md.py <URL>` (requires `curl_cffi`) |
| Markdown | Read directly |

> **Office vector assets (EMF/WMF)**: `doc_to_md.py` / `ppt_to_md.py` extract embedded vector images alongside bitmaps. After `import-sources`, these land in `images/` with `image_manifest.json`. Do NOT convert EMF/WMF to PNG — `svg_to_pptx.py` embeds them natively. Browser preview cannot render EMF (expected — PPTX is source of truth).

> **Failure handling**: If a converter fails (missing dependency, unsupported format, corrupted file), report the specific error and suggest alternatives (e.g., "Try saving as .docx first" for legacy .doc, or "Install pandoc" for RST/LaTeX).

**✅ Checkpoint — Proceed to Step 2.**

---

### Step 2: Project Initialization

🚧 **GATE**: Step 1 complete; source content is ready.

```bash
python3 ${SKILL_DIR}/scripts/project_manager.py init <project_name> --format <format>
```

Format options: `ppt169` (default, 16:9), `ppt43` (4:3), `xhs` (小红书), `story`, etc. Full list: `references/canvas-formats.md`.

Import source content:

| Situation | Action |
|-----------|--------|
| Has source files (PDF/MD/etc.) | `python3 ${SKILL_DIR}/scripts/project_manager.py import-sources <project_path> <source_files...> --move` |
| User-provided text in conversation | No import needed — content is in context |

> ⚠️ **MUST use `--move`** (not copy): all source files go into `sources/`. After execution they no longer exist at the original location.

> **Failure handling**: If `project_manager.py` reports "project already exists", prompt user for a different project name or `--force`. If the converter produced no output (`sources/` empty), revisit Step 1.

**✅ Checkpoint — Proceed to Step 3.**

---

### Step 3: Template Option

🚧 **GATE**: Step 2 complete; project directory structure ready.

**Default — free design.** Proceed directly to Step 4. Do NOT query any `*_index.json` unless triggered. Do NOT ask the user. Do NOT proactively suggest templates.

**Template flow triggers ONLY on explicit directory paths** from the user's initial message. A bare name without a resolvable directory path does not trigger.

| User input contains | Step 3 action |
|---------------------|---------------|
| One or more explicit template paths (each resolves to a `design_spec.md` with `kind: brand/layout/deck`) | Read each spec's `kind`, dispatch per kind matrix below, fuse if multiple |
| Anything else — bare names, style descriptions, or silence | Skip Step 3, free design |

**Three template kinds** (schema: `docs/zh/templates-architecture.md`):

| Kind | Physical dir | Contains |
|------|-------------|----------|
| **brand** | `templates/brands/<id>/` | Identity: color/typography/logo/voice/icon style |
| **layout** | `templates/layouts/<id>/` | Structure: canvas/page structure/page types/SVG roster |
| **deck** | `templates/decks/<id>/` | Full replica: identity + structure + overview |

**Single-path dispatch**:
- `kind: brand` → Copy `design_spec.md` + logo + assets. Identity locked; structure free.
- `kind: layout` → Copy spec + SVG roster + assets. Structure locked; identity free.
- `kind: deck` → Copy everything. All locked.

**Multi-path fusion** (different kinds): Fuse segments by priority — brand wins identity, layout wins structure, deck fills middle. See full fusion matrix in `docs/zh/templates-architecture.md`.

> **Failure handling**: If template directory doesn't contain a valid `design_spec.md`, report the invalid path and suggest listing available templates via `ls ${SKILL_DIR}/templates/layouts/`.

**✅ Checkpoint — Default path proceeds to Step 4 automatically.**

---

### Step 4: Strategist Phase (MANDATORY — cannot be skipped)

🚧 **GATE**: Step 3 complete.

First, read the role definition:
```text
Read references/strategist.md
```

> ⚠️ **Mandatory gate**: before writing `design_spec.md`, Strategist MUST `read_file templates/design_spec_reference.md` and follow its I–XI section structure.

#### Eight Confirmations

⛔ **BLOCKING**: Present the Eight Confirmations as a bundled recommendation set and **wait for explicit user confirmation** before outputting design spec.

1. **Canvas format** — 16:9 / 4:3 / story / custom
2. **Page count range** — estimated based on source material
3. **Target audience** — who will see this deck
4. **Style objective** — professional / academic / creative / minimalist / etc.
5. **Color scheme** — from template or recommended palette
6. **Icon usage approach** — icon library, stroke vs filled, density
7. **Typography plan** — including formula rendering policy (mixed/render-all/text-only)
8. **Image usage approach** — AI-generated / web-sourced / user-provided / placeholder

**Split-mode note** (mandatory, appended after the eight items):
- Heavy (long deck / bulky sources): Recommend split mode — stop this chat, open fresh window, use `继续生成 projects/<name>` for Phase B
- Normal: Default continuous mode; can switch to split mode any time with `继续生成 projects/<name>`

**Formula rendering policy** (inside item 7):
| Policy | Behavior |
|--------|----------|
| `mixed` (default) | Complex formulas → PNG; inline expressions → editable text |
| `render-all` | All formula-worthy expressions → PNG |
| `text-only` | No rendering; formulas stay as editable text |

After confirmation and **before outputting `design_spec.md`**, if formula policy is `mixed` or `render-all`:
1. Identify expressions for LaTeX rendering
2. Write `<project_path>/images/formula_manifest.json`
3. Run: `python3 ${SKILL_DIR}/scripts/latex_render.py <project_path>`
4. Include rendered PNGs in `design_spec.md §VIII`

**Output**:
- `<project_path>/design_spec.md` — Human-readable design narrative
- `<project_path>/spec_lock.md` — Machine-readable execution contract

**Checkpoint**:
```markdown
## ✅ Strategist Phase Complete
- [x] Eight Confirmations completed (user confirmed)
- [x] Design Specification & Content Outline generated
- [x] spec_lock.md generated
- [ ] **Next**: Auto-proceed to Image Acquisition / Executor
```

---

### Step 5: Image Acquisition Phase (Conditional)

🚧 **GATE**: Step 4 complete. Any formula rows have `Status: Rendered`.

**Trigger**: At least one row in `design_spec.md §VIII` has `Acquire Via: ai` or `web`. If all are `user`/`formula`/`placeholder`, skip to Step 6.

Load reference:
```text
Read references/image-base.md
```

Then dispatch per `Acquire Via`:
| Via | Load | Run |
|-----|------|-----|
| `ai` | `references/image-generator.md` | `python3 ${SKILL_DIR}/scripts/image_gen.py --manifest <project_path>/images/image_prompts.json` |
| `web` | `references/image-searcher.md` | `python3 ${SKILL_DIR}/scripts/image_search.py ...` |

Workflow:
1. Extract all rows with `Status: Pending`, `Acquire Via ∈ {ai, web}`
2. Generate prompts (ai) and/or search (web) per image-base.md §2
3. Verify each row reaches: `Generated` / `Sourced` / `Needs-Manual`

> **Failure handling**: On acquisition failure, retry once, then mark `Needs-Manual`, report to user, and continue.

**Checkpoint**:
```markdown
## ✅ Image Acquisition Complete
- [x] image_prompts.json / image_sources.json created
- [x] Each row: terminal status (no Pending remaining)
```

**Default — auto-proceed to Step 6.** If user opted into split mode, output Phase A hand-off marker:
```markdown
## ✅ Phase A Complete
- [x] Spec: design_spec.md, spec_lock.md
- [x] Resources: sources/, images/, templates/
- [ ] **Next**: Open fresh chat → `继续生成 projects/<name>` + resume-execute workflow
```

---

### Step 6: Executor Phase

🚧 **GATE**: Step 4 (and Step 5 if triggered) complete.

Read role definition:
```text
Read references/executor-base.md
Read references/shared-standards.md
Read references/executor-general.md  # or executor-consultant.md / consultant-top.md
```

**Design Parameter Confirmation**: Before first SVG, output key design parameters (canvas, colors, fonts, body font size).

**Live Preview Auto-Startup** (Mandatory):
```bash
python3 ${SKILL_DIR}/scripts/svg_editor/server.py <project_path> --live
```
- Starts at `http://localhost:5050` (port conflict → `--port <other>`)
- Do NOT wait for it to exit. Keeps running until user clicks Exit or says stop in chat.
- Do NOT read/apply annotations during generation — window opens after Step 7.

**Pre-generation Batch Read**: Before the first SVG, batch-read every distinct layout SVG in `spec_lock.page_layouts` and chart SVG in `spec_lock.page_charts`. One read per file, up front.

**Per-page spec_lock re-read**: Before **each** SVG page, `read_file <project_path>/spec_lock.md`. Colors/fonts/icons/images from this file only. Also read `page_rhythm` / `page_layouts` / `page_charts` for that page.

**Visual Construction**: Generate SVG pages sequentially, one at a time → `<project_path>/svg_output/`.

**Quality Check Gate** (after all SVGs):
```bash
python3 ${SKILL_DIR}/scripts/svg_quality_checker.py <project_path>
```
- `error` → Must fix before proceeding
- `warning` → Fix when straightforward, otherwise acknowledge and release

**Logic Construction**: Generate speaker notes → `<project_path>/notes/total.md`

> **Chart pages?** If the deck contains data charts, run `workflows/verify-charts.md` before Step 7.
> **Visual review (opt-in)?** Only if user explicitly asked — run `workflows/visual-review.md`.

**Spec_lock drift warnings**: `svg_quality_checker.py` may report spec_lock drift for template-native colors (`#F5F7FA`, `#E6F3FA`, etc.) not listed in spec_lock. These are safe to ignore — best practice is to add template auxiliary colors to spec_lock's `colors` section, but not blocking.

**Checkpoint**:
```markdown
## ✅ Executor Phase Complete
- [x] Live preview available at URL
- [x] All SVGs generated to svg_output/
- [x] svg_quality_checker passed (0 errors)
- [x] Speaker notes at notes/total.md
```

---

### Step 7: Post-processing & Export

🚧 **GATE**: Step 6 complete. Image readiness gate: every expected file must exist at `<project>/images/<filename>`.

Run three sub-steps **one at a time** — never combine them:

**Step 7.1** — Split speaker notes:
```bash
python3 ${SKILL_DIR}/scripts/total_md_split.py <project_path>
```

**Step 7.2** — SVG post-processing (icon/embed, image crop/embed, text flattening, rounded rect → path):
```bash
python3 ${SKILL_DIR}/scripts/finalize_svg.py <project_path>
```

**Step 7.3** — Export PPTX (embeds speaker notes by default):
```bash
python3 ${SKILL_DIR}/scripts/svg_to_pptx.py <project_path>
# Output: exports/<project_name>_<timestamp>.pptx  (native)
#         backup/<timestamp>/svg_output/            (SVG source backup)
```

**Optional animation flags** (defaults already give rich entrance animations — adjust only when user asks):
| Flag | Description |
|------|-------------|
| `-t <effect>` | Page transition. Default `fade`. Options: fade/push/wipe/split/strips/cover/random/none |
| `-a <effect>` | Per-element animation. Default `auto`. Options: fade/none/mixed |
| `--animation-trigger {on-click,with-previous,after-previous}` | Start mode. Default `after-previous` |
| `--auto-advance <seconds>` | Kiosk-style auto-play |

> **File list**: `finalize_svg.py` and `svg_to_pptx.py` do not detect missing image files at the script layer — if images are missing, the deck will have broken references. Verify files exist before Step 7.

> **Paragraph editability vs line fidelity**: Default merge behavior collapses dy-stacked paragraphs into one editable text frame. Add `--no-merge` for strict line-layout fidelity.

**Post-export annotation window**: If user submitted annotations during generation, run `workflows/live-preview.md` Step 2 to apply and re-export.

**Checkpoint**:
```markdown
## ✅ Post-processing Complete
- [x] Speaker notes split
- [x] SVG post-processed
- [x] Native .pptx exported at <path>
```

---

## Role Switching Protocol

Before switching roles, read the corresponding reference file. Output marker:
```markdown
## [Role Switch: <Role Name>]
📖 Reading: references/<filename>.md
📋 Current task: <brief description>
```

---

## Reference Resources

| Resource | Path |
|----------|------|
| Shared technical constraints | `references/shared-standards.md` |
| Canvas format specification | `references/canvas-formats.md` |
| Image-text layout patterns | `references/image-layout-patterns.md` |
| Image layout sizing | `references/image-layout-spec.md` |
| SVG image embedding | `references/svg-image-embedding.md` |
| Icon library | `templates/icons/README.md` |
| Animations | `references/animations.md` |
| Design Tokens | `references/design-tokens.md` | 设计系统Token抽象层（L0/L1/L2） |
| Verified pipeline | `references/verified-pipeline.md` |

---

## 🛑 Anti-Patterns (Do NOT Do)

- ❌ Do NOT combine steps 7.1/7.2/7.3 into one code block or shell invocation
- ❌ Do NOT use `cp` as a substitute for `finalize_svg.py` — finalize does critical processing
- ❌ Do NOT delegate SVG page generation to sub-agents
- ❌ Do NOT batch SVG pages (5 at a time) — generate one by one
- ❌ Do NOT pre-write SVG code during Strategist phase
- ❌ Do NOT skip the Eight Confirmations ⛔ BLOCKING
- ❌ Do NOT keep hardcoded personal paths, API keys, or credentials in the skill
- ❌ Do NOT default to calling external APIs for PPT generation — this skill runs fully local
- ❌ Do NOT use `git reset --hard` for rollback; use patch/revert
- ❌ Do NOT write "supports everything" or "fully automatic" in user-facing descriptions — be specific

## 🔒 Security & Safety

- **Local-only**: All scripts run locally. No data is sent to external PPT generation services
- **API keys**: AI image generation (Step 5) may require optional API keys — user configures their own
- **File operations**: PPT export writes to `<project>/exports/`. The skill never deletes files outside the project directory
- **Template isolation**: Custom templates are user-controlled; only reference files from the skill's template library
- **Split mode**: When using split mode, Phase A assets live in the project directory on disk — user controls access

## ✅ Acceptance Checklist

Before declaring the pipeline complete:
- [ ] Source content processed (Step 1)
- [ ] Project initialized with sources imported (Step 2)
- [ ] Template dispatched or free-design path taken (Step 3)
- [ ] Eight Confirmations confirmed by user (Step 4) ⛔
- [ ] Design spec + spec_lock generated (Step 4)
- [ ] Images acquired (Step 5, if applicable)
- [ ] SVG pages generated, one by one (Step 6)
- [ ] Quality check passed — 0 errors (Step 6)
- [ ] Speaker notes generated (Step 6)
- [ ] Post-processing complete (Step 7.1–7.3)
- [ ] Native .pptx exported and path reported to user

---

## Notes

- Local preview of SVG output: `python3 -m http.server -d <project_path>/svg_final 8000`
- **Troubleshooting**: On layout overflow / export errors / blank images, check `docs/faq.md`
- **Supported formats**: 16:9 (default), 4:3, story, xhs, custom
- **Supported source types**: PDF, DOCX, XLSX, PPTX, MD, URL, EPUB, HTML, LaTeX, RST, CSV, conversation text
