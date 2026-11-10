# CoRun+ R0 | PriorGraph runset and honest A/B execution

**State:** `PUBLIC_SOURCE_CANDIDATE` (once PR is published) / `PASS_LOCAL_SYNTHETIC_A_B` / `NO_HOST_OR_RECEIVER_RUNTIME_CLAIM`.

## Purpose

A whole bounded unit of work, not a list of prompts, can be scheduled as a typed dependency graph with optional parallel tasks, a self-challenge stage and a same-implementation serial proxy control. Independent challengers and a true legacy-product baseline remain future gates. A completed run produces reproducible **content**, exact input identity, output identity, scoped evidence, failures and a recovery pointer. Existing CoRun+ / CoCivium.exe launcher and supervision work is *prior art*: this candidate supplies a **read-only test harness**, not a replacement for a proven local runner or CoBar.

One `WorkID` binds all the pieces:

```
SOURCE / PRIOR GRAPH -> QUALIFY -> DAG
                           |     | A serial proxy (same code)
                           |     | B bounded concurrent (same exact work)
                           |     | C self-challenge (independence HELD)
                           +--> VERIFY CONTENT EQUALITY
                                -> HASHED RECEIPT -> CHECKPOINT -> SLEEP
```

No ongoing scheduler, external network, provider session orchestration, model-agent swarms, subprocesses, local machine control, unsupervised uploads, publication on behalf of another party, or human-receiver adoption in this R0. Exactly one dispatcher executes pure allowlisted operations; parallelism does not delegate authority. No new daemon is installed. This is a candidate to be consumed by existing authorized CoRun/CoGoAll carriers later, **not** a new scheduler.

## Existing prior evidence, not a greenfield engine

Use the *exact source blobs* as reusable donors, not as proof of live runtime:

| Donor | Why it matters | Observed Git blob (SHA-1) |
|---|---|---|
| [`CoEvoAll AutoCycle`](../../docs/Architecture/COEVOALL_LARGEST_PATHS_AUTOCYCLE_R1_20261024.md) | finite parent budget; bounded fanout/checkpoint/sleep; P0-P6 transfer | `ec656b6b381d1a178d400341ad7c15d014f426a7` |
| [`CoGoAll proof pulse`](../../.github/workflows/cogoall-unattended-proof-pulse.yml) | pre-existing hourly workflow; don't fork duplicate heartbeat | `f6ef642678e26b7f0ed04d420974d92b2dcd4cc9` |
| [`CoFlow Anchor Delta`](../../docs/Architecture/COFLOW_ANCHOR_DELTA_AUDIT_R0_20261026.md) | useful throughput, recovery, bottlenecks, falsifiers, drag anchors | `1c0ac83f181904bd870ad394c891a7b10beb626b` |
| [`CoFlow 12-case sample`](../../ai/flow/coflow-anchor-delta-sample12-r1.json) | real but purposively sampled 12 prior outcomes with prior FAILs | `3550b9c75e732c65ab3580494dd38f18b28f8c18` |
| [`CoDoodle/CoNex R1`](../codoodle_conex_r1/README.md) | constrained hypothesis alternatives / challenge, NOT an actual worker launch | `64b254d5f9bbc80b70bb499da72a11ca6f54f97e` |
| [`CoFleet RickBar R4`](../../docs/UX/COFLEET_RICKBAR_R4.md) | one-screen CoHereNow, exceptions rather than a provider tab wall | `4b7def69508344ca9720a3674fe61e62cb761c3c` |

Prior conversations also describe a CoRunSupervisor, read-only CoRunObserver, CoBar -> watcher -> sidecar path, CoModule manifests, and human-first CoRun executable cards. These are **historical context**, not proof this R0 can drive them, nor grounds to overwrite those older systems. Discovery/readproof of those original artifacts remains necessary before making a migration or deployment claim.

## Runnable reproducible experiment

