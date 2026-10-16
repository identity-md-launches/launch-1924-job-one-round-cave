"""Behavioral checks with all temporary fixtures under test/scratch/."""
import contextlib
import csv
import importlib.util
import io
import json
from pathlib import Path
import random
import tempfile
import unittest
from unittest.mock import patch


SOURCE = Path(__file__).resolve().with_name('multiplicity.py')
spec = importlib.util.spec_from_file_location('multiplicity', SOURCE)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class MultiplicityTests(unittest.TestCase):
    def setUp(self):
        root = Path('test/scratch')
        root.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=root)
        self.addCleanup(self.temp.cleanup)
        self.before = Path(self.temp.name) / 'before.csv'
        self.after = Path(self.temp.name) / 'after.csv'

    def write(self, path, rows):
        with path.open('w', encoding='utf-8', newline='') as stream:
            csv.writer(stream).writerows(rows)

    def compare(self, before, after, keys=('id',)):
        self.write(self.before, before)
        self.write(self.after, after)
        return m.compare(self.before, self.after, list(keys))

    def test_equal_duplicates_reordered_rows_and_headers(self):
        report = self.compare([['id', 'v'], ['a', '2'], ['a', '3'], ['a', '2']],
                              [['v', 'id'], ['2', 'a'], ['2', 'a'], ['3', 'a']])
        self.assertTrue(report['multiset_equal'])
        self.assertFalse(report['identity_matching'])
        self.assertEqual(report['summary']['retained_copies'], 3)
        self.assertEqual(report['summary']['duplicate_key_groups'], 1)
        variants = report['groups'][0]['variants']
        self.assertEqual(variants[0]['before_records'], [2, 4])
        self.assertEqual(variants[0]['after_records'], [2, 3])

    def test_multiplicity_surplus_does_not_choose_occurrences(self):
        report = self.compare([['id', 'v'], ['a', '2'], ['a', '2'], ['a', '2']],
                              [['id', 'v'], ['a', '2']])
        variant = report['groups'][0]['variants'][0]
        self.assertEqual((variant['retained_copies'], variant['before_surplus_copies'],
                          variant['after_surplus_copies']), (1, 2, 0))
        self.assertEqual(variant['before_records'], [2, 3, 4])
        self.assertNotIn('retained_records', variant)
        self.assertFalse(report['multiset_equal'])

    def test_conflicting_variants_are_surpluses_not_updates(self):
        report = self.compare([['id', 'v'], ['a', '2'], ['a', '3']],
                              [['id', 'v'], ['a', '3'], ['a', '4']])
        group = report['groups'][0]
        self.assertEqual((group['retained_copies'], group['before_surplus_copies'],
                          group['after_surplus_copies']), (1, 1, 1))
        variants = group['variants']
        self.assertEqual([v['values']['v'] for v in variants], ['2', '3', '4'])
        self.assertEqual([v['before_count'] for v in variants], [1, 1, 0])
        self.assertEqual([v['after_count'] for v in variants], [0, 1, 1])
        self.assertNotIn('changed', report)

    def test_one_sided_keys_and_header_only(self):
        report = self.compare([['id', 'v']], [['id', 'v'], ['a', '2'], ['a', '2']])
        self.assertEqual(report['summary']['after_surplus_copies'], 2)
        self.assertEqual(report['summary']['retained_copies'], 0)
        self.assertEqual(report['groups'][0]['before_count'], 0)
        report = m.compare(self.after, self.before, ['id'])
        self.assertEqual(report['summary']['before_surplus_copies'], 2)
        self.assertEqual(report['summary']['after_surplus_copies'], 0)
        report = self.compare([['id', 'v']], [['v', 'id']])
        self.assertTrue(report['multiset_equal'])
        self.assertEqual(report['groups'], [])

    def test_composite_keys_and_empty_components(self):
        rows = [['id', 'place', 'v'], ['a', 'x', '2'], ['a', '', '2'], ['a', '', '2']]
        report = self.compare(rows, rows, ('id', 'place'))
        self.assertTrue(report['multiset_equal'])
        self.assertEqual(report['summary']['key_groups'], 2)
        self.assertEqual(report['summary']['duplicate_key_groups'], 1)
        self.assertEqual(report['summary']['empty_key_groups'], 1)
        self.assertEqual(report['groups'][0]['empty_key_columns'], ['place'])

    def test_empty_singleton_is_flagged_even_when_equal(self):
        rows = [['id', 'v'], ['', '2']]
        report = self.compare(rows, rows)
        self.assertTrue(report['multiset_equal'])
        self.assertEqual(report['summary']['empty_key_groups'], 1)
        self.assertFalse(report['groups'][0]['duplicate_key'])

    def test_full_rows_not_independent_field_counts(self):
        report = self.compare([['id', 'x', 'y'], ['a', '1', '2'], ['a', '2', '1']],
                              [['id', 'x', 'y'], ['a', '1', '1'], ['a', '2', '2']])
        self.assertEqual(report['summary']['retained_copies'], 0)
        self.assertEqual(report['summary']['before_surplus_copies'], 2)
        self.assertEqual(report['summary']['after_surplus_copies'], 2)

    def test_exact_strings_have_no_normalization(self):
        report = self.compare([['id', 'v'], ['a', '01'], ['a', '1'], ['A', '1']],
                              [['id', 'v'], ['a', '1'], ['a', ' 1'], [' a', '1']])
        self.assertEqual(report['summary']['retained_copies'], 1)
        self.assertEqual(report['summary']['key_groups'], 3)
        self.assertEqual(report['summary']['before_surplus_copies'], 2)

    def test_multiline_bom_and_control_safe_text(self):
        rows = [['id', '\x1b[31m'], ['a', 'first\nsecond'], ['a', 'comma,quote"']]
        self.compare(rows, rows)
        self.before.write_bytes(b'\xef\xbb\xbf' + self.before.read_bytes())
        report = m.compare(self.before, self.after, ['id'])
        self.assertTrue(report['multiset_equal'])
        self.assertEqual(sorted(r for v in report['groups'][0]['variants']
                                for r in v['before_records']), [2, 3])
        text = m.render_text(report)
        self.assertNotIn('\x1b', text)
        self.assertIn('\\u001b', text)
        self.assertIn('first\\nsecond', text)

    def test_schema_mismatch_rejected_instead_of_projected(self):
        self.write(self.before, [['id', 'old'], ['a', '1']])
        self.write(self.after, [['id', 'new'], ['a', '1']])
        with self.assertRaisesRegex(ValueError, 'only in before:.*old.*only in after:.*new'):
            m.compare(self.before, self.after, ['id'])
        self.write(self.after, [['id', 'old', 'extra'], ['a', '1', '']])
        with self.assertRaisesRegex(ValueError, 'only in after:.*extra'):
            m.compare(self.before, self.after, ['id'])

    def test_invalid_keys_and_malformed_inputs(self):
        self.compare([['id'], ['a']], [['id'], ['a']])
        for keys in ([], [''], ['id', 'id'], ['missing']):
            with self.subTest(keys=keys), self.assertRaises(ValueError):
                m.compare(self.before, self.after, keys)
        for body in (b'id,id\na,a\n', b'id,v\na\n', b'id,v\n"unterminated',
                     b'id,\na,b\n', b'id,v\na,\xff\n'):
            self.before.write_bytes(body)
            with self.subTest(body=body), self.assertRaises(ValueError):
                m.compare(self.before, self.after, ['id'])

    def test_inherited_bounds_and_workspace_boundary(self):
        rows = [['id'], ['a'], ['b']]
        self.compare(rows, rows)
        with patch.object(m.engine, 'MAX_ROWS', 1), self.assertRaisesRegex(ValueError, 'data records'):
            m.compare(self.before, self.after, ['id'])
        with patch.object(m.engine, 'MAX_BYTES', 4), self.assertRaisesRegex(ValueError, 'bytes'):
            m.compare(self.before, self.after, ['id'])
        # The rejected path is never opened and need not exist.
        outside = Path.cwd().parent / 'csv-multiplicity-outside-not-opened.csv'
        with self.assertRaisesRegex(ValueError, 'inside the current working directory'):
            m.compare(outside, self.after, ['id'])

    def test_canonical_group_and_variant_order(self):
        rows = [['z', 'id', 'a'], ['3', 'b', '2'], ['2', 'a', '9'], ['1', 'a', '8']]
        report = self.compare(rows, rows)
        self.assertEqual(report['columns'], ['a', 'id', 'z'])
        self.assertEqual([g['key']['id'] for g in report['groups']], ['a', 'b'])
        self.assertEqual([v['values']['a'] for v in report['groups'][0]['variants']], ['8', '9'])
        self.assertEqual(report, m.compare(self.before, self.after, ['id']))

    def test_cli_statuses_formats_and_no_input_writes(self):
        rows = [['id', 'v'], ['a', '2'], ['a', '2']]
        self.compare(rows, rows)
        original_before = self.before.read_bytes()
        original_after = self.after.read_bytes()
        args = [str(self.before), str(self.after), '--key', 'id']
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(m.main(args), 0)
        self.assertTrue(json.loads(out.getvalue())['multiset_equal'])
        self.write(self.after, [['id', 'v'], ['a', '2']])
        changed_after = self.after.read_bytes()
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            self.assertEqual(m.main(args + ['--format', 'text']), 1)
        self.assertIn('No occurrences paired', out.getvalue())
        self.assertEqual(self.before.read_bytes(), original_before)
        self.assertEqual(self.after.read_bytes(), changed_after)
        self.after.write_bytes(original_after)
        out, err = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
            self.assertEqual(m.main(args + ['--key', 'missing']), 2)
        self.assertEqual(out.getvalue(), '')
        self.assertIn('error', json.loads(err.getvalue()))
        self.assertEqual(self.after.read_bytes(), original_after)

    def test_count_conservation_and_reverse_symmetry(self):
        # Independent small cases exercise multiplicity arithmetic across keys.
        rng = random.Random(737)
        choices = [(key, value) for key in ('', 'a', 'b') for value in ('1', '2', '3')]
        for _ in range(40):
            before = [rng.choice(choices) for _ in range(rng.randrange(20))]
            after = [rng.choice(choices) for _ in range(rng.randrange(20))]
            report = self.compare([['id', 'v']] + before, [['id', 'v']] + after)
            reverse = m.compare(self.after, self.before, ['id'])
            s, r = report['summary'], reverse['summary']
            retained = sum(min(before.count(row), after.count(row)) for row in set(before + after))
            self.assertEqual(s['retained_copies'], retained)
            self.assertEqual(s['retained_copies'] + s['before_surplus_copies'], len(before))
            self.assertEqual(s['retained_copies'] + s['after_surplus_copies'], len(after))
            self.assertEqual(s['before_surplus_copies'], r['after_surplus_copies'])
            self.assertEqual(s['after_surplus_copies'], r['before_surplus_copies'])
            self.assertEqual(s['retained_copies'], r['retained_copies'])


if __name__ == '__main__':
    unittest.main()
