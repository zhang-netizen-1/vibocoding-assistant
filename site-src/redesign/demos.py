"""Lossless demo markup with per-source assets and Shadow DOM isolation.

The source pages still own every example. Only the demo shell, its lifecycle and
source accent colours are adapted. No original page-level search/navigation runs.
"""
from html import escape
from functools import lru_cache
import importlib.util
from pathlib import Path
import re

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
KINDS = ('ui', 'motion', 'guide', 'skill-reference')


def _styles(source):
    return '\n'.join(re.findall(r'<style[^>]*>(.*?)</style>', source, re.S))


def _script(source):
    return '\n'.join(re.findall(r'<script[^>]*>(.*?)</script>', source, re.S))


def _palette(text):
    # Accent replacements only: charts, illustrative art and danger states retain
    # their semantic colours. The demo's primary action never uses shell blue.
    colors = {
        '#ed462d': 'var(--demo-primary)', '#c73a24': 'var(--demo-primary-active)',
        '#ff6a4a': 'var(--demo-primary)', '#ff5b41': 'var(--demo-primary-hover)',
        '#ff8a70': 'var(--demo-primary)', '#ff9a85': '#C4B5FD',
        '#ffd6cc': '#EDE9FE', '#fdeeea': '#F5F3FF', '#a5321f': 'var(--demo-primary-active)',
        '#1d4ed8': 'var(--demo-primary)', '#2448a4': 'var(--demo-primary-hover)',
    }
    text = re.sub(r'#[\da-fA-F]{3,8}\b', lambda m: colors.get(m[0].lower(), m[0]), text)
    return re.sub(r'rgba\(\s*237\s*,\s*70\s*,\s*45\s*,', 'rgba(109,40,217,', text, flags=re.I)


SHADOW_BASE = '''
:host{display:block;position:relative;isolation:isolate;contain:layout style;min-width:0;width:100%;color:var(--demo-ink,#111827);font:14px/1.6 -apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;--demo-primary:#6D28D9;--demo-primary-hover:#5B21B6;--demo-primary-active:#4C1D95;--demo-stage:#F6F7F9;--demo-ink:#111827;--demo-secondary:#4B5563;--demo-line:#E4E7EC;--demo-soft:#F3F4F6;--text:var(--demo-ink);--bg:#fff;--bg2:#fff;--bg3:var(--demo-soft);--panel:#fff;--panel2:var(--demo-soft);--line2:var(--demo-line);--demo-white:#fff;--font-sans:-apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif;--font-mono:ui-monospace,monospace;--acc:var(--demo-primary);--acc-solid:var(--demo-primary);--accent:var(--demo-primary);--accent-dark:var(--demo-primary-active);--ink:var(--demo-ink);--muted:var(--demo-secondary);--line:var(--demo-line)}
*{box-sizing:border-box} .demo-root{position:relative;min-width:0;overflow:hidden;background:var(--demo-stage);color:var(--demo-ink);border:0!important;border-radius:0!important;box-shadow:none!important;margin:0!important}
.demo-root>.canvas,.demo-root>.stage,.guide-card-stage{border:0;background:var(--demo-stage);background-image:none;min-height:224px;max-width:100%;margin:0;overflow:hidden}
:host(:not([data-demo-playing])) *,:host(:not([data-demo-playing])) *::before,:host(:not([data-demo-playing])) *::after{animation-play-state:paused!important}
:host(:not([data-interactive])) .demo-root{pointer-events:none;user-select:none}
:host([data-demo-playing]) .demo-root{pointer-events:auto}
.modal-mask,.drawer-mask,.drawer-panel,.cmdk-mask{position:absolute!important;inset-block:0;max-height:100%;z-index:20}
.drawer-panel{inset-inline-start:auto;max-width:90%}.modal-box{max-width:92%;width:360px}.toast-wrap{position:absolute!important;inset:auto 12px 12px;pointer-events:none}
.canvas .check,.tab-panel,.segmented,.ie-text,.tl-item.done .tt{color:var(--demo-ink)}.ie-text{border-bottom-color:var(--demo-secondary)}.demo-root input,.demo-root select,.demo-root textarea{accent-color:var(--demo-primary)}.stage .magnet-btn,.stage .ripple-btn{color:#fff!important}.demo-status{display:block;padding:8px 12px;color:var(--demo-secondary);font-size:12px;background:var(--demo-stage)}
:focus-visible{outline:2px solid var(--demo-primary);outline-offset:3px}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important;scroll-behavior:auto!important}}
'''