From the repository root, Python 3.9+ standard library (tested locally on Python 3.13):

```sh
python3 -m unittest discover -s examples/corun_r0 -p 'test_*.py' -v
# Synthetic twelve-case fixture; zero artificially introduced latency:
python3 examples/corun_r0/corun.py \
  --input examples/corun_r0/fixture.json --workers 4 --out /tmp/corun-r0-zero-UNIQUE
# Model I/O waiting for illustrating potential concurrency benefit, NOT actual receiver latency:
python3 examples/corun_r0/corun.py \
  --input examples/corun_r0/fixture.json --workers 4 --simulated-io-ms 25 \
  --out /tmp/corun-r0-delay-UNIQUE
# Read-only audit of the real, historical selected sample. Exact Git blob pin guards substitution:
python3 examples/corun_r0/corun.py \
  --input ai/flow/coflow-anchor-delta-sample12-r1.json \
  --expected-git-blob 3550b9c75e732c65ab3580494dd38f18b28f8c18 \
  --workers 4 --out /tmp/corun-r0-coflow-UNIQUE
```

The third command is **proposed** against the repo source; it was not run during the originating local test because the remote checkout could not be fetched in that execution environment. It must fail closed if the source blob changes; inspect/supersede the pin explicitly, do not remove the check to make a green badge. The first two were executed using the committed synthetic fixture. Each output directory is exclusive and contains `runset.json` and `receipt.json` with a separately checkable SHA-256.

## What was measured, without claiming magic

One local Python 3.13 run on November 9, 2026 (environment-specific, unreplicated; full event identities in `LOCAL_PROOF_R0.json`):

| Experiment | A, sequential | B, four workers | Exact outputs | Result |
|---|---:|---:|---|---|
| **No injected delay** | 1.56 ms | 1.59 ms | Equal | A slightly faster; parallel overhead wins this time |
| **25 ms artificial wait per node** | 456.47 ms | 203.30 ms | Equal | B faster in *synthetic latency* only |

In R0, **A is a same-code serial proxy, NOT a measured legacy product baseline**; B uses the same algorithm with bounded threads, and C is a same-code warning-stage, not an independent evaluator. The genuine legacy-versus-CoRun+ and independent-challenger studies remain HELD.

18 of 18 local automated tests passed **after repairing** an initial missing DAG dependency, which is preserved as `FAIL_RESOLVED`. Each run completed 18 nodes, two historical-pair checks, one aggregate, an internal counterevidence check, and one deliverable. Exact output hash is equal between arms. The challenger is the same implementation, so there is **no independent empirical reviewer**. Worker threads are not autonomous synths. **Human active minutes, user adoption, off-provider receiver pickup, operational energy/cost, true concurrency benefit and product service-level outcome all remain UNKNOWN.**

## Promotion rubric for real CoRun+ prodlets

- **Correctness and safety first:** identical expected semantics, independently challengeable source, no hidden mutations, fail closed on missing pin/receipt/permission, preserve historical FAIL and dissent. Competing arms may produce different outputs only with an explicit common evaluation rubric, never by deciding their own victory.
- **CoValue:** verified finished tasks and actual receiver benefit per **human active minute**, tracked separately from machine wall time, cost/energy, errors and human interruptions. Include time spent reviewing, correcting, recovering and handling false positives.
- **CoFlow:** critical path, queueing/waiting, duplicate labor, relay burden, unresolved proof debt, recovery time, and aged held cases.
- **CoCompetition:** A legacy/serial path, B proposed runset, C independent/adversarial alternative. Allow B to lose; no promotion without equality or independently rated better outputs. Repeat with shuffled sequence, counterbalanced assignment and independent receiver before claiming advantage.
- **CoRecovery:** checkpoint/resume, bounded retries, idempotency, isolated writer leases and cold receiver readproof must be separately tested before moving past this local pure-function prototype.
- **CoUX:** CoHereNow, best current evidence, material exceptions, one next action only at real human authority gates. Receipt drill-down is optional; no console popups by default when integrated into an existing approved surface.

