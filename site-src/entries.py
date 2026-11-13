"""Lossless source adapters with a validated, independent editorial overlay.

UI definitions use the existing .pts bullet text; .where remains when_use.
Unfilled editorial fields remain absent (source acceptance defaults to []).
Motion markup is taken from its normal generator output, verified against JSON
and extra_demos. No generator is imported for its side effects.
"""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import importlib.util
import json
import re

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / 'site-src'
STRICT_CONTENT = True
VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link', 'meta', 'param', 'source', 'track', 'wbr'}


def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class Node:
    def __init__(self, tag='', attrs=None, start=0, inner_start=0):
        self.tag, self.attrs = tag, dict(attrs or [])
        self.start, self.inner_start = start, inner_start
        self.inner_end = self.end = inner_start
        self.children = []

    def find_all(self, tag=None, cls=None):
        found = []
        for child in self.children:
            if isinstance(child, Node):
                if (tag is None or child.tag == tag) and (cls is None or cls in child.attrs.get('class', '').split()):
                    found.append(child)
                found.extend(child.find_all(tag, cls))
        return found

    def one(self, tag=None, cls=None):
        nodes = self.find_all(tag, cls)
        if not nodes:
            raise ValueError(f'Missing source element: {tag} / {cls}')
        return nodes[0]

    def text(self):
        return ''.join(c.text() if isinstance(c, Node) else c for c in self.children)

    def inner(self, source):
        return source[self.inner_start:self.inner_end]

    def outer(self, source):
        return source[self.start:self.end]


