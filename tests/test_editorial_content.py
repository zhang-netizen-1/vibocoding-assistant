"""Editorial overlay validation, without touching original source content."""
import copy
import importlib.util
from pathlib import Path
import unittest
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent.parent/'site-src'))

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('editorial_entries', ROOT/'site-src/entries.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def sample():
    return dict(aliases=['轻点执行', '执行控件', '主操作入口'], when_use='提交、保存时使用。',
                when_avoid='页面跳转使用链接。', prompt_edit='找到按钮后统一修改。',
                prompt_new='实现按钮。', acceptance=['焦点环对比度至少 3:1。', '状态切换时尺寸不变。', '加载期间不重复提交。'], reviewed=False)


class EditorialTest(unittest.TestCase):
    def setUp(self):
        self.entries = MODULE.load_entries(content={})
        self.key = 'components/button'

    def test_empty_overlay_is_lossless(self):
        self.assertEqual(MODULE.apply_content(self.entries, {}), self.entries)

    def test_overlay_preserves_source_prompt_and_uses_editorial_acceptance(self):
        original = copy.deepcopy(self.entries)
        edited = MODULE.apply_content(original, {self.key: sample()})
        button = next(e for e in edited if e['column'] == 'components' and e['slug'] == 'button')
        self.assertEqual(button['prompt'], sample()['prompt_edit'])
        self.assertEqual(button['acceptance'], sample()['acceptance'])
        self.assertEqual(button['prompt_original'], next(e for e in original if e['column'] == 'components' and e['slug'] == 'button')['prompt'])
        self.assertNotIn('prompt_original', original[0])

    def test_invalid_editorial_fields_are_rejected(self):
        mutations = [dict(aliases=['a', 'b']), dict(aliases=['a', 'a', 'b']),
                     dict(aliases=['按钮', 'b', 'c']), dict(aliases=['Button', 'b', 'c']),
                     dict(acceptance=['一条']), dict(acceptance=['好看', '两条', '三条']),
                     dict(prompt_edit=' '), dict(prompt_new=''), dict(when_use=''),
                     dict(when_avoid=''), dict(reviewed=None), dict(aliases='abc')]
        for mutation in mutations:
            with self.subTest(mutation=mutation), self.assertRaises(ValueError):
                MODULE.apply_content(self.entries, {self.key: {**sample(), **mutation}})

    def test_alias_conflict_reports_both_entries_and_strict_requires_all(self):
        with self.assertRaisesRegex(ValueError, 'components/button.*components/input'):
            MODULE.apply_content(self.entries, {self.key: sample(), 'components/input': sample()})
        with self.assertRaisesRegex(ValueError, '187'):
            MODULE.apply_content(self.entries, {}, strict=True)
        with self.assertRaisesRegex(ValueError, 'unknown'):
            MODULE.apply_content(self.entries, {'components/unknown': sample()})


class EditorialPageTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        spec = importlib.util.spec_from_file_location('editorial_templates', ROOT/'site-src/redesign/templates.py')
        cls.templates = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cls.templates)
        cls.raw = MODULE.load_entries(content={})
        cls.tax = MODULE.taxonomy()

    def edited(self, key='components/button'):
        fields = sample()
        fields['params'] = ['点击区域：24×24px 起，手机 44×44px，便于点选。']
        return MODULE.apply_content(self.raw, {key: fields})

    def test_both_payloads_include_numbered_acceptance_and_validation(self):
        for key in ('components/button', 'interactions/submit', 'interactions/undo'):
            edited = self.edited(key)
            entry = next(e for e in edited if e['column']+'/'+e['slug'] == key)
            for version in ('prompt_edit', 'prompt_new'):
                expected = entry[version] + '\n\n验收要求：\n' + '\n'.join(f'{i}. {text}' for i,text in enumerate(entry['acceptance'], 1)) + '\n\n完成后列出改了哪些文件，并说明以上 3 条各自是怎么验证的。'
                self.assertEqual(self.templates.copy_payload(entry, version), expected)
                self.assertNotIn(entry.get('prompt_secondary', 'UNUSED'), expected)

    def test_editorial_page_controls_and_collapsed_criteria(self):
        from html import unescape
        import re
        edited = self.edited()
        entry = next(e for e in edited if e['column'] == 'components' and e['slug'] == 'button')
        html = self.templates.detail(entry, edited, self.tax)
        self.assertIn('也叫：轻点执行、执行控件、主操作入口', html)
        self.assertIn('关键参数', html)
        self.assertIn('共 3 条验收要求，见使用卡；复制提示词时自动包含', html)
        self.assertIn('复制这一版', html)
        prompt_sections = MODULE.Document(html).root.find_all('section', 'prompt-box')
        self.assertTrue(any(section.find_all('details', 'new-section') for section in prompt_sections))
        self.assertIn('data-copy-source="copy-new-prompt"', html)
        self.assertNotIn('open', re.search(r'<details class="criteria"[^>]*>', html)[0])
        self.assertNotIn('open', re.search(r'<details class="entry-section new-section"[^>]*>', html)[0])
        payload = re.search(r'id="copy-new-prompt" hidden>(.*?)</pre>', html, re.S)[1]
        self.assertEqual(unescape(payload), self.templates.copy_payload(entry, 'prompt_new'))
        self.assertIn('<div class="bottom-bar"><button data-show-acceptance>验收要求</button>', html)
        self.assertEqual(html.count('复制这条'), 3)

    def test_unedited_entry_keeps_original_optional_sections(self):
        entry = next(e for e in self.raw if e['column'] == 'components' and e['slug'] == 'input')
        html = self.templates.detail(entry, self.raw, self.tax)
        self.assertNotIn('copy-new-prompt', html)
        self.assertNotIn('见使用卡', html)
        self.assertNotIn('entry-aliases', html)
        self.assertEqual(self.templates.copy_payload(entry), entry['prompt'])
