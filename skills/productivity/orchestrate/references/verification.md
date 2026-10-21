# Verification on the running app

Read before the first frontend packet is verified, and whenever more than one agent may drive
a UI on the same machine.

## Frontend is verified against the real service

Component tests against a mocked API (MSW and similar) cannot reveal a backend defect. Before
an FE packet lands, the screens it built are driven against the real service with real data.
Origin: the first drive of the activity panel on real data showed that the dispatcher never
persisted the rendered message, while 13 worker tests and 118 acceptance tests were green
because none asserted that column. The fix became a backend packet and a reality AC.

## One verification agent, one browser

- Executors never open a browser or a UI-driving tool. They verify with the gates, component
  tests, and calls against the real service, and report how to reach each state they built
  (URL + seed step).
- The root delegates driving to **one** verification subagent. It owns one browser (its own CDP
  port and a profile directory under `/tmp`), its own service ports, and an evidence directory.
  It never attaches to a browser another agent or the user started: tools that act on the
  active tab read whatever that tab shows.
- The prompt names the pages or flows, the spec each must match, the ports and profile, and the
  output: a verdict per page (match / minor / major, with the difference), evidence file paths,
  and API gaps. It returns findings and paths, not DOM trees or inline screenshots.
- The root reads the report and opens the evidence it needs. It drives itself only where a
  judgement is needed (a design call, an ambiguous finding).

Why delegate: in the origin run the root drove the browser itself and used most of a 1M-token
context on DOM trees and screenshots. Why one browser: about ten executor browsers overloaded
the machine, and a shared browser let one agent read another packet's screen.

## Look at every frontend land

After each FE packet lands, the root looks at its pages in that one browser before
dispatching the next FE packet. Layout defects (an input overflowing its cell, a missing page
padding) pass every typecheck, lint and component test. Origin: a limits stepper landed with an
overflowing text input that only a look at the page caught.

Findings go back as a delta to the same executor, or into the next FE packet; API gaps become a
backend packet. When the repo has a project-local verify skill (built with `verify-app`), the
verification agent follows its recipes and evidence rules.

## Done means walked as a user

A green UI packet is not done. Before reporting it done, the root (or the verification agent
it briefs) walks the flow as a user on the local stack, with realistic seeded data copied from the
reference product's real usage, with the reference product's screen open beside it. Empty or
toy data hides dead ends, missing columns and broken empty states; a feature checked only
against our own spec can match the spec and still be the wrong screen.

Internal vocabulary never reaches the UI: terms from the code, ADRs or other repos (revision,
tombstone, executor, lease) are not words the admin uses. Recommended gate: a test over the
UI locale files that fails on a deny-list of internal terms, with an allow-list for reviewed
exceptions. Add words to the list when a review finds one.

## Defects only the browser shows

Typecheck, lint and component tests passed while these shipped; look for them on every FE land:

- Utility classes that compile to nothing. A design system's spacing tokens may exist for padding
  and gap but not for `top-`/`left-`/`inset-`; the class is accepted and emits no CSS, so a dock or
  side panel renders in the wrong place. Keep a guard test that fails on such class names.
- Icons in flex rows collapsing to zero width next to long labels (missing `shrink-0`).
- Text that is correct in the test locale and truncated or untranslated in the other one.
- Copy that contradicts runtime behaviour (a card promising retries for a route the runtime parks).

Origin: one builder packet landed with 594 green component tests while its dock and panels were
misplaced; the next packet had 8 findings on the real backend, none caught by 679 tests.
