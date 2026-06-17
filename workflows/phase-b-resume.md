---
description: Phase B entry — resume PPT execution in a fresh chat after Phase A (SKILL.md Step 1-5) completed in a previous session. Reads project state from disk and runs Step 6 + Step 7. Optionally customize animations before export.
---

# Phase B: Resume Execution & Animation Customization

> Standalone Phase-B entry. Run when Phase A (SKILL.md Step 1–5) completed in a previous session and the user wants to continue.
> This workflow is **independent**: it owns Phase B starting from a fresh chat — no upstream conversation context required.

## When to Run

### Resume Execute (Phase A → Phase B)

Recognize any of:

|| Pattern | Example |
|---|---|
| "继续生成 projects/<project_name>" | "继续生成 projects/ppt169_joe_hisaishi" |
| "resume execution projects/<project_name>" | "resume execution projects/ppt169_joe_hisaishi" |
| Project path + any "继续 / 恢复 / 继续做 / 接着做" semantic | "把 projects/ppt169_joe_hisaishi 继续做完" |

**Prerequisite**: Phase A must have completed in the named project. Verified by file presence in Step 1; do NOT auto-trigger Phase A on missing state.

### Animation Customization (Post-Export)

|| Condition | Action |
|---|---|
| User asks for object-level animation, reveal order, timing, or effect changes | Run this workflow |
| User only wants the default animated deck | Do not run; normal `svg_to_pptx.py` export is enough |
| `svg_output/*.svg` is missing | Complete the main Executor phase first |
| Existing `animations.json` is present | Validate and edit it; do not overwrite unless the user asks |

---

## Phase B.1: Sanity Check

Verify the project's Phase-A artifacts before doing anything else:

|| File / Directory | Required when | Reason |
|---|---|---|
| `<project_path>/spec_lock.md` | Always | Strategist's execution contract; Executor reads it per page |
| `<project_path>/design_spec.md` | Always | Section IX page outline; Executor cross-references it |
| `<project_path>/images/` | `spec_lock images` references any image | Images must exist for embedding |
| `<project_path>/templates/` | `spec_lock page_layouts` / `page_charts` references any | Layout / chart SVGs needed for batch read |

If any required artifact is missing → report which one(s) and stop. Do NOT auto-fall-back into Phase A.

---

## Phase B.2: Execute (Step 6 + Step 7)

```
Read skills/ppt-master/SKILL.md
```

Then jump to `### Step 6: Executor Phase` and run the documented pipeline:

- Read references (executor-base + shared-standards + chosen style file + image-layout-spec + svg-image-embedding)
- Design Parameter Confirmation
- Pre-generation Batch Read (every layout / chart SVG referenced in `spec_lock`)
- Per-page `spec_lock` re-read + sequential page generation
- Quality Check Gate
- Speaker notes generation
- Step 7: Post-processing & Export (`total_md_split` → `finalize_svg` → `svg_to_pptx`)

The fresh session pays the cost of re-reading references (~14K tokens) but earns back substantially more headroom by dropping Phase A's accumulated context.

**Source materials**: Phase B is a fresh session; `<project_path>/sources/<file>.md` is NOT in context. The Executor SHOULD read the relevant `sources/` files when crafting per-page content — they hold the concrete facts, quotes, names, and details.

> Note: this workflow does NOT duplicate Step 6 / Step 7 content. SKILL.md is the authoritative procedure; Phase B only adds the resumption entry (When to Run + Step 1 sanity check above) and the source-materials guidance above.

> **Chart pages?** If the deck contains data charts, run `workflows/verify-charts.md` between Phase B.2 Step 6 and Step 7 as documented in SKILL.md.
> **Visual review (opt-in)?** Only if user explicitly asked — run `workflows/visual-review.md`.

---

## Phase B.3: Optional Animation Customization

Run this step ONLY if the user asks for finer animation control beyond the defaults.

### 1. Get Real Group IDs

**Default path — `list-groups`** (cheap, ~1KB of output even on a long deck):

