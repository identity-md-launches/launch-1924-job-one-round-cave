"""Repeated captured rows are counted without assigning identity to copies."""
import contextlib
import csv
import io
import json
from pathlib import Path
import tempfile
import unittest

import http_evidence
import multiplicity_review as tool


SOURCE = Path(__file__).with_name('observed-report.json')


class MultiplicityReviewTests(unittest.TestCase):
    def setUp(self):
        root = Path('test/scratch')
        root.mkdir(parents=True, exist_ok=True)
        self.tmp = tempfile.TemporaryDirectory(dir=root)
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def save(self, name, text):
        path = self.root / name
        path.write_text(text)
        return path

    def csv_rows(self, *rows):
        out = io.StringIO(newline='')
        writer = csv.DictWriter(out, fieldnames=http_evidence.COLUMNS, lineterminator='\n')
        writer.writeheader()
        writer.writerows(rows)
        return out.getvalue()

    def source_row(self, at=None):
        text = http_evidence.snapshot(SOURCE, True, at)
        return next(csv.DictReader(io.StringIO(text)))

    def test_repeated_real_source_rows_have_explicit_surplus(self):
        recent = self.source_row()
        stale = self.source_row('2026-10-15T19:03:45Z')
        before = self.save('before.csv', self.csv_rows(recent, recent, stale))
        after = self.save('after.csv', self.csv_rows(recent, stale, stale))
        result = tool.review(before, after)['comparison']
        self.assertEqual(result['summary']['retained_copies'], 2)
        self.assertEqual(result['summary']['before_surplus_copies'], 1)
        self.assertEqual(result['summary']['after_surplus_copies'], 1)
        self.assertEqual(result['summary']['duplicate_key_groups'], 1)
        self.assertFalse(result['identity_matching'])
        self.assertEqual(result['groups'][0]['before_count'], 3)
        self.assertEqual(result['groups'][0]['after_count'], 3)
        self.assertEqual(result['groups'][0]['variants'][0]['before_records'], [2, 3])

    def test_equal_copies_and_cli_exit_codes(self):
        recent = self.source_row()
        a = self.save('a.csv', self.csv_rows(recent, recent))
        b = self.save('b.csv', self.csv_rows(recent))
        with contextlib.redirect_stdout(io.StringIO()):
            self.assertEqual(tool.main([str(a), str(a)]), 0)
            self.assertEqual(tool.main([str(a), str(b)]), 1)

    def test_wrong_schema_and_empty_url_refuse_without_output(self):
        good = self.save('good.csv', self.csv_rows(self.source_row()))
        for bad in ('url\nhttps://api.imd.fun/launches\n',
                    self.csv_rows({**self.source_row(), 'url': ''})):
            path = self.save('bad.csv', bad)
            stdout, stderr = io.StringIO(), io.StringIO()
            with contextlib.redirect_stdout(stdout), contextlib.redirect_stderr(stderr):
                self.assertEqual(tool.main([str(good), str(path)]), 2)
            self.assertEqual(stdout.getvalue(), '')
            self.assertEqual(json.loads(stderr.getvalue())['error'],
                             'Invalid workspace HTTP evidence CSV.')

    def test_bounded_reader_and_workspace_path(self):
        good = self.save('good.csv', self.csv_rows(self.source_row()))
        with self.assertRaises(ValueError):
            tool.review(good, '/outside-workspace/not-opened.csv')


if __name__ == '__main__':
    unittest.main()
