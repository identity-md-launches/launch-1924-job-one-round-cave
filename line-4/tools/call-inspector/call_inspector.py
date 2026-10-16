#!/usr/bin/env python3
"""Identify and strictly decode supplied calldata against a bounded offline ABI."""
import argparse
import importlib.util
import json
from pathlib import Path
import sys

SOURCE = Path(__file__).resolve().parents[1] / 'selector-audit' / 'selector_audit.py'
spec = importlib.util.spec_from_file_location('line4_selector_inventory', SOURCE)
inventory = importlib.util.module_from_spec(spec)
spec.loader.exec_module(inventory)
codec = inventory.abi
MAX_FUNCTIONS = 256


def inspect_call(entries, data):
    """Never resolve a selector collision by whether one payload happens to decode."""
    codec.validate_abi(entries)
    if not isinstance(data, bytes):
        raise ValueError('calldata must be bytes')
    codec.check_budget(max(0, len(data) - 4), 'calldata')
    functions = [(i, entry) for i, entry in enumerate(entries)
                 if entry['type'] == 'function']
    if len(functions) > MAX_FUNCTIONS:
        raise ValueError(f'ABI exceeds {MAX_FUNCTIONS} function entries')
    # Admit every input schema before reporting a unique match. Skipping an
    # unsupported signature could conceal another function with this selector.
    rows = []
    for index, entry in functions:
        try:
            signature = codec.input_signature(entry)
        except ValueError as exc:
            raise ValueError(f'cannot inventory function at ABI index {index}: {exc}') from exc
        if len(signature) > codec.MAX_FUNCTION_REFERENCE:
            raise ValueError('canonical signature exceeds 8192 characters')
        rows.append((index, entry, signature,
                     codec.keccak256(signature.encode('ascii'))[:4]))
    result = {'schema': 'call-inspector/v1', 'calldata_bytes': len(data),
              'function_count': len(functions), 'selector': None,
              'status': 'short-calldata', 'candidates': []}
    if len(data) < 4:
        return result
    result['selector'] = '0x' + data[:4].hex()
    matches = [row for row in rows if row[3] == data[:4]]
    result['candidates'] = [{'abi_index': index, 'signature': signature}
                            for index, _, signature, _ in matches]
    if not matches:
        result['status'] = 'unknown-selector'
    elif len(matches) > 1:
        result['status'] = 'ambiguous-selector'
        result['ambiguity'] = ('duplicate' if len({r[2] for r in matches}) == 1
                               else 'collision')
    else:
        index, entry, signature, _ = matches[0]
        try:
            values = codec.decode_call(entry, signature, data)
        except ValueError as exc:
            result.update(status='invalid-calldata', error=str(exc))
        else:
            result.update(status='decoded', signature=signature, abi_index=index,
                          arguments=values)
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--abi', required=True, help='workspace-contained JSON ABI')
    parser.add_argument('--data', required=True, help='0x-prefixed complete calldata')
    args = parser.parse_args()
    try:
        data = codec.parse_data(args.data, call=True)
        result = inspect_call(inventory.read_abi(args.abi), data)
    except (ValueError, OSError) as exc:
        print(f'error: {exc}', file=sys.stderr)
        return 2
    print(json.dumps(result, indent=2))
    return 0 if result['status'] == 'decoded' else 1


if __name__ == '__main__':
    raise SystemExit(main())
