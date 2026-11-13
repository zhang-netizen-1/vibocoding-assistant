from functools import lru_cache
from html.parser import HTMLParser
from html import escape, unescape
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import importlib.util
import json
import math
import re
import subprocess
import sys
import unittest
from urllib.parse import unquote, urlsplit


ROOT = Path(__file__).resolve().parent.parent
DIST = ROOT / "dist"
GUIDE_SPEC = importlib.util.spec_from_file_location("guide_pages", ROOT / "site-src" / "guide_pages.py")
GUIDE_MODULE = importlib.util.module_from_spec(GUIDE_SPEC)
GUIDE_SPEC.loader.exec_module(GUIDE_MODULE)
SKILL_SPEC = importlib.util.spec_from_file_location("skill_catalog", ROOT / "site-src" / "skill_catalog.py")
SKILL_MODULE = importlib.util.module_from_spec(SKILL_SPEC)
SKILL_SPEC.loader.exec_module(SKILL_MODULE)


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.links = []
        self.cards = []
        self.references = []
        self.images = []
        self.demo_links = []
        self.commands = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        if attributes.get("data-demo-commands"):
            commands=json.loads(attributes["data-demo-commands"])
            self.commands.extend(commands)
            self.references.extend(command["href"] for command in commands)
        self.references.extend(attributes[key] for key in ("href", "src", "data-demo-css", "data-state-css", "data-spec-css", "data-kind-css", "data-skin-css", "data-a11y-css") if attributes.get(key))
        if tag == "img":
            self.images.append(attributes)
            self.references.extend(candidate.strip().split()[0] for candidate in attributes.get('srcset', '').split(',') if candidate.strip())
        if tag == "a" and "/demos/" in attributes.get("href", ""):
            self.demo_links.append(attributes)
        if attributes.get("id"):
            self.ids.add(attributes["id"])
        if tag == "a" and attributes.get("href"):
            self.links.append(attributes["href"])
        if tag == "article":
            classes = attributes.get("class", "").split()
            if "cmp" in classes or "effect-card" in classes or "guide-card" in classes or "skill-card" in classes:
                self.cards.append(attributes.get("id"))


@lru_cache(maxsize=None)
def parse(path):
    parser = PageParser()
    parser.feed(path.read_text(encoding="utf-8"))
    return parser


class SiteBuildTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, "scripts/build_site.py"], cwd=ROOT, check=True, capture_output=True)

    def test_output_is_explicit_allowlist(self):
        files = {str(path.relative_to(DIST)) for path in DIST.rglob("*") if path.is_file()}
        spec = importlib.util.spec_from_file_location("build_site", ROOT / "scripts/build_site.py")
        builder = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(builder)
        entries = json.loads((ROOT / "build/entries.json").read_text())
        self.assertEqual(files, builder.expected_build_files(entries))
        self.assertEqual(len(builder.REDESIGN.generated_pages(entries)), 10 + len(entries))

    def test_bench_pages_navigation_badges_and_local_references(self):
        paths = [DIST / "bench" / "index.html", *(DIST / "bench" / slug / "index.html" for slug in ("button", "crossfade", "grid"))]
        image_count = 0
        for path in paths:
            self.assertTrue(path.is_file(), path)
            page = path.read_text(encoding="utf-8")
            self.assertNotRegex(page.lower(), "dsh")
            self.assertIn('class="header"',page)
            self.assertNotIn('assets/theme.css',page)
            self.assertNotIn('INTERFACE FIELD GUIDE',page)
            parsed = parse(path)
            self.assertIn("main", parsed.ids)
            for ref in parsed.references:
                url = urlsplit(ref)
                if url.scheme or url.netloc:
                    continue
                target = (path.parent / unquote(url.path)).resolve() if url.path else path
                self.assertTrue(target.is_relative_to(DIST.resolve()), (path, ref))
                if target.is_dir():
                    target /= "index.html"
                self.assertTrue(target.is_file(), (path, ref))
                if url.fragment:
                    target_html=target.read_text()
                    redirects=re.search(r'id="redirect-map">(.*?)</script>',target_html,re.S)
                    destinations=json.loads(redirects[1]) if redirects else parse(target).ids
                    self.assertIn(unquote(url.fragment),destinations,(path,ref))
            for img in parsed.images:
                self.assertTrue(img.get("alt"))
                self.assertEqual(img.get("loading"), "lazy")
            image_count += len(parsed.images)
            if path.parent.name != "bench":
                self.assertEqual(len(parsed.demo_links), 4)
                for link in parsed.demo_links:
                    self.assertEqual(link.get("target"), "_blank")
                    self.assertIn("noopener", link.get("rel", "").split())
        self.assertEqual(image_count, 14)
        self.assertIn('./bench/',parse(DIST/'index.html').links)
        for column,slug,report in (('components','button','button'),('interactions','view-crossfade','crossfade'),('basics','grid','grid')):
            page=DIST/column/slug/'index.html'
            self.assertIn('../../bench/'+report+'/',parse(page).links)

    def test_bench_preserves_source_prompts_evidence_and_totals(self):
        source = ROOT / "site-src" / "bench" / "data"
        overview = (DIST / "bench" / "index.html").read_text(encoding="utf-8")
        narrative = json.loads((source / "narrative.json").read_text(encoding="utf-8"))
        self.assertIn(escape(narrative["time_note"]), overview)
        rounds = [json.loads((source / f"round{rnd}-results.json").read_text(encoding="utf-8")) for rnd in (1, 2)]
        for slug in ("button", "crossfade", "grid"):
            page = (DIST / "bench" / slug / "index.html").read_text(encoding="utf-8")
            destination={"button":"../../components/button/","crossfade":"../../interactions/view-crossfade/","grid":"../../basics/grid/"}[slug]
            self.assertIn(f'href="{destination}">回到条目复制提示词',page)
            entry=narrative["entries"][slug]
            conclusion=entry["stability"]["heading"] if "stability" in entry else entry["fixes"][0]["fixed"]
            self.assertIn(escape(conclusion),page)
            tbody = re.search(r'<tbody>(.*?)</tbody>', page, re.S).group(1)
            score_rows = re.findall(r'<tr>(.*?)</tr>', tbody, re.S)
            self.assertEqual(len(score_rows), 8)
            for number, row in enumerate(score_rows, 1):
                actual = [int(score) for score in re.findall(r'<td>(\d+)</td>', row)]
                expected = [next(item["score"] for item in data["scores"][slug][agent]["items"] if item["item"] == number)
                            for agent in ("codex", "hermes") for data in rounds]
                self.assertEqual(actual, expected, (slug, number))
            totals = re.search(r'<tfoot>(.*?)</tfoot>', page, re.S).group(1)
            self.assertEqual([int(score) for score in re.findall(r'<td>(\d+) /16</td>', totals)],
                             [data["scores"][slug][agent]["total"] for agent in ("codex", "hermes") for data in rounds])
            prompts = re.findall(r'<pre[^>]*>(.*?)</pre>', page, re.S)
            self.assertEqual(len(prompts), 2)
            for rnd, prompt in enumerate(prompts, 1):
                plain = unescape(re.sub(r'<[^>]+>', '', prompt))
                self.assertEqual(plain, (source / f"round{rnd}-{slug}-prompt.txt").read_text(encoding="utf-8"))
            for agent in ("codex", "hermes"):
                first, second = (data["scores"][slug][agent] for data in rounds)
                self.assertIn(f'{first["total"]} → {second["total"]} /16', overview)
                for data in (first, second):
                    for item in data["items"]:
                        self.assertIn(escape(item["evidence"]), page)
            self.assertIn("助手目测判定", page)
            self.assertIn("工具", page)
        time_body = re.findall(r'<tbody>(.*?)</tbody>', overview, re.S)[1]
        time_rows = re.findall(r'<tr>(.*?)</tr>', time_body, re.S)
        self.assertEqual(len(time_rows), 6)
        for row, (slug, agent) in zip(time_rows, ((slug, agent) for slug in ("button", "crossfade", "grid") for agent in ("codex", "hermes"))):
            actual = re.findall(r'<td>(.*?)</td>', row)
            expected = []
            for data in rounds:
                wall_s = Decimal(str(data["agents_runs"][f"{slug}/{agent}"]["wall_s"]))
                minutes, seconds = divmod(int(wall_s.quantize(Decimal("1"), rounding=ROUND_HALF_UP)), 60)
                expected.append(f"{minutes} 分 {seconds} 秒")
            self.assertEqual(actual, expected)

    def test_bench_assets_are_copied_without_changes(self):
        source = ROOT / "site-src" / "bench"
        for path in (source / "img").glob("*.jpg"):
            self.assertEqual(path.read_bytes(), (DIST / "bench" / "assets" / "img" / path.name).read_bytes())
        for path in (source / "demos").rglob("*.html"):
            self.assertEqual(path.read_bytes(), (DIST / "bench" / path.relative_to(source)).read_bytes())

    def test_site_routes_and_all_cards(self):
        home=parse(DIST/'index.html')
        entries=json.loads((ROOT/'build/entries.json').read_text())
        self.assertIn(f'{len(entries)} 个界面效果',(DIST/'index.html').read_text())
        for column in ('basics','components','interactions','scenarios','ai'):
            self.assertIn('./'+column+'/',home.links)
        self.assertEqual((DIST/'index.html').read_text().count('<article class="layer"'),5)
        frozen=json.loads((ROOT/'tests/fixtures/old_anchors.json').read_text())
        for section,original,prefix,expected in (('ui','网页UI元素速查.html','c-',70),('motion','动效速查.html','e-',79)):
            # Source cardinality remains frozen while public routes redirect.
            cards=parse(ROOT/original).cards
            self.assertEqual(len(cards),expected)
            self.assertEqual(len(set(cards)),expected)
            self.assertTrue(all(card.startswith(prefix) for card in cards))
            self.assertEqual(len([e for e in frozen['entries'] if e['old_path']==f'/{section}/']),expected)
        for section in ('layout','visual','interaction','pages','data'):
            self.assertEqual(len([e for e in frozen['entries'] if e['old_path']==f'/{section}/']),6)
        self.assertEqual(len([e for e in frozen['entries'] if e['old_path']=='/skills/']),10)

    def test_site_scripts_and_metadata(self):
        home=(DIST/'index.html').read_text()
        self.assertRegex(home,r'src="\./assets/redesign/site\.js\?v=[0-9a-f]{8}"')
        self.assertRegex(home,r'href="\./assets/redesign/tokens\.css\?v=[0-9a-f]{8}"')
        for section in ('ui','motion','layout','visual','interaction','pages','data','skills'):
            page=(DIST/section/'index.html').read_text()
            self.assertIn('<noscript>',page)
            self.assertIn('http-equiv="refresh"',page)
            self.assertIn('location.replace(',page)
            self.assertIn('decodeURIComponent(anchor)',page)
            self.assertNotIn('site-reference-workspace',page)
            self.assertNotIn('assets/theme.css',page)
            self.assertIn('rel="icon"',page)

    def test_global_search_index_matches_real_anchors(self):
        home = (DIST / "index.html").read_text(encoding="utf-8")
        self.assertNotIn('redesign-search-index', home)
        entries = json.loads((DIST / 'assets/search-index.json').read_text())["entries"]
        unified = json.loads((ROOT / "build/entries.json").read_text())
        self.assertEqual(len(entries), len(unified))
        self.assertEqual(len({entry["href"] for entry in entries}), len(unified))
        counts = {category: sum(entry["column"] == category for entry in entries) for category in {entry["column"] for entry in entries}}
        self.assertEqual(counts, {"设计基础": 17, "组件": 75, "交互与动效": 84, "页面与场景": 6, "AI 实现": 10})
        for entry in entries:
            url = urlsplit(entry["href"])
            target = DIST / unquote(url.path)
            if target.is_dir():
                target /= "index.html"
            self.assertTrue(target.is_file(), entry["href"])
            if url.fragment:
                self.assertIn(url.fragment, parse(target).ids, entry["href"])
            self.assertTrue(entry["zh"])
        for row in entries:
            target = DIST / unquote(urlsplit(row['href']).path) / 'index.html'
            payload = re.search(r'<pre class="sr" id="copy-prompt" hidden>(.*?)</pre>', target.read_text(), re.S)
            self.assertEqual(row['prompt'], unescape(payload[1]))
        self.assertEqual(list(dict.fromkeys(e['column'] for e in entries)), ['设计基础','组件','交互与动效','页面与场景','AI 实现'])

    def test_redesign_all_entries_and_local_routes(self):
        spec = importlib.util.spec_from_file_location('templates_test', ROOT/'site-src/redesign/templates.py')
        templates = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(templates)
        entries = json.loads((ROOT/'build/entries.json').read_text())
        for name in templates.generated_pages(entries):
            path = DIST/name
            self.assertTrue(path.is_file(), name)
            html = path.read_text()
            self.assertIn('Vibe Design 速查', html)
            self.assertIn('rel="icon"', html)
            self.assertNotIn('189', html)
            self.assertNotIn('INTERFACE FIELD GUIDE', html)
            parsed = parse(path)
            for ref in parsed.references:
                url = urlsplit(ref)
                if name == '404.html' and not ref.startswith('#'):
                    self.assertTrue(ref.startswith('/vibocoding-assistant/'), (name,ref))
                else:
                    self.assertFalse(ref.startswith('/'), (name,ref))
                if url.scheme or url.netloc:
                    # Existing skill source links are outbound anchors, never fetched resources.
                    self.assertEqual(url.netloc, 'github.com', (name,ref))
                    self.assertIn('ai/skills/', name)
                    continue
                if name == '404.html' and url.path:
                    target = (DIST/unquote(url.path).removeprefix('/vibocoding-assistant/')).resolve()
                else:
                    target = (path.parent/unquote(url.path)).resolve() if url.path else path
                self.assertTrue(target.is_relative_to(DIST.resolve()), (name,ref))
                if target.is_dir(): target /= 'index.html'
                self.assertTrue(target.is_file(), (name,ref))
                if url.fragment: self.assertIn(unquote(url.fragment),parse(target).ids,(name,ref))
            self.assertNotRegex(html, r'<(?:script|link|img)[^>]+(?:src|href)="https?://')
        for entry in entries:
            path = DIST/templates.entry_destination(entry)/'index.html'
            page = path.read_text()
            card = re.search(r'<aside class="use-card prompt-card".*?</aside>', page, re.S)[0]
            self.assertNotIn('entry-section prompt-box', page)
            self.assertEqual(page.count('id="entry-prompt"'), 1)
            prompt = re.search(r'<pre class="prompt-text" id="entry-prompt">(.*?)</pre>',card,re.S)
            self.assertEqual(unescape(prompt[1]),entry['prompt'])
            self.assertIn('data-copy-source="copy-prompt">复制</button>', card)
            self.assertEqual('复制时自动附带' in card, bool(entry['acceptance']))
            if entry['acceptance']:
                self.assertIn(f'复制时自动附带 {len(entry["acceptance"])} 条验收要求', card)
            payload = re.search(r'<pre class="sr" id="copy-prompt" hidden>(.*?)</pre>',page,re.S)
            self.assertEqual(unescape(payload[1]),templates.copy_payload(entry))
            self.assertIn('data-copy-source="copy-prompt"',page)
            for criterion in entry['acceptance']:
                self.assertIn(escape(criterion),page)
                self.assertIn(criterion,unescape(payload[1]))
            self.assertEqual('id="acceptance"' in page,bool(entry['acceptance']))
            if entry.get('prompt_secondary'):
                if not entry.get('prompt_edit'):
                    self.assertIn(escape(entry['prompt_secondary']),page)
                self.assertEqual(page.count(' data-interactive'),2)

    def test_all_column_galleries_and_source_markup(self):
        spec = importlib.util.spec_from_file_location('entry_adapter_test',ROOT/'site-src/entries.py')
        adapter=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        entries=adapter.load_entries()
        for column in adapter.taxonomy()['columns']:
            html=(DIST/column['slug']/'index.html').read_text()
            doc=adapter.Document(html).root
            cards=doc.find_all('article','gallery-card')
            self.assertEqual(len(cards),column['expected'])
            self.assertEqual(doc.find_all('article','simple-card'),[])
            self.assertEqual(doc.find_all(cls='prompt-text'),[])
            self.assertIn('提示词写法', html)
            for group in column['groups']:
                self.assertIn('id="group-'+group['slug']+'"',html)
        command_page=parse(DIST/'components/cmdk/index.html')
        self.assertEqual(len(command_page.commands),70)
        self.assertEqual(len({item['href'] for item in command_page.commands}),70)
        for entry in entries:
            middle='skills/' if entry['column']=='ai' else ''
            path=DIST/entry['column']/middle/entry['slug']/'index.html'
            html=path.read_text()
            doc=adapter.Document(html).root
            self.assertEqual(doc.one(cls='definition').text(),entry['definition'].splitlines()[0])
            points=doc.find_all(cls='entry-points')
            self.assertEqual([n.text() for n in points[0].find_all('li')] if points else [],entry['definition'].splitlines()[1:])
            dialog=next(n for n in doc.find_all('dialog') if n.attrs.get('id')=='search-dialog')
            index_path=(path.parent/urlsplit(dialog.attrs['data-index-url']).path).resolve()
            index=json.loads(index_path.read_text())
            self.assertEqual(len(index['entries']),192)
            for item in [*index['entries'],*index['columns']]:
                href=dialog.attrs['data-site-root']+item['href'][2:]
                target=(path.parent/urlsplit(href).path).resolve()
                self.assertFalse(item['href'].startswith('/'))
                if target.is_dir():target/='index.html'
                self.assertTrue(target.is_file(),(path,item['href']))

    def test_bench_new_shell_backlinks_and_pruned_assets(self):
        entries=json.loads((ROOT/'build/entries.json').read_text())
        scores=json.loads((ROOT/'site-src/bench/data/round2-results.json').read_text())['scores']
        for entry in entries:
            if 'bench' not in entry:continue
            slug=entry['bench']['slug']
            middle='skills/' if entry['column']=='ai' else ''
            page=DIST/entry['column']/middle/entry['slug']/'index.html'
            detail=(DIST/'bench'/slug/'index.html').read_text()
            self.assertIn('回到条目复制提示词',detail)
            self.assertIn('../../'+entry['column']+'/'+entry['slug']+'/',parse(DIST/'bench'/slug/'index.html').links)
            self.assertIn('../../bench/'+slug+'/',parse(page).links)
            self.assertEqual(entry['bench']['totals'],{agent:scores[slug][agent]['total'] for agent in ('codex','hermes')})
            for agent,score in entry['bench']['totals'].items():
                self.assertIn(agent.title()+' '+str(score),page.read_text())
        for page in (DIST/'bench').glob('*/index.html'):
            html=page.read_text()
            self.assertNotRegex(html,r'assets/(?:theme|site|guides)\.(?:css|js)')
            self.assertIn('assets/redesign/tokens.css',html)
            self.assertIn('id="search-dialog"',html)
        for name in ('theme.css','site.css','site.js','home.css','home.js','guides.css','guides.js','visual-styles.css','skills.css','skills.js'):
            self.assertFalse((DIST/'assets'/name).exists(),name)
            self.assertTrue((ROOT/'site-src'/name).is_file(),name)

    def test_component_motion_mapping_links_both_directions(self):
        spec=importlib.util.spec_from_file_location('mapping_templates',ROOT/'site-src/redesign/templates.py')
        templates=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(templates)
        entries=json.loads((ROOT/'build/entries.json').read_text())
        taxonomy=json.loads((ROOT/'site-src/taxonomy.json').read_text())
        by_anchor={anchor:entry for entry in entries for anchor in entry['old_anchors']}
        for pair in taxonomy['component_motion']:
            component,motion=(by_anchor[pair[key]] for key in ('component','motion'))
            for source,target,heading in ((component,motion,'它怎么动'),(motion,component,'用在哪些组件上')):
                page=templates.entry_destination(source)+'index.html'
                html=(DIST/page).read_text()
                self.assertIn(heading,html)
                href=templates.relative(page,templates.entry_destination(target))
                self.assertIn(href,parse(DIST/page).links)
                self.assertTrue((DIST/templates.entry_destination(target)/'index.html').is_file())
            self.assertIn('demo-motion.js',(DIST/templates.entry_destination(component)/'index.html').read_text())

    def test_ten_state_switchers_have_matching_captions_and_styles(self):
        spec=importlib.util.spec_from_file_location('states_test',ROOT/'site-src/redesign/states.py')
        states=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(states)
        self.assertEqual(len(states.STATES),10)
        css=(ROOT/'site-src/redesign/states.css').read_text()
        for slug,options in states.STATES.items():
            page=(DIST/'components'/slug/'index.html').read_text()
            self.assertEqual(page.count('class="state-picker"'),1,slug)
            self.assertIn('role="group" aria-labelledby="state-title"',page)
            self.assertIn('data-state-css="../../assets/redesign/states.css"',page)
            for key,label,description in options:
                self.assertIn(f'data-state="{key}" data-state-class="force-{key}"',page)
                self.assertIn(f'id="state-description-{key}"',page)
                self.assertIn(escape(description),page)
                self.assertIn(f':host(.force-{key})',css)
        for page in (DIST/'components').glob('*/index.html'):
            self.assertEqual('class="state-picker"' in page.read_text(),page.parent.name in states.STATES)

    def test_old_addresses_redirect_all_frozen_entries_and_auxiliary_anchors(self):
        frozen=json.loads((ROOT/'tests/fixtures/old_anchors.json').read_text())
        mappings={}
        for old in ('ui','motion','layout','visual','interaction','pages','data','skills'):
            html=(DIST/old/'index.html').read_text()
            mappings[old]=json.loads(re.search(r'id="redirect-map">(.*?)</script>',html,re.S)[1])
        for item in frozen['entries']+frozen['non_entries']:
            old=item['old_path'].strip('/')
            self.assertIn(item['anchor'],mappings[old],item)
            href=mappings[old][item['anchor']]
            self.assertFalse(href.startswith('/'))
            url=urlsplit(href)
            target=(DIST/old/url.path).resolve()
            if target.is_dir():target/='index.html'
            self.assertTrue(target.is_file(),(item,href))
            if url.fragment:self.assertIn(url.fragment,parse(target).ids,(item,href))
        self.assertEqual(mappings['motion']['e-extra-submit-flow'],'../interactions/submit/')
        self.assertEqual(mappings['interaction']['g-interaction-submit'],'../interactions/submit/')
        self.assertEqual(mappings['motion']['e-extra-delete-undo'],'../interactions/undo/')
        self.assertEqual(mappings['interaction']['g-interaction-undo'],'../interactions/undo/')
        for name in ('motion-demo-gallery.html','motion-demo-detail.html'):
            self.assertEqual((DIST/'motion'/name).read_bytes(),(ROOT/name).read_bytes())

    def test_guide_prompts_are_actionable_and_unique(self):
        prompts = {}
        for section, guide in GUIDE_MODULE.GUIDES.items():
            page = (DIST / section / "index.html").read_text(encoding="utf-8")
            self.assertIn('id="redirect-map"',page)
            self.assertEqual(len(GUIDE_MODULE.all_items(guide)),6)
            self.assertNotIn('data-copy=', page)
            for entry in GUIDE_MODULE.all_items(guide):
                prompt = GUIDE_MODULE.build_prompt(section, entry)
                self.assertIn('请在当前代码仓库中直接实现', prompt)
                self.assertIn('实施要求：', prompt)
                self.assertIn('边界与验收：', prompt)
                self.assertIn('运行项目现有构建或相关测试', prompt)
                self.assertIn(entry['check'], prompt)
                self.assertGreaterEqual(len(GUIDE_MODULE.PROMPT_STEPS[section][entry['demo']]), 2)
                self.assertNotIn('适合' + entry['fit'], prompt)
                prompts[(section, entry['demo'])] = prompt
        self.assertEqual(len(prompts), 30)
        self.assertEqual(len(set(prompts.values())), 30)
        self.assertIn('#FAF9F4', prompts[('visual', 'minimal')])
        self.assertIn('backdrop-filter', prompts[('visual', 'glass')])
        self.assertIn('aria-describedby', prompts[('interaction', 'validation')])

    def test_skill_catalog_sources_and_install_prompts(self):
        entries = SKILL_MODULE.all_skills()
        self.assertEqual(len(entries), 10)
        self.assertEqual(len({entry["slug"] for entry in entries}), 10)
        page = ''.join(path.read_text() for path in (DIST/'ai/skills').glob('*/index.html'))
        self.assertEqual(page.count('id="entry-prompt"'),10)
        self.assertEqual(page.count('data-copy-source="copy-prompt"'),20)
        for entry in entries:
            source = f'https://github.com/{entry["repo"]}/blob/main/{entry["path"]}/SKILL.md'
            self.assertIn(source, page)
            prompt = SKILL_MODULE.install_prompt(entry)
            self.assertIn(f'「{entry["slug"]}」Skill', prompt)
            self.assertIn(f'{entry["repo"]}/tree/main/{entry["path"]}', prompt)
            self.assertIn(f'~/.codex/skills/{entry["slug"]}/', prompt)
            if entry['path'].rsplit('/', 1)[-1] != entry['slug']:
                self.assertIn(f'--name {entry["slug"]}', prompt)
            self.assertIn('不要安装整个仓库', prompt)
            self.assertIn('安装后检查 SKILL.md', prompt)


