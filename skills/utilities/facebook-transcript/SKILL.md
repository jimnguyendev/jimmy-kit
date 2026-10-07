---
name: facebook-transcript
description: >-
  Pull transcripts from Facebook videos, reels and recorded lives, for one URL or a whole page's
  videos / reels / live_videos tab. Use when asked to get a transcript, subtitles or captions of a
  Facebook video or live, to summarize or analyze Facebook video content, or to batch-download
  every live of a page. Uses Facebook's own auto-captions via yt-dlp (no video download) and flags
  truncated caption tracks.
---

# Facebook Transcript

> **This skill exists to stop:** analyzing a Facebook video from a caption track that silently stops after the first minute, and treating a page's first ~50 visible videos as "all of them".

## 🤖 0. HOW TO USE

**Output rule:** every quote carries `video-id` + `[mm:ss]`. Save transcripts into the working repo (e.g. `.jimmy/docs/transcripts/<page>/`) so others can re-check them.

Two modes:

| Mode | Input | Steps |
| :-- | :-- | :-- |
| Single | one or a few video / reel / live URLs | §1 |
| Page | a page's `reels/`, `videos/` or `live_videos/` tab | §2 → §1 |

Output per video: `<upload_date>_<id>.txt` with a header (title, url, uploader, upload date, duration, caption end + coverage %, caption track) and `[mm:ss]` lines bucketed every 45 s. Batch bookkeeping: `index.tsv` (id, date, duration_s, coverage, words, title, file), `no_captions.txt`, `partial_captions.txt`.

## 1. Fetch transcripts — `fb_transcript.py`

```bash
python3 -m venv .venv && .venv/bin/pip install yt-dlp        # once
.venv/bin/python <skill>/fb_transcript.py "<URL>" --out <dir>
.venv/bin/python <skill>/fb_transcript.py links.txt --out <dir>   # one URL per line
```

Options: `--bucket 30` (seconds per line) · `--cookies-from-browser chrome` (a video that needs login). Re-runnable: ids already in `<dir>` are skipped. Exit codes: 0 ok · 1 some videos failed or had no captions · 2 yt-dlp missing.

How it works: `yt-dlp --skip-download --write-auto-subs` fetches the auto-caption track Facebook generated, with no video download, so it takes seconds per video. Facebook labels the track by account locale, not by spoken language (a Vietnamese live can come back as `en_US`), so check the text, not the label.

**Always read the coverage line before using a transcript.** Facebook auto-captions are sometimes cut off: a 62-minute live can return 48 seconds of text, and re-fetching gives the same result. Below 80% coverage the script prints `PARTIAL` and logs the URL in `partial_captions.txt`. Then either:
- tell the user the transcript covers only X% and summarize only that part, or
- offer the fallback: download audio only (`yt-dlp -x --audio-format m4a <url>`) and transcribe locally with Whisper (e.g. `mlx-whisper` on Apple Silicon, `faster-whisper` elsewhere). Ask first, because it downloads the audio and takes minutes per hour of speech.

## 2. List a whole page — `fb_collect_links.js`

yt-dlp cannot list a page's tabs (`Unsupported URL`). Collect the links in a real browser instead:

1. Ask the user to **log in** to Facebook in that browser. Logged out, the page stops after ~50 items behind a login wall. Never type the user's credentials yourself.
2. Open each tab you need (`/reels/`, `/videos/`, `/live_videos/`). Recorded lives usually appear under `live_videos/` and `videos/`, not `reels/`.
3. Run `fb_collect_links.js`: paste it into the DevTools Console, or evaluate it over CDP. It scrolls until nothing new loads (it handles layouts that scroll an inner container), then downloads `fb_links_<tab>.txt`. Over CDP, poll `window.__fbLinks.done` and read `Object.values(window.__fbLinks.seen)`.
4. Merge the tabs' lists and feed the file to §1. The same video id can appear as a `reel/` and a `watch/?v=` link; the script dedupes by id.

Driving the browser yourself: launch Chrome with a separate profile, e.g. `--remote-debugging-port=9222 --user-data-dir=<scratch dir>`, so the user's main profile is untouched, then have the user log in in that window.

Filtering: lives vs short reels is best done by `duration_s` in `index.tsv` (e.g. > 1200 s).

## 3. Reading the output

Auto-captions are unedited speech recognition: names, numbers and any language other than the track's are often wrong (Chinese or English words inside a Vietnamese live come out as nonsense syllables). Mark such spots as uncertain instead of guessing, and verify exact quotes by opening the video at the timestamp. For long transcripts (> 5,000 words), read by timestamp range, or split the work across helpers with a fixed extraction brief so nothing is skimmed.
