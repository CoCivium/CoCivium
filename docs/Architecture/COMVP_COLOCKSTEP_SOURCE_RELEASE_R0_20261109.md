# CoMVP+ / CoLockStep+ | Stable islands, selective release cohorts R0

**Observed:** 2026-11-09. **State:** PUBLIC TESTED LOCAL SOURCE-RELEASE CONTROLLER, NOT INSTALLED COALL RUNTIME OR USER-QUALIFIED PRODUCT.

## Problem observed

CoAll has substantial source, tests and conceptual modules, yet many components are not established usable for an end-to-end task. Continuing to add capabilities can leave a previously functional version harder to use, less predictable or incompatible with its consumers. A `PASS` from a unit test is not a deployed MVP, and a prototype that worked once is not a continuously available service. A larger checklist cannot repair missing version selection.

The existing [CoStageReview+](COREVIEW_PANEL_LIFECYCLE_R0.md) models nine stages and review seats but is explicitly **read-only**, not an installed release controller. [rickBar Continuity R1](RICKBAR_CONTINUITY_R1_20261108.md) already owns its conversation/WorkID substrate. Do not duplicate either, invent another Orb or create a second Seed.

## Decisions

1. **CoMVP+ is a qualified *useful* boundary per prodlet and consumer.** It requires an identifiable task, a working input/output contract, success and failure behavior, source integrity, actual receiver-side observation, reversibility/Break Glass, and retained user-visible utility. No feature count automatically earns MVP.
2. **CoLockStep+ is selective, not global.** Subsystems may experiment in parallel and commit tested source heads independently when their contracts remain compatible. An incompatible dependent pair must promote or roll back as one atomic cohort. Global clock synchronization of all CoAll would create an all-system bottleneck.
3. **Keep the last known qualified head.** Staging or failing a replacement must never silently replace the selected version. An in-progress candidate lives alongside the selected head, not on top of it.
4. **Stable is scoped.** A source-tested revision may be stable for the local source controller while still being entirely unqualified as a running X2 or public service. No one-word `PASS` for all layers.
5. **A successful newer version can be worse.** Functional acceptance and cross-version comparative tests must preserve the *consumer's minimum useful task*, recoverability and resource limits. Version-specific tests alone are insufficient to prove no regression. Broader qualification remains HELD until independently sourced contracts and receiver outcomes are available.
6. **ReEvo does not destroy the baseline.** Old verified heads and failure receipts remain addressable; rollback uses exact qualified source revisions and dependency checks. The active interface should show the selected stable head, not force users into a half-complete experiment.

## Implemented bounded local proof

[CoMVPLockStepR0.py](../../scripts/CoMVPLockStepR0.py) uses standard-library SQLite/WAL, explicit bounded source files, SHA-256 content revisions, local validator programs, compare-and-swap head generations, one SQLite transaction per compatible cohort and a linked local event digest chain. It offers CLI commands: `stage`, `qualify`, `promote`, `status`, `audit`. Existing [CoStageReview CI](../../.github/workflows/costage-review-r0.yml) runs its regressions without starting another daemon or scheduled watcher.

