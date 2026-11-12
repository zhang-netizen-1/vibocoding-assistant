/* Optional browser verification: temporary headless Chromium, local files only.
   Run after build_site.py; no server, user profile or desktop browser required. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require('playwright');
const root = path.resolve(__dirname,'../dist');
const output = path.resolve(__dirname,'../output/playwright');
const origin = 'http://127.0.0.1:4173', prefix = '/vibocoding-assistant/';
const types = {'.html':'text/html','.css':'text/css','.js':'text/javascript','.json':'application/json','.svg':'image/svg+xml'};

// Inspect real text nodes, including Shadow DOM. Invisible animation layers and
// inert templates are not readable text; scrollable content is not truncation.
function inspect() {
  const small = [], clipped = [], targets = [], overlaps = [];
  let texts = 0;
  const visible = node => {
    if (!node.getClientRects().length) return false;
    for (let parent = node; parent; parent = parent.parentElement || parent.getRootNode().host) {
      const style = getComputedStyle(parent);
      if (style.visibility === 'hidden' || style.display === 'none' || Number(style.opacity) === 0) return false;
    }
    return true;
  };
  function scan(rootNode, demo = false, interactive = true) {
    const controls = [];
    for (const node of rootNode.querySelectorAll('*')) {
      if (node.shadowRoot) scan(node.shadowRoot,true,node.hasAttribute('data-interactive'));
      if (!visible(node)) continue;
      if (interactive && node.matches('a,button,summary') && (!node.closest('p') || node.matches('.drawer-body>p>a')) && !node.matches('.skip')) {
        const r = node.getBoundingClientRect();
        const record = {label:node.textContent.trim().slice(0,50) || node.getAttribute('aria-label'),height:r.height};
        if (r.height < 43.9) targets.push(record);
        controls.push({node,r,record});
      }
      if (!demo || node.matches('script,style,template')) continue;
      for (const text of node.childNodes) {
        if (text.nodeType !== Node.TEXT_NODE || !text.textContent.trim()) continue;
        const range = document.createRange(); range.selectNodeContents(text);
        if (![...range.getClientRects()].some(r => r.width && r.height)) continue;
        texts++;
        const label = text.textContent.trim().slice(0,80), size = parseFloat(getComputedStyle(node).fontSize);
        if (size < 12) small.push({label,size});
        // Focus clipping assertions on the reported fixed cards. Scrolling,
        // animated masks, transformed scenes and ellipsis studies are deliberate.
        const card = node.closest('.scene-stack,.scene-slide,.scene-curtain,.micro-card');
        if (card) {
          const r = range.getBoundingClientRect(), box = card.getBoundingClientRect();
          if (r.left < box.left-1 || r.right > box.right+1 || r.top < box.top-1 || r.bottom > box.bottom+1)
            clipped.push({label,card:card.className});
        }
      }
    }
    for (let i = 0; i < controls.length; i++) for (const b of controls.slice(i+1)) {
      const a = controls[i];
      if (a.node.parentElement !== b.node.parentElement || a.node.contains(b.node) || b.node.contains(a.node)) continue;
      const width = Math.min(a.r.right,b.r.right)-Math.max(a.r.left,b.r.left);
      const height = Math.min(a.r.bottom,b.r.bottom)-Math.max(a.r.top,b.r.top);
      if (width > 1 && height > 1) overlaps.push([a.record.label,b.record.label]);
    }
  }
  scan(document);
  return {texts,small,clipped,targets,overlaps,horizontalOverflow:document.documentElement.scrollWidth > innerWidth+1};
}

(async () => {
  const browser = await chromium.launch({headless:true});
  fs.mkdirSync(output,{recursive:true});
  const report = {checks:[],errors:[],smallTextCount:0,textCount:0};
  try {
    const entries = JSON.parse(fs.readFileSync(path.resolve(__dirname,'../build/entries.json'),'utf8'));
    const destinations = entries.map(e => `${e.column}/${e.column === 'ai' ? 'skills/' : ''}${e.slug}/`);
    for (const mode of [{width:390,touch:true},{width:768,touch:true},{width:1023,touch:true},
                        {width:1024,touch:false},{width:1440,touch:false},{width:1440,touch:true}]) {
      const context = await browser.newContext({viewport:{width:mode.width,height:900},hasTouch:mode.touch,reducedMotion:'reduce'});
      const page = await context.newPage();
      page.on('pageerror',error => report.errors.push(error.message));
      await page.route('**/*',route => {
        const url = new URL(route.request().url());
        assert.equal(url.origin,origin);assert.ok(url.pathname.startsWith(prefix));
        let file = path.resolve(root,decodeURIComponent(url.pathname.slice(prefix.length)));
        if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file,'index.html');
        assert.ok(file.startsWith(root+path.sep));
        return route.fulfill({status:fs.existsSync(file)?200:404,contentType:types[path.extname(file)] || 'application/octet-stream',
          body:fs.existsSync(file)?fs.readFileSync(file):''});
      });
      async function visit(destination) {
        await page.goto(origin+prefix+destination,{waitUntil:'networkidle'});
        await page.waitForFunction(() => [...document.querySelectorAll('.demo-scope')].every(scope =>
          scope.shadowRoot && [...scope.shadowRoot.querySelectorAll('link[rel=stylesheet]')].every(link => link.sheet)));
      }
      async function record(destination,phase = 'idle') {
        const result = await page.evaluate(inspect);
        if (!mode.touch && mode.width >= 1024) {result.targets = [];result.overlaps = [];}
        report.textCount += result.texts;report.smallTextCount += result.small.length;
        report.checks.push({mode,destination,phase,...result});
      }
      await visit('');
      const compact = mode.width < 1024;
      assert.equal(await page.locator('.desktop-nav').isVisible(),!compact);
      assert.equal(await page.locator('#directory-toggle').isVisible(),compact);
      if (compact) {
        assert.ok((await page.locator('#header').boundingBox()).height <= 64);
        await page.locator('#directory-toggle').click();
        assert.equal(await page.locator('#directory').isVisible(),true);
        await page.locator('.drawer-category summary').first().click();
        await record('','drawer');
        await page.locator('[data-close=directory]').click();
        assert.equal(await page.locator('#directory-toggle').evaluate(node => node === document.activeElement),true);
      }
      assert.equal(await page.locator('.home-search .shortcut-hint').isVisible(),!compact && !mode.touch);
      await page.locator('#nav-search').click();
      assert.equal(await page.locator('.search-help').isVisible(),!compact && !mode.touch);
      await page.locator('#search-input').fill('按扭');
      await page.waitForFunction(() => document.querySelector('#search-body').textContent.includes('按钮'));
      assert.match(await page.locator('#search-body').innerText(),/相近的名称/);
      await record('','search');
      await page.locator('[data-close=search-dialog]').click();
      // All five galleries and all 192 entries, at every requested device mode.
      for (const destination of ['basics/','components/','interactions/','scenarios/','ai/',...destinations]) {
        await visit(destination);await record(destination);
        const states = await page.locator('[data-state]').evaluateAll(nodes => nodes.map(node => node.dataset.state));
        for (const state of states) {
          await page.locator(`[data-state="${state}"]`).click();await record(destination,state);
        }
        if (compact && mode.width === 390 && ['interactions/view-crossfade/','interactions/view-slide/',
            'interactions/view-curtain/','components/button/'].includes(destination))
          await page.screenshot({path:path.join(output,destination.replaceAll('/','-')+'390.png'),fullPage:true});
        if (destination === 'interactions/') {
          const play = page.locator('.play-button').first();
          await play.scrollIntoViewIfNeeded();
          const hit = await play.evaluate(node => {
            const r = node.getBoundingClientRect();return document.elementFromPoint(r.x+r.width/2,r.y+r.height/2) === node;
          });
          assert.equal(hit,true,'Play target must stay above the stretched entry link');
          const zoom = await page.locator('.mini-stage .demo-root').first().evaluate(node => Number(getComputedStyle(node).zoom));
          assert.equal(zoom,1.35);
        }
      }
      await context.close();
    }
    fs.writeFileSync(path.join(output,'audit-fix-batch4.json'),JSON.stringify(report,null,2));
    assert.deepEqual(report.errors,[]);
    const failures = report.checks.filter(row => row.small.length || row.clipped.length || row.targets.length || row.overlaps.length || row.horizontalOverflow);
    assert.deepEqual(failures,[],`See ${path.join(output,'audit-fix-batch4.json')}`);
    console.log(`检查 ${report.checks.length} 个页面/状态，${report.textCount} 段文字，小于 12px：${report.smallTextCount}。`);
  } finally {
    fs.writeFileSync(path.join(output,'audit-fix-batch4.json'),JSON.stringify(report,null,2));
    await browser.close();
  }
})().catch(error => {console.error(error);process.exitCode = 1;});
