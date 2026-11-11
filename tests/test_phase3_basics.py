"""Phase-three content, reciprocal links and local interactive demonstrations."""
import json
from pathlib import Path
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'site-src'))
import entries
sys.path.insert(0, str(ROOT / 'site-src/redesign'))
import templates

SLUGS = ('color', 'typography', 'spacing', 'radius-shadow', 'dark-mode')


class BasicsTokensTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = entries.load_entries()
        cls.tax = entries.taxonomy()
        cls.by_key = {e['column'] + '/' + e['slug']: e for e in cls.entries}

    def test_five_complete_tokens_and_dynamic_counts(self):
        self.assertEqual(len(self.entries), 192)
        tokens = [e for e in self.entries if e['group'] == 'tokens']
        self.assertEqual({e['slug'] for e in tokens}, set(SLUGS))
        self.assertEqual(sum(c['expected'] for c in self.tax['columns']), len(self.entries))
        for e in tokens:
            self.assertTrue(e['id'])
            self.assertEqual(e['old_anchors'], [])
            self.assertLessEqual(len(e['definition']), 30)
            self.assertIn('试一试', e['demo_hint'])
            self.assertIs(e['reviewed'], False)
            for field in ('params', 'aliases', 'when_use', 'when_avoid', 'prompt_edit', 'prompt_new', 'acceptance'):
                self.assertTrue(e[field], (e['slug'], field))
            for version in ('prompt_edit', 'prompt_new'):
                payload = templates.copy_payload(e, version)
                for criterion in e['acceptance']:
                    self.assertIn(criterion, payload)

    def test_tokens_have_reciprocal_component_links(self):
        for slug in SLUGS:
            key = 'basics/' + slug
            e = self.by_key[key]
            self.assertTrue(any(k.startswith('components/') for k in e['related']))
            for target in e['related']:
                other = self.by_key[target]
                self.assertIn(key, other['related'])
                html = templates.detail(e, self.entries, self.tax)
                href = templates.relative(templates.entry_destination(e) + 'index.html', templates.entry_destination(other))
                self.assertIn('href="' + href + '"', html)

    def test_local_scoped_demo_assets_and_page_controls(self):
        for slug in SLUGS:
            page = ROOT / 'dist/basics' / slug / 'index.html'
            self.assertTrue(page.is_file(), page)
            html = page.read_text()
            self.assertIn('data-demo-kind="token"', html)
            self.assertIn('试一试', html)
            self.assertNotIn('#1d4ed8', self.by_key['basics/' + slug]['demo']['html'].lower())
        css = (ROOT / 'dist/assets/redesign/demo-token.css').read_text()
        js = (ROOT / 'dist/assets/redesign/demo-token.js').read_text()
        self.assertIn('prefers-reduced-motion', css)
        self.assertNotRegex(css + js, r'(?i)#1d4ed8|@import|https?://')
        self.assertIn('var(--demo-primary)', css)
        self.assertIn('prefers-color-scheme', js)
        self.assertIn('vibe-token-demo-theme', js)
        home = (ROOT / 'dist/index.html').read_text()
        self.assertIn('192 个界面效果', home)
        self.assertNotIn('三期新增', home)
        self.assertIn('基础令牌 <span class="count">5 条', home)
        for name in ('tokens.css', 'site.js'):
            self.assertNotIn('prefers-color-scheme', (ROOT / 'site-src/redesign' / name).read_text())

    def test_token_handlers_without_browser(self):
        result = subprocess.run(['node', 'tests/token_demos.cjs'], cwd=ROOT, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
