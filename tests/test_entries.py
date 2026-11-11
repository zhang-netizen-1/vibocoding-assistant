from collections import Counter
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parent.parent
SPEC = importlib.util.spec_from_file_location('entries', ROOT / 'site-src/entries.py')
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class EntriesTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.entries = MODULE.load_entries()
        cls.raw = {e['anchor']: e for e in MODULE.source_entries()}
        cls.tax = MODULE.taxonomy()

    def test_counts_and_unique_slugs(self):
        self.assertEqual(len(self.entries), 192)
        self.assertEqual(Counter(e['column'] for e in self.entries),
                         {'basics': 17, 'components': 75, 'interactions': 84, 'scenarios': 6, 'ai': 10})
        for c in self.tax['columns']:
            for g in c['groups']:
                self.assertEqual(sum(e['column'] == c['slug'] and e['group'] == g['slug'] for e in self.entries), g['expected'])
        self.assertEqual(len({(e['column'], e['slug']) for e in self.entries}), 192)
        for e in self.entries:
            for field in ('slug', 'zh', 'prompt', 'demo'):
                self.assertTrue(e[field], (e['old_anchors'], field))
        self.assertEqual(next(e['slug'] for e in self.entries if 'g-data-table' in e['old_anchors']), 'sortable-table')

    def test_every_frozen_anchor_maps_once(self):
        frozen = json.loads((ROOT / 'tests/fixtures/old_anchors.json').read_text())['entries']
        self.assertEqual(Counter(a for e in self.entries for a in e['old_anchors']), Counter(e['anchor'] for e in frozen))
        for old, target in self.tax['merges'].items():
            e = next(e for e in self.entries if target in e['old_anchors'])
            self.assertEqual(e['old_anchors'], [target, old])
            self.assertEqual(e.get('prompt_original', e['prompt']), self.raw[target]['prompt'])
            self.assertEqual(e['demo']['secondary'], self.raw[old]['demo'])
            self.assertEqual(e['prompt_secondary'], self.raw[old]['prompt'])

    def test_source_copy_and_optional_fields_preserved(self):
        for e in self.entries:
            if not e['old_anchors']:
                self.assertEqual(e['source']['path'], 'site-src/token_entries.py')
                self.assertEqual(e['demo']['kind'], 'token')
                continue
            raw = self.raw[e['old_anchors'][0]]
            for field in ('zh', 'en', 'definition'):
                self.assertEqual(e[field], raw[field], (e['slug'], field))
            expected_terms = raw['terms'] + ''.join(' ' + self.raw[a]['terms'] for a in e['old_anchors'][1:])
            self.assertEqual(e['terms'], expected_terms)
            editorial = MODULE.load_content().get(e['column']+'/'+e['slug'])
            if editorial:
                self.assertEqual(e['prompt_original'], raw['prompt'])
                self.assertEqual(e['prompt'], editorial['prompt_edit'])
                for field, value in editorial.items():
                    self.assertEqual(e[field], value)
            else:
                self.assertEqual(e['prompt'], raw['prompt'])
                self.assertEqual(e['acceptance'], raw['acceptance'])
                self.assertNotIn('prompt_new', e)
                self.assertEqual(e.get('when_use'), raw.get('when_use'))
                self.assertEqual(e.get('when_avoid'), raw.get('when_avoid'))
                if raw['source']['old_path'] == '/ui/':
                    self.assertEqual(e['acceptance'], [])
        self.assertEqual(sum('bench' in e for e in self.entries), 3)
        for pair in self.tax['component_motion']:
            self.assertIn(pair['component'], self.raw)
            self.assertIn(pair['motion'], self.raw)
            self.assertEqual(self.tax['anchors'][pair['component']]['column'], 'components')
            self.assertEqual(self.tax['anchors'][pair['motion']]['column'], 'interactions')

    def test_validation_rejects_duplicate_slug_and_count_drift(self):
        import copy
        broken = copy.deepcopy(self.entries)
        broken[1]['slug'] = broken[0]['slug']
        with self.assertRaisesRegex(ValueError, 'Duplicate slug'):
            MODULE.validate(broken, self.tax)
        with self.assertRaises(ValueError):
            MODULE.validate(self.entries[:-1], self.tax)
