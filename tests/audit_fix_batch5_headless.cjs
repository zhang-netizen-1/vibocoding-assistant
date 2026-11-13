/* Optional rendering regressions. Only temporary headless Chromium and local responses. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require('playwright');
const root = path.resolve(__dirname,'../dist');
const origin = 'http://127.0.0.1:4173';
const prefix = '/vibocoding-assistant/';
const types = {'.html':'text/html','.css':'text/css','.js':'text/javascript','.json':'application/json','.svg':'image/svg+xml'};

function inspectShell() {
  const main = document.querySelector('#main');
  const footer = document.querySelector('footer .footer').getBoundingClientRect();
  const mainRect = main.getBoundingClientRect();
  const style = getComputedStyle(main);
  const clipped = [...document.querySelectorAll('.entry-section h2,.criteria summary,.gallery-caption strong,.link-block')]
    .filter(node => node.getClientRects().length && node.scrollWidth > node.clientWidth + 1)
    .map(node => node.textContent);
  return {
    overflow:document.documentElement.scrollWidth > innerWidth + 1,
    footerAligned:Math.abs(footer.left - mainRect.left - parseFloat(style.paddingLeft)) < 1 &&
      Math.abs(footer.right - mainRect.right + parseFloat(style.paddingRight)) < 1,
    clipped,
    headings:[...document.querySelectorAll('.entry-section h2,.use-card h2,.criteria summary,.new-section>summary')]
      .map(node => {
        const css = getComputedStyle(node);
        return [css.fontSize,css.fontWeight,css.lineHeight];
      }),
    labels:[...document.querySelectorAll('.chip,.count,.stat,.title-count,.result-count,.bench-badge')]
      .map(node => {
        const css = getComputedStyle(node);
        return [css.fontSize,css.fontWeight,css.lineHeight];
      }),
    cards:[...document.querySelectorAll('.gallery-caption strong,.layer h3')]
      .map(node => {
        const css = getComputedStyle(node);
        return [css.fontSize,css.fontWeight,css.lineHeight];
      }),
    shortLinks:[...document.querySelectorAll('.link-block')]
      .filter(node => node.getBoundingClientRect().height < 44).map(node => node.textContent)
  };
}

(async () => {
  const browser = await chromium.launch({headless:true});
  const report = [];
  const errors = [];
  try {
    const entries = JSON.parse(fs.readFileSync(path.resolve(__dirname,'../build/entries.json'),'utf8'));
    const destinations = entries.map(entry => `${entry.column}/${entry.column === 'ai' ? 'skills/' : ''}${entry.slug}/`);
    for (const width of [1440,1024,768,390]) {
      const context = await browser.newContext({viewport:{width,height:900},reducedMotion:'reduce'});
      const page = await context.newPage();
      page.on('pageerror',error => errors.push(error.message));
      await page.route('**/*',route => {
        const url = new URL(route.request().url());
        assert.equal(url.origin,origin);
        assert.ok(url.pathname.startsWith(prefix));
        let file = path.resolve(root,decodeURIComponent(url.pathname.slice(prefix.length)));
        assert.ok(file === root || file.startsWith(root + path.sep));
        if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file,'index.html');
        const exists = fs.existsSync(file);
        if (!exists) file = path.join(root,'404.html');
        return route.fulfill({status:exists ? 200 : 404,contentType:types[path.extname(file)],body:fs.readFileSync(file)});
      });
      async function visit(destination) {
        await page.goto(origin + prefix + destination,{waitUntil:'load'});
        const result = await page.evaluate(inspectShell);
        report.push({width,destination,...result});
        assert.equal(result.overflow,false,`${width} ${destination}`);
        assert.equal(result.footerAligned,true,`${width} ${destination}`);
        assert.deepEqual(result.clipped,[],`${width} ${destination}`);
        assert.deepEqual(result.shortLinks,[],`${width} ${destination}`);
        result.headings.forEach(value => assert.deepEqual(value,['22px','600','28.6px']));
        result.labels.forEach(value => assert.deepEqual(value,['13px','500','19.5px']));
        result.cards.forEach(value => assert.deepEqual(value,width <= 760 ? ['14px','600','21px'] : ['16px','600','24px']));
      }
      await visit('');
      const lines = await page.locator('.hero h1').evaluate(node => {
        const walker = document.createTreeWalker(node,NodeFilter.SHOW_TEXT);
        const lines = new Map();
        while (walker.nextNode()) {
          const text = walker.currentNode;
          for (let i = 0; i < text.length; i++) {
            const range = document.createRange();
            range.setStart(text,i); range.setEnd(text,i+1);
            const top = Math.round(range.getBoundingClientRect().top);
            lines.set(top,(lines.get(top) || '') + text.textContent[i]);
          }
        }
        return [...lines.values()];
      });
      assert.ok(lines.at(-1).replace(/[\s。，]/g,'').length > 2,`${width} ${JSON.stringify(lines)}`);
      await visit('ai/prompt-writing/');
      const gaps = await page.locator('.entry-section p + h3').evaluateAll(nodes => nodes.map(node => {
        return node.getBoundingClientRect().top - node.previousElementSibling.getBoundingClientRect().bottom;
      }));
      assert.deepEqual(gaps,[24,24]);
      assert.equal(await page.locator('[data-copy-source=button-edit-example]').evaluate(node => getComputedStyle(node).backgroundColor),'rgb(17, 24, 39)');
      for (const destination of ['basics/','components/','interactions/','scenarios/','ai/',...destinations]) {
        await visit(destination);
        const entry = entries.find(entry => destination === `${entry.column}/${entry.column === 'ai' ? 'skills/' : ''}${entry.slug}/`);
        if (!entry) continue;
        assert.equal(await page.locator('.prompt-card').count(),1);
        assert.equal(await page.locator('.prompt-card #entry-prompt').textContent(),entry.prompt);
        assert.equal(await page.locator('.entry-main .prompt-box').count(),0);
        const notice = page.locator('.prompt-card .prompt-meta');
        assert.equal(await notice.count(),Number(entry.acceptance.length > 0));
        if (entry.acceptance.length) assert.equal(await notice.textContent(),`复制时自动附带 ${entry.acceptance.length} 条验收要求`);
        const payload = await page.locator('#copy-prompt').textContent();
        for (const criterion of entry.acceptance) assert.ok(payload.includes(criterion));
        const geometry = await page.locator('.prompt-card').evaluate(card => {
          const button = card.querySelector('.prompt-head button').getBoundingClientRect();
          const rect = card.getBoundingClientRect();
          const demos = [...document.querySelectorAll('.entry-main > .entry-demo')];
          return {position:getComputedStyle(card).position,height:rect.height,
            viewport:innerHeight,top:rect.top,
            afterDemo:demos.every(demo => demo.getBoundingClientRect().bottom <= rect.top + 1),
            beforeMotion:[...document.querySelectorAll('.motion-section,.usage-section')]
              .every(section => section.getBoundingClientRect().top >= rect.bottom - 1),
            buttonWidth:button.width,buttonHeight:button.height,
            overscroll:getComputedStyle(card.querySelector('.prompt-body')).overscrollBehavior};
        });
        assert.ok(geometry.buttonWidth >= 44 && geometry.buttonHeight >= 44);
        assert.equal(geometry.overscroll,'contain');
        if (width >= 1024) {
          assert.equal(geometry.position,'fixed');
          assert.ok(geometry.height + geometry.top <= geometry.viewport);
        } else {
          assert.equal(geometry.position,'static');
          assert.equal(geometry.afterDemo,true);
          assert.equal(geometry.beforeMotion,true);
        }
      }
      // Shared card feedback and real viewport-driven keyboard exclusion.
      await visit('components/cmdk/');
      await page.evaluate(() => Object.defineProperty(navigator,'clipboard',{configurable:true,
        value:{writeText:async text => {window.__promptCopiedText = text;}}}));
      await page.locator('.prompt-head [data-copy-source="copy-prompt"]').click();
      assert.equal(await page.locator('.prompt-card').evaluate(card => getComputedStyle(card).backgroundColor),'rgb(109, 40, 217)');
      assert.equal(await page.locator('.prompt-card').evaluate(card => getComputedStyle(card).color),'rgb(255, 255, 255)');
      assert.equal(await page.locator('.prompt-head button').textContent(),'✓ 已复制');
      assert.equal(await page.locator('.prompt-head button').evaluate(button => getComputedStyle(button).backgroundColor),'rgb(255, 255, 255)');
      assert.equal(await page.locator('.prompt-card').evaluate(card => getComputedStyle(card).transitionDuration),'0s');
      assert.equal(await page.evaluate(() => window.__promptCopiedText === document.querySelector('#copy-prompt').textContent),true);
      await page.waitForFunction(() => document.querySelector('#live').textContent === '已复制');
      await page.waitForFunction(() => !document.querySelector('.prompt-card').classList.contains('is-copied'));
      assert.equal(await page.locator('.prompt-head button').textContent(),'复制');
      if (width <= 1023) {
        await page.locator('.prompt-card').scrollIntoViewIfNeeded();
        await page.waitForFunction(() => document.querySelector('.bottom-bar').hidden);
        assert.equal(await page.locator('.bottom-bar').evaluate(bar => bar.inert),true);
        await page.evaluate(() => scrollTo(0,document.documentElement.scrollHeight));
        await page.waitForFunction(() => !document.querySelector('.bottom-bar').hidden);
        assert.equal(await page.locator('.bottom-bar').evaluate(bar => bar.inert),false);
      }
      for (const missing of ['missing','a/b/c/missing/','components/missing/index.html']) {
        await visit(missing);
        await page.locator('[data-search]').click();
        await page.locator('#search-input').fill('按钮');
        await page.waitForFunction(() => document.querySelector('.result-name')?.textContent === '按钮');
        assert.equal(await page.locator('.result-name').first().getAttribute('href'),prefix + 'components/button/');
        await page.locator('.result-name').first().click();
        await page.waitForURL(origin + prefix + 'components/button/');
      }
      await context.close();
    }
    assert.deepEqual(errors,[]);
    console.log(`第 5 批无界面检查通过，共 ${report.length} 个页面与尺寸组合。`);
  } finally {
    const output = path.resolve(__dirname,'../output/playwright');
    fs.mkdirSync(output,{recursive:true});
    fs.writeFileSync(path.join(output,'audit-fix-batch5.json'),JSON.stringify({report,errors},null,2));
    await browser.close();
  }
})().catch(error => {console.error(error);process.exitCode = 1;});
