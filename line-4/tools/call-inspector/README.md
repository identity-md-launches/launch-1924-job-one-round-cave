# Call Inspector

Identify a supplied Ethereum call from its four-byte selector and a local ABI,
then strictly decode its arguments. This standard-library Python tool works
entirely offline. It reuses the delivered Selector Audit's bounded ABI reader
and ABI Workbench's Keccak, canonical signatures, schema limits and decoder.
Keep those sibling folders with it; no package installation is needed.

Run this one command from the repository root:

```sh
python3 -B line-4/tools/call-inspector/call_inspector.py --abi line-4/tools/selector-audit/erc20.json --data 0xa9059cbb000000000000000000000000d782bdea4ef02a0bd391eb9089470c8080f0a68e000000000000000000000000000000000000000000000000000000000000000c
```

Tried locally: exit 0, status `decoded`, ABI index 0,
`transfer(address,uint256)`, address `0xd782bdea4ef02a0bd391eb9089470c8080f0a68e`
and amount 12. ZTO's real address is an argument in constructed bytes; this is
not a token transfer, deployed-token ABI claim, balance, or observed transaction.

For another ABI use `--abi PATH --data 0x...`; run from the workspace containing
that ABI. Paths must resolve within the current workspace. Output JSON includes
all matching ABI indices/signatures; successful arguments retain their names,
canonical types and JSON values (tuples/arrays are nested JSON arrays).
Unnamed arguments use the codec's `arg0`, `arg1`, etc. Output types and mutability
are not interpreted. Non-function entries are structurally checked and ignored.

Exit codes:

- **0:** exactly one ABI function matches, and its complete calldata is canonical.
- **1:** JSON evidence reports `short-calldata`, `unknown-selector`,
  `ambiguous-selector`, or `invalid-calldata`. No decoded arguments are emitted.
- **2:** invalid JSON/schema/hex, file error, unsupported input type, or a budget
  refusal. A concise error goes to stderr with no result JSON.

Duplicate canonical signatures and distinct-signature collisions both refuse
identification, even if only one candidate's payload happens to decode. A known
`burn(uint256)` / `collate_propagate_storage(bytes16)` collision is tested.
Every function input signature must be supported: skipping unknown signatures
could hide a collision. Unsupported unrelated inputs therefore refuse the
whole inventory. Use the Workbench's explicit `decode-call --function` command
when you intentionally select a known supported function instead.

Limits: 1 MiB ABI file, 1 MiB argument bytes plus a four-byte selector,
256 function entries, 8,192 characters per canonical signature, and the inherited
32 tuple levels, 4,096 type nodes, 256 parameters and 4,096 array items. Supported
inputs are the Workbench's scalars, scalar arrays and nested tuples; tuple arrays,
nested arrays, and dynamic-element arrays remain explicit refusals. Limits bound
data sizes, not exact elapsed time or process memory. Inputs must remain stable
while being read; path admission is not a concurrent filesystem security boundary.

Run the behavioral checks:

```sh
python3 -B -m unittest discover -s line-4/tools/call-inspector -v
```

Tried locally: all 12 tests passed. They cover known selectors, real collision
refusal before decoding, alias duplicates, overloads, independently laid-out
dynamic tuples, noncanonical/truncated/surplus bytes, invalid padding, empty
arguments, unknown/short calls, unsupported signatures, budgets, CLI exits and
reader errors. Temporary fixtures stay under `test/scratch/`.

A match describes only the supplied ABI. It cannot authenticate a chain,
contract, proxy implementation, selector registry or execution result. Unknown
selectors do not establish fallback behavior. This tool has no RPC, wallet,
key, environment-reading, signing, sending, payment or posting capability.
