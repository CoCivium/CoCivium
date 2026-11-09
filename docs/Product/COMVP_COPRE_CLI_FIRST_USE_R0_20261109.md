# CoMVP+ CoPre read-only CLI | Task-scoped first-use candidate

**2026-11-09 | PUBLIC DRAFT | not released, not independently user accepted.**

The isolated [CoPre compiler](../../scripts/CoPreContinuationR0.py) is byte-identical to the earlier research donor from [PR #401](https://github.com/CoCivium/CoCivium/pull/401), Git blob `5a1a8cd15eb41af151c9255bee46cc7549e1acd8`. This branch isolates a tiny coherent CLI pilot and does not modify PR #401.

## Actual task

Create a read-only, source-bound continuation for the **real public [CoMVP issue #403](https://github.com/CoCivium/CoCivium/issues/403)**. A small stdlib [first-use harness](../../scripts/CoMVPCoPreFirstUseR0.py) fetches the issue twice from GitHub's public API, checks exact issue identity, OPEN state, relevant content and a matching content-and-update-time digest, then compiles the CoPrePack and shorter WorkID-only pointer.

## Run

Requires Python 3.10+ and access to GitHub's public issue endpoint; no API token or private data.

```sh
python3 -B scripts/CoPreContinuationR0.py --selftest
python3 -B scripts/CoMVPCoPreFirstUseR0.py --selftest
python3 -B scripts/CoMVPCoPreFirstUseR0.py --live-public-issue-403
```

The live command writes one JSON record to **stdout**, including `status`, `source_revision`, `pack_sha256`, `pack`, `continuation_input`, `pointer` and size comparison. It creates no files, changes no issue, and performs no publication. A source that changes between reads, is unavailable or mismatches becomes **HOLD** and exit code 2. A resulting `SOURCE_TASK_CLI_GENERATED_ONLY` means *the CLI generated a valid candidate*; it does not mean an independent user understood or used it.

### Input and output

Input is the current public issue #403 (not a synthetic paragraph). No human pasting or transient session memory is necessary. Output is two source-bound, read-only choices, full CoPre continuation or compact WorkID pointer. Neither automatically opens a ChatGPT input field or grants execution authority.

No private or child-facing state may be passed through this public demonstration. Public issue text is untrusted **data**; it is never executed or embedded verbatim as instructions. Its content digest is a byte-level consistency anchor **for the observed two reads**, not a signed GitHub historical version or proof of global currentness.

### What counts as MVP

**SOURCE_VERIFIED:** real public issue fetched reproducibly, exact scoped source identity and outputs, negative controls pass.

**TASK_MVP (HELD):** A separately authorized receiver actually reconstructs the task with correct STOP, source/currentness and authority; demonstrates a useful result with user-centric, intelligible errors; receiver-origin readproof and measured zero Rick relay. A GitHub Actions runner is not the independent user.

**OPERATIONAL_MVP (HELD):** a real installed runtime, monitoring, interruption and recovery proofs, availability and rollback.

### Compatibility and rollback

- Donor source is unchanged from PR #401; preserve that blob as the rollback baseline for this CLI candidate.
- Compare with the simpler WorkID-only pointer; token and byte sizes are not a benefit benchmark.
- No cross-provider session wake, storage election, CoEx, main merge, credential use, branch freeze or actual product release.
- CoStageReview and CoWaitless still govern release and independent unaffected CoLOT work.

**NEXT:** Obtain a separately operated, consenting first-use receiver for issue #403 with exact readback and useful task completion, compare compact pointer to full prompt, and retain the fitter candidate without overwriting the original.
