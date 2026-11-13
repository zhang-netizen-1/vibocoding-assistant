/* R1 acceptance measurements. No server: Playwright fulfills requests from dist.
   NODE_PATH=~/Downloads/Kreator/node_modules node tests/r1_headless.cjs */
const assert = require('node:assert/strict');
const fs = require('node:fs'), path = require('node:path');
const {chromium} = require('playwright');
const dist = path.resolve(__dirname, '../dist');
const origin = 'http://127.0.0.1:4179', prefix = '/vibocoding-assistant/';
const types = {'.html':'text/html', '.css':'text/css', '.js':'text/javascript', '.json':'application/json', '.svg':'image/svg+xml', '.webp':'image/webp', '.png':'image/png', '.jpg':'image/jpeg', '.woff2':'font/woff2'};
const close = (actual, expected, message) => assert.ok(Math.abs(actual - expected) <= 1, `${message}: ${actual}, expected ${expected}`);
function measure() {
  const box = el => { const r = el.getBoundingClientRect(); return {left:r.left, right:r.right, top:r.top, bottom:r.bottom, width:r.width, height:r.height}; };
  const display = el => el ? getComputedStyle(el).display : null;
  const brand = document.querySelector('.brand'), nav = document.querySelector('.nav-inner');
  const brandBox = box(brand), navBox = box(nav);
  const controls = [...document.querySelectorAll('.gallery-card :is(.play-button,.reduced-link)')].flatMap(control => {
    const r = box(control), s = getComputedStyle(control);
    if (!r.width || !r.height || s.visibility === 'hidden') return [];
    const card = control.closest('.gallery-card'), cr = box(card), cs = getComputedStyle(card);
    const parent = control.offsetParent;
    if (!parent) throw new Error('Visible gallery control has no offsetParent');
    const pr = box(parent), ps = getComputedStyle(parent);
    const cardRadius = parseFloat(cs.borderBottomRightRadius);
    const cardDistances = [cr.right - r.right, cr.bottom - r.bottom];
    return [{
      key:card.dataset.demoKey, control:control.className,
      containingBlock:parent === card ? 'card' : parent.className,
      radius:parseFloat(s.borderBottomRightRadius), cardRadius, cardDistances,
      inCorner:cardDistances.every(distance => distance >= 0 && distance < cardRadius),
      cardBorder:[parseFloat(cs.borderRightWidth), parseFloat(cs.borderBottomWidth)],
      offset:[parseFloat(s.right), parseFloat(s.bottom)],
      measuredOffset:[pr.right - r.right - parseFloat(ps.borderRightWidth), pr.bottom - r.bottom - parseFloat(ps.borderBottomWidth)],
      // HEAD base.css: button uses --radius-md (8px); site.css: plain span has
      // no radius, while motion-grid explicitly gave both control types 8px.
      preR1Radius:control.matches('.play-button') || control.closest('.motion-grid') ? 8 : 0,
    }];
  });
  const result = {brandX:brandBox.left, headerWidth:navBox.width, navFits:true, controls};
  if (innerWidth >= 1024) {
    const items = [brand, ...document.querySelectorAll('.desktop-nav .nav-link,.desktop-nav .nav-trigger'), document.querySelector('.nav-actions')].filter(el => display(el) !== 'none');
    const rs = items.map(box);
    result.navFits = rs.every(r => r.left >= navBox.left && r.right <= navBox.right && r.top >= navBox.top && r.bottom <= navBox.bottom)
      && rs.every((r, i) => i === 0 || r.left >= rs[i - 1].right - 1);
  }
  const card = document.querySelector('.gallery-card[data-demo-key="button"]');
  if (!card) return result;
  const host = card.querySelector('.demo-scope'), stage = host.shadowRoot.querySelector('.demo-root.ds-stage');
  const wrap = [...stage.children].find(el => display(el) !== 'none');
  const content = [...wrap.children].filter(el => display(el) !== 'none' && !/absolute|fixed/.test(getComputedStyle(el).position));
  if (content.length !== 1) throw new Error(`Expected one button content card, got ${content.length}`);
  const cr = box(card), sr = box(stage), kr = box(content[0]);
  const radii = el => { const s = getComputedStyle(el); return [parseFloat(s.borderTopLeftRadius), parseFloat(s.borderBottomRightRadius)]; };
  const play = card.querySelector('.play-button');
  const playStyle = getComputedStyle(play), playDisplay = playStyle.display;
  result.thumbnail = {
    cardRadii:radii(card), stageRadii:radii(stage), contentRadii:radii(content[0]),
    inset:[kr.left - sr.left, kr.top - sr.top, sr.right - kr.right, sr.bottom - kr.bottom],
    cardStageGap:[sr.left - cr.left, cr.right - sr.right],
    paddingBottom:parseFloat(getComputedStyle(card.querySelector('.mini-stage')).paddingBottom),
    playDisplay,
    reducedDisplay:display(card.querySelector('.reduced-link')),
    hover:matchMedia('(hover:hover)').matches,
    reduced:matchMedia('(prefers-reduced-motion:reduce)').matches,
  };
  return result;
}
(async () => {
  const browser = await chromium.launch({headless:true}), measurements = [];
  try {
    for (const width of [1440,1024,768,390]) {
      for (const [mode, hasTouch, reducedMotion] of [['hover',false,'no-preference'], ['reduced',false,'reduce'], ['touch',true,'no-preference'], ['touch-reduced',true,'reduce']]) {
        const ctx = await browser.newContext({viewport:{width,height:900}, hasTouch, reducedMotion});
        try {
          await ctx.route('**/*', route => {
            const url = new URL(route.request().url());
            if (url.origin !== origin || !url.pathname.startsWith(prefix)) return route.abort();
            let file = path.resolve(dist, decodeURIComponent(url.pathname.slice(prefix.length)) || '.');
            if (!file.startsWith(dist + path.sep) && file !== dist) return route.abort();
            if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
            return fs.existsSync(file) ? route.fulfill({contentType:types[path.extname(file)] || 'application/octet-stream', body:fs.readFileSync(file)}) : route.fulfill({status:404,body:''});
          });
          const page = await ctx.newPage();
          let brandX;
          for (const [type, route] of [['home',''], ['category','components/'], ['design-system','design-system/'], ['entry','components/button/']]) {
            await page.goto(origin + prefix + route, {waitUntil:'load'});
            if (type === 'category' || type === 'design-system') {
              // Shadow content can exist before its thumbnail stylesheet is applied.
              await page.waitForFunction(() => {
                if (document.fonts.status !== 'loaded') return false;
                const stage = document.querySelector('.gallery-card[data-demo-key="button"] .demo-scope')
                  ?.shadowRoot?.querySelector('.demo-root.ds-stage');
                if (!stage) return false;
                const wrap = [...stage.children].find(el => getComputedStyle(el).display !== 'none');
                if (!wrap) return false;
                const content = [...wrap.children].filter(el => getComputedStyle(el).display !== 'none'
                  && !/absolute|fixed/.test(getComputedStyle(el).position));
                if (content.length !== 1) return false;
                const style = getComputedStyle(content[0]);
                return [style.borderTopLeftRadius, style.borderBottomRightRadius].every(radius => parseFloat(radius) > 0);
              }, undefined, {timeout:10000}).catch(error => {
                throw new Error(`${width} ${mode} ${type}: button thumbnail did not settle (shadow stage, single styled content card, fonts ready)`, {cause:error});
              });
            }
            const m = {width,mode,type,...await page.evaluate(measure)};
            measurements.push(m);
            console.log(JSON.stringify(m));
            if (brandX === undefined) brandX = m.brandX;
            close(m.brandX, brandX, `${width} ${mode} ${type} brand alignment`);
            close(m.brandX, width === 1440 ? 64 : 16, `${width} ${mode} ${type} brand x`);
            assert.ok(m.navFits, `${width} ${mode} ${type}: nav/search wraps or overlaps`);
            for (const c of m.controls) {
              const label = `${width} ${mode} ${type} ${c.key} ${c.control}`;
              const expectedRadius = c.inCorner
                ? Math.max(0, Math.min(...c.offset.map((offset, i) => c.cardRadius - c.cardBorder[i] - offset)))
                : c.preR1Radius;
              close(c.radius, expectedRadius, `${label}: ${c.inCorner ? 'corner' : 'pre-R1'} control radius`);
              c.measuredOffset.forEach((offset, i) => close(offset, c.offset[i], `${label}: visible control offset from ${c.containingBlock}`));
            }
            if (!m.thumbnail) continue;
            const t = m.thumbnail;
            for (const r of t.cardRadii) close(r,32,'card radius');
            for (const r of t.stageRadii) close(r,31,'stage radius');
            for (const r of t.contentRadii) close(r,14,'content radius');
            for (const d of t.inset) close(d,17,'equal content inset');
            for (const d of t.cardStageGap) close(d,1,'card/stage outer-edge gap');
            const hidden = t.playDisplay === 'none' && t.reducedDisplay === 'none';
            const shownControlReservation = type === 'design-system' ? 60 : 72;
            close(t.paddingBottom, t.hover && !t.reduced && hidden ? 0 : shownControlReservation, 'thumbnail control reservation');
            if (hasTouch || t.reduced || width <= 1023) assert.notEqual(t.playDisplay,'none','visible play control');
            // Root-token changes must propagate into the shadow root and both derived radii.
            await page.addStyleTag({content:':root{--thumb-inset:20px}'});
            const changed = (await page.evaluate(measure)).thumbnail;
            for (const r of changed.stageRadii) close(r,35,'derived stage radius after inset change');
            for (const r of changed.cardRadii) close(r,36,'derived gallery radius after inset change');
            for (const d of changed.inset) close(d,21,'derived content inset');
          }
        } finally { await ctx.close(); }
      }
    }
  } finally { await browser.close(); }
  assert.ok(measurements.some(m => m.controls.some(c => c.inCorner && c.containingBlock === 'card')), 'measured card-corner controls');
  for (const type of ['category', 'design-system']) {
    assert.ok(measurements.some(m => m.type === type && m.controls.some(c => !c.inCorner && c.containingBlock === 'mini-stage')), `measured ${type} stage controls outside card corners`);
  }
  const dir = path.resolve(__dirname,'../output/r1'); fs.mkdirSync(dir,{recursive:true});
  fs.writeFileSync(path.join(dir,'measurements.json'), JSON.stringify(measurements,null,2));
  console.log(`R1 passed: ${measurements.length} page/mode/width measurements`);
})().catch(error => { console.error(error); process.exitCode = 1; });
