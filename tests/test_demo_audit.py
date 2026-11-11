import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('audit', ROOT / 'scripts/audit_demos.py')
AUDIT = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(AUDIT)


class DemoAuditTest(unittest.TestCase):
    def test_all_entries_have_evidence_and_migration_strategy(self):
        rows = AUDIT.audit()
        self.assertEqual(len(rows), 187)
        for e, category, evidence in rows:
            self.assertIn(category, ('纯 CSS 动画', '需要 JS 驱动', '依赖鼠标指针', '需人工确认'))
            self.assertTrue(evidence)
        report = AUDIT.report()
        self.assertEqual((ROOT / 'docs/phase1-demo-audit.md').read_text(), report)
        self.assertEqual(sum(line.startswith('| ') for line in report.splitlines()), 188)
        by_anchor = {a: category for e, category, _ in rows for a in e['old_anchors']}
        self.assertEqual(by_anchor['e-component-tilt'], '依赖鼠标指针')
        self.assertEqual(by_anchor['c-split-button'], '需要 JS 驱动')
        self.assertEqual(by_anchor['skill-frontend-design'], '需人工确认')
