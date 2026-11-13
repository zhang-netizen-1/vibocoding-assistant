/* Executor-only rendering checks. Uses temporary headless Chromium and route
   fulfillment from dist. No server, listening port or user browser profile. */
'use strict';
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '../dist');
const origin = 'https://design-system.test';
const prefix = '/vibocoding-assistant/';
const types = {'.html':'text/html', '.css':'text/css', '.js':'text/javascript',
  '.json':'application/json', '.svg':'image/svg+xml', '.webp':'image/webp',
  '.jpg':'image/jpeg', '.png':'image/png', '.woff2':'font/woff2'};

function inspectPage() {
  const smallText = [], smallTargets = [], overflowNodes = [];
  function visible(node) {
    if (!node.getClientRects().length) return false;
    for (let parent = node; parent; parent = parent.parentElement || parent.getRootNode().host) {
      const css = getComputedStyle(parent);
      if (css.display === 'none' || css.visibility === 'hidden' || Number(css.opacity) === 0 || parent.matches('.sr,.skip')) return false;
    }
    return true;
  }
  function scan(scope, inert = false) {
    for (const node of scope.querySelectorAll('*')) {
      if (node.matches('script,style,template,link')) continue;
      const passive = inert || Boolean(node.closest('[inert]'));
      if (node.shadowRoot) scan(node.shadowRoot, passive);
      if (!visible(node)) continue;
      const rect = node.getBoundingClientRect();
      if (rect.right > innerWidth + 1 || rect.left < -1) overflowNodes.push(node.className || node.tagName);
      if (!passive && node.matches('a[href],button,input,select,textarea,summary,[role="button"]')) {
        if (rect.height < 43.9 || rect.width < 43.9) {
          smallTargets.push({label:node.textContent.trim().slice(0,60) || node.getAttribute('aria-label'),
            width:rect.width, height:rect.height});
        }
      }
      for (const child of node.childNodes) {
        if (child.nodeType !== Node.TEXT_NODE || !child.textContent.trim()) continue;
        const range = document.createRange();
        range.selectNodeContents(child);
        if (![...range.getClientRects()].some(box => box.width && box.height)) continue;
        const size = parseFloat(getComputedStyle(node).fontSize);
        if (size < 12) smallText.push({text:child.textContent.trim().slice(0,60), size});
      }
    }
  }
  scan(document);
  return {overflow:document.documentElement.scrollWidth > innerWidth + 1,
    overflowNodes, smallText, smallTargets};
}

function runningAnimations() {
  const roots = [document];
  for (let index = 0; index < roots.length; index++) {
    for (const node of roots[index].querySelectorAll('*')) if (node.shadowRoot) roots.push(node.shadowRoot);
  }
  return roots.flatMap(scope => scope.getAnimations().filter(animation =>
    animation.playState === 'running' || animation.playState === 'pending').map(animation => ({
    target:animation.effect?.target?.className, timing:animation.effect?.getTiming()
  })));
}

