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

    def test_demo_spec_tokens_and_stage_are_separate_from_shell(self):
        css = (REDESIGN / 'demo-spec.css').read_text()
        colors = dict(re.findall(r'(--ds-[\w-]+):\s*(#[\da-fA-F]{6})', css))
        for key, value in {'stage':'#F7F7F8','ink':'#111827','ink-2':'#4B5563',
                           'border':'#868E9C','accent':'#6D28D9','accent-hover':'#5B21B6',
                           'accent-active':'#4C1D95','success':'#047857','danger':'#B91C1C'}.items():
            self.assertEqual(colors['--ds-' + key], value)
        for name in ['caption','label','body','strong','title','display']:
            self.assertRegex(css, '--ds-text-' + name + r':\d+px')
            self.assertIn('--ds-text-' + name + '-line-height:', css)
            self.assertIn('--ds-text-' + name + '-weight:', css)
        for name in ['1','2','3']:
            value = re.search('--ds-shadow-' + name + ':([^;]+)', css)[1]
            self.assertEqual(value.count('rgb('),2)
        for name in ['instant','fast','base','slow','scene']:
            self.assertIn('--ds-dur-' + name + ':',css)
        for name in ['standard','out','in','spring']:
            self.assertIn('--ds-ease-' + name + ':',css)
        for cls in ['stage','surface','hint','caption','img']:
            self.assertIn('.ds-' + cls,css)
        for lower_bound in ['max(320px,62.5cqi)','max(300px,66.667cqi)','max(260px,75cqi)']:
            self.assertIn('min-height:' + lower_bound,css)
        self.assertNotRegex(css, r'aspect-ratio:(?:16/10|3/2|4/3)')
        self.assertIn('aspect-ratio:auto',css)
        self.assertIn('--ds-subject-width:clamp(320px,52%,640px)',css)
        self.assertIn('@container demo-stage (min-width:640px)',css)
        self.assertIn('--ds-subject-width:clamp(420px,66%,560px)',css)
        self.assertIn('--ds-demo-body:16px',css)
        self.assertIn('--ds-demo-heading:22px',css)
        self.assertIn('--ds-demo-button:15px',css)
        self.assertIn('--ds-demo-control:48px',css)
        self.assertIn('inset:auto auto 12px 12px!important',css)
        self.assertIn('padding:16px 16px 76px',css)
        self.assertIn('0 0/24px 24px',css)
        self.assertIn('overflow:visible',css)
        self.assertNotIn('demo-spec.css', (REDESIGN/'templates.py').read_text().split('ASSETS =',1)[-1].split('\n\n',1)[0])

    def test_demo_spec_contrast_pairs(self):
        with contextlib.redirect_stdout(io.StringIO()):
            contrast = runpy.run_path(str(ROOT/'docs/style-research/contrast.py'))['cr']
        css = (REDESIGN/'demo-spec.css').read_text()
        colors=dict(re.findall(r'--ds-([\w-]+):\s*(#[\da-fA-F]{6})',css))
        self.assertGreaterEqual(contrast('#FFFFFF','#666666'),4.5)
        for fg,bg,minimum in [('ink-2','stage',7),('ink-3','surface',4.5),
                               ('surface','accent',7),('border','surface',3),
                               ('success','success-soft',4.5),('danger','danger-soft',4.5)]:
            self.assertGreaterEqual(contrast(colors[fg],colors[bg]),minimum,(fg,bg))

    def test_batch_b_specimen_styles_and_motion_contracts(self):
        skins=REDESIGN/'demo-skins'
        expected={
            'ui-modal':['rgb(17 24 39 / .45)','backdrop-filter:blur(4px)','var(--ds-shadow-3)','justify-content:flex-end','font-size:var(--ds-demo-title)'],
            'ui-tooltip':['background:#111827','color:#fff','13px/1.5','border-radius:8px','border-top-color:#111827'],
            'motion-scroll-reveal':['translateY(16px)','360ms var(--ds-ease-out)','ds-revealed','prefers-reduced-motion'],
            'guide-grid':['repeat(auto-fit,minmax(min(100%,128px),1fr))','gap:16px','gap:24px','height:auto'],
            'ui-skeleton':['background:#E9EBEF','rgb(255 255 255 / .75)','var(--ds-surface)','is-loaded'],
            'ui-carousel':['border-radius:16px','var(--ds-shadow-2)','width:24px','var(--ds-accent)','min-height:44px'],
        }
        for skin,contracts in expected.items():
            css=(skins/(skin+'.css')).read_text()
            for contract in contracts:self.assertIn(contract,css,skin)
            self.assertNotRegex(css,r'rgba\(0,0,0,')
        for name in ('ui-input','motion-component-lift','motion-view-crossfade','ui-modal','ui-tooltip','motion-scroll-reveal','guide-grid','ui-skeleton','ui-carousel'):
            self.assertIn('@container demo-stage (min-width:640px)',(skins/(name+'.css')).read_text())
        self.assertIn('.ds-tooltip-copy p{margin:8px 0 0;font-size:var(--ds-demo-body)',(skins/'ui-tooltip.css').read_text())
        source=(REDESIGN/'demos.py').read_text()
        self.assertIn('setTimeout(finishSkeleton,1400)',source)
        self.assertIn("setAttribute('aria-busy','false')",source)
        self.assertIn("rect.top<viewport.bottom-16",source)

    def test_subject_width_and_mobile_clearance_calculations(self):
        # Mirrors border-box stage padding and the public clamp, with no browser.
        for stage,padding in [(342,16),(358,16),(390,16),(725.333,32),(768,32),(960,32),(1200,32),(1440,32)]:
            inner=stage-2-2*padding
            subject=min(inner,max(420,min(inner*.66,560))) if stage>=640 else min(inner,max(320,min(inner*.52,640)))
            self.assertLessEqual(subject,inner)
            self.assertGreaterEqual((stage-subject)/2,16)
            if 640<=stage<=960:self.assertTrue(.60<=subject/inner<=.72)
            if stage>=1200:self.assertLessEqual(subject,560)
        # Two lines of 12px/1.5 text + capsule padding/border + bottom offset.
        hint_height=2*12*1.5+2*6+2
        self.assertLessEqual(hint_height+12+12,76)

    def test_detail_widths_choose_readable_type_and_grid_columns(self):
        desktop_stage=((1184-64)-32)*2/3
        mobile_stage=390-32
        def card_width(stage,padding):
            inner=stage-2*padding-2
            return min(inner,max(420,min(560,inner*.66))) if stage>=640 else min(inner,max(320,min(640,inner*.52)))
        desktop_card=card_width(desktop_stage,32)
        mobile_card=card_width(mobile_stage,16)
        self.assertAlmostEqual(desktop_card,435.16)
        self.assertEqual(mobile_card,320)
        self.assertEqual(int((desktop_card-50+16)/(128+16)),2)
        grid=(REDESIGN/'demo-skins/guide-grid.css').read_text()
        self.assertIn('grid-template-columns:repeat(2,minmax(0,1fr))',grid)
        self.assertIn('nth-child(n+5)',grid)
        css=(REDESIGN/'demo-spec.css').read_text()
        self.assertNotIn('@media(min-width:1024px)',css)


    def test_kind_token_skin_preserves_teaching_properties(self):
        css=(REDESIGN/'demo-skins/_kind-token.css').read_text()
        self.assertIn('.token-card:not(.elevation-card):not(.theme-sample)',css)
        self.assertNotIn('--sample-radius:',css)
        self.assertNotIn('--sample-shadow:',css)
        self.assertNotIn('--theme-bg:',css)
        self.assertNotIn('--sample-padding:',css)
        guide=(REDESIGN/'demo-skins/_kind-guide.css').read_text()
        self.assertIn('[data-demo="sticky"] .mini-layout { height:260px; overflow-y:auto;',guide)

    def test_hint_parent_fills_stage_without_losing_positioning_context(self):
        css=(REDESIGN/'demo-spec.css').read_text()
        selector='.demo-root.ds-stage > :is(.canvas,.stage,.guide-card-stage):has(> .ds-hint)'
        self.assertIn(selector,css)
        body=css.split(selector,1)[1].split('}',1)[0]
        for declaration in ('position:relative','flex:1 0 auto','min-height:min-content',
                            'padding-bottom:56px!important','align-content:safe center','overflow:visible'):
            self.assertIn(declaration,body)
        self.assertIn('.demo-root.ds-stage:has(> :is(.canvas,.stage,.guide-card-stage) > .ds-hint)',css)
        self.assertNotRegex(css,r'data-ds-sample[^{}]*>[^{}]*\{[^}]*position:static')
        a11y=(REDESIGN/'demo-accessibility.css').read_text()
        self.assertNotRegex(a11y,r'ds-(?:button|input|lift|crossfade)-demo[^{}]*\{[^}]*position:static')

    def test_ui_and_motion_kind_surfaces_exclude_hint_containers(self):
        skins=REDESIGN/'demo-skins'
        self.assertFalse((REDESIGN/'demo-skins-wip').exists())
        for kind in ('ui','motion'):
            css=(skins/('_kind-'+kind+'.css')).read_text()
            self.assertIn('var(--ds-surface)',css)
            self.assertIn(':not(.ds-hint)',css)
            for selectors,body in re.findall(r'([^{}]+)\{([^{}]*)\}',css):
                if re.search(r'>\s*\.(canvas|stage)\s*$',selectors.strip()):
                    self.assertNotIn('background:var(--ds-surface)',body)
                    self.assertNotIn('box-shadow:var(--ds-shadow-',body)
            self.assertNotIn('position:static',css)

    def test_floating_subjects_reserve_their_open_rectangles(self):
        ui=(REDESIGN/'demo-skins/_kind-ui.css').read_text()
        motion=(REDESIGN/'demo-skins/_kind-motion.css').read_text()
        for selector,height in (('.dropdown.open',176),
                                ('.popover-demo:has(> .popover-box:not([hidden]))',144),
                                ('.splitbtn-demo:has(> .split-menu:not([hidden]))',152)):
            body=ui.split(selector,1)[-1].split('}',1)[0]
            self.assertIn('margin-bottom:'+str(height)+'px',body)
        for selector,height in (('.mini-menu:has(> .menu-items:not([hidden]))',181),('.hvp-stage',152)):
            body=motion.split(selector,1)[-1].split('}',1)[0]
            self.assertIn('min-height:'+str(height)+'px',body)
        # Existing positioned popup rectangles at the two requested widths.
        self.assertLessEqual(6+3*(14*1.6+18)+(18+12)+14,176)
        self.assertLessEqual(9+28+4*13*1.6+5,144)
        self.assertLessEqual(5+3*44+12,152)
        self.assertEqual(39+3*44+10,181)
        self.assertLessEqual(76+24+13*1.6+5+12*1.6,152)

    def test_hint_rectangle_clearance_at_both_requested_widths(self):
        css=(REDESIGN/'demo-spec.css').read_text()
        self.assertIn('padding-bottom:76px!important',css.split('@container demo-stage (max-width:380px)',1)[-1])
        for stage,inset,reserve,lines,ratio in ((725.333,32,56,1,.625),(358,16,76,2,.75)):
            hint_height=lines*12*1.5+2*6+2
            for subject_height in (44,48,120,260,600,1200):
                with self.subTest(stage=stage,subject_height=subject_height):
                    # Auto height grows with intrinsic content. Border-box wrapper
                    # fills the parent's content box and keeps its own padding.
                    inside=max(max(320 if stage>640 else 260,stage*ratio)-2,
                               inset+subject_height+reserve)
                    available=inside-inset-reserve
                    subject_top=1+inset+(available-subject_height)/2
                    subject_bottom=subject_top+subject_height
                    hint_top=1+inside-12-hint_height
                    self.assertGreaterEqual(hint_top-subject_bottom,12)
                    self.assertLessEqual(subject_bottom,1+inside-reserve)
                    self.assertEqual(1+inside-(hint_top+hint_height),12)
                    self.assertGreaterEqual(subject_top,1+inset)

    def test_c_samples_use_scoped_light_surfaces(self):
        skins=REDESIGN/'demo-skins'
        for name in ('token-color','ui-color','guide-dashboard','skill-reference-frontend-design'):
            css=(skins/(name+'.css')).read_text()
            self.assertIn('var(--ds-surface)',css,name)
            self.assertNotIn('!important',css,name)
            self.assertIn('var(--ds-shadow-1)',css if name!='ui-color' else (REDESIGN/'demo-spec.css').read_text(),name)
        self.assertIn('.demo-root.ds-stage .skill-card dt',(skins/'skill-reference-frontend-design.css').read_text())


    def test_e_skins_keep_spec_geometry_and_state_grid(self):
        skins = REDESIGN / 'demo-skins'
        names = ('ui-states', 'guide-landing', 'ui-card', 'ui-toast', 'ui-navbar',
                 'ui-table', 'ui-tabs', 'ui-switch', 'ui-select', 'ui-hold-confirm',
                 'motion-view-slide', 'motion-view-curtain', 'motion-media-wipe',
                 'motion-media-blur', 'motion-scroll-parallax', 'motion-scroll-pin')
        for name in names:
            css = (skins / (name + '.css')).read_text()
            self.assertIn('width:min(100%,var(--ds-subject-width))', css, name)
            self.assertIn('var(--ds-shadow-1)', css, name)
            self.assertIn('border-radius:16px', css, name)
            self.assertNotRegex(css, r'(?<![\w-])font-size:\s*(?:[0-9]|1[01])px')
            self.assertNotRegex(css, r'https?://|@import|@font-face')
        states = (skins / 'ui-states.css').read_text()
        self.assertIn('grid-template-columns:repeat(4,minmax(0,1fr))', states)
        self.assertIn('grid-template-columns:repeat(3,minmax(0,1fr))', states)
        self.assertIn('color:var(--ds-ink-3); font:400 12px', states)
        self.assertIn('height:var(--ds-demo-control); min-height:44px', states)
        self.assertIn('var(--ds-shadow-3)', (skins / 'ui-toast.css').read_text())
        for stage, inset in ((725.333,32),(358,16)):
            available = stage - 2 - 2 * inset
            width = min(available, max(420, min(available*.66,560))) if stage >= 640 else min(available,320)
            self.assertGreaterEqual((stage-width)/2,16)
            if stage >= 640:
                self.assertGreaterEqual(width/stage,.55)
                self.assertLessEqual(width/stage,.66)


