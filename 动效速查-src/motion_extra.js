/* Extra examples use isolated event handling so the original 47 studies stay stable. */
(() => {
  const smallMotion = () => !reduce.matches;
  const sceneOf = element => element.closest('.extra-scene');
  const stageOf = element => element.closest('.stage');
  const visibleChildren = parent => [...parent.children].filter(child => !child.hidden);
  const positions = parent => new Map(visibleChildren(parent).map(child => [child, child.getBoundingClientRect()]));
  function animatePositions(parent, before) {
    if (!smallMotion()) return;
    for (const child of visibleChildren(parent)) {
      const old = before.get(child);
      if (!old) {
        child.animate([{opacity: 0, transform: 'translateY(8px) scale(.96)'}, {opacity: 1, transform: 'none'}], {duration: 300, easing: 'ease-out'});
        continue;
      }
      const now = child.getBoundingClientRect();
      const dx = old.left - now.left, dy = old.top - now.top;
      if (Math.abs(dx) + Math.abs(dy) > 1) child.animate([{transform: `translate(${dx}px, ${dy}px)`}, {transform: 'none'}], {duration: 360, easing: 'cubic-bezier(.2,.8,.2,1)'});
    }
  }

  let filterTimer;
  function filterGallery(button) {
    const scene = sceneOf(button), grid = scene.querySelector('.extra-gallery');
    const selected = button.dataset.value;
    clearTimeout(filterTimer);
    scene.querySelectorAll('.extra-filter-tabs button').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    grid.querySelectorAll('.extra-gallery-tile').forEach(tile => tile.classList.remove('leaving'));
    const applyFilter = () => {
      const before = positions(grid);
      let count = 0;
      grid.querySelectorAll('.extra-gallery-tile').forEach(tile => {
        tile.hidden = selected !== '全部' && tile.dataset.type !== selected;
        if (!tile.hidden) count++;
      });
      grid.querySelector('.extra-filter-empty').hidden = count > 0;
      scene.querySelector('.extra-status').textContent = `显示 ${count} 个作品`;
      animatePositions(grid, before);
    };
    if (!smallMotion()) { applyFilter(); return; }
    grid.querySelectorAll('.extra-gallery-tile:not([hidden])').forEach(tile => {
      if (selected !== '全部' && tile.dataset.type !== selected) tile.classList.add('leaving');
    });
    filterTimer = setTimeout(applyFilter, 180);
  }

  let undoTimer, undoTick, removedRow;
  function endUndo(scene) {
    clearTimeout(undoTimer); clearInterval(undoTick);
    if (scene) scene.querySelector('.extra-undo').hidden = true;
    removedRow = null;
  }
  function deleteRow(button) {
    const scene = sceneOf(button), row = button.closest('.extra-task'), list = scene.querySelector('.extra-task-list');
    if (removedRow && !removedRow.hidden) removedRow.classList.remove('leaving');
    endUndo(scene);
    removedRow = row;
    row.classList.add('leaving');
    setTimeout(() => {
      if (removedRow !== row) return;
      const before = positions(list);
      row.hidden = true;
      animatePositions(list, before);
      const undo = scene.querySelector('.extra-undo');
      undo.hidden = false;
      let remaining = 5;
      undo.querySelector('b').textContent = remaining;
      undoTick = setInterval(() => {
        remaining--;
        if (remaining <= 0) { endUndo(scene); return; }
        undo.querySelector('b').textContent = remaining;
      }, 1000);
      undoTimer = setTimeout(() => endUndo(scene), 5000);
    }, smallMotion() ? 220 : 0);
  }
  function undoDelete(button) {
    const scene = sceneOf(button);
    if (!removedRow) return;
    const list = scene.querySelector('.extra-task-list'), before = positions(list), row = removedRow;
    row.hidden = false; row.classList.remove('leaving'); row.classList.add('entering');
    animatePositions(list, before);
    setTimeout(() => row.classList.remove('entering'), 300);
    endUndo(scene);
    row.querySelector('button').focus();
  }

  function toggleAccordion(button) {
    const scene = sceneOf(button), opening = button.getAttribute('aria-expanded') !== 'true';
    scene.querySelectorAll('.extra-faq button').forEach(item => {
      const active = opening && item === button;
      item.setAttribute('aria-expanded', String(active));
      item.nextElementSibling.setAttribute('aria-hidden', String(!active));
    });
  }

  let submitTimer;
  function submitScene(button) {
    const scene = sceneOf(button), outcome = scene.querySelector('.extra-outcomes [aria-pressed=true]').dataset.value;
    const input = scene.querySelector('input'), error = scene.querySelector('.extra-field-error'), status = scene.querySelector('.extra-status');
    clearTimeout(submitTimer);
    input.removeAttribute('aria-invalid'); error.textContent = '';
    button.disabled = true; button.classList.add('busy'); button.innerHTML = '处理中… <span aria-hidden="true">◌</span>';
    status.textContent = '正在处理演示请求…'; status.dataset.state = '';
    submitTimer = setTimeout(() => {
      button.disabled = false; button.classList.remove('busy');
      if (input.value.trim().length < 4) {
        button.innerHTML = '修改后重试 <span aria-hidden="true">↗</span>';
        input.setAttribute('aria-invalid', 'true'); error.textContent = '请填写至少 4 个字符。';
        status.textContent = '演示校验失败，请检查项目名称。'; status.dataset.state = 'error'; input.focus();
      } else if (outcome === 'success' || outcome === 'invalid') {
        button.innerHTML = '再次提交 <span aria-hidden="true">↗</span>';
        status.textContent = '演示提交成功。'; status.dataset.state = 'success';
      } else {
        button.innerHTML = '重试提交 <span aria-hidden="true">↗</span>';
        status.textContent = '演示网络失败，内容已保留。'; status.dataset.state = 'error';
      }
    }, smallMotion() ? 520 : 0);
  }

  let noticeNumber = 0;
  function addNotice(button) {
    const list = sceneOf(button).querySelector('.extra-toast-list'), before = positions(list);
    const notices = ['新的内容已加入', '更改已保存', '任务已完成', '资料已更新'];
    const item = document.createElement('div');
    item.className = 'extra-notice entering';
    item.innerHTML = `<span>${notices[noticeNumber++ % notices.length]}</span><button type="button" data-extra-action="remove-toast" aria-label="关闭通知">×</button>`;
    list.append(item);
    const visible = visibleChildren(list);
    if (visible.length > 3) visible[0].remove();
    animatePositions(list, before);
    setTimeout(() => item.classList.remove('entering'), 300);
  }
  function removeNotice(button) {
    const item = button.closest('.extra-notice'), list = item.parentElement;
    item.classList.add('leaving');
    setTimeout(() => {
      const before = positions(list);
      item.remove(); animatePositions(list, before);
    }, smallMotion() ? 200 : 0);
  }

  const tabData = [
    {number: '24', label: '本周浏览', note: '较上周 ↑ 12%'},
    {number: '08', label: '最新活动', note: '3 项等待处理'},
    {number: '03', label: '偏好设置', note: '个性化选项'}
  ];
  function selectTab(button, focus = false) {
    const tabs = [...button.parentElement.querySelectorAll('[role=tab]')], index = tabs.indexOf(button);
    tabs.forEach(tab => {const active = tab === button; tab.setAttribute('aria-selected', String(active)); tab.tabIndex = active ? 0 : -1;});
    button.parentElement.querySelector('.extra-tab-indicator').style.transform = `translateX(${index * 100}%)`;
    const content = sceneOf(button).querySelector('.extra-tab-content');
    content.setAttribute('aria-labelledby', button.id);
    content.querySelector('.extra-stat-number').textContent = tabData[index].number;
    content.querySelector('strong').textContent = tabData[index].label;
    content.querySelector('small').textContent = tabData[index].note;
    content.classList.remove('changing'); void content.offsetWidth; content.classList.add('changing');
    if (focus) button.focus();
  }

  function commitDrop(scene, target) {
    const chip = scene.querySelector('.extra-drag-chip'), zone = scene.querySelector(`.extra-drop-target[data-target="${target}"]`);
    const before = chip.getBoundingClientRect();
    chip.style.transform = ''; chip.style.transition = ''; chip.style.pointerEvents = '';
    zone.append(chip);
    const after = chip.getBoundingClientRect();
    if (smallMotion()) chip.animate([{transform: `translate(${before.left - after.left}px, ${before.top - after.top}px)`}, {transform: 'none'}], {duration: 310, easing: 'cubic-bezier(.2,.8,.2,1)'});
    scene.querySelectorAll('.extra-drop-target').forEach(el => el.classList.toggle('is-selected', el === zone));
    scene.querySelector('.extra-status').textContent = `已放入「${target}」；可继续拖动或重置。`;
  }
  function resetDrop(scene) {
    const chip = scene.querySelector('.extra-drag-chip');
    chip.style.transform = ''; chip.style.transition = ''; chip.style.pointerEvents = '';
    scene.querySelector('.extra-drop-source').append(chip);
    scene.querySelectorAll('.extra-drop-target').forEach(el => el.classList.remove('is-selected', 'is-near'));
    scene.querySelector('.extra-status').textContent = '拖到目标区域，或使用下方按钮。';
  }
  const dragChip = document.querySelector('#e-extra-drop-snap .extra-drag-chip');
  dragChip.addEventListener('pointerdown', event => {
    if (event.pointerType === 'mouse' && event.button !== 0) return;
    event.preventDefault();
    const chip = event.currentTarget, scene = sceneOf(chip), startX = event.clientX, startY = event.clientY;
    chip.setPointerCapture(event.pointerId); chip.classList.add('dragging'); chip.style.pointerEvents = 'none';
    function move(ev) {
      chip.style.transform = `translate(${ev.clientX - startX}px, ${ev.clientY - startY}px)`;
      const found = document.elementFromPoint(ev.clientX, ev.clientY)?.closest('.extra-drop-target');
      scene.querySelectorAll('.extra-drop-target').forEach(zone => zone.classList.toggle('is-near', zone === found));
    }
    function end(ev) {
      chip.removeEventListener('pointermove', move); chip.removeEventListener('pointerup', end); chip.removeEventListener('pointercancel', end);
      chip.classList.remove('dragging');
      const found = ev.type === 'pointercancel' ? null : document.elementFromPoint(ev.clientX, ev.clientY)?.closest('.extra-drop-target');
      scene.querySelectorAll('.extra-drop-target').forEach(zone => zone.classList.remove('is-near'));
      if (found && scene.contains(found)) commitDrop(scene, found.dataset.target);
      else {
        const from = chip.style.transform; chip.style.transform = '';
        if (smallMotion()) chip.animate([{transform: from || 'none'}, {transform: 'none'}], {duration: 280, easing: 'ease-out'});
        chip.style.pointerEvents = '';
        scene.querySelector('.extra-status').textContent = '未放入目标区域，任务已回到原位。';
      }
    }
    chip.addEventListener('pointermove', move); chip.addEventListener('pointerup', end); chip.addEventListener('pointercancel', end);
  });
  dragChip.addEventListener('keydown', event => {if (event.key === 'Enter' || event.key === ' ') {event.preventDefault(); commitDrop(sceneOf(dragChip), '今天');}});

  const odometer = document.querySelector('#e-extra-odometer .extra-digits');
  let currentNumber = 198, rolling = false;
  function initializeDigits(number) {
    odometer.innerHTML = '';
    for (const digit of String(number)) {
      const shell = document.createElement('span'); shell.className = 'extra-digit';
      const track = document.createElement('span'); track.className = 'extra-digit-track';
      track.innerHTML = Array.from({length: 20}, (_, i) => `<span>${i % 10}</span>`).join('');
      track.style.transform = `translateY(-${Number(digit) * 47}px)`;
      shell.append(track); odometer.append(shell);
    }
  }
  initializeDigits(currentNumber);
  function rollDigits(button) {
    if (rolling) return;
    rolling = true; button.disabled = true;
    const target = currentNumber === 198 ? 205 : 198;
    const tracks = [...odometer.querySelectorAll('.extra-digit-track')];
    const from = String(currentNumber), to = String(target);
    tracks.forEach((track, i) => {
      const source = Number(from[i]), destination = Number(to[i]);
      const step = destination >= source ? destination : destination + 10;
      track.style.transition = smallMotion() ? `transform ${570 + i * 110}ms cubic-bezier(.19,.76,.23,1)` : 'none';
      track.style.transform = `translateY(-${step * 47}px)`;
    });
    setTimeout(() => {
      currentNumber = target;
      tracks.forEach((track, i) => {track.style.transition = 'none'; track.style.transform = `translateY(-${Number(to[i]) * 47}px)`;});
      odometer.setAttribute('aria-label', `当前数值 ${target}`);
      sceneOf(button).querySelector('.extra-number-footer b').textContent = target === 205 ? '＋7' : '－7';
      button.disabled = false; rolling = false;
    }, smallMotion() ? 850 : 0);
  }

  function updateHeader(scroller) {
    const progress = reduce.matches ? 0 : Math.min(1, scroller.scrollTop / 65), header = scroller.querySelector('.extra-scroll-header');
    header.style.setProperty('--scroll-progress', progress);
    header.style.minHeight = `${94 - 42 * progress}px`;
    header.style.paddingBlock = `${10 - 5 * progress}px`;
  }
  const headerScroll = document.querySelector('#e-extra-shrink-header .extra-header-scroll');
  headerScroll.addEventListener('scroll', () => updateHeader(headerScroll), {passive: true});
  reduce.addEventListener('change', () => updateHeader(headerScroll));
  const sectionScroll = document.querySelector('#e-extra-section-nav .extra-section-scroll');
  function updateSectionNav() {
    const index = Math.max(0, Math.min(2, Math.round(sectionScroll.scrollTop / 170)));
    sectionScroll.closest('.extra-scene').querySelectorAll('.extra-section-links button').forEach((button, i) => {
      if (i === index) button.setAttribute('aria-current', 'true'); else button.removeAttribute('aria-current');
    });
  }
  sectionScroll.addEventListener('scroll', updateSectionNav, {passive: true});
  const highlightScroll = document.querySelector('#e-extra-scroll-highlight .extra-highlight-scroll');
  function updateHighlight() {
    const total = highlightScroll.scrollHeight - highlightScroll.clientHeight;
    const count = Math.min(4, Math.max(0, Math.round(highlightScroll.scrollTop / total * 4)));
    highlightScroll.querySelectorAll('.extra-highlight-text span').forEach((span, i) => span.classList.toggle('lit', i < count));
  }
  highlightScroll.addEventListener('scroll', updateHighlight, {passive: true});
  const snapScroll = document.querySelector('#e-extra-snap-sections .extra-snap-scroll');
  snapScroll.addEventListener('scroll', () => {
    const index = Math.max(0, Math.min(2, Math.round(snapScroll.scrollTop / 168)));
    snapScroll.closest('.extra-scene').querySelector('.extra-snap-status').textContent = `当前章节 0${index + 1} / 03`;
  }, {passive: true});

  const art = document.querySelector('#e-extra-image-magnifier .extra-magnifier-art');
  function moveMagnifier(x, y) {
    const lens = art.querySelector('.extra-magnifier-lens');
    const clampedX = Math.max(0, Math.min(1, x)), clampedY = Math.max(0, Math.min(1, y));
    art.classList.add('active');
    lens.style.left = `${reduce.matches ? art.clientWidth - 78 : Math.max(0, Math.min(art.clientWidth - 70, clampedX * art.clientWidth - 35))}px`;
    lens.style.top = `${reduce.matches ? 8 : Math.max(0, Math.min(art.clientHeight - 70, clampedY * art.clientHeight - 35))}px`;
    lens.style.backgroundPosition = `${clampedX * 100}% ${clampedY * 100}%`;
  }
  art.addEventListener('pointermove', event => {
    const rect = art.getBoundingClientRect(); moveMagnifier((event.clientX - rect.left) / rect.width, (event.clientY - rect.top) / rect.height);
  });
  art.addEventListener('pointerleave', event => {if (event.pointerType === 'mouse') art.classList.remove('active');});
  art.addEventListener('keydown', event => {
    if (event.key === 'Escape') {art.classList.remove('active'); return;}
    if (!event.key.startsWith('Arrow')) return;
    event.preventDefault();
    const x = Number(art.dataset.x || .5) + (event.key === 'ArrowRight' ? .1 : event.key === 'ArrowLeft' ? -.1 : 0);
    const y = Number(art.dataset.y || .5) + (event.key === 'ArrowDown' ? .1 : event.key === 'ArrowUp' ? -.1 : 0);
    art.dataset.x = Math.max(0, Math.min(1, x)); art.dataset.y = Math.max(0, Math.min(1, y));
    moveMagnifier(Number(art.dataset.x), Number(art.dataset.y));
  });

  const timeline = document.querySelector('#e-extra-timeline-preview input[type=range]');
  let committedTime = Number(timeline.value);
  const timecode = value => `00:${String(value).padStart(2, '0')}`;
  function previewTime(value) {
    const scene = sceneOf(timeline), bubble = scene.querySelector('.extra-preview-bubble');
    bubble.classList.add('show'); bubble.style.left = `${16 + value / 48 * (scene.clientWidth - 105)}px`;
    bubble.querySelector('span').textContent = timecode(value);
    bubble.querySelector('.extra-preview-image').style.setProperty('--frame-hue', `${value * 3}deg`);
  }
  timeline.addEventListener('input', () => previewTime(Number(timeline.value)));
  timeline.addEventListener('change', () => {
    committedTime = Number(timeline.value);
    const scene = sceneOf(timeline);
    scene.querySelector('.extra-video-landscape').style.setProperty('--frame-hue', `${committedTime * 3}deg`);
    scene.querySelector('.extra-video-time').textContent = `${timecode(committedTime)} / 00:48`;
    scene.querySelector('.extra-preview-bubble').classList.remove('show');
    scene.querySelector('.extra-status').textContent = `已跳转到 ${timecode(committedTime)}。`;
  });
  timeline.addEventListener('keydown', event => {
    if (event.key !== 'Escape') return;
    event.preventDefault(); timeline.value = committedTime;
    sceneOf(timeline).querySelector('.extra-preview-bubble').classList.remove('show');
    sceneOf(timeline).querySelector('.extra-status').textContent = `已取消，仍在 ${timecode(committedTime)}。`;
  });
  timeline.addEventListener('pointercancel', () => {
    timeline.value = committedTime;
    sceneOf(timeline).querySelector('.extra-preview-bubble').classList.remove('show');
    sceneOf(timeline).querySelector('.extra-status').textContent = `已取消，仍在 ${timecode(committedTime)}。`;
  });

  const chartValues = {current: [42, 68, 54, 82, 63], previous: [58, 37, 72, 49, 44]};
  function switchChart(button) {
    const scene = sceneOf(button), key = button.dataset.value, values = chartValues[key];
    scene.querySelectorAll('.extra-chart-controls button').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
    scene.querySelectorAll('.extra-chart i').forEach((bar, i) => bar.style.setProperty('--bar', `${values[i]}%`));
    const label = key === 'current' ? '本周' : '上周';
    scene.querySelector('.extra-chart').setAttribute('aria-label', `${label}访问趋势：${values.map((n, i) => `周${'一二三四五'[i]} ${n}`).join('，')}`);
    scene.querySelector('.extra-status').textContent = `${label}访问总量 ${values.reduce((sum, value) => sum + value, 0)}`;
  }

  let handoffTimer;
  function handoff(button) {
    const scene = sceneOf(button), skeleton = scene.querySelector('.extra-content-skeleton'), real = scene.querySelector('.extra-content-real');
    clearTimeout(handoffTimer);
    real.hidden = true; real.classList.remove('entering'); skeleton.hidden = false; skeleton.classList.remove('leaving'); skeleton.classList.add('loading');
    button.disabled = true; button.textContent = '正在模拟加载…';
    handoffTimer = setTimeout(() => {
      skeleton.classList.remove('loading'); skeleton.classList.add('leaving');
      setTimeout(() => {
        skeleton.hidden = true; real.hidden = false; real.classList.add('entering');
        button.disabled = false; button.textContent = '重新演示';
      }, smallMotion() ? 230 : 0);
    }, smallMotion() ? 520 : 0);
  }

  document.addEventListener('click', event => {
    const button = event.target.closest('[data-extra-action]');
    if (!button) return;
    const scene = sceneOf(button), action = button.dataset.extraAction;
    if (action === 'filter') filterGallery(button);
    else if (action === 'delete') deleteRow(button);
    else if (action === 'undo') undoDelete(button);
    else if (action === 'accordion') toggleAccordion(button);
    else if (action === 'outcome') {
      scene.querySelectorAll('.extra-outcomes button').forEach(item => item.setAttribute('aria-pressed', String(item === button)));
      scene.querySelector('.extra-field input').value = button.dataset.value === 'invalid' ? '新' : '新的灵感';
      scene.querySelector('.extra-status').textContent = '已选择演示结果；点击模拟提交。';
    }
    else if (action === 'submit') submitScene(button);
    else if (action === 'add-toast') addNotice(button);
    else if (action === 'remove-toast') removeNotice(button);
    else if (action === 'tab') selectTab(button);
    else if (action === 'drop') commitDrop(scene, button.dataset.value);
    else if (action === 'reset-drop') resetDrop(scene);
    else if (action === 'roll') rollDigits(button);
    else if (action === 'reset-page') scene.querySelector('iframe').src = 'motion-demo-gallery.html';
    else if (action === 'expand') button.setAttribute('aria-expanded', String(button.getAttribute('aria-expanded') !== 'true'));
    else if (action === 'section') sectionScroll.scrollTo({top: (Number(button.dataset.target) - 1) * 170, behavior: reduce.matches ? 'instant' : 'smooth'});
    else if (action === 'reset-magnifier') art.classList.remove('active');
    else if (action === 'chart') switchChart(button);
    else if (action === 'load-content') handoff(button);
  });
  document.querySelector('#e-extra-tab-indicator .extra-tabs').addEventListener('keydown', event => {
    if (!['ArrowLeft', 'ArrowRight', 'Home', 'End'].includes(event.key)) return;
    event.preventDefault();
    const tabs = [...event.currentTarget.querySelectorAll('[role=tab]')], index = tabs.findIndex(tab => tab.getAttribute('aria-selected') === 'true');
    const next = event.key === 'Home' ? 0 : event.key === 'End' ? tabs.length - 1 : (index + (event.key === 'ArrowRight' ? 1 : -1) + tabs.length) % tabs.length;
    selectTab(tabs[next], true);
  });
})();

