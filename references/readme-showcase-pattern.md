# README Showcase Pattern

> How to add visual proof to a skill's README — embed screenshots that demonstrate the actual output.

## Why

A README without visuals is just documentation. Screenshots prove the skill works and lower the barrier for adoption.

## Pattern

1. **Create showcase directory**: `assets/showcase/`
2. **Generate representative output** — create a minimal test project that exercises the core capability
3. **Screenshot key pages** — 2-3 images showing different aspects (cover, architecture, data visualization)
4. **Embed in README** after the "What it delivers" section:

```markdown
### 效果展示

![Slide 1 — Cover](assets/showcase/showcase_slide1.png)

![Slide 2 — Pipeline Architecture](assets/showcase/showcase_slide2.png)

![Slide 3 — Data Cards](assets/showcase/showcase_slide3.png)

> 💡 双击 `exports/deck.html` 即可打开，无需安装任何依赖。按 `S` 进入演讲者模式，按 `T` 切换主题。
```

## Do

- Use real output from the skill (not mockups)
- Show different aspects: title page, data visualization, layout variety
- Keep captions descriptive: `![Description](path)`
- Include a tip about how to use the output

## Don't

- Use too many screenshots (2-3 is enough)
- Use screenshots that are too large (>200KB each)
- Embed screenshots in SKILL.md — README is the public-facing doc
- Forget to sync showcase to all agent runtimes (Hermes + CC + Codex)

## Sync Checklist

After adding showcase images:
1. Copy to `~/.hermes/skills/<category>/<skill>/assets/showcase/`
2. Copy to `~/.claude/skills/<skill>/assets/showcase/`
3. Verify both directories have identical files
4. Update README.md in both locations (they should be synced)
