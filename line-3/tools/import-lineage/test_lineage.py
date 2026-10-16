"""Behavioral checks for bounded, source-only import lineage."""
import contextlib
import importlib.util
import io
import json
from pathlib import Path
import tempfile
import unittest


HERE = Path(__file__).resolve().parent
WORKSPACE = HERE.parents[2]
spec = importlib.util.spec_from_file_location('line3_lineage_under_test', HERE / 'lineage.py')
tool = importlib.util.module_from_spec(spec)
spec.loader.exec_module(tool)


class LineageChecks(unittest.TestCase):
    def setUp(self):
        scratch = WORKSPACE / 'test' / 'scratch'
        scratch.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def source(self, name, body):
        path = self.root / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(body, encoding='utf-8')

    def test_symbol_import_is_local_edge_with_source_line(self):
        self.source('app.py', 'from service import run\n')
        self.source('service.py', 'def run(): pass\n')
        result = tool.trace(self.root, 'app', 'service')
        self.assertEqual(result['path'], ['app', 'service'])
        self.assertEqual(result['edges'][0]['sites'],
                         [{'path': 'app.py', 'line': 1, 'target': 'service import run'}])
        self.assertEqual(tool.lineage(self.root, 'app', 'service'), ['app', 'service'])
        self.assertEqual(len(result['inventory']['manifest']), 2)

    def test_package_initializer_relative_import(self):
        self.source('pkg/__init__.py', 'from . import helper\n')
        self.source('pkg/helper.py', 'pass\n')
        self.assertEqual(tool.trace(self.root, 'pkg', 'pkg.helper')['path'],
                         ['pkg', 'pkg.helper'])

    def test_parse_error_is_visible_alongside_valid_route(self):
        self.source('app.py', 'import service\n')
        self.source('service.py', 'pass\n')
        self.source('broken.py', 'def (\n')
        result = tool.trace(self.root, 'app', 'service')
        self.assertTrue(result['found'])
        self.assertEqual(result['issues'][0]['type'], 'parse_error')
        with contextlib.redirect_stdout(io.StringIO()) as output:
            code = tool.main([str(self.root), 'app', 'service', '--strict'])
        self.assertEqual(code, 1)
        self.assertEqual(json.loads(output.getvalue())['issues'][0]['type'], 'parse_error')

    def test_budget_refuses_before_route(self):
        self.source('app.py', 'import service\n')
        self.source('service.py', 'pass\n')
        with contextlib.redirect_stdout(io.StringIO()) as output:
            code = tool.main([str(self.root), 'app', 'service', '--max-files', '1'])
        self.assertEqual(code, 2)
        result = json.loads(output.getvalue())
        self.assertEqual(result['status'], 'refused')
        self.assertEqual(result['error']['budget'], 'files')
        self.assertNotIn('path', result)

    def test_no_source_execution_and_unknown_endpoints_refused(self):
        marker = self.root / 'should_not_exist'
        self.source('app.py', 'import service\nopen(' + repr(str(marker)) + ', "w")\n')
        self.source('service.py', 'pass\n')
        self.assertTrue(tool.trace(self.root, 'app', 'service')['found'])
        self.assertFalse(marker.exists())
        with self.assertRaisesRegex(ValueError, 'unknown local module'):
            tool.trace(self.root, 'app', 'missing')
        self.assertIsNone(tool.lineage(self.root, 'app', 'missing'))


if __name__ == '__main__':
    unittest.main()
