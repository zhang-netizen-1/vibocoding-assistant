'use strict';
(() => {
  const $ = selector => document.querySelector(selector), $$ = selector => [...document.querySelectorAll(selector)];
  const search = $('#search-dialog'), drawer = $('#directory'), input = $('#search-input'), body = $('#search-body');
  let data = null, indexRequest = null, indexFailed = false;
  const mobile = matchMedia('(max-width:1023px)'), reduced = matchMedia('(prefers-reduced-motion: reduce)');
  const escape = text => String(text).replace(/[&<>"']/g, char => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[char]));
  let announceTimer;
  function announce(message) { clearTimeout(announceTimer); $('#live').textContent = ''; announceTimer = setTimeout(() => { $('#live').textContent = message; }, 20); }

  let activeMenu = null, pinned = null, closeTimer;
  const triggers = $$('[data-nav]');
  function closeMenu(restore = false) {
    clearTimeout(closeTimer);
    const previous = activeMenu;
    triggers.forEach(button => { button.setAttribute('aria-expanded','false'); $('#mega-' + button.dataset.nav).hidden = true; });
    activeMenu = pinned = null;
    if (restore) previous?.focus();
  }
  function openMenu(button, focus = false) {
    clearTimeout(closeTimer);
    triggers.forEach(item => { const open = item === button; item.setAttribute('aria-expanded',String(open)); $('#mega-' + item.dataset.nav).hidden = !open; });
    activeMenu = button;
    if (focus) $('#mega-' + button.dataset.nav).querySelector('a')?.focus();
  }
  triggers.forEach(button => {
    button.addEventListener('pointerenter', event => { if (event.pointerType === 'mouse' && !mobile.matches) { pinned = null; openMenu(button); } });
    button.addEventListener('click', event => { if (pinned === button) closeMenu(); else { pinned = button; openMenu(button, event.detail === 0); } });
    button.addEventListener('keydown', event => { if (event.key === 'ArrowDown') { event.preventDefault(); pinned = button; openMenu(button,true); } });
  });
  $('#header').addEventListener('pointerenter', () => clearTimeout(closeTimer));
  $('#header').addEventListener('pointerleave', () => { if (!pinned && !$('#header').contains(document.activeElement)) closeTimer = setTimeout(closeMenu,180); });
  $('#header').addEventListener('focusout', () => setTimeout(() => { if (!$('#header').contains(document.activeElement)) closeMenu(); },0));
  document.addEventListener('pointerdown', event => { if (!$('#header').contains(event.target)) closeMenu(); });

  let savedScroll = 0, savedStyle = null, returnFocus = null;
  function lock() {
    if (savedStyle) return;
    savedScroll = scrollY;
    savedStyle = {position:document.body.style.position,top:document.body.style.top,width:document.body.style.width,overflow:document.body.style.overflow};
    Object.assign(document.body.style, {position:'fixed',top:`-${savedScroll}px`,width:'100%',overflow:'hidden'});
  }
  function unlock() {
    if (!savedStyle) return;
    Object.assign(document.body.style,savedStyle); savedStyle = null;
    scrollTo({top:savedScroll,behavior:'instant'});
  }
  function openSearch(query = '', trigger = document.activeElement) {
    if (search.open) { input.value = query; loadSearchIndex(); renderSearch(); input.focus(); return; }
    if (drawer.open) { drawer.close(); returnFocus = $('#directory-toggle'); }
    else returnFocus = trigger;
    stopAllCards(); closeMenu(); lock(); search.showModal(); input.value = query; loadSearchIndex(); renderSearch(); input.focus();
  }
  search.addEventListener('close', () => { if (!drawer.open) unlock(); returnFocus?.focus({preventScroll:true}); });
  function openDrawer() { stopAllCards(); closeMenu(); lock(); drawer.showModal(); $('#directory-toggle').setAttribute('aria-expanded','true'); }
  drawer.addEventListener('close', () => { if (!search.open) unlock(); $('#directory-toggle').setAttribute('aria-expanded','false'); $('#directory-toggle').focus({preventScroll:true}); });
  [search,drawer].forEach(dialog => {
    dialog.addEventListener('click', event => { const rect = dialog.getBoundingClientRect(); if (event.target === dialog && (event.clientX < rect.left || event.clientX > rect.right || event.clientY < rect.top || event.clientY > rect.bottom)) dialog.close(); });
  });
  $$('[data-close]').forEach(button => button.addEventListener('click', () => $('#' + button.dataset.close).close()));
  $('#nav-search').addEventListener('click', event => openSearch('',event.currentTarget));
  $$('[data-search]').forEach(button => button.addEventListener('click', event => openSearch('',event.currentTarget)));
  $('#directory-toggle').addEventListener('click',openDrawer);
  drawer.querySelectorAll('a').forEach(link => link.addEventListener('click', () => drawer.close()));

  let selected = 0, results = [];
  function loadSearchIndex() {
    if (data || indexRequest) return;
    indexFailed = false;
    indexRequest = fetch(search.dataset.indexUrl)
      .then(response => {
        if (!response.ok) throw new Error('Search index unavailable');
        return response.json();
      })
      .then(index => {
        if (![index.entries,index.columns,index.examples].every(Array.isArray)) throw new Error('Invalid search index');
        const localize = item => ({...item, href:search.dataset.siteRoot + item.href.slice(2)});
        data = {...index, entries:index.entries.map(localize), columns:index.columns.map(localize)};
      })
      .catch(() => { indexFailed = true; })
      .finally(() => { indexRequest = null; if (search.open) renderSearch(); });
  }
  const queryButtons = () => data.examples.map(query => `<button class="chip" data-query="${escape(query)}">${escape(query)}</button>`).join('');
  function thumbnail(entry) {
    const kinds = ['basics','components','interactions','scenarios','ai'];
    const kind = kinds.includes(entry.thumbnail) ? entry.thumbnail : 'fallback';
    const content = kind === 'fallback' ? escape(entry.column.slice(0,1)) : '<i></i><i></i><i></i>';
    return `<span class="result-thumb result-thumb-${kind}" aria-hidden="true">${content}</span>`;
  }
  function renderSearch() {
    input.removeAttribute('aria-activedescendant');
    input.removeAttribute('aria-controls');
    input.setAttribute('aria-expanded', 'false');
    selected = 0; results = [];
    body.setAttribute('aria-busy',String(!data && !indexFailed));
    if (!data) {
      body.innerHTML = indexFailed
        ? '<p role="status">搜索加载失败，请重试。</p><button data-search-retry>重试</button>'
        : '<p role="status">正在加载…</p>';
      return;
    }
    const query = input.value.trim(); results = query ? VibeSearch.match(data.entries,query) : [];
    if (!query) { body.innerHTML = `<h2 class="common-title">常用搜法</h2><div class="chips">${queryButtons()}</div>`; return; }
    if (!results.length) {
      const nearby = VibeSearch.similar(data.entries,query);
      const similar = nearby.length ? `<section class="empty-block"><h3>相近的名称</h3>${nearby.map(entry => `<a href="${escape(entry.href)}">${escape(entry.zh)} <span class="english">${escape(entry.en)}</span></a>`).join('')}</section>` : '';
      body.innerHTML = `<h2 class="empty-title">没有找到「${escape(query)}」</h2><div class="empty-grid">${similar}<section class="empty-block"><h3>换个说法</h3><p>描述它怎么动或在哪里，比如「滑入」「弹出」「浮起来」。</p></section><section class="empty-block"><h3>按栏目找</h3>${data.columns.map(column => `<a href="${escape(column.href)}">${escape(column.name)}</a>`).join('')}</section></div>`;
      announce(`没有找到「${query}」`); return;
    }
    body.innerHTML = `<p class="result-count">找到 ${results.length} 条结果</p><div id="result-list" role="grid" aria-label="搜索结果">${results.map((row,index) => `<div class="result-row${index === 0 ? ' selected' : ''}" id="result-${index}" role="row" aria-selected="${index === 0}"><div class="result-visual" role="gridcell">${thumbnail(row.entry)}</div><div class="result-info" role="gridcell"><a class="result-name" href="${escape(row.entry.href)}">${escape(row.entry.zh)}</a><span class="english">${escape(row.entry.en)}</span>${row.alias ? `<p class="result-alias">${escape(VibeSearch.aliasLabel(row))}</p>` : ''}<p class="result-definition">${escape(row.entry.definition.split('\n')[0])}</p><p class="result-meta">${escape(row.entry.column)} · ${escape(row.entry.group)}</p></div><div class="result-actions" role="gridcell"><a href="${escape(row.entry.href)}" tabindex="-1" aria-label="打开${escape(row.entry.zh)}">打开</a><button class="copy-btn" data-copy-result="${row.index}" aria-label="复制${escape(row.entry.zh)}提示词">复制提示词</button></div></div>`).join('')}</div>`;
    input.setAttribute('aria-expanded','true');
    input.setAttribute('aria-controls','result-list');
    input.setAttribute('aria-activedescendant','result-0');
    announce(`找到 ${results.length} 条结果`);
  }
  input.addEventListener('input',renderSearch);
  search.addEventListener('keydown', event => {
    if (event.isComposing) return;
    if (event.key === 'Escape') { event.preventDefault(); search.close(); return; }
    if (!results.length) return;
    if (['ArrowDown','ArrowUp'].includes(event.key) && event.target === input) {
      event.preventDefault(); selected = (selected + (event.key === 'ArrowDown' ? 1 : results.length - 1)) % results.length;
      $$('.result-row').forEach((row,index) => { row.classList.toggle('selected',index === selected); row.setAttribute('aria-selected',String(index === selected)); });
      input.setAttribute('aria-activedescendant','result-' + selected);
      $('#result-' + selected).scrollIntoView({block:'nearest'}); announce(`已选择 ${results[selected].entry.zh}，按 Enter 打开`);
    } else if (event.key === 'Enter' && event.target === input) { event.preventDefault(); location.assign(results[selected].entry.href); }
  });

  search.addEventListener('click', event => {
    const button = event.target.closest('[data-copy-result]');
    if (button) { event.stopPropagation(); copy(button,data.entries[Number(button.dataset.copyResult)].prompt); }
  });

  async function writeClipboard(text) {
    try { if (!navigator.clipboard?.writeText) throw new Error('Clipboard unavailable'); await navigator.clipboard.writeText(text); }
    catch (_) {
      const previous = document.activeElement, area = document.createElement('textarea');
      area.value = text; area.setAttribute('aria-label','临时复制文本'); area.style.cssText = 'position:fixed;top:0;left:0;width:1px;height:1px;opacity:0';
      (search.open ? search : drawer.open ? drawer : document.body).append(area); area.focus({preventScroll:true}); area.select();
      let success = false;
      try { success = document.execCommand('copy'); } finally { area.remove(); previous?.focus({preventScroll:true}); }
      if (!success) throw new Error('Copy failed');
    }
  }
  const promptCopyButtons = $$('[data-copy-source="copy-prompt"]');
  const promptCard = $('.prompt-card');
  const promptLabels = new Map(promptCopyButtons.map(button => [button,button.textContent]));
  let promptCopyTimer;
  function markPromptCopied() {
    clearTimeout(promptCopyTimer);
    promptCard?.classList.add('is-copied');
    promptCopyButtons.forEach(button => { button.textContent = '✓ 已复制'; button.classList.add('is-copied'); });
    promptCopyTimer = setTimeout(() => {
      promptCard?.classList.remove('is-copied');
      promptCopyButtons.forEach(button => { button.textContent = promptLabels.get(button); button.classList.remove('is-copied'); });
    },2000);
  }
  const copyTimers = new WeakMap();
  async function copy(button,text) {
    if (button.dataset.copying) return;
    button.dataset.copying = 'true';
    if (button.dataset.copySource === 'copy-prompt') {
      try { await writeClipboard(text); markPromptCopied(); announce('已复制'); }
      catch (_) { announce('复制未完成，请选择提示词文字后手动复制。'); }
      finally { delete button.dataset.copying; }
      return;
    }
    const previous = copyTimers.get(button), label = previous?.label || button.textContent;
    if (previous) clearTimeout(previous.timer);
    // Fix both dimensions before changing the label; restore after feedback.
    const width = previous?.width ?? button.style.width, height = previous?.height ?? button.style.height;
    button.style.width = `${button.getBoundingClientRect().width}px`; button.style.height = `${button.getBoundingClientRect().height}px`;
    try {
      await writeClipboard(text); button.textContent = '已复制'; announce('已复制');
      const timer = setTimeout(() => { button.textContent = label; button.style.width = width; button.style.height = height; copyTimers.delete(button); },1800);
      copyTimers.set(button,{label,timer,width,height});
    } catch (_) { button.textContent = label; button.style.width = width; button.style.height = height; announce('复制未完成，请选择提示词文字后手动复制。'); }
    finally { delete button.dataset.copying; }
  }
  function setupPromptVisibility() {
    const bottomBar = $('.bottom-bar');
    if (!promptCard || !bottomBar) return;
    let promptInView = false;
    function syncBottomBar() {
      const hide = !mobile.matches || promptInView;
      if (hide && bottomBar.contains(document.activeElement)) {
        promptCard.querySelector('[data-copy-source="copy-prompt"]')?.focus({preventScroll:true});
      }
      bottomBar.hidden = hide;
      bottomBar.inert = hide;
    }
    function measurePrompt() {
      const rect = promptCard.getBoundingClientRect();
      promptInView = rect.top < window.innerHeight && rect.bottom > 0;
      syncBottomBar();
    }
    if (typeof IntersectionObserver !== 'undefined') {
      const observer = new IntersectionObserver(entries => {
        promptInView = entries.some(entry => entry.isIntersecting);
        syncBottomBar();
      },{threshold:0});
      observer.observe(promptCard);
    } else {
      window.addEventListener('scroll',measurePrompt,{passive:true});
    }
    mobile.addEventListener('change',measurePrompt);
    window.addEventListener('resize',measurePrompt,{passive:true});
    measurePrompt();
  }
  setupPromptVisibility();
  document.addEventListener('click', event => {
    const button = event.target.closest('button'); if (!button) return;
    if (button.hasAttribute('data-query')) openSearch(button.dataset.query,button);
    if (button.matches('.spec-group .copy-prompt')) copy(button,button.previousElementSibling.textContent);
    if (button.hasAttribute('data-copy-source')) copy(button,document.getElementById(button.dataset.copySource).textContent);
    if (button.hasAttribute('data-search-retry')) { loadSearchIndex(); renderSearch(); }
    if (button.hasAttribute('data-copy-link')) copy(button,location.href.split('#')[0]);
    if (button.hasAttribute('data-show-acceptance')) { const details = $('#acceptance'); details.open = true; details.scrollIntoView({block:'start'}); details.querySelector('summary').focus(); }
  });
  document.addEventListener('keydown', event => {
    if (event.isComposing) return;
    if (event.key === 'Escape' && activeMenu) { event.preventDefault(); closeMenu(true); return; }
    const target = event.composedPath()[0];
    const editing = /^(INPUT|TEXTAREA|SELECT)$/.test(target.tagName) || target.isContentEditable;
    if (((event.ctrlKey || event.metaKey) && event.key.toLowerCase() === 'k') || (event.key === '/' && !editing && !event.ctrlKey && !event.metaKey && !event.altKey)) {
      event.preventDefault(); if (!search.open) openSearch('',event.composedPath()[0] instanceof HTMLElement ? event.composedPath()[0] : document.activeElement);
    }
  });

  let activeCard = null, cardTimer = null, controller = null;
  function stopAllCards() {
    clearTimeout(cardTimer); controller?.reset(); controller = null;
    if (activeCard) { activeCard.classList.remove('playing'); activeCard.querySelector('.play-button').setAttribute('aria-pressed','false'); }
    activeCard = null;
  }
  function playCard(card, once = false) {
    stopAllCards(); if ((reduced.matches && !once) || card.querySelector('.demo-scope').dataset.demoStatic === 'true') return;
    activeCard = card; card.classList.add('playing'); card.querySelector('.play-button').setAttribute('aria-pressed','true');
    const scope = card.querySelector('.demo-scope'); controller = window.VibeDemos.init(scope); controller.preview();
    // A full original action runs once; restart only while hover/focus is held.
    const duration = scope.dataset.demoKey === 'text-text-morph' ? 3000 : 2400;
    if (!reduced.matches) cardTimer = setTimeout(() => { const replay = activeCard === card && !once; stopAllCards(); if (replay) { activeCard = card; cardTimer = setTimeout(() => playCard(card),1200); } },duration);
  }
  window.VibeDemos.mountAll();
  $$('.gallery-card').forEach(card => {
    card.querySelector('.demo-scope').addEventListener('demo-playback-end', () => {if(activeCard === card)stopAllCards();});
    if (card.querySelector('.demo-scope').dataset.demoStatic === 'true') { card.classList.add('static-preview'); card.querySelector('.play-button').hidden = true; return; }
    card.addEventListener('pointerenter', event => { if (event.pointerType === 'mouse' && !mobile.matches) playCard(card); });
    card.addEventListener('pointerleave', () => { if (activeCard === card) stopAllCards(); });
    card.addEventListener('focusin', event => { if (event.target.matches('.gallery-link') && !mobile.matches) playCard(card); });
    card.addEventListener('focusout', event => { if (!card.contains(event.relatedTarget) && activeCard === card) stopAllCards(); });
    card.querySelector('.play-button').addEventListener('click', () => playCard(card,true));
  });
  $$('.demo-scope[data-interactive]').forEach(scope => window.VibeDemos.init(scope));
  $$('.state-picker').forEach(picker => {
    const scope = picker.closest('.entry-demo').querySelector('.demo-scope');
    const controller = window.VibeDemos.init(scope);
    const options = [...picker.querySelectorAll('[data-state]')];
    options.forEach(option => option.addEventListener('click', () => {
      const fieldSelector = 'input:not([type="checkbox"]):not([type="radio"]),textarea,select';
      const values = [...controller.root.querySelectorAll(fieldSelector)].map(field => field.value);
      const checkSelector = 'input[type="checkbox"],input[type="radio"]';
      const checks = [...controller.root.querySelectorAll(checkSelector)].map(field => ({checked:field.checked,indeterminate:field.indeterminate}));
      const buttonWidths = [...controller.root.querySelectorAll('.btn')].map(button => button.offsetWidth);
      controller.restore();
      options.forEach(button => {
        button.setAttribute('aria-pressed',String(button === option));
        scope.classList.remove(button.dataset.stateClass);
      });
      const state = option.dataset.state;
      scope.classList.add(option.dataset.stateClass);
      picker.querySelectorAll('[data-description]').forEach(caption => {caption.hidden = caption.dataset.description !== state;});
      const root = controller.root;
      root.querySelectorAll(fieldSelector).forEach((field,index) => {
        field.value = values[index];
        field.dispatchEvent(new Event('input',{bubbles:true}));
      });
      root.querySelectorAll(checkSelector).forEach((field,index) => Object.assign(field,checks[index]));
      if (state === 'focus') (root.querySelector('input,select,textarea') || root.querySelector('button'))?.setAttribute('data-simulated-focus','');
      if (state === 'selected' || state === 'unselected') {
        const checked = state === 'selected';
        const radios = [...root.querySelectorAll('input[type="radio"]')];
        root.querySelectorAll('input[type="checkbox"]').forEach(input => {input.checked = checked;input.indeterminate = false;});
        radios.forEach((input,index) => {input.checked = index === radios.length-1;});
        if (checked) root.querySelector('[data-cmd="switchTab"][data-arg="1"]')?.click();
      }
      if (state === 'disabled' || state === 'loading') {
        const controls = [...root.querySelectorAll('button,input,select,textarea')];
        // A single unavailable tab leaves keyboard navigation demonstrable.
        const disabled = root.querySelector('[role="tablist"]') ? controls.slice(-1) : controls;
        disabled.forEach(control => { control.disabled = true; });
        if (state === 'loading') {
          root.querySelectorAll('.btn').forEach((button,index) => {
            button.style.width = `${buttonWidths[index]}px`;
            button.setAttribute('aria-busy','true');
            button.innerHTML = '<span class="demo-loading-icon" aria-hidden="true"></span><span>提交中…</span>';
          });
        }
      }
      if (state === 'success') {root.querySelectorAll('.btn').forEach(button => {button.textContent = '已完成';});}
      if (state === 'error') {
        const errors = {姓名:'请输入姓名，例如「张三」。', 邮箱:'邮箱格式有误，请填写 name@example.com。',
          备注:'请填写 1–80 字的备注。', 城市:'请选择一个可用的城市。', 搜索词:'请输入有效搜索词，例如「按钮」。'};
        root.querySelectorAll('input,textarea,select').forEach((field,index) => {
          const anchor = field.closest('.floatfield,.searchbox') || field;
          const wrapper = document.createElement('div'); wrapper.className = 'demo-field-state';
          anchor.before(wrapper); wrapper.append(anchor);
          const error = document.createElement('p'); error.className = 'demo-field-error';
          error.id = `demo-field-error-${index}`;
          error.textContent = errors[field.getAttribute('aria-label')] || '内容有误，请检查后重试。';
          field.setAttribute('aria-invalid','true');
          field.setAttribute('aria-describedby',[field.getAttribute('aria-describedby'),error.id].filter(Boolean).join(' '));
          wrapper.append(error);
        });
      }
      scope.inert = !['free','disabled','loading','error'].includes(state);
    }));
  });
  $$('[data-demo-replay],[data-demo-slow],[data-demo-step]').forEach(button => {
    const scope = button.closest('.entry-demo').querySelector('.demo-scope');
    const demo = window.VibeDemos.init(scope);
    if (button.hasAttribute('data-demo-slow') && demo.supportsSlow === false) button.disabled = true;
    if (button.hasAttribute('data-demo-step')) button.hidden = !demo.supportsStep;
    button.addEventListener('click', () => {
      if (button.hasAttribute('data-demo-step')) { demo.step(); return; }
      button.closest('.entry-demo').querySelector('[data-state="free"]')?.click();
      const slow = button.hasAttribute('data-demo-slow');
      demo.preview(slow ? .25 : 1);
      button.closest('.demo-controls').querySelector('[data-demo-slow]').setAttribute('aria-pressed',String(slow));
    });
  });
  function updateReducedNotes() { $$('.reduced-note').forEach(note => {note.hidden = !reduced.matches;}); }
  updateReducedNotes();
  reduced.addEventListener('change',updateReducedNotes);
  document.addEventListener('demo-message', event => { if (!event.target.closest('.gallery-card')) announce(event.detail); });
  reduced.addEventListener('change',stopAllCards);
  mobile.addEventListener('change', () => { stopAllCards(); closeMenu(); if (!mobile.matches && drawer.open) drawer.close(); });
  document.addEventListener('visibilitychange', () => { if (document.hidden) stopAllCards(); });
  window.addEventListener('pagehide',stopAllCards);
})();
