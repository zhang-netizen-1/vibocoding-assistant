/* Real-DOM H checks, shared by the existing headless runner and local fixtures. */
async function demoHChecks(scope, slug) {
  const root = scope.shadowRoot;
  const checks = [];
  const assert = (condition, message) => {
    if (!condition) throw new Error(slug + ' ' + message);
    checks.push(message);
  };
  const wait = ms => new Promise(resolve => setTimeout(resolve, ms));
  const click = selector => root.querySelector(selector).click();
  const panel = root.querySelector('.ds-h-panel');
  const stage = root.querySelector('.ds-stage');
  const geometry = () => {
    const box = panel.getBoundingClientRect(), frame = stage.getBoundingClientRect();
    const hint = root.querySelector('.ds-hint').getBoundingClientRect();
    assert(box.top >= frame.top + 15.5 && box.left >= frame.left + 15.5 &&
      box.right <= frame.right - 15.5 && box.bottom <= frame.bottom - 15.5, 'subject clears four edges');
    assert(box.bottom <= hint.top - 11.5, 'subject clears capsule');
    assert(stage.scrollWidth <= stage.clientWidth + 2, 'stage has no horizontal overflow');
    if (innerWidth === 1440) assert(box.width / frame.width >= .55 && box.width / frame.width <= .66, 'desktop subject ratio');
  };
  geometry();
  const touchSelectors = {
    'component-tilt':'.tilt-card',
    'component-spotlight':'.spot-card',
    'component-hover-preview':'.hvp-link',
    'component-hover-action':'.hact-card',
    'component-magnetic':'.magnet-btn'
  };
  if (matchMedia('(pointer:coarse)').matches && touchSelectors[slug]) {
    const target = root.querySelector(touchSelectors[slug]);
    target.click();
    assert(target.classList.contains('touch-open'), 'touch preview opens');
    target.click();
    assert(!target.classList.contains('touch-open') && target.classList.contains('touch-closed'), 'touch preview closes');
  }
  if (slug === 'component-flip') {
    click('.flip-card');
    assert(root.querySelector('.flip-card').getAttribute('aria-pressed') === 'true', 'card flips');
    click('.flip-card');
    assert(root.querySelector('.flip-card').getAttribute('aria-pressed') === 'false', 'card returns');
  }
  if (slug === 'component-switch') {
    click('.switch-demo');
    assert(root.querySelector('.switch-demo').getAttribute('aria-checked') === 'true', 'switch selects');
    click('.switch-demo');
    assert(root.querySelector('.switch-demo').getAttribute('aria-checked') === 'false', 'switch clears');
  }
  if (slug === 'component-morph') {
    click('.morph-demo');
    assert(root.querySelector('.morph-demo').disabled, 'morph busy locks action');
    await wait(470);
    assert(root.querySelector('.morph-demo').classList.contains('done'), 'morph succeeds');
    await wait(1100);
    assert(root.querySelector('.morph-demo').textContent === '执行动作 →', 'morph restores');
  }
  if (slug === 'tab-indicator') {
    click('#extra-tab-activity');
    assert(root.querySelector('#extra-tab-activity').getAttribute('aria-selected') === 'true', 'tab selects');
    // The indicator is measured from the selected tab (unequal widths), so it must cover that tab exactly.
    await wait(400);
    const tab = root.querySelector('#extra-tab-activity').getBoundingClientRect(), bar = root.querySelector('.extra-tab-indicator').getBoundingClientRect();
    assert(root.querySelector('.extra-tab-indicator').style.transform !== '' && Math.abs(bar.left - tab.left) < 1.5 && Math.abs(bar.width - tab.width) < 1.5 && Math.abs(bar.top - tab.top) < 1.5, 'indicator advances onto the selected tab');
    click('#extra-tab-overview');
  }
  if (slug === 'inline-expand') {
    click('.extra-inline-card');
    assert(root.querySelector('.extra-inline-card').getAttribute('aria-expanded') === 'true', 'inline detail expands');
    await wait(400); geometry();
    click('.extra-inline-card');
  }
  if (slug === 'accordion') {
    const buttons = root.querySelectorAll('[data-extra-action="accordion"]');
    buttons[1].click();
    assert(buttons[1].getAttribute('aria-expanded') === 'true', 'second question opens');
    assert(buttons[0].getAttribute('aria-expanded') === 'false', 'previous question closes');
    await wait(400); geometry();
    buttons[0].click();
  }
  if (slug === 'overlay-menu') {
    click('[data-action="toggle"]');
    assert(!root.querySelector('.menu-items').hidden, 'menu opens');
    await wait(220); geometry();
    const box = root.querySelector('.menu-items').getBoundingClientRect(), bounds = panel.getBoundingClientRect();
    assert(box.bottom <= bounds.bottom - 15.5, 'menu fits subject');
    click('[role="menuitem"]');
    assert(root.querySelector('.menu-items').hidden, 'selection closes menu');
  }
  if (['overlay-drawer','overlay-modal','overlay-sheet'].includes(slug)) {
    click('[data-action="open"]');
    const layer = root.querySelector(slug === 'overlay-sheet' ? '.sheet' : '.overlay-shade');
    assert(!layer.hidden, 'dialog opens');
    click('[data-action="close"]');
    assert(layer.hidden, 'dialog closes');
  }
  if (slug === 'toast-stack') {
    click('[data-extra-action="add-toast"]');
    assert(root.querySelectorAll('.extra-notice').length === 2, 'notice added');
    click('[data-extra-action="remove-toast"]');
    await wait(260);
    assert(root.querySelectorAll('.extra-notice').length === 1, 'notice removed');
  }
  if (slug === 'data-reorder') {
    const first = root.querySelector('.sort-list').firstElementChild;
    click('[data-action="sort"]');
    assert(root.querySelector('.sort-list').lastElementChild === first, 'priority reordered');
  }
  if (slug === 'filter-grid') {
    click('[data-value="摄影"]');
    await wait(300);
    assert(!root.querySelector('.extra-filter-empty').hidden, 'empty filter state');
    click('[data-value="全部"]');
    await wait(300);
    assert([...root.querySelectorAll('.extra-gallery-tile')].every(node => !node.hidden), 'all works restored');
  }
  if (slug === 'chart-morph') {
    click('[data-value="previous"]');
    assert(root.querySelector('.extra-status').textContent.includes('260'), 'previous chart total');
    click('[data-value="current"]');
    assert(root.querySelector('.extra-status').textContent.includes('309'), 'current chart total');
  }
  if (slug === 'skeleton-handoff') {
    click('[data-extra-action="load-content"]');
    await wait(850);
    assert(root.querySelector('.extra-content-skeleton').hidden && !root.querySelector('.extra-content-real').hidden, 'content handoff completes');
  }
  if (slug === 'data-input-shake') {
    click('.shake-go');
    assert(!root.querySelector('.shake-err').hidden, 'invalid email feedback');
    root.querySelector('.shake-input').value = 'studio@example.com';
    click('.shake-go');
    assert(root.querySelector('.shake-err').hidden, 'valid email clears error');
  }
  if (slug === 'odometer') {
    click('[data-extra-action="roll"]');
    await wait(900);
    assert(root.querySelector('.extra-digits').getAttribute('aria-label') === '当前数值 205', 'odometer carries to 205');
  }
  if (slug === 'scroll-highlight') {
    const scroller = root.querySelector('.extra-highlight-scroll');
    scroller.scrollTop = scroller.scrollHeight;
    scroller.dispatchEvent(new Event('scroll'));
    assert(root.querySelectorAll('.extra-highlight-text .lit').length === 4, 'reading highlights final text');
  }
  await wait(400);
  geometry();
  return {checks};
}
if (typeof module !== 'undefined') module.exports = demoHChecks;
