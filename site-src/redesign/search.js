/* Pure search functions also run in Node unit tests, without a browser. */
'use strict';
const VibeSearch = (() => {
  const normalize = text => String(text || '').normalize('NFKC').toLowerCase().replace(/\s+/g, '');
  function rank(entry, query) {
    const q = normalize(query);
    if (!q) return 99;
    if (normalize(entry.zh) === q) return 0;
    if (String(entry.en || '').split('/').some(name => normalize(name) === q)) return 1;
    const aliases = entry.aliases || [];
    if (aliases.some(alias => normalize(alias) === q)) return 2;
    if (normalize(entry.zh).includes(q) || normalize(entry.en).includes(q)) return 3;
    if (aliases.some(alias => normalize(alias).includes(q))) return 4;
    if (normalize(entry.definition).includes(q)) return 5;
    return normalize(entry.terms).includes(q) ? 6 : 99;
  }
  function match(entries, query) {
    const q = normalize(query);
    return entries.map((entry,index) => {
      const priority = rank(entry, query);
      const alias = priority === 2 || priority === 4
        ? entry.aliases.find(value => priority === 2 ? normalize(value) === q : normalize(value).includes(q))
        : '';
      return {entry,index,rank:priority,alias};
    }).filter(row => row.rank < 99).sort((a,b) => a.rank-b.rank || a.index-b.index);
  }
  function aliasLabel(row) {
    return row.alias ? '也叫：' + row.alias : '';
  }
  function similar(entries, query) {
    const queryChars = new Set(normalize(query));
    return entries.map((entry,index) => ({entry,index,score:[...new Set(normalize(entry.zh + entry.en))].filter(char => queryChars.has(char)).length})).sort((a,b) => b.score-a.score || a.index-b.index).slice(0,3).map(row => row.entry);
  }
  return {normalize,rank,match,similar,aliasLabel};
})();
if (typeof module !== 'undefined') module.exports = VibeSearch;
