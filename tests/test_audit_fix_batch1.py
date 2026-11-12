"""Regression checks for the first audit batch's generated demo assets."""
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'site-src'))
from entries import Document


class AuditFixBatch1Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, 'scripts/build_site.py'], cwd=ROOT,
                       check=True, capture_output=True)
        cls.assets = ROOT / 'dist/assets/redesign'

    def test_view_cards_have_only_a_title_and_description(self):
        source = (ROOT / '动效速查.html').read_text()
        doc = Document(source).root
        for anchor in ('view-crossfade', 'view-slide', 'view-curtain'):
            card = next(n for n in doc.find_all('article') if n.attrs.get('id') == 'e-' + anchor)
            views = card.find_all(cls='mini-view') or card.find_all(cls='scene-slide')
            self.assertTrue(views)
            for view in views:
                children = [n for n in view.children if hasattr(n, 'tag') and 'curtain' not in n.attrs.get('class', '').split()]
                self.assertEqual([n.tag for n in children], ['strong', 'span'])
                self.assertIn('scene-description', children[1].attrs['class'])
        css = (self.assets / 'demo-motion.css').read_text()
        self.assertIn('font-size: 14px', css)
        self.assertIn('color: var(--demo-white, #FFFFFF)', css)
        self.assertIn('.stage .scene-stack', css)

    def test_interactive_borders_use_control_token_in_every_demo_family(self):
        for kind in ('ui', 'motion', 'guide', 'token', 'skill-reference'):
            css = (self.assets / f'demo-{kind}.css').read_text()
            self.assertRegex(css, r'border-color:\s*var\(--demo-border\)\s*!important')
            self.assertIn('input[type="checkbox"]', css)
            self.assertIn('input[type="radio"]', css)
            self.assertIn('.taginput-demo', css)
            self.assertIn('[tabindex]', css)
            self.assertIn('::-webkit-slider-runnable-track', css)
            self.assertIn('::-moz-range-track', css)
            self.assertRegex(css, r'--demo-border:\s*#868E9C')

    def test_pressed_and_real_active_have_independent_colors(self):
        states = (self.assets / 'states.css').read_text()
        ui = (self.assets / 'demo-ui.css').read_text()
        for name in ('pri', 'ghost', 'danger'):
            self.assertIn(f':host(.force-pressed) .btn-{name}', states)
            self.assertIn(f'.btn-{name}:active', ui)
        for token in ('--demo-primary-active', '--demo-danger-active'):
            self.assertIn(f'var({token})', states)
            self.assertIn(f'var({token})', ui)
        self.assertIn('translateY(1px)', states)
        self.assertIn('background: var(--demo-line)', states)

    def test_operation_hints_are_readable(self):
        for name in ('demo-ui.css', 'demo-motion.css', 'demo-guide.css'):
            css = (self.assets / name).read_text()
            self.assertRegex(css, r'font-size:\s*13px\s*!important')
            self.assertRegex(css, r'color:\s*#4B5563\s*!important')
            for selector in ('.stage-label', '.canvas .ctl', '.gesture-note'):
                self.assertIn(selector, css)

    def test_decorative_labels_are_removed_from_generated_markup_and_styles(self):
        for page in (ROOT / 'dist').rglob('*.html'):
            if 'bench' in page.parts:
                continue  # Historical bench specimens have separate fidelity checks.
            self.assertNotRegex(page.read_text(), r'stage-live|stage-signature|LIVE DEMO|MOTION STUDY')
        css = (self.assets / 'demo-motion.css').read_text()
        self.assertNotRegex(css, r'stage-live|stage-signature')
        source = (ROOT / '动效速查.html').read_text()
        self.assertNotIn('extra-heading"><small>', source)
        self.assertNotIn('stagger-kicker', source)

    def test_danger_palette_is_canonical(self):
        for css in self.assets.glob('demo-*.css'):
            self.assertNotIn('#dc2626', css.read_text().lower())
        script = (self.assets / 'demo-ui.js').read_text()
        self.assertNotIn('#dc2626', script.lower())
        css = (self.assets / 'demo-ui.css').read_text()
        for token in ('danger', 'danger-hover', 'danger-active'):
            self.assertIn(f'var(--demo-{token})', css)

    def test_button_background_values_are_distinct_after_token_resolution(self):
        ui = (self.assets / 'demo-ui.css').read_text()
        states = (self.assets / 'states.css').read_text()
        tokens = dict(re.findall(r'--([\w-]+):\s*(#[0-9A-Fa-f]{3,6})\b', ui))

        def background(css, selector):
            rules = re.findall(r'([^{}]+)\{([^{}]+)\}', css)
            bodies = [body for selectors, body in rules if selector in [s.strip() for s in selectors.split(',')]]
            self.assertTrue(bodies, selector)
            value = re.search(r'background:\s*([^;}]+)', bodies[-1])[1].strip()
            variable = re.fullmatch(r'var\(--([\w-]+)\)', value)
            return tokens[variable[1]].upper() if variable else value.upper()

        for name in ('pri', 'ghost', 'danger'):
            default = background(ui, '.btn-' + name)
            hover_selector = '.demo-root .btn-ghost:hover' if name == 'ghost' else '.btn-' + name + ':hover'
            hover = background(ui, hover_selector)
            active = background(ui, '.demo-root .btn-' + name + ':active')
            self.assertEqual(len({default, hover, active}), 3, name)
            self.assertEqual(active, {'pri': '#4C1D95', 'ghost': '#E4E7EC', 'danger': '#7F1D1D'}[name])
            self.assertEqual(background(states, ':host(.force-hover) .btn-' + name), hover)
            self.assertEqual(background(states, ':host(.force-pressed) .btn-' + name), active)
            self.assertEqual(background(ui, '.demo-root .btn-' + name + '[data-preview-active]'), active)

    def test_view_gradient_and_hint_contrast(self):
        import contextlib
        import io
        import runpy
        with contextlib.redirect_stdout(io.StringIO()):
            contrast = runpy.run_path(str(ROOT / 'docs/style-research/contrast.py'))['cr']
        tokens = dict(re.findall(r'--([\w-]+):\s*(#[0-9A-Fa-f]{6})', (ROOT / 'site-src/redesign/tokens.css').read_text()))
        for background in ('demo-primary', 'demo-primary-hover', 'demo-primary-active'):
            self.assertGreaterEqual(contrast('#FFFFFF', tokens[background]), 4.5)
        self.assertGreaterEqual(contrast('#4B5563', tokens['demo-stage']), 4.5)
        self.assertGreaterEqual(contrast(tokens['demo-border'], tokens['demo-stage']), 3)
