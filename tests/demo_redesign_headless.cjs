/* Headless-only acceptance check. Build dist first; this script never builds it.
 * NODE_PATH=/Users/zhiguang/Downloads/Kreator/node_modules node tests/demo_redesign_headless.cjs
 * DEMO_URL may point at an existing local server (including its deployment prefix).
 * SHOTS_DIR overrides the sandbox-safe output/demo-redesign/D screenshot folder.
 */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
let playwright;
try { playwright = require('playwright'); }
catch { playwright = require('/Users/zhiguang/Downloads/Kreator/node_modules/playwright'); }
const demoGChecks = require('./demo_g_browser.js');
const demoHChecks = require('./demo_h_browser.js');
const hSlugs = ["component-tilt", "component-spotlight", "component-flip", "component-press", "component-switch", "component-morph", "tab-indicator", "inline-expand", "component-magnetic", "component-hover-preview", "component-hover-action", "component-ripple", "component-underline", "accordion", "overlay-menu", "overlay-drawer", "overlay-modal", "overlay-tooltip", "overlay-sheet", "toast-stack", "data-count", "data-bars", "data-reorder", "data-success", "filter-grid", "chart-morph", "skeleton-handoff", "data-input-shake", "data-skeleton", "text-stagger", "text-mask", "text-typewriter", "text-scramble", "text-draw", "odometer", "scroll-highlight", "text-text-morph"];
const workspace = path.resolve(__dirname, '..');
const dist = path.join(workspace, 'dist');
const shots = path.resolve(process.env.SHOTS_DIR || path.join(workspace, 'output/demo-redesign/D'));
const reportPath = path.join(workspace, 'output/demo-redesign/headless-report.json');
const routes = [
  'components/button/', 'components/input/', 'interactions/component-lift/', 'interactions/view-crossfade/',
  'components/modal/', 'components/tooltip/', 'interactions/scroll-reveal/', 'basics/grid/',
  'components/skeleton/', 'components/carousel/',
  'basics/color/', 'components/color/', 'scenarios/dashboard/', 'ai/skills/frontend-design/',
  'components/states/', 'scenarios/landing/', 'components/card/', 'components/toast/',
  'components/navbar/', 'components/table/', 'components/tabs/', 'components/switch/',
  'components/select/', 'components/hold-confirm/', 'interactions/view-slide/',
  'interactions/view-curtain/', 'interactions/media-wipe/', 'interactions/media-blur/',
  'interactions/scroll-parallax/', 'interactions/scroll-pin/',
  ...['checkbox','radio','slider','otp','search','segmented','password-strength','tag-input',
      'stepper','rating','upload','combobox','date','form','alert','empty','loader','drawer','popover']
    .map(slug => `components/${slug}/`),
  ...'cmdk sidebar accordion breadcrumb pagination steps dropdown context-menu mega-menu footer badge chip avatar kpi timeline badge-dot view-switch card-link split-button fab back-to-top table-fixed table-columns table-edit sortable-table load-more'.split(' ').map(slug => `components/${slug}/`)
];
routes.push(...hSlugs.map(slug => `interactions/${slug}/`));
const galleries = ['basics/', 'components/', 'interactions/', 'scenarios/', 'ai/'];
const report = {started: new Date().toISOString(), checks: [], failures: [], pageErrors: [], resourceErrors: [], screenshots: [], galleries: []};
const mime = {'.html':'text/html; charset=utf-8','.js':'text/javascript; charset=utf-8','.css':'text/css; charset=utf-8','.json':'application/json','.svg':'image/svg+xml','.png':'image/png','.jpg':'image/jpeg','.jpeg':'image/jpeg','.webp':'image/webp','.avif':'image/avif','.woff2':'font/woff2'};
let server, browser;
async function localOrigin() {
  if (process.env.DEMO_URL) {
    const url = new URL(process.env.DEMO_URL);
    if (url.protocol === 'file:') return url.href.endsWith('/') ? url.href : url.href + '/';
    assert.ok(['localhost', '127.0.0.1', '[::1]'].includes(url.hostname), 'DEMO_URL must be local');
    assert.ok(!['4180', '4181'].includes(url.port), 'Ports 4180 and 4181 are excluded');
    return url.href.endsWith('/') ? url.href : url.href + '/';
  }
  assert.ok(fs.existsSync(path.join(dist, 'index.html')), 'Build dist before running this script');
  server = http.createServer((req, res) => {
    let pathname;
    try { pathname = decodeURIComponent(new URL(req.url, 'http://localhost').pathname); }
    catch {res.writeHead(400).end(); return;}
    // Support both the root URL and the production deployment prefix.
    pathname = pathname.replace(/^\/vibocoding-assistant(?=\/)/, '');
    let file = path.resolve(dist, '.' + pathname);
    if (!file.startsWith(dist + path.sep) && file !== dist) {res.writeHead(403).end(); return;}
    try {
      if (fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
      const body = fs.readFileSync(file);
      res.writeHead(200, {'Content-Type': mime[path.extname(file)] || 'application/octet-stream', 'Cache-Control':'no-store'}).end(body);
    } catch {res.writeHead(404).end('Not found');}
  });
  async function listen(port) {
    await new Promise((resolve, reject) => {
      const fail = error => {server.removeListener('listening', done); reject(error);};
      const done = () => {server.removeListener('error', fail); resolve();};
      server.once('error', fail); server.once('listening', done); server.listen(port, '127.0.0.1');
    });
  }
  try {await listen(4182);} catch (error) {if (error.code !== 'EADDRINUSE') throw error; await listen(0);}
  return `http://127.0.0.1:${server.address().port}/`;
}
async function check(name, fn) {
  try {const detail = await fn(); report.checks.push({name, pass:true, ...(detail === undefined ? {} : {detail})});}
  catch (error) {report.failures.push({name, error:error.message}); console.error('FAIL', name, error.message);}
}
function layoutAudit() {
  const scopes = [...document.querySelectorAll('.demo-scope')];
  const failures = [], images = [], chains = [];
  const visible = node => {
    const s = getComputedStyle(node);
    return node.getClientRects().length && s.display !== 'none' && s.visibility !== 'hidden';
  };
  scopes.forEach((scope, index) => {
    const slug = scope.dataset.demoSlug || scope.dataset.demoKey || `scope-${index}`;
    const failureStart = failures.length;
    const shadow = scope.shadowRoot;
    if (!shadow) {failures.push({index, slug, issue:'missing shadow root'}); return;}
    const root = shadow.querySelector('.demo-root'), box = scope.getBoundingClientRect();
    if (!root) {failures.push({index, slug, issue:'missing demo root'}); return;}
    const r = root.getBoundingClientRect();
    if (r.width > box.width + 2 || r.left < box.left - 2 || r.right > box.right + 2)
      failures.push({index, issue:'shadow root outside host', host:box.width, width:r.width});
    if (root.scrollWidth > root.clientWidth + 2)
      failures.push({index, issue:'shadow horizontal overflow', scroll:root.scrollWidth, client:root.clientWidth});
    for (const stage of shadow.querySelectorAll('.ds-stage,.canvas,.stage')) {
      if (!visible(stage)) continue;
      if (stage.scrollWidth > stage.clientWidth + 2)
        failures.push({index, issue:'stage horizontal overflow', selector:stage.className, scroll:stage.scrollWidth, client:stage.clientWidth});
    }
    for (const hint of root.querySelectorAll('.ds-hint')) {
      if (!visible(hint)) continue;
      const h=hint.getBoundingClientRect(), parent=hint.parentElement;
      if (Math.abs(h.left-r.left-13)>1.1 || Math.abs(r.bottom-h.bottom-13)>1.1)
        failures.push({index, issue:'hint detached from stage bottom', left:h.left-r.left, bottom:r.bottom-h.bottom});
      if (getComputedStyle(parent).position !== 'relative')
        failures.push({index, issue:'hint parent lost positioning context', selector:parent.className});
      for (const subject of parent.children) {
        if (subject.classList.contains('ds-hint') || !visible(subject)) continue;
        const s=subject.getBoundingClientRect();
        if (s.bottom>h.top-11.5)
          failures.push({index, issue:'subject enters hint clearance', selector:subject.className, clearance:h.top-s.bottom});
      }
    }
    failures.slice(failureStart).forEach(failure => {failure.slug = slug;});
    for (const img of shadow.querySelectorAll('img')) images.push({index, slug, src:img.currentSrc || img.src, complete:img.complete && img.naturalWidth > 0});
    chains.push({index, slug, demoKind:scope.dataset.demoKind, interactive:scope.hasAttribute('data-interactive'), sheets:[...shadow.querySelectorAll('link[rel="stylesheet"],style')].map(node => ({kind:node.dataset.demoSheet || node.dataset.demoStyle || '', href:node.getAttribute('href') || '', text:node.tagName === 'STYLE' ? node.textContent.slice(0,160) : ''}))});
  });
  for (const img of document.images) images.push({src:img.currentSrc || img.src, complete:img.complete && img.naturalWidth > 0});
  return {scopeCount:scopes.length, pageOverflow:document.documentElement.scrollWidth > innerWidth + 2, failures, images, chains};
}
function verifyChains(chains, requireSkin = false, requireStates = false) {
  for (const {index, slug, demoKind, interactive, sheets} of chains) {
    const classify = sheet => {
      const kinds = {demo:'source', source:'source', spec:'spec', kind:'kind', skin:'skin', a11y:'a11y', state:'states', states:'states'};
      if (kinds[sheet.kind]) return kinds[sheet.kind];
      const file = path.posix.basename(sheet.href);
      if (file === 'demo-accessibility.css') return 'a11y';
      if (file === 'states.css') return 'states';
      if (file.startsWith('_kind-')) return 'kind';
      if (sheet.href.includes('/demo-skins/')) return 'skin';
      if (file === 'demo-spec.css') return 'spec';
      if (/^demo-.*\.css$/.test(file)) return 'source';
      return null;
    };
    const actual = sheets.map(classify).filter(Boolean);
    const skinFile = `${demoKind}-${slug}.css`;
    const hasSkin = fs.existsSync(path.join(workspace, 'site-src/redesign/demo-skins', skinFile));
    const expected = ['source','spec', ...(actual.includes('kind') ? ['kind'] : []), ...(hasSkin || (requireSkin && interactive) || actual.includes('skin') ? ['skin'] : []), 'a11y', ...((requireStates && interactive) || actual.includes('states') ? ['states'] : [])];
    assert.deepEqual(actual, expected, `scope ${index}: expected ${expected.join(' → ')}, got ${actual.join(' → ')}`);
    if (hasSkin) {
      assert.ok(sheets.some(sheet => classify(sheet) === 'skin' && path.posix.basename(sheet.href) === skinFile), `scope ${index}: missing ${skinFile}`);
    }
  }
}
async function ready(page, url) {
  if (url.startsWith('file:') && url.endsWith('/')) url += 'index.html';
  const response = await page.goto(url, {waitUntil:'networkidle'});
  if (response) assert.equal(response.status(), 200, url);
  await page.waitForFunction(() => window.VibeDemos && [...document.querySelectorAll('.demo-scope')].every(scope => scope.shadowRoot && [...scope.shadowRoot.querySelectorAll('link[rel="stylesheet"]')].every(link => link.sheet)));
  await page.evaluate(async () => {
    const roots = [document, ...[...document.querySelectorAll('.demo-scope')].map(scope => scope.shadowRoot)];
    const images = roots.flatMap(root => [...root.querySelectorAll('img')]);
    await Promise.all(images.map(img => {img.loading='eager'; return img.decode().catch(() => {});}));
    await document.fonts.ready;
  });
}
async function state(page, name) {await page.locator(`[data-state="${name}"]`).click(); await page.waitForTimeout(210);}
function styleSnapshot(node) {
  const s = getComputedStyle(node), r = node.getBoundingClientRect();
  return {background:s.backgroundColor, color:s.color, transform:s.transform, shadow:s.boxShadow, outline:s.outlineStyle, outlineWidth:s.outlineWidth, opacity:s.opacity, cursor:s.cursor, width:r.width, height:r.height, disabled:node.disabled, busy:node.getAttribute('aria-busy'), text:node.textContent};
}
async function buttonChecks(page, label) {
  const button = page.locator('.demo-scope[data-interactive] .btn-pri').first();
  const snap = () => button.evaluate(styleSnapshot);
  await state(page,'free'); const initial = await snap();
  await state(page,'hover'); const hover = await snap();
  await state(page,'pressed'); const pressed = await snap();
  await check(`${label}: default/hover/pressed`, () => {
    assert.notEqual(initial.background, hover.background);
    assert.notEqual(hover.background, pressed.background);
    assert.notEqual(initial.transform, pressed.transform);
    return {initial,hover,pressed};
  });
  await state(page,'disabled');
  await check(`${label}: disabled`, async () => {const s = await snap(); assert.equal(s.disabled,true); assert.equal(s.cursor,'not-allowed'); assert.ok(Math.abs(Number(s.opacity)-.45)<.02, JSON.stringify(s)); return s;});
  await state(page,'focus');
  await check(`${label}: fixed focus ring`, async () => {const s = await snap(); assert.notEqual(s.outline,'none'); assert.ok(parseFloat(s.outlineWidth)>=2); return s;});
  await state(page,'free'); const beforeLoad = await snap();
  await state(page,'loading');
  await check(`${label}: loading dimensions`, async () => {const s = await snap(); assert.ok(Math.abs(s.width-beforeLoad.width)<1); assert.ok(Math.abs(s.height-beforeLoad.height)<1); assert.equal(s.busy,'true'); assert.equal(s.disabled,true); assert.equal(await button.locator('.demo-loading-icon').count(),1); return s;});
  await check(`${label}: success`, async () => {
    await state(page,'success');
    const evidence = await button.evaluate(styleSnapshot);
    assert.match(evidence.text,/成功|已保存|已提交|完成/);
    const successColor = await button.evaluate(node => getComputedStyle(node).getPropertyValue('--ds-success').trim());
    assert.ok(successColor, 'success token exists');
    assert.ok(evidence.color === 'rgb(4, 120, 87)' || evidence.background === 'rgb(4, 120, 87)', JSON.stringify(evidence));
    await state(page,'free');
    assert.equal(await button.textContent(),initial.text);
    assert.equal(await button.evaluate(node => node.disabled),false);
    return evidence;
  });
  await check(`${label}: copy success resets after 1.6s`, async () => {
    await state(page,'free');
    const copy = page.locator('.demo-scope[data-interactive] #copyDemoBtn');
    const original = await copy.textContent(); await copy.click();
    await page.waitForFunction(() => document.querySelector('.demo-scope[data-interactive]').shadowRoot.querySelector('#copyDemoBtn').classList.contains('ds-success'));
    const success = await copy.evaluate(styleSnapshot);
    assert.equal(success.disabled,true);
    assert.ok(success.color === 'rgb(4, 120, 87)' || success.background === 'rgb(4, 120, 87)', JSON.stringify(success));
    await page.waitForTimeout(1750);
    assert.equal(await copy.evaluate(node=>node.classList.contains('ds-success')),false);
    assert.equal(await copy.isDisabled(),false); assert.equal(await copy.textContent(),original);
    return success;
  });
  await state(page,'free');
  await check(`${label}: keyboard focus`, async () => {
    await button.focus(); await page.keyboard.press('Tab'); await page.keyboard.press('Shift+Tab');
    const result = await button.evaluate(node => ({focused:node.getRootNode().activeElement===node, visible:node.matches(':focus-visible'), outline:getComputedStyle(node).outlineStyle}));
    assert.equal(result.focused,true); assert.equal(result.visible,true); assert.notEqual(result.outline,'none'); return result;
  });
}
async function inputChecks(page, label) {
  const input = page.locator('.demo-scope[data-interactive] input:not([type="hidden"])').first();
  await input.fill('验收输入内容');
  for (const name of ['focus','disabled','error','free']) {
    await state(page,name);
    await check(`${label}: input survives ${name}`, async () => {assert.equal(await input.inputValue(),'验收输入内容'); if(name==='disabled') assert.equal(await input.isDisabled(),true); if(name==='error') assert.equal(await input.getAttribute('aria-invalid'),'true');});
  }
}
async function liftChecks(page, label, mobile) {
  const card = page.locator('.demo-scope[data-interactive] .lift-card').first();
  async function settledSnapshot() {
    await card.evaluate(async node => {
      // Flush style before collecting transitions triggered by focus or touch.
      getComputedStyle(node).transform;
      await Promise.all(node.getAnimations().filter(animation =>
        animation.effect.getComputedTiming().iterations !== Infinity
      ).map(animation => animation.finished.catch(() => {})));
    });
    return card.evaluate(styleSnapshot);
  }
  await page.mouse.move(0,0);
  await card.evaluate(node => node.blur());
  const original = await settledSnapshot();
  if (mobile) {
    assert.equal(await card.getAttribute('aria-pressed'),'false');
    // A tap is a pointer sequence (:active, then click); wait until the click's
    // touch-open state has taken effect before sampling the settled transform.
    await card.tap(); await card.evaluate((node, before) => new Promise(resolve => {
      const end = performance.now() + 1500;
      (function poll() { if (getComputedStyle(node).transform !== before || performance.now() > end) resolve(); else requestAnimationFrame(poll); })();
    }), original.transform); const lifted = await settledSnapshot();
    assert.equal(await card.getAttribute('aria-pressed'),'true');
    await card.tap(); const restored = await settledSnapshot();
    assert.equal(await card.getAttribute('aria-pressed'),'false');
    await check(`${label}: mobile tap toggle`, () => {const flat = value => (value === 'none' ? 'matrix(1, 0, 0, 1, 0, 0)' : value).replace(/-?\d+(\.\d+)?(e-?\d+)?/g, n => String(Math.round(Number(n) * 100) / 100 || 0)); assert.notEqual(flat(lifted.transform),flat(original.transform)); assert.equal(flat(restored.transform),flat(original.transform)); return {original,lifted,restored};});
  } else {
    await card.hover();
    await check(`${label}: hover lift`, async () => {const lifted = await settledSnapshot(); assert.notEqual(lifted.transform,original.transform); assert.notEqual(lifted.shadow,original.shadow); return lifted;});
    await page.mouse.move(0,0);
  }
}
async function crossfadeChecks(page, label) {
  const stack = page.locator('.demo-scope[data-interactive] .view-stack').first();
  const toggle = page.locator('.demo-scope[data-interactive] [data-action="next"]').first();
  async function layers() {return stack.evaluate(node => [...node.querySelectorAll('.view-a,.view-b')].map(el => ({hidden:el.getAttribute('aria-hidden'), opacity:Number(getComputedStyle(el).opacity), position:getComputedStyle(el).position, text:el.textContent, rect:{x:el.getBoundingClientRect().x,y:el.getBoundingClientRect().y}})));}
  const initial = await layers();
  await check(`${label}: crossfade two layers`, () => {assert.equal(initial.length,2); assert.equal(initial.filter(l=>l.hidden==='false').length,1); assert.equal(initial.filter(l=>l.hidden==='true').length,1); assert.ok(Math.abs(initial[0].rect.x-initial[1].rect.x)<2); assert.ok(Math.abs(initial[0].rect.y-initial[1].rect.y)<2); return initial;});
  await toggle.click(); await page.waitForTimeout(800); const next = await layers();
  await check(`${label}: crossfade swaps aria`, () => {assert.notEqual(next[0].hidden,initial[0].hidden); assert.equal(next.filter(l=>l.hidden==='false'&&l.opacity>.98).length,1); assert.equal(next.filter(l=>l.hidden==='true'&&l.opacity<.02).length,1); return next;});
  await toggle.evaluate(node => {for(let i=0;i<9;i++) node.click();});
  await page.waitForTimeout(800); const final = await layers();
  await check(`${label}: rapid toggle settles`, () => {assert.equal(final.filter(l=>l.hidden==='false'&&l.opacity>.98).length,1); assert.equal(final.filter(l=>l.hidden==='true'&&l.opacity<.02).length,1); assert.equal(final[0].hidden,initial[0].hidden); return final;});
}
async function batchEChecks(page, route, width) {
  const scope = page.locator('.demo-scope[data-interactive]').first();
  if (route === 'components/states/') {
    const sizes = await scope.locator('.st-btn').evaluateAll(nodes => nodes.map(node => {
      const r = node.getBoundingClientRect();
      return {width:r.width,height:r.height};
    }));
    assert.equal(sizes.length,12);
    assert.ok(sizes.every(size => Math.abs(size.width-sizes[0].width)<1 && Math.abs(size.height-sizes[0].height)<1));
    const labels = await scope.locator('.st-lbl').evaluateAll(nodes => nodes.map(node => getComputedStyle(node).fontSize));
    assert.ok(labels.every(size => size === '12px'));
  }
  if (route === 'components/toast/') {
    const trigger = scope.locator('[data-cmd="toast"]');
    await trigger.click();
    const toast = scope.locator('.ds-toast-output .demo-status');
    assert.equal(await toast.locator('.ds-toast-title').textContent(), await trigger.getAttribute('data-arg'));
    assert.ok(await toast.locator('.ds-toast-description').textContent());
    const style = await toast.evaluate(node => ({background:getComputedStyle(node).backgroundColor,shadow:getComputedStyle(node).boxShadow}));
    assert.equal(style.background,'rgb(255, 255, 255)');
    assert.notEqual(style.shadow,'none');
    await trigger.click();
    assert.equal(await scope.locator('.demo-status').count(),1);
  }
  if (route === 'components/switch/') {
    const input = scope.locator('.switch input');
    const initial = await input.isChecked();
    await scope.locator('label[for="ds-autosave"]').click();
    assert.equal(await input.isChecked(),!initial);
    await input.focus(); await page.keyboard.press('Space');
    assert.equal(await input.isChecked(),initial);
  }
  if (route === 'components/select/') {
    await scope.locator('select.i').selectOption({label:'上海'});
    assert.equal(await scope.locator('select.i option:checked').textContent(),'上海');
  }
  if (route === 'components/tabs/') {
    await scope.locator('#tab-reviews').click();
    assert.equal(await scope.locator('#tab-reviews').getAttribute('aria-selected'),'true');
    await page.keyboard.press('ArrowRight');
    assert.equal(await scope.locator('#tab-help').getAttribute('aria-selected'),'true');
  }
  if (route === 'components/hold-confirm/') {
    const button = scope.locator('#holdBtn');
    await button.focus(); await page.keyboard.down('Enter');
    await page.waitForTimeout(200); await page.keyboard.up('Enter');
    assert.equal(await button.evaluate(node=>node.classList.contains('completed')),false);
    await page.waitForTimeout(1250);
    await page.keyboard.down('Enter'); await page.waitForTimeout(1050);
    await page.keyboard.up('Enter');
    assert.equal(await button.evaluate(node=>node.classList.contains('completed')),true);
  }
  if (route === 'interactions/view-slide/') {
    const track = scope.locator('.view-track');
    await scope.locator('[data-action="next"]').click();
    assert.equal(await track.evaluate(node=>node.classList.contains('next')),true);
    await scope.locator('[data-action="next"]').click();
    assert.equal(await track.evaluate(node=>node.classList.contains('next')),false);
  }
  if (route === 'interactions/scroll-pin/' || route === 'interactions/scroll-parallax/') {
    await scope.locator('.mini-scroll').evaluate(node => {node.scrollTop=node.scrollHeight;node.dispatchEvent(new Event('scroll'));});
    if (route === 'interactions/scroll-pin/') {
      assert.equal(await scope.locator('.pin-scene>strong').textContent(),'第三幕');
      assert.equal(await scope.locator('.ds-pin-image-3').evaluate(node=>getComputedStyle(node).opacity),'1');
    }
  }
  const audit = await page.evaluate(layoutAudit);
  assert.equal(audit.pageOverflow,false,JSON.stringify({route,width,audit}));
  assert.deepEqual(audit.failures,[],JSON.stringify({route,width,audit}));
}
async function batchFChecks(page, route, width) {
  const slug = route.split('/')[1];
  const names = ['checkbox','radio','slider','otp','search','segmented','password-strength',
    'tag-input','stepper','rating','upload','combobox','date','form','alert','empty','loader','drawer','popover'];
  if (!route.startsWith('components/') || !names.includes(slug)) return;
  const scope = page.locator('.demo-scope[data-interactive]').first();
  if (slug === 'checkbox') {
    assert.equal(await scope.locator('#ckAll').evaluate(node => node.indeterminate), true);
    await scope.locator('.ds-check-parent').click();
    assert.equal(await scope.locator('.ck-child:checked').count(), 3);
    await scope.locator('.ds-check-children .check').first().click();
    assert.equal(await scope.locator('#ckAll').evaluate(node => node.indeterminate), true);
  }
  if (slug === 'radio') {
    await scope.locator('.radio-group .check').nth(1).click();
    assert.equal(await scope.locator('input[name="plan"]:checked').count(), 1);
    assert.equal(await scope.locator('input[name="plan"]').nth(1).isChecked(), true);
  }
  if (slug === 'slider') {
    await scope.locator('input[type="range"]').fill('64');
    assert.equal(await scope.locator('.ds-volume-control span').textContent(), '64%');
  }
  if (slug === 'otp') {
    const cells = scope.locator('.otp-row input');
    for (let index = 0; index < 6; index++) await cells.nth(index).fill(String(index + 1));
    assert.equal(await scope.locator('.otp-hint').textContent(), '已填完，可提交。');
    const rectangles = await cells.evaluateAll(nodes => nodes.map(node => {
      const box = node.getBoundingClientRect();
      return {width:box.width,height:box.height};
    }));
    assert.ok(rectangles.every(box => box.width >= 44 && box.height >= 44), JSON.stringify(rectangles));
  }
  if (slug === 'search') {
    await scope.locator('.searchbox input').fill('品牌提案');
    await scope.locator('.searchbox input').press('Enter');
    assert.match(await scope.locator('.demo-status').textContent(), /品牌提案/);
  }
  if (slug === 'segmented') {
    await scope.locator('.options label').nth(1).click();
    assert.equal(await scope.locator('input[value="grid"]').isChecked(), true);
  }
  if (slug === 'password-strength') {
    await scope.locator('#pwInput').fill('Project2026!');
    assert.equal(await scope.locator('.pw-demo').getAttribute('data-level'), '4');
  }
  if (slug === 'tag-input') {
    await scope.locator('#tagInput').fill('提案');
    await scope.locator('#tagInput').press('Enter');
    assert.equal(await scope.locator('.tagchip').count(), 2);
    await scope.locator('.tagx').last().click();
    assert.equal(await scope.locator('.tagchip').count(), 1);
  }
  if (slug === 'stepper') {
    await scope.locator('[data-arg="1"]').click();
    assert.equal(await scope.locator('#num').inputValue(), '3');
    await scope.locator('[data-arg="-1"]').click();
    assert.equal(await scope.locator('#num').inputValue(), '2');
  }
  if (slug === 'rating') {
    await scope.locator('.st').nth(3).click();
    assert.equal(await scope.locator('.st.on').count(), 4);
    assert.equal(await scope.locator('.st[aria-pressed="true"]').count(), 1);
  }
  if (slug === 'upload') {
    await scope.locator('#filei').setInputFiles({name:'项目资料.txt',mimeType:'text/plain',buffer:Buffer.from('项目资料')});
    assert.match(await scope.locator('#dz-text').textContent(), /项目资料.txt/);
  }
  if (slug === 'combobox') {
    await scope.locator('input[list="city-options"]').fill('上海');
    assert.equal(await scope.locator('input[list="city-options"]').inputValue(), '上海');
  }
  if (slug === 'date') {
    await scope.locator('input[type="date"]').fill('2026-11-20');
    assert.equal(await scope.locator('input[type="date"]').inputValue(), '2026-11-20');
  }
  if (slug === 'form') {
    await scope.locator('#ds-register-name').fill('设计工作室');
    await scope.locator('#ds-register-password').fill('Project2026!');
    await scope.locator('[data-cmd="demoRegister"]').click();
    assert.equal(await scope.locator('.demo-status').textContent(), '模拟提交完成，未创建账号');
  }
  if (slug === 'alert') assert.equal(await scope.locator('.alert').count(), 4);
  if (slug === 'empty') {
    await scope.locator('[data-cmd="toast"]').click();
    assert.equal(await scope.locator('.demo-status').textContent(), '去创建 ✓');
  }
  if (slug === 'loader') assert.equal(await scope.locator('.spinner').count(), 1);
  if (slug === 'drawer') {
    await scope.locator('[data-cmd="openDrawer"]').click();
    await page.waitForTimeout(400);
    const bounds = await scope.evaluate(node => {
      const root = node.shadowRoot.querySelector('.ds-stage').getBoundingClientRect();
      const panel = node.shadowRoot.querySelector('.drawer-panel').getBoundingClientRect();
      return {left:panel.left-root.left,right:root.right-panel.right,top:panel.top-root.top,bottom:root.bottom-panel.bottom};
    });
    assert.ok(Object.values(bounds).every(value => value >= -.5), JSON.stringify(bounds));
    await page.keyboard.press('Escape');
    assert.equal(await scope.locator('#dmask').evaluate(node => node.classList.contains('show')), false);
  }
  if (slug === 'popover') {
    await kindGeometryChecks(page, route);
    await page.keyboard.press('Escape');
    assert.equal(await scope.locator('#popover-trigger').getAttribute('aria-expanded'), 'false');
  }
  const audit = await page.evaluate(layoutAudit);
  assert.equal(audit.pageOverflow, false, JSON.stringify({route,width,audit}));
  assert.deepEqual(audit.failures, [], JSON.stringify({route,width,audit}));
}
async function specimenGeometry(page) {
  const result=await page.locator('.demo-scope[data-interactive]').first().evaluate(scope=>{
    const root=scope.shadowRoot.querySelector('.ds-stage');
    const subject=root.querySelector('.ds-h-panel,.ds-surface,.lift-card,.mini-scroll,.carousel,.token-demo,.mini-page,.skill-card,.ds-states-panel,.card2,.ds-toast-panel,.ds-navbar-panel,.ds-table-panel,.ds-tabs-panel,.ds-switch-panel,.ds-select-panel,.ds-hold-panel,.scene-window,.scene-curtain,.art,.canvas>section[class^="ds-"],.guide-card-stage>section[class^="ds-"]');
    const hint=root.querySelector('.ds-hint');
    const r=root.getBoundingClientRect(),s=subject.getBoundingClientRect(),h=hint?.getBoundingClientRect();
    const style=getComputedStyle(root);
    const frame=subject.parentElement, frameStyle=getComputedStyle(frame);
    const inner=frame.clientWidth-parseFloat(frameStyle.paddingLeft)-parseFloat(frameStyle.paddingRight);
    return {stage:r.width,subject:s.width,ratio:s.width/inner,left:s.left-r.left,right:r.right-s.right,top:s.top-r.top,bottom:r.bottom-s.bottom,
      typeBody:style.getPropertyValue('--ds-demo-body').trim(),typeHeading:style.getPropertyValue('--ds-demo-heading').trim(),typeButton:style.getPropertyValue('--ds-demo-button').trim(),hasHint:!!h,hintLeft:h?h.left-r.left:null,hintBottom:h?r.bottom-h.bottom:null,hintRight:h?r.right-h.right:null,clearance:h?h.top-s.bottom:null};
  });
  assert.ok(result.left>=15.5&&result.right>=15.5&&result.top>=15.5&&result.bottom>=15.5,JSON.stringify(result));
  if(result.hasHint) {
  assert.ok(Math.abs(result.hintLeft-13)<=1.1&&Math.abs(result.hintBottom-13)<=1.1,JSON.stringify(result));
  assert.ok(result.hintRight>=11.5&&result.clearance>=11.5,JSON.stringify(result));
  }
  assert.equal(result.typeBody,result.stage>=640?'16px':'14px');
  assert.equal(result.typeHeading,result.stage>=640?'22px':'16px');
  assert.equal(result.typeButton,result.stage>=640?'15px':'14px');
  if(result.stage>=640) {
    const inner=result.subject/result.ratio;
    const expected=Math.min(inner,Math.max(420,Math.min(inner*.66,560)));
    assert.ok(Math.abs(result.subject-expected)<2,JSON.stringify(result));
  }
  return result;
}
async function batchBChecks(page, route, label, mobile) {
  const scope=page.locator('.demo-scope[data-interactive]').first();
  if (route.includes('/modal/')) {
    await scope.locator('[data-cmd="openModal"]').click();
    await scope.locator('[role="dialog"]').waitFor({state:'visible'});
    assert.equal(await scope.locator('.modal-actions button').count(),2);
    const file=path.join(shots,`modal-open-${mobile?390:1440}.png`);
    await page.locator('.demo-stage').first().screenshot({path:file});report.screenshots.push(file);
    await page.keyboard.press('Escape');
    await scope.locator('[role="dialog"]').waitFor({state:'hidden'});
  }
  if (route.includes('/tooltip/')) {
    const trigger=scope.locator('[data-tooltip-trigger]');
    if(mobile)await trigger.tap();else await trigger.hover();
    await scope.locator('[role="tooltip"]').waitFor({state:'visible'});
    assert.equal(await scope.locator('[role="tooltip"]').evaluate(node=>getComputedStyle(node).fontSize),'13px');
    if(mobile){await trigger.tap();await scope.locator('[role="tooltip"]').waitFor({state:'hidden'});await trigger.tap();}
  }
  if (route.includes('/scroll-reveal/')) {
    const initial=await scope.locator('.mini-scroll').evaluate(node=>{
      const card=node.querySelector('.ds-reveal-card'),a=node.getBoundingClientRect(),b=card.getBoundingClientRect();
      return {shown:getComputedStyle(card).opacity,top:b.top-a.top,height:a.height,title:node.querySelector('.scroll-top strong').textContent};
    });
    assert.equal(initial.shown,'1'); assert.ok(initial.top<initial.height/2); assert.ok(initial.title);
    await scope.locator('.mini-scroll').evaluate(node=>{for(const card of node.querySelectorAll('.ds-reveal-card')){node.scrollTop=card.offsetTop-16;node.dispatchEvent(new Event('scroll'));}});
    await page.waitForTimeout(400);
    assert.equal(await scope.locator('.ds-reveal-card.ds-revealed').count(),3);
  }
  if (route.includes('/grid/')) {
    const originalWidth=await scope.locator('.mini-layout').evaluate(node=>node.getBoundingClientRect().width);
    await scope.locator('[data-guide-mode="1"]').click();
    assert.equal(await scope.locator('.guide-card-stage').getAttribute('data-mode'),'1');
    assert.ok(await scope.locator('.mini-layout').evaluate(node=>node.getBoundingClientRect().width)<originalWidth);
    if(mobile)assert.equal(await scope.locator('.ds-grid-card:visible').count(),4);
    await scope.locator('[data-guide-mode="0"]').click();
    assert.equal(await scope.locator('.ds-grid-card').count(),6);
    if(mobile) {
      assert.equal(await scope.locator('.ds-grid-card:visible').count(),4);
      assert.equal(await scope.locator('.mini-layout-items').evaluate(node=>getComputedStyle(node).gridTemplateColumns.split(' ').length),2);
    }
  }
  if (route.includes('/skeleton/')) {
    await scope.locator('.ds-skeleton-card.is-loaded').waitFor();
    assert.equal(await scope.locator('.ds-skeleton-card').getAttribute('aria-busy'),'false');
    assert.equal(await scope.locator('.ds-skeleton-content').getAttribute('aria-hidden'),'false');
  }
  if (route.includes('/carousel/')) {
    await scope.locator('#carPause').click();
    assert.equal(await scope.locator('#carPause').getAttribute('aria-pressed'),'true');
    await scope.locator('#carNext').click();
    assert.equal(await scope.locator('#carDots button').nth(1).getAttribute('aria-current'),'true');
    await scope.locator('#carPrev').click();
    assert.equal(await scope.locator('#carDots button').first().getAttribute('aria-current'),'true');
  }
}
async function batchCChecks(page,route) {
  const scope=page.locator('.demo-scope[data-interactive]').first();
  if(route==='basics/color/') {
    const input=scope.locator('[data-token-control="foreground"]');
    await input.evaluate(node=>{node.value='#FFFFFF';node.dispatchEvent(new Event('input',{bubbles:true}));});
    assert.match(await scope.locator('[data-token-output]').textContent(),/1\.00:1.*正文未达标/);
    await input.evaluate(node=>{node.value='#6D28D9';node.dispatchEvent(new Event('input',{bubbles:true}));});
  }
  if(route==='components/color/') {
    await scope.locator('input[type=color]').evaluate(node=>{node.value='#047857';node.dispatchEvent(new Event('input',{bubbles:true}));});
    assert.equal(await scope.locator('#hexc').textContent(),'#047857');
  }
  if(route==='scenarios/dashboard/') {
    await scope.locator('[data-guide-mode="1"]').click();
    assert.equal(await scope.locator('.guide-card-stage').getAttribute('data-mode'),'1');
    await scope.locator('[data-guide-mode="0"]').click();
    assert.equal(await scope.locator('.ds-dashboard-bars i').count(),7);
  }
  if(route==='ai/skills/frontend-design/') {
    assert.equal(await scope.locator('.skill-card').evaluate(node=>getComputedStyle(node).backgroundColor),'rgb(255, 255, 255)');
    assert.equal(await scope.locator('dt').first().evaluate(node=>getComputedStyle(node).color),'rgb(109, 40, 217)');
  }
}
async function reducedChecks(page, url, label) {
  await page.emulateMedia({reducedMotion:'reduce'}); await ready(page,url);
  await check(`${label}: reduced motion idle`, async () => {
    const result = await page.locator('.demo-scope').evaluateAll(scopes => scopes.flatMap(scope => [...scope.shadowRoot.querySelectorAll('*')].flatMap(node => {
      const s=getComputedStyle(node), animations=node.getAnimations().filter(a=>a.playState==='running');
      const transition=Math.max(...s.transitionDuration.split(',').map(x=>parseFloat(x)* (x.trim().endsWith('ms')?1:1000)));
      return transition>150.1 || animations.some(a=>a.effect.getTiming().iterations===Infinity) ? [{class:node.className,transition,animations:animations.length}] : [];
    })));
    assert.deepEqual(result,[]); return result;
  });
  if (url.includes('component-lift')) {
    const card=page.locator('.demo-scope .lift-card').first();
    await card.dispatchEvent('click'); await card.hover(); await page.waitForTimeout(170);
    await check(`${label}: reduced lift has no transform`, async () => assert.equal(await card.evaluate(el=>getComputedStyle(el).transform),'none'));
  }
  if (url.includes('view-crossfade')) await crossfadeChecks(page,`${label}: reduce`);
  await page.emulateMedia({reducedMotion:'no-preference'});
}
async function kindGeometryChecks(page, route) {
  const states={
    'components/dropdown/':['.dropdown > button','.dd-menu'],
    'components/popover/':['#popover-trigger','.popover-box'],
    'components/split-button/':['#splitCaret','.split-menu'],
    'interactions/overlay-menu/':['[data-action="toggle"]','.menu-items'],
    'interactions/component-hover-preview/':['.hvp-link','.hvp-pop']
  };
  const state=states[route];
  if (!state) return;
  const scope=page.locator('.demo-scope[data-interactive]').first();
  const trigger=scope.locator(state[0]);
  if(route.includes('hover-preview')) {
    await page.keyboard.press('Tab');
    await trigger.focus();
  } else await trigger.click();
  await page.waitForTimeout(600);
  const rectangle=await scope.evaluate((scope,selector)=>{
    const root=scope.shadowRoot.querySelector('.ds-stage');
    const popup=root.querySelector(selector), hint=root.querySelector('.ds-hint');
    const p=popup.getBoundingClientRect(),h=hint.getBoundingClientRect(),r=root.getBoundingClientRect();
    const style=getComputedStyle(popup);
    return {height:p.height,opacity:Number(style.opacity),display:style.display,
      clearance:h.top-p.bottom,left:p.left-r.left,right:r.right-p.right};
  },state[1]);
  assert.ok(rectangle.height>0&&rectangle.opacity>.98&&rectangle.display!=='none',JSON.stringify(rectangle));
  assert.ok(rectangle.clearance>=11.5&&rectangle.left>=.5&&rectangle.right>=.5,JSON.stringify(rectangle));
  return rectangle;
}
function catalogInventory() {
  const details = [];
  function walk(directory) {
    for(const entry of fs.readdirSync(directory,{withFileTypes:true})) {
      const file=path.join(directory,entry.name);
      if(entry.isDirectory()) walk(file);
      else if(entry.isFile() && entry.name==='index.html') {
        const source=fs.readFileSync(file,'utf8');
        const count=[...source.matchAll(/<div\b[^>]*class="demo-scope"[^>]*data-interactive\b/g)].length;
        const kind=source.match(/<div\b[^>]*class="demo-scope"[^>]*data-demo-kind="([^"]+)"[^>]*data-interactive\b/)?.[1];
        if(count && !file.includes(`${path.sep}design-system${path.sep}`)) details.push({route:path.relative(dist,path.dirname(file)).split(path.sep).join('/')+'/',demos:count,kind});
      }
    }
  }
  walk(dist); return details;
}
(async () => {
  fs.mkdirSync(shots,{recursive:true}); fs.mkdirSync(path.dirname(reportPath),{recursive:true});
  const base = await localOrigin(); report.baseURL=base; report.screenshotDirectory=shots;
  const inventory=catalogInventory();
  await check('Detail inventory: 192 entries / 194 demos',()=>{
    assert.equal(inventory.length,Number(process.env.EXPECTED_ENTRIES||192));
    assert.equal(inventory.reduce((sum,row)=>sum+row.demos,0),Number(process.env.EXPECTED_DEMOS||194));
    return {entries:inventory.length,demos:inventory.reduce((sum,row)=>sum+row.demos,0),secondary:inventory.filter(row=>row.demos>1)};
  });
  browser = await playwright.chromium.launch({headless:true});
  for (const width of [1440,768,390]) {
    const context = await browser.newContext({viewport:{width,height:1000},hasTouch:width===390,isMobile:width===390,reducedMotion:'no-preference'});
    const page = await context.newPage(); page.setDefaultTimeout(10000);
    page.on('pageerror',error => report.pageErrors.push({width,url:page.url(),message:error.message}));
    page.on('response',response => {if(response.status()>=400) report.resourceErrors.push({width,url:response.url(),status:response.status()});});
    page.on('requestfailed',request => report.resourceErrors.push({width,url:request.url(),failure:request.failure()}));
    for (const route of routes) {
      const label=`${width} ${route}`, url=new URL(route,base).href;
      await check(`${label}: visit and audit`, async () => {
        await ready(page,url); const audit=await page.evaluate(layoutAudit);
        audit.specimen=await specimenGeometry(page);
        const stageFile=path.join(shots,`${route.replaceAll('/','-').replace(/-$/,'')}-${width}-stage.png`);
        await page.locator('.demo-stage').first().screenshot({path:stageFile}); report.screenshots.push(stageFile);
        assert.equal(audit.pageOverflow,false); assert.deepEqual(audit.failures,[]); assert.ok(audit.scopeCount>0);
        assert.deepEqual(audit.images.filter(img=>!img.complete),[]); verifyChains(audit.chains,true,/components\/(button|input)\//.test(route)); return audit;
      });
      await check(`${label}: behavior`, async () => {
        if(route.includes('/button/')) await buttonChecks(page,label);
        if(route.includes('/input/')) await inputChecks(page,label);
        if(route.includes('component-lift')) await liftChecks(page,label,width===390);
        if(route.includes('view-crossfade')) await crossfadeChecks(page,label);
        await batchBChecks(page,route,label,width===390);
        await batchCChecks(page,route);
        await batchEChecks(page,route,width);
        await batchFChecks(page,route,width);
        const slug = route.split('/')[1];
        if (route.startsWith('components/') && 'cmdk sidebar accordion breadcrumb pagination steps dropdown context-menu mega-menu footer badge chip avatar kpi timeline badge-dot view-switch card-link split-button fab back-to-top table-fixed table-columns table-edit sortable-table load-more'.split(' ').includes(slug)) {
          const behavior = await page.locator('.demo-scope[data-interactive]').first().evaluate(demoGChecks,slug);
          assert.ok(behavior.checks);
        }
        if (route.startsWith('interactions/') && hSlugs.includes(slug)) {
          const behavior = await page.locator('.demo-scope[data-interactive]').first().evaluate(demoHChecks,slug);
          assert.ok(behavior.checks.length >= 3);
        }
      });
      await check(`${label}: screenshot`, async () => {
        const file=path.join(shots,`${route.replaceAll('/','-').replace(/-$/,'')}-${width}.png`);
        await page.screenshot({path:file,fullPage:true}); report.screenshots.push(file);
      });
      await check(`${label}: reduced motion`, () => reducedChecks(page,url,label));
    }
    for(const detail of inventory.filter(row=>['ui','motion'].includes(row.kind)&&!routes.includes(row.route))) {
      await check(`${width} ${detail.route}: kind skin geometry`,async()=>{
        await ready(page,new URL(detail.route,base).href);
        const audit=await page.evaluate(layoutAudit);
        assert.equal(audit.pageOverflow,false); assert.deepEqual(audit.failures,[]);
        verifyChains(audit.chains);
        const opened=await kindGeometryChecks(page,detail.route);
        const active=await page.evaluate(layoutAudit);
        assert.equal(active.pageOverflow,false); assert.deepEqual(active.failures,[]);
        return {demos:audit.scopeCount,opened};
      });
    }
    let entries=0, demoCount=0;
    for (const route of galleries) await check(`${width} ${route}: all gallery demos`, async () => {
      await ready(page,new URL(route,base).href); const audit=await page.evaluate(layoutAudit);
      const count=await page.locator('.gallery-card').count(); entries+=count; demoCount+=audit.scopeCount;
      assert.equal(audit.pageOverflow,false); assert.deepEqual(audit.failures,[]); assert.deepEqual(audit.images.filter(img=>!img.complete),[]);
      verifyChains(audit.chains); report.galleries.push({width,route,entries:count,...audit});
      return {entries:count,demos:audit.scopeCount};
    });
    await check(`${width}: full gallery coverage`, () => {assert.equal(entries,Number(process.env.EXPECTED_ENTRIES||192)); assert.equal(demoCount,Number(process.env.EXPECTED_ENTRIES||192)); return {entries,demoCount};});
    for(const detail of inventory.filter(row=>row.demos>1)) await check(`${width} ${detail.route}: secondary demos`,async()=>{
      await ready(page,new URL(detail.route,base).href); const audit=await page.evaluate(layoutAudit);
      assert.equal(audit.scopeCount,detail.demos); assert.equal(audit.pageOverflow,false); assert.deepEqual(audit.failures,[]);
      assert.deepEqual(audit.images.filter(img=>!img.complete),[]); verifyChains(audit.chains); return audit;
    });
    await context.close();
  }
  await check('No page JavaScript errors', () => assert.deepEqual(report.pageErrors,[]));
  await check('No failed resources', () => assert.deepEqual(report.resourceErrors,[]));
})().catch(error => {report.failures.push({name:'fatal',error:error.stack}); console.error(error);}).finally(async () => {
  if(browser) await browser.close();
  if(server) await new Promise(resolve=>server.close(resolve));
  report.finished=new Date().toISOString(); fs.mkdirSync(path.dirname(reportPath),{recursive:true});
  fs.writeFileSync(reportPath,JSON.stringify(report,null,2));
  console.log(`${report.checks.length} checks passed; ${report.failures.length} failed. Report: ${reportPath}`);
  if(report.failures.length) process.exitCode=1;
});
