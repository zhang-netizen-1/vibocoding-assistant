/* Focused batch-six rendering checks. Temporary headless Chromium and local
   route fulfillment only, with every request confined to the deployment path. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require('playwright');
const root = path.resolve(__dirname,'../dist');
const origin = 'http://127.0.0.1:4173', prefix = '/vibocoding-assistant/';
const types = {'.html':'text/html','.css':'text/css','.js':'text/javascript','.json':'application/json','.svg':'image/svg+xml'};
const miniLabels = ['.mini-layout-top','.mini-layout-heading small','.mini-layout-main p','.mini-layout-tail',
  '.mini-layout-bottom','.mini-interaction p:not([data-error="true"])','.mini-task span','.mini-page-top',
  '.mini-page-foot','.mini-page-hero small','.mini-page-metrics small','.mini-page-search','.mini-page-field',
  '.mini-page-list span','.mini-page-settings span','.mini-page-steps small','.mini-data-title','.mini-data p'].join(',');

function contrastRows(scope, selectors) {
  const channels = color => color.match(/[\d.]+/g).map(Number);
  function background(node) {
    let result = [0,0,0,0];
    for (let parent=node;parent;parent=parent.parentElement || parent.getRootNode().host) {
      const color = channels(getComputedStyle(parent).backgroundColor);
      const alpha = color[3] ?? 1;
      for (let i=0;i<3;i++) result[i] += (1-result[3])*alpha*color[i];
      result[3] += (1-result[3])*alpha;
      if (result[3] >= .999) return result.slice(0,3);
    }
    return result.slice(0,3).map(value => value+(1-result[3])*255);
  }
  function luminance(rgb) {
    const linear = rgb.slice(0,3).map(value => value/255).map(value =>
      value <= .04045 ? value/12.92 : ((value+.055)/1.055)**2.4);
    return linear[0]*.2126+linear[1]*.7152+linear[2]*.0722;
  }
  return [...scope.shadowRoot.querySelectorAll(selectors)].filter(node => {
    const style = getComputedStyle(node);
    return node.getClientRects().length && style.visibility !== 'hidden' && Number(style.opacity)>0;
  }).map(node => {
    const foreground = channels(getComputedStyle(node).color), bg = background(node);
    const a=luminance(foreground), b=luminance(bg);
    return {text:node.textContent.trim(),color:foreground,background:bg,ratio:(Math.max(a,b)+.05)/(Math.min(a,b)+.05)};
  });
}

(async () => {
  const browser = await chromium.launch({headless:true});
  const report = {gallery:[],hover:[],contrast:[]}, errors = [];
  try {
    const page = await browser.newPage({viewport:{width:1440,height:900},reducedMotion:'reduce'});
    page.on('pageerror',error => errors.push(error.message));
    await page.route('**/*',route => {
      const url = new URL(route.request().url());
      assert.equal(url.origin,origin);assert.ok(url.pathname.startsWith(prefix));
      let file = path.resolve(root,decodeURIComponent(url.pathname.slice(prefix.length)));
      assert.ok(file.startsWith(root+path.sep));
      if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file=path.join(file,'index.html');
      assert.ok(fs.existsSync(file),file);
      return route.fulfill({contentType:types[path.extname(file)] || 'application/octet-stream',body:fs.readFileSync(file)});
    });
    async function visit(destination) {
      await page.goto(origin+prefix+destination,{waitUntil:'networkidle'});
      await page.waitForFunction(() => [...document.querySelectorAll('.demo-scope')].every(scope =>
        scope.shadowRoot && [...scope.shadowRoot.querySelectorAll('link[rel=stylesheet]')].every(link => link.sheet)));
    }
    async function checkContrast(selectors) {
      const rows = await page.locator('.demo-scope').evaluateAll((scopes,selectors) => {
        // The helper is installed by addScriptTag below, scoped to this test page.
        return scopes.flatMap(scope => window.batch6Contrast(scope,selectors));
      },selectors);
      assert.ok(rows.length,selectors);
      for (const row of rows) assert.ok(row.ratio >= 4.5,JSON.stringify(row));
      report.contrast.push(...rows);
    }
    async function installContrastHelper() {
      await page.addScriptTag({content:`window.batch6Contrast = ${contrastRows.toString()}`});
    }
    async function checkHover(scope) {
      await page.waitForFunction(() => [...document.querySelectorAll('.demo-scope')].some(scope => {
        const popup=scope.shadowRoot?.querySelector('.hvp-pop');
        return popup && Number(getComputedStyle(popup).opacity)>.99;
      }));
      const row = await scope.evaluate(scope => {
        const popup=scope.shadowRoot.querySelector('.hvp-pop'), box=popup.getBoundingClientRect();
        const containers=[popup.closest('.stage'),scope.shadowRoot.querySelector('.demo-root'),scope.closest('.mini-stage')].filter(Boolean);
        return {text:popup.textContent,inside:containers.every(node => {
          const r=node.getBoundingClientRect();
          return box.left >= r.left-1 && box.right <= r.right+1 && box.top >= r.top-1 && box.bottom <= r.bottom-16;
        })};
      });
      assert.equal(row.inside,true,JSON.stringify(row));report.hover.push(row);
    }
    for (const width of [1440,768,390]) {
      await page.setViewportSize({width,height:900});
      for (const column of ['basics','components','interactions','scenarios','ai']) {
        await visit(column+'/');
        const cells = await page.locator('.mini-stage .demo-scope').evaluateAll(scopes => scopes.map(scope => {
          const stage=scope.closest('.mini-stage').getBoundingClientRect();
          const content=scope.shadowRoot.querySelector('.demo-root').getBoundingClientRect();
          return {key:scope.dataset.demoKey,ratio:content.width/stage.width,inside:content.left >= stage.left-1 &&
            content.right <= stage.right+1 && content.top >= stage.top-1 && content.bottom <= stage.bottom+1};
        }));
        assert.ok(cells.length);
        for (const cell of cells) assert.equal(cell.inside,true,JSON.stringify({width,column,...cell}));
        if (column==='interactions') {
          assert.ok(cells[0].ratio >= .85,JSON.stringify(cells[0]));
          const card=page.locator('.gallery-card[data-demo-key="component-hover-preview"]'), play=card.locator('.play-button');
          await play.scrollIntoViewIfNeeded();
          assert.equal(await play.evaluate(node => {
            const r=node.getBoundingClientRect();return document.elementFromPoint(r.x+r.width/2,r.y+r.height/2)===node;
          }),true);
          await play.click();await checkHover(card.locator('.demo-scope'));
        }
        report.gallery.push({width,column,cells});
        await installContrastHelper();
        if (column==='ai') await checkContrast('.skill-card dt');
        if (['basics','components','scenarios'].includes(column)) await checkContrast(miniLabels);
      }
      for (const destination of ['interactions/component-hover-preview/','components/card/']) {
        await visit(destination);
        const scope=page.locator('.demo-scope[data-demo-key="component-hover-preview"]');
        if (destination==='components/card/') {
          await page.locator('.gallery-card[data-demo-key="component-hover-preview"] .play-button').click();
        } else {
          await scope.locator('.hvp-link').hover();
        }
        await checkHover(scope);
      }
      for (const [slug,selector] of [['input','.fflabel'],['textarea','#taCountNum'],['chip','.chip button']]) {
        await visit('components/'+slug+'/');await installContrastHelper();await checkContrast(selector);
      }
    }
    assert.deepEqual(errors,[]);
    console.log(JSON.stringify({galleryPages:report.gallery.length,hoverCards:report.hover.length,
      contrastLabels:report.contrast.length,minContrast:Math.min(...report.contrast.map(row => row.ratio))},null,2));
  } finally {
    await browser.close();
  }
})().catch(error => {console.error(error);process.exitCode=1;});
