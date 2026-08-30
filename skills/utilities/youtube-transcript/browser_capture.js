/**
 * browser_capture.js — grab a YouTube transcript through the browser itself.
 *
 * USE WHEN: get_transcript.py reports `IpBlocked`. YouTube blocks cloud-provider IPs
 * (AWS/GCP/Azure…), so the python script fails inside a container, while a browser
 * on a personal machine is not blocked.
 *
 * HOW TO USE (paste each block into the Console of the tab playing the video, or run
 * it via a browser-automation tool such as mcp__claude-in-chrome__javascript_tool):
 *
 *   1. open  https://www.youtube.com/watch?v=<VIDEO_ID>
 *   2. run   openTranscriptPanel()      → opens the "Show transcript" panel
 *   3. run   await collectSegments()    → scrolls so YouTube renders every segment
 *   4. run   downloadTranscript(45)     → groups into paragraphs & downloads a .txt
 *   5. move the file into .jimmy/docs/transcripts/_raw/ and post-process as you like
 *
 * Note: step 3 is mandatory — YouTube uses virtual scrolling; without scrolling you
 * only get the first ~30 lines.
 */

/** Open the transcript panel. Returns true if the button was found. */
function openTranscriptPanel() {
  const expand = document.querySelector("tp-yt-paper-button#expand, #expand");
  if (expand) expand.click();
  const btn = [...document.querySelectorAll("button")].find((b) =>
    /^Show transcript|b\u1ea3n ch\u00e9p l\u1edbi/i.test(b.getAttribute("aria-label") || ""), // en + vi locale labels
  );
  if (btn) btn.click();
  return !!btn;
}

/**
 * Scroll the panel until no new segments appear. Stores the result in window.__RAW.
 * @returns {Promise<{count:number, first:string[], last:string[]}>}
 */
async function collectSegments() {
  const video = document.querySelector("video");
  if (video) video.pause(); // stop the panel auto-scrolling with playback
  await new Promise((r) => setTimeout(r, 3000)); // wait for the panel to load

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
 * Group segments into paragraphs by time window, then download a .txt file.
 * The header matches the format get_transcript.py writes.
 * @param {number} windowSec grouping window, default 45 seconds
 */
function downloadTranscript(windowSec = 45) {
  if (!window.__RAW?.length) throw new Error("No data yet — run collectSegments() first.");

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
    `# Source: YouTube Transcript panel, captured with browser_capture.js`,
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
