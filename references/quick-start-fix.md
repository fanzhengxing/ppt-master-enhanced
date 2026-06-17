# Quick-Start Fix (README.md)

## What was wrong

The README's "快速开始" section referenced `luban-skill` (`npx skills add LearnPrompt/luban-skill -g`), which is a skill management tool from the upstream (LearnPrompt) repo. This skill (ppt-master-enhanced) has **no dependency on luban-skill**. The reference was a leftover from the upstream repo's README.

## What was fixed (2026-06-15)

Changed the quick-start to be self-contained:

- **Install section** — shows `git clone https://github.com/fanzhengxing/ppt-master-enhanced.git <skills_dir>/ppt-master` (all agents) — no external dependency
- **Usage section** — just "加载 ppt-master skill" then describe your needs
- **Importantly**: no luban, no plugin marketplace, no third-party tools needed

## Correction (2026-06-15 v2)

`hermes skills install ppt-master` was wrong — this skill is NOT in the official skill hub.
It's a custom GitHub repo. All agents must use `git clone` from the GitHub URL.

## Key principle

ppt-master-enhanced is a **standalone skill**. It needs nothing beyond:
1. The skill directory (cloned to the agent's skills folder)
2. Python dependencies (`requirements.txt`)
3. A `.env` file (optional, for image gen providers)

No npm packages, no skill managers, no marketplace plugins.
