# ppt-master-enhanced: Gap Analysis vs Competitors

This file documents the competitive landscape that ppt-master-enhanced was designed against,
based on research conducted June 2026.

## PPTAgent (icip-cas)

| Dimension | PPTAgent | ppt-master-enhanced |
|-----------|----------|-------------------|
| Approach | Agent-driven, fine-tuned 9B model (DeepPresenter) | SVG→DrawingML pipeline + Strategist(LLM) |
| Run location | Docker (Linux/WSL, no Windows) | Local Python, Windows/macOS/Linux |
| Content research | Tavily/MinerU deep research | topic-research workflow (standard + deep) |
| Output | .pptx (python-pptx via compose) | .pptx (native SVG→DrawingML, editable shapes) |
| Design control | Free-form LLM layout | Template-constrained + spec_lock |
| Key strength | Free-form layout, deep research integration | Precision control, local-only, cross-platform |

**Takeaway**: Free-form layout approach is interesting but unreliable for corporate decks. Our
spec_lock approach gives better predictability. Deep Research integration pattern (Tavily) could
improve our topic-research workflow — noted as future enhancement.

## GordenSuperPPTSkills (GordenSun)

| Dimension | GordenSuperPPTSkills | ppt-master-enhanced |
|-----------|---------------------|-------------------|
| Approach | ImageGen → GPT vision → compose_pptx.py | SVG→DrawingML + compose_pptx.py |
| Output | Editable .pptx (4-layer decomposition) | Editable .pptx (both SVG and image→pptx) |
| Image→PPTX | ✅ Core feature (B1-B9) | ✅ Adopted as image-to-pptx workflow |
| compose_pptx.py | ✅ (adapted by ppt-master) | ✅ (forked and enhanced) |
| Platforms | Agent-only (no standalone) | Cross-agent (Hermes, CC, Codex, OpenClaw) |

**Takeaway**: Core image→PPTX technique adopted. Our version adds gap-analysis and quality
check workflows that Gorden lacks.

## html-ppt-skill

| Dimension | html-ppt-skill | ppt-master-enhanced |
|-----------|---------------|-------------------|
| Format | HTML slides (inline) | .pptx (native) + optional presenter-view.html |
| Renders in | Browser (Instant) | PowerPoint/Google Slides/Keynote |
| Speaker notes | Inline annotations | .pptx native notes + presenter-view HTML |
| Best for | Web/online sharing | Professional delivery/archive |

**Takeaway**: Can coexist: html-ppt-skill for instant web sharing, ppt-master for PDF export & formal delivery.

## huashu-slides / huashu-design

| Dimension | huashu-slides | ppt-master-enhanced |
|-----------|--------------|-------------------|
| Format | Multi-format (PPT/PDF/HTML) | .pptx focused |
| Pipeline | Template → SVG → export | Source → Strategist → SVG → export |
| Chinese support | Native (花叔 ecosystem) | Via Noto Sans SC + strategist.md |
| Best for | Quick slides + PDF export | Full production pipeline |

**Takeaway**: huashu-slides is lighter for quick-and-dirty slides. ppt-master is the heavy lifter
for production-grade decks.

## Open Design (Prompt Engineering Guide)

| Dimension | Open Design | ppt-master-enhanced |
|-----------|-------------|-------------------|
| Approach | Design token system (L0/L1/L2) | Design Token layer + Strategist constraint solving |
| Implementation | Prompt-based | SKILL.md + references/design-tokens.md |
| Coverage | Broader (logos, icons, motion) | PPT-focused token subset |
| Tech stack | Independent | ppt-master integrated |

**Takeaway**: Token abstraction layer adopted from Open Design. Our implementation is PPT-
specific but tightly integrated with the existing pipeline.

## guizang-ppt-skill

| Dimension | guizang-ppt-skill | ppt-master-enhanced |
|-----------|------------------|-------------------|
| Approach | Visual quality audit post-SVG | visual-quality-check workflow |
| Scope | Full quality rubric | Two-tier: pre-flight basic + deep quality |
| Integration | Standalone | Integrated into ppt-master pipeline |
| Output | Quality report | Quality report + actionable fix list |

**Takeaway**: Post-SVG quality check adopted from guizang's approach. Our version adds a
two-tier system (pre-flight for speed, deep for final review).

## Summary: Unique Selling Points

1. **Only cross-platform, local-only PPT generation system** — no Docker, no API keys
2. **SVG→DrawingML pipeline** — precise control over every shape, color, and animation
3. **13 standalone workflows** — topic research, image→PPTX, presenter view, visual QC, etc.
4. **Design Token abstraction** — brand-consistent multi-template output
5. **Cross-agent** — works on Hermes, Claude Code, Codex, OpenClaw
