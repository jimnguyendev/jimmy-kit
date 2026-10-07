// Collect every video / reel / live link from a Facebook page tab.
// Paste into the browser DevTools Console (or run via a CDP evaluate) while on e.g.
//   https://www.facebook.com/<page>/reels/
//   https://www.facebook.com/<page>/videos/
//   https://www.facebook.com/<page>/live_videos/
// Log in first: a logged-out page stops loading after ~50 items and shows a login wall.
// Auto-scrolls until nothing new appears, then:
//   - Console paste: downloads fb_links_<tab>.txt (one URL per line)
//   - CDP / automation: read window.__fbLinks.done, then Object.values(window.__fbLinks.seen)
(async () => {
  const state = (window.__fbLinks = { seen: {}, idle: 0, done: false });
  const re = /facebook\.com\/(?:reel\/(\d+)|[^/?]+\/videos\/(?:[^/?]+\/)?(\d+)|watch\/?\?v=(\d+))/;
  const grab = () => document.querySelectorAll("a[href]").forEach(a => {
    const m = a.href.match(re);
    const id = m && (m[1] || m[2] || m[3]);
    if (id && !state.seen[id]) {
      state.seen[id] = m[1] ? `https://www.facebook.com/reel/${id}` : `https://www.facebook.com/watch/?v=${id}`;
    }
  });
  // Some layouts scroll an inner container instead of the window: scroll both.
  const scrollAll = () => {
    window.scrollTo(0, document.scrollingElement.scrollHeight);
    document.querySelectorAll("div").forEach(d => {
      if (d.scrollHeight > d.clientHeight + 200 && /auto|scroll/.test(getComputedStyle(d).overflowY)) d.scrollTop = d.scrollHeight;
    });
  };
  grab();
  while (state.idle < 8) {                      // stop after ~8 scrolls with nothing new
    const before = Object.keys(state.seen).length;
    scrollAll();
    await new Promise(r => setTimeout(r, 2500));
    grab();
    const now = Object.keys(state.seen).length;
    state.idle = now === before ? state.idle + 1 : 0;
    console.log(`links: ${now}`);
  }
  state.done = true;
  const urls = Object.values(state.seen);
  const tab = location.pathname.split("/").filter(Boolean).pop() || "page";
  try {
    const a = Object.assign(document.createElement("a"), {
      href: URL.createObjectURL(new Blob([urls.join("\n") + "\n"], { type: "text/plain" })),
      download: `fb_links_${tab}.txt`,
    });
    a.click();
  } catch (e) { /* automation contexts may block downloads; read window.__fbLinks instead */ }
  console.log(`done: ${urls.length} links`);
})();
