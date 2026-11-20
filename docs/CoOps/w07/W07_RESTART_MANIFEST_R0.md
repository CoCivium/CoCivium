# W07 restart manifest (R0, cycle C1)

- worker_id: W07 · session_instance_id: `w07-si-43d985bc720b4b4f` (opaque, generated locally) · cycle_id: `W07-C1`
- Queue outcome (candidate `docs/CoOps/COCLAUDE_WORK_QUEUE_R0.json` @ `2f8b5d2c`, blob `861b527c…`): "Local dispatcher crash/restart/elected actuator tests", namespace `loop`
- Branch: `claude/w07-loop-20261118` from `a07f1544f83ccf13fad224328558fe77a176223b`. Every W07 file lives under `docs/CoOps/w07/`.
- **ExState: LOCAL_ONLY / LANDING_HOLD.** The branch exists only in the W07 session workspace; nothing has been pushed (see §Landing blocker).

## Current objective
Prove or falsify the CoLoop+ elected-actuator, idempotency, heartbeat and reboot-recovery properties with measurable tests, then land the evidence as an isolated candidate.

## Jobs
| job_id | Output | State |
|---|---|---|
| W07-C1-J1 inspect | `W07_LOCAL_LOOP_INSPECTION_AND_RECOVERY_TEST_R0.md` | DONE (commit `206a558`) |
| W07-C1-J2 implement | `w07_coloop_ref.py`, `W07_REF_RESULTS_R0.{md,json}` | DONE (commit `cde070d`). Its scaled results still stand, but the harness is superseded by J3's fixes (D1–D3). |
| W07-C1-J3 falsify + fix | L5 frozen-in-transaction test plus fix; defects D1–D4; `W07_C1_J3J4_RESULTS_R0.{md,json}` | DONE (this commit) |
| W07-C1-J4 production-timing spot runs | L2 ×5 and H2 ×3 at L=90/R=30/H=30 | DONE (this commit) |
| W07-C1-J5 landing package | this manifest, `w07_landing.py`, `landing/*.json`, bundle | DONE locally; landing HOLD |
| W07-C3-J1 three-flagship QA + delivery reconciliation | `c3/` (tool, QA JSON, report, contact sheets) | DONE (this commit). Candidates PASS 7/7; InSeed live body matches no repo blob |
| W07-C2-J7 Windows parity | `w07_coloop_ref.py`, `coloop_tick.py`, `w07_platform_selftest.py`, `W07_C2_J7_RESULTS_R0.json` | DONE on Linux; Windows run NOT_RUN |
| W07-C2-J6 pid guard + clock jump | `w07_coloop_ref.py` (L6, L7), `W07_C2_J6_RESULTS_R0.json` | DONE (this commit) |
| W07-C2-J1 tick + scheduler template | `coloop_tick.py`, `test_coloop_tick.py`, `CoLoopTick.TaskScheduler.TEMPLATE.xml` | DONE (this commit); template NOT registered |

## Restart instructions
1. If the workspace still exists: `cd <clone>` and `git log claude/w07-loop-20261118`. Check that HEAD has `docs/CoOps/w07/` and run `python3 -I docs/CoOps/w07/w07_landing.py verify docs/CoOps/w07/landing`; it exits 0 if every digest matches.
2. If only the bundle survives: `git clone https://github.com/CoCivium/CoCivium && cd CoCivium && git fetch <bundle> claude/w07-loop-20261118:claude/w07-loop-20261118`. The bundle needs `a07f154` as its prerequisite.
3. Reproduce the tests with `python3 -I docs/CoOps/w07/w07_coloop_ref.py {lease|idem|hb|falsify} --out x.json`. For production timing, set `W07_L=90 W07_R=30 W07_H=30` and run only L2/H2 with small trial counts (≈2 min per trial).
4. Do **not** rerun J1–J5 just because a new dispatch arrived. Reuse these results unless the source hashes below have changed.

