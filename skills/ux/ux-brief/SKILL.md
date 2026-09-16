---
name: ux-brief
description: >-
  Use when redesign findings need concrete visual direction, accepted keep/change decisions need a design brief, or the user asks what a redesigned page or component should look like.
version: "1.0.0"
modes: [build, architect]
---

# UX Brief

> **This skill exists to stop:** ambiguous design handoffs and repeated approval of directions the user already accepted.

## 🤖 0. HOW TO USE

BUILD produces a focused component/page brief; ARCHITECT covers the full redesign. Use evaluation findings and accepted decisions from the conversation, supplied documents, or `.jimmy/work/<feature>/design-evaluation.md`. Missing filenames do not require repeating research. Output `.jimmy/work/<feature>/design-brief.md`, scoped to the accepted change, for `ux-specify` and the development plan.

Translate evaluation findings into a design brief that the spec and plan
skills can execute against. This is where analysis becomes direction.

**Core Principle:** A design brief bridges the gap between "what's wrong"
(evaluation) and "what to build" (spec + plan). Without it, the developer
interprets the evaluation themselves — and developers optimize for code
elegance, not user experience. The brief makes design decisions explicit
so implementation follows design intent.

## When to Use

After ux-review evaluate mode and the user has confirmed classifications. Before the
normal elicitation and specification flow. The design brief becomes an INPUT to
the specification — enriching it with visual direction that the spec
alone wouldn't contain.

## Process

### Step 1: Confirm User Decisions

Carry accepted classifications and directions forward. Identify only unresolved material choices, especially consequential brand or scope changes. For those choices, propose a direction:

> "The evaluation found [N] items to improve. For each one, I'll propose
> a direction. Tell me if you agree or want something different."

For each priority improvement:

```
Current: [what exists now]
Issue:   [why it should change — from evaluation]
Proposed direction: [specific change]
→ Agree / Adjust / Skip
```

Example:
```
Current: Hero shows animated image grid with tagline "Smart learning platform"
Issue:   CTA is below fold. No clear value proposition. Category leaders
         answer "what is this?" and "why should I care?" in the hero.
Proposed direction: Replace image grid with focused hero —
  Headline: outcome-focused (e.g., "Ace your IELTS with AI-powered practice")
  Subheadline: how it works in one line
  Primary CTA: "Start Learning Free"
  Trust badges: verified student count + authorized award logos, if evidenced
→ Agree / Adjust / Skip
```

Record each decision.

### Step 2: Define Visual Direction

Based on confirmed decisions, establish the visual direction:

```markdown
## Visual Direction

### Color Direction
Keep: [brand colors that are MUST KEEP]
Change: [colors classified as MAY CHANGE or SHOULD IMPROVE, with new direction]
Add: [any new colors needed — e.g., a distinct CTA color]

### Typography Direction
Keep: [font family if it works]
Change: [size scale adjustments, hierarchy fixes]
Specific: [e.g., "Increase hero heading to 36px mobile / 56px desktop"]

### Layout Direction
Pattern: [e.g., "Full-width hero → Product cards grid → AI features →
          Social proof → Reviews → CTA footer"]
Mobile-first: [describe the mobile layout, then how it expands]
Key change: [the biggest structural change from current]

### Component Direction
Keep: [components that work — e.g., "Course cards (add key metric)"]
Redesign: [components that need significant change]
New: [components that don't exist yet — e.g., "Trust badge bar"]
Remove: [components to eliminate — e.g., "Repeated background pattern"]
```

### Step 3: Define Section-by-Section Direction

For each section of the redesigned page:

```markdown
## Section Directions

### 1. Hero
**Current:** [description from audit]
**Direction:** [what it becomes]
**Must include:** [specific elements]
**Mobile:** [how it works on mobile]

### 2. [Section name]
**Current:** [description]
**Direction:** [what changes]
...
```

### Step 4: Define Constraints

```markdown
## Constraints
- Brand elements that MUST NOT change: [list from MUST KEEP]
- Technical constraints: [e.g., "Images from CMS via next/image",
  "Must work for /vi/ and /en/ routes"]
- Performance targets: [e.g., "LCP < 2.5s, no layout shift on images"]
- Accessibility requirements: [e.g., "WCAG 2.2 AA, sequential heading
  hierarchy, 44px touch targets"]
```

### Step 5: Produce Design Brief

Save to `.jimmy/work/<feature>/design-brief.md`:

