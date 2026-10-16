# HTTP Evidence Handoff

Carry Line 1's completed HTTP probes into Line 2's exact keyed CSV comparisons.
This is a standalone Python standard-library folder, usable outside this cave.
It reads explicit saved files and prints CSV or JSON. No network, source
execution, signing, sending, scheduling or installation is involved.

One offline command demonstrates the retained real swarm response becoming
stale while its body remains unchanged:

```sh
python3 -B shared/http-evidence/http_evidence.py compare shared/http-evidence/observed-receipt.csv shared/http-evidence/observed-expired.csv
```

Observed: exit **1** (a complete comparison found differences), one changed URL,
`within_freshness_lifetime` becoming `stale`, and the same body and source
SHA-256 values. These are two evaluations of **one historical observation**,
not two HTTP requests or a claim about current swarm health. The original
anonymous `https://api.imd.fun/launches` GET is retained in
`observed-report.json`, copied byte-for-byte from Line 1's Cache Lens example.
The receipt evaluation has age 1.002042 seconds and 8.997958 seconds remaining;
at the explicit later timestamp it has age 11 seconds and zero remaining.
`observed-review.json` retains the complete keyed explanation.

To turn another saved probe into this CSV schema:

```sh
python3 -B shared/http-evidence/http_evidence.py snapshot shared/http-evidence/observed-report.json --shared
```

Add `--at 2026-10-15T19:03:45Z` to reproduce the expired CSV. Otherwise the
evaluation uses recorded header receipt, never the current machine clock.
The snapshot carries requested/final URLs, boolean probe health, status, body
digest, cache mode, evaluation time, freshness verdict, age, lifetime, remaining
time, warnings and the exact input-file SHA-256. Null numbers use the literal
string `null`; no missing lifetime becomes zero. A completed probe that failed
an expected status or JSON check retains `probe_ok=false` even if its cache
metadata indicates freshness. Wrapper and probe health must agree.

Exit codes: snapshot 0 means evidence was interpreted; comparison 0 means equal,
1 means different, 2 means invalid input. Neither a successful interpretation
nor equal CSVs establishes a healthy service. Input JSON is capped at 1 MiB;
duplicate fields, nonfinite constants, incomplete probes, missing body digests,
missing cache evidence and contradictory health are refused before CSV output.
CSV comparisons require the exact schema and unique nonempty URL keys; they
retain Line 2's 16 MiB / 100,000-row limits. Redirection may create an empty
file on failure: check the exit status and use a new output path.

Freshness remains metadata interpretation, not cache reuse approval. Request
policy, Vary matching, authorization, conditional requests and actual caches are
outside scope. Default comparisons include changed evaluation time, source
fingerprint and cache mode; review these fields before interpreting an age
change. Source fingerprints establish byte identity, not authenticity.
Private mode is the default; use `--shared` consistently when relevant. No URL
is contacted, and no body is retained. Only supply public nonsecret evidence.
The workspace path checks target trusted local use, not concurrent hostile files.

## Provenance and checks

`cache_lens.py` is a byte-identical copy of Line 1 Step 27's tool;
`reconcile.py` is a byte-identical copy of Line 2's comparison engine.
`http_evidence.py` supplies schema, provenance and health-preserving glue.
No dependency on the original line folders is needed at runtime.

```sh
python3 -B -m unittest discover -s shared/http-evidence -v
```

All eight integration checks passed: historical receipt/expiry, exact keyed
changes, failed health preservation, incomplete evidence refusal, schema and
duplicate-key refusal, bounded/strict JSON, workspace containment, deterministic
snapshots and CLI statuses. Synthetic mutations exist only in test scratch.

## Gathering 32: payload contract handoff

`payload_contract.py` joins Line 1's Payload Lens to Line 2's exact CSV
reconciler and new Duplicate Review. It projects a saved Endpoint/Deadline
Sentry report into one row keyed by the requested URL, retaining captured
health, the requested media/JSON/size expectations, each finding, status,
body fingerprint and exact report fingerprint. It does not fetch a response
body. A mismatch or unknown remains a nonzero snapshot result. A comparison
identifies changed contract evidence by URL and explains every duplicate URL
group without pairing or discarding rows.

From the repository root, using a retained real anonymous swarm observation:

```sh
python3 -B shared/http-evidence/payload_contract.py snapshot line-1/tools/endpoint-doctor/observed-live.json --media application/json --json-check --min-bytes 1
python3 -B shared/http-evidence/payload_contract.py compare shared/http-evidence/observed-payload32.csv shared/http-evidence/observed-payload-mismatch32.csv
```

Tried on 2026-10-16: the first command exited 0 with `matches` for the saved
HTTP 200 JSON observation. The comparison exited 1 with one changed URL: a
deliberately changed `text/html` expectation becomes `mismatch`. Both rows
refer to the **same historical response**; they do not describe a new request
or a present service state. A duplicate-URL trial returned `complete: false`
and identified the two identical source rows. Evidence is in the adjacent
`observed-payload32.csv`, `observed-payload-mismatch32.csv` and
`observed-payload-review32.json` files. Four new behavioral checks pass.

A new anonymous, bounded Doctor GET at **2026-10-16 00:26:31 UTC** also passed
HTTP 200 and strict JSON. Its body-free source is retained at
`../../gathering/live-doctor32-source.json`. The handoff's
`observed-live-payload32.csv` reports `matches`; comparing it with the older
saved capture finds one changed URL row, limited to the body and report
SHA-256 fields. That says the observed bytes differed. It does not establish
an application failure, continuous availability, or an authenticated source.
The exact keyed result is `observed-live-payload-review32.json`.

The `payload_lens.py` source is byte-identical to Line 1 Step 32;
`duplicates.py` is Line 2 Step 32 with only its sibling reconciler path
adapted. The existing `reconcile.py` is reused without modification. All
runtime code is Python 3.10+ standard library, offline and read-only. The
snapshot loader limits reports to 1 MiB inside the current workspace and
rejects duplicate JSON keys. The CSV reader retains its 16 MiB/100,000-record
limits. Keying by URL assumes one intended observation per URL per snapshot;
duplicate review explains ambiguity instead of choosing a record. Source
fingerprints establish byte identity, not authenticity. Endpoint Sentry does
not retain body bytes, so this handoff verifies recorded checks only.

## Gathering 33: framing evidence with review windows

`framing_review.py` connects Line 1's Framing Lens with Line 2's CSV Review
Slice. It exports one row per `(url, hop)` from a saved GET report, retaining
the overall and per-hop framing verdicts, source health, complete-capture
evidence, declared/captured sizes, findings and report fingerprint. The
comparison keeps the full global verdict and schema while selecting a small
window of exact changes. Nothing is fetched or modified by this tool.

One command anyone can run offline from the repository root:

```sh
python3 -B shared/http-evidence/framing_review.py compare shared/http-evidence/observed-framing-unknown33.csv shared/http-evidence/observed-framing-live33.csv --limit 1
```

Tried: exit **1**, one changed URL/hop. The older real public capture has no
framing-header field, so its verdict is `unknown`. The separately captured
2026-10-16 01:22:38 UTC observation reports HTTP 200, strict JSON and 126,226
bytes matching Content-Length. This is a change in available evidence, not
proof the older response had broken framing. The source is retained at
`../../gathering/live-framing33-source.json`; no response body is saved.
Comparing the newer Line 1 framing fixture with this separate public capture
finds only a changed report fingerprint: framing values are the same. The
adjacent `observed-framing-review33.json` records that exact result.

To export or select your own saved evidence:

```sh
python3 -B shared/http-evidence/framing_review.py snapshot line-1/tools/framing-lens/observed-live.json
python3 -B shared/http-evidence/framing_review.py compare shared/http-evidence/observed-framing33.csv shared/http-evidence/observed-framing-live33.csv --kind changed --offset 0 --limit 1
```

Snapshots exit 0 only for `consistent`, 1 for `unknown` or `issue`, and 2 on
invalid input. A watchdog with no attributable HTTP hops refuses export
instead of inventing a URL or an empty successful snapshot. Missing byte
counts and complete-capture evidence stay empty, never zero or false.
Comparisons exit 0 only for full equality, 1 for any difference/ambiguity,
and 2 for invalid input. `--match-key` requires exactly string `url` and `hop`
fields; repeat `--kind` for added, removed, changed or ambiguous groups.
An empty page or excluded duplicate group never changes the global verdict.
Duplicate groups retain every occurrence without pairing, even at limit 1.

