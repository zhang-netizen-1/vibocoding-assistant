"""Option D: shared prompt card, complete payload and responsive copy behavior."""
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest

from demo_css import declaration

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'site-src/redesign'


class PromptCardDTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(ROOT / 'site-src'))
        spec = importlib.util.spec_from_file_location('prompt_d_entries', ROOT / 'site-src/entries.py')
        cls.adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.adapter)
        spec = importlib.util.spec_from_file_location('prompt_d_templates', SOURCE / 'templates.py')
        cls.templates = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.templates)
        cls.entries = cls.adapter.load_entries()
        cls.tax = cls.adapter.taxonomy()

    def check_card(self, html, entry):
        doc = self.adapter.Document(html).root
        cards = doc.find_all('aside', 'prompt-card')
        self.assertEqual(len(cards), 1)
        card = cards[0]
        self.assertEqual(doc.find_all(cls='prompt-box'), [])
        body = card.one('div', 'prompt-body')
        self.assertEqual(body.attrs['tabindex'], '0')
        self.assertEqual(body.attrs['role'], 'region')
        prompt = next(n for n in body.find_all('pre') if n.attrs.get('id') == 'entry-prompt')
        self.assertEqual(prompt.text(), entry['prompt'])
        self.assertEqual(sum(n.attrs.get('id') == 'entry-prompt' for n in doc.find_all()), 1)
        head = card.one('div', 'prompt-head')
        self.assertEqual(head.one('h2').text(), '提示词')
        button = head.one('button')
        self.assertEqual(button.text(), '复制')
        self.assertEqual(button.attrs['data-copy-source'], 'copy-prompt')
        self.assertIn('btn-primary', button.attrs['class'])
        notices = card.find_all(cls='prompt-meta')
        self.assertEqual(len(notices), int(bool(entry['acceptance'])))
        if notices:
            self.assertEqual(notices[0].text(), f'复制时自动附带 {len(entry["acceptance"])} 条验收要求')
        criteria = card.find_all('details', 'criteria')
        self.assertEqual(len(criteria), int(bool(entry['acceptance'])))
        if criteria:
            self.assertNotIn('open', criteria[0].attrs)
            self.assertEqual([n.one('p').text() for n in criteria[0].find_all('li')], entry['acceptance'])
        actions = card.one('div', 'use-actions').find_all('button')
        self.assertEqual([n.text() for n in actions], ['复制英文名', '复制本页链接'])
        payload = next(n for n in doc.find_all('pre') if n.attrs.get('id') == 'copy-prompt')
        self.assertIn('hidden', payload.attrs)
        self.assertEqual(payload.text(), self.templates.copy_payload(entry))
        for criterion in entry['acceptance']:
            self.assertIn(criterion, payload.text())
        if entry.get('prompt_secondary') and not entry.get('prompt_edit'):
            self.assertIn(entry['prompt_secondary'], body.text())
        # Source order and mobile visual order both put the same card after demos.
        main = doc.one('article', 'entry-main')
        demos = main.find_all('div', 'entry-demo')
        self.assertTrue(demos)
        self.assertGreaterEqual(card.start, max(node.end for node in demos))
        for cls in ('motion-section', 'usage-section', 'new-section', 'related-section'):
            for node in main.find_all(cls=cls):
                self.assertGreaterEqual(node.start, card.end, cls)
        bar = doc.one('div', 'bottom-bar')
        self.assertIn('hidden', bar.attrs)
        self.assertIn('inert', bar.attrs)
        live = next(n for n in doc.find_all() if n.attrs.get('id') == 'live')
        self.assertEqual(live.attrs['aria-live'], 'polite')

    def test_all_192_built_entries_have_one_complete_prompt_card(self):
        self.assertEqual(len(self.entries), 192)
        for entry in self.entries:
            with self.subTest(slug=entry['slug']):
                page = ROOT / 'dist' / self.templates.entry_destination(entry) / 'index.html'
                self.check_card(page.read_text(), entry)

    def test_no_acceptance_omits_notice_and_keeps_original_payload(self):
        raw = self.adapter.load_entries(content={}, strict=False)
        entry = next(e for e in raw if not e['acceptance'] and not e.get('prompt_secondary'))
        self.check_card(self.templates.detail(entry, raw, self.tax), entry)
        self.assertEqual(self.templates.copy_payload(entry), entry['prompt'])

    def test_fixed_card_scroll_regions_mobile_order_and_touch_targets(self):
        css = (SOURCE / 'site.css').read_text()
        desktop = css[css.index('/* Keep the primary action'):css.index('/* Touch targets')]
        self.assertIn('@media(min-width:1024px)', desktop)
        self.assertRegex(desktop, r'\.use-card\{position:fixed;')
        self.assertIn('max-height:calc(100dvh - var(--nav-height) - 32px)', desktop)
        self.assertIn('overflow:auto;overscroll-behavior:contain', desktop)
        self.assertEqual(declaration(css, '.prompt-body', 'overflow'), 'auto')
        self.assertEqual(declaration(css, '.prompt-body', 'overscroll-behavior'), 'contain')
        self.assertEqual(declaration(css, '.prompt-text', 'white-space'), 'pre-wrap')
        self.assertNotRegex(css, r'(?:line-clamp|text-overflow:ellipsis)[^}]*prompt')
        for selector, prop, expected in (
            ('.prompt-card', 'border-radius', '16px'),
            ('.prompt-card', 'padding', '16px'),
            ('.prompt-body', 'border-radius', '8px'),
            ('.prompt-body', 'margin-top', '12px'),
            ('.prompt-head', 'gap', '12px'),
            ('.prompt-head .copy-btn', 'min-width', '104px'),
            ('.prompt-head .copy-btn', 'min-height', '44px'),
            ('.prompt-head .copy-btn', 'border-radius', '8px'),
            ('.prompt-card button', 'min-height', '44px'),
            ('.prompt-card .use-actions', 'gap', '8px'),
        ):
            self.assertEqual(declaration(css, selector, prop), expected, (selector, prop))
        self.assertIn('.entry-demo{order:1}', css)
        self.assertIn('.use-card{order:2}.motion-section{order:3}.usage-section{order:4}', css)
        self.assertIn('.prompt-card .prompt-body{max-height:none;overflow:visible}', css)

    def test_copied_card_palette_contrast_focus_and_reduced_motion(self):
        css = (SOURCE / 'site.css').read_text()
        self.assertEqual(declaration(css, '.prompt-card.is-copied', 'background'), '#6D28D9')
        self.assertEqual(declaration(css, '.prompt-card.is-copied', 'color'), '#FFFFFF')
        self.assertIn('.prompt-card.is-copied :is(button,button:hover){background:#FFFFFF;border-color:#FFFFFF;color:#6D28D9}', css)
        self.assertIn('.prompt-card.is-copied :focus-visible{outline:2px solid #FFFFFF;outline-offset:2px}', css)
        self.assertIn('@media(prefers-reduced-motion:reduce){.prompt-card,.prompt-card button,.bottom-bar{transition:none}}', css)
        base = (SOURCE / 'base.css').read_text()
        self.assertIn('.btn-primary { background: var(--ink); color: var(--white)', base)
        self.assertIn('outline: 2px solid var(--blue)', base)
        def luminance(color):
            channels = [int(color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
            return sum((v / 12.92 if v <= .04045 else ((v + .055) / 1.055) ** 2.4) * w
                       for v, w in zip(channels, (.2126, .7152, .0722)))
        self.assertGreaterEqual((luminance('#FFFFFF') + .05) / (luminance('#6D28D9') + .05), 7.1)

    def test_actual_copy_and_visibility_javascript_without_a_browser(self):
        result = subprocess.run(['node', 'tests/prompt_card_d_runtime.cjs'], cwd=ROOT,
                                capture_output=True, text=True, timeout=30)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == '__main__':
    unittest.main()
