/* Optional rendering regression. Uses only a temporary headless Chromium and
   local route fulfillment under the deployed subpath, with no outside requests. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require('playwright');
const root = path.resolve(__dirname,'../dist');
const origin = 'http://127.0.0.1:4173', prefix = '/vibocoding-assistant/';
const types = {'.html':'text/html','.css':'text/css','.js':'text/javascript','.json':'application/json','.svg':'image/svg+xml'};

(async () => {
  const browser = await chromium.launch({headless:true});
  try {
    const page = await browser.newPage({viewport:{width:1440,height:900},reducedMotion:'reduce'});
    const errors = [];
    page.on('pageerror',error => errors.push(error.message));
    await page.route('**/*',route => {
      const url = new URL(route.request().url());
      assert.equal(url.origin,origin); assert.ok(url.pathname.startsWith(prefix));
      let file = path.resolve(root,decodeURIComponent(url.pathname.slice(prefix.length)));
      assert.ok(file.startsWith(root + path.sep));
      if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file,'index.html');
      return route.fulfill({status:fs.existsSync(file) ? 200 : 404,
        contentType:types[path.extname(file)] || 'application/octet-stream',
        body:fs.existsSync(file) ? fs.readFileSync(file) : ''});
    });
    async function visit(destination) {
      await page.goto(origin + prefix + destination,{waitUntil:'networkidle'});
      await page.waitForFunction(() => [...document.querySelectorAll('.demo-scope')].every(scope => scope.shadowRoot));
    }
    async function choose(state) { await page.locator(`[data-state="${state}"]`).click(); }
    const slugs = ['button','input','textarea','select','search','checkbox','radio','switch','slider','tabs'];
    for (const slug of slugs) {
      await visit('components/' + slug + '/');
      await choose('disabled');
      const controls = await page.locator('.entry-demo .demo-scope').first().evaluate(scope =>
        [...scope.shadowRoot.querySelectorAll('button,input,select,textarea')].map(node => ({disabled:node.disabled})));
      assert.ok(slug === 'tabs' ? controls.at(-1).disabled && !controls[0].disabled : controls.every(node => node.disabled),slug);
      if (slug === 'tabs') {
        await page.locator('#tab-intro').focus();
        await page.locator('#tab-intro').press('End');
        assert.equal(await page.locator('#tab-reviews').getAttribute('aria-selected'),'true');
      }
      await choose('free');
      assert.equal(await page.locator('.entry-demo .demo-scope').first().evaluate(scope =>
        [...scope.shadowRoot.querySelectorAll('button,input,select,textarea')].some(node => node.disabled)),false);
      if (slug === 'button') {
        const widths = await page.locator('.entry-demo .btn').evaluateAll(nodes => nodes.map(node => node.getBoundingClientRect().width));
        await choose('loading');
        const loading = await page.locator('.entry-demo .btn').evaluateAll(nodes => nodes.map(node => ({
          width:node.getBoundingClientRect().width,label:node.textContent,busy:node.getAttribute('aria-busy'),disabled:node.disabled,
          spin:getComputedStyle(node.querySelector('.demo-loading-icon')).animationName
        })));
        loading.forEach((node,index) => {
          assert.ok(Math.abs(node.width - widths[index]) < 1); assert.ok(node.disabled);
          assert.equal(node.busy,'true'); assert.match(node.label,/提交中…/); assert.equal(node.spin,'none');
        });
      }
      if (['input','textarea','select','search'].includes(slug)) {
        await choose('error');
        const errors = await page.locator('.entry-demo .demo-scope').first().evaluate(scope =>
          [...scope.shadowRoot.querySelectorAll('[aria-invalid="true"]')].map(field => {
            const error = scope.shadowRoot.getElementById(field.getAttribute('aria-describedby').split(' ').at(-1));
            return {size:parseFloat(getComputedStyle(error).fontSize),text:error.textContent};
          }));
        assert.ok(errors.length); assert.ok(errors.every(error => error.size >= 12 && error.text.length));
      }
    }
    await visit('interactions/component-lift/');
    assert.equal(await page.locator('.reduced-note').first().isVisible(),true);
    assert.equal(await page.locator('[data-demo-motion-once]').count(),0);
    await page.locator('[data-demo-replay]').first().click();
    const duration = await page.locator('.micro-card').first().evaluate(node => getComputedStyle(node).transitionDuration);
    assert.ok(duration.split(',').some(value => parseFloat(value) > .00001),duration);
    assert.equal(await page.locator('[data-demo-motion-once]').count(),1);
    await page.waitForFunction(() => !document.querySelector('[data-demo-motion-once]'));
    await page.locator('[data-demo-slow]').first().click();
    assert.equal(await page.locator('[data-demo-motion-once]').count(),1);
    await visit('interactions/');
    const play = page.locator('.gallery-card').filter({has:page.locator('[data-demo-key="component-lift"]')}).locator('.play-button');
    await play.click(); assert.equal(await page.locator('[data-demo-motion-once]').count(),1);
    await visit('interactions/background-aurora/');
    await page.locator('[data-demo-step]').click();
    const firstPhase = await page.locator('.aurora').evaluate(node => getComputedStyle(node).backgroundPosition);
    await page.waitForTimeout(150);
    assert.equal(await page.locator('.aurora').evaluate(node => getComputedStyle(node).backgroundPosition),firstPhase);
    await page.locator('[data-demo-step]').click();
    assert.notEqual(await page.locator('.aurora').evaluate(node => getComputedStyle(node).backgroundPosition),firstPhase);
    assert.equal(await page.locator('[data-demo-motion-once]').count(),0);

    // Include the reported page and the smallest generated entry documents.
    const entries = JSON.parse(fs.readFileSync(path.resolve(__dirname,'../build/entries.json'),'utf8'));
    const destinations = entries.map(entry => `${entry.column}/${entry.column === 'ai' ? 'skills/' : ''}${entry.slug}/`);
    destinations.sort((a,b) => fs.statSync(path.join(root,a,'index.html')).size - fs.statSync(path.join(root,b,'index.html')).size);
    for (const destination of ['interactions/component-lift/',...destinations.slice(0,5)]) {
      await visit(destination);
      const details = page.locator('.use-card .criteria');
      if (await details.count()) await details.evaluate(node => {node.open = true; node.scrollTop = node.scrollHeight;});
      for (const fraction of [0,.5,1]) {
        await page.evaluate(value => scrollTo(0,(document.documentElement.scrollHeight-innerHeight)*value),fraction);
        const result = await page.locator('.use-card > .btn-primary').evaluate(button => {
          const r = button.getBoundingClientRect();
          const hit = document.elementFromPoint(r.left + r.width/2,r.top + r.height/2);
          return {top:r.top,bottom:r.bottom,viewport:innerHeight,header:document.querySelector('#header').getBoundingClientRect().bottom,
            clickable:hit === button || button.contains(hit)};
        });
        assert.ok(result.top >= result.header && result.bottom <= result.viewport && result.clickable,
          destination + ' ' + JSON.stringify(result));
      }
    }
    assert.deepEqual(errors,[]);
    console.log('Headless states, reduced-motion deliberate playback and copy-card hit tests passed.');
  } finally { await browser.close(); }
})().catch(error => {console.error(error);process.exitCode = 1;});
