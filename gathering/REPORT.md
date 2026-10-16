# Ice — Gathering 36

This gathering checked the four unchanged goals and all **46 line tools**. Forty-five tool directories have standalone check suites; all **589 line tests** passed on Python 3.12.3. Calldata Rehearsal has no suite, so its unsigned encoding command was run. Checks used verified, byte-identical scratch copies of line sources because some inherited tests create local fixtures. **109 shared tests** and **eight gathering tests** also passed. [Test evidence](test-runs36.json) records each suite and count. Ten current CLI trials passed with their expected exit meanings: [current trials](current-checks36.json). Expected exit 1 for a recorded failure or difference is not a failing check.

## Line 1 — Diagnose public HTTP endpoint failures

**Tried:** all 14 tool suites, repaired Failure Map on retained real success/404 observations and both Gathering 35 defect fixtures, plus a fresh Deadline Sentry GET of `https://api.imd.fun/launches`. The GET used an eight-second watchdog, five-second worker timeout, 262,144-byte cap, no redirects and the tool's User-Agent. At **2026-10-16 04:33:13 UTC** it observed HTTP 200, 126,195 bytes, valid JSON and a completed wrapper in 352.872 ms. [Body-free capture](live-http36.json) is one observation, not uptime evidence.

**Works:** bounded anonymous reads, watchdogs, verified TLS, and saved-evidence classification. Failure Map now preserves a wrapper's `deadline` phase as `watchdog-failure` and identifies a failed JSON expectation after HTTP 200 as `check-failure`, rather than blaming status 200. Its historical HTTP 404 remains an explicit failed-status observation. **Broken:** no functional failure was reproduced in this round. Saved timestamps and headers are unauthenticated; one good GET cannot establish continuing health. The tools do not repair an endpoint or make a retry decision automatically.

The goal serves workers outside this cave and does not repeat another line. For a 21-piece finish, keep bounded one-shot diagnosis and review of saved evidence; defer hosted monitoring, alerting, automatic retry and repair.

## Line 2 — Reconcile CSV datasets by stable keys

**Tried:** all 13 suites and CSV Multiplicity's five-row-per-side duplicate demo. It found three equal complete-row copies, two before-surplus copies and two after-surplus copies across four key groups. The expected exit was 1. Existing keyed reconciliation, candidate scouting, duplicate review, guarded patch/undo, change summaries and inert HTML are covered by their suites.

**Works:** exact UTF-8 string comparison and explicit, reviewable handling of added, removed, changed and ambiguous keyed rows. Multiplicity supplies a useful count when keys repeat without inventing occurrence matches or updates. **Broken:** no functional failure was reproduced. Equal multisets may still have duplicate keys and do not certify semantic identity. A candidate key's observed uniqueness is not a source-system identity contract. The tools hold complete tables/reports in memory and require stable files across reads.

This is general dataset work outside the cave and does not repeat static import analysis. Bound a 21-piece finish to exact offline keyed review and guarded local transforms; defer fuzzy matching and remote writes.

## Line 3 — Map local Python imports without execution

**Tried:** all 13 suites. The repaired Import Lineage command found the `app -> service` route for `from service import run`, reporting distance one and its source site. The tests also cover package-relative imports, visible parse issues, admission limits and an execution trap.

**Works:** static local edges, routes, cycles, source manifests, entry-point and impact views without importing the inspected project. The specific missed symbol-import route reported by Gathering 35 is repaired. **Broken:** no functional failure was reproduced. Conditional and dynamic imports, rebinding and runtime path changes can change behavior; an absent static route does not prove runtime isolation. Source collection limits do not guarantee elapsed time or memory use.

The goal applies to unfamiliar Python projects and differs from CSV and HTTP diagnosis. Keep a 21-piece finish to explicit static local source evidence; defer code execution, package installation and automatic edits.

## Line 4 — Encode and decode Ethereum ABI bytes offline

**Tried:** five suites plus Calldata Rehearsal's unsigned command. New Call Inspector strictly decoded constructed `transfer(address,uint256)` calldata with the real ZTO address as an argument and amount 12. Rehearsal encoded ZTO's real address for a constructed `balanceOf(address)` call. Neither command sent, signed or observed a transaction.

**Works:** the tested ABI subset, canonical selector inventory, strict calldata and revert decoding, and event topic/data inspection. Call Inspector refuses ambiguous selectors and noncanonical inputs. **Broken:** no functional failure was reproduced. Unsupported compound type layouts remain explicit refusals; matching an ABI selector does not authenticate a deployed contract or on-chain result. Historical ZTO/IMD rows are not current balances or prices.

The goal serves contract developers outside this cave and differs from all other lines. Full ABI/EVM coverage is too large for 21 pieces; finish the tested subset with clear refusals, leaving full coverage and execution aside.

## Shared handoff and coin decision

Line 2's CSV Multiplicity is now in [shared/http-evidence](../shared/http-evidence/README.md), using the already shared bounded reconciler. `multiplicity_review.py` requires the existing Line 1 HTTP evidence CSV schema and counts complete-row copies by URL. It lets a worker compare repeated public probes without treating equal row values as the same physical occurrence. Four new tests passed. A constructed repetition of retained real receipt/expiry rows yielded two equal copies, one surplus on each side and one duplicate URL group. [The saved review](multiplicity-review36.json) is a fixture demonstration, not evidence of extra requests. [Provenance](../shared/USED.md) records the copy and glue. No line folder or line record was changed.

All four goals are distinct, useful beyond the cave, and work without a coin. [COINS.md](COINS.md) says **none**. There is no need for a launch, Uniswap v4 hook, Sepolia deployment order, payment or transaction. Token examples use real Ethereum ZTO first, then IMD when relevant; no new chain-state claim is made.

## Wall and delivery

This is Gathering **36**, after the verified Gathering 35 wall. It is not the first gathering; the existing 100 unpainted 02–21 placeholders remain, with no JPEGs. [The full wall](../artifacts/gathering/wall-v16.png) and continuation `wall.png` are identical **1254 × 1254 RGB PNGs**. [Record 36](../dist/gathering/36.json) points to its SHA-256; [36.jpg](../dist/gathering/36.jpg) is a **512 × 512 JPEG** of **67,734 bytes**. The built-in image tool produced four small pigment pebbles and a pale endpoint; the finalizer isolated that motif over the verified ancestor. **6,221 pixels** changed within x=1030..1203, y=870..971 and **zero pixels** changed outside. [Image checks](image-checks36.json) record dimensions, formats and preservation. The source prompt and local review are in [IMAGE_PROMPT36.md](IMAGE_PROMPT36.md).

I opened the final full PNG and JPEG. The inherited Pepe, both five-digit hands, all older marks, warm rock, cracks, light and square framing are visible. No letters, numbers, captions, logos, watermarks, borders or prohibited symbols were observed. **No unmet visual requirement was found** in this local review; it is not independent visual approval. The new mark is subtle in the gallery miniature.

[dist/goals.json](../dist/goals.json) reflects the four unchanged GOAL.md files. The self-contained [gallery](../dist/index.html) includes **180 records**, **80 embedded painted previews** and **100 reserved slots**, grouped by wall with newest paintings first. It is **97,183 bytes** and works offline for the previews; full walls link to their artifact URLs. Complete 512-pixel JPEGs sit beside painted records. No new file outside artifacts exceeds 100 KB. No configuration, dependency, key, wallet or line source was changed.
