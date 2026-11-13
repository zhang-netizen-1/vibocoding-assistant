/* Nested-radius and spacing audit (headless only).
   Rule 1 (radius): a child box never has a larger corner radius than the box it
   sits in; when the child sits within the parent's corner zone (gap < parent
   radius) its radius must not exceed max(parentRadius - gap, 6px) (+1px slack).
   Pills/circles (radius >= half their short side) are shape-defined and skipped,
   but must keep gap >= parent radius from the parent's corner.
   Rule 2 (spacing): a button never touches or overlaps another visible box
   (bordered/filled element or media) that is not its ancestor, descendant or a
   member of the same deliberate control group; minimum gap 8px.
   Rule 2b (segmented): buttons in a control group may touch (gap < 8px) only when
   the group renders as one segmented control: the group itself draws a single
   outer outline (border, shadow or fill) with a rounded end radius; touching
   segments are not each fully bordered, carry no radius on the sides that touch
   (borderless inset fills excepted) and never double the divider (<= 1.5px).
   Groups that fail lose the exemption and are reported under "segmented".
   [data-geo-ignore] marks deliberate
   counter-examples.
   Usage: node tests/geometry_headless.cjs [routeFilter]   (serves ../dist) */
const fs = require('node:fs'), path = require('node:path');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '../dist'), prefix = '/vibocoding-assistant/', origin = 'http://127.0.0.1:4176';
const types = {'.html':'text/html','.css':'text/css','.js':'text/javascript','.json':'application/json','.svg':'image/svg+xml','.webp':'image/webp','.png':'image/png','.jpg':'image/jpeg'};
const filter = process.argv[2] || '';
const routes = [];
(function walk(dir){ for (const name of fs.readdirSync(dir)) { const p = path.join(dir,name); if (fs.statSync(p).isDirectory()) walk(p); else if (name === 'index.html') { const html = fs.readFileSync(p,'utf8'); if (html.includes('<body class="entry-active">')) routes.push(path.relative(root,path.dirname(p)) + '/'); } } })(root);
function audit() {
  const out = {radius:[], spacing:[], clip:[], indicator:[], narrow:[], segmented:[], cards:[]};
  const px = v => parseFloat(v) || 0;
  // Border radius in px; percentages resolve against the box (horizontal vs width, vertical vs height).
  const rp = (v, b) => { const [h, w = h] = String(v).trim().split(/\s+/); const f = (x, d) => x.endsWith("%") ? parseFloat(x) / 100 * d : (parseFloat(x) || 0); return Math.min(f(h, b.width), f(w, b.height)); };
  const visible = el => { if (el.closest('details:not([open])') && !el.closest('summary')) return false; const r = el.getBoundingClientRect(); if (r.width < 2 || r.height < 2) return false; for (let n = el; n; n = n.parentElement || n.getRootNode().host) { const s = getComputedStyle(n); if (s.display === 'none' || s.visibility === 'hidden' || Number(s.opacity) === 0) return false; } return true; };
  const isBox = el => { const s = getComputedStyle(el); if (el.matches('img,video,canvas,svg,iframe')) return true; const bg = s.backgroundColor !== 'rgba(0, 0, 0, 0)' && s.backgroundColor !== 'transparent' || s.backgroundImage !== 'none'; const bd = px(s.borderTopWidth) > 0 && s.borderTopStyle !== 'none' && !/rgba\(.*, 0\)$/.test(s.borderTopColor); return bg || bd || s.boxShadow !== 'none'; };
  const parentOf = el => el.parentElement || (el.getRootNode().host ?? null);
  const label = el => { const host = el.getRootNode().host; return (host ? '[' + (host.dataset.demoKey || 'shadow') + '] ' : '') + el.tagName.toLowerCase() + (el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/).slice(0,3).join('.') : ''); };
  // Visible part of a box after every overflow-clipping ancestor (scroll areas, clipped stages).
  const clipped = el => { let b = el.getBoundingClientRect(); b = {left:b.left, right:b.right, top:b.top, bottom:b.bottom};
    for (let n = parentOf(el); n && n.nodeType === 1; n = parentOf(n)) { const s = getComputedStyle(n); if (/(hidden|clip|auto|scroll)/.test(s.overflowX + s.overflowY)) { const c = n.getBoundingClientRect(); b = {left:Math.max(b.left,c.left), right:Math.min(b.right,c.right), top:Math.max(b.top,c.top), bottom:Math.min(b.bottom,c.bottom)}; if (b.right - b.left < 1 || b.bottom - b.top < 1) return null; } }
    return b; };
  const inside = (a, b) => { for (let n = b; n; n = n.parentElement || n.getRootNode().host) if (n === a) return true; return false; };
  const all = [];
  (function collect(rootNode){ for (const el of rootNode.querySelectorAll('*')) { all.push(el); if (el.shadowRoot) collect(el.shadowRoot); } })(document);
  const scopeOk = el => !el.closest('[data-geo-ignore]') && !el.getRootNode().host?.closest?.('[data-geo-ignore]') && !!(el.closest('.entry-main,.use-card,.entry-layout,.ds-page') || el.getRootNode().host?.closest?.('.entry-demo,.entry-main,.ds-page'));
  const bw = (s, side) => s['border' + side + 'Style'] !== 'none' && !/rgba\(.*, 0\)$/.test(s['border' + side + 'Color']) ? px(s['border' + side + 'Width']) : 0;
  const segCache = new Map();
  // Returns null when the group is a proper segmented control (or its members do not touch), else the reason.
  const segProblem = group => {
    if (segCache.has(group)) return segCache.get(group);
    const items = [...group.querySelectorAll('button,[role="tab"],[role="radio"],a')].filter(b => visible(b) && b.closest('[role="group"],[role="tablist"],[role="radiogroup"],.segmented,.seg,.split-button,.split-wrap,.split,.splitbtn,.btn-group,.pagination,.pager,.ds-seg') === group);
    let why = null;
    const touching = [];
    for (let i = 0; i < items.length; i++) for (let j = i + 1; j < items.length; j++) {
      const a = items[i].getBoundingClientRect(), b = items[j].getBoundingClientRect();
      const dx = Math.max(b.left - a.right, a.left - b.right), dy = Math.max(b.top - a.bottom, a.top - b.bottom);
      if (Math.max(dx, dy) < 8) touching.push([items[i], items[j], a, b]);
    }
    if (touching.length) {
      const gs = getComputedStyle(group), gr = group.getBoundingClientRect();
      const outline = isBox(group);
      const grad = Math.max(rp(gs.borderTopLeftRadius, gr), rp(gs.borderBottomRightRadius, gr));
      const endRad = items.some(b => { const t = getComputedStyle(b), r = b.getBoundingClientRect(); return Math.max(rp(t.borderTopLeftRadius, r), rp(t.borderBottomRightRadius, r)) > 0; });
      if (!outline) why = 'group has no single outer outline';
      else if (!(grad > 0 || endRad)) why = 'group ends are not rounded';
      else for (const [x, y, a, b] of touching) {
        const sx = getComputedStyle(x), sy = getComputedStyle(y);
        const full = t => ['Top','Right','Bottom','Left'].every(side => bw(t, side) > 0);
        if (full(sx) && full(sy)) { why = 'segments are separately bordered'; break; }
        const horiz = Math.abs(a.top - b.top) < 4;
        const [first, second, s1, s2, r1, r2] = (horiz ? a.left <= b.left : a.top <= b.top) ? [x, y, sx, sy, a, b] : [y, x, sy, sx, b, a];
        const divider = horiz ? bw(s1, 'Right') + bw(s2, 'Left') : bw(s1, 'Bottom') + bw(s2, 'Top');
        const overlapPx = horiz ? Math.max(0, r1.right - r2.left) : Math.max(0, r1.bottom - r2.top);
        if (divider - Math.min(overlapPx, divider / 2) > 1.5) { why = 'doubled divider'; break; }
        const inset = t => !['Top','Right','Bottom','Left'].some(side => bw(t, side) > 0);
        const innerA = horiz ? [s1.borderTopRightRadius, s1.borderBottomRightRadius] : [s1.borderBottomLeftRadius, s1.borderBottomRightRadius];
        const innerB = horiz ? [s2.borderTopLeftRadius, s2.borderBottomLeftRadius] : [s2.borderTopLeftRadius, s2.borderTopRightRadius];
        if ((!inset(s1) && innerA.some(v => rp(v, r1) > 0.5)) || (!inset(s2) && innerB.some(v => rp(v, r2) > 0.5))) { why = 'touching sides are rounded'; break; }
      }
      if (why) out.segmented.push({el:label(group), why, items:items.length});
    }
    segCache.set(group, why); return why;
  };
  for (const el of all) {
    if (!scopeOk(el) || !visible(el)) continue;
    const s = getComputedStyle(el), r = el.getBoundingClientRect();
    const rad = Math.max(rp(s.borderTopLeftRadius, r), rp(s.borderTopRightRadius, r), rp(s.borderBottomLeftRadius, r), rp(s.borderBottomRightRadius, r));
    // Leaf decorative shapes (blobs, dots) with no text are not containers.
    const leafShape = !el.matches('img,video,canvas,iframe,button,a,input') && !el.children.length && !el.textContent.trim();
    if (rad > 0 && isBox(el) && !leafShape) {
      let p = parentOf(el);
      while (p && p.nodeType === 1 && !(isBox(p) && Math.max(px(getComputedStyle(p).borderTopLeftRadius), px(getComputedStyle(p).borderBottomRightRadius)) > 0)) p = parentOf(p);
      if (p && p.nodeType === 1 && visible(p)) {
        const ps = getComputedStyle(p), pr = p.getBoundingClientRect();
        const prad = Math.max(rp(ps.borderTopLeftRadius, pr), rp(ps.borderTopRightRadius, pr), rp(ps.borderBottomLeftRadius, pr), rp(ps.borderBottomRightRadius, pr));
        const pill = rad >= Math.min(r.width, r.height) / 2 - 0.5;
        const ppill = prad >= Math.min(pr.width, pr.height) / 2 - 0.5;
        const gaps = {tl:Math.max(r.left-pr.left, r.top-pr.top), tr:Math.max(pr.right-r.right, r.top-pr.top), bl:Math.max(r.left-pr.left, pr.bottom-r.bottom), br:Math.max(pr.right-r.right, pr.bottom-r.bottom)};
        const radii = {tl:rp(s.borderTopLeftRadius, r), tr:rp(s.borderTopRightRadius, r), bl:rp(s.borderBottomLeftRadius, r), br:rp(s.borderBottomRightRadius, r)};
        if (!pill && !ppill) {
          if (rad > prad + 1 && r.width < pr.width + 1 && r.height < pr.height + 1) out.radius.push({el:label(el), parent:label(p), child:rad, outer:prad, rule:'inner>outer'});
          else for (const k of ['tl','tr','bl','br']) {
            const g = gaps[k]; if (g < -0.5 || g >= prad) continue;
            const allowed = Math.max(prad - g, Math.min(6, prad));
            if (radii[k] > allowed + 1) { out.radius.push({el:label(el), parent:label(p), corner:k, child:radii[k], outer:prad, gap:Math.round(g), allowed:Math.round(allowed), rule:'not-concentric'}); break; }
          }
        }
      }
    }
    if (el.matches('button,a.btn,[role="button"],.play-button') && isBox(el)) {
      let group = el.closest('[role="group"],[role="tablist"],[role="radiogroup"],.segmented,.seg,.split-button,.split-wrap,.split,.splitbtn,.btn-group,.pagination,.pager,.ds-seg');
      if (group && segProblem(group)) group = null;
      let card = parentOf(el); while (card && card.nodeType === 1 && !(isBox(card) && px(getComputedStyle(card).borderTopLeftRadius) > 0)) card = parentOf(card);
      if (!card || card.nodeType !== 1) continue;
      const within = all.filter(o => o !== el && inside(card, o) && !inside(o, el) && !inside(el, o) && !(group && inside(group, o)) && isBox(o) && visible(o) && getComputedStyle(o).position !== 'fixed');
      for (const o of within) {
        const q = clipped(o); if (!q) continue;
        if (o.closest('.ds-overlays,[aria-hidden="true"]') || el.closest('.ds-overlays')) continue;
        const dx = Math.max(q.left - r.right, r.left - q.right, 0), dy = Math.max(q.top - r.bottom, r.top - q.bottom, 0);
        const overlap = !(q.left >= r.right || q.right <= r.left || q.top >= r.bottom || q.bottom <= r.top);
        const gap = Math.max(dx, dy);
        if (overlap || gap < 8) {
          // contained decorations (o fully inside el's parent chain as a background) are ancestors-only; skip boxes that fully contain el
          if (q.left <= r.left && q.right >= r.right && q.top <= r.top && q.bottom >= r.bottom) continue;
          out.spacing.push({el:label(el), in:label(card), elText:(el.textContent||"").trim().slice(0,16), other:label(o), otherIn:label(parentOf(o)), rect:[r.left,r.top,r.width,r.height].map(Math.round), otherRect:[q.left,q.top,q.right-q.left,q.bottom-q.top].map(Math.round), gap:Math.round(gap*10)/10, overlap}); break;
        }
      }
    }
  }

  // Rule 3 (clip): visible text that is cut off by an overflow-clipping ancestor,
  // or that spills outside its own box. Scroll areas are not truncation.
  for (const el of all) {
    if (!scopeOk(el) || !visible(el) || el.matches('script,style,template,svg *,.sr,.sr-only,[aria-hidden="true"] *')) continue;
    for (const t of el.childNodes) {
      if (t.nodeType !== 3 || !t.textContent.trim()) continue;
      const range = document.createRange(); range.selectNodeContents(t); const tr = range.getBoundingClientRect(); if (tr.width < 1) continue;
      const box = el.getBoundingClientRect();
      if (tr.right > box.right + 2 || tr.left < box.left - 2) { const s = getComputedStyle(el); if (s.display !== 'inline') { out.narrow.push({el:label(el), text:t.textContent.trim().slice(0,20), box:Math.round(box.width), text_w:Math.round(tr.width)}); break; } }
      for (let n = parentOf(el); n && n.nodeType === 1; n = parentOf(n)) {
        const s = getComputedStyle(n); if (!/(hidden|clip)/.test(s.overflowX + s.overflowY)) continue; if (/(auto|scroll)/.test(s.overflowX + s.overflowY)) break;
        const c = n.getBoundingClientRect();
        if (tr.right > c.right + 1 || tr.left < c.left - 1 || tr.bottom > c.bottom + 1 || tr.top < c.top - 1) {
          const inter = Math.max(0, Math.min(tr.right,c.right) - Math.max(tr.left,c.left)) * Math.max(0, Math.min(tr.bottom,c.bottom) - Math.max(tr.top,c.top));
          if (inter > 0) out.clip.push({el:label(el), text:t.textContent.trim().slice(0,20), by:label(n)});
          break;
        }
        break;
      }
      break;
    }
  }
  // Rule 4 (indicator): a moving highlight must cover its selected target (<= 2px offset).
  for (const ind of all) {
    if (!scopeOk(ind) || !visible(ind) || !/(indicator|ink-bar|highlight-pill|tab-pill|seg-thumb|slider-thumb-bg)/.test(typeof ind.className === 'string' ? ind.className : '')) continue;
    const list = parentOf(ind); if (!list || list.nodeType !== 1) continue;
    const target = list.querySelector('[aria-selected="true"],[aria-pressed="true"],[aria-current="page"],[aria-current="true"],.active,.is-active');
    if (!target || target === ind) continue;
    const a = ind.getBoundingClientRect(), b = target.getBoundingClientRect();
    const s = getComputedStyle(ind);
    const underline = a.height <= 4;
    const dl = Math.abs(a.left - b.left), dr = Math.abs(a.right - b.right), dt = underline ? 0 : Math.abs(a.top - b.top), db = underline ? 0 : Math.abs(a.bottom - b.bottom);
    if (s.transitionDuration.split(',').some(v => parseFloat(v) > 0) && ind.getAnimations().length) continue;
    if (Math.max(dl,dr,dt,db) > 2) out.indicator.push({el:label(ind), target:label(target), offset:Math.round(Math.max(dl,dr,dt,db))});
  }
  // Rule 5 (cards): motion cards are >= 320px wide (or the full column), the caption sits on the card's
  // bottom edge and a visible play button is vertically centred on the caption (<= 4px).
  for (const c of document.querySelectorAll('.motion-grid .gallery-card')) {
    if (!visible(c)) continue;
    const cr = c.getBoundingClientRect(), grid = c.parentElement.getBoundingClientRect();
    const cap = c.querySelector('.gallery-caption'); if (!cap) continue; const kr = cap.getBoundingClientRect();
    const pb = c.querySelector('.play-button'); const br = pb && visible(pb) ? pb.getBoundingClientRect() : null;
    const issue = cr.width < 320 && cr.width < grid.width - 1 ? 'narrower than 320px' : cr.bottom - kr.bottom > 2 ? 'caption not on the bottom edge' : br && Math.abs((br.top + br.bottom) / 2 - (kr.top + kr.bottom) / 2) > 4 ? 'play button off the caption row' : null;
    if (issue) out.cards.push({el:label(c), title:(c.querySelector('.gallery-caption strong,.gallery-caption b,.gallery-caption h3')||cap).textContent.trim().slice(0,16), issue, w:Math.round(cr.width)});
  }
  return out;
}
(async () => {
  const browser = await chromium.launch({headless:true});
  const report = {radius:[], spacing:[], clip:[], indicator:[], narrow:[], segmented:[], cards:[], pages:0};
  try {
    for (const width of [1440,768,390]) {
      const context = await browser.newContext({viewport:{width,height:900},hasTouch:width===390,isMobile:width===390,reducedMotion:'reduce'});
      const page = await context.newPage();
      await page.route('**/*', route => { const url = new URL(route.request().url()); if (url.origin !== origin) return route.abort(); let file = path.resolve(root, decodeURIComponent(url.pathname.slice(prefix.length)) || '.'); if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file,'index.html'); if (!file.startsWith(root) || !fs.existsSync(file)) return route.fulfill({status:404,body:''}); return route.fulfill({contentType:types[path.extname(file)] || 'application/octet-stream', body:fs.readFileSync(file)}); });
      for (const route of routes.filter(r => r.includes(filter))) {
        await page.goto(origin + prefix + route, {waitUntil:'networkidle'});
        await page.waitForTimeout(150);
        const result = await page.evaluate(audit); report.pages++;
        for (const k of ['radius','spacing','clip','indicator','narrow','segmented','cards']) for (const row of result[k]) report[k].push({width, route, ...row});
      }
      await context.close();
    }
  } finally { await browser.close(); }
  fs.mkdirSync(path.resolve(__dirname,'../output/geometry'),{recursive:true});
  fs.writeFileSync(path.resolve(__dirname,'../output/geometry/report.json'), JSON.stringify(report,null,1));
  const dedupe = rows => [...new Map(rows.map(r => [r.route+'|'+r.el+'|'+r.rule, r])).values()];
  console.log(`pages ${report.pages}; ` + ['radius','spacing','clip','indicator','narrow','segmented','cards'].map(k => `${k} ${report[k].length}`).join('; '));
  if (['radius','spacing','clip','indicator','narrow','segmented','cards'].some(k => report[k].length)) process.exitCode = 1;
})();
