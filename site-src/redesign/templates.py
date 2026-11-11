"""Shared shell, five column galleries and all unified entry pages."""
from html import escape
from pathlib import Path
import hashlib
import json
import posixpath
import re
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import demos
import states

ASSETS = ('tokens.css', 'base.css', 'site.css', 'site.js', 'search.js', 'states.css')
EXAMPLES = ('浮起来', '弹出来的小黑框', 'Crossfade', '点了会变的按钮')


def entry_destination(entry):
    middle = 'skills/' if entry['column'] == 'ai' else ''
    return f'{entry["column"]}/{middle}{entry["slug"]}/'


def generated_pages(entries):
    return ['index.html', *(f'{column}/index.html' for column in ('basics', 'components', 'interactions', 'scenarios', 'ai')),
            *(entry_destination(e) + 'index.html' for e in entries), 'interactions/spec/index.html']


def generated_files(entries):
    return generated_pages(entries) + [f'assets/redesign/{name}' for name in (*ASSETS, *demos.assets(entries))]



def relative(page, destination):
    path, mark, fragment = destination.partition('#')
    path = path.strip('/')
    result = posixpath.relpath(path or '.', posixpath.dirname(page) or '.')
    if result == '.':
        result = './'
    elif not result.startswith('.'):
        result = './' + result
    if path.endswith('.html') or path.startswith('assets/'):
        pass
    elif not result.endswith('/'):
        result += '/'
    return result + (mark + fragment if mark else '')


def column_destination(column):
    return column + '/'


def group_destination(column, group):
    return column + '/#group-' + group


def copy_payload(entry, version='prompt_edit'):
    if entry.get('prompt_edit'):
        criteria = '\n'.join(f'{i}. {text}' for i,text in enumerate(entry['acceptance'], 1))
        return (entry[version] + '\n\n验收要求：\n' + criteria +
                f'\n\n完成后列出改了哪些文件，并说明以上 {len(entry["acceptance"])} 条各自是怎么验证的。')
    parts = [entry['prompt']]
    if entry.get('prompt_secondary'):
        parts.append(entry['prompt_secondary'])
    parts.extend(text for text in entry['acceptance'] if not any(text in part for part in parts))
    return '\n\n'.join(parts)



def query_buttons():
    return ''.join(f'<button class="chip" data-query="{escape(q)}">{escape(q)}</button>' for q in EXAMPLES)


def header(page, tax):
    triggers, panels, drawers = [], [], []
    for column in tax['columns']:
        slug, name = column['slug'], column['name']
        number = f'{column["order"]:02d}'
        triggers.append(f'<button class="nav-trigger" data-nav="{slug}" aria-expanded="false" aria-controls="mega-{slug}"><span class="nav-number">{number}</span> {name}</button>')
        groups = []
        for group in column['groups']:
            target = group_destination(slug, group['slug'])
            label = f'{escape(group["name"])} <span class="count">{group["expected"]} 条</span>'
            groups.append(f'<div class="menu-group"><a class="menu-group-link" href="{relative(page, target)}">{label}</a></div>' if target else f'<div class="menu-group"><span class="menu-group-link">{label}</span><p class="menu-note">三期新增</p></div>')
        if slug == 'interactions':
            groups.append(f'<div class="menu-group"><a class="menu-group-link" href="{relative(page, "interactions/spec/")}">动效实现规范 <span class="count">不计条目</span></a></div>')
        if slug == 'ai':
            groups.append(f'<div class="menu-group"><a class="menu-group-link" href="{relative(page, "bench/")}">测评结果</a></div>')
        # No entry lists in either menu. Only the approved component intro.
        first = f'<p class="small menu-intro">先看：<a href="{relative(page, "components/states/")}">组件状态</a></p>' if slug == 'components' else ''
        panels.append(f'<div class="mega" id="mega-{slug}" hidden><div class="wrap mega-inner"><div class="row between mega-heading"><h2>{name}</h2><span class="small">{column["expected"]} 条</span></div>{first}<div class="mega-grid">{"".join(groups)}</div></div></div><!-- mega -->')
        drawers.append(f'<details class="drawer-category"><summary>{number} {name}</summary>{"".join(groups)}</details>')
    return f'''<a class="skip" href="#main">跳到主要内容</a>
<header class="header" id="header"><div class="wrap nav-inner"><a class="brand" href="{relative(page, '')}"><span class="logo" aria-hidden="true"></span>Vibe Design 速查</a><nav class="desktop-nav" aria-label="主导航"><a class="nav-link" href="{relative(page, '')}">首页</a>{''.join(triggers)}</nav><div class="nav-actions"><button class="nav-search" id="nav-search" aria-haspopup="dialog" aria-controls="search-dialog"><span class="desktop-search">搜索 ⌘K</span><span class="mobile-only"><span class="search-icon" aria-hidden="true"></span><span class="sr">搜索</span></span></button><button class="mobile-only menu-button" id="directory-toggle" aria-haspopup="dialog" aria-controls="directory" aria-expanded="false">目录</button></div></div>{''.join(panels)}</header>
<dialog class="overlay drawer" id="directory" aria-labelledby="drawer-title"><div class="drawer-head row between"><h2 id="drawer-title">浏览目录</h2><button class="close-button" data-close="directory" autofocus>关闭</button></div><div class="drawer-body"><p><a href="{relative(page, '')}">首页 →</a></p>{''.join(drawers)}</div></dialog>'''


