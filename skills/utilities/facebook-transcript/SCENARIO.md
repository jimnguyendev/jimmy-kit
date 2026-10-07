# Scenario — facebook-transcript

## Current revision — 2026-09-26

**Status: EXIT 2 — scenario specified; no independent fresh-agent run recorded yet.**

**Origin:** built from a real session that pulled 25 hour-long language-teaching lives from one Facebook page. Two failures from that session shaped the skill: (1) the page's reels/videos tab cannot be listed by yt-dlp, and a logged-out browser stops after ~50 items; (2) 8 of 25 auto-caption tracks were silently truncated (a 62-minute live returned 48 seconds of text), and a first-pass analysis nearly treated those sessions as covered.

**Sample input A (single video):** "Get the transcript of https://www.facebook.com/<page>/videos/<id> and summarize it."

**Expected behaviors:**
- [ ] Runs `fb_transcript.py <url>`; does not download the video file.
- [ ] Output file carries title, url, upload date, duration and caption source in its header; lines are `[mm:ss]` buckets.
- [ ] Checks the coverage line (caption end vs duration). If coverage is under 80%, says so before summarizing and offers the Whisper fallback instead of summarizing a fragment as if it were the whole video.
- [ ] Summary quotes carry `[mm:ss]`.

**Sample input B (whole page):** "Download all live transcripts from https://www.facebook.com/<page>/live_videos/."

**Expected behaviors:**
- [ ] Explains that yt-dlp cannot list page tabs; collects links with `fb_collect_links.js` in a real browser (user logged in, a separate profile if driving via CDP), covering `reels/`, `videos/` and `live_videos/` as relevant.
- [ ] Never types the user's password; asks the user to log in.
- [ ] Runs the batch; reports counts of ok / no captions / partial captions from `index.tsv`, `no_captions.txt`, `partial_captions.txt`.
- [ ] Filters long-form items by duration when the user asked for lives only.

**Validation needed:** run both cases with a fresh agent on a public page, paste the output, grade each box.
