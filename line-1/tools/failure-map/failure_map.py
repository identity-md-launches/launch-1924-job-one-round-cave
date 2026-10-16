#!/usr/bin/env python3
"""Classify one saved Endpoint Sentry report by its observed failure phase."""
import argparse
import json
import math
from pathlib import Path
import sys

SCHEMA = "failure-map/v1"
MAX_BYTES = 1048576
PHASES = {
    "dns": "name resolution",
    "tls": "TLS handshake",
    "connect": "TCP connection",
    "timeout": "deadline or read timeout",
    "headers": "HTTP response headers",
    "body": "HTTP response body",
    "json": "JSON validation",
    "json_pointer": "JSON expectation",
    "json_value": "JSON expectation",
}
WORKER_PHASES = {
    "deadline": "worker deadline",
    "worker_start": "worker start",
    "worker_protocol": "worker protocol",
    "arguments": "worker arguments",
}


def unique_object(pairs):
    value = {}
    for key, item in pairs:
        if key in value:
            raise ValueError("duplicate JSON key")
        value[key] = item
    return value


def nonfinite(_):
    raise ValueError("nonfinite JSON number")


def finite_float(text):
    value = float(text)
    if not math.isfinite(value):
        raise ValueError("JSON number exceeds finite float range")
    return value


def load(path):
    """Keep the wrapper: evidence paths must address the original document."""
    p = Path(path).resolve()
    cwd = Path.cwd().resolve()
    if not p.is_relative_to(cwd) or not p.is_file():
        raise ValueError("report must be a regular file inside the workspace")
    with p.open("rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("report exceeds 1 MiB")
    value = json.loads(data.decode("utf-8"), object_pairs_hook=unique_object,
                       parse_constant=nonfinite, parse_float=finite_float)
    validate(value)
    return value


def validate(value):
    if not isinstance(value, dict) or type(value.get("ok")) is not bool:
        raise ValueError("report requires boolean ok")
    schema = value.get("schema")
    if schema == "deadline-sentry/v1":
        if "probe" in value:
            probe = value["probe"]
            if not isinstance(probe, dict) or probe.get("schema") != "endpoint-sentry/v1":
                raise ValueError("invalid worker report")
            validate(probe)
            if value["ok"] != probe["ok"] or value.get("error") is not None:
                raise ValueError("contradictory wrapper")
        elif value["ok"] or not isinstance(value.get("error"), dict):
            raise ValueError("missing worker failure evidence")
        elif not isinstance(value["error"].get("kind"), str) or not value["error"]["kind"]:
            raise ValueError("missing worker error kind")
        return
    if schema != "endpoint-sentry/v1":
        raise ValueError("expected Endpoint Sentry or Deadline Sentry report")
    checks = value.get("checks", [])
    if not isinstance(checks, list) or len(checks) > 128:
        raise ValueError("invalid checks")
    for check in checks:
        if (not isinstance(check, dict) or type(check.get("ok")) is not bool
                or not isinstance(check.get("name"), str)):
            raise ValueError("invalid check")
    error = value.get("error")
    if error is not None and (not isinstance(error, dict)
                              or not isinstance(error.get("kind"), str) or not error["kind"]):
        raise ValueError("invalid error")
    if value["ok"] and (error is not None or any(c["ok"] is False for c in checks)):
        raise ValueError("success contradicts failure evidence")


def classify(report):
    validate(report)
    prefix = ""
    if report["schema"] == "deadline-sentry/v1":
        if "probe" not in report:
            kind = report["error"]["kind"]
            return {"schema": SCHEMA,
                    "outcome": "watchdog-failure" if kind == "deadline" else "worker-failure",
                    "phase": WORKER_PHASES.get(kind, "worker failure"),
                    "evidence": "/error/kind",
                    "reason": "The wrapper recorded a worker failure; no completed probe is available."}
        report = report["probe"]
        prefix = "/probe"
    if report["ok"]:
        return {"schema": SCHEMA, "outcome": "healthy-observation",
                "phase": "completed checks", "evidence": prefix + "/checks",
                "reason": "The captured probe passed its requested checks."}
    error = report.get("error")
    if isinstance(error, dict):
        kind = error["kind"]
        return {"schema": SCHEMA, "outcome": "failure-observed",
                "phase": PHASES.get(kind, kind), "evidence": prefix + "/error/kind",
                "reason": error.get("message", "recorded error")}
    # A captured status alone does not establish a failed status expectation.
    # Inspect explicit failed checks before considering any terminal-hop status.
    for index, check in enumerate(report.get("checks", [])):
        if check["ok"] is not False:
            continue
        result = {"schema": SCHEMA, "outcome": "check-failure",
                  "phase": PHASES.get(check["name"], check["name"]),
                  "evidence": prefix + "/checks/{}".format(index),
                  "reason": "A requested check failed after a response was captured."}
        if check["name"] == "status":
            result.update(outcome="http-failure", phase="HTTP status",
                          reason="The captured status did not satisfy the requested status check.")
            # The check's actual value is authoritative here, not an unrelated hop.
            actual = check.get("actual")
            if type(actual) is int and 100 <= actual <= 599:
                result["status"] = actual
        return result
    return {"schema": SCHEMA, "outcome": "insufficient-evidence", "phase": "unknown",
            "evidence": prefix or "/", "reason": "The report has no usable phase evidence."}


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    ap.add_argument("report")
    args = ap.parse_args(argv)
    try:
        result = classify(load(args.report))
    except (OSError, ValueError, UnicodeError, RecursionError):
        print(json.dumps({"schema": SCHEMA, "error": "Invalid report or workspace path."}))
        return 2
    print(json.dumps(result, indent=2, sort_keys=True, allow_nan=False))
    return 0 if result["outcome"] == "healthy-observation" else 1


if __name__ == "__main__":
    sys.exit(main())
