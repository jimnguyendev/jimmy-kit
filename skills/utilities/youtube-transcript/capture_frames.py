#!/usr/bin/env python3
"""
capture_frames.py — cut slide frames from a YouTube video (or a local file).

Three modes:

  1. --at        cut at exactly the timestamps you specify
  2. --at-guide  read a guide .md, collect every [mm:ss] / [h:mm:ss] timestamp, cut those
  3. --auto      detect slide changes automatically with ffmpeg scene detection

Examples:

    # cut exactly 5 timestamps
    python3 capture_frames.py Xx3V8i11weo --at 3:56,13:34,24:26,1:08:53,1:36:09 \\
        --out docs/notes/screenshots --prefix v06

    # take timestamps straight from a written guide
    python3 capture_frames.py Xx3V8i11weo --at-guide docs/notes/guides/v06_guide.md \\
        --out docs/notes/screenshots --prefix v06 --emit-markdown

    # detect slide changes (download the video first — much faster)
    python3 capture_frames.py Xx3V8i11weo --auto --threshold 0.3 --download \\
        --out docs/notes/screenshots --prefix v06

    # work from a file you already have
    python3 capture_frames.py --local lecture.mp4 --auto --out ./slides

DEPENDENCIES
    ffmpeg, ffprobe   required
    yt-dlp            required when pulling from YouTube (skipped with --local)
    Pillow            optional — only used by --dedupe

WHERE TO RUN
    Run on a personal machine. YouTube blocks cloud-provider IP ranges, so running
    inside a container/CI fails at the yt-dlp step, same as get_transcript.py.
    See SKILL.md, section "Where to run".
"""
from __future__ import annotations

import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

TS_IN_MD = re.compile(r"\[(\d{1,2}:\d{2}(?::\d{2})?)\]")
SCENE_PTS = re.compile(r"pts_time:([0-9.]+)")
MIN_THRESHOLD = 0.04


# ---------------------------------------------------------------- shared helpers
def need(binary: str, why: str) -> str:
    path = shutil.which(binary)
    if not path:
        sys.exit(f"Missing `{binary}` — {why}")
    return path


def run(cmd: list[str], capture: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, capture_output=capture, text=True)


def parse_ts(text: str) -> int:
    """'3:56' -> 236 ; '1:08:53' -> 4133 ; '236' -> 236"""
    text = text.strip().lstrip("[").rstrip("]")
    if ":" not in text:
        return int(float(text))
    parts = [int(p) for p in text.split(":")]
    if len(parts) == 2:
        return parts[0] * 60 + parts[1]
    if len(parts) == 3:
        return parts[0] * 3600 + parts[1] * 60 + parts[2]
    raise ValueError(f"Cannot parse timestamp: {text!r}")


def fmt_ts(sec: int) -> str:
    h, rem = divmod(int(sec), 3600)
    m, s = divmod(rem, 60)
    return f"{h}:{m:02d}:{s:02d}" if h else f"{m:02d}:{s:02d}"


def slug_ts(sec: int) -> str:
    h, rem = divmod(int(sec), 3600)
    m, s = divmod(rem, 60)
    return f"{h}h{m:02d}m{s:02d}s" if h else f"{m:02d}m{s:02d}s"


def extract_video_id(url_or_id: str) -> str:
    if re.fullmatch(r"[a-zA-Z0-9_-]{11}", url_or_id):
        return url_or_id
    for pat in (
        r"(?:v=|/)([a-zA-Z0-9_-]{11})(?:[&?]|$)",
        r"youtu\.be/([a-zA-Z0-9_-]{11})",
        r"embed/([a-zA-Z0-9_-]{11})",
    ):
        m = re.search(pat, url_or_id)
        if m:
            return m.group(1)
    return url_or_id


# ---------------------------------------------------------------- video source
def stream_url(video_id: str, max_height: int) -> str:
    """Get a video-only stream URL. No audio needed — we only cut frames."""
    need("yt-dlp", "needed to fetch the YouTube stream. Install: pip install -U yt-dlp")
    fmt = f"bv*[height<={max_height}]/bv*/b[height<={max_height}]/b"
    p = run(["yt-dlp", "-f", fmt, "-g", "--no-warnings", f"https://www.youtube.com/watch?v={video_id}"])
    if p.returncode != 0 or not p.stdout.strip():
        err = (p.stderr or "").strip()
        if "blocked" in err.lower() or "sign in to confirm" in err.lower():
            sys.exit(
                "yt-dlp was blocked by YouTube.\n"
                "Usual cause: running from a cloud IP (container/CI). Re-run on a personal machine.\n"
                f"Details: {err[:400]}"
            )
        sys.exit(f"yt-dlp error:\n{err[:600]}")
    return p.stdout.strip().splitlines()[0]


