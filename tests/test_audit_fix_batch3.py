"""State coverage, deliberate reduced-motion playback and fixed copy access."""
import importlib.util
import hashlib
import json
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'site-src/redesign'


class AuditFixBatch3Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(['python3', 'scripts/build_site.py'], cwd=ROOT,
                       check=True, capture_output=True)

    def test_component_state_coverage(self):
        spec = importlib.util.spec_from_file_location('batch3_states', SOURCE / 'states.py')
        states = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(states)
        for slug, options in states.STATES.items():
            required = {'free', 'focus', 'disabled'}
            if slug == 'button':
                required |= {'loading', 'hover', 'pressed'}
            if slug in ('input', 'textarea', 'select', 'search'):
                required.add('error')
            self.assertTrue(required <= {key for key, _, _ in options}, slug)
            page = (ROOT / f'dist/components/{slug}/index.html').read_text()
            for key in required:
                self.assertIn(f'data-state="{key}"', page)

    def test_state_semantics_and_loading_style(self):
        script = (SOURCE / 'site.js').read_text()
        for hook in ('control.disabled = true', "'aria-invalid'", "'aria-describedby'",
                     "'aria-busy'", '提交中…', 'getBoundingClientRect().width'):
            self.assertIn(hook, script)
        css = (SOURCE / 'states.css').read_text()
        self.assertIn('cursor:not-allowed', css)
        self.assertIn('var(--demo-danger)', css)
        self.assertRegex(css, r'\.demo-field-error\s*\{[^}]*font-size:13px')
        self.assertIn('@media(prefers-reduced-motion:reduce)', css)
        self.assertRegex(css, r'\.demo-loading-icon\s*\{animation:none')
        self.assertNotRegex(css, r'opacity:\s*0\.[0-5]')

    def test_reduced_motion_generated_css_gates_every_override(self):
        for kind in ('ui', 'motion', 'guide', 'token', 'skill-reference'):
            css = (ROOT / f'dist/assets/redesign/demo-{kind}.css').read_text()
            blocks = re.findall(r'@media\s*\(prefers-reduced-motion:\s*reduce\)\s*\{((?:[^{}]|\{[^{}]*\})*)\}', css)
            self.assertTrue(blocks, kind)
            for block in blocks:
                for selectors in re.findall(r'([^{}]+)\{[^{}]*\}', block):
                    self.assertTrue(all('data-demo-motion-once' in s for s in selectors.split(',')),
                                    (kind, selectors))
        runtime = (SOURCE / 'demo-runtime.js').read_text()
        for hook in ('data-demo-motion-once', 'finishMotionOnce', 'motionTimer',
                     "query.includes('prefers-reduced-motion')", 'getComputedTiming'):
            self.assertIn(hook, runtime)

    def test_explicit_gallery_play_and_reduced_notes(self):
        script = (SOURCE / 'site.js').read_text()
        self.assertIn('reduced.matches && !once', script)
        css = (SOURCE / 'site.css').read_text()
        self.assertNotIn('.play-button{display:none!important}', css)
        for page in ('components/button', 'interactions/component-lift', 'interactions'):
            html = (ROOT / f'dist/{page}/index.html').read_text()
            self.assertIn('已开启减弱动态：点播放看一次', html)
        self.assertIn('data-demo-step', (SOURCE / 'templates.py').read_text())

    def test_continuous_effects_have_manual_static_steps(self):
        for slug in ('background-aurora', 'background-wave', 'background-particles',
                     'background-fluid', 'data-skeleton'):
            page = ROOT / f'dist/interactions/{slug}/index.html'
            self.assertIn('data-demo-loop="true"', page.read_text(), slug)
        runtime = (SOURCE / 'demo-runtime.js').read_text()
        for hook in ('data-demo-motion-step', 'animation.pause()', 'animation.currentTime', 'supportsStep'):
            self.assertIn(hook, runtime)

    def test_copy_card_has_viewport_anchor_and_bounded_height(self):
        css = (SOURCE / 'site.css').read_text()
        desktop = css[css.index('/* Keep the primary action'):]
        self.assertRegex(desktop, r'\.use-card\s*\{[^}]*position:fixed')
        self.assertIn('top:calc(var(--nav-height) + 16px)', desktop)
        self.assertIn('max-height:calc(100dvh - var(--nav-height) - 32px)', desktop)
        self.assertIn('min-height:0;overflow:auto', desktop)
        self.assertIn('.prompt-card .prompt-body{flex:1 1 auto}', desktop)
        self.assertIn('overscroll-behavior:contain', desktop)
        template = (SOURCE / 'templates.py').read_text()
        self.assertIn('class="use-card prompt-card"', template)
        self.assertNotIn('entry-section prompt-box', template)

    def test_all_content_acceptance_and_aliases_are_frozen(self):
        # Frozen before option D; compare every field without invoking Git.
        expected = {
            'ai.json': '0609768ab56007a808cf62632735a720edc7f79baed95f2bf1e17c39b1bd813c',
            'basics.json': '42fbb09385dbc3692dd2f850d09efc9bb0556ce984e1403ab71453fbd5eeebc1',
            'components.json': '9ec87aa11d172b27eb452eba93da4278af6da9e2bdbdff9474a529e067bc2d62',
            'interactions.json': 'cbe1976d806da91d5e03c306fd3ae737c0bb0a4b0d90a1305f3fb99eaacc3b65',
            'scenarios.json': '09bf6a4a779280b6642eafcaefc5f76781cef94a690b7a442b93bed5b8f7b1e4',
        }
        files = {file.name: file for file in (ROOT / 'site-src/content').glob('*.json')}
        self.assertEqual(set(files), set(expected))
        for name, file in files.items():
            payload = json.dumps(json.loads(file.read_text()), ensure_ascii=False, sort_keys=True).encode()
            self.assertEqual(hashlib.sha256(payload).hexdigest(), expected[name], name)

    def test_state_and_motion_runtime_behavior(self):
        result = subprocess.run(['node', 'tests/audit_fix_batch3.cjs'], cwd=ROOT,
                                capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_state_token_contrast(self):
        tokens = dict(re.findall(r'(--demo-[\w-]+):\s*(#[\da-fA-F]{6})',
                                 (SOURCE / 'tokens.css').read_text()))

        def luminance(color):
            rgb = [int(color[index:index + 2], 16) / 255 for index in (1, 3, 5)]
            channels = [value / 12.92 if value <= .04045 else ((value + .055) / 1.055) ** 2.4
                        for value in rgb]
            return sum(value * weight for value, weight in zip(channels, (.2126, .7152, .0722)))

        for foreground, background, minimum in (
            ('--demo-danger', '--demo-stage', 4.5),
            ('--demo-danger', '--demo-white', 4.5),
            ('--demo-white', '--demo-primary', 4.5),
            ('--demo-white', '--demo-danger', 4.5),
            ('--demo-secondary', '--demo-soft', 3),
        ):
            light, dark = sorted([luminance(tokens[foreground]), luminance(tokens[background])], reverse=True)
            self.assertGreaterEqual((light + .05) / (dark + .05), minimum,
                                    (foreground, background))
