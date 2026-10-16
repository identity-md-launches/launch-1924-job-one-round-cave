#!/usr/bin/env python3
"""Trace a local Python import lineage from bounded, unexecuted source."""

import argparse
import importlib.util
import json
from pathlib import Path
import sys


def load_route():
    """Load this line's delivered route tool, never the inspected project."""
    path = Path(__file__).resolve().parents[1] / 'import-route' / 'route.py'
    spec = importlib.util.spec_from_file_location('line3_lineage_route', path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def trace(root, start, target, limits=None):
    """Return complete source evidence for a shortest local-import lineage.

    An unknown endpoint raises ValueError. An absent path is reported only after
    a completed collection; parse issues and dynamic calls remain in the result.
    """
    route = load_route()
    budget = route.load_budget()
    scan = budget.scan(Path(root), limits)
    answer = route.explain(scan['map'], start, target)
    return dict(answer, status='complete', found=answer['reachable'],
                path=answer['import_path'] if answer['reachable'] else None,
                inventory=scan['inventory'], limits=scan['limits'],
                collection_scope=scan['scope'])


def lineage(root, start, target):
    """Keep the original path-only API for existing callers."""
    try:
        return trace(root, start, target)['path']
    except ValueError as exc:
        if str(exc).startswith('unknown local module:'):
            return None
        raise


def main(argv=None):
    route = load_route()
    budget = route.load_budget()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('root', type=Path, help='explicit import root inside the current workspace')
    parser.add_argument('start', help='exact dotted starting module')
    parser.add_argument('target', help='exact dotted destination module')
    parser.add_argument('--strict', action='store_true', help='fail if issues, cycles or dynamic calls remain')
    for name, value in budget.DEFAULTS.items():
        parser.add_argument('--max-' + name.replace('_', '-'), type=int,
                            default=value, dest=name)
    args = parser.parse_args(argv)
    try:
        result = trace(args.root, args.start, args.target,
                       {name: getattr(args, name) for name in budget.DEFAULTS})
    except (OSError, ValueError, RuntimeError, RecursionError) as exc:
        error = (exc.evidence if isinstance(getattr(exc, 'evidence', None), dict) else
                 {'type': 'scan_error', 'detail': str(exc)})
        print(json.dumps({'status': 'refused', 'error': error}, indent=2))
        return 2
    print(json.dumps(result, indent=2, ensure_ascii=False))
    warnings = result['issues'] or result['cycles'] or result['dynamic_imports']
    return int(not result['found'] or bool(args.strict and warnings))


if __name__ == '__main__':
    sys.exit(main())