class Document(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.source = source
        self.offsets = [0]
        for match in re.finditer('\n', source):
            self.offsets.append(match.end())
        self.root = Node()
        self.stack = [self.root]
        self.feed(source)

    def position(self):
        line, col = self.getpos()
        return self.offsets[line - 1] + col

    def handle_starttag(self, tag, attrs):
        start = self.position()
        node = Node(tag, attrs, start, start + len(self.get_starttag_text()))
        self.stack[-1].children.append(node)
        if tag not in VOID:
            self.stack.append(node)

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        if tag not in VOID:
            node = self.stack.pop()
            node.inner_end = node.end = node.inner_start

    def handle_endtag(self, tag):
        for i in range(len(self.stack) - 1, 0, -1):
            if self.stack[i].tag == tag:
                node = self.stack[i]
                node.inner_end = self.position()
                node.end = self.source.find('>', node.inner_end) + 1
                del self.stack[i:]
                break

    def handle_data(self, data):
        self.stack[-1].children.append(data)


def taxonomy():
    return json.loads((SOURCE / 'taxonomy.json').read_text(encoding='utf-8'))


def source_entries():
    ui = (ROOT / '网页UI元素速查.html').read_text(encoding='utf-8')
    for card in Document(ui).root.find_all('article', 'cmp'):
        yield dict(anchor=card.attrs['id'], zh=card.one('h2').text(), en=card.one(cls='en').text(),
                   terms=card.attrs.get('data-name', ''),
                   definition='\n'.join(n.text() for n in card.one(cls='pts').find_all('li')),
                   demo=dict(kind='ui', html=card.one(cls='canvas').outer(ui)),
                   prompt=card.one(cls='prompt-text').text(), acceptance=[],
                   when_use=card.one(cls='where').text(),
                   source=dict(path='网页UI元素速查.html', old_path='/ui/'))
    motion = (ROOT / '动效速查.html').read_text(encoding='utf-8')
    cards = {n.attrs['id']: n for n in Document(motion).root.find_all('article', 'effect-card')}
    extra = load_module('entry_extra_demos', ROOT / '动效速查-src/extra_demos.py')
    data = json.loads((ROOT / '动效速查-src/motion_entries.json').read_text(encoding='utf-8'))
    for key, group, zh, en, trigger, definition, prompt, *_ in data:
        card = cards['e-' + key]
        if prompt != card.one(cls='prompt-text').text():
            raise ValueError(f'Motion prompt drift: {key}')
        stage = card.one(cls='stage').outer(motion)
        if key.startswith('extra-') and extra.DEMOS[key] not in stage:
            raise ValueError(f'Extra demo drift: {key}')
        yield dict(anchor='e-' + key, zh=zh, en=en, terms=card.attrs.get('data-name', ''),
                   definition=definition, demo=dict(kind='motion', key=key, html=stage),
                   prompt=prompt, acceptance=[], source=dict(path='动效速查-src/motion_entries.json', old_path='/motion/'))
    guide = load_module('entry_guides', SOURCE / 'guide_pages.py')
    for section, data in guide.GUIDES.items():
        for item in guide.all_items(data):
            yield dict(anchor=f'g-{section}-{item["demo"]}', zh=item['title'], en=item['english'],
                       terms=' '.join((item['english'], item['fit'], item['avoid'])),
                       definition=item['description'], demo=dict(kind='guide', section=section, key=item['demo'], html=guide.demo_markup(section, item)),
                       prompt=guide.build_prompt(section, item), acceptance=[item['check']],
                       when_use=item['fit'], when_avoid=item['avoid'], source=dict(path='site-src/guide_pages.py', old_path=f'/{section}/'))
    skills = load_module('entry_skills', SOURCE / 'skill_catalog.py')
    for number, item in enumerate(skills.all_skills(), 1):
        yield dict(anchor='skill-' + item['slug'], zh=item['title'], en=item['slug'],
                   terms=' '.join((item['slug'], item['repo'], item['use'], *item['tags'])),
                   definition=item['summary'], demo=dict(kind='skill-reference', html=skills.render_card(item, number)),
                   prompt=skills.install_prompt(item), acceptance=[], when_use=item['use'],
                   source=dict(path='site-src/skill_catalog.py', old_path='/skills/'))


def load_entries(content=None, *, strict=None):
    tax = taxonomy()
    raw = {item['anchor']: item for item in source_entries()}
    if set(raw) != set(tax['anchors']):
        raise ValueError('Taxonomy must cover exactly every source anchor')
    result = []
    for anchor, item in raw.items():
        if anchor in tax['merges']:
            continue
        entry = {**tax['anchors'][anchor], **{k: v for k, v in item.items() if k != 'anchor'}, 'old_anchors': [anchor]}
        for old, target in tax['merges'].items():
            if target == anchor:
                entry['old_anchors'].append(old)
                entry['demo']['secondary'] = raw[old]['demo']
                entry['prompt_secondary'] = raw[old]['prompt']
                entry['source']['secondary'] = raw[old]['source']
                entry['terms'] += ' ' + raw[old]['terms']
        result.append(entry)
    native = load_module('native_token_entries', SOURCE / 'token_entries.py')
    result.extend(native.entries())
    for entry in result:
        entry.setdefault('id', entry['old_anchors'][0] if entry['old_anchors'] else '')
        entry.setdefault('related', [])
    by_key = {e['column'] + '/' + e['slug']: e for e in result}
    for entry in result:
        for target in entry['related'][:]:
            if target not in by_key:
                raise ValueError(f'Unknown related entry: {target}')
            reverse = by_key[target]['related']
            key = entry['column'] + '/' + entry['slug']
            if key not in reverse:
                reverse.append(key)
    validate(result, tax)
    return apply_content(result, load_content() if content is None else content, strict=strict)


def validate(entries, tax):
    expected = sum(c['expected'] for c in tax['columns'])
    if len(entries) != expected:
        raise ValueError(f'Expected {expected} unified entries')
    if len({e['id'] for e in entries}) != len(entries):
        raise ValueError('Duplicate entry id')
    counts = Counter((e['column'], e['group']) for e in entries)
    keys = [(e['column'], e['slug']) for e in entries]
    if len(set(keys)) != len(keys):
        raise ValueError('Duplicate slug inside a column; specify an override in taxonomy.json')
    for column in tax['columns']:
        if sum(e['column'] == column['slug'] for e in entries) != column['expected']:
            raise ValueError(f'Column count: {column["slug"]}')
        for group in column['groups']:
            if counts[(column['slug'], group['slug'])] != group['expected']:
                raise ValueError(f'Group count: {column["slug"]}/{group["slug"]}')
    for e in entries:
        if not all(e.get(field) for field in ('id', 'slug', 'zh', 'prompt', 'demo')):
            raise ValueError(f'Incomplete entry: {e}')
    frozen = json.loads((ROOT / 'tests/fixtures/old_anchors.json').read_text(encoding='utf-8'))['entries']
    all_anchors = [a for e in entries for a in e['old_anchors']]
    if Counter(all_anchors) != Counter(e['anchor'] for e in frozen):
        raise ValueError('Unified data must account for every frozen destination exactly once')


def write_entries():
    entries = load_entries()
    target = ROOT / 'build/entries.json'
    target.parent.mkdir(exist_ok=True)
    target.write_text(json.dumps(entries, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    return entries


def normalize_alias(text):
    import unicodedata
    return ''.join(unicodedata.normalize('NFKC', text).casefold().split())


def load_content():
    content = {}
    for column in taxonomy()['columns']:
        path = SOURCE / 'content' / (column['slug'] + '.json')
        data = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(data, dict):
            raise ValueError(f'Content must be an object: {path.name}')
        content.update({column['slug'] + '/' + slug: fields for slug, fields in data.items()})
    return content


def apply_content(entries, content, strict=None):
    """Require complete content by default, with explicit opt-out for source fixtures."""
    import copy
    strict = STRICT_CONTENT if strict is None else strict
    by_key = {e['column'] + '/' + e['slug']: e for e in entries}
    unknown = set(content) - set(by_key)
    if unknown:
        raise ValueError(f'Unknown editorial entries: {sorted(unknown)}')
    if strict and set(content) != set(by_key):
        raise ValueError(f'Strict content requires all {len(by_key)} entries; missing: {sorted(set(by_key)-set(content))}')
    aliases_seen = {}
    for key, fields in content.items():
        if not isinstance(fields, dict):
            raise ValueError(f'{key}: content must be an object')
        for field in ('prompt_edit', 'prompt_new', 'when_use', 'when_avoid'):
            if not isinstance(fields.get(field), str) or not fields[field].strip():
                raise ValueError(f'{key}: {field} must be nonempty text')
        aliases = fields.get('aliases')
        if not isinstance(aliases, list) or not 3 <= len(aliases) <= 10 or not all(isinstance(a, str) and a.strip() for a in aliases):
            raise ValueError(f'{key}: aliases must contain 3–10 nonempty strings')
        normalized = [normalize_alias(a) for a in aliases]
        names = [by_key[key]['zh'], by_key[key]['en'], *by_key[key]['en'].split('/')]
        if len(set(normalized)) != len(normalized) or set(normalized) & {normalize_alias(n) for n in names}:
            raise ValueError(f'{key}: duplicate alias or alias equals name')
        for alias in normalized:
            if alias in aliases_seen:
                raise ValueError(f'Alias conflict: {aliases_seen[alias]} and {key}: {alias}')
            aliases_seen[alias] = key
        acceptance = fields.get('acceptance')
        if not isinstance(acceptance, list) or not 3 <= len(acceptance) <= 6 or not all(isinstance(a, str) and a.strip() for a in acceptance):
            raise ValueError(f'{key}: acceptance must contain 3–6 nonempty strings')
        if any(re.search('好看|流畅|合适|自然|友好|美观', a) for a in acceptance):
            raise ValueError(f'{key}: acceptance contains forbidden wording')
        if not isinstance(fields.get('reviewed'), bool):
            raise ValueError(f'{key}: reviewed must be boolean')
        if strict and 'params' not in fields:
            raise ValueError(f'{key}: params must be present, with an empty list when unused')
        if 'params' in fields:
            params = fields['params']
            if not isinstance(params, list) or not all(isinstance(p, str) and p.strip() for p in params):
                raise ValueError(f'{key}: params must be a list of text')
            if strict and params and not 2 <= len(params) <= 4:
                raise ValueError(f'{key}: params must be empty or contain 2–4 items')
    result = copy.deepcopy(entries)
    for entry in result:
        fields = content.get(entry['column'] + '/' + entry['slug'])
        if fields is not None:
            entry['prompt_original'] = entry.get('prompt_original', entry['prompt'])
            entry.update(fields)
            entry['prompt'] = fields['prompt_edit']
    return result