**Verified GitHub test boundary:** [CoStageReview CI run 42604702695](https://github.com/CoCivium/CoCivium/actions/runs/42604702695) completed SUCCESS for the release-slot controller and stage-review donor. Scenarios include actual fresh-process CLI stage → qualify → promote → status, independent prodlet versions, incompatible dependent upgrade HOLD, atomic cohort promotion, failed candidate leaving the old head in place, coordinated rollback, stale-writer fencing, filesystem mutation, audit tampering and cold-process SQLite readback. **These are synthetic local-source fixtures, not actual rickBar/X2 receiver tests.**

### Source-only local CLI demonstration

Run in a trusted checkout containing a *trusted* test script. Validator scripts execute Python code with the caller's privileges; never run arbitrary unreviewed third-party scripts, nor use this as a sandbox.

```sh
python3 scripts/CoMVPLockStepR0.py --root . --db /tmp/comvp-local.sqlite status
python3 scripts/CoMVPLockStepR0.py --root . --db /tmp/comvp-local.sqlite stage --slot myprodlet --artifact myprodlet.py --test tests/test_myprodlet.py
```

`stage` emits the content SHA-256 revision. With that exact revision, `qualify --slot myprodlet --revision <SHA256>` runs a bounded source test. `promote --changes-json '{"myprodlet":"<SHA256>"}' --expected-json '{"myprodlet":null}'` commits the selected **local source pointer only** if dependencies and expected current heads permit. `status` and `audit` read back the local selection and event chain. The caller must supply actual files; these commands are an interface contract, not evidence that such a named prodlet has been qualified or installed. On Windows the `--db` path can be a private local file path.

A two-prodlet cohort uses `{"engine":"<REV2>","ui":"<UI_REV2>"}`, with both `expected` old revisions. If an active `ui` revision pins `engine` R1, promoting engine R2 alone fails and retains both prior heads. A rollback is the same atomic operation with previously qualified, compatible revisions. The active pointer cannot certify the underlying real product's usefulness.

## Qualification ladder and CoLOTS closure

| Layer | Claim that can be earned | Still needed |
| --- | --- | --- |
| C0: idea / sketch | Candidate relation or proposed prodlet | Scope, task, owner |
| C1: source builds | Source exists, immutable revision | Reproducible tested behavior |
| C2: source-tested slot | Exact artifact + local test executed, known rollback pointer | Independent acceptance contract and real receiver |
| C3: receiver-qualified CoMVP | One user-relevant task succeeds at a named runtime, including expected failure/recovery | Attested receiver, latency and baseline comparison |
| C4: dependable CoMVP | Restart, interruption, replacement and time-bound survival witnessed | Recovery, durability, independent observer |
| C5: publicly usable CoMVP | Accessible actual product, rights, consent, safety, feedback and public destination verified | Authorized publication and external acceptance |

The controller demonstrates C2 behavior on isolated fixtures only. It cannot attest C3-C5 or grant promotion authority.

**CoLOTS / closure tracking** belongs on the existing operations register, not a replacement master list. For each prodlet record `selected_source_head | source_test_receipt | actual_receiver | MVP_task | contract_version | dependent_slots | rollback_pointer | last_good_seen | regression_delta | next_verification`. `CLOSURE_RATIO = independently receiver-qualified useful prodlets / all declared active prodlets` is meaningful only with a real enumerated denominator and unbiased qualification evidence. Until then it is **UNKNOWN**, not 100% based on green CI.

**Prioritization:** favour finishing an existing user-visible vertical slice and making it dependable before enhancing its speculative feature surface. Experimental improvements proceed in separate branches, work objects or staging slots. Dependency-conflicting release promotion waits; independent research, discovery, security and CoEvo streams do not.

## Fail-closed boundaries and unresolved tests

- **Test independence debt:** version-controlled test scripts may be relaxed or replaced by their producer. Add a separately versioned, *consumer-owned* immutable minimum-use contract and reject any candidate that drops it. R0 does not certify that regression gate independently.
- **Cross-process filesystem races and custody debt:** SQLite atomic pointer transactions protect one database, not the artifact filesystem, external receivers or off-host storage. Source digest is checked before head commit but is not immutable host custody or a digital signature.
- **Authority:** no approval, consent, right to deploy or native rickBar effect is established by a localhost test runner. A user-authenticated controller, signed reviewer or independently verifiable receiver is needed before real promotion.
- **CoStead and >24h:** no real receiver pickup, network partition test, reboot, multi-host fencing or 24-hour live Seed survival is claimed.
- **Rollback safety:** source heads can revert, but real device/services require an observed Stop, state/migration compatibility, recovery and rollback receipt.
- **Identity:** one selected source revision for a given slot is not the same as one global Orb or stable WorkID. Reuse existing identities and product surfaces.

**Next decisive CoMVP:** qualify the existing rickBar R1 local Ollama conversation as one end-to-end useful task on an authorized host, with actual readback, crash/restart recovery and independent user benefit. Retain R0's working version while new adapters and visual features evolve. The source controller can manage version selections when an authorized integration exists; it is not already installed on X2.

**Rail:** `TESTED_SOURCE_NE_USABLE_MVP | CANDIDATE_NE_SELECTED | DEPENDENT_RELEASES_ATOMIC | INDEPENDENT_WORK_NONBLOCKING | ROLLBACK_NE_REAL_RECEIVER_RECOVERY | COLOTS_NE_NEW_CHECKLIST`.