(async () => {
  const browser = await chromium.launch({headless:true});
  const report = [], errors = [], failedRequests = [];
  try {
    for (const width of [1440, 768, 390]) {
      for (const reducedMotion of ['no-preference', 'reduce']) {
        const context = await browser.newContext({viewport:{width,height:960},hasTouch:true,
          isMobile:width === 390,reducedMotion,serviceWorkers:'block'});
        try {
          const page = await context.newPage();
          page.on('pageerror', error => errors.push({width,reducedMotion,message:error.message}));
          page.on('requestfailed', request => failedRequests.push({url:request.url(),failure:request.failure()}));
          page.on('response', response => {
            if (response.status() >= 400) failedRequests.push({url:response.url(),status:response.status()});
          });
          await page.route('**/*', async route => {
            const url = new URL(route.request().url());
            assert.equal(url.origin, origin, '所有请求必须由本地 dist 提供');
            assert.ok(url.pathname.startsWith(prefix));
            let file = path.resolve(root, decodeURIComponent(url.pathname.slice(prefix.length)));
            assert.ok(file === root || file.startsWith(root + path.sep));
            if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
            const exists = fs.existsSync(file) && fs.statSync(file).isFile();
            await route.fulfill({status:exists ? 200 : 404,
              contentType:types[path.extname(file)] || 'application/octet-stream',
              body:exists ? fs.readFileSync(file) : Buffer.from('Missing local file')});
          });
          await page.goto(origin + prefix + 'design-system/', {waitUntil:'networkidle'});
          await page.waitForFunction(() => [...document.querySelectorAll('.demo-scope')].every(scope =>
            scope.shadowRoot && [...scope.shadowRoot.querySelectorAll('link[rel="stylesheet"]')].every(link => link.sheet)));
          const baseline = await page.evaluate(inspectPage);
          assert.equal(baseline.overflow, false, `${width} 页面横向溢出`);
          assert.deepEqual(baseline.overflowNodes, [], `${width} 元素越出视口`);
          assert.deepEqual(baseline.smallText, [], `${width} 字号小于 12px`);
          assert.deepEqual(baseline.smallTargets, [], `${width} 点击区小于 44×44px`);
          assert.equal(await page.locator('.ds-toc').evaluate(node => getComputedStyle(node).position), width >= 1024 ? 'sticky' : 'static');

          // Open the variable inventories so their real text participates too.
          for (const summary of await page.locator('.ds-inventory summary').all()) await summary.click();
          const expanded = await page.evaluate(inspectPage);
          assert.equal(expanded.overflow, false);
          assert.deepEqual(expanded.smallText, []);
          assert.deepEqual(expanded.smallTargets, []);
          for (const summary of await page.locator('.ds-inventory summary').all()) await summary.click();

          // Search specimen must invoke the same global search dialog.
          await page.locator('.ds-page .home-search').click();
          await page.locator('#search-input').fill('按钮');
          await page.waitForFunction(() => document.querySelector('.result-name')?.textContent.includes('按钮'));
          await page.locator('[data-close="search-dialog"]').click();

          // Playwright pierces the embedded component's open ShadowRoot.
          const live = page.locator('#design-system-live-demo');
          await live.locator('button[data-cmd="toast"]').first().click();
          await page.waitForFunction(() => document.querySelector('#design-system-live-demo .demo-scope')
            .shadowRoot.querySelector('.demo-status')?.textContent.trim());
          const feedback = await live.locator('.demo-status').textContent();
          assert.ok(feedback.trim(), '真实演示应产生操作反馈');

          // Each duration and each curve must have an independently working play action.
          const cards = page.locator('.ds-motion-card');
          assert.equal(await cards.count(), 9);
          for (const card of await cards.all()) {
            const count = Number(await card.getAttribute('data-play-count') || 0);
            await card.locator('.ds-motion-play').click();
            assert.ok(Number(await card.getAttribute('data-play-count')) > count);
            if (reducedMotion === 'reduce') {
              assert.equal(await card.locator('.ds-motion-status').textContent(), '已到终点');
              assert.equal(await card.locator('.ds-motion-box').evaluate(node => node.getAnimations().length), 0);
            } else {
              await page.waitForFunction(node => node.querySelector('.ds-motion-status').textContent === '播放完成', await card.elementHandle());
            }
            const endpoint = await card.evaluate(node => {
              const track = node.querySelector('.ds-motion-track').getBoundingClientRect();
              const box = node.querySelector('.ds-motion-box').getBoundingClientRect();
              return Math.abs(track.right - box.right) < 1;
            });
            assert.ok(endpoint, '播放完成后方块应停在轨道终点');
          }

          // The static stage keeps all four subject insets and the bottom capsule.
          const insets = await page.locator('.ds-stage-diagram').evaluate(node => {
            const stage = node.getBoundingClientRect(), subject = node.querySelector('.ds-stage-surface').getBoundingClientRect();
            return [subject.left-stage.left,stage.right-subject.right,subject.top-stage.top,stage.bottom-subject.bottom];
          });
          assert.ok(insets.every(value => value >= 16), `${width} 舞台主体安全间距`);
          const final = await page.evaluate(inspectPage);
          assert.equal(final.overflow, false);
          assert.deepEqual(final.smallTargets, []);
          assert.deepEqual(final.smallText, []);
          if (reducedMotion === 'reduce') assert.deepEqual(await page.evaluate(runningAnimations), []);
          report.push({width,reducedMotion,baseline,expanded,final,insets,feedback});
        } finally {
          await context.close();
        }
      }
    }

    // Pointer hover remains a separate entry point on a mouse-capable context.
    const mouseContext = await browser.newContext({viewport:{width:1440,height:960}});
    try {
      const mousePage = await mouseContext.newPage();
      mousePage.on('pageerror', error => errors.push({mode:'mouse',message:error.message}));
      mousePage.on('requestfailed', request => failedRequests.push({url:request.url(),failure:request.failure()}));
      await mousePage.route('**/*', route => {
        const url = new URL(route.request().url());
        assert.equal(url.origin, origin);
        assert.ok(url.pathname.startsWith(prefix));
        let file = path.resolve(root, decodeURIComponent(url.pathname.slice(prefix.length)));
        assert.ok(file === root || file.startsWith(root + path.sep));
        if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
        assert.ok(fs.existsSync(file), file);
        return route.fulfill({contentType:types[path.extname(file)] || 'application/octet-stream',body:fs.readFileSync(file)});
      });
      await mousePage.goto(origin + prefix + 'design-system/', {waitUntil:'networkidle'});
      const sample = mousePage.locator('.ds-motion-card').first();
      await sample.hover();
      assert.ok(Number(await sample.getAttribute('data-play-count')) >= 1, '鼠标悬停应触发播放');
    } finally {
      await mouseContext.close();
    }
    assert.deepEqual(errors, [], '页面 JavaScript 错误');
    assert.deepEqual(failedRequests, [], '失败请求');
    console.log(`设计系统无界面检查通过，共 ${report.length} 个尺寸与动态偏好组合，含鼠标悬停。`);
  } finally {
    await browser.close();
  }
})().catch(error => { console.error(error); process.exitCode = 1; });
