# CLAUDE.md — Jimmy Kit

## What this repo is
A self-contained skill kit (49 skills, 7 categories) for AI agents, extracted 2026-08-30 from an internal working set. All English, brand-neutral (generic edtech examples), provenance in README.md. Operating model: docs/OPERATING-WORKFLOW.md (7-question intake → product-council gate → 4-phase chain; `routing` skill is the dispatcher). Decisions: docs/DECISIONS.md (ADR style, newest first — read before restructuring anything).

## Conventions (enforced)
- Every self-authored skill opens with `> **This skill exists to stop:** …` (one-line failure statement) and a `## 🤖 0. HOW TO USE` section (modes + output formats).
- Source tokens: `[sage]` = github.com/xoai/sage · `[docs]` = internal docs repo (optional deep-dives; skills must run without them; steps marked MUST READ stop and ask if the file is missing).
- Canonical bodies (routing, quality-gates, constitution, analyst, architect, change-tiers, independent-review + the 11 sage-product skills) are kept verbatim — do NOT rewrite them; heritage `/sage-*` mentions inside are intentional. Kit-specific context lives only in the "Applied context (edtech)" appendix at the end of a file.
- No company names, no real internal people. Voice profiles in product-council are anonymized archetypes — keep them unnamed.
- New/changed skills: add or update SCENARIO.md (write the scenario BEFORE the skill; status stays "exit 2" until a real run is pasted in).

## State at handoff (2026-08-30)
- Done: extraction, renaming (see README table), full EN translation, de-branding, templates translated, routing added from upstream, 3 scenarios PASS (author dry runs — first independent runs still wanted).
- Origin: the practice-labs working set (Vietnamese, keeps evolving separately); sync is MANUAL and one-way; archives live in the origin repo (skills-archive-2026-08-30/).
- Open items: (1) independent runs of the 3 scenarios; (2) git remote + tag v0.1.0 when ready; (3) maybe package as a `sage add` pack later (rejected for now — DECISIONS K1).

## Review checklist for the next session (Claude Code)
1. Vietnamese scan: `grep -rP '[ạảấầẩẫậắằẳẵặ...]' skills/` → empty.
2. Every skill dir: SKILL.md present, `name:` matches folder name.
3. Cross-references resolve to kit names (routing, analyst, architect, quality-gates, change-tiers, decision-log, independent-review, retrospective, tracking-architect, product-council, okr-outcome-architect, ux-*, jtbd, prd, opportunity-map, problem-solving…).
4. No source-company or real-person names outside README credits.
5. Frontmatter descriptions are situation-triggered ("use when…"), not feature descriptions.
6. Markdown: single H1 per file, tables render, no broken relative links.