def css(source):
    """Compatibility API; this stylesheet is loaded inside a ShadowRoot only."""
    original = _styles(source).replace(':root', ':host')
    # Also expose source hover effects to the deliberate automated preview.
    hover = '\n'.join(s + b for s, b in re.findall(r'([^{}]+)(\{[^{}]*\})', original)
                      if (':hover' in s or ':active' in s) and '@' not in s)
    hover = hover.replace(':hover', '[data-preview-hover]').replace(':active', '[data-preview-active]')
    return _palette(original) + '\n' + _palette(hover) + '\n' + SHADOW_BASE


def _ui_script(source):
    script = _script(source)
    script = script[script.index('function demoSearch'):]
    # Retain interaction functions; discard the page's copy/search/shortcuts.
    start = script.index('/* ---- 点击英文名复制术语')
    end = script.index('/* ---- 轮播')
    script = script[:start] + script[end:]
    start = script.index('/* ---- 命令面板')
    end = script.index('/* ---- 密码强度')
    script = script[:start] + '''
    function openCmdk(){const panel=document.getElementById('cmdk');if(panel){panel.classList.add('show');document.getElementById('cmdkInput')?.focus();}}
    function closeCmdk(){document.getElementById('cmdk')?.classList.remove('show');}
    ''' + script[end:]
    # Single-example pages omit every unrelated input/overlay; guard each legacy
    # initialization, rather than constructing dummy nodes or swallowing errors.
    script = re.sub(r"(document\.(?:getElementById|querySelector)\([^\n]+?\))\.addEventListener", r'\1?.addEventListener', script)
    script = script.replace("document.querySelectorAll('input[type=color]')[0].addEventListener", "document.querySelectorAll('input[type=color]')[0]?.addEventListener")
    script = script.replace("  dz.addEventListener('keydown'", "  if(dz&&fi){dz.addEventListener('keydown'")
    script = script.replace('  function toggleDD(e)', '  }\n  function toggleDD(e)')
    script = script.replace("document.getElementById('dd').classList.remove", "document.getElementById('dd')?.classList.remove")
    script = script.replace("function closePopover(){", "function closePopover(){if(!document.getElementById('popover-box'))return;")
    script = script.replace("const track=document.getElementById('carTrack');", "const track=document.getElementById('carTrack');if(!track)return;")
    # Pause the source carousel unless the user explicitly previews/opens it.
    script = script.replace('    auto();\n  })();', '    auto();\n  })();')
    script += "\ndocument.addEventListener('keydown',e=>{if(e.key==='Escape'){closeCmdk();if(document.getElementById('modal'))closeModal();if(document.getElementById('dmask'))closeDrawer();closePopover();}});\n"
    script = re.sub(r'(\w+)\.setPointerCapture\(e\.pointerId\)', r'e.isTrusted&&\1.setPointerCapture(e.pointerId)', script)
    return script


def _motion_script(source):
    script = _script(source)
    # Keep original action handlers, replay, typing, drag/gesture and all extras.
    script = script[script.index('function replay(stage)'):]
    start = script.index('// Canvas 仅在可见时更新')
    end = script.index('function moveDraggedRow')
    script = script[:start] + script[end:]
    script = re.sub(r"(document\.querySelector\('[^']+'\))\.addEventListener", r'\1?.addEventListener', script)
    script = script.replace("const stage=document.getElementById('e-'+kind).querySelector('.stage'),target=stage.querySelector('.micro-card');", "const stage=document.getElementById('e-'+kind)?.querySelector('.stage');if(!stage)continue;const target=stage.querySelector('.micro-card');if(!target)continue;")
    for name in ('wave', 'dragChip', 'headerScroll', 'sectionScroll', 'highlightScroll', 'snapScroll', 'art', 'timeline'):
        script = script.replace(name + '.addEventListener(', name + '?.addEventListener(')
    script = script.replace('  initializeDigits(currentNumber);', '  if(odometer)initializeDigits(currentNumber);')
    script = script.replace("reduce.addEventListener('change', () => updateHeader(headerScroll));", "if(headerScroll)reduce.addEventListener('change', () => updateHeader(headerScroll));")
    script = script.replace('  setInterval(()=>{\n    if(reduce.matches||paused()||switching)return;', '  if(!reduce.matches)setInterval(()=>{\n    if(reduce.matches||paused()||switching)return;')
    script = script.replace('Number(timeline.value)', 'Number(timeline?.value||0)')
    script = script.replace("||document.getElementById('pauseAll').getAttribute('aria-pressed')==='true'", '')
    # Never navigate to a path relative to the outer entry page.
    script = script.replace("scene.querySelector('iframe').src = 'motion-demo-gallery.html'", "scene.querySelector('iframe').src = scene.querySelector('iframe').dataset.initialSrc")
    script = script.replace('el.setPointerCapture(e.pointerId)', 'e.isTrusted&&el.setPointerCapture(e.pointerId)').replace('chip.setPointerCapture(event.pointerId)', 'event.isTrusted&&chip.setPointerCapture(event.pointerId)')
    return '''const reduce=matchMedia('(prefers-reduced-motion: reduce)'),coarse=matchMedia('(pointer: coarse)');
let activeDialog=null,inerted=[];
function openDialog(layer){if(!layer||activeDialog)return;layer.hidden=false;activeDialog=layer;layer.querySelector('[data-action=close]')?.focus();}
''' + script + '''
document.addEventListener('keydown',e=>{if(e.key==='Escape'&&activeDialog)closeLayer(activeDialog);const menu=e.target.closest('.menu-items[role=menu]');if(menu&&['ArrowUp','ArrowDown','Home','End'].includes(e.key)){e.preventDefault();const items=[...menu.querySelectorAll('[role=menuitem]')],i=items.indexOf(document.activeElement);items[e.key==='Home'?0:e.key==='End'?items.length-1:(i+(e.key==='ArrowDown'?1:-1)+items.length)%items.length]?.focus();}});
return {replay};
'''


