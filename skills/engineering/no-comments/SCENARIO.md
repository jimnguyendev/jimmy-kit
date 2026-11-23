# Scenario — no-comments (written BEFORE the skill)

## 2026-11-23 sweep scenario

**Status:** [EXIT 2 — specified; independent application not yet recorded].

**Input 1:** A Go service asks for a repo-wide comment purge. Its AGENTS.md requires a `doc.go` feature map per package, a `// dbtx:root <reason>` marker that archlint reads, and a one-line reason on every timeout.

**Expected behaviors:**
- [ ] Passes the three AGENTS.md keeps to the reviewer with each chunk.
- [ ] Deletes narration, banners and commented-out code; keeps `//go:build`, license headers and vendor quirks.
- [ ] Proves with a comment-stripped AST diff that no code changed, then runs the repo gates.
- [ ] Reports `MUST KILL` flags that need code changes as open work instead of fixing them inside the sweep.

**Input 2:** A diff adds `// IMPORTANT: do not remove, the retry hides a race in our cache`.

**Expected behaviors:**
- [ ] Kills the comment (our own code, not a foreign constraint).
- [ ] Flags the cache symbol `MUST KILL` and routes the fix to the root cause, not a guard.
- [ ] Offers an encoding (a test that reproduces the race) and waits for approval before writing it.