if __name__ == "__main__":
    unittest.main()

class DemoSpecBuildTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import sys
        sys.path.insert(0, str(ROOT/'site-src'))
        import entries
        spec=importlib.util.spec_from_file_location('demo_spec_contracts',ROOT/'site-src/redesign/demos.py')
        cls.demos=importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.demos)
        cls.entries=entries.load_entries()
        cls.Document=entries.Document

    def test_all_194_demos_receive_public_spec_and_keep_source_identity(self):
        total=0
        for entry in self.entries:
            demos=[entry['demo']]+([entry['demo']['secondary']] if entry['demo'].get('secondary') else [])
            for demo in demos:
                html=self.demos.markup(demo,'../../assets/redesign/',True,entry['slug'])
                tree=self.Document(html).root
                template=tree.one('template')
                article=tree.one('article')
                self.assertIn('ds-stage',article.attrs['class'].split())
                self.assertEqual(template.attrs['data-spec-css'],'../../assets/redesign/demo-spec.css')
                self.assertEqual(template.attrs['data-a11y-css'],'../../assets/redesign/demo-accessibility.css')
                anchor=self.demos._source_anchor(demo)
                if anchor:self.assertEqual(article.attrs['id'],anchor)
                total+=1
        self.assertEqual(total,194)

    def test_ten_skin_contracts_and_relative_image_urls_at_every_depth(self):
        for slug in ['button','input','component-lift','view-crossfade','modal','tooltip','scroll-reveal','grid','skeleton','carousel']:
            entry=next(e for e in self.entries if e['slug']==slug)
            for prefix in ['./assets/redesign/','../assets/redesign/','../../assets/redesign/','../../../assets/redesign/']:
                html=self.demos.markup(entry['demo'],prefix,True,slug)
                root=self.Document(html).root
                template=root.one('template')
                self.assertEqual(template.attrs['data-skin-css'],prefix+'demo-skins/'+entry['demo']['kind']+'-'+slug+'.css')
                self.assertNotIn('{{demo-assets}}',html)
                for image in root.find_all('img'):
                    import posixpath
                    expected=posixpath.normpath(prefix+'../../demo-assets')+'/'
                    self.assertTrue(image.attrs['src'].startswith(expected))
                    self.assertIn('640w',image.attrs['srcset'])
                    self.assertIn('1280w',image.attrs['srcset'])
                    for candidate in image.attrs['srcset'].split(','):
                        self.assertTrue(candidate.strip().startswith(expected))
            source=self.Document(self.demos.markup(entry['demo'],'./',True,slug)).root
            if slug=='button':
                buttons=source.find_all('button',cls='btn')
                self.assertEqual(len(buttons),4)
                self.assertEqual([b.attrs.get('data-arg') for b in buttons[:3]],['点击了主要按钮','这是次要按钮','确认删除？'])
                self.assertEqual(buttons[3].attrs['id'],'copyDemoBtn')
            elif slug=='input':
                self.assertEqual([n.attrs['aria-label'] for n in source.find_all('input')],['姓名','邮箱'])
                floating=source.one(cls='floatfield')
                nodes=[n for n in floating.children if hasattr(n,'tag')]
                self.assertEqual([n.tag for n in nodes],['input','span'])
                self.assertEqual(nodes[0].attrs['placeholder'],' ')
                self.assertIn('fflabel',nodes[1].attrs['class'])
            elif slug=='component-lift':
                self.assertEqual(source.one(cls='stage').attrs['data-effect'],slug)
                self.assertEqual(source.one(cls='lift-card').tag,'button')
                self.assertEqual(len(source.find_all('img')),1)
            elif slug=='view-crossfade':
                stack=source.one(cls='scene-stack')
                self.assertEqual(len(stack.find_all(cls='mini-view')),2)
                self.assertEqual(len(stack.find_all('img')),2)
                self.assertEqual(source.one('button').attrs['data-action'],'next')

    def test_batch_b_original_hooks_and_real_content(self):
        roots={}
        for slug in ['modal','tooltip','scroll-reveal','grid','skeleton','carousel']:
            entry=next(e for e in self.entries if e['slug']==slug)
            html=self.demos.markup(entry['demo'],'../../assets/redesign/',True,slug)
            roots[slug]=self.Document(html).root
            self.assertEqual(html.count('ds-hint-icon'),1,slug)
            self.assertIn('data-ds-sample',html)
        modal=roots['modal']
        self.assertEqual(modal.one(cls='modal-mask').attrs['id'],'modal')
        dialog=modal.one(cls='modal-box')
        self.assertEqual(dialog.attrs['role'],'dialog')
        self.assertEqual(dialog.attrs['aria-labelledby'],'modal-title')
        self.assertEqual([n.attrs['data-cmd'] for n in modal.find_all('button')],['openModal','closeModal','closeModal'])
        tooltip=roots['tooltip']
        self.assertEqual(tooltip.one(cls='bubble').attrs['role'],'tooltip')
        self.assertEqual(tooltip.one('button').attrs['aria-describedby'],'share-tooltip')
        self.assertEqual(tooltip.one('button').attrs['aria-label'],'分享')
        scroll=roots['scroll-reveal']
        self.assertEqual(scroll.one(cls='stage').attrs['data-effect'],'scroll-reveal')
        self.assertEqual(len(scroll.find_all(cls='reveal-target')),3)
        self.assertEqual(len(scroll.find_all('img')),3)
        self.assertIsNotNone(scroll.one(cls='scroll-meter'))
        grid=roots['grid']
        self.assertEqual(grid.one(cls='guide-card-stage').attrs['data-demo'],'grid')
        self.assertEqual(len(grid.find_all(cls='ds-grid-card')),6)
        self.assertEqual(len(grid.find_all('img')),6)
        self.assertEqual([n.attrs['data-guide-mode'] for n in grid.find_all('button')],['0','1'])
        skeleton=roots['skeleton']
        self.assertEqual(skeleton.one(cls='skeleton').attrs['aria-busy'],'true')
        self.assertEqual(len(skeleton.find_all(cls='sk')),4)
        self.assertEqual(len(skeleton.find_all('img')),1)
        self.assertEqual(skeleton.one(cls='ds-skeleton-content').attrs['aria-hidden'],'true')
        carousel=roots['carousel']
        ids={n.attrs.get('id') for n in carousel.find_all()}
        self.assertTrue({'carTrack','carPrev','carNext','carDots','carPause'}<=ids)
        self.assertEqual(len(carousel.find_all(cls='car-slide')),3)
        self.assertEqual([n.attrs['aria-current'] for n in carousel.one(cls='car-dots').find_all('button')],['true','false','false'])
        for index,image in enumerate(carousel.find_all('img'),1):
            self.assertIn(f'garden-dusk-0{index}',image.attrs['src'])

    def test_manifest_images_are_byte_identical_and_have_declared_sizes(self):
        manifest=json.loads((ROOT/'site-src/demo-assets/manifest.json').read_text())
        for image in manifest['images']:
            for width,name in image['files'].items():
                raw=(ROOT/'site-src/demo-assets'/name).read_bytes()
                self.assertEqual(raw,(DIST/'demo-assets'/name).read_bytes())
                self.assertEqual(raw[:4],b'RIFF')
                self.assertEqual(raw[8:12],b'WEBP')
                if raw[12:16]==b'VP8X':
                    actual=(int.from_bytes(raw[24:27],'little')+1,int.from_bytes(raw[27:30],'little')+1)
                elif raw[12:16]==b'VP8 ':
                    self.assertEqual(raw[23:26],b'\x9d\x01\x2a')
                    actual=(int.from_bytes(raw[26:28],'little') & 0x3fff,int.from_bytes(raw[28:30],'little') & 0x3fff)
                else:
                    self.fail(f'Unverified WebP encoding: {name}')
                self.assertEqual(actual[0],int(width))
                expected=round(image['height']*int(width)/image['width'])
                self.assertLessEqual(abs(actual[1]-expected),1)

    def test_public_sheets_are_not_embedded_in_kind_styles(self):
        assets=self.demos.assets(self.entries)
        for kind in self.demos.KINDS:
            self.assertNotIn('Opaque backing preserves hint contrast',assets['demo-'+kind+'.css'])
            self.assertNotIn('--ds-dur-scene:',assets['demo-'+kind+'.css'])
        runtime=assets['demo-runtime.js']
        positions=[runtime.index("['"+key+"', template.dataset.") for key in ['demo','spec','kind','skin','a11y','state']]
        self.assertEqual(positions,sorted(positions))
        for name in ['demo-spec.css','demo-accessibility.css']:
            self.assertIn(name,assets)

    def test_reduced_motion_gate_is_idempotent_and_preserves_function_selectors(self):
        gate=':host(:not([data-demo-motion-once]):not([data-demo-motion-step]))'
        original='@media(prefers-reduced-motion:reduce){'+gate+' .lift-card{transform:none}.ds-stage :is(button,[role=button]):active{transform:none}}'
        result=self.demos._gate_reduced_motion(original)
        self.assertNotIn(gate+' '+gate,result)
        self.assertIn('.ds-stage :is(button,[role=button]):active{',result)
        self.assertEqual(result,self.demos._gate_reduced_motion(result))

    def test_closed_drawer_is_contained_without_clipping_demo_content(self):
        entry=next(e for e in self.entries if e['column']=='components' and e['slug']=='drawer')
        markup=self.demos.markup(entry['demo'],'../../assets/redesign/',True,entry['slug'])
        root=self.Document(markup).root
        overlay=root.one(cls='ds-overlays')
        nodes=[n for n in overlay.children if hasattr(n,'tag')]
        self.assertEqual([node.attrs['id'] for node in nodes],['dmask','dpanel'])
        self.assertIn('overflow:clip',(ROOT/'site-src/redesign/demo-spec.css').read_text().split('.ds-stage > .ds-overlays')[1].split('}')[0])


