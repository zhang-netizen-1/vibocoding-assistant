"""Keep the original 46f923e page portable, byte-faithful, and outside dist."""

from collections import Counter
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent
EXPORT = ROOT / 'docs/design-system-page'
FIXTURE = ROOT / 'tests/fixtures/design_system_page_hashes.json'
LIVE_ROOT = 'https://zhang-netizen-1.github.io/vibocoding-assistant/'
CSS_URL = re.compile(r'''url\(\s*(?:"([^"]*)"|'([^']*)'|([^\s)]*))\s*\)''', re.I)
PATH_ATTRIBUTE = re.compile(
    r'''\b(href|src|data-index-url|data-site-root|data-[\w-]+-css)=(['"])(.*?)\2'''
)


class ExportParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.references = []
        self.inline_styles = []
        self.search_attributes = None

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        for key, value in attrs:
            if key in ('href', 'src', 'data-index-url', 'data-site-root') or key.endswith('-css'):
                self.references.append(value)
            if key == 'srcset':
                self.references.extend(item.strip().split()[0] for item in value.split(','))
            if key == 'style':
                self.inline_styles.append(value)
        if 'data-index-url' in attributes:
            self.search_attributes = attributes


class DesignSystemPageExportTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.fixture = json.loads(FIXTURE.read_text(encoding='utf-8'))
        cls.html = (EXPORT / 'index.html').read_text(encoding='utf-8')
        cls.page = ExportParser()
        cls.page.feed(cls.html)

    def assert_local_reference(self, ref, owner):
        url = urlsplit(ref)
        self.assertNotIn(url.hostname, ('localhost', '127.0.0.1'), (owner, ref))
        if url.scheme or url.netloc:
            return
        self.assertFalse(url.path.startswith('/'), (owner, ref))
        target = (owner.parent / unquote(url.path)).resolve() if url.path else owner.resolve()
        self.assertTrue(target.is_relative_to(EXPORT.resolve()), (owner, ref))
        if target.is_dir():
            target /= 'index.html'
        self.assertTrue(target.is_file(), (owner, ref))

    def test_index_and_all_html_and_css_resources_resolve_inside_export(self):
        index = EXPORT / 'index.html'
        self.assertTrue(index.is_file())
        for ref in self.page.references:
            with self.subTest(file='index.html', ref=ref):
                self.assert_local_reference(ref, index)
        styles = [(index, text) for text in self.page.inline_styles]
        styles.extend((path, path.read_text(encoding='utf-8')) for path in EXPORT.rglob('*.css'))
        for path, text in styles:
            for match in CSS_URL.finditer(text):
                ref = next(value for value in match.groups() if value is not None)
                with self.subTest(file=str(path.relative_to(EXPORT)), ref=ref):
                    self.assert_local_reference(ref, path)
            # Also validate quoted CSS imports, should a future original use them.
            for ref in re.findall(r'''@import\s+["']([^"']+)["']''', text):
                self.assert_local_reference(ref, path)

    def test_runtime_styles_and_online_search_paths(self):
        runtime_css = {
            ref for ref in self.page.references
            if ref.startswith('assets/redesign/') and ref.endswith('.css')
        }
        self.assertTrue({
            'assets/redesign/demo-ui.css',
            'assets/redesign/demo-spec.css',
            'assets/redesign/demo-skins/ui-button.css',
            'assets/redesign/demo-accessibility.css',
        }.issubset(runtime_css))
        self.assertIsNotNone(self.page.search_attributes)
        self.assertEqual(self.page.search_attributes['data-site-root'], LIVE_ROOT)
        self.assertEqual(self.page.search_attributes['data-index-url'],
                         LIVE_ROOT + 'assets/search-index.json?v=d51d9aef')
        self.assertIn('href="./"', self.html)
        self.assertIn('href="#demo-stage"', self.html)

    def test_no_parent_paths_or_loopback_references(self):
        for path in EXPORT.rglob('*'):
            if path.suffix not in ('.html', '.css', '.js', '.svg'):
                continue
            text = path.read_text(encoding='utf-8')
            with self.subTest(file=str(path.relative_to(EXPORT))):
                self.assertNotIn('../', text)
                self.assertNotRegex(text.lower(), r'localhost|127\.0\.0\.1')

    def test_assets_match_original_build_hashes(self):
        self.assertEqual(self.fixture['source_commit'], '46f923e')
        expected = self.fixture['assets']
        actual = {str(path.relative_to(EXPORT)) for path in EXPORT.rglob('*')
                  if path.is_file() and path.name not in ('index.html', 'README.md')}
        self.assertEqual(actual, set(expected))
        self.assertEqual(len(expected), 14)
        for name, digest in expected.items():
            with self.subTest(asset=name):
                self.assertEqual(hashlib.sha256((EXPORT / name).read_bytes()).hexdigest(), digest)

    def test_index_diff_contains_only_recorded_path_rewrites(self):
        exported = (EXPORT / 'index.html').read_bytes()
        self.assertEqual(hashlib.sha256(exported).hexdigest(), self.fixture['export_index_sha256'])
        reverse = {}
        expected_counts = Counter()
        for change in self.fixture['rewrites']:
            self.assertEqual(change['file'], 'index.html')
            self.assertTrue(change['old'].startswith('../'))
            old = change['old']
            expected_new = (old[3:] if old.startswith('../assets/') and
                            change['attribute'] != 'data-index-url' else LIVE_ROOT + old[3:])
            self.assertEqual(change['new'], expected_new)
            key = (change['attribute'], change['new'])
            self.assertNotIn(key, reverse)
            reverse[key] = old
            expected_counts[key] = change['count']
        counts = Counter()

        def restore(match):
            attribute, quote, value = match.groups()
            key = (attribute, value)
            if key not in reverse:
                return match.group(0)
            counts[key] += 1
            return attribute + '=' + quote + reverse[key] + quote

        original = PATH_ATTRIBUTE.sub(restore, self.html).encode('utf-8')
        self.assertEqual(counts, expected_counts)
        self.assertEqual(hashlib.sha256(original).hexdigest(), self.fixture['source_index_sha256'])

    def test_fresh_public_build_excludes_offline_page_and_assets(self):
        subprocess.run([sys.executable, '-B', 'scripts/build_site.py'],
                       cwd=ROOT, check=True, capture_output=True)
        dist = ROOT / 'dist'
        self.assertFalse((dist / 'design-system').exists())
        self.assertFalse((dist / 'design-system-page').exists())
        self.assertFalse((dist / 'docs').exists())
        self.assertFalse((dist / 'assets/redesign/design-system.css').exists())
        for path in dist.rglob('*'):
            if path.suffix in ('.html', '.json', '.xml'):
                self.assertNotIn('design-system-page', path.read_text(encoding='utf-8'), str(path))


if __name__ == '__main__':
    unittest.main()