/* ===== P0-2 新增动效演示 ===== */
const coarsePointer=matchMedia('(pointer: coarse)');
/* 磁吸按钮 */
document.querySelectorAll('.magnet-wrap').forEach(wrap=>{
  const btn=wrap.querySelector('.magnet-btn'),label=wrap.querySelector('.magnet-label');
  wrap.addEventListener('pointermove',e=>{
    if(coarsePointer.matches||reduce.matches)return;
    const r=btn.getBoundingClientRect(),cx=r.left+r.width/2,cy=r.top+r.height/2;
    const dx=(e.clientX-cx)/r.width,dy=(e.clientY-cy)/r.height;
    btn.style.transform=`translate(${dx*14}px,${dy*12}px)`;
    label.style.transform=`translate(${dx*5}px,${dy*4}px)`;
  });
  wrap.addEventListener('pointerleave',()=>{btn.style.transform='';label.style.transform='';});
});
/* 悬停操作栏键盘可达（focus-within 已由 CSS 处理） */
/* 文字变形（定时轮换，尊重暂停与减少动态） */
document.querySelectorAll('.morph-stage').forEach(stage=>{
  const word=stage.querySelector('.morph-word'),cur=word.querySelector('.mw-cur'),next=word.querySelector('.mw-next');
  const words=['快速设计','稳定开发','顺畅部署'];let idx=0,switching=false;
  function paused(){return document.hidden||stage.closest('.effect-card').classList.contains('is-paused')||document.getElementById('pauseAll').getAttribute('aria-pressed')==='true'}
  setInterval(()=>{
    if(reduce.matches||paused()||switching)return;
    switching=true;
    idx=(idx+1)%words.length;
    next.textContent=words[idx];
    word.style.width=next.offsetWidth+'px';
    word.classList.add('morphing');
    setTimeout(()=>{
      cur.textContent=words[idx];
      word.classList.remove('morphing');
      switching=false;
    },320);
  },2300);
});
/* 错误抖动 */
document.querySelectorAll('.shake-demo').forEach(demo=>{
  const input=demo.querySelector('.shake-input'),go=demo.querySelector('.shake-go'),err=demo.querySelector('.shake-err');
  go.addEventListener('click',()=>{
    const valid=/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(input.value.trim());
    if(valid){err.hidden=true;input.classList.remove('shake');toast('提交成功（演示）');return;}
    if(reduce.matches){err.hidden=false;return;}
    input.classList.remove('shake');void input.offsetWidth;input.classList.add('shake');
    err.hidden=false;
  });
  input.addEventListener('animationend',()=>input.classList.remove('shake'));
});
/* 自定义光标跟随 */
document.querySelectorAll('.cf-stage').forEach(stage=>{
  const dot=stage.querySelector('.cf-dot'),ring=stage.querySelector('.cf-ring'),target=stage.querySelector('.cf-target');
  if(coarsePointer.matches){stage.style.cursor='auto';dot.style.display='none';ring.style.display='none';return;}
  stage.addEventListener('pointermove',e=>{
    const r=stage.getBoundingClientRect();
    dot.style.transform=`translate(${e.clientX-r.left}px,${e.clientY-r.top}px)`;
    ring.style.translate=`${e.clientX-r.left}px ${e.clientY-r.top}px`;
  });
  target.addEventListener('pointerenter',()=>ring.classList.add('big'));
  target.addEventListener('pointerleave',()=>ring.classList.remove('big'));
  stage.addEventListener('pointerleave',()=>{dot.style.opacity='0';ring.style.opacity='0';});
  stage.addEventListener('pointerenter',()=>{dot.style.opacity='1';ring.style.opacity='1';});
});
/* 光标拖尾 */
document.querySelectorAll('.trail-stage').forEach(stage=>{
  let last=0;
  stage.addEventListener('pointermove',e=>{
    if(coarsePointer.matches||reduce.matches)return;
    const now=performance.now();
    if(now-last<26)return;last=now;
    const r=stage.getBoundingClientRect();
    if(stage.querySelectorAll('.trail-dot').length>26)return;
    const d=document.createElement('span');d.className='trail-dot';
    d.style.left=(e.clientX-r.left)+'px';d.style.top=(e.clientY-r.top)+'px';
    d.addEventListener('animationend',()=>d.remove());
    stage.appendChild(d);
  });
});
/* 鼠标跟随眼睛 */
document.querySelectorAll('.eyes-stage').forEach(stage=>{
  const pupils=[...stage.querySelectorAll('.eye i')];
  stage.addEventListener('pointermove',e=>{
    if(coarsePointer.matches)return;
    pupils.forEach(p=>{
      const eye=p.parentElement,r=eye.getBoundingClientRect();
      const cx=r.left+r.width/2,cy=r.top+r.height/2;
      const ang=Math.atan2(e.clientY-cy,e.clientX-cx),dist=Math.min(13,Math.hypot(e.clientX-cx,e.clientY-cy)/6);
      p.style.transform=`translate(${Math.cos(ang)*dist}px,${Math.sin(ang)*dist}px)`;
    });
  });
  stage.addEventListener('pointerleave',()=>pupils.forEach(p=>p.style.transform=''));
});
/* 3D 物体跟随 */
document.querySelectorAll('.obj-stage').forEach(stage=>{
  const card=stage.querySelector('.obj-card');
  stage.addEventListener('pointermove',e=>{
    if(coarsePointer.matches||reduce.matches)return;
    const r=stage.getBoundingClientRect(),x=(e.clientX-r.left)/r.width-.5,y=(e.clientY-r.top)/r.height-.5;
    card.style.transform=`rotateX(${(-y*16).toFixed(2)}deg) rotateY(${(x*18).toFixed(2)}deg)`;
  });
  stage.addEventListener('pointerleave',()=>card.style.transform='');
});
/* 图片序列：滚动进度映射到帧 */
document.querySelectorAll('.seq-scroll').forEach(scroller=>{
  const box=scroller.querySelector('.seq-box'),cap=scroller.querySelector('.seq-caption');
  function frame(){
    const total=scroller.scrollHeight-scroller.clientHeight;
    const p=total?Math.max(0,Math.min(1,scroller.scrollTop/total)):0;
    const f=Math.round(p*5);
    scroller.dataset.frame=f;
    cap.textContent=`旋转 ${f*60}°`;
  }
  scroller.addEventListener('scroll',frame,{passive:true});frame();
});

/* 滚动隐藏页头 */
document.querySelectorAll('.hidehead-scroll').forEach(scroller=>{
  let lastTop=scroller.scrollTop;
  scroller.addEventListener('scroll',()=>{
    const delta=scroller.scrollTop-lastTop;
    if(delta>2)scroller.classList.add('scrolldown');
    else if(delta<-2)scroller.classList.remove('scrolldown');
    lastTop=scroller.scrollTop;
  },{passive:true});
});

/* 点击涟漪 */
document.querySelectorAll('.ripple-btn').forEach(btn=>{
  btn.addEventListener('click',e=>{
    if(reduce.matches)return;
    const ink=btn.querySelector('.ripple-ink'),r=btn.getBoundingClientRect();
    const d=document.createElement('i');
    d.style.left=(e.clientX-r.left)+'px';d.style.top=(e.clientY-r.top)+'px';
    ink.appendChild(d);
    d.addEventListener('animationend',()=>d.remove());
  });
});
/* 下划线展开：当前页切换 */
document.querySelectorAll('.uline-nav .uline').forEach(a=>a.addEventListener('click',()=>{
  document.querySelectorAll('.uline-nav .uline').forEach(x=>x.classList.toggle('on',x===a));
}));