class BatchCKindSkinTest(unittest.TestCase):
    setUpClass = classmethod(DemoSpecBuildTest.setUpClass.__func__)
    def test_color_slug_is_resolved_by_kind_and_contracts_survive(self):
        for kind in ('ui','token'):
            entry=next(e for e in self.entries if e['slug']=='color' and e['demo']['kind']==kind)
            html=self.demos.markup(entry['demo'],'../../assets/redesign/',True,'color')
            self.assertIn('demo-skins/'+kind+'-color.css',html)
            self.assertNotIn('data-kind-css',html)
            root=self.Document(html).root
            if kind=='ui':
                self.assertEqual(root.one('input').attrs['type'],'color')
                self.assertEqual(root.one('input').attrs['aria-label'],'选择颜色')
                self.assertEqual(root.one('span',cls='ctl').attrs['class'],'ctl ds-hint')
                self.assertIn('id="hexc"',html)
            else:
                self.assertEqual([n.attrs['data-token-control'] for n in root.find_all('input')],['foreground','background'])
                self.assertIn('data-token-sample',html)
                self.assertIn('data-token-output',html)

    def test_dashboard_and_skill_keep_source_contracts(self):
        for slug in ('dashboard','frontend-design'):
            entry=next(e for e in self.entries if e['slug']==slug)
            html=self.demos.markup(entry['demo'],'../../assets/redesign/',True,slug)
            self.assertIn('data-ds-sample',html)
            root=self.Document(html).root
            if slug=='dashboard':
                self.assertEqual(root.one(cls='guide-card-stage').attrs['data-demo'],'dashboard')
                self.assertEqual(len(root.find_all('i')),7)
                self.assertIn('1,280',html)
                self.assertIn('24%',html)
                self.assertEqual([n.attrs['data-guide-mode'] for n in root.find_all('button')],['0','1'])
            else:
                self.assertEqual(root.one(cls='skill-summary').text(),self.Document(entry['demo']['html']).root.one(cls='skill-summary').text())
                self.assertEqual(len(root.find_all('dt')),2)
                self.assertEqual(len(root.one(cls='skill-tags').find_all('span')),2)

    def test_kind_skin_coverage_and_special_style_exclusions(self):
        assets=self.demos.assets(self.entries)
        for kind in ('ui','motion'):
            name='demo-skins/_kind-'+kind+'.css'
            self.assertIn(':not(.ds-hint)',assets[name])
            self.assertIn('var(--ds-surface)',assets[name])
            self.assertGreater(len(assets[name].splitlines()),10)
            self.assertEqual((DIST/'assets/redesign'/name).read_text(),assets[name])
        counts={kind:0 for kind in self.demos.KINDS}
        samples=skips=0
        sample_slugs = set()
        for entry in self.entries:
            kind=entry['demo']['kind']
            html=self.demos.markup(entry['demo'],'../../assets/redesign/',True,entry['slug'])
            if 'data-kind-css=' in html:
                counts[kind]+=1
                self.assertIn('data-ds-kind="'+kind+'"',html)
                self.assertIn('demo-skins/_kind-'+kind+'.css',html)
                self.assertNotIn('data-ds-sample',html)
            elif 'data-ds-sample' in html:
                samples+=1
                sample_slugs.add(entry['slug'])
            else:
                skips+=1
                self.assertIn(entry['slug'],self.demos.KIND_SKIN_SKIPS.get(kind,()))
        # I1–I4 gave every entry its own sample skin; only the six visual styles keep their own CSS.
        self.assertEqual(counts,{'ui':0,'motion':0,'guide':0,'token':0,'skill-reference':0})
        self.assertEqual(samples,186)
        for slug in ('sidebar', 'list', 'settings', 'baseline-ui', 'wizard', 'detail', 'dark-mode',
                     'typography', 'mobile-pull', 'media-compare', 'background-aurora', 'view-stagger'):
            self.assertIn(slug, sample_slugs)
        for slug in ('advanced-settings', 'conditional-step', 'context-options', 'infinite-scroll',
                     'inline-edit', 'progress', 'table-reorder', 'textarea', 'virtual-list',
                     'auto-save', 'bar', 'donut', 'heatmap', 'line', 'stacked'):
            self.assertIn(slug, sample_slugs)
        self.assertEqual(skips,6)
        self.assertEqual(sum(counts.values())+samples+skips,192)

    def test_all_hint_texts_fit_reserved_bottom_rectangles(self):
        count=0
        for entry in self.entries:
            demos=[entry['demo']]+([entry['demo']['secondary']] if entry['demo'].get('secondary') else [])
            for demo in demos:
                root=self.Document(self.demos.markup(demo,'../../assets/redesign/',True,entry['slug'])).root.one('article')
                wrappers=[node for node in root.children if hasattr(node,'attrs') and
                          set(node.attrs.get('class','').split()) & {'canvas','stage','guide-card-stage'}]
                for hint in root.find_all(cls='ds-hint'):
                    count+=1
                    self.assertTrue(any(hint in node.children for node in wrappers),entry['slug'])
                    # Bound each character by one fullwidth 12px glyph, including
                    # hidden pointer/touch alternatives. Subtract edge offsets,
                    # capsule padding/border, and the icon plus its 8px gap.
                    text=hint.text().removeprefix('↖')
                    for width,reserve,max_lines in ((725.333,56,1),(358,76,2)):
                        available=width-2-24-26-20
                        lines=max(1,math.ceil(len(text)*12/available))
                        self.assertLessEqual(lines,max_lines,(entry['slug'],width))
                        height=lines*18+14
                        self.assertGreaterEqual(reserve-12-height,12,(entry['slug'],width))
        self.assertEqual(count,150)

    def test_reveal_starts_with_a_visible_card_and_grid_keeps_all_data(self):
        skins=ROOT/'site-src/redesign/demo-skins'
        reveal=(skins/'motion-scroll-reveal.html').read_text()
        self.assertIn('reveal-target ds-reveal-card ds-revealed',reveal)
        self.assertIn('发现庭院之美',reveal)
        self.assertEqual(reveal.count('class="ds-reveal-copy"'),3)
        self.assertIn('.scroll-spacer{height:16px}',(skins/'motion-scroll-reveal.css').read_text())
        self.assertEqual((skins/'guide-grid.html').read_text().count('class="ds-grid-card"'),6)
        self.assertIn('nth-child(n+5)',(skins/'guide-grid.css').read_text())


