# Examples — bad questions and their briefs

Read before the first brief of a session. The bad questions are real (translated); each made the owner ask back before deciding. The good versions are illustrative: their numbers show the shape, not facts.

## 1. Two decisions in one line

**Bad:** "Give me two answers: open the PR on the skill kit? Accept ADR-0017?"

The owner replied "what is this?". Neither the PR nor the ADR was explained, and they were bundled.

**Good (first of two briefs):**

> **1. Open a PR on the public skill kit so the land script runs every test before merging?**
> What it is: the skill kit is the shared set of agent instructions this project installs. During this build the script that merges a finished packet ("land") pushed and merged without running any tests; packet 28 landed with one suite not re-run. The branch has three commits: the script now runs every check listed in `.orchestrate/gates` on the merged code, refuses to merge if one fails, and has tests for both. About 150 lines.
> Why now: until it merges, every project installing the kit can still land untested code. This project already uses the fixed copy.
> Options: A. Open the PR now. Cost: 10 minutes of review for you. Effect: the fix reaches every install. B. Keep the fix local. Cost: none now; later projects repeat the bug. Effect: only this project is protected.
> Recommendation: A. The change is small and tested, and the bug already cost one bad land.
> If no answer: I do not open it (it is public); the branch stays ready and nothing here is blocked.
> Evidence: branch `fix-land-gates`, test output in `.orchestrate/archive/land-tests.log`.

The second brief explains ADR-0017 the same way: the rule it sets (for example "a failed send is retried by the dispatcher, not at enqueue"), what each option costs, and what learners notice.

## 2. A list of one-liners

**Bad:**
> 1. Contract test: add kin-openapi (default: yes)
> 2. Rate-limit store: Redis (default: yes)
> 3. … four more

No reason to decide now, no cost, no word on what kin-openapi is or what happens without an answer.

**Good:** triage first. Adding a contract-test library, renaming a package, and upgrading Go are reversible engineering calls: decide them and report one line each ("I added kin-openapi, a Go library that checks every API response against the OpenAPI spec, so a field renamed by mistake fails the build"). Only the calls that are the owner's get a brief: removing an endpoint that old clients still call, how long send logs are kept, and paying for a Redis instance. Each of those gets all seven parts.

## 3. Options with no cost

**Bad:** "Do you want me to go this way? Or limit per week like the old vendor?"

**Good:**

> **Should the frequency cap count messages per day or per week?**
> What it is: the cap stops one learner from getting too many marketing messages. Today it counts per day per channel (for example at most 2 push messages a day). Past the cap, the extra message is dropped, not delayed. The old vendor counted per week.
> Why now: the admin card for the cap is the next frontend packet; its fields depend on this.
> Options: A. Per day (as built). Cost: none. Effect: a learner can still get 14 pushes a week. B. Per week. Cost: about 1 day backend (count over 7 days), half a day frontend. Effect: matches campaigns copied from the old vendor. C. Both. Cost: about 2 days. Effect: most control; the card gets two fields to explain.
> Recommendation: B. Campaigns are planned weekly, and a daily cap allows a heavy week.
> If no answer: I build B on Monday; switching back to A later is a config change.
> Evidence: `.jimmy/work/limits/brief.md`.

## The good explanation from the same run

The explanation of the admin's limits card got an answer at once. It said what the feature does, what happens past the limit, what is wrong in the current screen, the proposal, and the backend and frontend work the proposal needs. That is the shape every brief copies: what it is, what the user sees, what it costs, what you suggest.
