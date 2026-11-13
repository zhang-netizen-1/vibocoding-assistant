"""Shared templates and deep-path recovery regressions for batch five."""
from pathlib import Path
import json
import re
import subprocess
import sys
import unittest
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'site-src'))
from entries import Document


class AuditFixBatch5Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(['python3', 'scripts/build_site.py'], cwd=ROOT,
                       check=True, capture_output=True)

    def test_chinese_404_reuses_shell_and_recovers_at_unknown_depths(self):
        path = ROOT / 'dist/404.html'
        self.assertTrue(path.is_file())
        html = path.read_text()
        doc = Document(html).root
        self.assertIn('这个页面不存在，可能是网址输错了或条目改名了', doc.text())
        self.assertEqual(len(doc.find_all('header', 'header')), 1)
        self.assertEqual(len(doc.find_all('footer')), 1)
        self.assertEqual(len(doc.find_all('div', 'footer')), 1)
        self.assertTrue(any(a.text() == '回首页' and a.attrs['href'] == '/vibocoding-assistant/'
                            for a in doc.find_all('a')))
        self.assertTrue(any('data-search' in b.attrs for b in doc.find_all('button')))
        search = next(n for n in doc.find_all('dialog') if n.attrs.get('id') == 'search-dialog')
        index = json.loads((ROOT / 'dist/assets/search-index.json').read_text())
        for missing in ('missing', 'a/b/c/missing/', 'components/missing/index.html'):
            current = 'https://example.test/vibocoding-assistant/' + missing
            references = [n.attrs[key] for n in doc.find_all()
                          for key in ('href', 'src') if key in n.attrs]
            references += [search.attrs['data-index-url']]
            references += [search.attrs['data-site-root'] + item['href'][2:]
                           for item in [*index['entries'], *index['columns']]]
            for ref in references:
                self.assertNotIn('../', ref)
                url = urlsplit(urljoin(current, ref))
                self.assertEqual(url.netloc, 'example.test')
                self.assertTrue(url.path.startswith('/vibocoding-assistant/'), ref)
                if ref.startswith('#'):
                    self.assertTrue(any(n.attrs.get('id') == url.fragment for n in doc.find_all()))
                    continue
                target = ROOT / 'dist' / url.path.removeprefix('/vibocoding-assistant/')
                if target.is_dir():
                    target /= 'index.html'
                self.assertTrue(target.is_file(), (missing, ref))

    def test_home_keeps_prompt_word_and_punctuation_together(self):
        html = (ROOT / 'dist/index.html').read_text()
        self.assertIn('<span class="nowrap">提示词。</span>', html)
        self.assertIn('.nowrap { white-space: nowrap; }', (ROOT / 'site-src/redesign/base.css').read_text())

    def test_footer_rule_is_inside_shared_padding_on_every_shell_page(self):
        for path in (ROOT / 'dist').rglob('*.html'):
            html = path.read_text()
            if 'id="search-dialog"' in html:
                self.assertIn('<footer class="wrap"><div class="footer">', html, str(path))
                self.assertNotIn('class="wrap footer"', html, str(path))

    def test_prompt_writing_uses_primary_copy_and_token_spacing(self):
        doc = Document((ROOT / 'dist/ai/prompt-writing/index.html').read_text()).root
        button = next(b for b in doc.find_all('button') if b.attrs.get('data-copy-source') == 'button-edit-example')
        self.assertIn('btn-primary', button.attrs['class'].split())
        css = (ROOT / 'site-src/redesign/site.css').read_text()
        self.assertRegex(css, r'\.entry-section p\s*\+\s*h3\s*\{\s*margin-top:\s*var\(--space-6\)')

    def test_related_and_reverse_component_links_share_arrow_blocks(self):
        entries = json.loads((ROOT / 'build/entries.json').read_text())
        for entry in entries:
            middle = 'skills/' if entry['column'] == 'ai' else ''
            path = ROOT / 'dist' / entry['column'] / middle / entry['slug'] / 'index.html'
            doc = Document(path.read_text()).root
            related = doc.one(cls='related-section')
            for section in [related, *[s for s in doc.find_all('section', 'motion-section')
                                      if '用在哪些组件上' in s.text()]]:
                links = section.find_all('a')
                self.assertTrue(links, str(path))
                for link in links:
                    self.assertIn('link-block', link.attrs['class'].split(), str(path))
                    self.assertNotIn('chip', link.attrs['class'].split(), str(path))
                    self.assertTrue(link.text().endswith('→'), str(path))
                    self.assertEqual(link.find_all('span')[-1].attrs.get('aria-hidden'), 'true')

    def test_generated_demo_danger_color_has_no_old_red(self):
        assets = ROOT / 'dist/assets/redesign'
        for path in assets.glob('*'):
            if path.suffix in ('.css', '.js'):
                self.assertNotIn('#dc2626', path.read_text().lower(), path.name)
        for path in (ROOT / 'dist').rglob('*.html'):
            for demo in re.findall(r'<template data-demo-template\b.*?</template>', path.read_text(), re.S):
                self.assertNotIn('#dc2626', demo.lower(), str(path))