class BatchESkinTest(unittest.TestCase):
    setUpClass = classmethod(DemoSpecBuildTest.setUpClass.__func__)
    SLUGS = ('states', 'landing', 'card', 'toast', 'navbar', 'table', 'tabs',
             'switch', 'select', 'hold-confirm', 'view-slide', 'view-curtain',
             'media-wipe', 'media-blur', 'scroll-parallax', 'scroll-pin')

    def test_e_skins_keep_source_selectors_and_behavior_attributes(self):
        for slug in self.SLUGS:
            with self.subTest(slug=slug):
                entry = next(row for row in self.entries if row['slug'] == slug)
                source = self.Document(entry['demo']['html']).root
                markup = self.demos.markup(entry['demo'], '../../assets/redesign/', True, slug)
                result = self.Document(markup).root
                template = result.one('template')
                skin = entry['demo']['kind'] + '-' + slug
                self.assertEqual(template.attrs['data-skin-css'], '../../assets/redesign/demo-skins/' + skin + '.css')
                self.assertNotIn('data-kind-css', template.attrs)
                self.assertIn('data-ds-sample', result.one('article').attrs)
                nodes = result.find_all()
                for original in source.find_all():
                    classes = set(original.attrs.get('class', '').split())
                    candidates = [node for node in nodes if node.tag == original.tag and
                                  classes <= set(node.attrs.get('class', '').split())]
                    protected = {key: value for key, value in original.attrs.items()
                                 if key == 'id' or key.startswith('data-') or
                                 key in ('role', 'aria-controls', 'aria-label', 'tabindex', 'checked', 'disabled')}
                    self.assertTrue(any(all(node.attrs.get(key) == value and key in node.attrs
                                           for key, value in protected.items()) for node in candidates),
                                    (slug, original.tag, original.attrs))
                hints = result.find_all(cls='ds-hint')
                self.assertEqual(len(hints), 0 if slug == 'landing' else 1)
                if hints:
                    self.assertIn(hints[0], result.one(cls='stage' if entry['demo']['kind'] == 'motion' else 'canvas').children)
                css = (ROOT / 'site-src/redesign/demo-skins' / (skin + '.css')).read_text()
                self.assertNotIn('.ds-hint', css)
                self.assertIn('var(--ds-subject-width)', css)
                self.assertIn('var(--ds-shadow-1)', css)
                self.assertEqual((DIST / 'assets/redesign/demo-skins' / (skin + '.css')).read_text(),
                                 self.demos.assets(self.entries)['demo-skins/' + skin + '.css'])

    def test_e_real_images_have_responsive_paths_and_manifest_sources(self):
        import posixpath
        names = {name for image in json.loads((ROOT / 'site-src/demo-assets/manifest.json').read_text())['images']
                 for name in image['files'].values()}
        expected = {'landing':1, 'card':1, 'view-slide':2, 'view-curtain':2,
                    'media-wipe':1, 'media-blur':1, 'scroll-parallax':2, 'scroll-pin':3}
        for slug, count in expected.items():
            entry = next(row for row in self.entries if row['slug'] == slug)
            for depth in range(4):
                prefix = '../' * depth + 'assets/redesign/'
                markup = self.demos.markup(entry['demo'], prefix, True, slug)
                self.assertNotIn('{{demo-assets}}', markup)
                images = self.Document(markup).root.find_all('img')
                self.assertEqual(len(images), count, slug)
                base = posixpath.normpath(prefix + '../../demo-assets') + '/'
                for image in images:
                    self.assertIn('alt', image.attrs)
                    self.assertTrue(image.attrs['src'].startswith(base))
                    self.assertIn(image.attrs['src'].split('/')[-1], names)
                    self.assertIn('640w', image.attrs['srcset'])
                    self.assertIn('1280w', image.attrs['srcset'])
                    for candidate in image.attrs['srcset'].split(','):
                        self.assertTrue(candidate.strip().startswith(base))

    def test_e_states_labels_select_tabs_and_hold_contracts(self):
        def root(slug):
            entry = next(row for row in self.entries if row['slug'] == slug)
            return self.Document(self.demos.markup(entry['demo'], './', True, slug)).root
        states = root('states')
        self.assertEqual(len(states.find_all(cls='st-btn')), 12)
        self.assertEqual([node.text() for node in states.find_all(cls='st-lbl')],
                         ['default', ':hover', ':active', 'pressed', ':focus', 'selected',
                          ':disabled', 'readonly', 'loading', 'success', 'error', 'warning'])
        self.assertIn('disabled', states.one(cls='dis').attrs)
        toggle = root('switch')
        checkbox = toggle.one('input')
        self.assertEqual(checkbox.attrs['data-cmd'], 'toastChecked')
        self.assertEqual(next(node for node in toggle.find_all('label') if node.attrs.get('id') == checkbox.attrs['aria-labelledby']).text(), '自动保存')
        self.assertEqual(checkbox.attrs['id'], 'ds-autosave')
        select = root('select')
        self.assertEqual([node.text() for node in select.find_all('option')], ['请选择城市…', '北京', '上海', '深圳'])
        self.assertEqual(select.one('label').attrs['for'], select.one('select').attrs['id'])
        tabs = root('tabs')
        self.assertEqual([node.attrs['data-arg'] for node in tabs.find_all(cls='tab')], ['0','1','2'])
        self.assertEqual(tabs.one(cls='tab-panel').attrs['id'], 'tp')
        hold = root('hold-confirm')
        self.assertEqual(hold.one(cls='holdbtn').attrs['id'], 'holdBtn')
        self.assertEqual(hold.one(cls='hold-alt').attrs['data-arg'], '已通过普通按钮删除（演示）')
        self.assertIsNotNone(root('toast').one(cls='ds-toast-output').attrs.get('data-toast-description'))


