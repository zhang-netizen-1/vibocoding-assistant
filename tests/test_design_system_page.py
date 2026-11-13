"""Read-only assertions for the executor's existing dist output. Never builds."""
from html.parser import HTMLParser
from pathlib import Path
import re
import unittest
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DIST = ROOT / 'dist'
SOURCE = ROOT / 'site-src/redesign'


class ReferencePage(HTMLParser):
    def __init__(self, source):
        super().__init__()
        self.colors = {}
        self.types = {'shell': [], 'demo': []}
        self.references = []
        self.footer_links = []
        self.in_footer = False
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'footer':
            self.in_footer = True
        if self.in_footer and tag == 'a':
            self.footer_links.append(attrs.get('href'))
        for key in ('href', 'src', 'data-spec-css', 'data-demo-css', 'data-skin-css', 'data-a11y-css', 'data-kind-css', 'data-index-url', 'data-site-root'):
            if key in attrs:
                self.references.append(attrs[key])
        if 'data-color-token' in attrs:
            self.colors[attrs['data-color-token']] = attrs
        if 'data-type-group' in attrs:
            self.types[attrs['data-type-group']].append(int(attrs['data-type-size']))

    def handle_endtag(self, tag):
        if tag == 'footer':
            self.in_footer = False


def read_tokens():
    shell = (SOURCE / 'tokens.css').read_text(encoding='utf-8').split('.demo-scope')[0]
    demo = (SOURCE / 'demo-spec.css').read_text(encoding='utf-8').split(':host {', 1)[1].split('}', 1)[0]
    pattern = r'(--[\w-]+)\s*:\s*([^;{}]+)'
    return dict(re.findall(pattern, shell)), dict(re.findall(pattern, demo))


def wcag_ratio(first, second):
    def lightness(color):
        values = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
        linear = [value / 12.92 if value <= .04045 else ((value + .055) / 1.055) ** 2.4 for value in values]
        return sum(value * weight for value, weight in zip(linear, (.2126, .7152, .0722)))
    values = sorted([lightness(first), lightness(second)])
    return (values[1] + .05) / (values[0] + .05)


class DesignSystemPageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.page = DIST / 'design-system/index.html'
        if not cls.page.is_file():
            raise AssertionError('缺少 dist/design-system/index.html，请由执行者先构建站点')
        cls.html = cls.page.read_text(encoding='utf-8')
        cls.parsed = ReferencePage(cls.html)

    def test_page_and_page_only_stylesheet(self):
        self.assertIn('<h1>设计系统</h1>', self.html)
        self.assertIn('网站外框', self.html)
        self.assertIn('演示舞台与提示胶囊', self.html)
        self.assertTrue((DIST / 'assets/redesign/design-system.css').is_file())
        stylesheet = [ref for ref in self.parsed.references if 'design-system.css' in ref]
        self.assertEqual(len(stylesheet), 1)
        self.assertEqual(urlsplit(stylesheet[0]).path, '../assets/redesign/design-system.css')
        for relative in ('index.html', 'components/button/index.html'):
            self.assertNotIn('design-system.css', (DIST / relative).read_text(encoding='utf-8'))

    def test_footer_relative_links_from_root_and_deep_entries(self):
        cases = [('index.html', './design-system/'),
                 ('components/button/index.html', '../../design-system/'),
                 ('design-system/index.html', '../design-system/')]
        ai_pages = sorted((DIST / 'ai/skills').glob('*/index.html'))
        self.assertTrue(ai_pages, '应包含深层 AI 条目页')
        cases.append((str(ai_pages[0].relative_to(DIST)), '../../../design-system/'))
        for name, href in cases:
            with self.subTest(page=name):
                source = (DIST / name).read_text(encoding='utf-8')
                parsed = ReferencePage(source)
                self.assertIn(href, parsed.footer_links)
                self.assertIn('>设计系统</a>', source)
                self.assertEqual((DIST / name).parent.joinpath(href).resolve(), self.page.parent.resolve())

    def test_every_color_and_computed_contrast(self):
        shell, demo = read_tokens()
        expected = {}
        for group, tokens, stage in [('shell', shell, shell['--stage'].strip()), ('demo', demo, demo['--ds-stage'].strip())]:
            for token, raw in tokens.items():
                color = raw.strip()
                if not re.fullmatch(r'#[0-9a-fA-F]{6}', color):
                    continue
                expected[token] = color
                with self.subTest(token=token):
                    self.assertIn(token, self.parsed.colors)
                    actual = self.parsed.colors[token]
                    self.assertEqual(actual['data-color'], color)
                    self.assertEqual(actual['data-color-group'], group)
                    self.assertEqual(actual['data-stage'], stage)
                    for attribute, background in [('data-white-contrast', '#FFFFFF'), ('data-stage-contrast', stage)]:
                        value = f'{wcag_ratio(color, background):.2f}'
                        self.assertEqual(actual[attribute], value)
                    start = self.html.index(f'data-color-token="{token}"')
                    end = self.html.index('</article>', start)
                    card = self.html[start:end]
                    self.assertIn(f'background:{color}', card)
                    self.assertIn(f'白底 {wcag_ratio(color, "#FFFFFF"):.2f}:1', card)
                    self.assertIn(f'舞台 {wcag_ratio(color, stage):.2f}:1', card)
                    self.assertIn('什么时候用', card)
        self.assertEqual(set(self.parsed.colors), set(expected))

    def test_all_shell_and_demo_tokens_are_documented(self):
        shell, _ = read_tokens()
        demo_names = set(re.findall(r'--ds-[\w-]+(?=\s*:)', (SOURCE / 'demo-spec.css').read_text(encoding='utf-8')))
        for token in set(shell) | demo_names:
            with self.subTest(token=token):
                self.assertIn(f'<code>{token}</code>', self.html)
        self.assertIn('三级文字不放浅底', self.html)
        self.assertIn('--ds-ink-3 只放白底', self.html)

    def test_type_scales_are_complete(self):
        self.assertEqual(self.parsed.types['shell'], [12, 13, 14, 16, 18, 22, 28, 36])
        self.assertEqual(self.parsed.types['demo'], [12, 13, 14, 16, 20, 28])
        for duration in ('100ms', '160ms', '240ms', '360ms', '560ms'):
            self.assertIn(duration, self.html)
        self.assertEqual(self.html.count('class="ds-motion-play"'), 9)
        for state in ('force-hover', 'force-pressed', 'force-focus', 'force-disabled'):
            self.assertIn(state, self.html)

    def test_real_demo_and_bundles(self):
        self.assertIn('id="design-system-live-demo"', self.html)
        self.assertRegex(self.html, r'class="demo-scope"[^>]*data-interactive')
        self.assertIn('data-demo-template', self.html)
        self.assertIn('demo-runtime.js', self.html)
        self.assertIn('demo-ui.js', self.html)
        self.assertIn('data-demo-slug="button"', self.html)

    def test_all_local_references_are_relative_and_resolve(self):
        for ref in self.parsed.references:
            with self.subTest(reference=ref):
                parts = urlsplit(ref)
                if parts.scheme or parts.netloc:
                    continue
                self.assertFalse(parts.path.startswith('/'), ref)
                target = (self.page.parent / unquote(parts.path)).resolve() if parts.path else self.page
                self.assertTrue(target.is_relative_to(DIST.resolve()), ref)
                if target.is_dir():
                    target /= 'index.html'
                self.assertTrue(target.is_file(), ref)
                if parts.fragment:
                    self.assertRegex(target.read_text(encoding='utf-8'), rf'id=[\"\']{re.escape(unquote(parts.fragment))}[\"\']')


if __name__ == '__main__':
    unittest.main()
