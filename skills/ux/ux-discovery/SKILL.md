---
name: ux-discovery
description: >-
  Use when a feature lacks user evidence, a team needs interview planning or category benchmarks, or disagreement about user behavior leaves a material design decision unresolved.
version: "1.0.0"
modes: [build, architect]
---

# UX Discovery

> **This skill exists to stop:** design decisions based on invented user behavior or unexamined category assumptions.

## 🤖 0. HOW TO USE

Select BUILD for missing context in a scoped feature, ARCHITECT for substantial discovery, or research for category benchmarks. For interview planning, load [User Interview Design](references/user-interview.md). Output context notes, evidence-grounded personas/journeys, a research plan, or category benchmarks under `.jimmy/work/<feature>/` as needed for the handoff; small answers may stay inline.

Reuse supplied context, accepted research objectives, and prior evidence. Ask only missing questions that affect the decision; absent artifact files do not require repeating discovery. User interviews are conducted by people or separately authorized research tools: a plan is not a completed study. Never invent participants, findings, verbatim quotations, or measurements. Label synthesized personas and emotional arcs as hypotheses unless supported by evidence; quotations require an actual source.

Gathers user context to ground specifications in real user behavior rather than
developer assumptions. Supports the current elicitation or `analyst` work when user context is missing.

## Mode: BUILD (light)

Add these UX-focused questions to the elicitation, woven into the normal
elicitation flow. Don't extend the time — make the existing questions sharper.

**Ask about the user's context (pick 2-3 most relevant):**

1. "Who specifically uses this, and what's their state of mind when they arrive?"
   (Rushed? Anxious? Browsing? In the middle of another task?)
2. "What are they doing immediately before this feature? How do they get here?"
   (From a notification? Search? Navigation? Deep link?)
3. "What do they currently do to solve this problem?" (The existing workflow,
   including workarounds. Past behavior > hypothetical behavior.)
4. "What goes wrong? What's the most common failure or frustration?"

**Capture in the user-context-notes artifact:**
- Who: one sentence describing the primary user and their context
- Before: how they arrive at this feature
- After: where they go when done
- Pain: the current frustration this feature addresses

## Mode: ARCHITECT (full)

Run the complete UX discovery process. This is a structured investigation
that produces artifacts feeding directly into specification.

### Phase 1: Stakeholder Context (5 min)

Review what's known about the users from:
- Existing documentation, previous specs, analytics data
- The codebase-scan output (what patterns exist? what user flows already exist?)
- Stakeholder input ("who is this for and why now?")

### Phase 2: User Research Framing (10-15 min)

Apply The Mom Test principles to structure the inquiry:
- Frame questions about past behavior, not opinions
- Ask "When did you last...?" not "Would you ever...?"
- Look for concrete facts: what they did, what tools they used, what frustrated them
- If talking to real users isn't possible, use the best proxy: support tickets,
  analytics data, competitor reviews, forum posts

Produce: research findings summary

### Phase 3: Persona Development (10 min)

From the research, develop 2-3 behavioral personas:

```
[Name] — [Role]
"[Quote capturing their attitude]"

GOAL: What they're trying to accomplish
CONTEXT: When, where, on what device
PAIN: What frustrates them about current solutions
BEHAVIOR: How they approach problems
FREQUENCY: How often they do this
```

Designate one as the PRIMARY persona (design for this person first).
Optionally designate a NEGATIVE persona (explicitly NOT designing for).

Produce: persona-profiles artifact

### Phase 4: Journey Mapping (10-15 min)

Map the primary persona's full journey:

1. **Trigger:** What causes them to start this journey?
2. **Arrival:** How do they get to the feature? What do they expect?
3. **Core flow:** Step by step, what do they do?
4. **Decision points:** Where do they choose between options?
5. **Failure points:** Where can things go wrong? What happens?
6. **Completion:** What tells them they're done? Where do they go next?
7. **Emotional arc:** When are they confident? Confused? Frustrated? Relieved?

Produce: journey-map artifact

### Phase 5: Pain Point Inventory (5 min)

From the journey map, extract the top pain points ranked by severity:
- **Blockers:** User can't complete their goal
- **Friction:** User can complete but with unnecessary effort or confusion
- **Annoyance:** User notices something wrong but works around it

These feed directly into the specification as requirements and acceptance criteria.

## References

The discovery methods above are self-contained. Load [User Interview Design](references/user-interview.md) only when planning a qualitative study.

---

## Mode: Research — category benchmarks

Benchmark the current design against category leaders. Not to copy — to
understand what conventions users already expect, and where intentional
deviation creates differentiation.

**Core Principle:** Users don't experience your product in isolation. They
bring expectations from every other product in your category. An edtech
homepage that ignores conventions from Duolingo, Coursera, and Khan Academy
isn't being original — it's being confusing. Research identifies what's
convention (match it) vs. what's commodity (differentiate from it).

## When to Use

- When current-state evidence is available (from ux-review audit mode or equivalent supplied material)
- Before ux-review evaluate mode (you need context for the gap analysis)
- When redesigning a page and category context would improve decisions