class BatchFSkinTest(unittest.TestCase):
    setUpClass = classmethod(DemoSpecBuildTest.setUpClass.__func__)
    SLUGS = ('checkbox', 'radio', 'slider', 'otp', 'search', 'segmented',
             'password-strength', 'tag-input', 'stepper', 'rating', 'upload',
             'combobox', 'date', 'form', 'alert', 'empty', 'loader', 'drawer', 'popover')

    def rendered(self, slug):
        entry = next(row for row in self.entries if row['slug'] == slug)
        markup = self.demos.markup(entry['demo'], '../../assets/redesign/', True, slug)
        return entry, self.Document(markup).root

    def test_f_skin_publication_source_contracts_and_hint_parent(self):
        for slug in self.SLUGS:
            with self.subTest(slug=slug):
                entry, result = self.rendered(slug)
                template = result.one('template')
                name = 'demo-skins/ui-' + slug + '.css'
                self.assertEqual(template.attrs['data-skin-css'], '../../assets/redesign/' + name)
                self.assertNotIn('data-kind-css', template.attrs)
                self.assertIn('data-ds-sample', result.one('article').attrs)
                nodes = result.find_all()
                source = self.Document(entry['demo']['html']).root
                for original in source.find_all():
                    classes = set(original.attrs.get('class', '').split())
                    protected = {key: value for key, value in original.attrs.items()
                                 if key == 'id' or key.startswith(('data-', 'aria-')) or
                                 key in ('role', 'tabindex', 'type', 'name', 'value', 'min', 'max',
                                         'maxlength', 'inputmode', 'autocomplete', 'list', 'for',
                                         'checked', 'disabled', 'hidden', 'placeholder')}
                    candidates = [node for node in nodes if node.tag == original.tag and
                                  classes <= set(node.attrs.get('class', '').split())]
                    self.assertTrue(any(all(key in node.attrs and node.attrs[key] == value
                                           for key, value in protected.items()) for node in candidates),
                                    (slug, original.tag, protected))
                    for child in original.children:
                        if isinstance(child, str) and child.strip():
                            self.assertIn(child.strip(), result.text(), slug)
                hints = result.find_all(cls='ds-hint')
                self.assertEqual(len(hints), 1)
                self.assertIn(hints[0], result.one(cls='canvas').children)
                css = (ROOT / 'site-src/redesign' / name).read_text()
                self.assertNotIn('.ds-hint', css)
                self.assertEqual((DIST / 'assets/redesign' / name).read_text(),
                                 self.demos.assets(self.entries)[name])

    def test_f_control_labels_and_original_values(self):
        for slug in ('slider', 'search', 'password-strength', 'tag-input', 'stepper', 'date', 'form'):
            _, root = self.rendered(slug)
            labels = {node.attrs.get('for') for node in root.find_all('label')}
            for field in root.find_all('input'):
                self.assertIn(field.attrs.get('id'), labels, slug)
                self.assertIn('aria-describedby', field.attrs, slug)
        _, otp = self.rendered('otp')
        self.assertEqual(len(otp.one(cls='otp-row').find_all('input')), 6)
        self.assertEqual([node.attrs['aria-label'] for node in otp.one(cls='otp-row').find_all('input')],
                         ['第 1 位', '第 2 位', '第 3 位', '第 4 位', '第 5 位', '第 6 位'])
        _, combo = self.rendered('combobox')
        self.assertEqual([node.attrs['value'] for node in combo.find_all('option')], ['北京', '上海', '深圳', '广州'])
        _, alerts = self.rendered('alert')
        self.assertEqual([node.one('strong').text() for node in alerts.find_all(cls='alert')],
                         ['ℹ️ 这是信息提示', '⚠️ 这是一条警告', '❌ 这是一条错误', '✓ 操作已完成'])

    def test_f_overlays_keep_original_commands_and_single_instances(self):
        _, drawer = self.rendered('drawer')
        for identifier in ('dmask', 'dpanel'):
            self.assertEqual(len([node for node in drawer.find_all() if node.attrs.get('id') == identifier]), 1)
        self.assertEqual(drawer.one(cls='drawer-mask').attrs['data-cmd'], 'closeDrawer')
        self.assertEqual(drawer.one(cls='drawer-head').one('button').attrs['data-cmd'], 'closeDrawer')
        _, popover = self.rendered('popover')
        self.assertIn('hidden', popover.one(cls='popover-box').attrs)
        self.assertEqual(popover.one(cls='popover-demo').one('button').attrs['aria-controls'], 'popover-box')


