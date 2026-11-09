# CoMVP+ CoPre CLI Pilot | Wave BEGIN

**WorkID:** `CoMVP.CoPrePilot.20261109` | **Wave:** `CLI-first-use-r0` | **Phase:** BEGIN
**Date:** 2026-11-09 UTC | **Surface:** CoCivium public draft-review branch
**Base:** `20c0db2118f28be6b0a08d921ebec949216463d7` (main at branch creation) | **State:** `INTENT_ONLY`

## CoHereNow

The broad [CoPre research PR #401](https://github.com/CoCivium/CoCivium/pull/401) has reproducible synthetic code checks but its 38 commits / 26 files have not earned product acceptance. [CoMVP acceptance issue #403](https://github.com/CoCivium/CoCivium/issues/403) directs us to isolate and finish one coherent task rather than add features.

This wave isolates the original **unchanged** `scripts/CoPreContinuationR0.py` from PR #401 (Git blob `5a1a8cd15eb41af151c9255bee46cc7549e1acd8`) into a narrow candidate branch rooted in main. The source file is copied byte-for-byte, not rewritten or silently superseded; review/merge conflicts with the broader PR remain possible and require normal resolution.

## First user-worthy job

Given the **live public GitHub issue #403** and its current source revision, generate one bounded read-only CoPrePack and one explicit continuation message; preserve WorkID, source hash, authority, STOP, receiver reference, and recovery pointer. Compare it with a compact WorkID-only pointer. Fail closed when public source is unreachable or currentness cannot be verified.

This is a live external public *task object* but a CI-operated demonstration, **not** first use by an independent human or actual product receiver. Source identity verification by GitHub API and currentness must happen outside the pure CoPre compiler and be stated explicitly.

## Scope and stop

- Land unchanged core CLI, a short first-use README, a focused live-public-task acceptance harness, and a read-only CI workflow. No CoEv/Copattern/CoLOT subsystem expansion.
- Test fresh process operation, stale source refusal, private/effect hold, quiescence, concise pointer versus full message, and source hash.
- Save separate END render after code is committed; CI result and exact Git readback will be attached as an external receipt.
- Preserve old broad PR #401. Do **not** merge into main automatically or declare task-level MVP without receiver-side acceptance.

**Authority:** public read-only API and candidate-branch source writes only. **RickAction:** none.  
**STOP:** unauthorized or unreachable source, incompatible donor source, unstable output, absent receiver.  
**NEXT:** current-source issue #403 CLI acceptance and baseline comparison.

**Nonclaims:** `BEGIN_NE_PASS | SOURCE_TASK_NE_INDEPENDENT_RECEIVER | SAME_SOURCE_BLOB_NE_MERGED_BASELINE | CI_PASS_NE_TASK_MVP | NO_MUTATION_GRANTED`.
