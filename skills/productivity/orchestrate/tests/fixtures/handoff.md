# HANDOFF — linter fixture

## Landed
- Packet 031, the email editor (PR #41).

## Waiting on owner

### 1. Should the frequency cap count marketing messages per day or per week?
- What it is: the cap stops one learner from getting too many marketing messages. Today it counts per day per channel and drops the extra message. ADR-0017 records the daily rule; the old vendor counted per week.
- Why now: the admin card for the cap is the next frontend packet, and its fields depend on this.
- Options:
  - A. Per day, as built. Cost: none. Effect: a learner can still get 14 pushes a week.
  - B. Per week. Cost: about 1 day backend and half a day frontend. Effect: matches campaigns copied from the old vendor.
- Recommendation: B, because campaigns are planned weekly and a daily cap allows a heavy week.
- If no answer: under the owner's decide-don't-ask rule for this build, I build B on Monday; switching back to A is a config change.
- Evidence: .jimmy/work/limits/brief.md

## Next
1. Land packet 033 after the dispatcher fix passes.
