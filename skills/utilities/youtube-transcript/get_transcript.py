#!/usr/bin/env python3
import sys
import site
sys.path.insert(0, site.getusersitepackages())
import re
import json
import argparse
from youtube_transcript_api import YouTubeTranscriptApi

def extract_video_id(url_or_id: str) -> str:
    """Extract YouTube video ID from various URL formats or raw ID."""
    if not url_or_id:
        return ""
    # Raw ID pattern (11 characters)
    if re.match(r'^[a-zA-Z0-9_-]{11}$', url_or_id):
        return url_or_id
    
    # URL patterns
    patterns = [
        r'(?:v=|\/)([a-zA-Z0-9_-]{11})(?:[&?]|$)',
        r'youtu\.be\/([a-zA-Z0-9_-]{11})',
        r'embed\/([a-zA-Z0-9_-]{11})',
        r'shorts\/([a-zA-Z0-9_-]{11})'
    ]
    for pattern in patterns:
        match = re.search(pattern, url_or_id)
        if match:
            return match.group(1)
    return url_or_id

class IpBlockedError(RuntimeError):
    """YouTube blocked the calling IP (common when running from a container/cloud)."""


BROWSER_FALLBACK_HINT = """
YouTube blocked the calling IP (IpBlocked).

Cause: cloud-provider IPs (AWS/GCP/Azure, CI containers...) are blocked by YouTube
by default. Re-running this script from a personal machine usually works.

If a personal machine is not an option, use the browser path — see
  browser_capture.js next to this script.
Open the video in Chrome and run, in order:
  openTranscriptPanel()
  await collectSegments()
  downloadTranscript(45)
The downloaded .txt has the same header format as this script's output, so any
post-processing you apply to one works on the other.
""".strip()


def _list_transcripts(ytt, video_id):
    """Compatible with several API versions: .list() (new) and .list_transcripts() (old)."""
    for name in ("list", "list_transcripts"):
        fn = getattr(ytt, name, None)
        if callable(fn):
            return fn(video_id)
    raise RuntimeError("This youtube-transcript-api version has neither .list() nor .list_transcripts()")


def get_transcript(video_id: str, languages=['vi', 'en', 'en-US']):
    """Fetch transcript using youtube_transcript_api."""
    ytt = YouTubeTranscriptApi()
    first_err = None
    try:
        transcript = ytt.fetch(video_id, languages=languages)
    except Exception as e:
        first_err = e
        if type(e).__name__ in ("IpBlocked", "RequestBlocked"):
            raise IpBlockedError(BROWSER_FALLBACK_HINT) from e
        try:
            transcript_list = _list_transcripts(ytt, video_id)
            first_t = next(iter(transcript_list))
            transcript = first_t.fetch()
        except Exception as e2:
            if type(e2).__name__ in ("IpBlocked", "RequestBlocked"):
                raise IpBlockedError(BROWSER_FALLBACK_HINT) from e2
            raise RuntimeError(
                f"Could not fetch a transcript for video '{video_id}'.\n"
                f"  - fetch(languages={languages}): {type(first_err).__name__}: {first_err}\n"
                f"  - fallback list(): {type(e2).__name__}: {e2}"
            ) from e2
    
    items = []
    for snippet in transcript:
        items.append({
            'start': getattr(snippet, 'start', 0),
            'duration': getattr(snippet, 'duration', 0),
            'text': getattr(snippet, 'text', '')
        })
    return items

def format_timestamp(seconds: float) -> str:
    total = int(seconds)
    hrs, rem = divmod(total, 3600)
    mins, secs = divmod(rem, 60)
    if hrs:
        return f"[{hrs}:{mins:02d}:{secs:02d}]"
    return f"[{mins:02d}:{secs:02d}]"

def main():
    parser = argparse.ArgumentParser(description="Extract full YouTube video transcript.")
    parser.add_argument("url_or_id", help="YouTube URL or Video ID")
    parser.add_argument("--out", "-o", help="Output file path (default: transcript_<id>.txt)", default=None)
    parser.add_argument("--json", help="Output as JSON", action="store_true")
    args = parser.parse_args()

    vid = extract_video_id(args.url_or_id)
    if not vid:
        print("Error: Invalid YouTube URL or Video ID", file=sys.stderr)
        sys.exit(1)

    try:
        items = get_transcript(vid)
    except IpBlockedError as err:
        print(str(err), file=sys.stderr)
        sys.exit(2)
    except Exception as err:
        print(f"Error: {err}", file=sys.stderr)
        sys.exit(1)

    full_text = " ".join(item['text'] for item in items)
    word_count = len(full_text.split())
    char_count = len(full_text)
    total_sec = items[-1]['start'] + items[-1]['duration'] if items else 0
    duration_str = format_timestamp(total_sec)

    print(f"Video ID: {vid}")
    print(f"Duration: ~{duration_str}")
    print(f"Total Segments: {len(items)}")
    print(f"Word Count: {word_count}")
    print(f"Character Count: {char_count}")

    if args.json:
        result = {
            'video_id': vid,
            'duration_seconds': total_sec,
            'word_count': word_count,
            'character_count': char_count,
            'transcript': items
        }
        output_content = json.dumps(result, ensure_ascii=False, indent=2)
    else:
        lines = []
        lines.append(f"# YouTube Transcript ({vid})")
        lines.append(f"# URL: https://www.youtube.com/watch?v={vid}")
        lines.append(f"# Duration: ~{duration_str} | Segments: {len(items)} | Words: {word_count}")
        lines.append("# Source: YouTube captions, fetched with get_transcript.py\n")
        for item in items:
            ts = format_timestamp(item['start'])
            lines.append(f"{ts} {item['text']}")
        output_content = "\n".join(lines)

    out_path = args.out or f"transcript_{vid}.txt"
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(output_content)

    print(f"Successfully saved transcript to: {out_path}")

if __name__ == "__main__":
    main()