def mapped_entries(entry, entries, tax):
    anchors = {anchor:item for item in entries for anchor in item['old_anchors']}
    forward, reverse = [], []
    for pair in tax['component_motion']:
        if pair['component'] in entry['old_anchors']:
            forward.append(anchors[pair['motion']])
        if pair['motion'] in entry['old_anchors']:
            reverse.append(anchors[pair['component']])
    def unique(items):
        return list({entry_destination(item):item for item in items}.values())
    return unique(forward), unique(reverse)


def motion_links(entry, page, entries, tax):
    forward, reverse = mapped_entries(entry,entries,tax)
    parts = []
    if forward:
        shown = ''.join(gallery_card(item,page,compact=True) for item in forward[:6])
        more = '<details class="more-motions"><summary>更多动效</summary><div class="gallery motion-grid">' + ''.join(gallery_card(item,page,compact=True) for item in forward[6:]) + '</div></details>' if len(forward)>6 else ''
        parts.append(f'<section class="entry-section motion-section"><h2>它怎么动</h2><div class="gallery motion-grid">{shown}</div>{more}</section>')
    if reverse:
        links = ''.join(f'<a class="chip" href="{relative(page,entry_destination(item))}">{escape(item["zh"])}</a>' for item in reverse)
        parts.append(f'<section class="entry-section motion-section"><h2>用在哪些组件上</h2><div class="chips">{links}</div></section>')
    return ''.join(parts)


