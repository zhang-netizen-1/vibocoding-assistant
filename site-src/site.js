(() => {
  const homeTabs = [...document.querySelectorAll('.home-demo-tabs [role="tab"]')];
  if (homeTabs.length) {
    function activateHomeTab(tab, moveFocus = false) {
      for (const item of homeTabs) {
        const selected = item === tab;
        item.setAttribute('aria-selected', String(selected));
        item.tabIndex = selected ? 0 : -1;
        document.getElementById(item.getAttribute('aria-controls')).hidden = !selected;
      }
      if (moveFocus) tab.focus();
    }
    homeTabs.forEach((tab, index) => {
      tab.addEventListener('click', () => activateHomeTab(tab));
      tab.addEventListener('keydown', event => {
        if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
        event.preventDefault();
        const next = event.key === 'Home' ? 0 : event.key === 'End' ? homeTabs.length - 1 : (index + (event.key === 'ArrowRight' ? 1 : -1) + homeTabs.length) % homeTabs.length;
        activateHomeTab(homeTabs[next], true);
      });
    });
    document.getElementById('home-demo-submit')?.addEventListener('click', () => {
      const name = document.getElementById('home-demo-name').value.trim();
      const notice = document.getElementById('home-demo-notice').checked;
      const result = document.getElementById('home-demo-result');
      result.textContent = !name ? '请先填写项目名称。' : notice ? `已完成本地演示：“${name}”，并显示提醒。` : `已完成本地演示：“${name}”，提醒已关闭。`;
    });
    let motionView = 1;
    document.getElementById('home-demo-motion-button')?.addEventListener('click', () => {
      motionView = motionView === 1 ? 2 : 1;
      const content = document.getElementById('home-demo-motion-content');
      content.dataset.view = String(motionView);
      content.innerHTML = motionView === 1
        ? '<small>VIEW 01</small><strong>概览视图</strong><span>内容会平滑切换，而不是突然消失。</span>'
        : '<small>VIEW 02</small><strong>详情视图</strong><span>新的内容进入，阅读位置保持稳定。</span>';
      content.classList.remove('is-changing');
      void content.offsetWidth;
      content.classList.add('is-changing');
    });
  }

  const reference = document.querySelector('body.site-reference');
  if (reference) {
    const main = reference.querySelector('main.wrap');
    const filterRow = reference.querySelector('.chips-row, .nav-row');
    if (main && filterRow) {
      const sidebar = document.createElement('aside');
      sidebar.className = 'ref-sidebar';
      sidebar.setAttribute('aria-label', '按分类浏览');
      const sidebarHeading = document.createElement('p');
      sidebarHeading.className = 'ref-sidebar-heading';
      sidebarHeading.textContent = 'BROWSE / 按分类浏览';
      sidebar.append(sidebarHeading, filterRow);

      const categoryChips = filterRow.querySelector('.chips');
      if (categoryChips) {
        const scrollHint = document.createElement('span');
        scrollHint.className = 'ref-scroll-hint';
        scrollHint.textContent = '左右滑动查看更多 →';
        scrollHint.hidden = true;
        sidebarHeading.append(scrollHint);
        let hintDismissed = false;
        const syncScrollHint = () => {
          scrollHint.hidden = hintDismissed || categoryChips.scrollWidth <= categoryChips.clientWidth + 1;
        };
        categoryChips.addEventListener('scroll', () => {
          hintDismissed = true;
          scrollHint.hidden = true;
        }, { once: true, passive: true });
        requestAnimationFrame(syncScrollHint);
        window.addEventListener('resize', syncScrollHint);
      }

      const content = document.createElement('div');
      content.className = 'ref-main';
      content.append(...main.children);
      main.classList.add('ref-layout');
      main.append(sidebar, content);

      const intro = content.querySelector('.hint, .intro');
      if (intro) {
        const guide = document.createElement('details');
        guide.className = 'ref-guide';
        const summary = document.createElement('summary');
        summary.textContent = '如何使用这份速查';
        intro.before(guide);
        guide.append(summary, intro);
      }
      const pauseAll = content.querySelector('#pauseAll');
      if (pauseAll) {
        const tools = document.createElement('div');
        tools.className = 'ref-tools';
        content.querySelector('.ref-guide')?.after(tools);
        tools.append(pauseAll);
      }
    }
  }

  const cards = document.querySelectorAll('article.cmp[id], article.effect-card[id]');

  async function copyLink(value) {
    if (navigator.clipboard?.writeText) {
      try {
        await navigator.clipboard.writeText(value);
        return true;
      } catch (_) {
        // The fallback also works on local HTTP and older browsers.
      }
    }
    const field = document.createElement('textarea');
    field.value = value;
    field.style.cssText = 'position:fixed;left:-9999px;opacity:0';
    document.body.appendChild(field);
    field.select();
    let copied = false;
    try { copied = document.execCommand('copy'); } catch (_) { /* Clipboard unavailable. */ }
    field.remove();
    return copied;
  }

  for (const card of cards) {
    const heading = card.querySelector('h2, h3')?.textContent?.trim() || '当前条目';
    const row = document.createElement('div');
    row.className = 'site-card-tools';

    const direct = document.createElement('a');
    direct.href = `#${card.id}`;
    direct.textContent = '# 直达此条';
    direct.setAttribute('aria-label', `定位到${heading}`);

    const copy = document.createElement('button');
    copy.type = 'button';
    copy.textContent = '复制链接';
    copy.setAttribute('aria-label', `复制${heading}的链接`);
    copy.addEventListener('click', async () => {
      const url = new URL(location.href);
      url.hash = card.id;
      const ok = await copyLink(url.href);
      copy.textContent = ok ? '已复制 ✓' : '复制失败，请使用直达链接';
      copy.dataset.copied = String(ok);
      clearTimeout(copy._resetTimer);
      copy._resetTimer = setTimeout(() => {
        copy.textContent = '复制链接';
        delete copy.dataset.copied;
      }, 2500);
    });

    row.append(direct, copy);
    card.append(row);
  }

  function revealLinkedCard() {
    let id;
    try { id = decodeURIComponent(location.hash.slice(1)); } catch (_) { return; }
    const card = id && document.getElementById(id);
    if (!card || !card.matches('article.cmp, article.effect-card')) return;

    const all = document.querySelector('.fchip[data-cat="all"], .chip[data-filter="all"]');
    all?.click();
    const search = document.getElementById('q');
    if (search?.value) {
      search.value = '';
      search.dispatchEvent(new Event('input', { bubbles: true }));
    }
    requestAnimationFrame(() => card.scrollIntoView({ behavior: 'instant', block: 'start' }));
  }

  window.addEventListener('hashchange', revealLinkedCard);
  if (location.hash) requestAnimationFrame(revealLinkedCard);
})();

