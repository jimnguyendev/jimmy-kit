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

## Measure layout, do not read screenshots

The verification agent runs `verify-app`'s `scripts/layout_sweep.mjs` over every route and every
panel or dialog after each frontend land, and the land waits for zero findings or a recorded waiver.
It measures the DOM (horizontal scrollers, overlapping controls, controls past their panel edge, raw
i18n keys) and prints one line per defect; screenshots are for design judgement only.
Origin: screens built from packet text needed six fix packets (about 800k executor tokens) after
landing, the root spent about 40 minutes guessing selectors in a shared browser, and the owner still
found two defects by eye. The first sweep found the remaining one in seconds: a design-system input
kept its 166 px intrinsic width inside a 64 px box and scrolled a 360 px side panel sideways.

Before the look, rebuild and restart the backend from the branch that just landed and apply its
migrations. A stale binary produced a fake defect (a raw `…sourceBadge.undefined` key) because
the old API did not return the new field.

## Design before the screen is built

A screen or panel with no exported design page gets a brief and a design first
([design-export.md](design-export.md)), or at least the layout rules below in its acceptance
criteria. Origin: the one screen built from the owner's design page landed in a single round with
zero layout findings; every screen built from packet text came back with layout and copy defects.

## Layout rules for narrow panels and forms

Put these in every FE packet's acceptance criteria; each one shipped past component tests:

- No fixed pixel wrapper around a control (`w-[104px]` around a select): a design-system control
  with a larger minimum width spills over its neighbour. Use grids with `minmax(0, 1fr)`.
- Inputs and textareas carry `min-width: 0` (once, globally): an `<input>` keeps an intrinsic width
  of about 20 characters and ignores a narrower box.
- A segmented control with more than three options, or labels that wrap, becomes a dropdown in a
  panel under about 400 px; never a horizontally scrolling segmented control that hides the selection.
- No error and no empty-state error on a pristine field or step: validate on blur, save or input.
- No raw grammar, codes, API paths, field names (`as_of`) or i18n keys on screen; copy in the UI
  language only.
- A dialog keeps its action buttons visible (sticky footer) at 1440 x 900.
- An icon button inside a small chip uses the small size; a removable chip is one local component.
- When a design-system component falls short (missing `listbox`/`option` roles, a dropped
  `aria-label`, an intrinsic width), wrap or replace it once in the app's own UI folder for every
  call site. Forty-nine call sites working around it one by one broke in several places.

## Driving a design-system UI over CDP

`element.click()` does not open many design-system dropdowns; dispatch real mouse events
(`Input.dispatchMouseEvent` pressed and released at the element centre). Fill long wizards by
importing their file format (`DOM.setFileInputFiles`) instead of clicking through. Accept
`beforeunload` dialogs from the CDP session (`Page.javascriptDialogOpening`), or the tab freezes and
every later call times out.

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
