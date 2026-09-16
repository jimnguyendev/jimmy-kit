# Evaluate — category comparison

## UX Evaluate

Compare what you have against what the category expects. Not to copy
competitors — to make intentional decisions about what to keep, evolve,
and improve.

**Core Principle:** A redesign without evaluation is a reskin. Changing
colors and fonts without understanding what works and what doesn't produces
a different-looking version of the same problems. Evaluation grounds the
redesign in evidence: what's working (keep it), what's convention (match it),
what's below standard (fix it).

## When to Use

When current-state and category evidence are available, whether supplied directly or collected by ux-review audit mode and ux-discovery research mode. It can feed ux-brief when design direction is needed.

## Process

### Step 1: Load Inputs

Load current-state and category evidence, from supplied inputs or these conventional artifacts:
- `.jimmy/work/<feature>/current-design-system.md` (from ux-review audit mode)
- `.jimmy/work/<feature>/category-benchmarks.md` (from ux-discovery research mode)

Equivalent supplied evidence is sufficient; filenames are not prerequisites. If current-state or category evidence is genuinely missing, collect only that missing evidence using the corresponding mode. Label unsupported comparisons provisional; do not fabricate benchmarks.

The tables below are illustrative, not researched category facts or claims to reuse. Replace every example value with observed evidence. A competitor pattern does not establish a conversion effect or accessibility standard.

### Step 2: Evaluate Each Design Dimension

For each dimension (colors, typography, layout, components, information
architecture), compare current state against category benchmarks and produce
a classification:

#### Color Evaluation

```markdown
## Colors
| Element | Current | Category Convention | Classification | Rationale |
|---------|---------|-------------------|----------------|-----------|
| Primary brand color | Orange #f97316 | Varies (each brand unique) | MUST KEEP | Brand identity — recognized by users |
| CTA color | Orange (same as brand) | Contrasting color from brand | SHOULD IMPROVE | CTA doesn't stand out from brand elements |
| Background | White #fff | White or light gray | SHOULD KEEP | Matches convention, no issue |
| Text color | #333 | #111-#333 range | SHOULD KEEP | Within convention range |
```

#### Typography Evaluation

```markdown
## Typography
| Element | Current | Category Convention | Classification | Rationale |
|---------|---------|-------------------|----------------|-----------|
| Hero heading size | ~28px mobile | 32-40px mobile | SHOULD IMPROVE | Below category standard, feels less impactful |
| Body text | 16px | 16-18px | SHOULD KEEP | Matches convention |
| Heading hierarchy | h1 → h3 (skips h2) | Sequential h1 → h2 → h3 | SHOULD IMPROVE | Investigate heading structure and accessible navigation |
```

#### Layout Evaluation

```markdown
## Layout
| Element | Current | Category Convention | Classification | Rationale |
|---------|---------|-------------------|----------------|-----------|
| Hero pattern | Image grid + tagline | Clear value prop + single CTA | SHOULD IMPROVE | Category leaders lead with outcome, not feature showcase |
| CTA placement | Below fold on mobile | Above fold | SHOULD IMPROVE | Users must scroll to take action |
| Section count | 7 sections | 4-6 sections | MAY CHANGE | Slightly long but not critical |
```

#### Component Evaluation

```markdown
## Components
| Element | Current | Category Convention | Classification | Rationale |
|---------|---------|-------------------|----------------|-----------|
| Course cards | Image + title + description | Image + title + key metric + CTA | SHOULD IMPROVE | Missing useful differentiating information; add a metric only if substantiated |
| Testimonials | Text carousel | Photo + name + score + quote | SHOULD IMPROVE | Test whether verified attribution helps users assess credibility |
| Bee mascot | Present throughout | N/A (unique to the brand) | MUST KEEP | Brand differentiator, recognized by users |
```

#### Information Architecture Evaluation

```markdown
## Information Architecture
| Element | Current | Category Convention | Classification | Rationale |
|---------|---------|-------------------|----------------|-----------|
| First screen content | Brand tagline + animated images | Value prop + CTA + social proof | SHOULD IMPROVE | Category leaders answer "what is this?" and "why should I care?" above fold |
| Social proof position | Bottom half of page | Top half, near hero | SHOULD IMPROVE | 100K+ students is a powerful signal — it's buried |
| Navigation | Full nav with dropdowns | Simplified nav + prominent CTA | MAY CHANGE | Current works, but heavy for a landing page |
```

### Step 3: Classification Framework

Use these four categories consistently:

**MUST KEEP** — Brand identity elements. Changing these confuses existing users.
- Logo, brand colors, mascot/character, brand voice/tone
- Unique differentiators that aren't replicated by competitors
- Test: "Would existing users not recognize this as the same product?"

**SHOULD KEEP** — Patterns that work and match conventions.
- Elements that are both functionally correct AND match category expectations
- Test: "Is there evidence this is broken or underperforming?" If no → keep

