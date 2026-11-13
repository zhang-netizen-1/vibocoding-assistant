/* Layered UI audit (headless). Serves ../dist itself; covers the site chrome and the
   demos (shadow roots) on every page.
   Measured layers:
   - icon: every inline icon+text pair (svg/img icons, icon glyphs such as → ▶ ✓ ⌘ ⌄ ▼,
     and ::before/::after glyphs) — the icon's INK centre must match the adjacent text's
     ink centre (CJK runs) or text box centre (Latin-only) within 1px. Ink is read from
     a real screenshot, so glyphs that sit on the baseline are caught.
   - type: font-size / line-height / weight values outside the token set (shell and demo
     token sets are separate); color values outside the palette.
   - rows: siblings of the same kind laid out in one row (same top) with unequal heights.
   - filled: a filled (saturated) button carrying a grey outline.
  - inset: a gallery thumbnail holding one content card must show the same gray inset on all 4 sides (≤1px).
  - gap: masonry galleries (CSS columns) keep column gap = row gap between cards (≤1px).
   - states: hover / focus / open screenshots of the nav triggers and primary buttons.
   Usage: node tests/ui_audit_headless.cjs [routeFilter] [--widths=1440,390] [--inject=CSS]
   (--inject plants a defect to prove a rule fires, e.g. --inject='.nav-caret{top:3px}')
   Writes output/ui-audit/report.json and output/ui-audit/states/*.png; exits 1 on any
   icon / rows / type / color finding. */
const fs = require('node:fs'), path = require('node:path');
const {chromium} = require('playwright');
const ROOT = path.resolve(__dirname, '..'), dist = path.join(ROOT, 'dist'), outDir = path.join(ROOT, 'output/ui-audit');
const prefix = '/vibocoding-assistant/', origin = 'http://127.0.0.1:4178';
const types = {'.html':'text/html','.css':'text/css','.js':'text/javascript','.json':'application/json','.svg':'image/svg+xml','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg','.woff2':'font/woff2'};
const args = process.argv.slice(2), filter = args.find(a => !a.startsWith('--')) || '';
const inject = (args.find(a => a.startsWith('--inject=')) || '--inject=').slice(9); // self-test: extra CSS to plant a defect
const widths = (args.find(a => a.startsWith('--widths=')) || '--widths=1440,390').slice(9).split(',').map(Number);
const routes = [];
(function walk(d){ for (const n of fs.readdirSync(d)) { const p = path.join(d,n); if (fs.statSync(p).isDirectory()) { if (!['assets','demo-assets'].includes(n)) walk(p); }
  else if (n === 'index.html') { const html = fs.readFileSync(p,'utf8'); if (/http-equiv="refresh"/i.test(html)) continue;
    const r = path.relative(dist, d).split(path.sep).join('/'); routes.push(r ? r + '/' : ''); } } })(dist);
const selected = routes.filter(r => r.includes(filter)).sort();