class BatchGSkinTest(unittest.TestCase):
    setUpClass = classmethod(DemoSpecBuildTest.setUpClass.__func__)
    SLUGS = tuple('cmdk sidebar accordion breadcrumb pagination steps dropdown context-menu mega-menu footer badge chip avatar kpi timeline badge-dot view-switch card-link split-button fab back-to-top table-fixed table-columns table-edit sortable-table load-more'.split())

    def test_g_publication_source_contracts_and_original_copy(self):
        for slug in self.SLUGS:
            with self.subTest(slug=slug):
                entry = next(row for row in self.entries if row['column'] == 'components' and row['slug'] == slug)
                kind = entry['demo']['kind']
                name = 'demo-skins/' + kind + '-' + slug
                override = (ROOT / 'site-src/redesign' / (name + '.html')).read_text()
                original = self.Document(entry['demo']['html']).root
                skin_root = self.Document(override).root
                result = self.Document(self.demos.markup(entry['demo'], '../../assets/redesign/', True, slug)).root
                self.assertEqual(result.one('template').attrs['data-skin-css'], '../../assets/redesign/' + name + '.css')
                self.assertNotIn('data-kind-css', result.one('template').attrs)
                self.assertIn('data-ds-sample', result.one('article').attrs)
                self.assertEqual(len(result.find_all(cls='ds-' + slug + '-panel')), 1)
                for node in original.find_all():
                    classes = set(node.attrs.get('class', '').split())
                    protected = {key:value for key,value in node.attrs.items() if key != 'class'}
                    candidates = [item for item in skin_root.find_all() if item.tag == node.tag and
                                  classes <= set(item.attrs.get('class', '').split())]
                    self.assertTrue(any(all(key in item.attrs and item.attrs[key] == value
                                            for key,value in protected.items()) for item in candidates),
                                    (slug,node.tag,protected))
                    for child in node.children:
                        if isinstance(child,str) and child.strip():
                            if child.strip() in {'▾', '▼', '⌄'}:
                                # Decorative text chevrons sit on the baseline; skins draw them as a centred SVG chevron instead.
                                self.assertTrue(any(svg.one('path') for svg in skin_root.find_all('svg')), (slug, child.strip()))
                                continue
                            self.assertIn(child.strip(), skin_root.text(), slug)
                hints = result.find_all(cls='ds-hint')
                self.assertEqual(len(hints), int(kind == 'ui'))
                if hints:
                    self.assertIn(hints[0], result.one(cls='canvas').children)
                self.assertEqual((DIST / 'assets/redesign' / (name + '.css')).read_text(),
                                 self.demos.assets(self.entries)[name + '.css'])

    def test_g_kind_prefixes_and_overlay_ownership(self):
        sidebar = next(row for row in self.entries if row['column'] == 'basics' and row['slug'] == 'sidebar')
        guide = self.demos.markup(sidebar['demo'], './', True, 'sidebar')
        self.assertNotIn('ui-sidebar.css', guide)
        # basics/sidebar now has its own guide skin; it must never pick up the component's ui-sidebar skin.
        self.assertIn('data-skin-css="./demo-skins/guide-sidebar.css"', guide)
        cmdk = next(row for row in self.entries if row['column'] == 'components' and row['slug'] == 'cmdk')
        result = self.Document(self.demos.markup(cmdk['demo'], './', True, 'cmdk')).root
        overlays = result.one(cls='ds-overlays')
        self.assertEqual(len(overlays.find_all(cls='cmdk-mask')), 1)
        self.assertIsNotNone(overlays.one(cls='cmdk-mask').attrs.get('data-demo-commands'))
        sortable = next(row for row in self.entries if row['column'] == 'components' and row['slug'] == 'sortable-table')
        result = self.Document(self.demos.markup(sortable['demo'], './', True, 'sortable-table')).root
        self.assertIn('guide-sortable-table.css', result.one('template').attrs['data-skin-css'])
        self.assertEqual([node.attrs['data-guide-mode'] for node in result.find_all('button')], ['0', '1'])


