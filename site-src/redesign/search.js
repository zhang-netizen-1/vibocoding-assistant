/* Pure search functions also run in Node unit tests, without a browser. */
'use strict';
const VibeSearch = (() => {
  const normalize = text => String(text || '').normalize('NFKC').toLowerCase().replace(/\s+/g, '');
  const FUZZY_STOP_WORDS = [
    '的','了','一下','一点','怎么','怎样','什么','如何','时候','这个','那个',
    '会','能','让','被','把','就','要','想','做','个','吗','呢','啊','效果',
    '显示','出现','用','和','跟','有','没','地','得','上去','下去','起来','之类'
  ];
  const FUZZY_STOP_PATTERN = new RegExp([...FUZZY_STOP_WORDS].sort((a,b) => b.length-a.length).join('|'), 'g');
  const FUZZY_LIMIT = 8;

  function fuzzyTokens(text) {
    // Preserve English word boundaries, which strict normalization removes.
    const value = String(text || '').normalize('NFKC').toLowerCase().replace(FUZZY_STOP_PATTERN, '');
    const tokens = new Set(value.match(/[a-z0-9]+/g) || []);
    const characters = new Set();
    for (const phrase of value.match(/[\u3400-\u9fff]+/g) || []) {
      for (const character of phrase) characters.add(character);
      for (let index = 0; index < phrase.length-1; index++) tokens.add(phrase.slice(index,index+2));
    }
    return {tokens,characters};
  }

  function fuzzyField(text, query, weight) {
    const field = fuzzyTokens(text);
    const hits = [...query.tokens].filter(token => field.tokens.has(token));
    // Favor concise names without counting repeated aliases as extra evidence.
    const precision = hits.length / (field.tokens.size || 1);
    const score = weight * hits.length * (0.5 + 0.5 * precision);
    return {hits,score,characters:field.characters};
  }

  function fuzzyMatch(entry, query) {
    const names = [fuzzyField(entry.zh,query,6),fuzzyField(entry.en,query,6)];
    const aliases = (entry.aliases || []).map(alias => ({...fuzzyField(alias,query,6),alias}));
    const primary = [...names,...aliases];
    const terms = fuzzyField(entry.terms,query,3);
    const definition = fuzzyField(entry.definition,query,1);
    const hits = new Set([...primary,terms,definition].flatMap(field => field.hits));
    const coverage = hits.size / query.tokens.size;
    const bestAlias = aliases.filter(field => field.score > 0).sort((a,b) => b.score-a.score)[0];
    if (coverage >= 0.5 || primary.some(field => field.hits.length)) {
      const score = (Math.max(...primary.map(field => field.score)) + terms.score + definition.score) * coverage;
      return {score,alias:bestAlias?.alias || ''};
    }
    // Short spoken fragments such as “输错了抖一下” lose their connecting words.
    // Require multiple distinct meaningful characters in one name or alias.
    if (query.characters.size >= 2 && query.characters.size <= 4) {
      const fragments = primary.map(field => {
        const count = [...query.characters].filter(character => field.characters.has(character)).length;
        return {...field,count,coverage:count/query.characters.size};
      }).filter(field => field.count >= 2 && field.coverage >= 0.6).sort((a,b) => b.coverage-a.coverage);
      if (fragments.length) return {score:fragments[0].coverage,alias:fragments[0].alias || ''};
    }
    return {score:0,alias:''};
  }
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
    const strict = entries.map((entry,index) => {
      const priority = rank(entry, query);
      const alias = priority === 2 || priority === 4
        ? entry.aliases.find(value => priority === 2 ? normalize(value) === q : normalize(value).includes(q))
        : '';
      return {entry,index,rank:priority,alias};
    }).filter(row => row.rank < 99).sort((a,b) => a.rank-b.rank || a.index-b.index);
    if (strict.length >= 3) return strict;
    const tokens = fuzzyTokens(query);
    if (!tokens.tokens.size) return strict;
    const matched = new Set(strict.map(row => row.index));
    const fuzzy = entries.map((entry,index) => {
      if (matched.has(index)) return null;
      const {score,alias} = fuzzyMatch(entry,tokens);
      return {entry,index,rank:7,alias,score};
    }).filter(row => row && row.score > 0).sort((a,b) => b.score-a.score || a.index-b.index).slice(0,FUZZY_LIMIT);
    return [...strict,...fuzzy];
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
