"""Gallery sizing, hover-card clearance and solid-background text contrast."""
import contextlib
import io
from pathlib import Path
import re
import runpy
import subprocess
import unittest
from demo_css import declaration, demo_styles, resolve_color

ROOT = Path(__file__).resolve().parent.parent


class AuditFixBatch6Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(['python3', 'scripts/build_site.py'], cwd=ROOT, check=True, capture_output=True)
        cls.assets = ROOT / 'dist/assets/redesign'
        with contextlib.redirect_stdout(io.StringIO()):
            cls.contrast = staticmethod(runpy.run_path(str(ROOT / 'docs/style-research/contrast.py'))['cr'])

    def test_gallery_runtime_width_scale_height_limit_and_repeat_stability(self):
        # Unified stages reflow at their available width and grow with content.
        # Run the actual function repeatedly across narrow/wide/zero-width hosts.
        code = r"""
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const runtime = fs.readFileSync('site-src/redesign/demo-runtime.js','utf8');
const start = runtime.indexOf('    function fitGallery()');
const end = runtime.indexOf('    function preventExampleNavigation',start);
assert.ok(start >= 0 && end > start);
for (const width of [140,336,436]) for (const natural of [160,224,400,760]) {
  const body = {style:{width:'312px',zoom:'.4'},scrollHeight:natural};
  const stage = {clientWidth:width};
  const scope = {clientWidth:width,style:{},closest:selector => {
    assert.equal(selector,'.mini-stage'); return stage;
  }};
  const context = vm.createContext({scope,body});
  vm.runInContext(runtime.slice(start,end),context);
  for (const resizedWidth of [width,180,436,140,width]) {
    scope.clientWidth = resizedWidth;
    for (let call=0;call<4;call++) {
      vm.runInContext('fitGallery()',context);
      assert.equal(body.style.width,`${resizedWidth}px`);
      assert.equal(body.style.flexShrink,'0');
      assert.equal(body.style.zoom,'1');
      assert.equal(body.scrollHeight,natural);
      assert.equal(scope.style.display,'flex');
      assert.equal(scope.style.alignItems,'center');
      assert.equal(scope.style.justifyContent,'center');
    }
  }
  scope.clientWidth = 0;
  vm.runInContext('fitGallery()',context);
  assert.equal(body.style.width,`${width}px`,'Use stage width before a host gets layout');
  stage.clientWidth = 0;
  vm.runInContext('fitGallery()',context);
  assert.equal(body.style.width,'1px','Keep initial hidden layout finite');
}
for (const body of [null,{style:{}}]) {
  const scope = {style:{},closest:() => null};
  const context = vm.createContext({scope,body});
  vm.runInContext(runtime.slice(start,end),context);
  vm.runInContext('fitGallery()',context);
  assert.deepEqual(scope.style,{});
  if (body) assert.deepEqual(body.style,{},'Detail stages retain their own sizing');
}
"""
        result = subprocess.run(['node', '-e', code], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_hover_card_stage_reserves_clearance_in_both_entry_points(self):
        css = (self.assets / 'demo-accessibility.css').read_text()
        selector = ':host .demo-root .stage[data-effect="component-hover-preview"]'
        self.assertGreaterEqual(float(declaration(css, selector, 'min-height').removesuffix('px')), 250)
        self.assertEqual(declaration(css, selector, 'justify-content'), 'flex-start')
        self.assertGreater(css.index(selector), css.index(':host(:not([data-interactive])) .demo-root:not(.ds-stage) :is(.canvas,.stage,.guide-card-stage)'))
        skin = (self.assets / 'demo-skins/motion-component-hover-preview.css').read_text()
        stage = '.demo-root .stage[data-effect="component-hover-preview"]'
        panel = stage + ' .hvp-stage.ds-h-panel'
        popup = stage + ' .hvp-pop'
        # Last declarations are the narrow-container overrides. Check both sizes.
        heights = re.findall(re.escape(panel) + r'\s*\{[^}]*min-height:(\d+)px', skin)
        tops = re.findall(re.escape(popup) + r'\s*\{[^}]*top:(\d+)px', skin)
        self.assertEqual(len(heights), 2)
        self.assertEqual(len(tops), 2)
        photo_height = float(declaration(skin, popup + ' .ds-h-photo', 'height').removesuffix('px'))
        photo_margin = float(declaration(skin, popup + ' .ds-h-photo', 'margin-bottom').removesuffix('px'))
        padding = float(declaration(skin, popup, 'padding').removesuffix('px'))
        # Photo, two text lines, original title margin, padding and border.
        popup_height = photo_height + photo_margin + 14 * 1.6 + 5 + 12 * 1.6 + 2 * padding + 2
        for height, top in zip(heights, tops):
            self.assertGreaterEqual(float(height), float(top) + popup_height + 12)
        self.assertEqual(declaration(skin, panel, 'justify-content'), 'flex-start')
        for destination in ('interactions/component-hover-preview', 'components/card', 'interactions'):
            page = (ROOT / f'dist/{destination}/index.html').read_text()
            self.assertIn('data-effect="component-hover-preview"', page, destination)
            self.assertIn('demo-motion.css', page, destination)
            self.assertIn('demo-accessibility.css', page, destination)
            self.assertIn('demo-skins/motion-component-hover-preview.css', page, destination)

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
            ('skill-reference', 'skill-reference-frontend-design', '.demo-root.ds-stage .skill-card dt', 'var(--ds-fill)'),
            ('ui', 'ui-input', '.ds-input-demo .floatfield .fflabel', 'var(--ds-surface)'),
            ('ui', None, '.demo-root #taCountNum', 'var(--ds-stage)'),
            ('ui', 'ui-chip', '.demo-root .chip button', 'var(--ds-fill)'),
        )
        for kind, skin, selector, background in cases:
            css = demo_styles(self.assets, kind, skin)
            color = resolve_color(css, declaration(css, selector, 'color'))
            background = resolve_color(css, background)
            self.assertGreaterEqual(self.contrast(color, background), 4.5, (selector, color, background))
        # Focused labels and hovered remove buttons use their skin colors too.
        for skin, selector, background in (
            ('ui-input', '.ds-input-demo .floatfield input:focus + .fflabel', 'var(--ds-surface)'),
            ('ui-chip', '.ds-chip-panel .chip button:hover:not(:disabled)', 'var(--ds-line)'),
        ):
            css = demo_styles(self.assets, 'ui', skin)
            self.assertGreaterEqual(self.contrast(resolve_color(css, declaration(css, selector, 'color')),
                                                  resolve_color(css, background)), 4.5, selector)
