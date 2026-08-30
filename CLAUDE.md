# CLAUDE.md — Jimmy Kit

## What this repo is
A self-contained skill kit (48 skills, 7 categories) for AI agents, extracted 2026-08-30 from an internal working set. All English, brand-neutral (generic edtech examples), provenance in README.md. Operating model: docs/OPERATING-WORKFLOW.md (7-question intake → product-council gate → 4-phase chain; `routing` skill is the dispatcher). Glossary: CONTEXT.md (domain language — keep it updated when terms shift). Install tooling: scripts/. Decisions: docs/DECISIONS.md (ADR style, newest first — read before restructuring anything).

## Conventions (enforced)
- Every self-authored skill opens with `> **This skill exists to stop:** …` (one-line failure statement) and a `## 🤖 0. HOW TO USE` section (modes + output formats).
- Source tokens: `[sage]` = github.com/xoai/sage · `[docs]` = internal docs repo (optional deep-dives; skills must run without them; steps marked MUST READ stop and ask if the file is missing).
- Canonical bodies (routing, quality-gates, constitution, analyst, architect, change-tiers, independent-review + the 11 sage-product skills) stay close to upstream — do not restructure or re-voice them. Exception (DECISIONS K5): anything that needs the Sage runtime is replaced with a kit-runnable equivalent — no `sage-*.sh`, `sage add`, `sage/...` paths, `/sage-*` commands, or `.sage/` paths anywhere in `skills/`. Skill output paths in a TARGET repo are namespaced under `.jimmy/` (mirrors upstream `.sage/`): `.jimmy/work/<feature>/` (in-progress artifacts + feature decisions), `.jimmy/docs/` (durable outputs), `.jimmy/decisions.md` (global ADRs) · `.jimmy/adr/NNNN-slug.md` (numbered engineering ADRs), `.jimmy/constitution.md`. Never write skill outputs to a target repo's `docs/`. (This kit's own `docs/DECISIONS.md` is the kit's ADR log, unrelated.) Kit-specific context lives in the "Applied context (edtech)" appendix at the end of a file.
- No source-company names, internal repo names, or real internal people (public third-party method attributions such as Duolingo, Nielsen, Krug are fine). Voice profiles in product-council are anonymized archetypes — keep them unnamed.
- New/changed skills: add or update SCENARIO.md (write the scenario BEFORE the skill; status stays "exit 2" until a real run is pasted in).

## State at handoff (2026-08-30)
- Done: extraction, renaming (see README table), full EN translation, de-branding, routing ported; 3 scenarios PASS with independent fresh-agent runs (`okr-outcome-architect`, `product-council`, `ux-cro-audit` — run #1 missed the AI-failure branch → §7 row 15 added → run #2 PASS); 6-step review checklist run and all findings fixed; kafka-patterns dropped (48 skills); Sage-runtime commands/paths removed (K5); outputs namespaced under `.jimmy/`; usage guide in docs/USAGE.md.
- Origin: an internal Vietnamese working set that keeps evolving separately; sync is MANUAL and one-way (archives stay in the origin repo).
- Open: git remote + tag v0.1.0 (needs the remote URL). Install tooling for Codex/Cursor destinations is documented in docs/USAGE.md; `link-skills.sh --category` filter not built yet.

## Review checklist for the next session (Claude Code)
1. Vietnamese scan: `grep -rP` with the Vietnamese-diacritics character class over `skills/` → empty.
2. Every skill dir: SKILL.md present, `name:` matches folder name.
3. Cross-references resolve to kit names (routing, analyst, architect, quality-gates, change-tiers, decision-log, independent-review, retrospective, tracking-architect, product-council, okr-outcome-architect, ux-*, jtbd, prd, opportunity-map, problem-solving…).
4. No source-company or real-person names outside README credits.
5. Frontmatter descriptions are situation-triggered ("use when…"), not feature descriptions.
6. Markdown: single H1 per file, tables render, no broken relative links.
7. Vietnamese WITHOUT diacritics (grep common words: `khong|duoc|nguon|chay|phien ban|tai ve`) → empty; also scan `.py/.js/.sql/.ts`, not just `.md`.
8. Sage runtime: `grep -rnE 'sage/|\.sage/|sage-[a-z-]+\.(sh|py)|/sage-|sage add|delegate_task|Hermes'` over `skills/` → only the two `[sage] skills/sage-*` provenance pointers.
9. Output paths: no `docs/` paths inside `skills/` except the pointer to `docs/OPERATING-WORKFLOW.md` and external URLs — everything else is `.jimmy/…`.
10. Frontmatter parses as YAML (nested `"` inside a `"`-quoted description breaks the loader — use `>-` block scalars).
11. Bundled scripts compile: `python3 -m py_compile`, `node --check`; no `__pycache__` tracked; internal repo names (`grep -rn` for them) absent outside README credits.
