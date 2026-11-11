"""Fixed spoken queries exercise the generated index through Node, without a browser."""
import json
from pathlib import Path
import re
import subprocess
import sys
import unittest

ROOT = Path(__file__).resolve().parent.parent


class SearchQueriesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run([sys.executable, 'scripts/build_site.py'], cwd=ROOT, check=True, capture_output=True)
        cls.result = subprocess.run(['node', 'tests/search_queries.cjs'], cwd=ROOT, text=True, capture_output=True)
        if not cls.result.stdout:
            raise AssertionError(cls.result.stderr)
        cls.report = json.loads(cls.result.stdout)
        cls.home = (ROOT / 'dist/index.html').read_text()
        cls.data = json.loads(re.search(r'id="redesign-search-index">(.*?)</script>', cls.home, re.S)[1])

    def test_fixed_queries_hit_expected_entries_in_top_three(self):
        report = self.report
        print(f"口语搜索前 3 条命中 {report['hits']}/{report['total']}，命中率 {report['hit_rate']:.0%}，未命中 {len(report['missed'])} 条。")
        for missed in report['missed']:
            print(f"未命中查询「{missed['query']}」，期望 {missed['expected']}，前 3 条为 {missed['top3']}。")
        self.assertEqual(report['total'], 60)
        self.assertGreaterEqual(report['hit_rate'], 0.9, self.result.stdout)
        self.assertEqual(report['mandatory_missed'], [], self.result.stdout)
        self.assertEqual(self.result.returncode, 0, self.result.stderr + self.result.stdout)

    def test_english_case_changes_preserve_all_result_ordering(self):
        self.assertGreaterEqual(self.report['english_queries'], 192)
        self.assertEqual(self.report['case_failures'], [], self.result.stdout)

    def test_home_and_search_overlay_use_the_spoken_examples(self):
        examples = ['浮起来', '弹出来的小黑框', 'Crossfade', '点了会变的按钮']
        self.assertEqual(self.data['examples'], examples)
        self.assertEqual(re.findall(r'data-query="([^"]+)"', self.home), examples)
        placeholder = '用你自己的说法搜，比如：鼠标放上去浮起来'
        self.assertIn(placeholder, self.home)
        self.assertIn(f'placeholder="{placeholder}"', self.home)
        for example in examples:
            result = next(row for row in self.report['results'] if row['query'] == example)
            self.assertTrue(result['hit'], example)
        script = (ROOT / 'dist/assets/redesign/site.js').read_text()
        self.assertIn('data.examples.map', script)
        self.assertIn('比如「滑入」「弹出」「浮起来」', script)