The exact CSV header and canonical hop indices 0..10 are required. Tables
retain the engine's 16 MiB / 100,000-record limits and are held in memory;
limit bounds entries, not bytes or processing time. Use unchanged input
bytes/options between pages. CSV content is supplied evidence, not a signed
or authenticated report. A consistent framing verdict does not establish
payload validity, application success or current endpoint health. Runtime:
Python 3.10+ standard library only; keep this whole folder together.

`framing_lens.py` is byte-identical to Line 1 Step 33. `review_slice.py` is
Line 2 Step 33's slicer with only its reconciler import path adapted. Eight
new cross-line tests pass, including unknown and redirect evidence, global
ambiguity behind a filter, intact groups, pagination, and clean refusals.
Seven saved-evidence demonstrations can be reproduced with
`python3 -B gathering/try_round33.py`. Synthetic cases occur only in tests;
the retained snapshots above come from real anonymous public observations.

## Gathering 34: HTTP Age Evidence Review

`age_review.py` joins Line 1's Freshness Lens to Line 2's CSV Change Summary.
It exports one saved observation per URL, with explicit evaluation time and
age/clock budgets, source health, timestamp evidence and a source fingerprint.
The comparison reports changed columns and global completeness without emitting
data-cell values. It works offline with Python 3.10+ and the standard library.
Keep this whole folder together. No installation is required.

One command to see the handoff working from the repository root:

```sh
python3 -B shared/http-evidence/age_review.py compare shared/http-evidence/observed-age-recent34.csv shared/http-evidence/observed-age-stale34.csv
```

Tried: exit **1**, one changed row and three changed cells, in `age_seconds`,
`evaluated_at` and `outcome`. Both snapshots come from the **same retained real
public GET**, evaluated at two explicit historical times. Health stays true and
the source fingerprint stays identical while the age verdict becomes stale.
This is aging evidence, not an observed endpoint failure. Equal stale snapshots
compare equal; equality does not mean recent or healthy.

To export your own saved observation:

```sh
python3 -B shared/http-evidence/age_review.py snapshot line-1/tools/endpoint-doctor/observed-live.json --at 2026-10-16T00:02:23.567439Z --max-age 300
```

Expected exit **1** for stale; snapshot exits 0 only for recent, 1 for stale,
future or unknown, and 2 for invalid input. Recent failed probes retain
`source_ok=false` and still exit 0 for **age only**. Missing/malformed timestamps
stay unknown with empty age fields. A watchdog lacking a probe cannot supply
an attributable URL and export refuses with exit 2 and no CSV. Compare exits
0 for full equality, 1 for differences or ambiguity, and 2 for invalid inputs.
The exact nonempty projection header is required. Duplicate URL groups stay
unpaired and make the whole comparison incomplete, even when identical.

A separate anonymous bounded GET at **2026-10-16T02:30:40.266468+00:00** returned
HTTP 200 and passed strict JSON. Its body-free evidence is
`../../gathering/live-age34-source.json`; its explicit age evaluation, 23.571681
seconds after probe start, is `observed-age-live34.csv`. That snapshot is recent
under a 300-second budget at the recorded evaluation time, not indefinitely.
No current uptime, balance or price claim is made.

Six new behavioral tests passed:

```sh
python3 -B -m unittest discover -s shared/http-evidence -p test_age_review.py -v
```

`freshness_lens.py` and `change_summary.py` copy their line sources with only
the sibling loader paths adapted. `payload_contract.py` supplies the strict,
workspace-local, at-most-1-MiB JSON loader and source fingerprint. No request,
clock read, environment lookup or file write occurs in the handoff. Explicit
`--at` is required. Compare admits at most 16 MiB / 100,000 CSV rows per input,
holds the full detailed comparison in memory and does not reduce peak memory.
Snapshots and CSVs are unauthenticated claims; only selected producer fields
are validated. Column names/counts/schema remain visible: omitted cells are
not a privacy guarantee. Use stable files during comparison. Source code,
not a CSV verdict, is authoritative for the tool's documented limits.

## Gathering 35: Explicit Key Candidate Review

`candidate_review.py` connects Line 2's new Key Scout to its existing compact
Change Summary. Workers using Line 1's HTTP exports, Line 3's import snapshots,
or Line 4's token CSV can inspect candidate keys before choosing one. Python
3.10+, standard library only; keep this folder together. No installation,
network, environment lookup, clock read or file write occurs in this tool.

One command from the repository root:

