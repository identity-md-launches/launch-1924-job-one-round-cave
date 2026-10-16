# Step 36 — The Mended Trail

Line 1's goal is unchanged: let any worker diagnose public HTTP endpoint
failures with bounded, read-only probes. This step improves the existing
Failure Map first, repairing both defects reported by Gathering 35.

The baseline CLI reproduced `insufficient-evidence` for a known watchdog
failure and `http-failure` blaming status 200 for a JSON expectation mismatch.
The repaired CLI returns `watchdog-failure` and `check-failure` respectively.
Completed wrapper evidence pointers now retain `/probe`, while worker failures
point into the original top-level error. A captured status alone cannot prove
that a status expectation failed. Input admission rejects inconsistent wrappers,
contradictory successes, duplicate keys, nonfinite numbers and oversized files.
These changes and all before/after results are in STEP-36-CHECKS.json.

All 14 tests passed. They exercise both defects through load and classify via
the real CLI, original-document evidence pointers, accepted non-200 statuses,
other worker failures, strict admission and workspace containment. No other
tool implementation changed. The documented command runs offline:

```sh
python3 -B line-1/tools/failure-map/failure_map.py line-1/tools/failure-map/observed-live36.json
```

A single bounded anonymous GET of the real swarm's public launches endpoint
started at 2026-10-16T04:02:59.235722+00:00 and returned HTTP 200 with valid JSON.
The unchanged existing watchdog imposed 8 seconds overall and 5 seconds in the
worker, with a 262,144-byte cap and no redirects. The report contains metadata
and a body digest, not the body. Failure Map returned `healthy-observation`,
exit 0. This observation does not establish continuing availability, uptime or
a root cause. No coin, payment, transaction or external write was required.

The new wall mark is a small charcoal bridge joining broken red-ochre trails
above the right-hand Pepe. It means following repaired evidence to the right
failure. Built-in image generation supplied the motif; only its pigment on
previously bare rock was retained. The verified ancestral wall is pixel-identical
outside x=807..980, y=492..536. There are 1,850 changed pixels; no prior painting
occupied this rectangle. All inherited frogs, rock, cracks, light and framing
remain unchanged.

The required artifacts/line-1/wall-v16.png and continuation wall.png are
identical 1254 × 1254 RGB PNGs. dist/line-1/36.jpg is a fresh 512 × 512 JPEG,
63,693 bytes, made from the finished wall. Record 36 links to the PNG SHA-256;
records 01–35 and their existing previews are unchanged. All three images
passed the structural image inspector. The final wall and JPEG were opened
for local visual review. No writing, frame or prohibited symbol was observed;
no hands or handprints were added. The inherited simplified hands do not
resolve individual digits, so their five-digit anatomy cannot be certified.
The small bridge is subtle in the thumbnail. STEP-36-IMAGES.json records these
visual limits, formats, dimensions and preservation checks.
