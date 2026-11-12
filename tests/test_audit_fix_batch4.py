"""Shared responsive, demo typography and typo regressions for batch four."""
from pathlib import Path
import re
import subprocess
import unittest

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'site-src/redesign'


def small_fonts(text):
    return [value for value in re.findall(r'(?<![\w-])font(?:-size)?\s*:\s*([^;}"\']+)', text)
            if any(float(size) < 12 for size in re.findall(r'(?<![\w.-])([\d.]+)px', value))]


class AuditFixBatch4Test(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(['python3', 'scripts/build_site.py'], cwd=ROOT, check=True, capture_output=True)

    def test_short_chinese_typos_and_ascii_noise(self):
        code = """
const assert = require('node:assert/strict');
const search = require('./site-src/redesign/search.js');
const {entries} = require('./dist/assets/search-index.json');
for (const [query,name] of [['按扭','按钮'],['输人框','输入框'],['滑东条','滑动条'],['轮拨图','轮播图']]) {
  assert.equal(search.similar(entries,query)[0]?.zh,name,query);
}
for (const query of ['asdfgh','qwerty','zzzz','jkl;','xyzxyz']) {
  assert.deepEqual(search.match(entries,query),[],query);
  assert.deepEqual(search.similar(entries,query),[],query);
}
assert.deepEqual(search.similar([{zh:'窗帘',en:'abxxef',aliases:[]}],'abcdef'),[]);
assert.equal(search.similar(entries,'buton')[0]?.zh,'按钮');
"""
        result = subprocess.run(['node', '-e', code], cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_every_generated_demo_font_declaration_is_at_least_twelve(self):
        assets = ROOT / 'dist/assets/redesign'
        for name in ('demo-ui.css', 'demo-motion.css', 'demo-guide.css',
                     'demo-skill-reference.css', 'demo-token.css', 'states.css',
                     'motion-demo-gallery.css', 'motion-demo-detail.css'):
            self.assertEqual(small_fonts((assets / name).read_text()), [], name)
        # Inline styles can override CSS: inspect every generated demo template too.
        for page in (ROOT / 'dist').rglob('*.html'):
            for demo in re.findall(r'<template data-demo-template\b.*?</template>', page.read_text(), re.S):
                self.assertEqual(small_fonts(demo), [], str(page))

    def test_tablet_header_and_runtime_share_the_1024_breakpoint(self):
        css = (SOURCE / 'site.css').read_text()
        self.assertNotIn('min-height:96px', css)
        self.assertNotIn('flex-basis:100%', css)
        self.assertRegex(css, r'@media\(max-width:1023px\)\s*\{\s*\.nav-inner\{[^}]*height:calc\(var\(--nav-height\) - 1px\)')
        self.assertIn('.desktop-nav,.desktop-search,.mega{display:none}', css)
        self.assertIn("matchMedia('(max-width:1023px)')", (SOURCE / 'site.js').read_text())
        home = (ROOT / 'dist/index.html').read_text()
        self.assertIn('<kbd class="shortcut-hint">⌘K</kbd>', home)
        self.assertNotIn('搜索 ⌘K</span>', home)
        self.assertIn('<kbd class="shortcut-hint">/</kbd>', home)
        self.assertIn('(hover:none), (pointer:coarse)', css)
        self.assertIn('.shortcut-hint,.search-help{display:none}', css)

    def test_touch_targets_use_layout_space_and_keep_inline_prose_links(self):
        css = (SOURCE / 'site.css').read_text()
        self.assertIn('@media(max-width:1023px), (hover:none), (pointer:coarse)', css)
        self.assertIn(':where(a,button,summary){min-height:44px}', css)
        self.assertIn('a:where(:not(p a))', css)
        for selector in ('.breadcrumbs a', '.drawer-body>p>a', '.menu-group-link', '.play-button'):
            self.assertIn(selector, css)
        self.assertIn('.play-button{min-height:44px', css)
        self.assertIn('.nav-search{min-height:44px}', css)
        self.assertNotIn('margin-block:-', css)
        for kind in ('ui','motion','guide','token','skill-reference'):
            demo_css = (ROOT / f'dist/assets/redesign/demo-{kind}.css').read_text()
            self.assertIn(':host([data-interactive]) :is(a,button,summary)', demo_css)
            self.assertRegex(demo_css, r'min-height:\s*44px')
            self.assertIn('.car-track { grid-column:1/-1;grid-row:1;', demo_css)
            self.assertIn('.car-dots { position:static;', demo_css)

    def test_column_and_command_demo_shortcuts_are_separately_hideable(self):
        for column in ('basics','components','interactions','scenarios','ai'):
            html = (ROOT / f'dist/{column}/index.html').read_text()
            self.assertIn('搜索条目 <kbd class="shortcut-hint">⌘K</kbd>', html)
            self.assertNotIn('搜索条目　⌘K', html)
        command = (ROOT / 'dist/components/cmdk/index.html').read_text()
        self.assertIn('<span class="demo-shortcut-hint">，或直接按 ⌘K / Ctrl+K</span>', command)
        self.assertIn('<span class="demo-shortcut-hint"> ⌘K</span>', command)
        self.assertIn('.demo-shortcut-hint', (SOURCE / 'demo-accessibility.css').read_text())

    def test_gallery_zoom_is_shadow_local_and_stage_can_grow(self):
        css = (SOURCE / 'site.css').read_text()
        self.assertIn('.gallery-card{container-type:inline-size}', css)
        self.assertIn('.mini-stage{min-height:max(240px,75cqw);height:auto', css)
        self.assertNotIn('.mini-stage{aspect-ratio:', css)
        self.assertIn('padding:12px 12px 60px', css)
        for kind in ('ui','motion','guide','token','skill-reference'):
            demo_css = (ROOT / f'dist/assets/redesign/demo-{kind}.css').read_text()
            self.assertIn(':host(:not([data-interactive])) .demo-root', demo_css)
            self.assertNotIn('zoom:1.35', demo_css)
            self.assertIn('.scene-description', demo_css)
            self.assertIn('overflow-wrap:anywhere', demo_css)
        runtime = (SOURCE / 'demo-runtime.js').read_text()
        self.assertIn("body.style.width='312px'", runtime)
        self.assertIn('Math.min(1.35,width/312', runtime)