## Verified source refs (at manifest time)
- CoCivium `a07f154`: contract blob `41832275…` (sha256 `ec169cff…3e7`); `due_work_catchup_r0.py` blob `a143e683…`.
- InSeed `1d09646`: workflows `16fde065…` and `3e73d188…`; loops `54930be5…`, `a6bf6a01…`, `d390651f…`.
- Candidate rail `2f8b5d2c`: queue blob `861b527c…`, landing contract blob `bccd5deb…`, bootcard `COWALKAWAY261118_RECOVERY_BOOTCARD_R0.md`.

## Landing blocker (exact)
- Class: **authorization**. The session's git proxy refused to inject a credential: "CoCivium/CoCivium is not in this session's authorized repository set", HTTP 403 on push, 2026-11-18T17:3xZ. `add_repo(push)` returned "link your GitHub account to let Claude access repositories". `GH_TOKEN` in the environment is invalid. Not retried.
- No other authorized transport exists in this session. A chat attachment does not count as a landing.
- **Narrowest permission that would unblock:** link the steward's GitHub account to this Claude session and add only `CoCivium/CoCivium` with contents write. On GitHub, add a repository ruleset that restricts that actor to creating and updating refs matching `claude/w07-*`, with no access to `main`, tags, Actions, Pages, settings or secrets. Reading InSeed Actions run history (next gate N2) additionally needs `actions: read` on `CoCivium/InSeed`.

## Unverified pointers (not evidence for W07)
- The bootcard states that X2 tasks CoLoopCore, CoHP_CoWaveParallelDispatch, CoBackRunner and CoTidalContinuity "were inspected and disabled", and that `dispatcher_r1.py` and `crash_test_r1.py` passed there. W07 cannot read X2, so it treats all of these as UNKNOWN.
- `docs/CoSites/INSEED_SOURCE_WRITER_GATE_20261118_R0.md` confirms the InSeed workflow configuration that W07 reported. It cites a Claude report, so it may share W07's reasoning lineage. It is a duplicate of the finding, not an independent check.

## Provenance anomaly (quarantined, not W07 output)
- On resuming at 2026-11-18T20:08Z, W07 found `docs/CoOps/w07/w07_falsify_r1.py` (sha256 `ae638ccc6d1af34a676dc446aad5676bb9362d47a40dd6d8feb0bb3634402183`, mtime 17:56:35Z) in its workspace, plus 18 harness scratch dirs and `/tmp/w07run/falsify.json` (utc 17:59:19Z). All of these were created **between W07 turns**, when no W07 process was running. Author: **UNKNOWN**.
- The file was **not executed** by W07. It was removed from the branch and moved outside the repo to a workspace quarantine. Its recorded result (L5-baseline FAIL, L5-fix 10/10 ≤ 4.418 s, L5-pidguard 5/5 no kill) matches W07's J3 finding. Because its naming and structure look like the same lineage, it is **not an independent check**. W07 will implement the pid guard (C2-J6) itself.
- No other file in the repo working tree, and nothing in the InSeed clone, changed in that window. Every W07 file still matches its recorded hash.

## Successor backlog (dependency-aware)
0. **Site delivery gates (owner-held, from C3-J1):** find inseed.com's real serving origin; elect the CoCivium front door and privately review www; configure CoPolitic hosting. W07 can rerun `c3/w07_site_qa.cjs` on any newly elected commit without a gate.
1. **W07-C2-J8 Windows self-test run (needs a Windows host, read-only):** run `w07_platform_selftest.py` and record `selftest_windows.json`. This can be combined with C2-J4 on X2.
2. **W07-C2-J2 L5 policy decision (needs steward):** choose HOLD or single-kill for STALE_LOCK in production; single-kill needs authority to terminate the orchestrator's own process.
3. **W07-C2-J3 independent rerun (needs a reviewer of different lineage):** a non-Claude worker or human reruns `lease|idem|hb|falsify` from the landed commit and posts the hashes.
4. **W07-C2-J4 X2 read-only inspection plus integration with `dispatcher_r1.py` (needs local shell on X2).**
5. **W07-C2-J5 reboot ladder rung R1 (needs J1, J4 and install authority).**
