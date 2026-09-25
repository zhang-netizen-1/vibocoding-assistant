(() => {
  const root = document.querySelector('.site-guide');
  if (!root) return;
  const search = document.querySelector('#guide-search');
  const count = document.querySelector('#guide-count');
  const empty = document.querySelector('#guide-empty');
  const copyStatus = document.querySelector('#guide-copy-status');
  const cards = [...document.querySelectorAll('.guide-card')];

  function filterCards() {
    const query = search.value.trim().toLocaleLowerCase();
    let visible = 0;
    for (const card of cards) {
      const match = card.dataset.search.toLocaleLowerCase().includes(query);
      card.hidden = !match;
      if (match) visible++;
    }
    for (const section of document.querySelectorAll('.guide-section')) {
      section.hidden = !section.querySelector('.guide-card:not([hidden])');
    }
    count.textContent = `${visible} / ${cards.length} 个条目`;
    empty.hidden = visible !== 0;
  }
  search.addEventListener('input', filterCards);
  document.querySelector('#guide-clear').addEventListener('click', () => {
    search.value = '';
    filterCards();
    search.focus();
  });
  document.addEventListener('keydown', event => {
    if (event.key !== '/' || event.ctrlKey || event.metaKey || event.altKey) return;
    if (['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName) || document.activeElement.isContentEditable) return;
    event.preventDefault();
    search.focus();
  });

  function setText(stage, selector, value) {
    const element = stage.querySelector(selector);
    if (element) element.textContent = value;
  }

  function updateInteraction(stage, mode) {
    const demo = stage.dataset.demo;
    if (demo === 'validation') {
      const field = stage.querySelector('[data-field]');
      field.value = mode ? '新' : '新的灵感';
      field.setAttribute('aria-invalid', mode ? 'true' : 'false');
      const message = stage.querySelector('[data-message]');
      message.dataset.error = mode ? 'true' : 'false';
      message.textContent = mode ? '至少填写 4 个字符。' : '名称已填写，可以继续。';
    } else if (demo === 'submit') {
      setText(stage, '[data-message]', mode ? '模拟请求失败：输入已保留，可以重试。' : '演示提交成功，项目已创建。');
    } else if (demo === 'undo') {
      stage.querySelector('[data-task]').hidden = !mode;
      setText(stage, '[data-message]', mode ? '已撤销，条目恢复到原位置。' : '已删除条目，仍可撤销。');
    } else if (demo === 'bulk') {
      stage.querySelectorAll('.mini-task').forEach((task, index) => {
        task.textContent = `${mode ? '□' : '☑'}　${index ? '组件说明' : '首页草图'}`;
      });
      setText(stage, '[data-message]', mode ? '已清除选择。' : '已选 2 项，可批量操作。');
    } else if (demo === 'optimistic') {
      setText(stage, '[data-state-label]', mode ? '未收藏' : '已收藏');
      setText(stage, '[data-message]', mode ? '模拟失败：已回滚本地状态。' : '本地演示：已显示收藏状态。');
    } else if (demo === 'focus') {
      const buttons = stage.querySelectorAll('button');
      buttons[mode ? 0 : 1].focus();
      setText(stage, '[data-message]', mode ? '焦点已返回第一项。' : '焦点已移动到第二项。');
    }
  }

  function updateData(stage, mode) {
    const demo = stage.dataset.demo;
    const period = stage.querySelector('[data-period]');
    const graphic = stage.querySelector('[role="img"]');
    if (demo === 'line') {
      period.textContent = mode ? '上周' : '本周';
      const values = mode ? [38, 50, 46, 60, 54, 69] : [42, 58, 49, 74, 66, 88];
      stage.querySelector('.chart-line').setAttribute('points', mode ? '16,98 60,86 104,90 148,76 192,82 240,67' : '16,94 60,78 104,87 148,62 192,70 240,46');
      graphic.setAttribute('aria-label', `六日趋势折线：${values.join('、')}`);
      setText(stage, '[data-summary]', `六日数值：${values.join('、')} · 单位：次`);
    } else if (demo === 'bar') {
      period.textContent = mode ? '转化量' : '访问量';
      const values = mode ? [25, 40, 32, 48] : [42, 68, 54, 82];
      graphic.querySelectorAll('i').forEach((bar, index) => bar.style.setProperty('--h', `${values[index]}%`));
      graphic.setAttribute('aria-label', `四类${period.textContent}柱状对比：${values.join('、')}`);
      setText(stage, '[data-summary]', `A—D 四类${period.textContent}：${values.join('、')} · 单位：次`);
    } else if (demo === 'stacked' || demo === 'donut') {
      period.textContent = mode ? (demo === 'donut' ? '上月' : '上期') : (demo === 'donut' ? '本月' : '本期');
      const values = mode ? [35, 40, 25] : [45, 35, 20];
      graphic.setAttribute('aria-label', `总量 100，三类占比：${values.join('%、')}%`);
      setText(stage, '.mini-legend', `自然 ${values[0]}% · 推荐 ${values[1]}% · 直接 ${values[2]}%`);
      setText(stage, '[data-summary]', '三类占比合计 100% · 演示数据');
    } else if (demo === 'heatmap') {
      period.textContent = mode ? '完成率' : '活跃度';
      const cells = graphic.querySelectorAll('i');
      cells.forEach((cell, index) => {
        const level = mode ? (index * 3 + Math.floor(index / 7)) % 5 : (index * 7 + Math.floor(index / 4) * 3) % 5;
        cell.dataset.level = String(level);
        cell.setAttribute('title', `第 ${Math.floor(index / 7) + 1} 时段，周${'一二三四五六日'[index % 7]}：等级 ${level}`);
      });
      graphic.setAttribute('aria-label', `周一至周日、四个时段的${period.textContent}矩阵；颜色从浅到深表示 0 至 4 级`);
      setText(stage, '[data-summary]', `${period.textContent}等级：浅色低，深色高；悬停可查看每格数值。`);
    } else if (demo === 'table') {
      period.textContent = mode ? '按数值' : '按名称';
      const body = stage.querySelector('tbody');
      const rows = [...body.querySelectorAll('tr')];
      rows.sort((a, b) => mode ? Number(b.cells[1].textContent) - Number(a.cells[1].textContent) : a.cells[0].textContent.localeCompare(b.cells[0].textContent, 'zh-CN'));
      rows.forEach(row => body.append(row));
      stage.querySelectorAll('th').forEach((th, index) => th.setAttribute('aria-sort', (mode ? index === 1 : index === 0) ? (mode ? 'descending' : 'ascending') : 'none'));
      setText(stage, '[data-summary]', mode ? '按访问量从高到低排序 · 单位：次' : '按渠道名称排序 · 单位：次');
    }
  }

  for (const card of cards) {
    const stage = card.querySelector('.guide-card-stage');
    if (root.dataset.guide === 'data') updateData(stage, 0);
    if (root.dataset.guide === 'interaction' && stage.dataset.demo !== 'focus') updateInteraction(stage, 0);
  }
  document.addEventListener('click', event => {
    const control = event.target.closest('.guide-card-controls button');
    if (control) {
      const card = control.closest('.guide-card');
      const stage = card.querySelector('.guide-card-stage');
      const mode = Number(control.dataset.mode);
      stage.dataset.mode = String(mode);
      card.querySelectorAll('.guide-card-controls button').forEach(button => button.setAttribute('aria-pressed', String(button === control)));
      if (root.dataset.guide === 'visual') {
        stage.querySelector('.style-preview').setAttribute('aria-label', `${card.querySelector('h3').textContent}：${mode ? '组件细节' : '页面预览'}`);
      }
      if (root.dataset.guide === 'interaction') updateInteraction(stage, mode);
      if (root.dataset.guide === 'data') updateData(stage, mode);
      if (stage.dataset.demo === 'sticky') stage.querySelector('.mini-layout').scrollTop = mode ? 95 : 0;
      return;
    }
    const promptButton = event.target.closest('.guide-copy');
    const linkButton = event.target.closest('.guide-copy-link');
    const button = promptButton || linkButton;
    if (!button) return;
    const value = promptButton
      ? button.closest('.guide-card-prompt').querySelector('.guide-prompt-text').textContent.trim()
      : `${location.origin}${location.pathname}#${button.closest('.guide-card').id}`;
    navigator.clipboard.writeText(value).then(() => {
      const original = button.textContent;
      button.textContent = '已复制';
      copyStatus.textContent = `已复制「${button.closest('.guide-card').querySelector('h3').textContent}」的${promptButton ? '提示词' : '链接'}。`;
      window.setTimeout(() => { button.textContent = original; }, 1800);
    }).catch(() => {
      button.textContent = '复制失败';
      copyStatus.textContent = '复制失败。请手动选择内容并复制。';
    });
  });
})();