```bash
python3 skills/ppt-master/scripts/animation_config.py list-groups <project_path>
```

Output is one line per slide: `<slide_basename>: id1, id2, id3` — chrome groups excluded.

If `animations.json` does not exist and you want a starting file to edit:

```bash
python3 skills/ppt-master/scripts/animation_config.py scaffold <project_path>
```

If it already exists:

```bash
python3 skills/ppt-master/scripts/animation_config.py validate <project_path>
```

### 2. Read Semantic Context

**Mandatory**: before editing `animations.json`, read the deck's semantic planning files.

|| File | Use |
|---|---|
| `<project_path>/design_spec.md` | Understand each slide's content intent, narrative role, and visual emphasis |
| `<project_path>/spec_lock.md` | Confirm page rhythm, layout role, chart/template constraints |
| `<project_path>/notes/total.md` or `<project_path>/notes/*.md` | Use speaker flow to tune reveal order, delays, and emphasis |

**Hard rule**: semantic files determine animation intent; `svg_output/*.svg` determines valid animation targets. Never reference a slide or group id absent from the scaffold / SVG scan.

### 3. Plan Slide and Object Motion

**Per-page motion brief**: for each slide, decide transition effect, transition duration, object reveal sequence, object effects, and timing.

|| Layer | Config path | Use |
|---|---|---|
| Page transition | `defaults.transition` or `slides.<slide>.transition` | How one slide enters from the previous |
| Page animation defaults | `defaults.animation` or `slides.<slide>.animation` | Default entrance for animated groups |
| Object overrides | `slides.<slide>.groups.<group_id>` | Per-object effect, order, delay, duration |

**Timing guidance**:

|| Context | Transition duration | Object duration | Delay / stagger |
|---|---:|---:|---:|
| `anchor` / section opener / closing synthesis | 0.35-0.60s | 0.45-0.75s | 0.20-0.40s |
| `breathing` concept slide / hero diagram | 0.25-0.45s | 0.40-0.65s | 0.16-0.30s |
| `dense` technical slide / repeated pattern | 0.18-0.35s | 0.25-0.45s | 0.10-0.24s |
| Key insight / final takeaway | 0.30-0.50s | 0.50-0.80s | 0.25-0.45s |

### 4. Edit `animations.json`

**Hard rule — write every slide explicitly; let groups inherit**. Each slide under `slides.<slide>` MUST carry its own complete `transition` and `animation` block, even when values match `defaults`. Group-level overrides remain opt-in.

**Forbidden**:
- Omitting a slide that exists in `svg_output/`
- Writing a slide block with only `groups` and no `transition`/`animation`
- Enumerating every content group just to restate the slide-level default
- Listing chrome groups

**Canonical example**:

```json
{
  "version": 1,
  "defaults": {
    "transition": { "effect": "fade", "duration": 0.4 },
    "animation": { "effect": "fade", "duration": 0.4, "stagger": 0.5, "trigger": "after-previous" }
  },
  "slides": {
    "01_cover": {
      "transition": { "effect": "fade", "duration": 0.5 },
      "animation": { "effect": "fade", "duration": 0.5, "stagger": 0.4, "trigger": "after-previous" }
    }
  }
}
```

### 5. Validate and Re-export

```bash
python3 skills/ppt-master/scripts/animation_config.py validate <project_path>
python3 skills/ppt-master/scripts/svg_to_pptx.py <project_path>
```

---

## ✅ Phase B Complete

- [ ] Sanity check passed (spec_lock, design_spec, images, templates)
- [ ] Executor Phase (Step 6): SVG pages generated to svg_output/
- [ ] Quality Check Gate: svg_quality_checker passed (0 errors)
- [ ] Post-processing (Step 7): total_md_split → finalize_svg → svg_to_pptx
- [ ] PPTX exported at `exports/<project_name>_<timestamp>.pptx`
- [ ] HTML deck exported at `exports/deck.html`
- [ ] **Animation?** Object-level overrides applied (if requested)
- [ ] **Charts?** verify-charts workflow run (if deck contains data charts)
