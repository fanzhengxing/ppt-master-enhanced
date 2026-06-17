# Hermes Runtime Notes for ppt-master-enhanced

## Path Resolution

On Hermes, `${SKILL_DIR}` resolves to the skill installation directory:
```
~/.hermes/skills/productivity/ppt-master/
```

## Python

Use `python3` (Hermes venv Python is on PATH). If `python3` not found, fall back to `python`:
```bash
python3 scripts/compose_pptx.py layout.json output.pptx
# or
python scripts/compose_pptx.py layout.json output.pptx
```

## WebSearch/WebFetch on Hermes

Hermes provides built-in web search and fetch tools. The topic-research workflow
uses these natively — no extra configuration needed.

## Background Processes

For long-running processes (live preview server, image generation), use:
```
terminal(background=true, notify_on_complete=true)
```
Not shell-level `&` or powershell `Start-Process`.

## Hermes ←→ CC 双端同步 (Windows)

When syncing ppt-master between CC and Hermes on Windows git-bash:

```bash
# ❌ BAD: cp -r of whole .git causes Permission denied on locked objects
cp -r /c/Users/fzx/.claude/skills/ppt-master/. /c/Users/fzx/skills/ppt-master/
# → returns exit 1: "Permission denied" on .git/objects/**/*

# ✅ GOOD: copy files only, skip .git directory
cd /c/Users/fzx/.claude/skills/ppt-master
find . -not -path './.git/*' -not -name '.git' -type f | while read f; do
  mkdir -p "/c/Users/fzx/skills/ppt-master/$(dirname "$f")"
  cp "$f" "/c/Users/fzx/skills/ppt-master/$f"
done
# Verify: find /c/Users/fzx/skills/ppt-master/ -type f -not -path '*/.git/*' | wc -l
```

**Caveats:**
- `rsync` is NOT available on Windows (returns "command not found")
- Each file is `cp`'d individually → ~2 min for 12K files
- Templates dir (~11K files) takes bulk of time — copy it first
- After sync, re-sync SKILL.md separately to apply fixes (the find+cp loop copies the original)

**Key directories to verify after sync:**
```
scripts/     → ~43 items (expected: 43)
workflows/   → ~13 items (expected: 13)
references/  → ~120 items (expected: 120)
templates/   → ~11,841 items (expected: 11,841)
README.md + test-prompts.json + .env.example + SKILL.md → verify exist
```

**Final step:** After `cp`, run `skill_manage(action='edit')` on Hermes to update the skill index.

## Live Preview

The SVG live preview server (Step 6) must be started via Hermes background terminal.
Do NOT use `&` in background mode.

### Port conflict workaround
```bash
python3 ${SKILL_DIR}/scripts/svg_editor/server.py <project_path> --live --port 5051
```

## compose_pptx.py (Image→PPTX workflow)

```bash
python3 ${SKILL_DIR}/scripts/compose_pptx.py <layout.json> <output.pptx>
```

Requires `python-pptx`. Install if missing:
```bash
pip install python-pptx
```

The script composes a 4-layer PPTX (background → frame → icons → editable text)
from a layout JSON file. Works independently of the main pipeline.

## Quality Check Scripts

```bash
# Pre-flight (basic): runs as part of Step 6
python3 ${SKILL_DIR}/scripts/svg_quality_checker.py <project_path>

# Deep quality check (user opt-in, post-export):
# Run visual-quality-check workflow
# (no standalone script — LLM-driven via workflow instructions)
```
