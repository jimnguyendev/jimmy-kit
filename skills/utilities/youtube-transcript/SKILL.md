---
name: youtube-transcript
description: >-
  Extract transcripts AND cut slide frames from any YouTube URL or Video ID.
  Use when asked to get a transcript, fetch subtitles, summarize a YouTube video, read captions,
  or grab slide screenshots at given timestamps. Transcript has two paths: a python script (fast, blocked on cloud IPs) and a browser fallback.
---

# YouTube Transcript & Frame Extractor

> **This skill exists to stop:** quoting video content that can't be traced — a quote without video-id + timestamp is a [GUESS] borrowing the video's authority.

## 🤖 0. OUTPUT RULE
Every transcript quote carries `video-id` + timestamp (or .txt line number); downloaded transcripts are saved into the repo's transcripts folder so others can verify later.

Two jobs: **transcript** → `get_transcript.py` or `browser_capture.js` (§1–2) · **slide frames** → `capture_frames.py` (§4).

## Transcript: two paths — pick correctly upfront
| | Path A: python script | Path B: browser |
| :-- | :-- | :-- |
| File | `get_transcript.py` | `browser_capture.js` |
| Runs on | Personal machine (residential IP) | Chrome on a personal machine |
| Speed | Fast, one command | Slower, 3 steps |
| Fails when | **Cloud IPs are blocked by YouTube** → `IpBlocked`, exit code 2 | Almost never |

> ⚠️ Inside containers / CI / cloud sandboxes, path A and `capture_frames.py` both fail (YouTube blocks cloud IP ranges). The script exits 2 and prints the fallback instructions. Don't proxy around it — use path B.

## 1. Path A — python
```bash
/usr/bin/python3 .claude/skills/youtube-transcript/get_transcript.py "<URL_OR_ID>" --out transcript.txt
```
Options: `--json` for per-segment start/duration. Exit codes: 0 ok · 1 generic error · 2 IP-blocked (switch to B). Dependency: `pip install youtube-transcript-api --user`.

## 2. Path B — browser
Open the video in Chrome, then run the three functions in `browser_capture.js` (paste into Console, or drive via a browser tool):
```js
openTranscriptPanel();      // opens "Show transcript"
await collectSegments();    // scrolls so YouTube renders everything — MANDATORY
downloadTranscript(45);     // buckets into 45s chunks, downloads <videoId>_raw.txt
```
Three classic mistakes: skipping `collectSegments()` (virtual scrolling → only ~30 lines, and it "looks fine") · reading the DOM before the panel loads (the function already waits 3s) · fetching `captionTracks[].baseUrl` directly (now token-gated, returns empty — go through the panel). Move the downloaded file from Downloads into the repo before processing.

## 3. After you have the transcript
Raw output is noisy: `[music]`, stutter lines, mis-recognized terms. Run it through your cleanup script (noise removal, term dictionary, segment merging, metadata header); extend the term dictionary in the script and re-run from `_raw/` when needed.

## 4. Cutting slide frames — `capture_frames.py`
Three modes:
```bash
# (a) Known timestamps — fastest, no video download
capture_frames.py <VIDEO_ID> --at 3:56,13:34,24:26 --out shots/ --prefix v06
# (b) Timestamps straight from a written guide — closes the loop with docs
capture_frames.py <VIDEO_ID> --at-guide .jimmy/docs/guides/v06_guide.md --out shots/ --prefix v06 --dedupe --emit-markdown
# (c) Unknown — let ffmpeg detect slide changes
capture_frames.py <VIDEO_ID> --auto --download --limit 30 --dedupe --out shots/ --prefix v06
```
**How it works:** `yt-dlp -g` grabs the video-only stream URL, then `ffmpeg -ss <sec> -i <url> -frames:v 1`. Putting `-ss` BEFORE `-i` is the key — fast HTTP-range seeking instead of decoding from the start.

Useful flags: `--threshold` (0.1 default suits text-only slide changes; 0.05 catches animations; 0.2–0.3 big scene cuts; auto-lowers if <3 hits) · `--download` (cache the video first — turn on for >10 frames or `--auto`) · `--crop auto` (kill letterboxing — screen-share recordings almost always have it) · `--dedupe` (average-hash, needs Pillow — essential with `--auto`) · `--emit-markdown` (ready-to-paste image blocks) · `--limit` (cap for `--auto`, default 40) · `--dry-run`.

Output naming: `<prefix>_<n>_<timestamp>.png` + a `<prefix>_manifest.json` mapping timestamps ↔ files. Out-of-range timestamps are skipped (and reported), so `--at-guide` is safe against typos.

Three classic mistakes: threshold too high on `--auto` (white slides changing only text score very low — hence 0.1 default) · no `--download` for many frames (each seek is a fresh request; stream URLs expire in hours) · forgetting `--crop auto`.

## Reading & analysis
Long videos (>5,000 words): read by timestamp ranges, not start-to-finish. Auto-captions stay wrong even after cleanup — for exact quotes, open the video at the timestamp to verify, and mark uncertainty instead of guessing.
