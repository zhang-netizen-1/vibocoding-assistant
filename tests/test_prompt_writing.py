"""Prompt-writing is a local explanation page, excluded from entry counts."""
from pathlib import Path
import sys
import unittest
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'site-src'))
import entries
sys.path.insert(0, str(ROOT / 'site-src/redesign'))
import templates


class PromptWritingTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.path = ROOT / 'dist/ai/prompt-writing/index.html'
        cls.entries = entries.load_entries()

    def test_page_sources_and_full_button_example(self):
        self.assertTrue(self.path.is_file())
        html = self.path.read_text()
        doc = entries.Document(html).root
        self.assertIn('结构怎么读：形态与变体 → 状态 → 可配置项 → 交互约束 → 沿用项目规范', doc.text())
        for text in ('技术工具', '触发方式', '动效类型', 'UX 规则', '谁触发', '怎样恢复', '键盘和触屏', '写进去的稳定', '3–6 条', '约 2 倍', '改现有页面', '新做一个'):
            self.assertIn(text, doc.text())
        button = next(e for e in self.entries if e['column'] == 'components' and e['slug'] == 'button')
        for version, identifier in [('prompt_edit', 'button-edit-example'), ('prompt_new', 'button-new-example')]:
            example = next(n for n in doc.find_all('pre') if n.attrs.get('id') == identifier)
            self.assertEqual(example.text(), templates.copy_payload(button, version))
            self.assertIn(f'data-copy-source="{identifier}"', html)

    def test_all_links_and_motion_fragments_resolve(self):
        self.assertTrue(self.path.is_file())
        doc = entries.Document(self.path.read_text()).root
        links = [n.attrs['href'] for n in doc.find_all('a')]
        for required in ('../../interactions/spec/#spec-structure', '../../interactions/spec/#spec-checklist', '../../bench/', '../../components/button/'):
            self.assertIn(required, links)
        for ref in links:
            url = urlsplit(ref)
            self.assertFalse(url.scheme or url.netloc or ref.startswith('/'), ref)
            target = (self.path.parent / url.path).resolve() if url.path else self.path
            if target.is_dir():
                target /= 'index.html'
            self.assertTrue(target.is_relative_to((ROOT / 'dist').resolve()))
            self.assertTrue(target.is_file(), ref)
            if url.fragment:
                ids = [n.attrs.get('id') for n in entries.Document(target.read_text()).root.find_all()]
                self.assertIn(url.fragment, ids, ref)

    def test_column_mega_and_drawer_entries_and_count(self):
        html = (ROOT / 'dist/ai/index.html').read_text()
        doc = entries.Document(html).root
        mega = next(n for n in doc.find_all() if n.attrs.get('id') == 'mega-ai')
        drawer = next(n for n in doc.find_all() if n.attrs.get('id') == 'directory')
        main = next(n for n in doc.find_all() if n.attrs.get('id') == 'main')
        for region in (mega, drawer, main):
            self.assertTrue(any(n.text().startswith('提示词写法') and n.attrs.get('href') == './prompt-writing/' for n in region.find_all('a')))
        self.assertEqual(len(self.entries), 192)
        self.assertEqual(sum(e['column'] == 'ai' for e in self.entries), 10)
        self.assertEqual(templates.generated_pages(self.entries).count('ai/prompt-writing/index.html'), 1)
        self.assertFalse(any(e['slug'] == 'prompt-writing' for e in self.entries))