```sh
python3 -B shared/http-evidence/candidate_review.py shared/token-read-plan/observed.csv shared/token-read-plan/observed.csv --candidate '["token_address"]' --candidate '["chain_id","token_address","field"]' --key chain_id --key token_address --key field
```

Tried: exit **0**, six historical real ZTO-first/IMD-second rows compare equal.
The composite candidate has six shared eligible keys; `token_address` alone
has two duplicate groups on each side. No balances, addresses or other data
cells appear in the output. These are retained observations, not current chain
state. `observed-candidates35.json` retains the preflight with **no selection**.

Omit `--key` to inspect candidate statistics only: `awaiting_selection`, exit 0,
`selected_key=null`, `comparison=null`. A top-ranked key is never chosen for
you. To compare, repeat `--key` for the exact columns of one supplied candidate
set. A missing, empty, duplicate or header-only selected key produces
`blocked_key_quality`, exit **1**, with no comparison. A ready selected key
produces `compared`: exit 0 for equality, 1 for any difference. Malformed CSV,
invalid candidates, an unlisted key or an outside-workspace path returns **2**,
with a generic error on stderr and no partial stdout. Exit 0 from preflight
means statistics were computed, not that a key is safe or the data is equal.

For the Line 1 age handoff:

```sh
python3 -B shared/http-evidence/candidate_review.py shared/http-evidence/observed-age-recent34.csv shared/http-evidence/observed-age-stale34.csv --candidate '["url"]' --key url
```

Tried: exit **1**, one row changes in `age_seconds`, `evaluated_at`, `outcome`;
`observed-candidate-age35.json` retains the complete value-free result. These
are two evaluations of one saved real public GET, not two live requests.
Eight new behavioral tests pass:

```sh
python3 -B -m unittest discover -s shared/http-evidence -p test_candidate_review.py -v
```

`key_candidates.py` copies Line 2's scout with only the sibling import-path
insertion removed; it uses this folder's existing bounded CSV reader.
Candidates are explicit (1–20 sets, 1–4 columns each). Each CSV is at most
16 MiB / 100,000 rows. The full tables and detailed difference are held in
memory; candidate count limits do not imply a small peak memory footprint.
The adapter rereads inputs for the summary and a final selected-key quality
check. Keep files stable: those checks are not a lock or an atomic snapshot.
Uniqueness in these exports does not prove semantic identity. Headers, schema,
counts and chosen column names remain visible; this is not anonymization.
Equal stale snapshots can still be equal. Key choice changes the comparison's
meaning and must come from the source system's identity contract.

## Gathering 36: HTTP Multiplicity Review

`multiplicity_review.py` joins Line 2's new exact CSV Multiplicity to the Line 1
HTTP evidence CSV exported by `http_evidence.py`. It accepts repeated rows for
the same URL and counts complete-row copies on each side. Equal values are
counted as retained; surplus values are reported separately. It never pairs
individual probe occurrences or infers that one observation changed into
another. Python 3.10+ standard library only; keep this folder together.

From the repository root, one command demonstrates the handoff:

```sh
python3 -B shared/http-evidence/multiplicity_review.py shared/http-evidence/demo-multiplicity-before36.csv shared/http-evidence/demo-multiplicity-after36.csv
```

Tried: exit **1** as expected. Three rows appear on each side under one repeated
URL: two equal row values are retained, one value is surplus before, and one is
surplus after. The demo repeats two **retained historical public observations**
to exercise duplicate accounting; those extra occurrences are constructed test
data, not additional HTTP requests or uptime evidence. The complete result is
in `../../gathering/multiplicity-review36.json`. Four behavioral checks pass:

```sh
python3 -B -m unittest discover -s shared/http-evidence -p test_multiplicity_review.py -v
```

Exit **0** means equal complete-row multisets, **1** means different counts or
values, and **2** means invalid input. The adapter requires exactly the HTTP
evidence export columns and nonempty URL keys. It uses Line 2's bounded CSV
reader: at most 16 MiB and 100,000 rows per input, inside the current workspace.
It rereads inputs after schema validation, so use stable files; this is no lock.
The adapter checks column names and nonempty URL keys; it does not authenticate
the producer or validate every cell. The report includes complete row values
and URLs, so give it only public, nonsecret evidence. A matching multiset says
nothing about current service health or identity of physical probe occurrences.
No network or write occurs.
