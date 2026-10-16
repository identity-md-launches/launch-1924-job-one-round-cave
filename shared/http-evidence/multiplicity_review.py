#!/usr/bin/env python3
"""Review repeated HTTP evidence exports as exact row multisets by URL."""
import argparse
import json
import sys

import http_evidence
import multiplicity
import reconcile


def review(before, after):
    for path in (before, after):
        header, groups, _ = reconcile.load_table(path, ['url'])
        if set(header) != set(http_evidence.COLUMNS) or len(header) != len(http_evidence.COLUMNS):
            raise ValueError('expected the HTTP evidence export columns')
        if any(not key[0] for key in groups):
            raise ValueError('HTTP evidence rows require nonempty URLs')
    result = multiplicity.compare(before, after, ['url'])
    return {'schema': 'http-evidence-multiplicity/v1',
            'source_schema': 'http-evidence CSV',
            'comparison': result,
            'caution': ('Retained copies count equal row values. They do not identify '
                        'physical probe occurrences, establish uptime, or pair changes.')}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    parser.add_argument('before')
    parser.add_argument('after')
    args = parser.parse_args(argv)
    try:
        result = review(args.before, args.after)
    except (OSError, ValueError):
        print(json.dumps({'error': 'Invalid workspace HTTP evidence CSV.'}), file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=True, sort_keys=True, indent=2))
    return 0 if result['comparison']['multiset_equal'] else 1


if __name__ == '__main__':
    sys.exit(main())
