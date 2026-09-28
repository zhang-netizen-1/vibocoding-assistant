(() => {
  const entries = JSON.parse(document.getElementById('home-search-index').textContent);
  const input = document.getElementById('global-search');
  const results = document.getElementById('search-results');
  const categories = document.getElementById('directory-categories');
  const list = document.getElementById('result-list');
  const count = document.getElementById('result-count');
  const empty = document.getElementById('result-empty');
  const clearButton = document.getElementById('clear-search');

  const normalize = (value) => value.normalize('NFKC').toLocaleLowerCase().trim();

  function matches(query) {
    const tokens = normalize(query).split(/\s+/).filter(Boolean);
    return entries.map((entry, index) => {
      const title = normalize(entry.title);
      const category = normalize(entry.category);
      const terms = normalize(entry.terms);
      const description = normalize(entry.description);
      const haystack = `${title} ${category} ${terms} ${description}`;
      if (!tokens.every((token) => haystack.includes(token))) return null;
      const phrase = normalize(query);
      const score = title === phrase ? 100 : title.startsWith(phrase) ? 80 : title.includes(phrase) ? 60
        : terms.includes(phrase) ? 35 : category.includes(phrase) ? 20 : 10;
      return { entry, index, score };
    }).filter(Boolean).sort((a, b) => b.score - a.score || a.index - b.index);
  }

  function createResult(entry) {
    const link = document.createElement('a');
    link.className = 'directory-result';
    link.href = entry.href;
    const category = document.createElement('span');
    category.className = 'directory-result-category';
    category.textContent = entry.category;
    const title = document.createElement('strong');
    title.textContent = entry.title;
    const description = document.createElement('p');
    description.textContent = entry.description;
    const arrow = document.createElement('span');
    arrow.setAttribute('aria-hidden', 'true');
    arrow.textContent = '↗';
    link.append(category, title, description, arrow);
    return link;
  }

  function update() {
    const query = input.value.trim();
    const searching = Boolean(query);
    results.hidden = !searching;
    categories.hidden = searching;
    if (!searching) {
      list.replaceChildren();
      count.textContent = '';
      empty.hidden = true;
      return;
    }
    const found = matches(query);
    list.replaceChildren(...found.map(({ entry }) => createResult(entry)));
    count.textContent = `找到 ${found.length} 个匹配条目`;
    empty.hidden = found.length > 0;
  }

  input.addEventListener('input', update);
  input.addEventListener('keydown', (event) => {
    if (event.key === 'Escape') {
      input.value = '';
      update();
    } else if (event.key === 'Enter' && list.firstElementChild) {
      event.preventDefault();
      window.location.assign(list.firstElementChild.href);
    } else if (event.key === 'ArrowDown' && list.firstElementChild) {
      event.preventDefault();
      list.firstElementChild.focus();
    }
  });
  clearButton.addEventListener('click', () => {
    input.value = '';
    update();
    input.focus();
  });
  document.addEventListener('keydown', (event) => {
    if (event.key === '/' && !event.metaKey && !event.ctrlKey && !event.altKey
        && !['INPUT', 'TEXTAREA'].includes(document.activeElement.tagName)) {
      event.preventDefault();
      input.focus();
    }
  });
})();
