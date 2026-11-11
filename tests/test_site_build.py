from html.parser import HTMLParser
from html import escape, unescape
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path
import importlib.util
import json
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

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        self.references.extend(attributes[key] for key in ("href", "src") if attributes.get(key))
        if tag == "img":
            self.images.append(attributes)
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
        self.assertEqual(len(builder.REDESIGN.generated_pages(entries)), 2 + len(builder.REDESIGN.first_group(entries)))

    def test_bench_pages_navigation_badges_and_local_references(self):
        paths = [DIST / "bench" / "index.html", *(DIST / "bench" / slug / "index.html" for slug in ("button", "crossfade", "grid"))]
        image_count = 0
        for path in paths:
            self.assertTrue(path.is_file(), path)
            page = path.read_text(encoding="utf-8")
            self.assertNotRegex(page.lower(), "dsh")
            self.assertIn('aria-current="page">测评结果</a>', page)
            parsed = parse(path)
            self.assertIn("site-content", parsed.ids)
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
                    self.assertIn(unquote(url.fragment), parse(target).ids, (path, ref))
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
        for section in ("ui", "motion", "layout", "visual", "interaction", "pages", "data", "skills"):
            self.assertIn("../bench/", parse(DIST / section / "index.html").links)
        self.assertIn("./bench/", parse(DIST / "index.html").links)
        for section, slug in (("ui", "button"), ("motion", "crossfade"), ("layout", "grid")):
            page = (DIST / section / "index.html").read_text(encoding="utf-8")
            self.assertIn(f'href="../bench/{slug}/">测评结果 →</a>', page)
            self.assertEqual(page.count("测评结果 →</a>"), 1)
            anchor = {"button": "c-button", "crossfade": "e-view-crossfade", "grid": "g-layout-grid"}[slug]
            card = re.search(rf'<article[^>]*id="{anchor}".*?</article>', page, re.S).group()
            self.assertIn(f'href="../bench/{slug}/">测评结果 →</a>', card)

    def test_bench_preserves_source_prompts_evidence_and_totals(self):
        source = ROOT / "site-src" / "bench" / "data"
        overview = (DIST / "bench" / "index.html").read_text(encoding="utf-8")
        narrative = json.loads((source / "narrative.json").read_text(encoding="utf-8"))
        self.assertIn(escape(narrative["time_note"]), overview)
        rounds = [json.loads((source / f"round{rnd}-results.json").read_text(encoding="utf-8")) for rnd in (1, 2)]
        for slug in ("button", "crossfade", "grid"):
            page = (DIST / "bench" / slug / "index.html").read_text(encoding="utf-8")
            self.assertIn(f'href="../{narrative["entries"][slug]["site_link"]}">查看速查条目', page)
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
        home = parse(DIST / "index.html")
        self.assertIn("./components/", home.links)
        self.assertIn("./motion/#section-view", home.links)
        home_html = (DIST / "index.html").read_text(encoding="utf-8")
        entries = json.loads((ROOT / "build/entries.json").read_text())
        self.assertIn(f"{len(entries)} 个界面效果", home_html)
        self.assertIn('id="search-dialog"', home_html)
        self.assertEqual(home_html.count('<article class="layer"'), len({e["column"] for e in entries}))
        self.assertNotIn('class="home-demo"', home_html)
        self.assertEqual((DIST / "ui" / "index.html").read_text(encoding="utf-8").count("<summary>查看并复制组件实现提示词</summary>"), 70)
        self.assertEqual((DIST / "motion" / "index.html").read_text(encoding="utf-8").count("<summary>查看并复制动效实现提示词</summary>"), 79)
        for section, original, prefix, expected_count in (
            ("ui", "网页UI元素速查.html", "c-", 70),
            ("motion", "动效速查.html", "e-", 79),
        ):
            built = parse(DIST / section / "index.html")
            source = parse(ROOT / original)
            self.assertEqual(len(built.cards), expected_count)
            self.assertEqual(set(built.cards), set(source.cards))
            self.assertEqual(len(set(built.cards)), expected_count)
            self.assertTrue(all(card.startswith(prefix) for card in built.cards))
            self.assertIn("../", built.links)
            self.assertIn("../ui/", built.links)
            self.assertIn("../motion/", built.links)
            self.assertIn("site-content", built.ids)
        home_js = (DIST / "assets" / "home.js").read_text(encoding="utf-8")
        self.assertNotIn("directory-secondary", home_js)
        self.assertNotIn("directory-secondary", home_html)
        ui_html = (DIST / "ui" / "index.html").read_text(encoding="utf-8")
        self.assertNotIn('class="scenarios"', ui_html)
        for page_path in (DIST / "index.html", *(DIST / section / "index.html" for section in ("ui", "motion", "layout", "visual", "interaction", "pages", "data", "skills"))):
            page = page_path.read_text(encoding="utf-8")
            self.assertNotIn('>组合流程</a>', page)

        for section in ("layout", "visual", "interaction", "pages", "data"):
            built = parse(DIST / section / "index.html")
            self.assertEqual(len(built.cards), 6, section)
            self.assertEqual((DIST / section / "index.html").read_text(encoding="utf-8").count("<summary>查看并复制实现提示词</summary>"), 6, section)
            self.assertEqual(len(set(built.cards)), 6, section)
            self.assertTrue(all(card.startswith(f"g-{section}-") for card in built.cards))
            if section == "data":
                self.assertIn("../data/#g-data-line", parse(DIST / "components/index.html").links)
            else:
                self.assertIn(f"./{section}/", home.links)
            self.assertIn("guide-main", built.ids)
            self.assertIn("../", built.links)
        visual_html = (DIST / "visual" / "index.html").read_text(encoding="utf-8")
        self.assertIn("极简主义", visual_html)
        self.assertIn("玻璃拟态", visual_html)
        self.assertIn("新粗野主义", visual_html)
        self.assertIn('id="g-visual-type"', visual_html)
        self.assertNotIn('<h3>字体层级</h3>', visual_html)
        skills = parse(DIST / "skills" / "index.html")
        self.assertEqual(len(skills.cards), 10)
        self.assertEqual((DIST / "skills" / "index.html").read_text(encoding="utf-8").count("<summary>查看并复制 Skill 安装提示词</summary>"), 10)
        self.assertEqual(len(set(skills.cards)), 10)
        self.assertTrue(all(card.startswith("skill-") for card in skills.cards))
        self.assertIn("./skills/", home.links)
        self.assertIn("skills-main", skills.ids)
        self.assertIn("../", skills.links)

    def test_site_scripts_and_metadata(self):
        home = (DIST / "index.html").read_text(encoding="utf-8")
        self.assertRegex(home, r'src="\./assets/redesign/site\.js\?v=[0-9a-f]{8}"')
        self.assertRegex(home, r'href="\./assets/redesign/tokens\.css\?v=[0-9a-f]{8}"')
        for section in ("ui", "motion"):
            page = (DIST / section / "index.html").read_text(encoding="utf-8")
            self.assertIn('name="description"', page)
            self.assertRegex(page, r'src="../assets/site\.js\?v=[0-9a-f]{8}"')
            self.assertRegex(page, r'href="../assets/site\.css\?v=[0-9a-f]{8}"')
            self.assertIn('class="site-nav"', page)
            self.assertIn('class="site-skip"', page)
            self.assertIn('class="site-reference-workspace"', page)
        for section in ("layout", "visual", "interaction", "pages", "data"):
            page = (DIST / section / "index.html").read_text(encoding="utf-8")
            self.assertRegex(page, r'src="../assets/guides\.js\?v=[0-9a-f]{8}"')
            self.assertRegex(page, r'href="../assets/guides\.css\?v=[0-9a-f]{8}"')
            self.assertIn('class="site-skip"', page)
            self.assertIn('id="guide-copy-status" class="site-announcement" role="status"', page)
            if section == "visual":
                self.assertRegex(page, r'href="../assets/visual-styles\.css\?v=[0-9a-f]{8}"')
        skills_page = (DIST / "skills" / "index.html").read_text(encoding="utf-8")
        self.assertRegex(skills_page, r'src="../assets/skills\.js\?v=[0-9a-f]{8}"')
        self.assertRegex(skills_page, r'href="../assets/skills\.css\?v=[0-9a-f]{8}"')
        self.assertIn('aria-current="page">Skills', skills_page)
        self.assertIn('id="skill-copy-status" class="site-announcement" role="status"', skills_page)
        for section in ("ui", "motion", "layout", "visual", "interaction", "pages", "data", "skills"):
            page = (DIST / section / "index.html").read_text(encoding="utf-8")
            self.assertRegex(page, r'assets/theme\.css\?v=[0-9a-f]{8}')

    def test_global_search_index_matches_real_anchors(self):
        home = (DIST / "index.html").read_text(encoding="utf-8")
        match = re.search(r'<script type="application/json" id="redesign-search-index">(.*?)</script>', home, re.S)
        self.assertIsNotNone(match)
        entries = json.loads(match.group(1))["entries"]
        unified = json.loads((ROOT / "build/entries.json").read_text())
        self.assertEqual(len(entries), len(unified))
        self.assertEqual(len({entry["href"] for entry in entries}), len(unified))
        counts = {category: sum(entry["column"] == category for entry in entries) for category in {entry["column"] for entry in entries}}
        self.assertEqual(counts, {"设计基础": 12, "组件": 75, "交互与动效": 84, "页面与场景": 6, "AI 实现": 10})
        for entry in entries:
            url = urlsplit(entry["href"])
            target = DIST / unquote(url.path)
            if target.is_dir():
                target /= "index.html"
            self.assertTrue(target.is_file(), entry["href"])
            if url.fragment:
                self.assertIn(url.fragment, parse(target).ids, entry["href"])
            self.assertTrue(entry["zh"])
        self.assertEqual([e["prompt"] for e in entries], [e["prompt"] for e in unified])

    def test_redesign_first_group_and_local_routes(self):
        entries = json.loads((ROOT / "build/entries.json").read_text())
        actions = [e for e in entries if e["column"] == "components" and e["group"] == "actions"]
        new_pages = [DIST / "index.html", DIST / "components/index.html", *(DIST / "components" / e["slug"] / "index.html" for e in actions)]
        for path in new_pages:
            self.assertTrue(path.is_file(), path)
            page = path.read_text()
            self.assertIn("Vibe Design 速查", page)
            self.assertNotIn("189", page)
            self.assertNotIn("INTERFACE FIELD GUIDE", page)
            parsed = parse(path)
            for ref in parsed.references:
                url = urlsplit(ref)
                self.assertFalse(ref.startswith("/"), (path, ref))
                self.assertFalse(url.scheme or url.netloc, (path, ref))
                target = (path.parent / unquote(url.path)).resolve() if url.path else path
                self.assertTrue(target.is_relative_to(DIST.resolve()), (path, ref))
                if target.is_dir():
                    target /= "index.html"
                self.assertTrue(target.is_file(), (path, ref))
                if url.fragment:
                    self.assertIn(unquote(url.fragment), parse(target).ids, (path, ref))
            for panel in re.findall(r'<div class="mega".*?</div><!-- mega -->', page, re.S):
                # D19 exception: the component-state introduction is allowed.
                text = unescape(re.sub(r'<[^>]+>', '', panel))
                for entry in entries:
                    if entry["zh"] != "组件状态":
                        self.assertNotRegex(text, r'(?<![\w\u4e00-\u9fff])' + re.escape(entry["zh"]) + r'(?![\w\u4e00-\u9fff])')
        for e in actions:
            page = (DIST / "components" / e["slug"] / "index.html").read_text()
            match = re.search(r'<pre class="prompt-text" id="entry-prompt">(.*?)</pre>', page, re.S)
            self.assertIsNotNone(match)
            self.assertEqual(unescape(match[1]), e["prompt"])
            self.assertIn('data-copy-source="entry-prompt"', page)
            self.assertIn('class="demo-scope"', page)
            self.assertNotIn('id="acceptance"', page)  # UI sources contain no acceptance array.
            self.assertNotIn('状态切换', page)
            self.assertNotIn('它怎么动', page)

    def test_first_group_uses_original_demo_markup_and_safe_search_destinations(self):
        spec = importlib.util.spec_from_file_location("entry_adapter_test", ROOT / "site-src/entries.py")
        adapter = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(adapter)
        entries = adapter.load_entries()
        actions = [e for e in entries if e['column'] == 'components' and e['group'] == 'actions']
        column_path = DIST / 'components/index.html'
        column_html = column_path.read_text()
        column_doc = adapter.Document(column_html).root
        self.assertEqual(len(column_doc.find_all('article','gallery-card')),len(actions))
        self.assertEqual(len(column_doc.find_all('article','simple-card')),sum(e['column']=='components' for e in entries)-len(actions))
        self.assertEqual(column_doc.find_all(cls='prompt-text'),[])
        for e in actions:
            path = DIST / 'components' / e['slug'] / 'index.html'
            page = path.read_text()
            doc = adapter.Document(page).root
            self.assertEqual(doc.one(cls='demo-scope').inner(page), e['demo']['html'])
            self.assertEqual(doc.one(cls='definition').text(), e['definition'].splitlines()[0])
            points = doc.find_all(cls='entry-points')
            self.assertEqual([n.text() for n in points[0].find_all('li')] if points else [], e['definition'].splitlines()[1:])
            for optional in ('when_avoid','prompt_new'):
                self.assertNotIn(optional,e)
            if 'bench' in e:
                self.assertIn('../../bench/'+e['bench']['slug']+'/',parse(path).links)
            else:
                self.assertEqual(doc.find_all(cls='bench-badge'),[])
        paths = [DIST/'index.html', column_path, *(DIST/'components'/e['slug']/'index.html' for e in actions)]
        for path in paths:
            html = path.read_text()
            doc = adapter.Document(html).root
            ids = [node.attrs['id'] for node in doc.find_all() if node.attrs.get('id')]
            self.assertEqual(len(ids),len(set(ids)),path)
            index = json.loads(next(n for n in doc.find_all('script') if n.attrs.get('id')=='redesign-search-index').text())
            self.assertEqual(len(index['entries']),len(entries))
            for item in [*index['entries'],*index['columns']]:
                href = item['href']
                self.assertFalse(href.startswith('/'),(path,href))
                url = urlsplit(href)
                target = (path.parent/url.path).resolve()
                self.assertTrue(target.is_relative_to(DIST.resolve()))
                if target.is_dir(): target /= 'index.html'
                self.assertTrue(target.is_file(),(path,href))
                if url.fragment: self.assertIn(url.fragment,parse(target).ids,(path,href))

    def test_old_pages_unchanged_during_first_group(self):
        import hashlib
        hashes = json.loads((ROOT / "tests/fixtures/legacy_page_hashes.json").read_text())
        for name, expected in hashes.items():
            self.assertEqual(hashlib.sha256((DIST / name).read_bytes()).hexdigest(), expected, name)

    def test_guide_prompts_are_actionable_and_unique(self):
        prompts = {}
        for section, guide in GUIDE_MODULE.GUIDES.items():
            page = (DIST / section / "index.html").read_text(encoding="utf-8")
            self.assertEqual(page.count('class="guide-prompt-text"'), 6)
            self.assertEqual(page.count('class="guide-copy"'), 6)
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
        page = (DIST / "skills" / "index.html").read_text(encoding="utf-8")
        self.assertEqual(page.count('class="skill-install-text"'), 10)
        self.assertEqual(page.count('class="skill-copy"'), 10)
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
