import contextlib
import io
from pathlib import Path
import re
import runpy
import unittest

ROOT = Path(__file__).resolve().parent.parent
REDESIGN = ROOT / 'site-src/redesign'


class RedesignTokensTest(unittest.TestCase):
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
            self.assertNotRegex(css.lower(), r'dark|@import|https?://|@font-face')
            if 'demo' in path.name:
                self.assertNotIn('#1d4ed8', css.lower())
        tokens = (REDESIGN / 'tokens.css').read_text()
        self.assertNotIn('#1d4ed8', tokens.split('.demo-scope')[1].lower())
        base = (REDESIGN / 'base.css').read_text()
        self.assertIn('outline: 2px solid var(--blue)', base)
        self.assertIn('outline-offset: 2px', base)
        self.assertEqual(re.findall(r'--text-[\w-]+: (\d+)px', tokens), ['12','13','14','16','18','22','28','36'])