class BatchFTokenTest(unittest.TestCase):
    def test_f_individual_skins_keep_geometry_states_and_tokens(self):
        names = ('checkbox', 'radio', 'slider', 'otp', 'search', 'segmented',
                 'password-strength', 'tag-input', 'stepper', 'rating', 'upload',
                 'combobox', 'date', 'form', 'alert', 'empty', 'loader', 'drawer', 'popover')
        skins = REDESIGN / 'demo-skins'
        for name in names:
            with self.subTest(name=name):
                css = (skins / ('ui-' + name + '.css')).read_text()
                self.assertIn('width:min(100%,var(--ds-subject-width))', css)
                self.assertIn('border-radius:16px', css)
                self.assertIn('var(--ds-shadow-1)', css)
                self.assertIn(':focus-visible', css)
                self.assertIn(':disabled', css)
                self.assertIn('[aria-invalid="true"]', css)
                self.assertIn('@container demo-stage (max-width:480px)', css)
                self.assertNotRegex(css, r'(?<![\w-])font-size:\s*(?:[0-9]|1[01])px')
                self.assertNotRegex(css, r'#[0-9a-fA-F]{3,8}|https?://|@import|@font-face')
        self.assertIn('repeat(3,minmax(44px,1fr))', (skins / 'ui-otp.css').read_text())
        self.assertIn('margin-bottom:168px', (skins / 'ui-popover.css').read_text())
        self.assertIn('var(--ds-shadow-3)', (skins / 'ui-drawer.css').read_text())
        self.assertIn('animation:none', (skins / 'ui-loader.css').read_text())

    def test_g_intrinsic_canvas_keeps_top_clearance_for_long_subjects(self):
        css = (REDESIGN / 'demo-spec.css').read_text()
        selector = '.demo-root.ds-stage > :is(.canvas,.stage,.guide-card-stage):has(> .ds-hint)'
        body = css.split(selector, 1)[1].split('}', 1)[0]
        for declaration in ('flex:1 0 auto', 'min-height:min-content', 'align-items:safe center',
                            'justify-content:safe center', 'align-content:safe center',
                            'padding-top:max(16px,var(--ds-stage-inset))!important'):
            self.assertIn(declaration, body)
        self.assertIn('height:auto', css)
        for content_height in (44, 260, 390, 600, 1200):
            height = max(268.5, 2 + 16 + content_height + 76)
            top = 1 + 16 + max(0, height - 2 - 16 - 76 - content_height) / 2
            self.assertGreaterEqual(top, 16)
            self.assertGreaterEqual(height - top - content_height, 16)

    def test_g_individual_skins_keep_spec_and_popup_clearance(self):
        skins = REDESIGN / 'demo-skins'
        slugs = 'cmdk sidebar accordion breadcrumb pagination steps dropdown context-menu mega-menu footer badge chip avatar kpi timeline badge-dot view-switch card-link split-button fab back-to-top table-fixed table-columns table-edit sortable-table load-more'.split()
        for slug in slugs:
            with self.subTest(slug=slug):
                kind = 'guide' if slug == 'sortable-table' else 'ui'
                css = (skins / (kind + '-' + slug + '.css')).read_text()
                for contract in ('width:min(100%,var(--ds-subject-width))', 'min-width:0',
                                 'border-radius:16px', 'var(--ds-shadow-1)', ':focus-visible',
                                 ':disabled', '[aria-invalid="true"]', 'prefers-reduced-motion',
                                 '@container demo-stage (max-width:480px)'):
                    self.assertIn(contract, css, slug)
                self.assertNotIn('.ds-hint', css)
                self.assertNotRegex(css, r'#[\da-fA-F]{3,8}|https?://|@import|@font-face')
                self.assertNotRegex(css, r'font-size:\s*(?:[0-9]|1[01])px')
        self.assertIn('margin-bottom:188px', (skins / 'ui-dropdown.css').read_text())
        self.assertIn('margin-bottom:176px', (skins / 'ui-split-button.css').read_text())
        self.assertIn('min-height:192px', (skins / 'ui-context-menu.css').read_text())
        self.assertIn('min-width:480px', (skins / 'ui-table-fixed.css').read_text())
        self.assertIn('position:static', (skins / 'ui-card-link.css').read_text())

    def test_g_cmdk_expanded_height_outweighs_mobile_stage_rule(self):
        css = (REDESIGN / 'demo-skins/ui-cmdk.css').read_text()
        self.assertIn('.demo-root.ds-stage:has(.cmdk-mask.show) { min-height:560px; }', css)
        self.assertIn('var(--ds-shadow-3)', css)

    def test_h_motion_skins_keep_subject_size_tokens_and_motion_gate(self):
        slugs = 'component-tilt component-spotlight component-flip component-press component-switch component-morph tab-indicator inline-expand component-magnetic component-hover-preview component-hover-action component-ripple component-underline accordion overlay-menu overlay-drawer overlay-modal overlay-tooltip overlay-sheet toast-stack data-count data-bars data-reorder data-success filter-grid chart-morph skeleton-handoff data-input-shake data-skeleton text-stagger text-mask text-typewriter text-scramble text-draw odometer scroll-highlight text-text-morph'.split()
        for slug in slugs:
            with self.subTest(slug=slug):
                css = (REDESIGN / 'demo-skins' / ('motion-' + slug + '.css')).read_text()
                for token in ('width:min(100%,var(--ds-subject-width))', 'min-width:0', 'var(--ds-surface)', 'var(--ds-shadow-1)', 'prefers-reduced-motion', 'data-demo-motion-once', ':focus-visible', '@container demo-stage (max-width:480px)'):
                    self.assertIn(token, css)
                self.assertNotIn('.ds-hint', css)
                self.assertNotRegex(css, r'@import|@font-face|https?://|font-size:\s*(?:[0-9]|1[01])px')
                self.assertNotIn('@keyframes', css)
