---
description: Post-SVG visual quality inspection — runs svg_quality_checker.py then AI scan for contrast, whitespace balance, and alignment across the full deck
---

# Visual Quality Check Workflow

> Standalone post-generation step. Run after Executor finishes all SVG pages and before post-processing & export. Catches both technical SVG violations (via script) and visual quality issues (contrast ratio, whitespace imbalance, alignment drift) via quick AI scan.
>
> This workflow is **independent** — safe to invoke in a fresh chat with only `<project_path>` as input.

**Scope**: deck-level quality gate. For deep per-page rubric review with AI subagents scoring each slide individually, use [`visual-review`](./visual-review.md) instead. Run this first; escalate to visual-review only when the user explicitly asks.

## When to Run

- Executor (SKILL.md Step 6) has finished all SVG pages in `<project_path>/svg_output/`
- Post-processing (`finalize_svg.py`, `svg_to_pptx.py`) has **not** yet run
- User asks to "检查视觉质量" / "check visual quality" / "quality check" / "QC" the deck

## When NOT to Run

- SVG pages don't exist yet — finish Executor first
- User asked for deep per-slide rubric review → use `visual-review` workflow instead
- The deck has already been exported and the user only wants to read/share it → no re-check needed

---

## Step 1: Technical Quality Check (Script)

```bash
python3 ${SKILL_DIR}/scripts/svg_quality_checker.py <project_path>
```

The checker scans every `.svg` in `svg_output/` and reports:

| Severity | Meaning | Action |
|----------|---------|--------|
| `error` | Forbidden SVG feature, broken XML, spec_lock drift, missing file | **Must fix before proceeding** |
| `warning` | Suboptimal but exportable (e.g. template auxiliary color not in spec_lock) | Fix if straightforward; acknowledge and release otherwise |

**Common errors and fixes**:

| Error | Fix |
|-------|-----|
| `<foreignObject>` found | Replace with native SVG text elements |
| `rgba()` in fill/stroke | Change to `fill="#HEX" fill-opacity="0.X"` |
| `<style>` or `class` attribute | Move all styles to inline attributes; remove `<style>` block |
| `<symbol>` + `<use>` (non-icon) | Expand symbol inline; `<use data-icon="...">` is allowed |
| HTML entity (`&mdash;`, `&nbsp;`) | Replace with raw Unicode character (`—`, ` `) |
| Bare `&` or `<` in text | Escape as `&amp;` or `&lt;` |
| Missing image file | Verify `images/` directory; re-run image acquisition if needed |

Fix all `error`-level issues, re-run the checker, and confirm 0 errors before Step 2.

---

## Step 2: Visual Quality Scan (AI)

Read `<project_path>/spec_lock.md` (or `spec_lock_minimal.md`), then inspect each SVG in `svg_output/` sequentially across three quality dimensions:

### A. Contrast

- **Text on background**: body text (`fill` on `<text>`) must achieve at least 4.5:1 contrast against the element behind it. Titles may use 3:1 when large (font-size ≥ 28px bold).
- **Brand color on white**: check primary/accent colors defined in spec_lock against white (`#FFFFFF`) and the deck's background color.
- **Flag**: any text element where estimated contrast < 3:1 against its immediate background.

> Contrast estimation: approximate from HEX luminance. For `#RRGGBB`, relative luminance `L = 0.2126R + 0.7152G + 0.0722B` (linearized). Ratio = `(L_lighter + 0.05) / (L_darker + 0.05)`.

### B. Whitespace Balance

Per slide, check:
- **Content density**: if more than 75% of the viewBox area is covered by non-background elements, flag as over-dense.
- **Margin clearance**: text elements closer than 40px to any canvas edge are flagged (default margin floor per `references/executor-base.md`).
- **Blank gutters**: if a slide has a clearly split two-column layout, check that the gutter between columns is ≥ 40px.

### C. Alignment

Scan for elements that are *almost* aligned but not quite — the most common visual polish issue:

- **Grid drift**: elements in a grid (cards, list items, process steps) whose top/left edges differ by 1–5px when they should be identical.
- **Text baseline drift**: adjacent text elements on the same visual row whose `y` coordinates differ by < 3px (should be identical) or between 3–8px (suspicious — flag for review).
- **Icon-text misalignment**: `<use data-icon>` elements paired with adjacent `<text>` — their visual centers should align within 4px vertically.

---

## Step 3: Quality Report

Output a compact structured report:

```
## Visual Quality Check — <project_name>

### Script Check (svg_quality_checker.py)
- Status: ✅ 0 errors, N warnings
- [List any warnings with file names]

### Contrast
- ✅ All checked / ⚠️ N issues found
- [Issue]: <page>.svg — <element description>: estimated ratio ~X:1 (minimum 4.5:1 required)

### Whitespace Balance
- ✅ All clear / ⚠️ N issues found
- [Issue]: <page>.svg — [over-dense | margin violation | narrow gutter]

### Alignment
- ✅ All clear / ⚠️ N issues found
- [Issue]: <page>.svg — <element description>: drift = Xpx

### Summary
- [N] issues require fixing before export
- [N] advisory items (optional polish)
- Recommended action: [proceed to Step 7 | fix N items first | escalate to visual-review for deep review]
```

---

## Step 4: Fix Issues

For each flagged issue:

1. Read the affected SVG: `<project_path>/svg_output/<page>.svg`
2. Apply the minimal fix (adjust `fill` color for contrast, shift coordinates for alignment, add margin for whitespace)
3. Do NOT restructure the slide layout — only fix the flagged attribute

After fixing, re-run Step 1 to confirm no new technical violations were introduced.

---

## After Quality Check

Proceed to post-processing & export ([SKILL.md Step 7](../SKILL.md)):

```bash
python3 ${SKILL_DIR}/scripts/total_md_split.py <project_path>
python3 ${SKILL_DIR}/scripts/finalize_svg.py <project_path>
python3 ${SKILL_DIR}/scripts/svg_to_pptx.py <project_path>
```

If the user requested deeper per-page rubric review, run [`visual-review`](./visual-review.md) before Step 7.
