#!/usr/bin/env node
// layout_sweep.mjs — measure layout defects on a running web app through Chrome DevTools Protocol.
//
// Finds what typecheck, lint and component tests cannot: containers that scroll sideways, interactive
// controls that overlap, controls that run past the panel or dialog that clips them, and raw i18n keys
// or unrendered template text on screen. It reads the DOM; it never asks a model to look at pixels.
// A route that does not load (HTTP >= 400, e.g. a stale dev server on the port, or no text after 15 s) and a
// click text that is not on screen are findings too, so a broken run never prints "ok".
//
// usage: node layout_sweep.mjs --cdp http://127.0.0.1:9333 --base http://localhost:5173 --routes routes.json
//                              [--tab <target id prefix>] [--width 1440] [--height 900] [--out report.json]
// routes.json: [{"name": "settings", "path": "/settings"},
//               {"name": "journey panel", "path": "/journeys/x", "open": ["Start step"]}]
//   "open": visible texts clicked in order after load (a real mouse event at the element centre), so
//   panels and dialogs are measured too. Opt-outs: data-allow-scroll (may scroll sideways), data-allow-overlap,
//   data-allow-raw (shows template syntax on purpose, e.g. an example chip); <code> and <pre> are skipped.
// exit: 0 no findings, 1 findings, 2 usage or connection error. Needs Node 22+ (global WebSocket).

import { readFileSync, writeFileSync } from 'node:fs';

const args = Object.fromEntries(process.argv.slice(2).reduce((acc, a, i, all) => {
  if (a.startsWith('--')) acc.push([a.slice(2), all[i + 1] && !all[i + 1].startsWith('--') ? all[i + 1] : 'true']);
  return acc;
}, []));
if (!args.cdp || !args.base || !args.routes) {
  console.error('usage: node layout_sweep.mjs --cdp <url> --base <url> --routes <file> [--tab id] [--out file]');
  process.exit(2);
}
const width = Number(args.width ?? 1440);
const height = Number(args.height ?? 900);
const routes = JSON.parse(readFileSync(args.routes, 'utf8'));
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

let targets;
try {
  targets = await (await fetch(`${args.cdp}/json/list`, { signal: AbortSignal.timeout(5000) })).json();
} catch (err) {
  console.error(`cannot reach CDP at ${args.cdp}: ${err.message}`);
  process.exit(2);
}
const tab = targets.find((t) => t.type === 'page' && (!args.tab || t.id.startsWith(args.tab)));
if (!tab) {
  console.error('no page target; open a tab in the browser the CDP port belongs to');
  process.exit(2);
}

const ws = new WebSocket(tab.webSocketDebuggerUrl);
let nextId = 0;
const pending = new Map();
ws.onmessage = (e) => {
  const m = JSON.parse(e.data);
  // A beforeunload or alert dialog freezes the page and every later call; accept it.
  if (m.method === 'Page.javascriptDialogOpening') ws.send(JSON.stringify({ id: ++nextId, method: 'Page.handleJavaScriptDialog', params: { accept: true } }));
  if (pending.has(m.id)) { pending.get(m.id)(m); pending.delete(m.id); }
};
await new Promise((r, j) => { ws.onopen = r; ws.onerror = j; });
const send = (method, params = {}) => Promise.race([
  new Promise((r) => { const i = ++nextId; pending.set(i, r); ws.send(JSON.stringify({ id: i, method, params })); }),
  sleep(15000).then(() => ({ error: { message: `${method} timed out` } })),
]);
const evaluate = async (expression) => {
  const r = await send('Runtime.evaluate', { expression, awaitPromise: true, returnByValue: true });
  if (r.error || r.result?.exceptionDetails) throw new Error(r.error?.message ?? r.result.exceptionDetails.exception?.description ?? r.result.exceptionDetails.text);
  return r.result.result.value;
};

await send('Page.enable');
await send('Emulation.setDeviceMetricsOverride', { width, height, deviceScaleFactor: 1, mobile: false });