class BatchHSkinTest(unittest.TestCase):
    setUpClass = classmethod(DemoSpecBuildTest.setUpClass.__func__)
    SLUGS = 'component-tilt component-spotlight component-flip component-press component-switch component-morph tab-indicator inline-expand component-magnetic component-hover-preview component-hover-action component-ripple component-underline accordion overlay-menu overlay-drawer overlay-modal overlay-tooltip overlay-sheet toast-stack data-count data-bars data-reorder data-success filter-grid chart-morph skeleton-handoff data-input-shake data-skeleton text-stagger text-mask text-typewriter text-scramble text-draw odometer scroll-highlight text-text-morph'.split()

    def test_h_individual_skin_publication_and_source_contracts(self):
        assets = self.demos.assets(self.entries)
        for slug in self.SLUGS:
            with self.subTest(slug=slug):
                entry = next(row for row in self.entries if row['slug'] == slug and row['demo']['kind'] == 'motion')
                name = 'demo-skins/motion-' + slug
                self.assertTrue((ROOT / 'site-src/redesign' / (name + '.css')).is_file())
                html = self.demos.markup(entry['demo'], '../../assets/redesign/', True, slug)
                result = self.Document(html).root
                self.assertEqual(result.one('template').attrs['data-skin-css'], '../../assets/redesign/' + name + '.css')
                self.assertNotIn('data-kind-css', result.one('template').attrs)
                self.assertEqual(len(result.find_all(cls='ds-h-panel')), 1)
                original = self.Document(entry['demo']['html']).root
                nodes = result.find_all()
                for node in original.find_all():
                    classes = set(node.attrs.get('class', '').split())
                    protected = {key: ('#' if key == 'href' and value == 'javascript:void 0' else value)
                                 for key,value in node.attrs.items() if key != 'class'}
                    candidates = [item for item in nodes if item.tag == node.tag and classes <= set(item.attrs.get('class', '').split())]
                    self.assertTrue(any(all(key in item.attrs and item.attrs[key] == value for key,value in protected.items()) for item in candidates), (slug,node.tag,protected))
                    for child in node.children:
                        if isinstance(child, str) and child.strip():
                            self.assertIn(child.strip(), result.text(), slug)
                hints = result.find_all(cls='ds-hint')
                self.assertEqual(len(hints), 1)
                self.assertIn(hints[0], result.one(cls='stage').children)
                self.assertEqual((DIST / 'assets/redesign' / (name + '.css')).read_text(), assets[name + '.css'])

    def test_h_accordion_uses_motion_kind_and_images_resolve(self):
        import posixpath
        manifest = json.loads((ROOT / 'site-src/demo-assets/manifest.json').read_text())['images']
        filenames = {name for image in manifest for name in image['files'].values()}
        for slug in self.SLUGS:
            entry = next(row for row in self.entries if row['slug'] == slug and row['demo']['kind'] == 'motion')
            for depth in range(4):
                prefix = '../' * depth + 'assets/redesign/'
                markup = self.demos.markup(entry['demo'], prefix, True, slug)
                self.assertNotIn('{{demo-assets}}', markup)
                for image in self.Document(markup).root.find_all('img'):
                    self.assertTrue(image.attrs['alt'])
                    self.assertIn(image.attrs['src'].split('/')[-1], filenames)
                    self.assertTrue(image.attrs['src'].startswith(posixpath.normpath(prefix + '../../demo-assets') + '/'))
                    self.assertIn('640w', image.attrs['srcset'])
                    self.assertIn('1280w', image.attrs['srcset'])
        ui = next(row for row in self.entries if row['slug'] == 'accordion' and row['demo']['kind'] == 'ui')
        self.assertIn('ui-accordion.css', self.demos.markup(ui['demo'], './', True, 'accordion'))
