# CoMVP+ CoPre read-only CLI | Task-scoped first-use candidate

**2026-11-09 | PUBLIC DRAFT | not released, not independently user accepted.**

The isolated [CoPre compiler](../../scripts/CoPreContinuationR0.py) is byte-identical to the earlier research donor from [PR #401](https://github.com/CoCivium/CoCivium/pull/401), Git blob `5a1a8cd15eb41af151c9255bee46cc7549e1acd8`. This branch isolates a tiny coherent CLI pilot and does not modify PR #401.

## Actual task

Create a read-only, source-bound continuation for the **real public [CoMVP issue #403](https://github.com/CoCivium/CoCivium/issues/403)**. A small stdlib [first-use harness](../../scripts/CoMVPCoPreFirstUseR0.py) fetches the issue twice from GitHub's public API, checks exact issue identity, OPEN state, relevant content and a matching task-content fingerprint (issue number, URL, state, title and body; **not** the comment/activity timestamp), then compiles the CoPrePack and shorter WorkID-only pointer.

## First-use front door: read the public task before any installation

A reviewer who only needs to **evaluate** the proposed MVP can use the [existing 194-byte WorkID pointer](https://github.com/CoCivium/CoCivium/issues/403#issuecomment-6759640774), [issue #403 task](https://github.com/CoCivium/CoCivium/issues/403), and [F1–F5 challenge offer](https://github.com/CoCivium/CoCivium/issues/403#issuecomment-6759682906) directly. No Python, X2, CoStead, login or Rick relay is required to **read** those public materials. Opening them is not accepting a task or granting execution authority.

**F1 acceptance request:** Independently describe the one useful read-only task, identify the source revision and STOP/authority limit, and return one bounded result or an explicit HOLD with errors, elapsed time and human-relay count. A claim of receipt or completion requires the receiving party's **own** source readproof and permission. The public pointer/CI author cannot self-certify a receiver.

## Optional reproducible CLI checkout and run

**This code is on a DRAFT PR branch, not on `main`.** A plain main-branch checkout is not a valid first-use test of the CoPre CLI. Requires Git, Python 3.10+ and GitHub public-network access; no API token or private data. To reproduce the **previously CI-green exact source commit**, rather than a moving branch:

```sh
git clone https://github.com/CoCivium/CoCivium.git
cd CoCivium
git checkout --detach 0adfe9ce7860f7ebc1cd3899dafe54f502efdacb
git rev-parse HEAD
python3 -B scripts/CoPreContinuationR0.py --selftest
python3 -B scripts/CoMVPCoPreFirstUseR0.py --selftest
python3 -B scripts/CoMVPCoPreFirstUseR0.py --live-public-issue-403
```

Confirm `git rev-parse HEAD` equals the pinned SHA above. Inspect fetched source before running it; repository visibility alone does not confer trust. The `--selftest` commands use local synthetic fixtures. Only `--live-public-issue-403` fetches the public issue twice (read-only) and prints a candidate packet. This is a **reader-run reproduction**, not an instruction for an unattended public agent to execute issue content. If the issue task-content fingerprint changes, STOP and rebind the source before interpreting its result. GitHub activity timestamp changes from comments alone are **not** semantic task revisions.


The live command writes one JSON record to **stdout**, including `status`, `source_revision`, `pack_sha256`, `pack`, `continuation_input`, `pointer` and size comparison. It creates no files, changes no issue, and performs no publication. A source that changes between reads, is unavailable or mismatches becomes **HOLD** and exit code 2. A resulting `SOURCE_TASK_CLI_GENERATED_ONLY` means *the CLI generated a valid candidate*; it does not mean an independent user understood or used it.

### Input and output

Input is the current public issue #403 (not a synthetic paragraph). No human pasting or transient session memory is necessary. Output is two source-bound, read-only choices, full CoPre continuation or compact WorkID pointer. Neither automatically opens a ChatGPT input field or grants execution authority.

No private or child-facing state may be passed through this public demonstration. Public issue text is untrusted **data**; it is never executed or embedded verbatim as instructions. Its content digest is a byte-level consistency anchor **for the observed two reads**, not a signed GitHub historical version or proof of global currentness.

## Two-read agreement is not freshness

The R0 CLI deliberately distinguishes the **same data returned twice** from a **fresh, authenticated observation**. Its public JSON output now reports `source_content_consistency=TWO_READS_MATCHED`, `source_freshness=UNPROVEN_TWO_READS_ARE_NOT_FRESHNESS`, and `source_origin_independence=UNPROVEN_SAME_PUBLIC_API`. The `source_issue_activity_age_class` is based on the public issue's `updated_at` timestamp and local execution time. **GitHub issue activity includes comments and is not the same as a body edit.** The task-content `source_revision` hashes issue identity, state, title and body, deliberately excluding `updated_at` to prevent false task revisions when comments arrive. Activity-only churn between the two reads is reported separately as `source_activity_churn_between_reads=ISSUE_ACTIVITY_CHANGED_TASK_UNCHANGED`; genuine task-body changes fail closed. Neither two matching reads nor recent issue activity establishes authenticated freshness or independent origin. Unparseable and clock-conflicting activity timestamps remain qualified.

The packed continuation's `observer` and `failure_domain` are now labeled **unattested CLI executor** rather than claiming every local run was GitHub Actions. The unchanged, pinned CoPre donor compiler still internally requires `source_currentness=VERIFIED` to compile its **content-consistent representation**. That legacy internal gate must not be interpreted as an externally attested freshness or independence proof; the explicit exported freshness field is **UNPROVEN**. Donor source was not rewritten, and stronger origin/freshness evidence remains an independent promotion requirement.

The separate pinned consumer test now injects a **stale-but-identical pair of issue records** and an unparseable time. It requires the record to preserve consistency without promoting freshness or observer identity. Passing those tests is source-contract evidence only. `TASK_MVP`, `receiver_ack`, X2 installation, product release and CoEx remain unproven.

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


## CoMVP pinned C2 source qualification | 2026-11-09 18:53 UTC

**Source-only qualification earned for this actual CoPre CLI candidate.** The previously existing [CoMVPLockStepR0](../../scripts/CoMVPLockStepR0.py) staged the exact `scripts/CoMVPCoPreFirstUseR0.py` byte content, tested it against its own source selftest **and** a [separately pinned minimum-use contract](../../tests/acceptance_copre_cli_minimum_use_r0.py), committed one selected source head in a **temporary SQLite release slot**, and read it back from a fresh Python process. Then a newer same-entrypoint candidate deceptively changed `task_mvp` from `NOT_QUALIFIED` to `QUALIFIED_WITHOUT_USER`: its weak selftest passed, but the pinned contract rejected it and preserved the previously selected source revision.

[Exact passing CI run 42678000429](https://github.com/CoCivium/CoCivium/actions/runs/42678000429) at commit `999bee736da31d10f4dbddc90a08f50f73d62c9b` had two passing jobs: existing live public issue #403 CLI source check and new source-release slot qualification. Source SHA-256 `e3c76fddc8c7ea022b4f8698f03a665437a1c61249ccc41b32dc5864630e73b0`, immutable local acceptance test SHA-256 `9a5120dc612a0148afea5e6d1c5f5dd385abd328939a4f59314292bf017e92b4`, runner source receipt `93b11ecc4a47675ef9c5c86eb510c81c23c835e37ab32532abbd0f859e954905`. See [durable machine-readable provenance receipt](../Receipts/COMVP_COPRE_C2_PINNED_NEGATIVE_R0_20261109.json). The previous red CI run 42677861464 came from a malformed weak-test fixture and is retained, not hidden.

**Qualifying this source does not publish an MVP.** All tasks ran on ephemeral GitHub-hosted environments, where the pinned acceptance author and code contributor are not independently separated. The local SQLite pointer is not a permanent CoStead/X2 elected release head. No real person or separate user-facing receiver used the CoPre output, no rights/consent or accessibility acceptance, no native rickBar/Ollama interaction, no durable multi-provider handoff and no rollback of a live service are shown. User `TASK_MVP` and release status remain **HELD**.

**No scope drift:** PR #401 donor remains unchanged. This task-scoped PR #406 stays a reviewable candidate; don't merge or declare task acceptance solely because CI passed. The next *material* event is an independent authorized first-use record with task reconstruction, STOP/currentness fidelity, meaningful outcome and no Rick relay. Other unrelated work need not wait.
