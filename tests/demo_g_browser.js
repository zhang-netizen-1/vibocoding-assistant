/* Shared real-DOM checks for G fixtures and the headless detail-page runner. */
async function demoGChecks(scope, slug) {
  const root = scope.shadowRoot;
  const checks = [];
  const assert = (condition, message) => {
    if (!condition) throw new Error(slug + ': ' + message);
    checks.push(message);
  };
  const wait = ms => new Promise(resolve => setTimeout(resolve, ms));
  const key = (node, value) => node.dispatchEvent(new KeyboardEvent('keydown', {key:value, bubbles:true}));
  const geometry = selector => {
    const stage = root.querySelector('.ds-stage').getBoundingClientRect();
    const box = root.querySelector(selector).getBoundingClientRect();
    const hint = root.querySelector('.ds-hint')?.getBoundingClientRect();
    assert(box.top >= stage.top + 15.5 && box.left >= stage.left + 15.5 &&
      box.right <= stage.right - 15.5 && box.bottom <= stage.bottom - 15.5, selector + ' stays inside stage ' + JSON.stringify({stage:{top:stage.top,bottom:stage.bottom,left:stage.left,right:stage.right},box:{top:box.top,bottom:box.bottom,left:box.left,right:box.right}}));
    if (hint && !selector.includes('cmdk')) assert(box.bottom <= hint.top - 11.5, selector + ' clears hint');
  };
  if (slug === 'cmdk') {
    root.querySelector('[data-cmd="openCmdk"]').click();
    assert(root.querySelector('#cmdk').classList.contains('show'), 'palette opens');
    geometry('.cmdk');
    const input = root.querySelector('#cmdkInput');
    input.value = '不存在的组件搜索词';
    input.dispatchEvent(new Event('input', {bubbles:true}));
    assert(!!root.querySelector('.cmdk-empty'), 'empty search feedback');
    key(input, 'Escape');
    assert(!root.querySelector('#cmdk').classList.contains('show'), 'palette closes');
  }
  if (slug === 'accordion') {
    const heads = root.querySelectorAll('.acc-head');
    heads[0].click();
    assert(heads[0].getAttribute('aria-expanded') === 'true', 'first disclosure opens');
    geometry('.ds-accordion-panel');
    heads[1].click();
    assert(heads[0].getAttribute('aria-expanded') === 'false' && heads[1].getAttribute('aria-expanded') === 'true', 'single disclosure ownership');
    heads[1].click();
  }
  if (slug === 'steps') {
    root.querySelector('[data-arg="2"]').click();
    assert(root.querySelectorAll('.step')[2].getAttribute('aria-current') === 'step', 'step selection');
  }
  if (slug === 'dropdown') {
    const button = root.querySelector('[data-cmd="toggleDD"]');
    button.click();
    assert(root.querySelector('.dropdown').classList.contains('open'), 'dropdown opens');
    geometry('.dd-menu');
    root.querySelector('[data-cmd="pickDD"]').click();
    assert(!root.querySelector('.dropdown').classList.contains('open'), 'dropdown selection closes');
  }
  if (slug === 'context-menu') {
    const zone = root.querySelector('#ctxZone');
    key(zone, 'Enter');
    assert(!root.querySelector('.ctxmenu').hidden, 'keyboard context menu');
    geometry('.ctxmenu');
    key(root.querySelector('.ctxmenu button'), 'Escape');
    assert(root.querySelector('.ctxmenu').hidden, 'context menu closes');
  }
  if (slug === 'mega-menu') {
    root.querySelector('#megaTrigger').click();
    assert(!root.querySelector('#megaPanel').hidden, 'mega menu opens');
    geometry('.ds-mega-menu-panel');
    key(root.querySelector('.mega-link'), 'Escape');
    assert(root.querySelector('#megaPanel').hidden, 'mega menu closes');
  }
  if (slug === 'chip') {
    root.querySelector('.chip button').click();
    assert(root.querySelectorAll('.chip').length === 2, 'chip removes independently');
  }
  if (slug === 'badge-dot') {
    root.querySelector('.bdg').click();
    assert(!root.querySelector('.num') || getComputedStyle(root.querySelector('.num')).display === 'none', 'notification count clears');
  }
  if (slug === 'view-switch') {
    root.querySelector('[data-view="list"].segb').click();
    assert(root.querySelector('#viewBody').dataset.view === 'list', 'list view selected');
    geometry('.ds-view-switch-panel');
    root.querySelector('[data-view="grid"].segb').click();
  }
  if (slug === 'card-link') {
    root.querySelector('.clk-share').click();
    assert(root.querySelector('.demo-status').textContent.includes('仅分享'), 'share preserves independent action');
  }
  if (slug === 'split-button') {
    root.querySelector('#splitCaret').click();
    assert(!root.querySelector('#splitMenu').hidden, 'split menu opens');
    geometry('.split-menu');
    root.querySelector('.split-pick').click();
    assert(root.querySelector('#splitMenu').hidden, 'split selection closes');
  }
  if (slug === 'fab') {
    root.querySelector('#fabBtn').click();
    assert(!root.querySelector('#fabActions').hidden, 'quick actions open');
    geometry('.ds-fab-panel');
    key(root.querySelector('#fabBtn'), 'Escape');
    assert(root.querySelector('#fabActions').hidden, 'quick actions close');
  }
  if (slug === 'back-to-top') {
    const page = root.querySelector('#bttPage');
    page.scrollTop = page.scrollHeight;
    page.dispatchEvent(new Event('scroll'));
    assert(!root.querySelector('#bttBtn').hidden, 'return control appears');
    root.querySelector('#bttBtn').click();
    await wait(700);
    assert(page.scrollTop < 2, 'return control reaches top');
  }
  if (slug === 'table-fixed') {
    const table = root.querySelector('.tblfix-demo');
    table.scrollTop = 60;
    table.scrollLeft = 80;
    await wait(20);
    const scroller = table.getBoundingClientRect();
    const heading = root.querySelector('.fixcol').getBoundingClientRect();
    // At wide stages every column fits, so horizontal scrolling is only required when the table overflows.
    const overflowsX = table.scrollWidth > table.clientWidth + 1;
    assert(table.scrollTop > 0 && (!overflowsX || table.scrollLeft > 0) && Math.abs(heading.top - scroller.top - 1) < 2 &&
      Math.abs(heading.left - scroller.left - 1) < 2, 'header and first column stay fixed');
  }
  if (slug === 'table-columns') {
    const toggle = root.querySelector('[data-col="2"]');
    toggle.click();
    assert(root.querySelector('#colTbl').rows[0].cells[2].style.display === 'none', 'column hides');
    toggle.click();
    assert(root.querySelector('#colTbl').rows[0].cells[2].style.display === '', 'column restores');
    const grip = root.querySelector('.colgrip');
    const width = grip.parentElement.offsetWidth;
    for (const [type, x] of [['pointerdown', 100], ['pointermove', 116], ['pointerup', 116]]) {
      grip.dispatchEvent(new PointerEvent(type, {clientX:x, pointerId:7, bubbles:true}));
    }
    assert(parseFloat(grip.parentElement.style.width) >= width + 15, 'column resizes');
    geometry('.ds-table-columns-panel');
  }
  if (slug === 'table-edit') {
    const cell = root.querySelector('.edittarget');
    const original = cell.textContent;
    key(cell, 'Enter');
    let input = cell.querySelector('input');
    assert(!!input, 'cell enters editing');
    input.value = '已复核';
    key(input, 'Enter');
    assert(cell.textContent === '已复核', 'cell commits');
    key(cell, 'Enter');
    input = cell.querySelector('input');
    input.value = '取消修改';
    key(input, 'Escape');
    assert(cell.textContent === '已复核', 'cell cancels');
    cell.textContent = original;
  }
  if (slug === 'sortable-table') {
    root.querySelector('[data-guide-mode="1"]').click();
    const values = [...root.querySelectorAll('tbody tr')].map(row => Number(row.cells[1].textContent));
    assert(values.join(',') === '82,68,42', 'table sorts descending');
    root.querySelector('[data-guide-mode="0"]').click();
    const names = [...root.querySelectorAll('tbody tr')].map(row => row.cells[0].textContent);
    assert(names.join(',') === [...names].sort((a,b) => a.localeCompare(b,'zh-CN')).join(','), 'table name order restores');
  }
  if (slug === 'load-more') {
    const button = root.querySelector('#lmBtn');
    button.click();
    assert(button.disabled && button.textContent.includes('加载'), 'loading locks repeated requests');
    await wait(550);
    assert(root.querySelectorAll('.inf-item').length === 5 && !button.disabled, 'first batch appends');
    button.click();
    await wait(550);
    assert(root.querySelectorAll('.inf-item').length === 8 && button.disabled, 'terminal state');
    geometry('.ds-load-more-panel');
  }
  return {slug, checks};
}
if (typeof module !== 'undefined') module.exports = demoGChecks;