def shell(page, title, body, entries, tax, entry=False):
    columns = {c['slug']: c for c in tax['columns']}
    order = list(tax['anchors'])
    ordered = sorted(entries, key=lambda e: (columns[e['column']]['order'], next(i for i,g in enumerate(columns[e['column']]['groups']) if g['slug'] == e['group']), (order.index(e['id']) if e['id'] in order else len(order))))
    index = [dict(aliases=e.get('aliases', []), zh=e['zh'], en=e['en'], terms=e['terms'], definition=e['definition'], prompt=copy_payload(e),
                  column=columns[e['column']]['name'], group=next(g['name'] for g in columns[e['column']]['groups'] if g['slug'] == e['group']), href=relative(page, entry_destination(e))) for e in ordered]
    data = json.dumps(dict(entries=index, columns=[dict(name=c['name'], href=relative(page, column_destination(c['slug']))) for c in tax['columns']], examples=EXAMPLES), ensure_ascii=False, separators=(',', ':')).replace('<', '\u003c')
    selected = [e for e in entries if entry_destination(e) + 'index.html' == page] if entry else [e for e in entries if page == e['column'] + '/index.html']
    bundle_names = set()
    for item in selected:
        bundle_names.update(demos.bundle_names(item['demo']))
        if item['demo'].get('secondary'):
            bundle_names.update(demos.bundle_names(item['demo']['secondary']))
    if entry and selected:
        for related in mapped_entries(selected[0],entries,tax)[0]:
            bundle_names.update(demos.bundle_names(related['demo']))
    generated = demos.assets(entries)
    def asset_tag(name):
        content = generated[name] if name in generated else (HERE/name).read_text(encoding='utf-8')
        url = relative(page, 'assets/redesign/' + name) + '?v=' + hashlib.sha256(content.encode()).hexdigest()[:8]
        return f'<link rel="stylesheet" href="{url}">' if name.endswith('.css') else f'<script defer src="{url}"></script>'
    css = ''.join(asset_tag(name) for name in ASSETS if name.endswith('.css') and name != 'states.css')
    css += asset_tag('demos.css')
    css += ''.join(asset_tag(name) for name in sorted(bundle_names) if name.endswith('.css'))
    js = ''.join(asset_tag(name) for name in ('demo-runtime.js', *sorted(name for name in bundle_names if name.endswith('.js') and name != 'demo-runtime.js'), 'search.js', 'site.js'))
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="description" content="查看界面效果的中英文名称与演示，复制原始实现提示词。"><title>{escape(title)} · Vibe Design 速查</title><link rel="icon" href="{relative(page, "assets/favicon.svg")}">{css}{js}</head><body{' class="entry-active"' if entry else ''}>{header(page,tax)}<main class="wrap view" id="main" tabindex="-1">{body}</main><footer class="wrap footer">Vibe Design 速查 · <a href="{relative(page,'bench/')}">测评结果</a></footer>
<dialog class="overlay search-dialog" id="search-dialog" aria-label="搜索条目"><div class="search-top"><label class="sr" for="search-input">搜索中文名、英文名或已有词</label><input id="search-input" type="search" placeholder="用你自己的说法搜，比如：鼠标放上去浮起来" autocomplete="off" role="combobox" aria-autocomplete="list" aria-haspopup="grid" aria-expanded="false" aria-describedby="search-help"><button class="close-button" data-close="search-dialog">关闭</button></div><div class="search-body" id="search-body"></div><p class="search-help" id="search-help">↑↓ 选择条目 · Enter 打开 · Tab 选择操作 · Esc 关闭</p></dialog><div class="sr" id="live" role="status" aria-live="polite" aria-atomic="true"></div><script type="application/json" id="redesign-search-index">{data}</script></body></html>'''


def home(entries, tax):
    page = 'index.html'
    descriptions = ['先建立颜色、排版和布局的共同语言。', '认识界面单元，理解用途、状态和实现要求。', '写清操作规则、反馈过程和界面变化。', '把组件和规则组织成完整页面与操作场景。', '把需求交给 AI，用提示词、技能和测评辅助验收。']
    starts = ['g-layout-grid', 'c-button', 'e-view-crossfade', 'g-pages-landing', 'skill-frontend-design']
    layers = []
    for c, description, anchor in zip(tax['columns'], descriptions, starts):
        start = next(e for e in entries if anchor in e['old_anchors'])
        layers.append(f'<article class="layer"><span class="number">{c["order"]:02d}</span><h3><a href="{relative(page,column_destination(c["slug"]))}">{c["name"]}</a></h3><span class="stat">{c["expected"]} 条</span><p>{description}</p><a class="start" href="{relative(page,entry_destination(start))}">推荐起点：{escape(start["zh"])} →</a></article>')
    body = f'''<div class="hero"><h1>看见一个效果，叫出它的名字，拿到能粘进 AI 的提示词。</h1><p class="sub">{len(entries)} 个界面效果，附中英文名称、演示和可直接复制的提示词。</p><button class="home-search" data-search><span class="search-icon" aria-hidden="true"></span><span>用你自己的说法搜，比如：鼠标放上去浮起来</span><kbd>/</kbd></button><div class="chips examples">{query_buttons()}</div></div><h2 class="section-head">从这里开始</h2><div class="layers">{''.join(layers)}</div><section class="method"><h2>怎么用</h2><ol class="steps"><li>找到效果</li><li>看演示</li><li>复制提示词</li><li>粘进 AI 并验收</li></ol></section>'''
    return shell(page, '首页', body, entries, tax)


def demo_scope(demo, page, interactive=False):
    attrs = ' data-interactive' if interactive else ' inert aria-hidden="true"'
    markup = demos.markup({k:v for k,v in demo.items() if k != 'secondary'}, relative(page, "assets/redesign/") + '/', interactive)
    if interactive and page.startswith('components/') and page.split('/')[1] in states.STATES:
        markup = markup.replace('data-demo-template ', f'data-demo-template data-state-css="{relative(page, "assets/redesign/states.css")}" ', 1)
    return f'<div class="demo-scope" data-demo-kind="{demo["kind"]}" data-demo-key="{escape(demo.get("key", ""))}" data-demo-section="{demo.get("section", "")}"{attrs}>{markup}</div>'



def gallery_card(e, page, compact=False):
    target = relative(page, entry_destination(e))
    caption = f'<strong>{escape(e["zh"])}</strong><span class="english">{escape(e["en"])}</span><p>{escape(e["definition"].splitlines()[0])}</p>'
    if compact:
        caption = f'<strong>{escape(e["zh"])}</strong><span class="english">{escape(e["en"])}</span>'
    return f'''<article class="gallery-card" data-demo-key="{e['slug']}"><div class="mini-stage">{demo_scope(e['demo'], page)}<button class="play-button" aria-label="播放{escape(e['zh'])}演示" aria-pressed="false">▶ 播放</button><span class="reduced-link">看演示 →</span></div><a class="gallery-link" href="{target}"><div class="gallery-caption">{caption}</div></a></article>'''


def column_page(slug, entries, tax):
    page = slug + '/index.html'
    column = next(c for c in tax['columns'] if c['slug'] == slug)
    chips = ''.join(f'<a class="chip" href="#group-{g["slug"]}">{g["name"]} {g["expected"]}</a>' for g in column['groups'] if g['expected'])
    sections = []
    order = list(tax['anchors'])
    for g in column['groups']:
        cards = [e for e in entries if e['column'] == slug and e['group'] == g['slug']]
        cards.sort(key=lambda e: order.index(e['id']) if e['id'] in order else len(order))
        content = '<div class="gallery">' + ''.join(gallery_card(e,page) for e in cards) + '</div>' if cards else '<p class="small">三期新增</p>'
        sections.append(f'<section class="group-section" id="group-{g["slug"]}"><h2>{g["name"]} <span class="count">{len(cards)}</span></h2>{content}</section>')
    extra = f'<p class="entry-section"><a href="{relative(page, "bench/")}">测评结果 →</a></p>' if slug == 'ai' else ''
    if slug == 'interactions':
        extra = f'<p class="entry-section"><a href="{relative(page, "interactions/spec/")}">动效实现规范 →</a></p>'
    descriptions = ['先建立颜色、排版和布局的共同语言。', '认识界面里可复用的基本单元，理解用途、状态与实现要求。', '写清操作规则、反馈过程和界面变化。', '把组件和规则组织成完整页面与操作场景。', '把需求交给 AI，用提示词、技能和测评辅助验收。']
    body = f'<nav class="breadcrumbs" aria-label="面包屑"><a href="../">首页</a><span>/</span><span aria-current="page">{column["name"]}</span></nav><div class="row landing-title"><h1>{column["name"]}</h1><span class="title-count">{column["expected"]} 条</span></div><p class="lead">{descriptions[column["order"]-1]}</p><button class="column-search" data-search>搜索条目　⌘K</button><nav class="chips group-tabs" aria-label="栏目分组">{chips}</nav>{"".join(sections)}{extra}'
    return shell(page, column['name'], body, entries, tax)



def copy_button(source, label='复制提示词', primary=False):
    return f'<button class="copy-btn{" btn-primary" if primary else ""}" data-copy-source="{source}">{label}</button>'


def detail(e, entries, tax):
    page = entry_destination(e) + 'index.html'
    column = next(c for c in tax['columns'] if c['slug'] == e['column'])
    group = next(g for g in column['groups'] if g['slug'] == e['group'])
    definition_lines = e['definition'].splitlines()
    points = '<ul class="entry-points">' + ''.join(f'<li>{escape(line)}</li>' for line in definition_lines[1:]) + '</ul>' if len(definition_lines) > 1 else ''
    usage = ''.join(f'<section class="entry-section usage-section"><h2>{label}</h2><p>{escape(e[key])}</p></section>' for key,label in (('when_use','何时用'),('when_avoid','何时不用')) if e.get(key))
    params = e.get('params', [])
    if params:
        usage += '<section class="entry-section usage-section"><h2>关键参数</h2><ul>' + ''.join(f'<li>{escape(item)}</li>' for item in params) + '</ul></section>'
    aliases = '<p class="entry-aliases small">也叫：' + escape('、'.join(e['aliases'][:5])) + '</p>' if e.get('aliases') else ''
    notice = f'<p class="small">共 {len(e["acceptance"])} 条验收要求，见使用卡；复制提示词时自动包含</p>' if e.get('prompt_edit') else ''
    related = ''.join(f'<a class="chip" href="{relative(page,entry_destination(other))}">{escape(other["zh"])}</a>' for other in entries if (other['column'] == e['column'] and other['group'] == e['group'] and other['slug'] != e['slug']) or other['column'] + '/' + other['slug'] in e.get('related', []))
    criteria = ''
    if e['acceptance']:
        items = ''.join(f'<li><p id="criterion-{i}">{escape(text)}</p>{copy_button("criterion-"+str(i), "复制这条")}</li>' for i,text in enumerate(e['acceptance']))
        criteria = f'<details class="criteria" id="acceptance"><summary>验收要求（{len(e["acceptance"])} 条）</summary><ol>{items}</ol></details>'
    bench = f'<a class="bench-badge" href="{relative(page,"bench/"+e["bench"]["slug"]+"/")}">{escape(" · ".join(agent.title() + " " + str(score) for agent,score in e["bench"]["totals"].items()))} · 测评结果 →</a>' if 'bench' in e else ''
    bench_line = f'<p class="bench-line">提示词测评：{bench}</p>' if bench else ''
    prompt_new = ''
    if e.get('prompt_new'):
        prompt_new = f'<details class="entry-section new-section"><summary>新做一个</summary><pre class="prompt-text" id="new-prompt">{escape(e["prompt_new"])}</pre>{copy_button("copy-new-prompt", "复制这一版")}<pre class="sr" id="copy-new-prompt" hidden>{escape(copy_payload(e, "prompt_new"))}</pre></details>'
    use_card = f'<aside class="use-card" aria-labelledby="use-card-title"><h2 id="use-card-title">使用卡</h2>{copy_button("copy-prompt",primary=True)}{criteria}<div class="use-actions">{copy_button("entry-english","复制英文名")}<button class="copy-btn" data-copy-link>复制本页链接</button></div>{bench}</aside>'
    def demonstration(demo):
        controls = '<div class="demo-controls"><button type="button" data-demo-replay>重播</button><button type="button" data-demo-slow aria-pressed="false">慢放 0.25 倍</button><span class="reduced-note" hidden>你的系统开启了减弱动态</span></div>' if demo['kind'] == 'motion' else ''
        return '<div class="entry-demo"><div class="demo-stage">' + demo_scope(demo, page, True) + '</div>' + controls + '</div>'
    demonstrations = demonstration(e['demo'])
    if e.get('demo_hint'):
        demonstrations += f'<p class="small demo-hint">{escape(e["demo_hint"])}</p>'
    if e['column'] == 'components' and e['slug'] in states.STATES:
        demonstrations = demonstrations.replace('<div class="demo-stage">',states.render(e['slug']) + '<div class="demo-stage">',1)
    if e['demo'].get('secondary'):
        demonstrations += demonstration(e['demo']['secondary'])
    secondary = f'<section class="entry-section prompt-box"><h2>提示词 · 第二演示</h2><pre class="prompt-text" id="secondary-prompt">{escape(e["prompt_secondary"])}</pre>{copy_button("secondary-prompt")}</section>' if e.get('prompt_secondary') and not e.get('prompt_edit') else ''
    source_link = ''
    if e['demo']['kind'] == 'skill-reference':
        links = re.findall(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', e['demo']['html'], re.S)
        source_link = '<section class="entry-section"><h2>来源</h2>' + ''.join(f'<p><a href="{escape(url)}" rel="noopener noreferrer">{text}</a></p>' for url,text in links) + '</section>'
    body = f'''<div class="entry-layout"><article class="entry-main"><header class="entry-heading"><nav class="breadcrumbs" aria-label="面包屑"><a href="{relative(page, "")}">首页</a><span>/</span><a href="{relative(page, column_destination(e["column"]))}">{column["name"]}</a><span>/</span><a href="{relative(page, group_destination(e["column"],e["group"]))}">{group["name"]}</a></nav><div class="entry-title"><h1>{escape(e['zh'])}</h1><span class="english" id="entry-english">{escape(e['en'])}</span>{aliases}</div><p class="definition">{escape(definition_lines[0])}</p>{points}</header>{demonstrations}{motion_links(e,page,entries,tax)}{usage}<section class="entry-section prompt-box"><h2>提示词</h2><pre class="prompt-text" id="entry-prompt">{escape(e['prompt'])}</pre>{notice}{prompt_new}</section>{secondary}{source_link}<pre class="sr" id="copy-prompt" hidden>{escape(copy_payload(e))}</pre><section class="entry-section related-section"><h2>相关条目</h2><div class="chips related">{related}</div></section>{bench_line}</article>{use_card}</div><div class="bottom-bar">{'<button data-show-acceptance>验收要求</button>' if e['acceptance'] else ''}{copy_button('copy-prompt',primary=True)}</div>'''
    return shell(page, e['zh']+' '+e['en'], body, entries, tax, entry=True)


def spec_page(entries, tax):
    source = (HERE.parent.parent / '动效速查.html').read_text(encoding='utf-8')
    sys.path.insert(0, str(HERE.parent))
    from entries import Document
    section = next(n for n in Document(source).root.find_all('section') if n.attrs.get('id') == 'section-spec')
    body = '<nav class="breadcrumbs" aria-label="面包屑"><a href="../../">首页</a><span>/</span><a href="../">交互与动效</a></nav><h1>动效实现规范</h1>' + section.inner(source)
    return shell('interactions/spec/index.html', '动效实现规范', body, entries, tax)


def build(output, entries, tax):
    assets = output / 'assets/redesign'
    assets.mkdir(parents=True)
    contents = {name:(HERE/name).read_text(encoding='utf-8') for name in ASSETS}
    contents.update(demos.assets(entries))
    for name, content in contents.items():
        (assets/name).write_text(content, encoding='utf-8')
    pages = {'index.html':home(entries,tax), 'interactions/spec/index.html':spec_page(entries,tax)}
    pages.update({f'{column["slug"]}/index.html':column_page(column['slug'],entries,tax) for column in tax['columns']})
    pages.update({entry_destination(e) + 'index.html':detail(e,entries,tax) for e in entries})
    for name, html in pages.items():
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding='utf-8')
