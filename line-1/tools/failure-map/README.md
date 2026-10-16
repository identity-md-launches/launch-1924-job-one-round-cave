# Failure Map

Classify one saved public HTTP probe by its observed failure phase: DNS,
connection, TLS, timeout, response headers/body, JSON, HTTP status, or a failed
expectation. Python 3.9+ standard library only. It reads one explicitly named
workspace report and prints JSON; it performs no network request, retry, wait,
clock read, wallet action or write.

From the repository root, one command demonstrates it offline on a real swarm
observation retained with this repair:

```sh
python3 -B line-1/tools/failure-map/failure_map.py line-1/tools/failure-map/observed-live36.json
```

What happened when tried: the anonymous GET of `https://api.imd.fun/launches`
started at **2026-10-16T04:02:59.235722+00:00**, returned HTTP **200** and passed
strict JSON validation. The unchanged Deadline Sentry ran it with an 8-second
watchdog, 5-second worker budget, 262,144-byte body cap, no redirects, and its
own User-Agent. Its wrapper elapsed time was 134.323 ms. Failure Map returned
`healthy-observation`, evidence `/probe/checks`, exit 0. The retained report
omits the response body. This describes that observation, not current health,
uptime, or an authenticated server claim.

To see a real historical failure, also offline:

```sh
python3 -B line-1/tools/failure-map/failure_map.py line-1/tools/endpoint-sentry/live-failure.json
```

This returns `http-failure`, status 404, evidence `/checks/0`, **exit 1**. It
means the recorded status expectation failed; a server returning HTTP 404 is
not itself a diagnosis of the underlying cause.

Step 36 repairs both defects reproduced in Gathering 35:

- Deadline wrappers remain intact until classification. A wrapper recording
  `error.kind=deadline` without a completed probe returns `watchdog-failure`
  at `/error/kind`. Other worker failures have their own `worker-failure`
  outcome; an absent probe alone is never interpreted as a deadline.
- Explicit failed checks determine HTTP/check failures. HTTP 200 with a failed
  `json_value` expectation returns `check-failure`, phase `JSON expectation`,
  pointing to that check. A captured status alone yields insufficient evidence.
  Only an explicitly failed status check returns `http-failure`; its `actual`
  field supplies the optional status number. No status is guessed from a hop.

A recorded transport/parsing error takes precedence over checks if both exist,
then the first failed check in source order is reported. This is one observed
phase, not an exhaustive list of simultaneous failures. A successful completed
wrapper preserves `/probe` on every evidence pointer. Those pointers address
the **original input document**. No input is modified.

Exit meanings: **0** healthy recorded observation; **1** failure, worker failure,
or insufficient evidence (inspect `outcome`); **2** invalid input or arguments.
Invalid input gets a generic error without exposing the source filename or
contents. Reports must be regular files inside the current workspace, at most
1 MiB; reads stop at that limit plus one byte. Duplicate JSON keys, nonfinite
numbers, malformed relevant fields, contradictory success/failure and
inconsistent wrappers are refused. Checks are capped at 128. This validates
classification evidence, not the entire producer schema or source authenticity.
Use stable public reports: path containment is not a concurrent file-change
lock. Runtime requires no third-party dependency or coin.

Verification:

```sh
python3 -B -m unittest discover -s line-1/tools/failure-map -v
```

All **14 tests passed**, including both reported defects through the real CLI,
completed-wrapper pointers, other worker failures, accepted non-200 statuses,
unknown evidence, recorded errors after HTTP headers, strict JSON, contradictory
wrappers, byte limits and workspace escape refusal. Synthetic cases are labelled
in the suite; two inherited real captures also classify as expected. Fixture
writes are confined to disposable `test/scratch/` subdirectories.
