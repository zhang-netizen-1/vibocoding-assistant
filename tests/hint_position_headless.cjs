/* Hint pill position (headless): on every entry page (192) at 1440 and 390, each
   visible .ds-hint inside an interactive demo sits at the site-wide position:
   12px inset + 1px stage border = 13px from the demo root's left and bottom edges.
   Serves ../dist itself. Usage: node tests/hint_position_headless.cjs */
const fs = require('node:fs'), path = require('node:path'), assert = require('node:assert/strict');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '../dist'), prefix = '/vibocoding-assistant/', origin = 'http://127.0.0.1:4177';
const types = {'.html':'text/html','.css':'text/css','.js':'text/javascript','.json':'application/json','.svg':'image/svg+xml','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg'};
const routes = [];
(function walk(dir){ for (const name of fs.readdirSync(dir)) { const p = path.join(dir,name);
  if (fs.statSync(p).isDirectory()) walk(p);
  else if (name === 'index.html' && /class="demo-scope"[^>]*data-interactive/.test(fs.readFileSync(p,'utf8')))
    routes.push(path.relative(root, path.dirname(p)).split(path.sep).join('/') + '/'); } })(root);
function measure() {
  const out = [];
  for (const scope of document.querySelectorAll('.demo-scope[data-interactive]')) {
    const demo = scope.shadowRoot && scope.shadowRoot.querySelector('.demo-root'); if (!demo) continue;
    const r = demo.getBoundingClientRect();
    for (const hint of demo.querySelectorAll('.ds-hint')) {
      const h = hint.getBoundingClientRect(), s = getComputedStyle(hint);
      if (s.display === 'none' || s.visibility === 'hidden' || h.width < 2) continue;
      out.push({left:+(h.left - r.left).toFixed(2), bottom:+(r.bottom - h.bottom).toFixed(2), position:s.position});
    }
  }
  return out;
}
(async () => {
  assert.equal(routes.length, Number(process.env.EXPECTED_ENTRIES || 192), 'entry pages with an interactive demo');
  const browser = await chromium.launch(), bad = [], counts = {};
  for (const width of [1440, 390]) {
    const context = await browser.newContext({viewport:{width, height:1000}, hasTouch:width === 390, isMobile:width === 390});
    await context.route('**/*', route => { const url = new URL(route.request().url());
      if (url.origin !== origin) return route.abort();
      let file = path.join(root, decodeURIComponent(url.pathname.slice(prefix.length)));
      if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
      if (!fs.existsSync(file)) return route.fulfill({status:404, body:''});
      return route.fulfill({status:200, contentType:types[path.extname(file)] || 'application/octet-stream', body:fs.readFileSync(file)}); });
    let next = 0, hints = 0, pagesWithHint = 0;
    await Promise.all(Array.from({length:6}, async () => { const page = await context.newPage();
      while (next < routes.length) { const route = routes[next++];
        await page.goto(origin + prefix + route, {waitUntil:'load'}); await page.waitForTimeout(150);
        const found = await page.evaluate(measure); hints += found.length; if (found.length) pagesWithHint++;
        for (const m of found) if (m.position !== 'absolute' || Math.abs(m.left - 13) > 1.1 || Math.abs(m.bottom - 13) > 1.1) bad.push({width, route, ...m}); }
      await page.close(); }));
    counts[width] = {pages:routes.length, pagesWithHint, hints};
    await context.close();
  }
  await browser.close();
  console.log(JSON.stringify({counts, failures:bad.length, bad:bad.slice(0, 20)}, null, 1));
  assert.ok(counts[1440].hints >= 150, 'hint pills were actually measured');
  assert.deepEqual(bad, [], 'hint pill not at the site-wide 13px left/bottom position');
  console.log(`提示胶囊位置：${routes.length} 条 × 2 宽，${counts[1440].hints + counts[390].hints} 个胶囊全部在 13px 位置。`);
})().catch(error => { console.error(error); process.exit(1); });
