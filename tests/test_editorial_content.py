"""Editorial overlay validation, without touching original source content."""
import copy
import importlib.util
from pathlib import Path
import unittest

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