Do NOT use for:
- Internal tools with no public competitors
- Entirely novel product categories (research won't find benchmarks)

## Process

### Step 1: Identify Product Category

From supplied current-state evidence and project context, determine:

```markdown
## Category Definition
Product type:    [edtech / SaaS / e-commerce / marketplace / fintech / ...]
Page type:       [homepage / landing page / dashboard / product page / ...]
Target audience: [students / professionals / developers / consumers / ...]
Market:          [geography, language — affects design conventions]
```

If unclear, ask the user: "Is this primarily a [A] or [B]? This determines
which competitors I research."

### Step 2: Identify 3-5 Category Leaders

Select reference products based on:
- **Direct competitors** — same product type, same market
- **Category leaders** — best-in-class regardless of market
- **Aspirational references** — products known for excellent UX in adjacent categories

```markdown
## Reference Products
1. [Product] — [why selected: direct competitor / category leader / aspirational]
2. [Product] — [why]
3. [Product] — [why]
```

For the product homepage example:
1. Duolingo — category leader in language learning UX
2. Coursera — established online education platform
3. Khan Academy — known for accessible learning design
4. EF Education — IELTS-specific competitor
5. Elsa Speak — AI-powered language learning (adjacent)

### Step 3: Analyze Category Patterns

For each reference product, capture (via web search and page analysis):

```markdown
### [Product Name]

**Hero pattern:**
[What's in the hero? Headline copy approach? CTA text? Visual treatment?
Single CTA or multiple? Video? Animation? Social proof in hero?]

**Value proposition:**
[How do they explain what they do? How many words? What framework —
problem → solution → benefit? Feature list? Outcome-focused?]

**Social proof approach:**
[Testimonials? Logos? Numbers? Scores? User photos? Video testimonials?
Placement — above fold or below? How prominent?]

**CTA strategy:**
[Primary CTA text and placement. How many CTAs on page?
Free trial? Demo? Sign up? Pricing? What's the conversion path?]

**Visual style:**
[Color approach? Illustration vs. photography? Light vs. dark?
Playful vs. professional? Information density?]

**Mobile approach:**
[What changes on mobile? What's hidden? What's prioritized?
Sticky nav? Sticky CTA?]
```

### Step 4: Identify Category Conventions

From the analysis, extract patterns that appear in 3+ reference products:

```markdown
## Category Conventions (appearing in most leaders)
1. [Convention]: [what it is, who does it]
   Example: "Hero with single clear CTA — Duolingo, Coursera, Khan Academy
   all use one primary CTA above the fold"

2. [Convention]: [what it is]
   Example: "Social proof near hero — score numbers, student count, or
   testimonials within first viewport"

3. ...
```

### Step 5: Identify Differentiation Opportunities

Patterns where reference products are similar to each other but different
from the audited product — or where the category has a gap:

```markdown
## Differentiation Opportunities
1. [Opportunity]: Most competitors [do X]. Current product [does Y differently].
   Assess: is Y intentionally different (brand identity) or accidentally missing?

2. [Opportunity]: No competitor [does Z]. Could this be a meaningful differentiator?

3. [Opportunity]: Competitors [do X poorly]. An excellent version of X would stand out.
```

### Step 6: Produce Benchmarks Document

Save to `.jimmy/work/<feature>/category-benchmarks.md`:

```markdown
# Category Benchmarks: [product] — [page type]

**Category:** [edtech / SaaS / ...]
**References analyzed:** [count]
**Date:** [timestamp]

## Reference Products
[from Step 2]

## Category Conventions
[from Step 4 — what most leaders do]

## Differentiation Opportunities
[from Step 5 — where to stand out]

## Detailed Analysis
[from Step 3 — per-product breakdowns]
```

Show to user: "Here's what category leaders do. This feeds into the
design evaluation — we'll compare your current design against these patterns."

## Rules

**MUST (violation = uninformed redesign):**
- For a category-wide claim, analyze at least 3 relevant reference products. With fewer, label the comparison limited and do not claim a category convention.
- MUST distinguish conventions (most do this) from individual choices
  (only one does this). Conventions are what users expect.
- Include a direct competitor and a category leader when they exist and are accessible; otherwise document the limitation and why adjacent references are relevant.

**SHOULD (violation = shallow research):**
- Use dated supplied evidence or inspect current reference products with available web/browser tools; do not present remembered designs as current observations.
- SHOULD capture the reference products' mobile approach, not just desktop.
- SHOULD note the reference products' copy approach (tone, length, language
  level) since this affects conversion as much as visual design.

**MAY (context-dependent):**
- MAY reduce to 2 references for niche categories with few competitors.
- MAY include references from adjacent categories if direct competitors
  are few (e.g., a fintech app referencing banking apps AND investment apps).
- MAY skip this skill if the user explicitly says "I don't want to look at
  competitors — I have my own vision."

## Failure Modes

- **No web search available (Tier 2 platform):** Ask the user to share 2-3
  competitor URLs directly. Analyze those instead of searching. Note the
  limitation in the report.
- **Competitor pages require login:** Analyze the public-facing pages only
  (homepage, pricing, landing pages). Note what's behind auth.
- **Very niche product with no clear competitors:** Broaden the category.
  "No direct competitor" is itself a finding — note it and research
  adjacent categories.
- **User disagrees with competitor selection:** Replace with their suggestions.
  They know their market better.


> Interview planning uses [User Interview Design](references/user-interview.md); competitor benchmarking is not user research.

---

## Applied context (edtech — merged from a retired research skill)
> Blocks: benchmarking = listing competitor features and proposing to copy them. Principle: borrow how competitors SIMPLIFY user decisions, and state what they sacrificed. **MUST:** every competitor claim carries source + access date, else label it [ASSUMPTION]. End every benchmark with "things we will NOT copy, and why (up to 3 supported findings)." VoC mining: internal conversation corpus + competitors' 1-star reviews, for verbatim pain language.
