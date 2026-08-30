#!/usr/bin/env python3
"""
capture_frames.py — cắt ảnh slide từ video YouTube (hoặc file local).

Ba chế độ:

  1. --at        cắt đúng các mốc thời gian bạn chỉ định
  2. --at-guide  đọc file guide .md, lấy mọi timestamp dạng [mm:ss] / [h:mm:ss] rồi cắt
  3. --auto      tự dò thời điểm slide đổi bằng scene detection của ffmpeg

Ví dụ:

    # cắt đúng 5 mốc
    python3 capture_frames.py Xx3V8i11weo --at 3:56,13:34,24:26,1:08:53,1:36:09 \\
        --out docs/prep/screenshots --prefix v06

    # lấy timestamp trực tiếp từ guide đã viết
    python3 capture_frames.py Xx3V8i11weo --at-guide docs/prep/guides/v06_guide.md \\
        --out docs/prep/screenshots --prefix v06 --emit-markdown

    # tự dò slide đổi (tải video về trước cho nhanh)
    python3 capture_frames.py Xx3V8i11weo --auto --threshold 0.3 --download \\
        --out docs/prep/screenshots --prefix v06

    # làm việc với file đã có sẵn
    python3 capture_frames.py --local buoi_hoc.mp4 --auto --out ./slides

PHỤ THUỘC
    ffmpeg, ffprobe   bắt buộc
    yt-dlp            bắt buộc nếu lấy từ YouTube (bỏ qua khi dùng --local)
    Pillow            không bắt buộc — chỉ dùng cho --dedupe

CHẠY Ở ĐÂU
    Phải chạy trên máy cá nhân. YouTube chặn dải IP của các nhà cung cấp cloud, nên
    chạy trong container/CI sẽ hỏng ở bước yt-dlp giống như get_transcript.py.
    Xem SKILL.md mục "Chạy ở đâu".
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


# ---------------------------------------------------------------- tiện ích chung
def need(binary: str, why: str) -> str:
    path = shutil.which(binary)
    if not path:
        sys.exit(f"Thiếu `{binary}` — {why}")
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
    raise ValueError(f"Không đọc được timestamp: {text!r}")


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


# ---------------------------------------------------------------- lấy nguồn video
def stream_url(video_id: str, max_height: int) -> str:
    """Lấy URL stream video-only. Không cần audio vì chỉ cắt ảnh."""
    need("yt-dlp", "cần để lấy stream YouTube. Cài: pip install -U yt-dlp")
    fmt = f"bv*[height<={max_height}]/bv*/b[height<={max_height}]/b"
    p = run(["yt-dlp", "-f", fmt, "-g", "--no-warnings", f"https://www.youtube.com/watch?v={video_id}"])
    if p.returncode != 0 or not p.stdout.strip():
        err = (p.stderr or "").strip()
        if "blocked" in err.lower() or "sign in to confirm" in err.lower():
            sys.exit(
                "yt-dlp bị YouTube chặn.\n"
                "Nguyên nhân thường gặp: đang chạy từ IP cloud (container/CI). Chạy lại trên máy cá nhân.\n"
                f"Chi tiết: {err[:400]}"
            )
        sys.exit(f"yt-dlp lỗi:\n{err[:600]}")
    return p.stdout.strip().splitlines()[0]


def download(video_id: str, max_height: int, dest_dir: Path) -> Path:
    """Tải hẳn video về — nhanh hơn nhiều khi cần cắt >10 khung hoặc chạy --auto."""
    need("yt-dlp", "cần để tải video. Cài: pip install -U yt-dlp")
    dest_dir.mkdir(parents=True, exist_ok=True)
    out = dest_dir / f"{video_id}.mp4"
    if out.exists():
        print(f"  dùng lại file đã tải: {out}")
        return out
    fmt = f"bv*[height<={max_height}]+ba/b[height<={max_height}]/b"
    p = run(
        ["yt-dlp", "-f", fmt, "--merge-output-format", "mp4", "-o", str(out),
         "--no-warnings", f"https://www.youtube.com/watch?v={video_id}"],
        capture=False,
    )
    if p.returncode != 0 or not out.exists():
        sys.exit("yt-dlp không tải được video. Nếu đang ở container/CI thì chạy lại trên máy cá nhân.")
    return out


def probe_duration(src: str) -> float:
    need("ffprobe", "đi kèm ffmpeg")
    p = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
             "-of", "default=nw=1:nk=1", src])
    try:
        return float(p.stdout.strip())
    except ValueError:
        return 0.0


# ---------------------------------------------------------------- cắt khung hình
def detect_crop(src: str, at: int) -> str | None:
    """Dò viền đen (video họp/Zoom hay có letterbox) bằng cropdetect."""
    p = run(["ffmpeg", "-hide_banner", "-ss", str(at), "-i", src, "-frames:v", "60",
             "-vf", "cropdetect=24:16:0", "-f", "null", "-"])
    crops = re.findall(r"crop=(\d+:\d+:\d+:\d+)", (p.stderr or ""))
    return crops[-1] if crops else None


def grab_one(src: str, sec: int, dest: Path, width: int | None, crop: str | None) -> bool:
    """`-ss` ĐẶT TRƯỚC `-i` — seek nhanh, không giải mã từ đầu video."""
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
    """Dò thời điểm slide đổi. Trả về danh sách giây (đã làm tròn, đã khử trùng)."""
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
        # slide đổi thì thường có vài frame chuyển tiếp liền nhau -> gộp trong 3 giây
        if not secs or s - secs[-1] >= 3:
            secs.append(s)

    # Ngưỡng quá chặt là lỗi hay gặp nhất: slide nền trắng chỉ đổi chữ cho điểm
    # scene rất thấp. Bắt được quá ít thì tự hạ ngưỡng một bậc rồi thử lại.
    if len(secs) < 3 and threshold > MIN_THRESHOLD and depth < 2:
        lower = max(MIN_THRESHOLD, round(threshold / 2, 3))
        print(f"  chỉ thấy {len(secs)} mốc ở threshold={threshold} — thử lại ở {lower}")
        return detect_scenes(src, lower, limit, depth + 1)

    if limit and len(secs) > limit:
        step = len(secs) / limit
        secs = [secs[int(i * step)] for i in range(limit)]
    return secs


def dedupe(paths: list[Path], distance: int = 6) -> list[Path]:
    """Bỏ ảnh gần trùng bằng average-hash. Cần Pillow; không có thì bỏ qua êm."""
    try:
        from PIL import Image
    except ImportError:
        print("  (bỏ qua --dedupe: chưa cài Pillow)")
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
        description="Cắt ảnh slide từ video YouTube hoặc file local.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("url_or_id", nargs="?", help="URL hoặc Video ID của YouTube")
    ap.add_argument("--local", type=Path, help="Dùng file video có sẵn thay vì tải từ YouTube")
    mode = ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--at", help="Danh sách mốc, cách nhau bởi dấu phẩy: 3:56,13:34,1:08:53")
    mode.add_argument("--at-guide", type=Path, help="File .md — lấy mọi [mm:ss] trong đó")
    mode.add_argument("--auto", action="store_true", help="Tự dò thời điểm slide đổi")
    ap.add_argument("--out", type=Path, default=Path("./screenshots"), help="Thư mục ra")
    ap.add_argument("--prefix", default="", help="Tiền tố tên file, vd v06")
    ap.add_argument("--threshold", type=float, default=0.1,
                    help="Ngưỡng scene detection cho --auto. 0.05 = bắt cả animation · 0.1 = hợp cho slide đổi chữ (mặc định) · 0.2 = chỉ chuyển lớn · 0.3 = chỉ đổi cảnh hẳn")
    ap.add_argument("--limit", type=int, default=40, help="Số ảnh tối đa ở chế độ --auto. Mặc định 40")
    ap.add_argument("--width", type=int, default=1600, help="Resize chiều ngang. 0 = giữ nguyên")
    ap.add_argument("--max-height", type=int, default=1080, help="Chất lượng stream tối đa")
    ap.add_argument("--crop", choices=["auto", "off"], default="off", help="Cắt viền đen")
    ap.add_argument("--download", action="store_true",
                    help="Tải hẳn video về trước. Nên bật khi cắt >10 ảnh hoặc dùng --auto")
    ap.add_argument("--dedupe", action="store_true", help="Bỏ các ảnh gần trùng nhau")
    ap.add_argument("--emit-markdown", action="store_true",
                    help="In sẵn khối markdown để dán vào guide")
    ap.add_argument("--dry-run", action="store_true", help="Chỉ in ra sẽ cắt mốc nào, không cắt")
    args = ap.parse_args()

    need("ffmpeg", "cài qua brew install ffmpeg / apt install ffmpeg")

    # ----- xác định nguồn -----
    if args.local:
        if not args.local.exists():
            sys.exit(f"Không thấy file: {args.local}")
        src, vid = str(args.local), args.local.stem
    else:
        if not args.url_or_id:
            sys.exit("Cần URL/Video ID, hoặc dùng --local <file>")
        vid = extract_video_id(args.url_or_id)
        if args.download or args.auto:
            src = str(download(vid, args.max_height, Path(".cache_video")))
        else:
            print(f"Lấy stream URL cho {vid} …")
            src = stream_url(vid, args.max_height)

    prefix = args.prefix or vid

    # ----- xác định danh sách mốc -----
    if args.at:
        secs = sorted({parse_ts(t) for t in args.at.split(",") if t.strip()})
        how = "chỉ định tay"
    elif args.at_guide:
        if not args.at_guide.exists():
            sys.exit(f"Không thấy file guide: {args.at_guide}")
        found = TS_IN_MD.findall(args.at_guide.read_text(encoding="utf-8", errors="replace"))
        secs = sorted({parse_ts(t) for t in found})
        how = f"đọc từ {args.at_guide.name}"
    else:
        print(f"Dò slide đổi (threshold={args.threshold}) — bước này mất vài phút …")
        secs = detect_scenes(src, args.threshold, args.limit)
        how = f"scene detection @ {args.threshold}"

    dur = probe_duration(src)
    if dur:
        before = len(secs)
        secs = [s for s in secs if s < dur - 1]
        if len(secs) != before:
            print(f"  bỏ {before - len(secs)} mốc vượt quá thời lượng video ({fmt_ts(int(dur))})")

    if not secs:
        sys.exit("Không có mốc nào để cắt.")

    print(f"\n{len(secs)} mốc ({how}): {', '.join(fmt_ts(s) for s in secs[:12])}"
          f"{' …' if len(secs) > 12 else ''}")
    if args.dry_run:
        return 0

    # ----- cắt -----
    crop = None
    if args.crop == "auto":
        crop = detect_crop(src, secs[len(secs) // 2])
        print(f"  crop phát hiện: {crop or 'không có viền đen'}")

    args.out.mkdir(parents=True, exist_ok=True)
    width = args.width or None
    made: list[tuple[int, Path]] = []
    for i, sec in enumerate(secs, 1):
        dest = args.out / f"{prefix}_{i:02d}_{slug_ts(sec)}.png"
        ok = grab_one(src, sec, dest, width, crop)
        print(f"  [{i:>2}/{len(secs)}] {fmt_ts(sec):>8}  {'✓ ' + dest.name if ok else '✗ lỗi'}")
        if ok:
            made.append((sec, dest))

    if args.dedupe and made:
        kept = dedupe([p for _, p in made])
        kept_set = set(kept)
        removed = len(made) - len(kept)
        made = [(s, p) for s, p in made if p in kept_set]
        if removed:
            print(f"\n  --dedupe: bỏ {removed} ảnh gần trùng")

    print(f"\nXong: {len(made)}/{len(secs)} ảnh → {args.out}")

    if args.emit_markdown and made:
        print("\n--- dán vào guide ---")
        for sec, p in made:
            rel = f"../screenshots/{p.name}"
            print(f"![Slide {fmt_ts(sec)}]({rel})\n*Slide tại `[{fmt_ts(sec)}]`*\n")

    manifest = args.out / f"{prefix}_manifest.json"
    manifest.write_text(json.dumps(
        {"video_id": vid, "mode": how, "frames": [
            {"timestamp": fmt_ts(s), "seconds": s, "file": p.name} for s, p in made]},
        ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Manifest: {manifest}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
