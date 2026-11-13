"""Regression checks for the first audit batch's generated demo assets."""
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'site-src'))
from entries import Document
from demo_css import declaration, demo_styles, resolve_color


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
        import contextlib
        import io
        import runpy
        with contextlib.redirect_stdout(io.StringIO()):
            contrast = runpy.run_path(str(ROOT / 'docs/style-research/contrast.py'))['cr']
        a11y = (self.assets / 'demo-accessibility.css').read_text()
        control_selector = '.demo-root :is(input, textarea, select, button, [role="button"], [role="checkbox"], [role="radio"], [role="switch"], [tabindex])'
        self.assertEqual(declaration(a11y, control_selector, 'border-color'), 'var(--demo-border)')
        self.assertRegex(a11y, re.escape(control_selector) + r'[^{}]*\{[^}]*border-color:\s*var\(--demo-border\)\s*!important')
        for selector in ('.demo-root input[type="checkbox"]', '.demo-root input[type="radio"]',
                         '.demo-root input[type="range"]::-webkit-slider-runnable-track',
                         '.demo-root input[type="range"]::-moz-range-track'):
            self.assertEqual(declaration(a11y, selector, 'border'), '1px solid var(--demo-border)')
        for selector in ('.taginput-demo', '[tabindex]', 'input[type="checkbox"]',
                         'input[type="radio"]', '::-webkit-slider-runnable-track', '::-moz-range-track'):
            self.assertIn(selector, a11y)
        for kind in ('ui', 'motion', 'guide', 'token', 'skill-reference'):
            css = demo_styles(self.assets, kind)
            border = resolve_color(css, 'var(--demo-border)')
            self.assertEqual(border, '#868E9C')
            for background in ('--ds-stage', '--ds-surface', '--ds-fill'):
                self.assertGreaterEqual(contrast(border, resolve_color(css, f'var({background})')), 3, (kind, background))
        seen = set()
        for page in (ROOT / 'dist').rglob('*.html'):
            for attributes in re.findall(r'<template (data-demo-template[^>]*)>', page.read_text()):
                self.assertIn('data-a11y-css=', attributes, str(page))
                self.assertIn('demo-accessibility.css', attributes, str(page))
                self.assertIn('demo-spec.css', attributes, str(page))
                seen.update(re.findall(r'demo-(ui|motion|guide|token|skill-reference)\.css', attributes))
        self.assertEqual(seen, {'ui', 'motion', 'guide', 'token', 'skill-reference'})

    def test_pressed_and_real_active_have_independent_colors(self):
        states = (self.assets / 'states.css').read_text()
        a11y = (self.assets / 'demo-accessibility.css').read_text()
        skin = (self.assets / 'demo-skins/ui-button.css').read_text()
        for name in ('pri', 'ghost', 'danger'):
            self.assertIn(f':host(.force-pressed) .btn-{name}', states)
            self.assertIn(f'.btn-{name}:active', a11y)
            self.assertIn(f'.ds-button-demo .btn-{name}:active:not(:disabled)', skin)
        for token in ('--demo-primary-active', '--demo-danger-active'):
            self.assertIn(f'var({token})', states)
            self.assertIn(f'var({token})', a11y)
        self.assertIn('transform:scale(.98)', states)
        self.assertIn('background: var(--demo-line)', states)

    def test_operation_hints_are_readable(self):
        import contextlib
        import io
        import runpy
        with contextlib.redirect_stdout(io.StringIO()):
            contrast = runpy.run_path(str(ROOT / 'docs/style-research/contrast.py'))['cr']
        for kind in ('ui', 'motion', 'guide'):
            css = demo_styles(self.assets, kind)
            selector = '.demo-root.ds-stage .ds-hint'
            self.assertGreaterEqual(float(declaration(css, selector, 'font-size').removesuffix('px')), 12)
            foreground = resolve_color(css, declaration(css, selector, 'color'))
            background = resolve_color(css, declaration(css, selector, 'background'))
            self.assertGreaterEqual(contrast(foreground, background), 4.5, kind)
            for legacy_selector in ('.stage-label', '.canvas .ctl', '.gesture-note'):
                self.assertIn(legacy_selector, (self.assets / 'demo-accessibility.css').read_text())

    def test_decorative_labels_are_removed_from_generated_markup_and_styles(self):
        for page in (ROOT / 'dist').rglob('*.html'):
            self.assertNotRegex(page.read_text(), r'stage-live|stage-signature|LIVE DEMO|MOTION STUDY')
        css = (self.assets / 'demo-motion.css').read_text()
        self.assertNotRegex(css, r'stage-live|stage-signature')
        source = (ROOT / '动效速查.html').read_text()
        self.assertNotIn('extra-heading"><small>', source)
        self.assertNotIn('stagger-kicker', source)

    def test_danger_palette_is_canonical(self):
        for path in self.assets.rglob('*.css'):
            self.assertNotIn('#dc2626', path.read_text().lower(), str(path))
        script = (self.assets / 'demo-ui.js').read_text()
        self.assertNotIn('#dc2626', script.lower())
        css = demo_styles(self.assets, 'ui', 'ui-button')
        skin = (self.assets / 'demo-skins/ui-button.css').read_text()
        for token, expected in (('danger', '#B91C1C'), ('danger-hover', '#991B1B'), ('danger-active', '#7F1D1D')):
            self.assertEqual(resolve_color(css, f'var(--demo-{token})'), expected)
        for selector, token in (('.ds-button-demo .btn-danger', 'danger'),
                                ('.ds-button-demo .btn-danger:hover:not(:disabled)', 'danger-hover'),
                                ('.ds-button-demo .btn-danger:active:not(:disabled)', 'danger-active')):
            self.assertEqual(resolve_color(css, declaration(skin, selector, 'background')),
                             resolve_color(css, f'var(--demo-{token})'))

    def test_button_background_values_are_distinct_after_token_resolution(self):
        css = demo_styles(self.assets, 'ui', 'ui-button')
        states = (self.assets / 'states.css').read_text()
        skin = (self.assets / 'demo-skins/ui-button.css').read_text()
        a11y = (self.assets / 'demo-accessibility.css').read_text()

        def background(sheet, selector):
            return resolve_color(css, declaration(sheet, selector, 'background'))

        for name in ('pri', 'ghost', 'danger'):
            default = background(skin, '.ds-button-demo .btn-' + name)
            hover = background(skin, '.ds-button-demo .btn-' + name + ':hover:not(:disabled)')
            active = background(skin, '.ds-button-demo .btn-' + name + ':active:not(:disabled)')
            self.assertEqual(len({default, hover, active}), 3, name)
            self.assertEqual(active, {'pri': '#4C1D95', 'ghost': '#E4E7EC', 'danger': '#7F1D1D'}[name])
            self.assertEqual(background(skin, ':host(.force-hover) .ds-button-demo .btn-' + name), hover)
            self.assertEqual(background(skin, ':host(.force-pressed) .ds-button-demo .btn-' + name), active)
            self.assertEqual(background(states, ':host(.force-hover) .btn-' + name), hover)
            self.assertEqual(background(states, ':host(.force-pressed) .btn-' + name), active)
            self.assertEqual(background(a11y, '.demo-root .btn-' + name + ':active'), active)
            self.assertEqual(background(a11y, '.demo-root .btn-' + name + '[data-preview-active]'), active)

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
