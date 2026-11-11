/* Pure search functions also run in Node unit tests, without a browser. */
'use strict';
const VibeSearch = (() => {
  const normalize = text => String(text || '').normalize('NFKC').toLowerCase().replace(/\s+/g, '');
  function rank(entry, query) {
    const q = normalize(query);
    if (!q) return 99;
    if (normalize(entry.zh) === q) return 0;
    if (normalize(entry.en).includes(q)) return 1;
    if (normalize(entry.terms).includes(q) || normalize(entry.zh).includes(q)) return 2;
    return normalize(entry.definition).includes(q) ? 3 : 99;
  }
  function match(entries, query) {
    return entries.map((entry,index) => ({entry,index,rank:rank(entry,query)})).filter(row => row.rank < 99).sort((a,b) => a.rank-b.rank || a.index-b.index);
  }
  function similar(entries, query) {
    const queryChars = new Set(normalize(query));
    return entries.map((entry,index) => ({entry,index,score:[...new Set(normalize(entry.zh + entry.en))].filter(char => queryChars.has(char)).length})).sort((a,b) => b.score-a.score || a.index-b.index).slice(0,3).map(row => row.entry);
  }
  return {normalize,rank,match,similar};
})();
if (typeof module !== 'undefined') module.exports = VibeSearch;
