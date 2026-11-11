"""Phase 1, step 5: shared shell and the first five component detail pages."""
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

ASSETS = ('tokens.css', 'base.css', 'site.css', 'site.js', 'search.js', 'demos.css', 'demos.js')
EXAMPLES = ('鼠标放上去浮起来', '弹出来的小黑框', 'Crossfade', '点了会变的按钮')


def first_group(entries):
    return [e for e in entries if e['column'] == 'components' and e['group'] == 'actions']


def generated_pages(entries):
    return ['index.html', 'components/index.html', *(f'components/{e["slug"]}/index.html' for e in first_group(entries))]


def generated_files(entries):
    return generated_pages(entries) + [f'assets/redesign/{name}' for name in ASSETS]


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


def entry_destination(entry):
    if entry['column'] == 'components' and entry['group'] == 'actions':
        return f'components/{entry["slug"]}/'
    return entry['source']['old_path'].strip('/') + '/#' + entry['old_anchors'][0]


def column_destination(column):
    return {'basics':'visual/', 'components':'components/', 'interactions':'interaction/', 'scenarios':'pages/', 'ai':'skills/'}[column]


def group_destination(column, group):
    if column == 'components':
        return 'components/#group-' + group
    if column == 'basics':
        return {'visual':'visual/', 'layout':'layout/'}.get(group)
    if column == 'interactions':
        return 'interaction/' if group == 'rules' else f'motion/#section-{group}'
    return 'pages/' if column == 'scenarios' else 'skills/'


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
            groups.append(f'<div class="menu-group"><a class="menu-group-link" href="{relative(page, "motion/#section-spec")}">动效实现规范 <span class="count">不计条目</span></a></div>')
        if slug == 'ai':
            groups.append(f'<div class="menu-group"><a class="menu-group-link" href="{relative(page, "bench/")}">测评结果</a></div>')
        # No entry lists in either menu. Only the approved component intro.
        first = f'<p class="small menu-intro">先看：<a href="{relative(page, "ui/#c-states")}">组件状态</a></p>' if slug == 'components' else ''
        panels.append(f'<div class="mega" id="mega-{slug}" hidden><div class="wrap mega-inner"><div class="row between mega-heading"><h2>{name}</h2><span class="small">{column["expected"]} 条</span></div>{first}<div class="mega-grid">{"".join(groups)}</div></div></div><!-- mega -->')
        drawers.append(f'<details class="drawer-category"><summary>{number} {name}</summary>{"".join(groups)}</details>')
    return f'''<a class="skip" href="#main">跳到主要内容</a>
<header class="header" id="header"><div class="wrap nav-inner"><a class="brand" href="{relative(page, '')}"><span class="logo" aria-hidden="true"></span>Vibe Design 速查</a><nav class="desktop-nav" aria-label="主导航"><a class="nav-link" href="{relative(page, '')}">首页</a>{''.join(triggers)}</nav><div class="nav-actions"><button class="nav-search" id="nav-search" aria-haspopup="dialog" aria-controls="search-dialog"><span class="desktop-search">搜索 ⌘K</span><span class="mobile-only"><span class="search-icon" aria-hidden="true"></span><span class="sr">搜索</span></span></button><button class="mobile-only menu-button" id="directory-toggle" aria-haspopup="dialog" aria-controls="directory" aria-expanded="false">目录</button></div></div>{''.join(panels)}</header>
<dialog class="overlay drawer" id="directory" aria-labelledby="drawer-title"><div class="drawer-head row between"><h2 id="drawer-title">浏览目录</h2><button class="close-button" data-close="directory" autofocus>关闭</button></div><div class="drawer-body"><p><a href="{relative(page, '')}">首页 →</a></p>{''.join(drawers)}</div></dialog>'''


