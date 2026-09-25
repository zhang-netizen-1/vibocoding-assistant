from html.parser import HTMLParser
from pathlib import Path
import importlib.util
import subprocess
import sys
import unittest


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

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
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
        self.assertEqual(files, {
            ".generated-site", "index.html", "ui/index.html", "motion/index.html",
            "motion/motion-demo-gallery.html", "motion/motion-demo-detail.html",
            "layout/index.html", "visual/index.html", "interaction/index.html", "pages/index.html", "data/index.html", "skills/index.html",
            "assets/site.css", "assets/theme.css", "assets/site.js", "assets/guides.css", "assets/guides.js", "assets/visual-styles.css", "assets/skills.css", "assets/skills.js", "assets/favicon.svg",
        })

    def test_site_routes_and_all_cards(self):
        home = parse(DIST / "index.html")
        self.assertIn("./ui/", home.links)
        self.assertIn("./motion/", home.links)
        home_html = (DIST / "index.html").read_text(encoding="utf-8")
        self.assertIn("<strong>152</strong> 个可查条目", home_html)
        self.assertIn("65 个条目", home_html)
        for section, original, prefix, expected_count in (
            ("ui", "网页UI元素速查.html", "c-", 47),
            ("motion", "动效速查.html", "e-", 65),
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

        for section in ("layout", "visual", "interaction", "pages", "data"):
            built = parse(DIST / section / "index.html")
            self.assertEqual(len(built.cards), 6, section)
            self.assertEqual(len(set(built.cards)), 6, section)
            self.assertTrue(all(card.startswith(f"g-{section}-") for card in built.cards))
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
        self.assertEqual(len(set(skills.cards)), 10)
        self.assertTrue(all(card.startswith("skill-") for card in skills.cards))
        self.assertIn("./skills/", home.links)
        self.assertIn("skills-main", skills.ids)
        self.assertIn("../", skills.links)

    def test_site_scripts_and_metadata(self):
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
        self.assertIn('aria-current="page">UI 与交互 Skills', skills_page)
        self.assertIn('id="skill-copy-status" class="site-announcement" role="status"', skills_page)
        for page_path in (DIST / "index.html", *(DIST / section / "index.html" for section in ("ui", "motion", "layout", "visual", "interaction", "pages", "data", "skills"))):
            page = page_path.read_text(encoding="utf-8")
            self.assertRegex(page, r'assets/theme\.css\?v=[0-9a-f]{8}')

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
