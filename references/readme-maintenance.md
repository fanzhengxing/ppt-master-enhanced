# README Maintenance Best Practices

> How to maintain accurate, user-facing documentation for a skill.

## Core Rules

1. **Installation instructions must be accurate** — no fake commands, no invented CLI syntax
2. **Platform-specific installation** — list actual methods per runtime (Hermes built-in, CC clone, GitHub ZIP)
3. **Feature coverage** — document ALL output types (PPTX, HTML, presenter view, etc.)
4. **Screenshots prove it works** — embed real output, not mockups
5. **Sync across runtimes** — README changes must propagate to all agent platforms

## Anti-Patterns

- ❌ Inventing CLI commands that don't exist (`npx skills add`, `/plugin marketplace`)
- ❌ Documenting features that aren't implemented (e.g., HTML output without the actual feature)
- ❌ Using generic "install skill" instructions without platform specifics
- ❌ Leaving README outdated after feature additions (e.g., new HTML export)

## Sync Checklist

After any README change:
1. Update Hermes-side README (`~/.hermes/skills/...`)
2. Update CC-side README (`~/.claude/skills/...`)
3. Commit and push to GitHub repo
4. Verify both sides identical