// Token sets from docs/design-system.md (shell + demo type scales; 26px = hero <=760px;
// demo 15/22/24 = container-width overrides) and the palettes in tokens.css / demo-spec.css.
const read = f => fs.readFileSync(path.join(ROOT, 'site-src/redesign', f), 'utf8');
const hexes = text => [...new Set([...text.matchAll(/#[0-9a-fA-F]{6}\b/g)].map(m => m[0].toUpperCase()))];
const TOKENS = {
  shell: {sizes:[12,13,14,16,18,22,26,28,36], ratios:[1.3,1.5,1.7], weights:[400,500,600,650], colors:hexes(read('tokens.css').split('.demo-scope')[0])},
  demo: {sizes:[12,13,14,15,16,20,22,24,28], ratios:[1.2,1.35,1.4,1.5,1.6], weights:[400,500,600,650], colors:hexes(read('demo-spec.css')).concat(hexes(read('tokens.css').split('.demo-scope')[1]||''))},
};

function collect(tokens) {
  // Specimens whose own typography/colour IS the content: the six visual styles keep
  // their own style by rule, and the type-scale entry shows the scale itself.
  const SPECIMENS = ['brutalist','editorial','glass','minimal','neumorphic','organic','typography'];
  const ICON = /[→←↑↓↗↘▶▸►◀▼▾▲▴⌄⌃✓✔✕×⌘⏎↵›‹☰★☆⇧⌥↺↻]/;
  const ICONS_ONLY = /^[\s→←↑↓↗↘▶▸►◀▼▾▲▴⌄⌃✓✔✕×⌘⏎↵›‹☰★☆⇧⌥↺↻]+$/;
  const CJK = /[\u3400-\u9fff]/;
  const roots = [document];
  const addRoots = node => node.querySelectorAll('*').forEach(el => { if (el.shadowRoot) { roots.push(el.shadowRoot); addRoots(el.shadowRoot); } });
  addRoots(document);
  const all = roots.flatMap(r => [...r.querySelectorAll('*')]);
  const visible = el => { const r = el.getBoundingClientRect(); if (r.width <= 1.5 || r.height <= 1.5) return false;
    for (let n = el; n && n.nodeType === 1; n = n.parentElement || n.getRootNode().host) { const s = getComputedStyle(n); if (s.display === 'none' || s.visibility === 'hidden' || +s.opacity === 0) return false; if (n.matches('details:not([open]) > :not(summary)')) return false; }
    return true; };
  const label = el => { const host = el.getRootNode().host; return (host ? `[${host.dataset.demoSlug || 'demo'}] ` : '') + el.tagName.toLowerCase() + (typeof el.className === 'string' && el.className.trim() ? '.' + el.className.trim().split(/\s+/).slice(0,2).join('.') : ''); };
  const box = r => ({x:r.left + scrollX, y:r.top + scrollY, w:(r.width ?? r.right - r.left), h:(r.height ?? r.bottom - r.top)});
  const deepAt = (x, y) => { let el = document.elementFromPoint(x, y); while (el && el.shadowRoot) { const inner = el.shadowRoot.elementFromPoint(x, y); if (!inner || inner === el) break; el = inner; } return el; };
  const contains = (a, b) => { for (let n = b; n; n = n.parentElement || (n.getRootNode() && n.getRootNode().host)) if (n === a) return true; return false; };
  const rangeRect = (node, from, to) => { const r = document.createRange(); r.setStart(node, from); r.setEnd(node, to); const rs = [...r.getClientRects()].filter(q => q.width > 0); if (!rs.length) return null;
    return rs.reduce((a, q) => ({left:Math.min(a.left,q.left), right:Math.max(a.right,q.right), top:Math.min(a.top,q.top), bottom:Math.max(a.bottom,q.bottom), lines:a.lines + (Math.abs(q.top - a.top) > 2 ? 1 : 0)}), {left:1e9,right:-1e9,top:1e9,bottom:-1e9,lines:1}); };
  const isDemo = el => !!el.getRootNode().host;
  const pairs = [], type = [], rows = [], filled = [], inset = [], gap = [];
  // Text parts of an element: CJK runs (ink mode) or whole non-icon text (box mode).
  function textPart(el, skip, line) {
    const parts = [];
    const walker = document.createTreeWalker(el, NodeFilter.SHOW_TEXT);
    for (let t = walker.nextNode(); t; t = walker.nextNode()) {
      if (skip && skip.contains(t)) continue;
      const p = t.parentElement; if (!p || !visible(p) || p.closest('svg')) continue;
      const s = t.textContent; let i = 0;
      while (i < s.length) { const ch = s[i]; if (ICON.test(ch) || /\s/.test(ch)) { i++; continue; }
        let j = i; while (j < s.length && !ICON.test(s[j]) && !/\s/.test(s[j]) && CJK.test(s[j]) === CJK.test(ch)) j++;
        const rr = rangeRect(t, i, j); if (rr && (!line || ((rr.top + rr.bottom) / 2 > line.top && (rr.top + rr.bottom) / 2 < line.bottom))) parts.push({...rr, cjk:CJK.test(ch)}); i = j; }
    }
    if (!parts.length) return null;
    const cjk = parts.filter(p => p.cjk), use = cjk.length ? cjk : parts;
    const top = Math.min(...use.map(p => p.top)), bottom = Math.max(...use.map(p => p.bottom));
    if (bottom - top > Math.max(...use.map(p => p.bottom - p.top)) * 1.4) return null; // wraps over lines
    return {left:Math.min(...use.map(p => p.left)), right:Math.max(...use.map(p => p.right)), top, bottom, mode:cjk.length ? 'ink' : 'box'};
  }
  for (const el of all) {
    if (!(el instanceof HTMLElement) || !visible(el) || el.closest('[data-geo-ignore],[data-ui-audit-ignore]')) continue;
    const r = el.getBoundingClientRect(), small = r.height <= 120; // icon pairs live in label-sized boxes
    // a) child icon element next to text
    for (const icon of (small ? el.children : [])) {
      const tag = icon.tagName.toLowerCase(), ir = icon.getBoundingClientRect();
      const isIcon = (tag === 'svg' || tag === 'img' || (icon.textContent.trim() && ICONS_ONLY.test(icon.textContent)) || /(^|[-_ ])(icon|caret|chevron|arrow)([-_ ]|$)/i.test(icon.className && icon.className.baseVal !== undefined ? icon.className.baseVal : icon.className || ''))
        && ir.width > 0 && ir.width <= 28 && ir.height <= 28 && visible(icon);
      if (!isIcon) continue;
      const text = textPart(el, icon, ir); if (!text || text.top > ir.bottom || text.bottom < ir.top) continue;
      pairs.push({kind:'element', el:label(el), icon:label(icon), iconBox:box(ir), textBox:box(text), mode:text.mode, demo:isDemo(el), probe:[ir.left + ir.width/2, ir.top + ir.height/2]});
    }
    // b) icon glyphs inside the element's own text nodes
    for (const t of (small ? el.childNodes : [])) {
      // Only labels of controls/chips: a glyph mentioned in prose ("带 × 的小标签") is not an icon.
      if (t.nodeType !== 3 || !ICON.test(t.textContent) || ICONS_ONLY.test(el.textContent) || el.textContent.trim().length > 24 || !el.closest('button,a,summary,label,kbd,[role=button],[role=tab],[role=option],[role=menuitem],.chip,.btn')) continue;
      const s = t.textContent;
      for (let i = 0; i < s.length; i++) { if (!ICON.test(s[i]) || (s[i] === '×' && /[\w\d]/.test((s[i-1] || '') + (s[i+1] || '')))) continue;
        const ir = rangeRect(t, i, i + 1); if (!ir) continue;
        const text = textPart(el, null, ir); if (!text || text.top > ir.bottom || text.bottom < ir.top) continue;
        pairs.push({kind:'glyph', glyph:s[i], el:label(el), iconBox:box(ir), textBox:box(text), mode:text.mode, demo:isDemo(el), probe:[(ir.left+ir.right)/2, (ir.top+ir.bottom)/2]}); }
    }
    // c) pseudo-element glyphs
    for (const pseudo of (small ? ['::before','::after'] : [])) {
      const ps = getComputedStyle(el, pseudo), content = ps.content;
      if (!content || content === 'none' || content === 'normal' || content === '""' || ps.display === 'none') continue;
      if (!/^"[^"]{1,2}"$/.test(content)) continue;
      const text = textPart(el, null); if (!text) continue;
      const side = pseudo === '::after' ? {left:text.right, right:r.right - parseFloat(getComputedStyle(el).paddingRight)} : {left:r.left + parseFloat(getComputedStyle(el).paddingLeft), right:text.left};
      if (side.right - side.left < 3) continue;
      pairs.push({kind:'pseudo', glyph:content, el:label(el) + pseudo, iconBox:box({left:side.left, width:side.right - side.left, top:r.top, height:r.height}), textBox:box(text), mode:text.mode, demo:isDemo(el), probe:[(side.left+side.right)/2, r.top + r.height/2]});
    }
    // type & color for elements that own visible text
    const own = [...el.childNodes].some(n => n.nodeType === 3 && n.textContent.trim());
    const host = el.getRootNode().host, slug = host && host.dataset.demoSlug;
    // Rolling digit cells (odometer) size their line box to the cell height by design.
    const specimen = SPECIMENS.includes(slug) || el.closest('.ds-type-sample,[data-ui-audit-specimen],.extra-digits');
    const iconText = /^[\s\p{Extended_Pictographic}\u2190-\u21ff\u2300-\u23ff\u25a0-\u27bf\u00d7\u2039\u203a\uff0b+]+$/u.test(el.textContent);
    if (own && !specimen && !iconText && !el.closest('svg,pre,code,kbd,.prompt-text')) {
      const s = getComputedStyle(el), set = tokens[isDemo(el) ? 'demo' : 'shell'];
      // The design-system page documents both palettes, so either is allowed there.
      const palette = el.closest('.ds-page') ? tokens.shell.colors.concat(tokens.demo.colors) : set.colors;
      const fs = parseFloat(s.fontSize), lh = s.lineHeight === 'normal' ? null : parseFloat(s.lineHeight), fw = +s.fontWeight;
      const okRatio = lh === null || set.ratios.some(q => Math.abs(lh - fs * q) <= 0.75) || r.height <= lh + 1 && el.matches('button,a,.chip,[role=tab],label,input');
      const rgb = s.color.match(/[\d.]+/g).map(Number), hex = '#' + rgb.slice(0,3).map(v => Math.round(v).toString(16).padStart(2,'0')).join('').toUpperCase();
      const alpha = rgb.length > 3 ? rgb[3] : 1;
      const issues = [];
      if (!set.sizes.includes(Math.round(fs*100)/100)) issues.push(`font-size ${fs}px`);
      if (!okRatio) issues.push(`line-height ${lh}px (${(lh/fs).toFixed(2)})`);
      if (!set.weights.includes(fw)) issues.push(`font-weight ${fw}`);
      if (alpha === 1 && !palette.includes(hex)) issues.push(`color ${hex}`);
      if (issues.length) type.push({el:label(el), text:el.textContent.trim().slice(0,24), demo:isDemo(el), issues});
    }
    // rows of same-kind siblings with unequal heights
    // Filled controls (saturated fill) must not carry a grey outline: border equals fill or is transparent.
    if (el.matches('button,[role=button],a.btn,.btn') ) {
      const bs = getComputedStyle(el), rgb = x => (x.match(/[\d.]+/g) || []).map(Number);
      const bg = rgb(bs.backgroundColor), bc = rgb(bs.borderTopColor), bw = parseFloat(bs.borderTopWidth);
      const sat = c => c.length >= 3 && (c[3] ?? 1) > .9 && Math.max(c[0],c[1],c[2]) - Math.min(c[0],c[1],c[2]) > 60;
      if (bw > 0 && sat(bg) && (bc[3] ?? 1) > .5 && !sat(bc) && Math.max(bc[0],bc[1],bc[2]) - Math.min(bc[0],bc[1],bc[2]) < 40 && Math.max(bc[0],bc[1],bc[2]) < 200)
        filled.push({el:label(el), text:el.textContent.trim().slice(0, 16), bg:bs.backgroundColor, border:bs.borderTopColor, demo:isDemo(el)});
    }
    // Boxed controls (border or fill) sharing a row must be equally tall; cards likewise.
    const boxed = k => { const ks = getComputedStyle(k); return parseFloat(ks.borderTopWidth) > 0 || !/rgba\(0, 0, 0, 0\)|transparent/.test(ks.backgroundColor); };
    const families = {control:'button,a,input,select,.chip,.btn,[role=tab],[role=option]', card:'article,.card,.gallery-card,.simple-card,li'};
    for (const [family, sel] of Object.entries(families)) {
      if (family === 'card' && el.matches('.gallery')) continue; // masonry: card height follows content
      const kids = [...el.children].filter(k => visible(k) && k.matches(sel) && boxed(k));
      if (kids.length < 2) continue;
      const byTop = new Map();
      // Controls compare across kinds; cards only with cards of the same kind (a demo grid may mix card types on purpose).
      for (const k of kids) { const kr = k.getBoundingClientRect(), key = Math.round(kr.top) + (family === 'card' ? '|' + (typeof k.className === 'string' ? k.className.split(/\s+/)[0] : '') : ''); if (!byTop.has(key)) byTop.set(key, []); byTop.get(key).push({h:kr.height, k}); }
      for (const [, list] of byTop) { if (list.length < 2) continue; const hs = list.map(x => x.h);
        if (Math.max(...hs) - Math.min(...hs) > 1) rows.push({el:label(el), group:family + ':' + list.map(x => label(x.k)).slice(0, 4).join(' / '), heights:hs.map(h => +h.toFixed(1)), demo:isDemo(el)}); }
    }
  }
  // Gallery thumbnails: a single content card sits with an equal inset on all four sides.
  for (const card of document.querySelectorAll('.gallery-card')) {
    if (!visible(card)) continue;
    const host = card.querySelector('.demo-scope'), root = host && host.shadowRoot && host.shadowRoot.querySelector('.demo-root'); if (!root) continue;
    const wrap = [...root.children].find(e => getComputedStyle(e).display !== 'none'); if (!wrap) continue;
    const kids = [...wrap.children].filter(e => { const st = getComputedStyle(e); return st.display !== 'none' && !/absolute|fixed/.test(st.position); });
    if (kids.length !== 1) continue;
    const k = kids[0], ks = getComputedStyle(k);
    if (/rgba\(0, 0, 0, 0\)|transparent/.test(ks.backgroundColor) && !(parseFloat(ks.borderTopWidth) > 0) && ks.boxShadow === 'none') continue;
    const sr = root.getBoundingClientRect(), kr = k.getBoundingClientRect(), d = [kr.left - sr.left, kr.top - sr.top, sr.right - kr.right, sr.bottom - kr.bottom];
    if (Math.max(...d) - Math.min(...d) > 1) inset.push({el:`[${host.dataset.demoSlug}] ${label(k)}`, inset:d.map(v => +v.toFixed(1)), demo:true});
  }
  // Masonry galleries: every horizontal and vertical gap between neighbouring cards is the same.
  for (const g of document.querySelectorAll('.gallery')) {
    if (!visible(g)) continue;
    const rs = [...g.children].filter(visible).map(c => c.getBoundingClientRect()); if (rs.length < 2) continue;
    const cols = new Map(); for (const r of rs) { const key = Math.round(r.left); if (!cols.has(key)) cols.set(key, []); cols.get(key).push(r); }
    const lefts = [...cols.keys()].sort((a, b) => a - b), gaps = [];
    for (let i = 1; i < lefts.length; i++) gaps.push(lefts[i] - cols.get(lefts[i - 1])[0].right);
    for (const list of cols.values()) { list.sort((a, b) => a.top - b.top); for (let j = 1; j < list.length; j++) gaps.push(list[j].top - list[j - 1].bottom); }
    if (gaps.length && Math.max(...gaps) - Math.min(...gaps) > 1) gap.push({el:label(g), gaps:[...new Set(gaps.map(v => +v.toFixed(1)))], demo:false});
  }
  // occlusion: drop pairs whose icon is covered by something else (fixed bars etc.)
  const kept = pairs.filter(p => { const at = deepAt(p.probe[0], p.probe[1]); return !!at && !(at.closest && at.closest('.bottom-bar')); });
  return {pairs:kept, type, rows, filled, inset, gap};
}

// Ink measurement in the page: decode the screenshot and find ink rows inside boxes.
async function measureInk(page, png, pairs) {
  return page.evaluate(async ({b64, pairs, dpr}) => {
    const img = new Image(); img.src = 'data:image/png;base64,' + b64; await img.decode();
    const c = document.createElement('canvas'); c.width = img.width; c.height = img.height; const g = c.getContext('2d', {willReadFrequently:true}); g.drawImage(img, 0, 0);
    const inkCentre = bx => {
      const x0 = Math.max(0, Math.floor(bx.x * dpr)), y0 = Math.max(0, Math.floor(bx.y * dpr)), w = Math.max(1, Math.ceil(bx.w * dpr)), h = Math.max(1, Math.ceil(bx.h * dpr));
      if (x0 + w > c.width || y0 + h > c.height) return null;
      const d = g.getImageData(x0, y0, w, h).data, counts = new Map();
      for (let i = 0; i < d.length; i += 4) { const k = d[i] >> 3 << 10 | d[i+1] >> 3 << 5 | d[i+2] >> 3; counts.set(k, (counts.get(k) || 0) + 1); }
      const bgKey = [...counts.entries()].sort((a, b) => b[1] - a[1])[0][0];
      const bg = [(bgKey >> 10 & 31) << 3, (bgKey >> 5 & 31) << 3, (bgKey & 31) << 3];
      let top = -1, bottom = -1, weight = 0, sum = 0;
      for (let y = 0; y < h; y++) { let row = 0; for (let x = 0; x < w; x++) { const i = (y * w + x) * 4; const diff = Math.abs(d[i]-bg[0]) + Math.abs(d[i+1]-bg[1]) + Math.abs(d[i+2]-bg[2]); if (diff > 90) row++; }
        if (row) { if (top < 0) top = y; bottom = y; weight += row; sum += row * y; } }
      if (top < 0) return null;
      return {centre:(y0 + (top + bottom + 1) / 2) / dpr, top:(y0 + top) / dpr, bottom:(y0 + bottom + 1) / dpr};
    };
    return pairs.map(p => { const icon = inkCentre(p.iconBox); const text = p.mode === 'ink' ? inkCentre(p.textBox) : {centre:p.textBox.y + p.textBox.h / 2};
      return {...p, iconInk:icon, textInk:text, delta:icon && text ? +(icon.centre - text.centre).toFixed(2) : null}; });
  }, {b64:png.toString('base64'), pairs, dpr:1});
}

async function stateShots(browser) {
  const dir = path.join(outDir, 'states'); fs.mkdirSync(dir, {recursive:true});
  const shots = [];
  for (const width of [1440, 1024]) {
    const ctx = await browser.newContext({viewport:{width, height:900}, deviceScaleFactor:2}); await serve(ctx); const page = await ctx.newPage();
    await page.goto(origin + prefix + 'components/cmdk/', {waitUntil:'load'}); await page.waitForTimeout(300);
    const nav = await page.locator('.nav-inner').boundingBox(); const clip = {x:nav.x, y:nav.y, width:Math.min(nav.width, width), height:nav.height};
    const trigger = page.locator('.nav-trigger').first();
    await page.screenshot({path:path.join(dir, `nav-${width}-default.png`), clip}); shots.push(`nav-${width}-default.png`);
    await trigger.hover(); await page.waitForTimeout(250); await page.screenshot({path:path.join(dir, `nav-${width}-hover.png`), clip}); shots.push(`nav-${width}-hover.png`);
    await trigger.click(); await page.waitForTimeout(350); await page.screenshot({path:path.join(dir, `nav-${width}-open.png`), clip:{...clip, height:Math.min(500, 900)}}); shots.push(`nav-${width}-open.png`);
    await page.keyboard.press('Escape'); await page.mouse.move(width - 10, 880); await page.waitForTimeout(200);
    await page.keyboard.press('Tab'); for (let i = 0; i < 6 && !(await page.evaluate(() => document.activeElement.matches('.nav-trigger'))); i++) await page.keyboard.press('Tab');
    await page.waitForTimeout(200); await page.screenshot({path:path.join(dir, `nav-${width}-focus.png`), clip}); shots.push(`nav-${width}-focus.png`);
    for (const [name, sel] of [['copy', '.prompt-head button'], ['search', '.nav-search']]) {
      const btn = page.locator(sel).first(); if (!(await btn.count()) || !(await btn.isVisible())) continue;
      const bb = await btn.boundingBox(); const c = {x:Math.max(0, bb.x - 12), y:Math.max(0, bb.y - 12), width:bb.width + 24, height:bb.height + 24};
      await page.mouse.move(width - 10, 880); await page.screenshot({path:path.join(dir, `${name}-${width}-default.png`), clip:c});
      await btn.hover(); await page.waitForTimeout(200); await page.screenshot({path:path.join(dir, `${name}-${width}-hover.png`), clip:c});
      await btn.focus(); await page.mouse.move(width - 10, 880); await page.waitForTimeout(150); await page.screenshot({path:path.join(dir, `${name}-${width}-focus.png`), clip:c});
      shots.push(`${name}-${width}-*.png`);
    }
    await ctx.close();
  }
  return shots;
}
async function serve(ctx) {
  await ctx.route('**/*', route => { const url = new URL(route.request().url()); if (url.origin !== origin) return route.abort();
    let file = path.join(dist, decodeURIComponent(url.pathname.slice(prefix.length)));
    if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
    if (!fs.existsSync(file)) return route.fulfill({status:404, body:''});
    return route.fulfill({status:200, contentType:types[path.extname(file)] || 'application/octet-stream', body:fs.readFileSync(file)}); });
}

(async () => {
  fs.mkdirSync(outDir, {recursive:true});
  const browser = await chromium.launch(), report = {started:new Date().toISOString(), widths, pages:selected.length, icon:[], type:[], rows:[], filled:[], inset:[], gap:[], pairsChecked:0, errors:[]};
  for (const width of widths) {
    const ctx = await browser.newContext({viewport:{width, height:900}, hasTouch:width < 500, isMobile:width < 500, reducedMotion:'reduce'}); await serve(ctx);
    let next = 0;
    await Promise.all(Array.from({length:4}, async () => { const page = await ctx.newPage();
      while (next < selected.length) { const route = selected[next++];
        try {
          await page.setViewportSize({width, height:900});
          await page.goto(origin + prefix + route, {waitUntil:'load'}); await page.waitForTimeout(200);
          await page.addStyleTag({content:'.skip{display:none!important}*{caret-color:transparent!important}' + inject});
          const h = Math.min(await page.evaluate(() => document.documentElement.scrollHeight), 7000);
          await page.setViewportSize({width, height:h}); await page.waitForTimeout(250);
          const found = await page.evaluate(collect, TOKENS);
          const png = await page.screenshot();
          const measured = await measureInk(page, png, found.pairs);
          report.pairsChecked += measured.length;
          for (const m of measured) if (m.delta !== null && Math.abs(m.delta) > 1) report.icon.push({width, route, el:m.el, icon:m.icon || m.glyph, kind:m.kind, mode:m.mode, delta:m.delta, demo:m.demo});
          for (const t of found.type) report.type.push({width, route, ...t});
          for (const r of found.rows) report.rows.push({width, route, ...r});
          for (const f of found.filled) report.filled.push({width, route, ...f});
          for (const f of found.inset) report.inset.push({width, route, ...f});
          for (const f of found.gap) report.gap.push({width, route, ...f});
        } catch (error) { report.errors.push({width, route, error:error.message.slice(0, 200)}); }
      }
      await page.close(); }));
    await ctx.close();
  }
  report.stateShots = await stateShots(browser);
  await browser.close();
  report.finished = new Date().toISOString();
  fs.writeFileSync(path.join(outDir, 'report.json'), JSON.stringify(report, null, 1));
  const uniq = list => new Set(list.map(x => `${x.el}|${x.icon || x.group || (x.issues || []).join(',')}`)).size;
  console.log(`页面 ${selected.length} × 宽 ${widths.join('/')}；图标文字对 ${report.pairsChecked} 组`);
  console.log(`icon 未居中 ${report.icon.length}（去重 ${uniq(report.icon)}）；type/color ${report.type.length}（去重 ${uniq(report.type)}）；rows 不等高 ${report.rows.length}（去重 ${uniq(report.rows)}）；filled 实心按钮灰描边 ${report.filled.length}（去重 ${uniq(report.filled)}）；错误 ${report.errors.length}；inset 缩略图内边距不等 ${report.inset.length}（去重 ${uniq(report.inset)}）；gap 瀑布流间距不等 ${report.gap.length}（去重 ${uniq(report.gap)}）`);
  process.exit(report.icon.length || report.type.length || report.rows.length || report.filled.length || report.inset.length || report.gap.length || report.errors.length ? 1 : 0);
})().catch(error => { console.error(error); process.exit(2); });
