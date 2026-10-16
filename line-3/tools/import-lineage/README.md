# Import Lineage

Trace a shortest path between two local Python modules without importing or
executing the inspected project. The tool uses this line's delivered Import
Budget, Import Map and Import Route. Keep those sibling folders with it. Python
3.10+ and the standard library suffice.

From the repository root, run this one command:

```sh
python3 -B line-3/tools/import-lineage/lineage.py line-3/tools/import-lineage/examples app service
```

Tried here: it exited 0 and reported `found: true`, `path: ["app", "service"]`,
distance one, and `app.py:1` as the site of `from service import run`. This
repairs the missed symbol-import case in Gathering 35. The example now uses a
valid explicit import root. The original `lineage(root, start, target)` API
still returns a path or `None` for existing callers.

The JSON includes source sites, map issues, cycles, dynamic import call lines,
and a SHA-256 manifest of every admitted source file. A completed missing route
exits 1 and has `found: false`; an unknown module, invalid root, read error or
exceeded budget exits 2 with `status: refused` and no partial path. `--strict`
also exits 1 for any map issue, cycle or dynamic call. Limits default to 1,000
files, 262,144 bytes per file, 8,388,608 total bytes, 20,000 directory entries
and depth 64; use the corresponding `--max-*` options to change them.

Checks run with:

```sh
python3 -B -m unittest discover -s line-3/tools/import-lineage -v
```

Tried here: five tests passed. They cover the reported symbol import, package
initializer relative import, visible parse failure, refusal at a file budget,
unknown endpoints and a source execution trap. Inspected source was never run.

A source-only trial on `line-1/tools/deadline-sentry` found the real local edge
`test_deadline_sentry -> deadline_sentry` at line 10, with two admitted files,
one local edge and no issues or cycles. It did not execute that worker.

This is an explicit static local-import graph. Conditional imports may never
execute, and dynamic imports, external packages, implicit package initialization
and runtime path changes are not simulated. Parse issues can hide links. A
missing static route does not prove runtime isolation. Input limits bound source
collection, not parser CPU, memory or elapsed time. Use a stable source tree
inside the current workspace.
