/* Run with an installed playwright module. Uses an ephemeral headless browser
   and locally fulfilled HTTP requests under the deployment subpath. */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const {chromium} = require('playwright');
const root = path.resolve(__dirname, '../dist');
const prefix = '/vibocoding-assistant/';
const widths = [1440, 1024, 768, 390];
const viewSlugs = ['view-crossfade', 'view-slide', 'view-curtain', 'view-shared', 'view-stagger'];
const types = {'.html':'text/html', '.css':'text/css', '.js':'application/javascript', '.json':'application/json', '.svg':'image/svg+xml'};
(async () => {
  const origin = 'http://127.0.0.1:4173';
  let browser;
  try {
    browser = await chromium.launch({headless:true});
    const page = await browser.newPage();
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    await page.route('**/*', route => {
      const url = new URL(route.request().url());
      if (url.origin !== origin || !url.pathname.startsWith(prefix)) {
        errors.push('External request ' + route.request().url());
        return route.abort();
      }
      let file = path.resolve(root, decodeURIComponent(url.pathname.slice(prefix.length)) || '.');
      if (!file.startsWith(root + path.sep) && file !== root) return route.fulfill({status:403,body:''});
      if (fs.existsSync(file) && fs.statSync(file).isDirectory()) file = path.join(file, 'index.html');
      if (!fs.existsSync(file)) return route.fulfill({status:404,body:''});
      return route.fulfill({contentType:types[path.extname(file)] || 'application/octet-stream',body:fs.readFileSync(file)});
    });
    async function visit(destination) {
      await page.goto(origin + prefix + destination, {waitUntil:'networkidle'});
      await page.waitForFunction(() => [...document.querySelectorAll('.demo-scope')].every(scope => scope.shadowRoot?.querySelector('.demo-root')));
    }
    async function inspectViews() {
      return page.evaluate(() => {
        const rows = [];
        for (const scope of document.querySelectorAll('.demo-scope')) {
          for (const node of scope.shadowRoot.querySelectorAll('.scene-stack .mini-view,.scene-slide,.scene-curtain,.stagger-box,.shared-chip')) {
            const style = getComputedStyle(node);
            rows.push({text:node.textContent.trim(), height:node.clientHeight, scroll:node.scrollHeight,
              width:node.clientWidth, scrollWidth:node.scrollWidth, color:style.color});
            for (const text of node.querySelectorAll('strong,.scene-description')) {
              rows.push({text:text.textContent.trim(), height:text.clientHeight, scroll:text.scrollHeight,
                width:text.clientWidth, scrollWidth:text.scrollWidth, color:getComputedStyle(text).color});
            }
          }
        }
        return rows;
      });
    }
    let viewChecks = 0;
    for (const width of widths) {
      await page.setViewportSize({width, height:900});
      for (const slug of viewSlugs) {
        await visit(`interactions/${slug}/`);
        for (const row of await inspectViews()) {
          assert.ok(row.height >= row.scroll, `${width} ${slug} vertical ${JSON.stringify(row)}`);
          assert.ok(row.width >= row.scrollWidth, `${width} ${slug} horizontal ${JSON.stringify(row)}`);
          viewChecks++;
        }
        if (['view-crossfade','view-slide','view-curtain'].includes(slug)) {
          const typography = await page.locator('.entry-demo .demo-scope').first().evaluate(scope =>
            [...scope.shadowRoot.querySelectorAll('.mini-view strong,.scene-slide strong,.scene-description')].map(node => ({
              color:getComputedStyle(node).color, size:parseFloat(getComputedStyle(node).fontSize)})));
          assert.ok(typography.length);
          for (const item of typography) {assert.equal(item.color, 'rgb(255, 255, 255)');assert.ok(item.size >= 13 && item.size <= 32, `${width} ${slug} type size ${item.size}`);}
        }
      }
      await visit('interactions/');
      for (const row of await inspectViews()) {
        assert.ok(row.height >= row.scroll, `${width} gallery vertical ${JSON.stringify(row)}`);
        assert.ok(row.width >= row.scrollWidth, `${width} gallery horizontal ${JSON.stringify(row)}`);
        viewChecks++;
      }
    }
    await page.setViewportSize({width:1440,height:900});
    await visit('components/button/');
    const colors = {};
    for (const state of ['free','hover','pressed']) {
      await page.locator(`[data-state="${state}"]`).click();
      await page.waitForTimeout(180);
      colors[state] = await page.locator('.entry-demo .demo-scope').first().evaluate(scope =>
        [...scope.shadowRoot.querySelectorAll('.btn-pri,.btn-ghost,.btn-danger')].map(node => ({
          background:getComputedStyle(node).backgroundColor, border:getComputedStyle(node).borderColor,
          transform:getComputedStyle(node).transform})));
    }
    for (let i=0;i<3;i++) {
      assert.equal(new Set(Object.values(colors).map(items=>items[i].background)).size,3, `forced colors ${i}`);
      assert.equal(colors.pressed[i].transform,'matrix(0.98, 0, 0, 0.98, 0, 0)');
    }
    assert.equal(colors.pressed[0].background,'rgb(76, 29, 149)');
    assert.equal(colors.free[2].background,'rgb(185, 28, 28)');
    assert.equal(colors.hover[2].background,'rgb(153, 27, 27)');
    assert.equal(colors.pressed[2].background,'rgb(127, 29, 29)');
    assert.notEqual(colors.hover[1].border,colors.pressed[1].border);
    await page.locator('[data-state="free"]').click();
    for (const [i, selector] of ['.btn-pri','.btn-ghost[data-cmd="toast"]','.btn-danger'].entries()) {
      const button = page.locator('.entry-demo .demo-scope').first().locator(selector);
      await button.hover();await page.waitForTimeout(180);
      const hover = await button.evaluate(node=>getComputedStyle(node).backgroundColor);
      await page.mouse.down();await page.waitForTimeout(180);
      const pressed = await button.evaluate(node=>getComputedStyle(node).backgroundColor);
      await page.mouse.up();
      assert.equal(hover,colors.hover[i].background);
      assert.equal(pressed,colors.pressed[i].background);
    }
    let controls = 0, hints = 0;
    for (const column of ['basics','components','interactions','scenarios','ai']) {
      await visit(`${column}/`);
      const result = await page.evaluate(() => {
        const failures = [];let controls=0,hints=0;
        for(const scope of document.querySelectorAll('.demo-scope')) {
          for(const node of scope.shadowRoot.querySelectorAll('input,textarea,select,button,[role="button"],[tabindex],.searchbox,.taginput-demo,.stepper,.dropzone,.slider,.switch-demo')) {
            const css=getComputedStyle(node);
            if(css.borderStyle==="none"||css.borderTopWidth==="0px")continue;
            // Image cards are identified by their photo and elevation (WCAG 1.4.11 needs no boundary there); their hairline border is decorative.
            if(node.matches(".micro-card,.extra-inline-card,.hact-card,.ds-h-panel")&&node.querySelector("img"))continue;
            controls++;
            if(!['rgb(134, 142, 156)','rgb(4, 120, 87)','rgb(185, 28, 28)','rgb(180, 83, 9)','rgb(109, 40, 217)'].includes(css.borderColor))failures.push(['border',node.outerHTML.slice(0,140),css.borderColor]);
          }
          for(const node of scope.shadowRoot.querySelectorAll('.stage-label,.canvas .ctl,.gesture-note,.preview-label,.cf-hint,.trail-hint,.eyes-note,.magnet-note')) {
            const css=getComputedStyle(node);hints++;
            if(css.color!=='rgb(75, 85, 99)'||parseFloat(css.fontSize)<12)failures.push(['hint',node.textContent,css.color,css.fontSize]);
          }
          if(scope.shadowRoot.querySelector('.stage-live,.stage-signature'))failures.push(['decoration']);
        }
        return {failures,controls,hints};
      });
      assert.deepEqual(result.failures,[],column);
      controls+=result.controls;hints+=result.hints;
    }
    assert.deepEqual(errors,[]);
    console.log(JSON.stringify({viewChecks,controls,hints,buttonColors:colors},null,2));
  } finally {
    if(browser)await browser.close();
  }
})().catch(error=>{console.error(error);process.exitCode=1;});