/* 滚动进度线 + 返回顶部（全内容页） */
(function(){
  const bar=document.createElement('div');bar.className='site-progress';document.body.appendChild(bar);
  const btn=document.createElement('button');btn.type='button';btn.className='site-top-btn';
  btn.textContent='↑';btn.setAttribute('aria-label','返回顶部');btn.hidden=true;
  document.body.appendChild(btn);
  function upd(){
    const max=document.documentElement.scrollHeight-document.documentElement.clientHeight;
    bar.style.width=(max>0?(document.documentElement.scrollTop/max)*100:0)+'%';
    btn.hidden=document.documentElement.scrollTop<600;
  }
  addEventListener('scroll',upd,{passive:true});upd();
  btn.addEventListener('click',()=>{
    scrollTo({top:0,behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});
  });
})();

/* 滚动进度线 + 返回顶部（全内容页） */
(function(){
  const bar=document.createElement('div');bar.className='site-progress';document.body.appendChild(bar);
  const btn=document.createElement('button');btn.type='button';btn.className='site-top-btn';
  btn.textContent='↑';btn.setAttribute('aria-label','返回顶部');btn.hidden=true;
  document.body.appendChild(btn);
  function upd(){
    const max=document.documentElement.scrollHeight-document.documentElement.clientHeight;
    bar.style.width=(max>0?(document.documentElement.scrollTop/max)*100:0)+'%';
    btn.hidden=document.documentElement.scrollTop<600;
  }
  addEventListener('scroll',upd,{passive:true});upd();
  btn.addEventListener('click',()=>{
    scrollTo({top:0,behavior:matchMedia('(prefers-reduced-motion: reduce)').matches?'instant':'smooth'});
  });
})();