**MAY CHANGE** — Style elements where updating would freshen without breaking.
- Background colors, section styling, animation approaches
- Layout tweaks that don't change information architecture
- Test: "Would changing this confuse anyone or break anything?" If no → candidate

**SHOULD IMPROVE** — Elements that fall below category standards or have
measurable problems.
- Missing conventions that users expect (CTA above fold, social proof near hero)
- Accessibility violations (contrast, heading hierarchy, touch targets)
- Visible rendering defects such as broken images; claim layout shift or timing only with observed interaction or measurement evidence
- Test: "Is this measurably worse than category convention?" If yes → improve

### Step 4: Prioritize Improvements

Rank SHOULD IMPROVE items by impact:

```markdown
## Priority Improvements
1. [Highest impact]: [description] — [why: conversion / accessibility / performance]
2. [High impact]: [description] — [why]
3. [Medium impact]: [description] — [why]
...
```

Impact factors:
- Task reach and severity, based on observed journeys and available traffic data
- Accessibility barriers and the users/tasks they exclude
- Device and viewport mix from this product
- Conversion hypotheses to validate, rather than assumed effects of placement

### Step 5: Produce Evaluation Document

Save to `.jimmy/work/<feature>/design-evaluation.md`:

```markdown
# Design Evaluation: [page/product]

**Based on:** [actual current-state and category sources, paths if present, and dates]
**Date:** [timestamp]

## Summary
[2-3 sentences: overall assessment, how current design compares to category]

## Classification Table
| Dimension | MUST KEEP | SHOULD KEEP | MAY CHANGE | SHOULD IMPROVE |
|-----------|-----------|-------------|------------|----------------|
| Colors | [count] | [count] | [count] | [count] |
| Typography | [count] | [count] | [count] | [count] |
| Layout | [count] | [count] | [count] | [count] |
| Components | [count] | [count] | [count] | [count] |
| IA | [count] | [count] | [count] | [count] |

## Detailed Evaluation
[from Step 2 — all dimension tables]

## Priority Improvements
[from Step 4 — ranked list]
```

Present classifications with evidence and unresolved decisions. Carry accepted keep/change decisions forward. For consequential brand or scope changes outside the accepted direction, ask the user to resolve the specific choice before the dependent brief; do not repeat confirmation of settled decisions.

## Rules

**MUST (violation = uninformed redesign):**
- MUST have current-state and category evidence for a comparative conclusion. Equivalent supplied evidence counts; absent evidence makes the comparison provisional.
- MUST preserve accepted user decisions. Resolve only new consequential keep/change choices before carrying those choices into ux-brief.
- MUST classify accessibility violations as SHOULD IMPROVE regardless
  of category convention. Accessibility is a standard, not a preference.

**SHOULD (violation = incomplete evaluation):**
- SHOULD evaluate all five dimensions (colors, typography, layout,
  components, information architecture).
- SHOULD reference specific category benchmark evidence for each
  SHOULD IMPROVE classification. Cite which observed reference does what, with source/date; prevalence alone does not prove effectiveness.

**MAY (context-dependent):**
- MAY merge dimensions if the page is simple (e.g., a single-section
  landing page doesn't need separate layout and IA evaluation).
- MAY add dimensions not listed (animation, micro-interactions,
  illustration style) if they're relevant to the redesign.

## Failure Modes

- **User disagrees with MUST KEEP classification:** Respect their decision.
  They know their brand better. Reclassify and note the reason.
- **No clear category convention exists:** Mark as MAY CHANGE with note
  "No strong convention — this is a differentiation opportunity."
- **Current design is significantly better than competitors in an area:**
  Mark as MUST KEEP with note "Ahead of category — preserve this advantage."
- **User wants to change everything:** Caution them: "Changing everything
  at once risks losing what works. Suggest phasing: SHOULD IMPROVE items
  first, MAY CHANGE items in a second pass." Respect their final decision.

## Quality Criteria

**Communication style:** Analytical language. Justify classifications
with evidence — benchmarks, conventions, principles. Evaluations should
hold up if challenged by a stakeholder.

Good UX evaluation output:
- Every scoped dimension is classified (MUST KEEP / SHOULD KEEP / MAY CHANGE / SHOULD IMPROVE)
- Classifications are justified with evidence — benchmark data, conventions, principles
- MUST KEEP items cite specific brand or usability reasons
- SHOULD IMPROVE items cite category benchmarks or established conventions
- Competitor analysis is specific — names, observations, patterns
- The evaluation would hold up if challenged by a stakeholder

## Self-Review

Before presenting your output, check each quality criterion above.
For each, confirm it's met or note what's missing. Present your
findings AND your self-assessment:

"Self-review: [X/Y criteria met]. [Note any gaps and why they exist.]"
