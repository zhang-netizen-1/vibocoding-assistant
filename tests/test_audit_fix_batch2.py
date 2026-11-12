"""Search and use-card regressions for audit batch two."""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unittest
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent


class AuditFixBatch2Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(['python3', 'scripts/build_site.py'], cwd=ROOT,
                       check=True, capture_output=True)

    def test_shared_index_is_versioned_and_resolves_at_every_depth(self):
        index_file = ROOT / 'dist/assets/search-index.json'
        self.assertTrue(index_file.is_file())
        data = json.loads(index_file.read_text())
        self.assertEqual(len(data['entries']), 192)
        version = hashlib.sha256(index_file.read_bytes()).hexdigest()[:8]
        pages = 0
        for page in (ROOT / 'dist').rglob('*.html'):
            html = page.read_text()
            if 'id="search-dialog"' not in html:
                continue
            pages += 1
            self.assertNotIn('redesign-search-index', html)
            self.assertNotIn('"entries":[', html)
            url = re.search(r'data-index-url="([^"]+)"', html)[1]
            self.assertEqual(urlsplit(url).query, 'v=' + version)
            is_error_page = page == ROOT / 'dist/404.html'
            if is_error_page:
                self.assertTrue(url.startswith('/vibocoding-assistant/assets/search-index.json'))
                target_index = ROOT / 'dist' / urlsplit(url).path.removeprefix('/vibocoding-assistant/')
            else:
                target_index = page.parent / urlsplit(url).path
            self.assertEqual(target_index.resolve(), index_file.resolve())
            prefix = re.search(r'data-site-root="([^"]+)"', html)[1]
            for item in [*data['entries'], *data['columns']]:
                href = prefix + item['href'][2:]
                if is_error_page:
                    self.assertTrue(href.startswith('/vibocoding-assistant/'))
                    target = ROOT / 'dist' / href.removeprefix('/vibocoding-assistant/')
                else:
                    self.assertFalse(href.startswith(('/', 'http:','https:')))
                    target = page.parent / href
                self.assertTrue((target / 'index.html').is_file(), (page, href))
        self.assertGreater(pages, 200)
        self.assertLess((ROOT / 'dist/components/button/index.html').stat().st_size, 100_000)

    def test_static_thumbnails_have_small_metadata_and_a_fallback(self):
        index = json.loads((ROOT / 'dist/assets/search-index.json').read_text())
        self.assertTrue(all(e['thumbnail'] in ('basics','components','interactions','scenarios','ai')
                            for e in index['entries']))
        self.assertLess(sum(len(e['thumbnail']) for e in index['entries']), 2500)
        script = (ROOT / 'site-src/redesign/site.js').read_text()
        self.assertIn('result-thumb', script)
        self.assertIn('entry.column.slice(0,1)', script)
        css = (ROOT / 'site-src/redesign/site.css').read_text()
        self.assertIn('.result-thumb', css)
        self.assertIn('width:56px', css)
        self.assertIn('height:56px', css)

    def test_stretched_link_and_responsive_use_card_rules(self):
        script = (ROOT / 'site-src/redesign/site.js').read_text()
        self.assertIn('<a class="result-name" href=', script)
        self.assertIn('event.stopPropagation()', script)
        css = (ROOT / 'site-src/redesign/site.css').read_text()
        for rule in ('.result-name::after', '.result-row:hover', 'cursor:pointer',
                     '.result-actions{position:relative;z-index:2}',
                     '@media(min-width:1024px)', 'max-height:calc(100dvh - var(--nav-height) - 32px)',
                     '.use-card .criteria[open]', 'min-height:0', 'overflow:auto',
                     '@media(max-width:1023px), (hover:none), (pointer:coarse)'):
            self.assertIn(rule, css)

    def test_browser_independent_search_lifecycle(self):
        result = subprocess.run(['node', 'tests/audit_fix_batch2.cjs'], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_unrelated_aliases_and_all_acceptance_stay_unchanged(self):
        current = json.loads((ROOT / 'site-src/content/interactions.json').read_text())
        additions = {'scroll-parallax':['滚动时背景动得慢','滚动视差'],
                     'component-spotlight':['鼠标光晕','光晕跟随鼠标']}
        records = {slug:{key:item.get(key, []) for key in ('aliases','acceptance')}
                   for slug,item in current.items()}
        for slug, aliases in additions.items():
            self.assertEqual(records[slug]['aliases'][-len(aliases):], aliases)
            records[slug]['aliases'] = records[slug]['aliases'][:-len(aliases)]
        # Frozen before this batch, independent of the user's eventual commit.
        digest = hashlib.sha256(json.dumps(records, ensure_ascii=False, sort_keys=True).encode()).hexdigest()
        self.assertEqual(digest, '1a25896bb9e9a315cc49dd8f8009aea80790e92d9b05cb4b08395a2ce97df17e')

    def test_noise_and_reasonable_typos(self):
        code = """
const assert = require('node:assert/strict');
const search = require('./site-src/redesign/search.js');
const data = require('./dist/assets/search-index.json');
for (const query of ['asdfgh','qwerty','zzzz','qzxv','霓虹灯','']) {
  assert.deepEqual(search.match(data.entries,query),[],query);
  assert.deepEqual(search.similar(data.entries,query),[],query);
}
assert.equal(search.similar(data.entries,'交叉淡华')[0].zh,'交叉淡化');
assert.equal(search.similar(data.entries,'搜索匡')[0].zh,'搜索框');
assert.equal(search.similar(data.entries,'buton')[0].zh,'按钮');
for (const [query,slug] of [['滚动时背景动得慢','scroll-parallax'],['鼠标光晕','component-spotlight']]) {
  assert.ok(search.match(data.entries,query)[0].entry.href.includes('/'+slug+'/'),query);
}
"""
        result = subprocess.run(['node','-e',code], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