### Reusable future runsets (not executed here)

1. **CoRun.Product:** source version -> design variants -> independent A/B build -> test -> first-use accessibility -> receiver return.
2. **CoRun.Research:** prior graph -> competing hypotheses -> independent data paths -> negative controls -> prediction registry -> peer challenge -> scoped result.
3. **CoRun.Media:** source + rights -> script variants -> render variants -> QC -> audience-appropriate candidate -> separately approved publication -> outcome.
4. **CoRun.Onboarding:** read-only environment checks -> adapter selection -> reversible setup proposal -> health/recovery checks -> human-visible acceptance.
5. **CoRun.Continuity:** custody inventory -> hashes -> dedupe -> fork/merge candidates -> independent cold readback -> explicit CoStead receiver ACK. Never equate local source to custody.

Current R0 is one *real executable local control*, not these five products, not a machine swarm, and not proof of beneficial acceleration in human time. Prefer an authorized adaptation of existing work over spinning up new dashboards and schedulers.

## CI verification boundary

The PR-only [CoRun source-proof workflow](../../.github/workflows/corun-r0-source-proof.yml) runs 18 offline unit tests, the source-pinned historical twelve-case CoFlow comparison, and two synthetic A/B conditions. It checks exact receipts, output equality, bounded workers, uncertainty and nonclaims. A GitHub Actions success would establish **runner-scoped test evidence**, not model-swarm autonomy, independent human benefit, CoStead custody, X2 execution, deployment, or live receiver acknowledgment. The workflow has **no schedule**, and does not modify the pre-existing hourly CoGoAll proof pulse.

## R0 differential code-path verification and R1 prospective design

A second, separately implemented [reference oracle](reference_oracle.py) computes the same evidence-summary contract without importing the DAG scheduler or copying its node/task implementation. The [counterbalanced differential runner](reference_compare.py) compares both implementations against the **same inputs** over repeated trials, preserving divergent outputs as fail-closed. The [11 adversarial tests](test_reference_compare.py) include dropped historical failures, altered counterevidence, missing/one-sided pair relations, duplicate cases, input pin drift, budget violations, and exact receipt/no-clobber checks.