def download(video_id: str, max_height: int, dest_dir: Path) -> Path:
    """Download the whole video — much faster when cutting >10 frames or running --auto."""
    need("yt-dlp", "needed to download the video. Install: pip install -U yt-dlp")
    dest_dir.mkdir(parents=True, exist_ok=True)
    out = dest_dir / f"{video_id}.mp4"
    if out.exists():
        print(f"  reusing downloaded file: {out}")
        return out
    fmt = f"bv*[height<={max_height}]+ba/b[height<={max_height}]/b"
    p = run(
        ["yt-dlp", "-f", fmt, "--merge-output-format", "mp4", "-o", str(out),
         "--no-warnings", f"https://www.youtube.com/watch?v={video_id}"],
        capture=False,
    )
    if p.returncode != 0 or not out.exists():
        sys.exit("yt-dlp could not download the video. If you are in a container/CI, re-run on a personal machine.")
    return out


def probe_duration(src: str) -> float:
    need("ffprobe", "ships with ffmpeg")
    p = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", src])
    try:
        return float(p.stdout.strip())
    except ValueError:
        return 0.0


# ---------------------------------------------------------------- frame cutting
def detect_crop(src: str, at: int) -> str | None:
    """Detect black borders (meeting/Zoom recordings are often letterboxed) via cropdetect."""
    p = run(["ffmpeg", "-hide_banner", "-ss", str(at), "-i", src, "-frames:v", "60",
             "-vf", "cropdetect=24:16:0", "-f", "null", "-"])
    crops = re.findall(r"crop=(\d+:\d+:\d+:\d+)", (p.stderr or ""))
    return crops[-1] if crops else None


def grab_one(src: str, sec: int, dest: Path, width: int | None, crop: str | None) -> bool:
    """`-ss` goes BEFORE `-i` — fast seek, no decoding from the start of the video."""
    vf = []
    if crop:
        vf.append(f"crop={crop}")
    if width:
        vf.append(f"scale={width}:-2:flags=lanczos")
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "error", "-y",
           "-ss", str(sec), "-i", src, "-frames:v", "1"]
    if vf:
        cmd += ["-vf", ",".join(vf)]
    cmd += [str(dest)]
    return run(cmd).returncode == 0 and dest.exists() and dest.stat().st_size > 0


def detect_scenes(src: str, threshold: float, limit: int, depth: int = 0) -> list[int]:
    """Detect slide-change moments. Returns a list of seconds (rounded, de-duplicated)."""
    p = run(["ffmpeg", "-hide_banner", "-i", src,
             "-vf", f"select='gt(scene,{threshold})',metadata=print:file=-",
             "-fps_mode", "vfr", "-f", "null", "-"])
    out = (p.stdout or "") + (p.stderr or "")
    if p.returncode != 0 and ("Unrecognized option" in out or "fps_mode" in out):
        p = run(["ffmpeg", "-hide_banner", "-i", src,
                 "-vf", f"select='gt(scene,{threshold})',metadata=print:file=-",
                 "-vsync", "vfr", "-f", "null", "-"])
        out = (p.stdout or "") + (p.stderr or "")

    secs: list[int] = []
    for m in SCENE_PTS.finditer(out):
        s = int(float(m.group(1)))
        # a slide change usually produces a few consecutive transition frames -> merge within 3s
        if not secs or s - secs[-1] >= 3:
            secs.append(s)

    # A too-strict threshold is the most common failure: white-background slides that
    # only change text score very low. If too few hits, lower the threshold one step and retry.
    if len(secs) < 3 and threshold > MIN_THRESHOLD and depth < 2:
        lower = max(MIN_THRESHOLD, round(threshold / 2, 3))
        print(f"  only {len(secs)} hits at threshold={threshold} — retrying at {lower}")
        return detect_scenes(src, lower, limit, depth + 1)

    if limit and len(secs) > limit:
        step = len(secs) / limit
        secs = [secs[int(i * step)] for i in range(limit)]
    return secs


def dedupe(paths: list[Path], distance: int = 6) -> list[Path]:
    """Drop near-duplicate images via average-hash. Needs Pillow; silently skipped otherwise."""
    try:
        from PIL import Image
    except ImportError:
        print("  (skipping --dedupe: Pillow not installed)")
        return paths

    def ahash(p: Path) -> int:
        img = Image.open(p).convert("L").resize((8, 8))
        px = list(img.getdata())
        avg = sum(px) / len(px)
        bits = 0
        for i, v in enumerate(px):
            if v > avg:
                bits |= 1 << i
        return bits

    kept: list[Path] = []
    hashes: list[int] = []
    for p in paths:
        h = ahash(p)
        if any(bin(h ^ prev).count("1") <= distance for prev in hashes):
            p.unlink(missing_ok=True)
            continue
        kept.append(p)
        hashes.append(h)
    return kept


