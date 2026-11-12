/* Headless-only acceptance check. Build dist first; this script never builds it.
 * NODE_PATH=/Users/zhiguang/Downloads/Kreator/node_modules node tests/demo_redesign_headless.cjs
 * DEMO_URL may point at an existing local server (including its deployment prefix).
 * SHOTS_DIR overrides the sandbox-safe output/demo-redesign/AB screenshot folder.
 */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const http = require('node:http');
let playwright;
try { playwright = require('playwright'); }
catch { playwright = require('/Users/zhiguang/Downloads/Kreator/node_modules/playwright'); }
const workspace = path.resolve(__dirname, '..');
const dist = path.join(workspace, 'dist');
const shots = path.resolve(process.env.SHOTS_DIR || path.join(workspace, 'output/demo-redesign/AB'));
const reportPath = path.join(workspace, 'output/demo-redesign/headless-report.json');
const routes = [
  'components/button/', 'components/input/', 'interactions/component-lift/', 'interactions/view-crossfade/',
  'components/modal/', 'components/tooltip/', 'interactions/scroll-reveal/', 'basics/grid/',
  'components/skeleton/', 'components/carousel/'
];
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
    failures.slice(failureStart).forEach(failure => {failure.slug = slug;});
    for (const img of shadow.querySelectorAll('img')) images.push({index, slug, src:img.currentSrc || img.src, complete:img.complete && img.naturalWidth > 0});
    chains.push({index, slug, sheets:[...shadow.querySelectorAll('link[rel="stylesheet"],style')].map(node => ({kind:node.dataset.demoSheet || node.dataset.demoStyle || '', href:node.getAttribute('href') || '', text:node.tagName === 'STYLE' ? node.textContent.slice(0,160) : ''}))});
  });
  for (const img of document.images) images.push({src:img.currentSrc || img.src, complete:img.complete && img.naturalWidth > 0});
  return {scopeCount:scopes.length, pageOverflow:document.documentElement.scrollWidth > innerWidth + 2, failures, images, chains};
}
function verifyChains(chains, requireSkin = false, requireStates = false) {
  for (const {index, sheets} of chains) {
    const classify = sheet => {
      const value = `${sheet.kind} ${sheet.href}`;
      if (/accessibility|a11y/.test(value)) return 'a11y';
      if (/state/.test(value)) return 'states';
      if (/skin/.test(value)) return 'skin';
      if (/spec/.test(value)) return 'spec';
      if (/source|demo/.test(value)) return 'source';
      return null;
    };
    const actual = sheets.map(classify).filter(Boolean);
    const expected = ['source','spec', ...(requireSkin || actual.includes('skin') ? ['skin'] : []), 'a11y', ...(requireStates || actual.includes('states') ? ['states'] : [])];
    let previous = -1;
    for (const kind of expected) {
      const at = actual.indexOf(kind);
      assert.ok(at > previous, `scope ${index}: expected ${expected.join(' → ')}, got ${actual.join(' → ')}`);
      previous = at;
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
  const original = await card.evaluate(styleSnapshot);
  if (mobile) {
    await card.tap(); await page.waitForTimeout(260); const lifted = await card.evaluate(styleSnapshot);
    await card.tap(); await page.waitForTimeout(260); const restored = await card.evaluate(styleSnapshot);
    await check(`${label}: mobile tap toggle`, () => {assert.notEqual(lifted.transform,original.transform); assert.equal(restored.transform,original.transform); return {original,lifted,restored};});
  } else {
    await card.hover(); await page.waitForTimeout(260);
    await check(`${label}: hover lift`, async () => {const lifted = await card.evaluate(styleSnapshot); assert.notEqual(lifted.transform,original.transform); assert.notEqual(lifted.shadow,original.shadow); return lifted;});
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
async function specimenGeometry(page) {
  const result=await page.locator('.demo-scope[data-interactive]').first().evaluate(scope=>{
    const root=scope.shadowRoot.querySelector('.ds-stage');
    const subject=root.querySelector('.ds-surface,.lift-card,.mini-scroll,.carousel');
    const hint=root.querySelector('.ds-hint');
    const r=root.getBoundingClientRect(),s=subject.getBoundingClientRect(),h=hint.getBoundingClientRect();
    const style=getComputedStyle(root);
    const inner=r.width-parseFloat(style.paddingLeft)-parseFloat(style.paddingRight)-2;
    return {stage:r.width,subject:s.width,ratio:s.width/inner,left:s.left-r.left,right:r.right-s.right,
      hintLeft:h.left-r.left,hintBottom:r.bottom-h.bottom,hintRight:r.right-h.right,clearance:h.top-s.bottom};
  });
  assert.ok(result.left>=15.5&&result.right>=15.5,JSON.stringify(result));
  assert.ok(Math.abs(result.hintLeft-13)<=1.1&&Math.abs(result.hintBottom-13)<=1.1,JSON.stringify(result));
  assert.ok(result.hintRight>=11.5&&result.clearance>=11.5,JSON.stringify(result));
  if(result.stage>=640)assert.ok(result.ratio>=.45&&result.ratio<=.60,JSON.stringify(result));
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
    await scope.locator('.mini-scroll').evaluate(node=>{for(const card of node.querySelectorAll('.ds-reveal-card')){node.scrollTop=card.offsetTop-16;node.dispatchEvent(new Event('scroll'));}});
    await page.waitForTimeout(400);
    assert.equal(await scope.locator('.ds-reveal-card.ds-revealed').count(),3);
  }
  if (route.includes('/grid/')) {
    await scope.locator('[data-guide-mode="1"]').click();
    assert.equal(await scope.locator('.guide-card-stage').getAttribute('data-mode'),'1');
    await scope.locator('[data-guide-mode="0"]').click();
    assert.equal(await scope.locator('.ds-grid-card').count(),6);
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
function catalogInventory() {
  const details = [];
  function walk(directory) {
    for(const entry of fs.readdirSync(directory,{withFileTypes:true})) {
      const file=path.join(directory,entry.name);
      if(entry.isDirectory()) walk(file);
      else if(entry.isFile() && entry.name==='index.html') {
        const source=fs.readFileSync(file,'utf8');
        const count=[...source.matchAll(/<div\b[^>]*class="demo-scope"[^>]*data-interactive\b/g)].length;
        if(count) details.push({route:path.relative(dist,path.dirname(file)).split(path.sep).join('/')+'/',demos:count});
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
  for (const width of [1440,390]) {
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
      });
      await check(`${label}: screenshot`, async () => {
        const file=path.join(shots,`${route.replaceAll('/','-').replace(/-$/,'')}-${width}.png`);
        await page.screenshot({path:file,fullPage:true}); report.screenshots.push(file);
      });
      await check(`${label}: reduced motion`, () => reducedChecks(page,url,label));
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
