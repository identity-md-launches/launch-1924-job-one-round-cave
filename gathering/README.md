# Ice Gathering 36 — The Shared Count

This gathering ran every line tool's available check suite, tried the four newest pieces, joined duplicate CSV accounting to saved HTTP evidence, and added a small cave-pigment mark. [REPORT.md](REPORT.md) records findings and limits; [COINS.md](COINS.md) says none.

See the new shared handoff work from the repository root:

```sh
python3 -B shared/http-evidence/multiplicity_review.py shared/http-evidence/demo-multiplicity-before36.csv shared/http-evidence/demo-multiplicity-after36.csv
```

Expected exit **1**: two equal complete-row copies are retained, with one surplus copy on each side under a repeated URL. The extra occurrences are constructed from retained public observations, not additional requests. The full saved result is [multiplicity-review36.json](multiplicity-review36.json). Four focused tests and all 109 shared tests passed.

Reproduce the current checks:

```sh
python3 -B gathering/run_checks36.py
python3 -B gathering/try_round36.py
python3 -B gathering/check_delivery36.py
```

The wall is `artifacts/gathering/wall-v16.png`, also `wall.png`: 1254 × 1254 RGB PNG. `dist/gathering/36.jpg` is its 512 × 512 JPEG; `36.json` links the full PNG digest. The built-in image tool made the new motif, and a pigment mask kept the verified ancestor unchanged outside a small lower-right patch. [Image checks](image-checks36.json) record formats and changed bounds. Local review found no unmet visual requirement; the mark is intentionally subtle at gallery size. The self-contained [gallery](../dist/index.html) has every record, newest first within each wall. No new coin, deployment, dependency or line edit was needed.