```markdown
# Design Brief: [page/product] Redesign

**Based on:** [actual evaluation source and accepted decisions, with date/context]
**Prepared for:** [`ux-specify` + `ux-plan-tasks`]

## Objective
[One sentence: what this redesign achieves]
Example: "Modernize the product homepage to improve conversion by
clarifying the value proposition above the fold and strengthening
social proof."

## User Decisions
| Item | Classification | Decision | Direction |
|------|---------------|----------|-----------|
| Brand colors | MUST KEEP | Keep | Orange palette stays |
| Hero layout | SHOULD IMPROVE | Agreed | Outcome-focused hero with CTA above fold |
| Bee mascot | MUST KEEP | Keep | Retain in key positions |
| CTA placement | SHOULD IMPROVE | Agreed | Primary CTA above fold on all breakpoints |
| Section count | MAY CHANGE | Agreed | Reduce from 7 to 5 sections |
| ... | ... | ... | ... |

## Visual Direction
[from Step 2]

## Section Directions
[from Step 3]

## Constraints
[from Step 4]

## Success Criteria
[from evaluation priorities — measurable outcomes]
1. CTA visible above fold on mobile (375px)
2. LCP < 2.5s
3. WCAG 2.2 AA compliance
4. Social proof visible within first viewport on desktop
```

Present the complete brief with its constraints and unresolved choices. Continue to already authorized specification or implementation work; no extra approval is required for a settled direction.

## How This Connects to the Kit Workflow

```
ux-review audit mode → ux-discovery research mode → ux-review evaluate mode → ux-brief
                                            ↓
                                    design-brief.md
                                            ↓
Development: existing context → specification + ux-specify → plan (ux-plan-tasks for ARCHITECT) → implementation
```

The design brief is an input to the feature specification, not a replacement. The specification
adds functional requirements, acceptance criteria, and technical constraints.
The brief adds visual direction, brand constraints, and design decisions.
Together, they provide the requirements needed for task decomposition.

## Rules

**MUST (violation = implementation without design direction):**
- MUST preserve accepted directions and authorization. Ask about unresolved consequential choices before dependent work; routine details within the accepted direction may be specified and explained without another approval.
- MUST include constraints section. Implementation without constraints
  drifts from brand, breaks accessibility, or ignores performance.
- MUST produce a brief that downstream specification and planning can reference by path.

**SHOULD (violation = vague brief):**
- SHOULD be specific enough that two different developers would produce
  similar-looking implementations. "Make the hero better" is too vague.
  "Hero with outcome-focused headline, subheadline, primary CTA, trust
  badges — mobile: stacked, desktop: text-left image-right" is specific.
- SHOULD define mobile layout explicitly, not just desktop.
- SHOULD include success criteria that can be verified by visual and interaction checks appropriate to the requirement.

**MAY (context-dependent):**
- MAY include rough wireframe descriptions (ASCII or text-based layout
  sketches) for complex sections.
- MAY reference specific competitor implementations as direction: "Social
  proof approach similar to Duolingo's — numbers, not just testimonials."
- MAY skip section-by-section directions in BUILD mode if the redesign
  is a single component, not a full page.

## Failure Modes

- **User changes everything the evaluation recommended keeping:** Respect it
  but note the risk: "Changing brand elements may confuse returning users.
  Consider an A/B test if possible."
- **User skips all improvements:** Note it. The brief becomes a "keep as-is"
  document — which is a valid outcome. The evaluation is on record.
- **Brief is too vague for implementation:** Self-check: can you draw a rough
  wireframe from this brief? If not, add more specificity. Each section
  direction should answer: what's in it, how is it arranged, what's the CTA.
- **Spec and brief conflict:** Brief takes precedence for visual decisions.
  Spec takes precedence for functional requirements. Note the conflict
  and ask the user to resolve.

## Quality Criteria

**Communication style:** Design direction language. Be visual and
concrete — describe what the user will see and experience. Ground
every direction in evaluation findings.

Good UX brief output:
- Every design direction is grounded in evaluation findings
- "Keep" and "change" decisions are justified with evidence
- The brief is specific enough that a designer can create mockups
- Content direction includes tone, messaging hierarchy, and key copy points
- Success metrics are defined and measurable
- Can you visualize the end result from reading this brief? If not, it's too vague

## Self-Review

Before presenting your output, check each quality criterion above.
For each, confirm it's met or note what's missing. Present your
findings AND your self-assessment:

"Self-review: [X/Y criteria met]. [Note any gaps and why they exist.]"
