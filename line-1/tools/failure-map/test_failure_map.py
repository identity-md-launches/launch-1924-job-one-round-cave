"""Regression tests use saved reports or explicitly synthetic workspace fixtures."""
import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location("failure_map", HERE / "failure_map.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def probe(ok=False, checks=None, **fields):
    return dict(schema="endpoint-sentry/v1", ok=ok,
                checks=[] if checks is None else checks, **fields)


class FailureMapTests(unittest.TestCase):
    def setUp(self):
        scratch = ROOT / "test" / "scratch"
        scratch.mkdir(parents=True, exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(dir=scratch)
        self.addCleanup(self.temp.cleanup)
        self.folder = Path(self.temp.name)

    def cli(self, source=None, raw=None):
        path = self.folder / "report.json"
        path.write_text(json.dumps(source) if raw is None else raw, encoding="utf-8")
        result = subprocess.run([sys.executable, "-I", "-B", str(HERE / "failure_map.py"), str(path)],
                                cwd=ROOT, capture_output=True, text=True, timeout=5)
        self.assertEqual(result.stderr, "")
        return result.returncode, json.loads(result.stdout)

    def test_transport(self):
        for kind, phase in m.PHASES.items():
            with self.subTest(kind=kind):
                result = m.classify(probe(error={"kind": kind, "message": "synthetic failure"}))
                self.assertEqual((result["outcome"], result["phase"]), ("failure-observed", phase))

    def test_http_status_requires_failed_status_check(self):
        code, result = self.cli(probe(hops=[{"status": 503}], checks=[
            {"name": "status", "ok": False, "actual": 503, "expected": 200}]))
        self.assertEqual(code, 1)
        self.assertEqual((result["outcome"], result["status"], result["evidence"]),
                         ("http-failure", 503, "/checks/0"))

    def test_200_json_value_failure_cli(self):
        """Gathering 35: HTTP 200 must not mask a JSON expectation mismatch."""
        source = probe(hops=[{"status": 200}], checks=[
            {"name": "status", "ok": True, "actual": 200},
            {"name": "json", "ok": True},
            {"name": "json_value", "ok": False, "path": "/state"}])
        code, result = self.cli(source)
        self.assertEqual(code, 1)
        self.assertEqual((result["outcome"], result["phase"], result["evidence"]),
                         ("check-failure", "JSON expectation", "/checks/2"))
        self.assertNotIn("status", result)

    def test_watchdog_failure_cli(self):
        """Gathering 35: exercise load AND classify through the real CLI."""
        source = {"schema": "deadline-sentry/v1", "ok": False,
                  "error": {"kind": "deadline", "message": "synthetic expired budget"}}
        code, result = self.cli(source)
        self.assertEqual((code, result["outcome"], result["phase"], result["evidence"]),
                         (1, "watchdog-failure", "worker deadline", "/error/kind"))

    def test_other_worker_failures_are_not_deadlines(self):
        for kind in ("worker_start", "worker_protocol", "arguments", "unrecognized"):
            code, result = self.cli({"schema": "deadline-sentry/v1", "ok": False,
                                     "error": {"kind": kind}})
            self.assertEqual((code, result["outcome"]), (1, "worker-failure"))
            self.assertNotEqual(result["phase"], "worker deadline")

    def test_wrapper_evidence_addresses_original_source(self):
        cases = [probe(ok=True), probe(error={"kind": "tls"}),
                 probe(checks=[{"name": "json_value", "ok": False}]),
                 probe(checks=[{"name": "status", "ok": False, "actual": 404}])]
        for inner in cases:
            source = {"schema": "deadline-sentry/v1", "ok": inner["ok"], "probe": inner}
            before = copy.deepcopy(source)
            code, result = self.cli(source)
            pointer = result["evidence"]
            self.assertTrue(pointer.startswith("/probe/"))
            target = source
            for key in pointer[1:].split("/"):
                target = target[int(key)] if isinstance(target, list) else target[key]
            self.assertEqual(code, 0 if inner["ok"] else 1)
            self.assertEqual(source, before)

    def test_hop_alone_is_not_status_failure(self):
        for status in (200, 404, 503, True):
            result = m.classify(probe(hops=[{"status": status}]))
            self.assertEqual(result["outcome"], "insufficient-evidence")

    def test_accepted_non200_success(self):
        code, result = self.cli(probe(ok=True, hops=[{"status": 404}], checks=[
            {"name": "status", "ok": True, "expected": 404, "actual": 404}]))
        self.assertEqual((code, result["outcome"]), (0, "healthy-observation"))

    def test_error_after_status_check_retains_recorded_phase(self):
        result = m.classify(probe(hops=[{"status": 200}], checks=[{"name": "status", "ok": True}],
                                  error={"kind": "json_pointer"}))
        self.assertEqual((result["phase"], result["evidence"]), ("JSON expectation", "/error/kind"))

    def test_unavailable_actual_status_is_not_inferred(self):
        result = m.classify(probe(hops=[{"status": 200}],
                                  checks=[{"name": "status", "ok": False}]))
        self.assertEqual(result["outcome"], "http-failure")
        self.assertNotIn("status", result)

    def test_invalid_wrappers_and_contradictory_success(self):
        sources = [
            {"schema": "deadline-sentry/v1", "ok": False},
            {"schema": "deadline-sentry/v1", "ok": True, "error": {"kind": "deadline"}},
            {"schema": "deadline-sentry/v1", "ok": False, "probe": None},
            {"schema": "deadline-sentry/v1", "ok": False, "probe": probe(ok=True)},
            {"schema": "deadline-sentry/v1", "ok": True, "probe": probe(ok=True), "error": {"kind": "deadline"}},
            probe(ok=True, error={"kind": "tls"}),
            probe(ok=True, checks=[{"name": "status", "ok": False}]),
            probe(checks=[{"name": "status", "ok": 0}]),
            probe(error={"kind": None}),
            {"schema": "endpoint-sentry/v1", "ok": 0},
            [], {},
        ]
        for source in sources:
            with self.subTest(source=source):
                code, result = self.cli(source)
                self.assertEqual(code, 2)
                self.assertIn("error", result)

    def test_strict_json_and_byte_limit(self):
        for raw in ('{"schema":"endpoint-sentry/v1","ok":false,"ok":true}',
                    '{"schema":"endpoint-sentry/v1","ok":true,"x":NaN}',
                    '{"schema":"endpoint-sentry/v1","ok":true,"x":Infinity}',
                    '{"schema":"endpoint-sentry/v1","ok":true,"x":1e9999}',
                    '[]', '{', ' ' * (m.MAX_BYTES + 1)):
            code, _ = self.cli(raw=raw)
            self.assertEqual(code, 2)

    def test_workspace_escape_rejected_before_read(self):
        # A lexical escape exercises containment without reading an external file.
        with self.assertRaises(ValueError):
            m.load(ROOT.parent / "outside-workspace.json")
        with self.assertRaises(ValueError):
            m.load(self.folder)
        link = self.folder / "escape.json"
        link.symlink_to(ROOT.parent / "outside-workspace.json")
        with self.assertRaises(ValueError):
            m.load(link)

    def test_real_retained_swarm_reports(self):
        expected = [("live-failure.json", "http-failure"), ("live-success.json", "healthy-observation")]
        for filename, outcome in expected:
            source = m.load(HERE.parent / "endpoint-sentry" / filename)
            self.assertEqual(m.classify(source)["outcome"], outcome)


if __name__ == "__main__":
    unittest.main()