def shell(page, title, body, entries, tax, entry=False):
    columns = {c['slug']: c for c in tax['columns']}
    index = [dict(zh=e['zh'], en=e['en'], terms=e['terms'], definition=e['definition'], prompt=e['prompt'],
                  column=columns[e['column']]['name'], group=next(g['name'] for g in columns[e['column']]['groups'] if g['slug'] == e['group']), href=relative(page, entry_destination(e))) for e in entries]
    data = json.dumps(dict(entries=index, columns=[dict(name=c['name'], href=relative(page, column_destination(c['slug']))) for c in tax['columns']], examples=EXAMPLES), ensure_ascii=False, separators=(',', ':')).replace('<', '\\u003c')
    css = ''.join(f'<link rel="stylesheet" href="{relative(page, "assets/redesign/" + name)}?v={hashlib.sha256((HERE/name).read_bytes()).hexdigest()[:8]}">' for name in ASSETS if name.endswith('.css') and not name.startswith('demos'))
    # Demo assets are generated from original source, so use a stable source hash.
    demo_hash = hashlib.sha256((HERE.parent.parent / '网页UI元素速查.html').read_bytes() + (HERE/'demos.py').read_bytes()).hexdigest()[:8]
    css += f'<link rel="stylesheet" href="{relative(page, "assets/redesign/demos.css")}?v={demo_hash}">'
    js = ''.join(f'<script defer src="{relative(page, "assets/redesign/" + name)}?v={demo_hash if name == "demos.js" else hashlib.sha256((HERE/name).read_bytes()).hexdigest()[:8]}"></script>' for name in ('demos.js', 'search.js', 'site.js'))
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><meta name="color-scheme" content="light"><meta name="description" content="查看界面效果的中英文名称与演示，复制原始实现提示词。"><title>{escape(title)} · Vibe Design 速查</title>{css}{js}</head><body{' class="entry-active"' if entry else ''}>{header(page,tax)}<main class="wrap view" id="main" tabindex="-1">{body}</main><footer class="wrap footer">Vibe Design 速查 · <a href="{relative(page,'bench/')}">测评结果</a></footer>
<dialog class="overlay search-dialog" id="search-dialog" aria-label="搜索条目"><div class="search-top"><label class="sr" for="search-input">搜索中文名、英文名或别名</label><input id="search-input" type="search" placeholder="搜索名称、英文名或你自己的说法" autocomplete="off" aria-controls="result-list" aria-describedby="search-help"><button class="close-button" data-close="search-dialog">关闭</button></div><div class="search-body" id="search-body"></div><p class="search-help" id="search-help">↑↓ 选择条目 · Enter 打开 · Tab 选择操作 · Esc 关闭</p></dialog><div class="sr" id="live" role="status" aria-live="polite" aria-atomic="true"></div><script type="application/json" id="redesign-search-index">{data}</script></body></html>'''


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


def gallery_card(e, page):
    target = relative(page, entry_destination(e))
    caption = f'<strong>{escape(e["zh"])}</strong><span class="english">{escape(e["en"])}</span><p>{escape(e["definition"].splitlines()[0])}</p>'
    if e['group'] != 'actions':
        return f'<article class="simple-card"><a href="{target}">{caption}</a></article>'
    return f'''<article class="gallery-card" data-demo-key="{e['slug']}"><div class="mini-stage"><div class="demo-scope" inert aria-hidden="true">{e['demo']['html']}</div><button class="play-button" aria-label="播放{escape(e['zh'])}演示" aria-pressed="false">▶ 播放</button><span class="reduced-link">看演示 →</span></div><a class="gallery-link" href="{target}"><div class="gallery-caption">{caption}</div></a></article>'''


def components(entries, tax):
    page = 'components/index.html'
    column = next(c for c in tax['columns'] if c['slug'] == 'components')
    chips = ''.join(f'<a class="chip" href="#group-{g["slug"]}">{g["name"]} {g["expected"]}</a>' for g in column['groups'])
    sections = []
    for g in column['groups']:
        cards = [e for e in entries if e['column'] == 'components' and e['group'] == g['slug']]
        order = list(tax['anchors'])
        cards.sort(key=lambda e: order.index(e['old_anchors'][0]))
        sections.append(f'<section class="group-section" id="group-{g["slug"]}"><h2>{g["name"]} <span class="count">{len(cards)}</span></h2><div class="gallery">{"".join(gallery_card(e,page) for e in cards)}</div></section>')
    body = f'<nav class="breadcrumbs" aria-label="面包屑"><a href="../">首页</a><span>/</span><span aria-current="page">组件</span></nav><div class="row landing-title"><h1>组件</h1><span class="title-count">{column["expected"]} 条</span></div><p class="lead">认识界面里可复用的基本单元，理解用途、状态与实现要求。</p><button class="column-search" data-search>搜索组件或其他条目　⌘K</button><nav class="chips group-tabs" aria-label="组件分组">{chips}</nav>{"".join(sections)}'
    return shell(page, '组件', body, entries, tax)


def copy_button(source, label='复制提示词', primary=False):
    return f'<button class="copy-btn{" btn-primary" if primary else ""}" data-copy-source="{source}">{label}</button>'


def detail(e, entries, tax):
    page = f'components/{e["slug"]}/index.html'
    aliases = [term for term in e['terms'].split() if term.casefold() not in {e['zh'].casefold(), *e['en'].casefold().split()}]
    aliases = list(dict.fromkeys(aliases))
    alias_html = '<div class="chips aliases"><span class="small">也叫：</span>' + ''.join(f'<span class="chip">{escape(a)}</span>' for a in aliases) + '</div>' if aliases else ''
    definition_lines = e['definition'].splitlines()
    points = '<ul class="entry-points">' + ''.join(f'<li>{escape(line)}</li>' for line in definition_lines[1:]) + '</ul>' if len(definition_lines) > 1 else ''
    usage = ''.join(f'<section class="entry-section usage-section"><h2>{label}</h2><p>{escape(e[key])}</p></section>' for key,label in (('when_use','何时用'),('when_avoid','何时不用')) if e.get(key))
    related = ''.join(f'<a class="chip" href="{relative(page,entry_destination(other))}">{escape(other["zh"])}</a>' for other in first_group(entries) if other['slug'] != e['slug'])
    criteria = ''
    if e['acceptance']:
        items = ''.join(f'<li><p id="criterion-{i}">{escape(text)}</p>{copy_button("criterion-"+str(i), "复制这条")}</li>' for i,text in enumerate(e['acceptance']))
        criteria = f'<details class="criteria" id="acceptance"><summary>验收要求（{len(e["acceptance"])} 条）</summary><ol>{items}</ol></details>'
    bench = f'<a class="bench-badge" href="{relative(page,"bench/"+e["bench"]["slug"]+"/")}">查看测评 →</a>' if 'bench' in e else ''
    bench_line = f'<p class="bench-line">提示词测评：{bench}</p>' if bench else ''
    prompt_new = f'<details class="entry-section new-section"><summary>提示词 · 新做一个</summary><pre class="prompt-text" id="new-prompt">{escape(e["prompt_new"])}</pre>{copy_button("new-prompt")}</details>' if e.get('prompt_new') else ''
    use_card = f'<aside class="use-card" aria-labelledby="use-card-title"><h2 id="use-card-title">使用卡</h2>{copy_button("entry-prompt",primary=True)}{criteria}<div class="use-actions">{copy_button("entry-english","复制英文名")}<button class="copy-btn" data-copy-link>复制本页链接</button></div>{bench}</aside>'
    body = f'''<div class="entry-layout"><article class="entry-main"><header class="entry-heading"><nav class="breadcrumbs" aria-label="面包屑"><a href="../../">首页</a><span>/</span><a href="../">组件</a><span>/</span><a href="../#group-actions">按钮与操作</a></nav><div class="entry-title"><h1>{escape(e['zh'])}</h1><span class="english" id="entry-english">{escape(e['en'])}</span></div>{alias_html}<p class="definition">{escape(definition_lines[0])}</p>{points}</header><div class="demo-stage"><div class="demo-scope" data-interactive>{e['demo']['html']}</div></div>{usage}<section class="entry-section prompt-box"><h2>提示词</h2><pre class="prompt-text" id="entry-prompt">{escape(e['prompt'])}</pre></section>{prompt_new}<section class="entry-section related-section"><h2>同组相关条目</h2><div class="chips related">{related}</div></section>{bench_line}</article>{use_card}</div><div class="bottom-bar">{'<button data-show-acceptance>验收要求</button>' if e['acceptance'] else ''}{copy_button('entry-prompt',primary=True)}</div>'''
    return shell(page, e['zh']+' '+e['en'], body, entries, tax, entry=True)


def build(output, entries, tax):
    assets = output / 'assets/redesign'
    assets.mkdir(parents=True)
    ui = (HERE.parent.parent / '网页UI元素速查.html').read_text(encoding='utf-8')
    for name in ASSETS:
        content = demos.css(ui) if name == 'demos.css' else demos.javascript(ui) if name == 'demos.js' else (HERE/name).read_text(encoding='utf-8')
        (assets/name).write_text(content, encoding='utf-8')
    pages = {'index.html':home(entries,tax), 'components/index.html':components(entries,tax)}
    pages.update({f'components/{e["slug"]}/index.html':detail(e,entries,tax) for e in first_group(entries)})
    for name, html in pages.items():
        target = output / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(html, encoding='utf-8')
