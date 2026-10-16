import contextlib
import io
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
import call_inspector as tool


def fn(name, *types):
    return {'type': 'function', 'name': name,
            'inputs': [{'type': t} for t in types]}


def word(n):
    return n.to_bytes(32, 'big')


class InspectorTests(unittest.TestCase):
    def test_known_transfer_and_real_zto_argument(self):
        zto = 'd782bdea4ef02a0bd391eb9089470c8080f0a68e'
        entry = fn('transfer', 'address', 'uint')
        entry['inputs'][0]['name'] = 'recipient'
        result = tool.inspect_call([fn('balanceOf', 'address'), entry],
            bytes.fromhex('a9059cbb' + '0'*24 + zto) + word(12))
        self.assertEqual(result['status'], 'decoded')
        self.assertEqual(result['signature'], 'transfer(address,uint256)')
        self.assertEqual(result['abi_index'], 1)
        self.assertEqual(result['arguments'][0],
            {'name': 'recipient', 'type': 'address', 'value': '0x'+zto})
        self.assertEqual(result['arguments'][1]['value'], 12)

    def test_real_collision_refused_even_if_only_one_payload_valid(self):
        entries = [fn('burn', 'uint256'), fn('collate_propagate_storage', 'bytes16')]
        result = tool.inspect_call(entries, bytes.fromhex('42966c68') + word(1))
        self.assertEqual(result['status'], 'ambiguous-selector')
        self.assertEqual(result['ambiguity'], 'collision')
        self.assertEqual(len(result['candidates']), 2)
        self.assertNotIn('arguments', result)

    def test_alias_duplicate_is_ambiguous(self):
        entry = fn('burn', 'uint')
        result = tool.inspect_call([entry, fn('burn', 'uint256')],
                                  bytes.fromhex('42966c68') + word(1))
        self.assertEqual(result['ambiguity'], 'duplicate')

    def test_unknown_and_short_include_no_arguments(self):
        for data, status in [(b'', 'short-calldata'), (b'\x01'*3, 'short-calldata'),
                             (b'\xff'*4, 'unknown-selector')]:
            result = tool.inspect_call([fn('burn', 'uint')], data)
            self.assertEqual(result['status'], status)
            self.assertNotIn('arguments', result)

    def test_truncated_surplus_and_invalid_scalar(self):
        entry = fn('transfer', 'address', 'uint')
        selector = bytes.fromhex('a9059cbb')
        for payload in [b'', word(1), word(1)*3, word(1<<160)+word(1)]:
            self.assertEqual(tool.inspect_call([entry], selector+payload)['status'],
                             'invalid-calldata')

    def test_dynamic_tuple_and_noncanonical_tail(self):
        entry = fn('put')
        entry['inputs'] = [{'type': 'tuple', 'components':
                            [{'type': 'uint'}, {'type': 'string'}]}]
        # Known put((uint256,string)) selector and independently laid out bytes.
        selector = bytes.fromhex('58b31d65')
        payload = word(32)+word(7)+word(64)+word(2)+b'hi'+b'\0'*30
        result = tool.inspect_call([entry], selector+payload)
        self.assertEqual(result['arguments'][0]['value'], [7, 'hi'])
        displaced = word(64)+word(0)+payload[32:]
        self.assertEqual(tool.inspect_call([entry], selector+displaced)['status'],
                         'invalid-calldata')

    def test_zero_arguments_ignore_uninterpreted_outputs_and_events(self):
        entry = fn('totalSupply')
        entry['outputs'] = [{'type': 'tuple[]'}]
        result = tool.inspect_call([{'type':'event', 'name':'Transfer'}, entry],
                                  bytes.fromhex('18160ddd'))
        self.assertEqual(result['status'], 'decoded')
        self.assertEqual(result['arguments'], [])

    def test_overloads_selected_by_selector(self):
        result = tool.inspect_call([fn('burn', 'address'), fn('burn', 'uint256')],
                                  bytes.fromhex('42966c68')+word(12))
        self.assertEqual(result['status'], 'decoded')
        self.assertEqual(result['signature'], 'burn(uint256)')

    def test_unsupported_sibling_fails_closed(self):
        with self.assertRaisesRegex(ValueError, 'cannot inventory function at ABI index 1'):
            tool.inspect_call([fn('burn', 'uint'), fn('other', 'bytes[]')],
                              bytes.fromhex('42966c68')+word(1))

    def test_function_signature_and_data_budgets(self):
        with self.assertRaisesRegex(ValueError, '256 function'):
            tool.inspect_call([fn('f')]*257, b'')
        with self.assertRaisesRegex(ValueError, '8192 characters'):
            tool.inspect_call([fn('f'*8193)], b'')
        with self.assertRaisesRegex(ValueError, 'byte ABI budget'):
            tool.inspect_call([], b'\0'*(tool.codec.MAX_DATA_BYTES+5))

    def test_cli_exit_codes_and_no_tracebacks(self):
        with tempfile.TemporaryDirectory(dir='test/scratch') as tmp:
            path = Path(tmp)/'abi.json'
            path.write_text(json.dumps([fn('burn', 'uint')]))
            for data, status in [('0x42966c68'+'0'*63+'1', 0),
                                 ('0xffffffff', 1), ('0x1', 2)]:
                out, err = io.StringIO(), io.StringIO()
                with patch('sys.argv', ['inspector','--abi',str(path),'--data',data]), \
                     contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
                    self.assertEqual(tool.main(), status)
                if status == 2:
                    self.assertEqual(out.getvalue(), '')
                    self.assertTrue(err.getvalue().startswith('error:'))
                else:
                    self.assertEqual(err.getvalue(), '')
                    self.assertIn('status', json.loads(out.getvalue()))
            path.write_text('[{"type":"function","name":"f","name":"g"}]')
            with self.assertRaisesRegex(ValueError, 'duplicate JSON field'):
                tool.inventory.read_abi(path)

    def test_reader_missing_and_outside_workspace(self):
        with self.assertRaises(OSError):
            tool.inventory.read_abi('test/scratch/no-such-abi.json')
        with self.assertRaisesRegex(ValueError, 'inside the current workspace'):
            tool.inventory.read_abi('../outside.json')


if __name__ == '__main__':
    unittest.main()
