from collections import Counter
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent


class FrozenAnchorsTest(unittest.TestCase):
    def test_frozen_search_destinations(self):
        data = json.loads((ROOT / 'tests/fixtures/old_anchors.json').read_text())
        entries = data['entries']
        self.assertEqual(len(entries), 189)
        self.assertEqual(len({(e['old_path'], e['anchor']) for e in entries}), 189)
        self.assertEqual(len({e['anchor'] for e in entries}), 189)
        self.assertTrue(all(e['title'] for e in entries))
        self.assertEqual(Counter(e['old_path'] for e in entries),
                         {'/ui/': 70, '/motion/': 79, '/layout/': 6, '/visual/': 6,
                          '/interaction/': 6, '/pages/': 6, '/data/': 6, '/skills/': 10})
        others = data['non_entries']
        self.assertTrue(any(e['anchor'].startswith('section-') for e in others))
        self.assertTrue(any(e['anchor'].startswith('spec-') for e in others))
        for page in ('layout', 'visual', 'interaction', 'pages', 'data'):
            self.assertIn({'old_path': f'/{page}/', 'anchor': 'guide-sections'}, others)
        self.assertIn({'old_path': '/skills/', 'anchor': 'skill-sections'}, others)
        self.assertTrue(any(e['old_path'] == '/ui/' for e in others))
