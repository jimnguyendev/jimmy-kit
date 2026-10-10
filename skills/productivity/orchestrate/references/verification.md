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