[GitHub Actions run #42600686685](https://github.com/CoCivium/CoCivium/actions/runs/42600686685) completed successfully on head `2d1f0dd7f3cdf08897f05ed1d6ebeb845974da84`, including the pinned historical sample, synthetic fixture, seven differential trials per source, and SHA-256 receipts. This is **independent-code-path semantic agreement**, not a truly independent scientific source, reviewer, provider, legacy production implementation, or fair productivity comparison. The direct reference does less work than the DAG (no per-node hashes), so **timings must not be treated as a fair speed contest**.

The proposed next stage is explicitly [preregistered in PROSPECTIVE_AB_R1.md](PROSPECTIVE_AB_R1.md): real legacy A versus CoRun+ B, independently evaluated outcomes, operator and receiver human minutes, source/authority parity, counterbalanced trial order, nullable costs, recovery and stop conditions. This is a study specification, **not a conducted study**. Remain draft and do not silently promote or deploy.

## CoLockStep+ / CoMVP+ stability-island extension

The [CoLockStep / CoMVP R0 release-island contract](COLOCKSTEP_COMVP_R0.md) addresses the case where newer intermediate code breaks a previously useful user workflow. **Do not impose global synchronous evolution.** Instead, declare a closed local dependency island and protect its last proven working version while other candidates evolve in parallel.

The [source-island gate](colockstep.py), [exact pinned fixture](colockstep_fixture.json) and [15 adversarial unit tests](test_colockstep.py) are a bounded implementation in this R0 example. The protected predecessor is **source-qualified only**. It is explicitly **not** represented as a proven MVP. An additive compatible candidate may earn `SOURCE_COHERENT__NOT_MVP`, never real deployment, receiver ACK, human task completion, or cross-island synchronization merely from this check. Changed interface majors, missing dependencies, stale source pins, historical FAIL lineage loss, extra authority and fake receiver evidence hold promotion while keeping the baseline intact.

Actual **CoMVP qualification** requires one reproducible useful human/receiver task, recovery and rollback, verified rights/consent/currentness, and context-specific usefulness evidence, then separately authorized release. The [prospective A/B protocol](PROSPECTIVE_AB_R1.md) proposes such testing but has not executed it. This source-only gate is additive to existing CoStageReview, AutoCycle and Civ2 cell release policies; it does not replace them or introduce a scheduler.

## Protected public browser plateau (new scoped experiment)

[Browser canary](browser_plateau.py) identifies exact Git-blob revisions of [CoDemoWow R0](../codemow/truth-gate-r0.html) and [CoDemoWow R1](../codemow/truth-gate-r1.html), then replays both using Chromium with a 390-pixel viewport. It tests the original source qualification, unsupported-X2 claim refusal, timestamp-freshness rejection, bad-JSON refusal, reset, no JS errors, no HTTP requests and unchanged predecessor bytes.

A deliberately **broken R1 successor** is created **only inside a temporary test directory** by disabling the pinned observation timestamp predicate. The adversarial test is designed to observe the unsafe false-green result and reject the successor. The original R1 is then reloaded and verified unchanged. The GitHub Actions `browser_plateau` job uses the Playwright Chromium runtime with a pinned Ubuntu runner and exports an exact SHA-256 report/receipt if its steps pass.

This is not a deployment switchover, production rollback, independent user acceptance, second-provider reconstruction or certified CoMVP. A browser demo may work while CoBar/X2, the CoStead receiver, and independent first-use adoption remain unproven. Keep the public R0 and R1 sources unchanged; do not transfer the candidate's experimentally demonstrated false-positive behavior into the public demo.

## CoPreCursor first-task browser canary (2026-11-10)

[First-task canary](coprecursor_first_task.py) protects the existing public [CoPreCursor offline HTML](../coprecursor/index.html), exact source Git blob `773e9de7aa7c6b03bf0bc75eddb7ca0a0c8dd101`, without modifying it. Playwright Chromium walks the user-visible **Preview next → Accept in this field → Undo last acceptance** path and checks explicit reject, an in-memory synthetic private marker not leaking into local count-only receipts, hidden editor/receipt in ambient projection, reversible view switching, reset, reload clearing the draft, narrow mobile layout, no HTTP requests and no page errors. The PR CI browser job produces a run-scoped report with a SHA-256 receipt; **the report passes only if the job actually completes successfully**.

This adds **automated functional first-task evidence**, not human first-use acceptance. A 390px viewport and a scripted synthetic task cannot measure real-world usefulness, comprehension, accessibility, support load or independent receiver acceptance. The HTML intentionally does **not** persist a draft beyond reload: this confirms no hidden private retention but is not a durable restore. No X2 runtime, custom-domain product availability, CoStead/CoEx custody, production rollback or qualified MVP is implied. Keep independent first-use evaluation and authorized durable recovery as explicit open gates.

## Nonclaims

`PREEXISTING_CORUN_NE_CURRENT_RUNTIME | SAME_SOURCE_NE_INDEPENDENT_TEST | MORE_PARALLELISM_NE_MORE_VALUE | ARTIFACT_NE_ADOPTION | RUN_COMPLETED_NE_RECEIVER_PICKUP | SYNTHETIC_WAIT_NE_REAL_DEPLOYMENT_SPEEDUP | GIT_PR_NE_PRODUCTION | PR_CANDIDATE_NE_MERGED | LOCAL_IS_NOT_LANDED | ACK_NE_ASSERTION | RICK_NE_MAILMAN`.
