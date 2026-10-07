#!/usr/bin/env python3
"""Fetch Facebook auto-captions for one or many video/reel/live URLs.

usage:
  fb_transcript.py <url> [<url> ...]      [--out DIR] [--bucket 45] [--cookies-from-browser chrome]
  fb_transcript.py links.txt              (one URL per line)

Writes <out>/<upload_date>_<id>.txt (header + [mm:ss] buckets) and appends to
<out>/index.tsv. Videos without captions go to <out>/no_captions.txt; videos whose
captions stop well before the end go to <out>/partial_captions.txt.
Re-runnable: ids already present in <out> are skipped.
Needs yt-dlp on PATH or next to this interpreter (pip install yt-dlp).
Exit codes: 0 all ok · 1 at least one failure/no captions · 2 yt-dlp missing.
"""
import argparse, json, re, shutil, subprocess, sys, tempfile
from pathlib import Path

PARTIAL_BELOW = 0.8  # caption end / duration


def find_ytdlp():
    local = Path(sys.executable).with_name("yt-dlp")
    return str(local) if local.exists() else shutil.which("yt-dlp")


def srt_segments(text):
    for block in re.split(r"\n\s*\n", text.strip()):
        lines = block.splitlines()
        if len(lines) < 3 or "-->" not in lines[1]:
            continue
        h, m, s = lines[1].split("-->")[0].strip().replace(",", ".").split(":")
        yield int(h) * 3600 + int(m) * 60 + float(s), " ".join(lines[2:]).strip()


def fmt(sec):
    sec = int(sec)
    return f"{sec // 3600}:{sec % 3600 // 60:02d}:{sec % 60:02d}" if sec >= 3600 else f"{sec // 60:02d}:{sec % 60:02d}"


def fetch(ytdlp, url, bucket, out, cookies, langs="all"):
    with tempfile.TemporaryDirectory() as tmp:
        cmd = [ytdlp, "--skip-download", "--write-auto-subs", "--write-subs", "--sub-langs", langs,
               "--sub-format", "srt", "--print-json", "-o", f"{tmp}/%(id)s.%(ext)s"]
        if cookies:
            cmd += ["--cookies-from-browser", cookies]
        r = subprocess.run(cmd + [url], capture_output=True, text=True)
        if r.returncode != 0 or not r.stdout.strip():
            return None, "error: " + (r.stderr.strip().splitlines() or ["unknown"])[-1]
        meta = json.loads(r.stdout.strip().splitlines()[-1])
        srts = sorted(Path(tmp).glob("*.srt"))
        if not srts:
            return meta, "no captions"
        segs = list(srt_segments(srts[0].read_text(encoding="utf-8")))
        chunks, cur_start, cur = [], None, []
        for start, line in segs:
            if cur_start is None or start - cur_start >= bucket:
                if cur:
                    chunks.append(f"[{fmt(cur_start)}] {' '.join(cur)}")
                cur_start, cur = start, []
            cur.append(line)
        if cur:
            chunks.append(f"[{fmt(cur_start)}] {' '.join(cur)}")
    duration = int(meta.get("duration") or 0)
    last = int(segs[-1][0]) if segs else 0
    coverage = (last / duration) if duration else 1.0
    lang = srts[0].suffixes[-2].lstrip(".") if len(srts[0].suffixes) > 1 else "?"
    header = [f"# {meta.get('title', '')}", f"url: {meta.get('webpage_url', url)}", f"id: {meta['id']}",
              f"uploader: {meta.get('uploader', '')}", f"upload_date: {meta.get('upload_date', '')}",
              f"duration_s: {duration}", f"caption_end_s: {last} (coverage {coverage:.0%})",
              f"source: {meta.get('extractor_key', '').lower()} auto-captions (track {lang}), unedited", ""]
    path = out / f"{meta.get('upload_date', 'nodate')}_{meta['id']}.txt"
    path.write_text("\n".join(header + chunks) + "\n", encoding="utf-8")
    meta["_coverage"], meta["_words"] = coverage, sum(len(c.split()) for c in chunks)
    return meta, path


def main():
    ap = argparse.ArgumentParser(description="Facebook auto-caption transcripts via yt-dlp")
    ap.add_argument("inputs", nargs="+", help="URLs, or text files with one URL per line")
    ap.add_argument("--out", default="transcripts")
    ap.add_argument("--bucket", type=int, default=45, help="seconds per [mm:ss] line")
    ap.add_argument("--cookies-from-browser", dest="cookies", help="e.g. chrome, if a video needs login")
    ap.add_argument("--sub-langs", default="all", help="yt-dlp caption langs; on YouTube use the original track, e.g. en-orig")
    a = ap.parse_args()
    ytdlp = find_ytdlp()
    if not ytdlp:
        print("yt-dlp not found. Install: python3 -m venv .venv && .venv/bin/pip install yt-dlp", file=sys.stderr)
        sys.exit(2)
    urls = []
    for item in a.inputs:
        p = Path(item)
        urls += [l.strip() for l in p.read_text().splitlines() if l.strip()] if p.is_file() else [item]
    urls = list(dict.fromkeys(urls))
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    done = {f.stem.split("_")[-1] for f in out.glob("*_*.txt")}
    failed = 0
    with (out / "index.tsv").open("a", encoding="utf-8") as index:
        for i, url in enumerate(urls, 1):
            vid = re.search(r"(\d{6,})", url)
            if vid and vid.group(1) in done:
                print(f"[{i}/{len(urls)}] skip {url} (already fetched)")
                continue
            meta, res = fetch(ytdlp, url, a.bucket, out, a.cookies, a.sub_langs)
            if isinstance(res, Path):
                cov = meta["_coverage"]
                index.write(f"{meta['id']}\t{meta.get('upload_date', '')}\t{int(meta.get('duration') or 0)}\t"
                            f"{cov:.2f}\t{meta['_words']}\t{meta.get('title', '')}\t{res.name}\n")
                index.flush()
                flag = ""
                if cov < PARTIAL_BELOW:
                    flag = f"  PARTIAL: captions cover {cov:.0%} of the video"
                    with (out / "partial_captions.txt").open("a") as f:
                        f.write(f"{url}\t{cov:.2f}\n")
                print(f"[{i}/{len(urls)}] ok   {res}  ({meta['_words']} words){flag}")
            else:
                failed += 1
                with (out / "no_captions.txt").open("a") as f:
                    f.write(f"{url}\t{res}\n")
                print(f"[{i}/{len(urls)}] --   {url}: {res}")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
