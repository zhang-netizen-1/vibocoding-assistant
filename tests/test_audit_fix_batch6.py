"""Gallery sizing, hover-card clearance and solid-background text contrast."""
import contextlib
import io
from pathlib import Path
import re
import runpy
import subprocess
import unittest

ROOT = Path(__file__).resolve().parent.parent


def declaration(css, selector, property_name):
    css = re.sub(r'/\*.*?\*/', '', css, flags=re.S)
    values = []
    for selectors, body in re.findall(r'([^{}]+)\{([^{}]*)\}', css):
        if selector in [item.strip() for item in selectors.split(',')]:
            values.extend(re.findall(r'(?<![\w-])' + property_name + r':\s*([^;}]+)', body))
    if not values:
        raise AssertionError(f'Missing {property_name} for {selector}')
    return values[-1].strip().removesuffix('!important').strip()


class AuditFixBatch6Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(['python3', 'scripts/build_site.py'], cwd=ROOT, check=True, capture_output=True)
        cls.assets = ROOT / 'dist/assets/redesign'
        with contextlib.redirect_stdout(io.StringIO()):
            cls.contrast = staticmethod(runpy.run_path(str(ROOT / 'docs/style-research/contrast.py'))['cr'])

    def test_gallery_runtime_width_scale_height_limit_and_repeat_stability(self):
        # Exercise the real sizing function, including auto-height reflow, fixed
        # height limits, resize and repeated calls from ResizeObserver.
        code = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const runtime = fs.readFileSync('site-src/redesign/demo-runtime.js','utf8');
const start = runtime.indexOf('    function fitGallery()');
const end = runtime.indexOf('    function preventExampleNavigation',start);
for (const width of [140,336,436]) for (const natural of [160,224,400]) {
  for (const limit of [Infinity,180]) {
    const body = {style:{},scrollHeight:natural};
    const stage = {clientWidth:width,get clientHeight() {
      return Math.min(limit,Math.max(240,natural*Number(body.style.zoom || 1)+72));
    }};
    const scope = {clientWidth:width,style:{},closest:() => stage};
    const context = vm.createContext({scope,body,getComputedStyle:() => ({paddingTop:'12',paddingBottom:'60'})});
    vm.runInContext(runtime.slice(start,end),context);
    for (let call=0;call<4;call++) {
      vm.runInContext('fitGallery()',context);
      assert.equal(body.style.width,'312px');
      assert.equal(body.style.flexShrink,'0');
      const expected = Math.min(1.35,width/312,(stage.clientHeight-72)/natural);
      assert.ok(Math.abs(Number(body.style.zoom)-expected)<.001,JSON.stringify({width,natural,limit,body}));
      assert.ok(312*Number(body.style.zoom)<=width+.01);
      assert.ok(natural*Number(body.style.zoom)<=stage.clientHeight-72+.01);
    }
    if (limit===Infinity && width===336) assert.ok(Number(body.style.zoom)>1.07);
    scope.clientWidth=180;
    vm.runInContext('fitGallery()',context);
    assert.ok(312*Number(body.style.zoom)<=180+.01);
  }
}
"""
        result = subprocess.run(['node', '-e', code], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_hover_card_stage_reserves_clearance_in_both_entry_points(self):
        css = (self.assets / 'demo-motion.css').read_text()
        selector = ':host .demo-root .stage[data-effect="component-hover-preview"]'
        self.assertGreaterEqual(float(declaration(css, selector, 'min-height').removesuffix('px')), 250)
        self.assertEqual(declaration(css, selector, 'justify-content'), 'flex-start')
        self.assertGreater(css.index(selector), css.index(':host(:not([data-interactive])) .demo-root :is(.canvas,.stage,.guide-card-stage)'))
        for destination in ('interactions/component-hover-preview', 'components/card', 'interactions'):
            page = (ROOT / f'dist/{destination}/index.html').read_text()
            self.assertIn('data-effect="component-hover-preview"', page, destination)
            self.assertIn('demo-motion.css', page, destination)

    def test_miniature_text_colors_meet_contrast_on_all_solid_backgrounds(self):
        css = (self.assets / 'demo-guide.css').read_text()
        selectors = ('.mini-layout-top', '.mini-layout-heading small', '.mini-layout-main p',
                     '.mini-layout-tail', '.mini-layout-bottom', '.mini-interaction p', '.mini-task span',
                     '.mini-page-top', '.mini-page-foot', '.mini-page-hero small', '.mini-page-metrics small',
                     '.mini-page-search', '.mini-page-field', '.mini-page-list span', '.mini-page-settings span',
                     '.mini-page-steps small', '.mini-data-title', '.mini-data p')
        for selector in selectors:
            color = declaration(css, selector, 'color')
            for background in ('#FFFFFF', '#F5EFE9', '#F5F2FA', '#F0F6F3'):
                self.assertGreaterEqual(self.contrast(color, background), 4.5, (selector, color, background))

    def test_skill_and_component_small_text_contrast(self):
        cases = (
            ('skill-reference', '.demo-root .skill-card dt', '#232320'),
            ('ui', '.demo-root .fflabel', '#F6F7F9'),
            ('ui', '.demo-root #taCountNum', '#F6F7F9'),
            ('ui', '.demo-root .chip button', '#E5E7EB'),
        )
        for kind, selector, background in cases:
            css = (self.assets / f'demo-{kind}.css').read_text()
            color = declaration(css, selector, 'color')
            tokens = dict(re.findall(r'(--[\w-]+):\s*(#[\da-fA-F]{6})\b', css))
            if color.startswith('var('):
                color = tokens[color[4:-1]]
            self.assertGreaterEqual(self.contrast(color, background), 4.5, selector)