# ---------------------------------------------------------------- main
def main() -> int:
    ap = argparse.ArgumentParser(
        description="Cut slide frames from a YouTube video or a local file.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("url_or_id", nargs="?", help="YouTube URL or Video ID")
    ap.add_argument("--local", type=Path, help="Use an existing video file instead of downloading from YouTube")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--at", help="Comma-separated timestamps: 3:56,13:34,1:08:53")
    mode.add_argument("--at-guide", type=Path, help=".md file — collect every [mm:ss] found in it")
    mode.add_argument("--auto", action="store_true", help="Detect slide changes automatically")
    ap.add_argument("--out", type=Path, default=Path("./screenshots"), help="Output directory")
    ap.add_argument("--prefix", default="", help="Filename prefix, e.g. v06")
    ap.add_argument("--threshold", type=float, default=0.1,
                    help="Scene-detection threshold for --auto. 0.05 = catches animations · 0.1 = good for text-only slide changes (default) · 0.2 = major transitions only · 0.3 = full scene cuts only")
    ap.add_argument("--limit", type=int, default=40, help="Max frames in --auto mode. Default 40")
    ap.add_argument("--width", type=int, default=1600, help="Resize width. 0 = keep original")
    ap.add_argument("--max-height", type=int, default=1080, help="Max stream quality")
    ap.add_argument("--crop", choices=["auto", "off"], default="off", help="Crop black borders")
    ap.add_argument("--download", action="store_true",
                    help="Download the whole video first. Recommended when cutting >10 frames or using --auto")
    ap.add_argument("--dedupe", action="store_true", help="Drop near-duplicate frames")
    ap.add_argument("--emit-markdown", action="store_true",
                    help="Print a ready-to-paste markdown block for the guide")
    ap.add_argument("--dry-run", action="store_true", help="Only print which timestamps would be cut")
    args = ap.parse_args()

    need("ffmpeg", "install via brew install ffmpeg / apt install ffmpeg")

    # ----- resolve source -----
    if args.local:
        if not args.local.exists():
            sys.exit(f"File not found: {args.local}")
        src, vid = str(args.local), args.local.stem
    else:
        if not args.url_or_id:
            sys.exit("Need a URL/Video ID, or use --local <file>")
        vid = extract_video_id(args.url_or_id)
        if args.download or args.auto:
            src = str(download(vid, args.max_height, Path(".cache_video")))
        else:
            print(f"Fetching stream URL for {vid} …")
            src = stream_url(vid, args.max_height)

    prefix = args.prefix or vid

    # ----- resolve timestamp list -----
    if args.at:
        secs = sorted({parse_ts(t) for t in args.at.split(",") if t.strip()})
        how = "manual"
    elif args.at_guide:
        if not args.at_guide.exists():
            sys.exit(f"Guide file not found: {args.at_guide}")
        found = TS_IN_MD.findall(args.at_guide.read_text(encoding="utf-8", errors="replace"))
        secs = sorted({parse_ts(t) for t in found})
        how = f"read from {args.at_guide.name}"
    else:
        print(f"Detecting slide changes (threshold={args.threshold}) — this takes a few minutes …")
        secs = detect_scenes(src, args.threshold, args.limit)
        how = f"scene detection @ {args.threshold}"

    dur = probe_duration(src)
    if dur:
        before = len(secs)
        secs = [s for s in secs if s < dur - 1]
        if len(secs) != before:
            print(f"  dropped {before - len(secs)} timestamps beyond video duration ({fmt_ts(int(dur))})")

    if not secs:
        sys.exit("No timestamps to cut.")

    print(f"\n{len(secs)} timestamps ({how}): {', '.join(fmt_ts(s) for s in secs[:12])}"
          f"{' …' if len(secs) > 12 else ''}")
    if args.dry_run:
        return 0

    # ----- cut -----
    crop = None
    if args.crop == "auto":
        crop = detect_crop(src, secs[len(secs) // 2])
        print(f"  detected crop: {crop or 'no black borders'}")

    args.out.mkdir(parents=True, exist_ok=True)
    width = args.width or None
    made: list[tuple[int, Path]] = []
    for i, sec in enumerate(secs, 1):
        dest = args.out / f"{prefix}_{i:02d}_{slug_ts(sec)}.png"
        ok = grab_one(src, sec, dest, width, crop)
        print(f"  [{i:>2}/{len(secs)}] {fmt_ts(sec):>8}  {'✓ ' + dest.name if ok else '✗ failed'}")
        if ok:
            made.append((sec, dest))

    if args.dedupe and made:
        kept = dedupe([p for _, p in made])
        kept_set = set(kept)
        removed = len(made) - len(kept)
        made = [(s, p) for s, p in made if p in kept_set]
        if removed:
            print(f"\n  --dedupe: dropped {removed} near-duplicate frames")

    print(f"\nDone: {len(made)}/{len(secs)} frames → {args.out}")

    if args.emit_markdown and made:
        print("\n--- paste into the guide ---")
        for sec, p in made:
            rel = f"../screenshots/{p.name}"
            print(f"![Slide {fmt_ts(sec)}]({rel})\n*Slide at `[{fmt_ts(sec)}]`*\n")

    manifest = args.out / f"{prefix}_manifest.json"
    manifest.write_text(json.dumps(
        {"video_id": vid, "mode": how, "frames": [
            {"timestamp": fmt_ts(s), "seconds": s, "file": p.name} for s, p in made]},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Manifest: {manifest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