def _guide_script():
    source = (ROOT / 'site-src/guides.js').read_text()
    start = source.index('  function setText(')
    end = source.index('  for (const card of cards)')
    # The original state functions are independent of the old page shell.
    return source[start:end] + '''
const stage=document.querySelector('.guide-card-stage'),section=scope.dataset.demoSection||document.body.dataset.guide;
function update(mode){stage.dataset.mode=String(mode);if(section==='interaction')updateInteraction(stage,mode);if(section==='data')updateData(stage,mode);if(stage.dataset.demo==='sticky')stage.querySelector('.mini-layout').scrollTop=mode?95:0;}
document.addEventListener('click',e=>{const control=e.target.closest('[data-guide-mode]');if(control)update(Number(control.dataset.guideMode));});
return {preview(){update(1);}};
'''


def _package(kind, script):
    # Lexically scoped facades ensure source code cannot install document-wide
    # handlers or leave unmanaged timers. No eval/Function or inline scripts.
    return "/* Extracted source handlers; demo-runtime owns the lifecycle. */\nwindow.VibeDemos.register(" + repr(kind) + ",env=>{\nconst {scope,document,window,matchMedia,setTimeout,clearTimeout,setInterval,clearInterval,requestAnimationFrame,cancelAnimationFrame,performance,animate,toast}=env;\n" + _palette(re.sub(r'(\w+)\.animate\(', r'animate(\1,', script)) + '\n});\n'


def javascript(source):
    """Compatibility API for the original five-demo builder."""
    return (HERE / 'demo-runtime.js').read_text() + '\n' + _package('ui', _ui_script(source))


def bundle_names(demo):
    """JS ordered before site.js; source CSS loads only inside each ShadowRoot."""
    names = ['demo-runtime.js', f'demo-{demo["kind"]}.js']
    if demo.get('secondary'):
        names.extend(bundle_names(demo['secondary']))
    return tuple(dict.fromkeys(names))


@lru_cache(maxsize=1)
def _ui_inventory():
    from entries import Document
    source = (ROOT / '网页UI元素速查.html').read_text()
    tree = Document(source).root
    anchors = {card.one(cls='canvas').outer(source):card.attrs['id'] for card in tree.find_all('article', 'cmp')}
    overlays = {node.attrs['id']: node.outer(source) for node in tree.find_all()
                if node.attrs.get('id') in ('modal','dmask','dpanel','cmdk')}
    return anchors, overlays


@lru_cache(maxsize=1)
def _classification():
    spec = importlib.util.spec_from_file_location('demo_source_audit', ROOT / 'scripts/audit_demos.py')
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return {entry['old_anchors'][0]:category for entry,category,_ in module.audit()}


def _source_anchor(demo):
    if demo['kind'] == 'motion':
        return 'e-' + demo['key']
    if demo['kind'] == 'ui':
        return _ui_inventory()[0].get(demo['html'], '')
    if demo['kind'] == 'guide':
        return 'g-' + demo['section'] + '-' + demo['key']
    return ''


