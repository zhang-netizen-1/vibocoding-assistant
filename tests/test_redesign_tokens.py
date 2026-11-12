import contextlib
import io
from pathlib import Path
import re
import runpy
import unittest

ROOT = Path(__file__).resolve().parent.parent
REDESIGN = ROOT / 'site-src/redesign'


class RedesignTokensTest(unittest.TestCase):
    def test_batch5_typography_and_related_link_values(self):
        base = (REDESIGN / 'base.css').read_text()
        site = (REDESIGN / 'site.css').read_text()

        def declarations(css, selector):
            blocks = re.findall(r'([^{}]+)\{([^{}]*)\}', css)
            rules = [body for selectors, body in blocks if selector in [s.strip() for s in selectors.split(',')]]
            self.assertTrue(rules, selector)
            return dict(re.findall(r'([\w-]+)\s*:\s*([^;]+)', rules[0]))

        for selector in ('.entry-section h2', '.use-card h2', '.criteria summary', '.new-section>summary', '.group-section h2'):
            rule = declarations(site, selector)
            self.assertEqual(rule['font-size'], 'var(--text-section)', selector)
            self.assertEqual(rule['line-height'], '1.3', selector)
            self.assertEqual(rule['font-weight'], '600', selector)
        for css, selector in ((base, '.chip'), (site, '.count'), (site, '.stat'),
                              (site, '.title-count'), (site, '.result-count'), (site, '.bench-badge')):
            rule = declarations(css, selector)
            self.assertEqual(rule['font-size'], 'var(--text-label)', selector)
            self.assertEqual(rule['font-weight'], '500', selector)
            self.assertEqual(rule['line-height'], '1.5', selector)
        for selector in ('.gallery-caption strong', '.simple-card strong', '.layer h3'):
            rule = declarations(site, selector)
            self.assertEqual(rule['font-size'], '16px', selector)
            self.assertEqual(rule['font-weight'], '600', selector)
            self.assertEqual(rule['line-height'], '1.5', selector)
            self.assertRegex(site, re.escape(selector) + r'[^{}]*\{font-size:14px')
        self.assertNotRegex(site, r'\.motion-grid \.gallery-caption strong\{font-size:14px')
        rule = declarations(base, '.link-block')
        for prop, expected in {'background':'var(--white)', 'border':'1px solid var(--control)',
                               'color':'var(--ink)', 'min-height':'44px', 'overflow-wrap':'anywhere'}.items():
            self.assertEqual(rule[prop], expected)
        self.assertEqual(declarations(base, '.link-block:hover')['border-color'], 'var(--ink)')
        self.assertIn('outline: 2px solid var(--blue)', base)

    def test_prd_contrast_pairs(self):
        with contextlib.redirect_stdout(io.StringIO()):
            contrast = runpy.run_path(str(ROOT / 'docs/style-research/contrast.py'))['cr']
        css = (REDESIGN / 'tokens.css').read_text()
        tokens = dict(re.findall(r'--([\w-]+):\s*(#[0-9A-Fa-f]{6})', css))
        pairs = [('line', 'white', 1.24), ('control', 'white', 3.3),
                 ('ink', 'white', 17.74), ('ink', 'soft', 16.12),
                 ('secondary', 'white', 7.56), ('secondary', 'stage', 7.05),
                 ('muted', 'white', 4.83), ('muted', 'stage', 4.51),
                 ('blue', 'white', 6.7), ('blue', 'stage', 6.25),
                 ('blue-hover', 'white', 8.72), ('white', 'ink', 17.74),
                 ('white', 'black-hover', 10.31), ('demo-white', 'demo-primary', 7.1),
                 ('demo-white', 'demo-danger', 6.47)]
        for fg, bg, minimum in pairs:
            self.assertGreaterEqual(contrast(tokens[fg], tokens[bg]), minimum, (fg, bg))
        self.assertEqual(tokens['demo-primary'], '#6D28D9')
        self.assertEqual(tokens['demo-danger'], '#B91C1C')

    def test_light_only_and_separate_demo_colors(self):
        for path in REDESIGN.glob('*.css'):
            css = path.read_text()
            self.assertNotRegex(css.lower(), r'@import|https?://|@font-face')
            if path.name == 'token-demo.css':
                self.assertIn('.theme-sample[data-theme=dark]', css)
                self.assertNotRegex(css, r':root|prefers-color-scheme|body\[')
            else:
                self.assertNotIn('dark', css.lower())
            if 'demo' in path.name:
                self.assertNotIn('#1d4ed8', css.lower())
        tokens = (REDESIGN / 'tokens.css').read_text()
        self.assertNotIn('#1d4ed8', tokens.split('.demo-scope')[1].lower())
        base = (REDESIGN / 'base.css').read_text()
        self.assertIn('outline: 2px solid var(--blue)', base)
        self.assertIn('outline-offset: 2px', base)
        self.assertEqual(re.findall(r'--text-[\w-]+: (\d+)px', tokens), ['12','13','14','16','18','22','28','36'])
