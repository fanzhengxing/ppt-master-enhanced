---
description: Reverse-engineer an editable PPTX from slide screenshots or images — 4-layer decompose → layout.json → compose_pptx.py
---

# Image to PPTX Workflow

> Standalone workflow. Convert screenshots, photos, or scanned slides of an existing presentation into a native, editable `.pptx` file.
>
> **Pipeline**: User images → AI 4-layer decomposition → `layout.json` → `compose_pptx.py` → editable `.pptx`

This workflow is **independent** — safe to run in a fresh chat with only the source images as input.

## When to Run

- User provides screenshot(s) / photo(s) of existing slides and wants an editable PPTX
- User wants to replicate a competitor deck, poster, or printed slide as an editable file
- User says "从截图还原PPT" / "reverse engineer this slide" / "make this editable" / "recreate this PPT"

## When NOT to Run

- User has an existing `.pptx` file → use `template-fill-pptx` workflow or read with `ppt_to_md.py`
- User wants to generate a new PPT from content (not replicate a visual) → use the main pipeline (SKILL.md Step 1–7)
- User has a PDF with selectable text → extract with `pdf_to_md.py`, then use the main pipeline

---

## Step 1: Collect and Assess Source Images

Ask the user to provide the slide images if not already supplied. Accepted formats: PNG, JPG, WEBP, PDF screenshot.

For each image, assess:
- **Slide count**: how many slides to reconstruct
- **Content type**: text-heavy / chart-heavy / image-heavy / mixed
- **Editable priority**: which elements the user most needs to edit (titles, body text, data labels)

> ⚠️ The quality of the output PPTX is bounded by the source image quality. Blurry or low-resolution images (< 800px wide) produce less accurate text extraction and geometry. Warn the user if images are low quality.

---

## Step 2: 4-Layer Decomposition (AI Analysis)

For each slide image, analyze and extract four stacked layers from back to front:

### Layer 1 — Background
The full-bleed background element:
- Solid color: note the hex color
- Gradient: note direction, start/stop colors
- Image: note which portion of the source image serves as background

### Layer 2 — Frame
Structural decorative elements that sit above the background:
- Colored bars, header/footer bands, side panels, geometric shapes
- Describe as bounding box fractions (x, y, width, height as 0.0–1.0 of slide dimensions)
- Note fill color

### Layer 3 — Icons / Images
Logos, icons, photos, charts embedded in the slide:
- Note position (bounding box fractions)
- For icons: describe the icon concept (e.g., "checkmark", "chart bar", "person")
- For photos: describe the subject for image search or AI generation

### Layer 4 — Text Boxes (Editable)
All text content that should remain editable in PPTX:
- Exact text content (copy from the image as accurately as possible)
- Approximate position (bounding box fractions)
- Font size (estimate from visual hierarchy: title ≈ large, body ≈ medium, caption ≈ small)
- Font weight (bold / normal)
- Text color (hex)
- Alignment (left / center / right)

---

## Step 3: Generate layout.json

Create `layout.json` (place alongside the output PPTX, or in a temp directory):

```json
{
  "canvas": {"width_inches": 13.333, "height_inches": 7.5},
  "slides": [
    {
      "background": {
        "type": "color",
        "color": "#1A237E"
      },
      "frame": [
        {
          "type": "rect",
          "x": 0.0, "y": 0.0, "w": 1.0, "h": 0.12,
          "color": "#0D47A1"
        }
      ],
      "texts": [
        {
          "content": "Quarterly Business Review",
          "x": 0.05, "y": 0.15, "w": 0.9, "h": 0.18,
          "font_size": 40,
          "bold": true,
          "color": "#FFFFFF",
          "align": "center"
        },
        {
          "content": "Q4 2024 Results",
          "x": 0.05, "y": 0.35, "w": 0.9, "h": 0.10,
          "font_size": 24,
          "bold": false,
          "color": "#BBDEFB",
          "align": "center"
        }
      ]
    }
  ]
}
```

**Field reference**:

| Field | Type | Description |
|-------|------|-------------|
| `canvas.width_inches` | float | Slide width. 16:9 = 13.333, 4:3 = 10.0 |
| `canvas.height_inches` | float | Slide height. 16:9 = 7.5, 4:3 = 7.5 |
| `background.type` | string | `"color"` or `"image"` |
| `background.color` | string | HEX color (when type = color) |
| `background.file` | string | Image path relative to layout.json (when type = image) |
| `frame[].type` | string | `"rect"` (more types may be added) |
| `frame[].x/y/w/h` | float | Bounding box as fraction of slide dimensions (0.0–1.0) |
| `frame[].color` | string | HEX fill color |
| `texts[].content` | string | Text to display |
| `texts[].x/y/w/h` | float | Bounding box fractions |
| `texts[].font_size` | int | Font size in points |
| `texts[].bold` | bool | Bold weight |
| `texts[].color` | string | HEX text color |
| `texts[].align` | string | `"left"`, `"center"`, or `"right"` |

---

## Step 4: Run compose_pptx.py

```bash
python3 ${SKILL_DIR}/scripts/compose_pptx.py layout.json output.pptx
```

Optional: generate slide preview images alongside the PPTX:

```bash
python3 ${SKILL_DIR}/scripts/compose_pptx.py layout.json output.pptx --preview-dir preview/
```

The script reads `layout.json`, builds each slide as stacked PPTX shapes (background rect → frame rects → image placeholders → editable text boxes), and writes the native `.pptx`.

> **Output**: a fully editable `.pptx` where all text boxes are native PPTX text frames — selectable, resizable, and font-changeable in PowerPoint / WPS / Keynote.

---

## Step 5: Deliver and Iterate

Tell the user:
- Output PPTX path
- Which elements are editable text (Layer 4)
- Which elements are fixed shapes (Layers 1–3) — to change these, edit `layout.json` and re-run Step 4

**Common follow-up requests**:

| User request | Action |
|-------------|--------|
| "Change the text on slide 2" | Edit `texts[].content` in layout.json for slide index 1, re-run Step 4 |
| "The font size looks wrong" | Adjust `texts[].font_size`, re-run Step 4 |
| "Add my logo" | Add an `icons` entry with `file` path to the logo PNG, re-run Step 4 |
| "Make a full PPT from this style" | Extract the brand identity → use `create-brand` workflow → use main pipeline with the new brand |

---

## Notes

- **Text accuracy**: for slides with small text or stylized fonts, OCR from the image may be imperfect. Always review extracted text content before finalizing.
- **Charts**: data charts (bar, line, pie) are embedded as images in this workflow, not as native PPTX charts. To get editable chart data, use the main pipeline (SKILL.md) with the chart data typed in as source content.
- **Aspect ratio**: default canvas is 16:9 (13.333 × 7.5 inches). If the source slide is 4:3, set `width_inches: 10.0`.
- **Multi-slide decks**: add one object per slide to the `"slides"` array in layout.json.
