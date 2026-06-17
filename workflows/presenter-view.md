---
description: Generate a self-contained HTML presentation from project assets — keyboard navigation, presenter mode, theme switching, offline-ready
---

# Presenter View Workflow

> Standalone post-export step. Generates a single self-contained HTML file (`deck.html`) from a completed ppt-master project. No dependencies — all CSS, JS, and SVGs are base64-inlined. Double-click to open, no server required.

This workflow is **independent** — safe to invoke in a fresh chat with only `<project_path>` as input, provided Step 7 has completed.

## When to Run

- User wants to share the deck without requiring PowerPoint / WPS
- User wants a browser-based presentation (team standup, remote screen share, web embed)
- User says "生成HTML演示" / "做个网页版" / "HTML幻灯片" / "presenter view" / "browser presentation"
- Internal sharing where the audience may not have Office installed

## When NOT to Run

- User needs the editable `.pptx` file → use the main pipeline (SKILL.md Step 7.3)
- Step 7 has never run — the SVG files must be post-processed first (`finalize_svg.py`)
- User wants to read/analyze the existing `.pptx` → use the `powerpoint` skill

---

## Prerequisites

The project must have completed at least through Step 7.2 (finalize_svg.py):

```
<project_path>/
├── svg_output/          ← raw SVGs (Executor output)
├── svg_final/           ← post-processed SVGs (finalize_svg.py output) ← required
├── notes/               ← per-page speaker notes (total_md_split.py output)
└── spec_lock.md         ← design tokens (theme auto-detection source)
```

If `svg_final/` is empty or missing, run Step 7.1–7.2 first:

```bash
python3 ${SKILL_DIR}/scripts/total_md_split.py <project_path>
python3 ${SKILL_DIR}/scripts/finalize_svg.py <project_path>
```

---

## Step 1: Generate HTML Deck

```bash
python3 ${SKILL_DIR}/scripts/html_export.py <project_path>
```

Output: `<project_path>/exports/deck.html` — a single self-contained file with all assets inlined.

**Options**:

| Flag | Description | Default |
|------|-------------|---------|
| `--theme <name>` | Override auto-detected theme | Auto from `spec_lock.md` |
| `--output <dir>` / `-o <dir>` | Output directory | `<project_path>/exports/` |
| `--quiet` / `-q` | Suppress progress output | Off |

**Available themes**:

| Theme name | Best for |
|-----------|---------|
| `corporate-clean` | Business / professional decks (default for most) |
| `minimal-white` | Academic / clean decks with light backgrounds |
| `minimal-dark` | Dark-background decks, tech/creative presentations |

Theme auto-detection reads the `colors` section of `spec_lock.md` — if the background color is dark (`luminance < 0.2`), `minimal-dark` is selected; otherwise `corporate-clean`.

---

## Step 2: Deliver to User

Tell the user (in their language):
- Output path: `exports/deck.html`
- Double-click to open — no server, no install needed
- Keyboard shortcuts (list below)

**Keyboard navigation**:

| Key | Action |
|-----|--------|
| `→` / `Space` | Next slide |
| `←` | Previous slide |
| `Home` / `End` | First / last slide |
| `F` | Fullscreen |
| `S` | Presenter mode (4-card: current + next preview + speaker notes + timer) |
| `T` | Cycle themes |
| `N` | Toggle speaker notes panel |
| `O` | Overview / slide grid |
| `A` | Toggle animations |

---

## Notes

- **Self-contained**: the HTML file has no external dependencies. All SVGs are base64-encoded, CSS/JS are inlined. Safe to email or upload anywhere.
- **Speaker notes**: read from `<project_path>/notes/<NN>_*.md` files. If notes are missing, the presenter mode shows empty note cards.
- **Animations**: entrance animations defined in `svg_to_pptx.py` are represented as CSS transitions in the HTML deck. The `A` key toggles them off for accessibility.
- **Print**: `Ctrl+P` in the browser → "Print to PDF" gives one slide per page (no layout changes needed — the HTML is print-optimized).
- **Re-generation**: if SVGs change after export (e.g., live-preview annotations applied), re-run Step 1 to refresh `deck.html`.
- **Sharing via URL**: if the user has a web server, `deck.html` can be served directly — it has no CORS or same-origin dependencies.

---

## Troubleshooting

| Symptom | Cause | Fix |
|---------|-------|-----|
| Blank slides in HTML | `svg_final/` not found or empty | Run `finalize_svg.py` first (Step 7.2) |
| Icons missing in HTML | Icon `<use data-icon>` not expanded | `finalize_svg.py` expands icons; re-run it before `html_export.py` |
| Wrong theme / colors look off | `spec_lock.md` colors not parsed | Pass `--theme <name>` explicitly to override |
| Large file size (> 20 MB) | Many high-res images embedded | Normal for image-heavy decks; consider compressing images in `images/` before re-running |
| Notes not showing in presenter mode | `notes/` directory missing or empty | Run `total_md_split.py` first (Step 7.1) |