def markup(demo, prefix, interactive=False):
    """Return a dormant template INSIDE the caller's .demo-scope host.

    prefix is the relative assets/redesign/ directory, including trailing slash.
    Template IDs are original source IDs and enter only an isolated ShadowRoot.
    """
    from entries import Document
    kind, content = demo['kind'], demo['html']
    content = content.replace('href="javascript:void 0"', 'href="#"').replace("href='javascript:void 0'", "href='#'")
    extra = ''
    if kind == 'ui':
        overlays = _ui_inventory()[1]
        for trigger, ids in [('openModal', ('modal',)), ('openDrawer', ('dmask','dpanel')), ('openCmdk', ('cmdk',))]:
            if f'data-cmd="{trigger}"' in content:
                extra += ''.join(overlays[identifier] for identifier in ids)
        cls = 'cmp'
    elif kind == 'motion':
        cls = 'effect-card'
        content = content.replace('src="motion-demo-gallery.html"', f'src="{escape(prefix)}motion-demo-gallery.html" data-initial-src="{escape(prefix)}motion-demo-gallery.html"')
    elif kind == 'guide':
        cls = 'site-guide'
        content = f'<div class="guide-card-stage" data-demo="{escape(demo["key"])}" data-mode="0">{content}</div>'
        if interactive:
            # These are preview controls, not new entry copy.
            content += '<div class="demo-controls"><button type="button" data-guide-mode="0">初始状态</button><button type="button" data-guide-mode="1">切换状态</button></div>'
    else:
        cls = 'site-skills'
        tree = Document(content).root
        # Static original overview, without installation prompts or nested footer
        # navigation competing with the enclosing entry's canonical prompt.
        head = tree.find_all(cls='skill-card-top')
        body = tree.find_all(cls='skill-card-body')
        content = '<div class="skill-card">' + ''.join(n.outer(content) for n in head+body) + '</div>'
    # The source has a damaged hex-label ID; repair only that attribute.
    content = content.replace('id=#ed462d" data-x="x" data-hexc="', 'id="hexc"')
    anchor = _source_anchor(demo)
    category = '静态演示' if kind == 'skill-reference' else _classification().get(anchor, '')
    attrs = f' id="{escape(anchor)}"' if anchor else ''
    if kind == 'guide':
        attrs += f' data-guide="{escape(demo["section"])}"'
    result = f'<template data-demo-template data-demo-css="{escape(prefix)}demo-{kind}.css" data-demo-static="{'true' if category == '静态演示' else 'false'}" data-demo-category="{escape(category)}"><article class="demo-root {cls}"{attrs}>{content}{extra}</article></template>'
    return result


def assets(entries):
    return _assets()


@lru_cache(maxsize=1)
def _assets():
    ui = (ROOT / '网页UI元素速查.html').read_text()
    motion = (ROOT / '动效速查.html').read_text()
    result = {
        'demo-runtime.js': (HERE / 'demo-runtime.js').read_text(),
        'demo-ui.js': _package('ui', _ui_script(ui)),
        'demo-motion.js': _package('motion', _motion_script(motion)),
        'demo-guide.js': _package('guide', _guide_script()),
        'demo-skill-reference.js': _package('skill-reference', 'return {};'),
        'demo-ui.css': css(ui), 'demo-motion.css': css(motion),
        'demo-guide.css': css('<style>' + (ROOT / 'site-src/guides.css').read_text() + (ROOT / 'site-src/visual-styles.css').read_text() + '</style>'),
        'demo-skill-reference.css': css('<style>' + (ROOT / 'site-src/skills.css').read_text() + '</style>'),
        'demos.css': '.demo-scope{display:block;position:relative;min-width:0;width:100%;isolation:isolate}.demo-secondary{margin-top:16px}.demo-scope>template{display:none}\n',
    }
    for page in ('motion-demo-gallery', 'motion-demo-detail'):
        original = (ROOT / (page + '.html')).read_text()
        result[page + '.css'] = _palette(_styles(original))
        result[page + '.html'] = re.sub(r'<style[^>]*>.*?</style>', f'<link rel="stylesheet" href="{page}.css">', original, flags=re.S)
    return result


def smoke_fixture(entries):
    """Serializable real-source DOMs for demo-smoke.cjs initialization checks."""
    from entries import Document
    def node_data(node):
        return dict(tag=node.tag, attrs=node.attrs, children=[node_data(child) for child in node.children if hasattr(child, 'tag')])
    rows = []
    for entry in entries:
        demos = [entry['demo']] + ([entry['demo']['secondary']] if entry['demo'].get('secondary') else [])
        for demo in demos:
            source = Document(markup({k:v for k,v in demo.items() if k != 'secondary'}, './', True)).root
            article = source.one('article')
            rows.append(dict(kind=demo['kind'],section=demo.get('section',''),anchor=_source_anchor(demo) or entry['old_anchors'][0],node=node_data(article)))
    return dict(demos=rows, sources={kind:_assets()[f'demo-{kind}.js'] for kind in KINDS})
