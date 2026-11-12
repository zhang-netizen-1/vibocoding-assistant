/* Run the real search function against the generated homepage index. */
'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const search = require('../site-src/redesign/search.js');

const root = path.resolve(__dirname, '..');
const fixtures = JSON.parse(fs.readFileSync(path.join(__dirname, 'fixtures/search_queries.json'), 'utf8'));
const html = fs.readFileSync(path.join(root, 'dist/index.html'), 'utf8');
const indexMatch = html.match(/id="redesign-search-index">(.*?)<\/script>/s);
assert.ok(indexMatch, 'Generated homepage must contain its search index');
const index = JSON.parse(indexMatch[1]).entries;

function entryKey(entry) {
  assert.ok(entry.href.startsWith('./'), 'Homepage result links must use relative paths');
  return entry.href.replace(/^\.\//, '').replace(/^ai\/skills\//, 'ai/').replace(/\/$/, '');
}

const indexKeys = new Set(index.map(entryKey));
const taxonomy = JSON.parse(fs.readFileSync(path.join(root, 'site-src/taxonomy.json'), 'utf8'));
const count = taxonomy.columns.reduce((sum, column) => sum + column.expected, 0);
assert.equal(index.length, count);
assert.equal(indexKeys.size, count);
assert.equal(fixtures.length, 60);
assert.equal(new Set(fixtures.map(test => search.normalize(test.query))).size, 60);
assert.deepEqual([...new Set(fixtures.map(test => test.expected.split('/')[0]))].sort(),
  ['ai', 'basics', 'components', 'interactions', 'scenarios']);
for (const test of fixtures) {
  assert.equal(typeof test.query, 'string');
  assert.ok(test.query.trim());
  assert.ok(indexKeys.has(test.expected), `Unknown expected entry ${test.expected}`);
}

const results = fixtures.map(test => {
  const top3 = search.match(index, test.query).slice(0, 3).map(row => entryKey(row.entry));
  return {...test, top3, hit: top3.includes(test.expected)};
});
const missed = results.filter(result => !result.hit);

const mandatory = new Map([
  ['按钮', 'components/button'], ['Button', 'components/button'],
  ['浮起来', 'interactions/component-lift'], ['小黑框', 'components/tooltip'],
  ['弹窗', 'components/modal'], ['Toggle', 'components/switch'],
  ['水波纹', 'interactions/component-ripple'], ['加载占位', 'components/skeleton'],
  ['淡入淡出', 'interactions/view-crossfade'], ['提交中', 'interactions/submit'],
  ['鼠标放上去浮起来', 'interactions/component-lift'],
  ['弹出来的小黑框', 'components/tooltip'],
  ['Crossfade', 'interactions/view-crossfade'], ['点了会变的按钮', 'components/button']
]);
const byQuery = new Map(results.map(result => [result.query, result]));
for (const [query, expected] of mandatory) {
  assert.equal(byQuery.get(query)?.expected, expected, `Required fixture ${query}`);
}
const baseline = JSON.parse(fs.readFileSync(path.join(__dirname, 'fixtures/phase2-search-ranks.json'), 'utf8'));
assert.equal(Object.keys(baseline).length, 50);
for (const [query, previous] of Object.entries(baseline)) {
  const current = byQuery.get(query);
  assert.equal(current.expected, previous.expected);
  const rank = current.top3.indexOf(previous.expected);
  assert.ok(rank >= 0 && rank <= previous.rank, `Original query regressed: ${query}`);
}
for (const test of fixtures.slice(50)) mandatory.set(test.query, test.expected);
const mandatoryMissed = results.filter(result => mandatory.has(result.query) && !result.hit);

const englishQueries = new Set([
  ...index.flatMap(entry => entry.en.split('/').map(name => name.trim())),
  ...fixtures.map(test => test.query).filter(query => /[a-z]/i.test(query))
]);
const caseFailures = [];
for (const query of englishQueries) {
  const variants = [query.toLowerCase(), query.toUpperCase(),
    [...query].map((letter, position) => position % 2 ? letter.toUpperCase() : letter.toLowerCase()).join('')];
  const expected = search.match(index, query).map(row => entryKey(row.entry));
  for (const variant of variants) {
    const actual = search.match(index, variant).map(row => entryKey(row.entry));
    if (JSON.stringify(actual) !== JSON.stringify(expected)) {
      caseFailures.push({query, variant, expected, actual});
    }
  }
}

const hits = results.length - missed.length;
const report = {
  total: results.length,
  hits,
  hit_rate: hits / results.length,
  missed,
  mandatory_missed: mandatoryMissed,
  english_queries: englishQueries.size,
  case_failures: caseFailures,
  results
};
process.stdout.write(JSON.stringify(report, null, 2) + '\n');
process.exitCode = report.hit_rate < 0.9 || mandatoryMissed.length || caseFailures.length ? 1 : 0;
