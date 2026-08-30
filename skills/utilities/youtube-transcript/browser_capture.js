/**
 * browser_capture.js — lấy transcript YouTube qua chính trình duyệt.
 *
 * DÙNG KHI: get_transcript.py báo `IpBlocked`. YouTube chặn IP của các nhà cung cấp
 * cloud (AWS/GCP/Azure...), nên script python chạy trong container sẽ hỏng, trong khi
 * trình duyệt trên máy cá nhân thì không bị chặn.
 *
 * CÁCH DÙNG (dán từng khối vào Console của tab đang mở video, hoặc chạy qua
 * mcp__claude-in-chrome__javascript_tool):
 *
 *   1. mở  https://www.youtube.com/watch?v=<VIDEO_ID>
 *   2. chạy  openTranscriptPanel()      → mở panel "Show transcript"
 *   3. chạy  await collectSegments()    → cuộn cho YouTube render hết segment
 *   4. chạy  downloadTranscript(45)     → gom đoạn & tải file .txt về máy
 *   5. chuyển file vào docs/<nhóm>/transcripts/_raw/ rồi chạy clean_transcript.py
 *
 * Lưu ý: bước 3 bắt buộc — YouTube dùng virtual scrolling, không cuộn thì chỉ
 * lấy được ~30 dòng đầu.
 */

/** Mở panel bản chép lời. Trả về true nếu tìm thấy nút. */
function openTranscriptPanel() {
  const expand = document.querySelector("tp-yt-paper-button#expand, #expand");
  if (expand) expand.click();
  const btn = [...document.querySelectorAll("button")].find((b) =>
    /^Show transcript|bản chép lời/i.test(b.getAttribute("aria-label") || ""),
  );
  if (btn) btn.click();
  return !!btn;
}

/**
 * Cuộn panel cho tới khi không còn segment mới. Ghi kết quả vào window.__RAW.
 * @returns {Promise<{count:number, first:string[], last:string[]}>}
 */
async function collectSegments() {
  const video = document.querySelector("video");
  if (video) video.pause(); // tránh panel tự cuộn theo tiến độ phát
  await new Promise((r) => setTimeout(r, 3000)); // chờ panel tải xong

  const all = () => [...document.querySelectorAll("ytd-transcript-segment-renderer")];
  const box =
    document.querySelector("ytd-transcript-segment-list-renderer #segments-container") ||
    document.querySelector("ytd-transcript-segment-list-renderer");

  let segs = all();
  let idle = 0;
  for (let i = 0; i < 500 && idle < 10; i++) {
    const before = segs.length;
    if (box) box.scrollTop = box.scrollHeight;
    await new Promise((r) => setTimeout(r, 150));
    segs = all();
    idle = segs.length === before ? idle + 1 : 0;
  }

  window.__RAW = segs
    .map((el) => [
      (el.querySelector(".segment-timestamp")?.textContent || "").trim(),
      (el.querySelector(".segment-text")?.textContent || "").replace(/\s+/g, " ").trim(),
    ])
    .filter((p) => p[1]);

  return {
    count: window.__RAW.length,
    first: window.__RAW[0],
    last: window.__RAW[window.__RAW.length - 1],
  };
}

/**
 * Gom segment thành đoạn theo cửa sổ thời gian rồi tải file .txt về máy.
 * Header khớp định dạng mà clean_transcript.py đọc được.
 * @param {number} windowSec cửa sổ gom đoạn, mặc định 45 giây
 */
function downloadTranscript(windowSec = 45) {
  if (!window.__RAW?.length) throw new Error("Chưa có dữ liệu — chạy collectSegments() trước.");

  const toSec = (ts) => {
    const p = ts.split(":").map(Number);
    return p.length === 3 ? p[0] * 3600 + p[1] * 60 + p[2] : p[0] * 60 + p[1];
  };
  const fmt = (t) => {
    const h = Math.floor(t / 3600);
    const m = Math.floor((t % 3600) / 60);
    const s = t % 60;
    const pad = (n) => String(n).padStart(2, "0");
    return h ? `${h}:${pad(m)}:${pad(s)}` : `${pad(m)}:${pad(s)}`;
  };

  const rows = window.__RAW
    .map(([t, x]) => [toSec(t), x])
    .filter(([, x]) => x && !/^\[.*\]$/.test(x) && !/^(I\s*)+$/.test(x));

  const paras = [];
  let start = rows.length ? rows[0][0] : 0;
  let buf = [];
  for (const [t, x] of rows) {
    if (t - start >= windowSec && buf.length) {
      paras.push([start, buf.join(" ")]);
      start = t;
      buf = [x];
    } else {
      buf.push(x);
    }
  }
  if (buf.length) paras.push([start, buf.join(" ")]);

  const lines = paras.map(([t, x]) => `[${fmt(t)}] ${x.replace(/\s+/g, " ").trim()}`);
  const pr = window.ytInitialPlayerResponse || {};
  const vd = pr.videoDetails || {};
  const vid = vd.videoId || new URLSearchParams(location.search).get("v") || "unknown";
  const dur = Number(vd.lengthSeconds || 0);

  const header = [
    `# YouTube Transcript (${vid})`,
    `# Title: ${vd.title || ""}`,
    `# Channel: ${vd.author || ""}`,
    `# URL: https://www.youtube.com/watch?v=${vid}`,
    `# Duration: ~[${fmt(dur)}] | Segments: ${lines.length} | Words: ${lines.join(" ").split(/\s+/).length}`,
    `# Nguon: panel Transcript cua YouTube, lay bang browser_capture.js`,
    "",
  ].join("\n");

  const blob = new Blob([header + lines.join("\n\n") + "\n"], {
    type: "text/plain;charset=utf-8",
  });
  const a = document.createElement("a");
  a.href = URL.createObjectURL(blob);
  a.download = `${vid}_raw.txt`;
  document.body.appendChild(a);
  a.click();
  a.remove();

  return { paragraphs: lines.length, bytes: blob.size, file: `${vid}_raw.txt` };
}
