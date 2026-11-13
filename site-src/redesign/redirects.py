"""Generate client-side redirects from the frozen legacy anchor inventory."""
from html import escape
import json
import posixpath
from pathlib import Path

DEFAULTS = {
    'ui': 'components/', 'motion': 'interactions/', 'layout': 'basics/',
    'visual': 'basics/', 'interaction': 'interactions/',
    'pages': 'scenarios/', 'data': 'components/', 'skills': 'ai/',
}


# Only paths previously published on main receive removal redirects.
REMOVED_BENCH_PAGES = (
    'bench/index.html',
    *(f'bench/{slug}/index.html' for slug in ('button', 'crossfade', 'grid')),
    *(f'bench/demos/round{rnd}/{slug}/{agent}.html'
      for rnd in (1, 2) for slug in ('button', 'crossfade', 'grid')
      for agent in ('codex', 'hermes')),
)


def removed_page(page):
    home = posixpath.relpath('.', posixpath.dirname(page)) + '/'
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>测评结果页面已移除</title><meta http-equiv="refresh" content="0; url={home}"><link rel="canonical" href="{home}"><meta name="robots" content="noindex"></head><body><a href="{home}">本页已移除，返回首页</a></body></html>'''


def tables(entries, tax, adapter):
    fixture = json.loads((Path(__file__).resolve().parents[2]/'tests/fixtures/old_anchors.json').read_text())
    by_anchor = {anchor:entry for entry in entries for anchor in entry['old_anchors']}
    def destination(entry):
        middle = 'skills/' if entry['column']=='ai' else ''
        return f'{entry["column"]}/{middle}{entry["slug"]}/'
    result = {old:{} for old in DEFAULTS}
    for item in fixture['entries']:
        result[item['old_path'].strip('/')][item['anchor']] = '../' + destination(by_anchor[item['anchor']])
    # Auxiliary controls inside an old specimen lead to that specimen's page.
    owners = {}
    for source in adapter.source_entries():
        entry = by_anchor[source['anchor']]
        for node in adapter.Document(source['demo']['html']).root.find_all():
            if node.attrs.get('id'):
                owners[(source['source']['old_path'],node.attrs['id'])] = destination(entry)
    for item in fixture['non_entries']:
        old,anchor = item['old_path'].strip('/'),item['anchor']
        target = owners.get((item['old_path'],anchor),DEFAULTS[old])
        if anchor == 'guide-sections':
            target = {'layout':'basics/#group-layout','visual':'basics/#group-visual','interaction':'interactions/#group-rules','pages':'scenarios/','data':'components/#group-charts'}[old]
        if old=='motion' and anchor.startswith('section-'):
            group = anchor.removeprefix('section-')
            target = 'interactions/spec/' if group=='spec' else 'interactions/#group-'+group
        if old=='motion' and anchor.startswith('spec-'):
            target='interactions/spec/#'+anchor
        # Historical aliases retained by the original visual guide.
        if old=='visual' and anchor.startswith('g-visual-'):
            target='basics/#group-visual'
        result[old][anchor]='../'+target
    return result


def render(old, mapping, tax):
    fallback='../'+DEFAULTS[old]
    column = DEFAULTS[old].split('/')[0]
    name=next(c['name'] for c in tax['columns'] if c['slug']==column)
    data=json.dumps(mapping,ensure_ascii=False,separators=(',',':')).replace('<','\\u003c')
    return f'''<!doctype html><html lang="zh-CN"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>本页已搬到{name}</title><link rel="icon" href="../assets/favicon.svg"><noscript><meta http-equiv="refresh" content="0;url={escape(fallback)}"></noscript></head><body><h1>本页已搬到{name}</h1><p><a href="{escape(fallback)}">前往{name}</a></p><noscript><p>本页已搬到 <a href="{escape(fallback)}">{name}</a></p></noscript><script type="application/json" id="redirect-map">{data}</script><script>(() => {{const mapping=JSON.parse(document.getElementById('redirect-map').textContent);let anchor=location.hash.slice(1);try{{anchor=decodeURIComponent(anchor)}}catch{{}}location.replace(Object.hasOwn(mapping,anchor) ? mapping[anchor] : {json.dumps(fallback)});}})();</script></body></html>'''


def build(output, entries, tax, adapter):
    for old,mapping in tables(entries,tax,adapter).items():
        (output/old/'index.html').write_text(render(old,mapping,tax),encoding='utf-8')
    for page in REMOVED_BENCH_PAGES:
        target = output / page
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(removed_page(page), encoding='utf-8')
