(() => {
  const page = document.querySelector('.site-skills');
  if (!page) return;
  const search = document.querySelector('#skill-search');
  const cards = [...document.querySelectorAll('.skill-card')];
  const count = document.querySelector('#skill-count');
  const empty = document.querySelector('#skill-empty');
  const copyStatus = document.querySelector('#skill-copy-status');

  function filter() {
    const query = search.value.trim().toLocaleLowerCase();
    let visible = 0;
    for (const card of cards) {
      card.hidden = !card.dataset.search.toLocaleLowerCase().includes(query);
      if (!card.hidden) visible++;
    }
    for (const section of document.querySelectorAll('.skill-section')) {
      section.hidden = !section.querySelector('.skill-card:not([hidden])');
    }
    count.textContent = `${visible} / ${cards.length} 个 Skill`;
    empty.hidden = visible !== 0;
  }

  search.addEventListener('input', filter);
  document.querySelector('#skill-clear').addEventListener('click', () => {
    search.value = '';
    filter();
    search.focus();
  });
  document.addEventListener('click', event => {
    const button = event.target.closest('.skill-copy');
    if (!button) return;
    const prompt = button.closest('.skill-install').querySelector('.skill-install-text').textContent.trim();
    navigator.clipboard.writeText(prompt).then(() => {
      button.textContent = '已复制';
      copyStatus.textContent = `已复制「${button.closest('.skill-card').querySelector('h3').firstChild.textContent.trim()}」的安装提示词。`;
      window.setTimeout(() => { button.textContent = '复制安装提示词'; }, 1800);
    }).catch(() => {
      button.textContent = '复制失败';
      copyStatus.textContent = '复制失败。请手动选择安装提示词并复制。';
    });
  });
})();