// Runs in the page. Returns findings for the current screen.
const MEASURE = `(() => {
  const visible = (e) => { const b = e.getBoundingClientRect(); const s = getComputedStyle(e);
    return b.width > 0 && b.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const label = (e) => (e.getAttribute('aria-label') || e.innerText || e.placeholder || e.value || e.tagName).trim().replace(/\\s+/g, ' ').slice(0, 40);
  const findings = [];
  // A canvas zoomed with a CSS scale, or a layer (fixed, absolute, sticky), stacks on purpose: a side
  // panel over canvas nodes is not a defect. Controls are compared only inside the same layer.
  const scaled = (e) => { const m = getComputedStyle(e).transform.match(/^matrix\\(([^,]+),/); return m && Math.abs(Number(m[1]) - 1) > 0.01; };
  const layer = (e) => { for (let p = e; p && p !== document.body; p = p.parentElement) {
    const s = getComputedStyle(p); if (['fixed', 'absolute', 'sticky'].includes(s.position) || scaled(p)) return p; } return document.body; };
  const inCanvas = (e) => { for (let p = e.parentElement; p && p !== document.body; p = p.parentElement) {
    if (scaled(p) || p.tagName.toLowerCase() === 'svg') return true; } return false; };
  // Hidden on purpose: opacity 0, or the visually-hidden (sr-only) pattern of a 1 px clipping box.
  const hidden = (e) => { if (Number(getComputedStyle(e).opacity) === 0) return true;
    for (let p = e.parentElement, i = 0; p && i < 3; p = p.parentElement, i++) { const b = p.getBoundingClientRect();
      if ((b.width <= 1 || b.height <= 1) && getComputedStyle(p).overflow !== 'visible') return true; } return false; };
  for (const e of document.querySelectorAll('*')) {
    const s = getComputedStyle(e);
    if (!['auto', 'scroll'].includes(s.overflowX) || e.closest('[data-allow-scroll],table,pre,code,[role=tablist]')) continue;
    if (e.scrollWidth > e.clientWidth + 1 && visible(e))
      findings.push({ kind: 'h-scroll', where: label(e), detail: e.scrollWidth + ' > ' + e.clientWidth + ' px' });
  }
  const controls = [...document.querySelectorAll('input,select,textarea,button,a[href],[role=combobox],[role=button]')]
    .filter((e) => visible(e) && !hidden(e) && !e.closest('[aria-hidden=true],[data-allow-overlap]'));
  const boxes = controls.map((e) => [e, e.getBoundingClientRect()]);
  for (let i = 0; i < boxes.length; i++) for (let j = i + 1; j < boxes.length; j++) {
    const [x, a] = boxes[i], [y, b] = boxes[j];
    if (x.contains(y) || y.contains(x) || layer(x) !== layer(y) || inCanvas(x) || inCanvas(y)) continue;
    if (a.left < b.right - 2 && b.left < a.right - 2 && a.top < b.bottom - 2 && b.top < a.bottom - 2)
      findings.push({ kind: 'overlap', where: label(x) + ' / ' + label(y), detail: Math.round(Math.min(a.right, b.right) - Math.max(a.left, b.left)) + ' px' });
  }
  for (const [e, b] of boxes) {
    if (inCanvas(e)) continue;
    let p = e.parentElement;
    while (p && p !== document.body) { const s = getComputedStyle(p);
      if (['hidden', 'auto', 'scroll', 'clip'].includes(s.overflowX) || p.matches('[role=dialog],aside,dialog')) break;
      p = p.parentElement; }
    if (!p || p === document.body) continue;
    const pb = p.getBoundingClientRect();
    if (b.right > pb.right + 1 || b.left < pb.left - 1)
      findings.push({ kind: 'past-edge', where: label(e), detail: Math.round(Math.max(b.right - pb.right, pb.left - b.left)) + ' px outside ' + (p.getAttribute('role') || p.tagName.toLowerCase()) });
  }
  if (!document.body) return [{ kind: 'not-loaded', where: location.pathname, detail: 'page navigated away during the measure' }];
  const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
  for (let n = walker.nextNode(); n; n = walker.nextNode()) {
    const t = n.textContent.trim();
    if (!t || !n.parentElement || !visible(n.parentElement) || n.parentElement.closest('code,pre,script,style,[data-allow-raw]')) continue;
    if (/^[a-z][a-zA-Z0-9_]*(\\.[a-zA-Z0-9_]+){2,}$/.test(t) || /\\b(undefined|NaN|\\[object Object\\])\\b/.test(t) || /\\{\\{.*\\}\\}/.test(t))
      findings.push({ kind: 'raw-text', where: t.slice(0, 60), detail: 'i18n key, template or undefined on screen' });
  }
  return findings;
})()`;

const report = [];
for (const route of routes) {
  send('Page.navigate', { url: args.base + route.path });
  await sleep(Number(route.waitMs ?? 2500));
  // A loaded box under load can need longer than waitMs: wait up to 15 s for a body with text.
  // An error page (HTTP >= 400, a stale dev server on the port) is a finding, never "ok".
  let load = null;
  for (let i = 0; i < 30; i++) {
    load = await evaluate(`(() => ({ ready: document.readyState === 'complete' && !!document.body && document.body.innerText.trim().length > 0,
      status: performance.getEntriesByType('navigation')[0]?.responseStatus ?? 0 }))()`).catch(() => null);
    if (load?.ready) break;
    await sleep(500);
  }
  if (!load?.ready || load.status >= 400) {
    const detail = load?.status >= 400 ? `HTTP ${load.status}` : 'no body with text after 15 s';
    report.push({ name: route.name ?? route.path, path: route.path, findings: [{ kind: 'not-loaded', where: route.path, detail }] });
    console.log(`FAIL ${route.name ?? route.path} (1)\n     not-loaded: ${route.path} — ${detail}`);
    continue;
  }
  const missing = [];
  for (const text of route.open ?? []) {
    const point = await evaluate(`(() => { const t = ${JSON.stringify(text)};
      const hits = [...document.querySelectorAll('button,a,[role=tab],[role=option],[role=menuitem],li,td,div,span,label')]
        .filter((e) => { const b = e.getBoundingClientRect(); return b.width > 0 && (e.innerText || e.getAttribute('aria-label') || '').trim() === t; })
        .sort((a, b) => a.innerText.length - b.innerText.length);
      if (!hits.length) return null; hits[0].scrollIntoView({ block: 'center' });
      const b = hits[0].getBoundingClientRect(); return { x: b.x + b.width / 2, y: b.y + b.height / 2 }; })()`);
    if (!point) { missing.push(text); continue; }
    for (const type of ['mouseMoved', 'mousePressed', 'mouseReleased'])
      await send('Input.dispatchMouseEvent', { type, x: point.x, y: point.y, button: 'left', clickCount: 1 });
    await sleep(900);
  }
  const findings = await evaluate(MEASURE);
  for (const text of missing) findings.push({ kind: 'not-opened', where: text, detail: 'no visible element with this text' });
  report.push({ name: route.name ?? route.path, path: route.path, findings });
  console.log(`${findings.length ? 'FAIL' : 'ok  '} ${route.name ?? route.path}${findings.length ? ` (${findings.length})` : ''}`);
  for (const f of findings.slice(0, 8)) console.log(`     ${f.kind}: ${f.where} — ${f.detail}`);
}
ws.close();
if (args.out) writeFileSync(args.out, JSON.stringify(report, null, 2));
process.exit(report.some((r) => r.findings.length) ? 1 : 0);
