# CoObject^^ / OVP R0: receiver-relative whole-task closure

**State:** `PUBLIC_SAFE_REVIEW_CANDIDATE__SOURCE_ONLY__NOT_CANON_NOT_DEPLOYED_NOT_RECEIVER_QUALIFIED`  
**WorkID:** `OVP_COOBJECT_CLOSURE_R0_20261109`  
**Purpose:** Prevent a green component or attractive research PR from being mistaken for a complete, dependable, usable product.

## Decision

Use **existing CoObject+ Vitality** for object-level identity, dependencies and repair; **existing CoGrace+** for phase/receiver-relative sufficiency; **existing CoMVP+ / CoLockStep+** for preserved selected heads, minimum-use acceptance and atomic incompatible release cohorts. Add a *derived, read-only* closure view, **OVP R0**, across them. Do **not** build a duplicate scheduler, invent a second source-of-truth, silently reclassify source CI as receiver acceptance, or global-lock unrelated fronts.

**OVP** means *Optimal Viable Prodlet-set candidate*, with *optimal* interpreted as a **Pareto-eligible, receiver-relative choice** among available sets at a particular time, under rights, safety, continuity and useful-task constraints. It is not a magic global maximizer. A more conservative working alias is *Qualified Viable Prodlet Set*, if CoLex collision/meaning review prefers it.

**What is a prodlet?** A named, bounded receiver-useful task, including its dependency closure and failure/exit path. It may contain components in different modules. A collection of individual passing modules is not automatically a viable prodlet-set.

### CoObject^^ notation proposal

- `CoObject^receiver.task.time^` is an optional **human-readable scoped lookup**: inspect the object's task-relevant dependency and proof closure for receiver, task and observation time. Never parse it as an authority grant.
- `CoObject^^` is **an unresolved whole-view query**, not a promise that the entire universe is represented: the caller must supply/derive an authorized receiver, task, scope and time before query resolution. If scope is unclear, fail closed for effects and ask or show a bounded read-only candidate.
- No existing CoObject identifier or canonical schema changes. The actual machine representation is a versioned, typed JSON manifest; punctuation is merely shorthand. A collision with existing notation must retire this shorthand without harming the underlying contract.

## Closure over the entire *relevant* story

For task T, receiver R and observation time t, `closure(T,R,t)` is the set of all **required and allowed** components reached through explicitly typed dependencies, together with currentness, rights, receipts, fallbacks, last-known-good heads and unknowns. Optional modules can be disclosed as degraded/absent without violating a core task. Never claim universal completeness outside the declared scope.

For an interactive local AI task, the minimum concern roles are:

| Role | Question | Nonclaim |
|---|---|---|
| entry | Can the receiver actually initiate the task? | A button mockup is not an input path |
| worker | Is the chosen worker qualified and reachable? | A model name is not a process |
| state | Can WorkID, context and outcomes be recovered? | A transient chat is not durable custody |
| view | Can the receiver read a meaningful result or an honest degraded state? | A green orb is not a result |
| receipt | Is source/action/result identity recoverable? | A log is not receiver ACK |
| recovery | Can interruption, retry and rollback preserve safety? | A code pointer is not a successful restart |
| permission | Are identity, consent, rights, scope and exit constraints enforced? | Policy prose is not effect authority |
| return | Can receiver feedback, contradiction or failure be attributed and routed back? | Activity does not establish benefit |

Additional context may be mandatory for a particular task: source provenance, CoStead persistence, publication rights, network independence, accessibility, or a named third-party receiver. Required roles are **minimum concerns**, not proof that eight modules suffice for any human experience.

## Object and set states

- `SOURCE_BOUND_CLOSURE`: the declared graph, version pins and field contracts are structurally coherent. **Not** a working product.
- `SOURCE_INCOMPLETE_HELD`: required role, dependency, digest, version, permission or recovery contract invalid/missing; block claims and effects.
- `SOURCE_DEGRADED_READ_ONLY`: a noncritical projection is stale/missing, but a source-bound text or accessibility fallback is available. Report it; never silently greenwash.
- `AWAITING_INDEPENDENT_RECEIVER_PROOF`: source coherent, but real user, runtime and recovery evidence absent. This is expected for the initial synthetic fixture.
- `RECEIVER_QUALIFIED`: only a separate authenticated receiver/custody test may establish the real task C3 qualification; this source validator **cannot** return it.
- `DEPENDABLE_WITH_REAL_SURVIVAL`: independent restart, interruption and time-bound recovery witnessed; not implied by CI, planned schedules or screenshots.
- `DORMANT_WITH_WAKE`, `STALE`, `BLOCKED`, `SUPERSEDED`, `RETIRED`: reuse existing CoSystemic Metabolism states; preserving a dormant path can be healthier than perpetual compute.

For stateful effects, default `fail_closed=true`. Read-only, truthful, accessible fallback may remain open under explicitly scoped rights. A fault in an unrelated independent prodlet must not block a separately compatible set. A changed required dependency must either preserve its pinned contract or enter an atomic CoLockStep+ cohort with rollback.

## OVP evaluation, not a false single score

Hard gates: privacy, rights/consent, authenticated scope for actual effects, source integrity, required dependency closure, selected-version compatibility, minimum receiver task and safe recovery/exit.

Among viable candidates compare vectors: task completion, epistemic calibration, accessibility, comprehensibility, total human/compute cost, latency, resilience, recoverability, optionality, novelty, maintenance debt, independent feedback and equitable benefit. Keep Pareto alternatives and the null/no-change option. A simpler standalone product may win. No synthetic fixture demonstrates such a win.

## 1 Seed / 1 Orb / 1 Gauge / 1 Thumb / 1 Time

- **Seed:** stable WorkID and manifest pointer to immutable source revisions, **not** a fragile monolithic file.
- **Orb:** one role-relative, accessible view with text-first fallback; **not** proof the host is running.
- **Gauge:** decomposed per-role evidence, freshness and blocker provenance, not a cosmetic total score.
- **Thumb:** one allowed reversible action (or clearly stated `HELD_NO_ACTION`), not automatic source-to-code execution.
- **Time:** distinguish source, observation, validity, receipt and independent receiver times. Missing timestamp = explicit UNKNOWN, not 'now'.

## Parallel front rule

Independent fronts may explore, simulate, code and test in parallel. Only dependency-conflicting *selected effects* require exclusive fencing and atomic cohort promotion. Use existing CoReGroup / CoLockStep election; don't create a new global coordinator. Protect the last verified head, detect provenance loss and clobber, make all unverified receiver claims `HELD`. Each front preserves an exact WorkID/source ref, contested delta, required receiver, test or wake trigger and safe exit. Fan-in deduplicates and challenges; it must never treat many independent-looking narratives as independent receiver proof.

## Source-only first proof (this packet)

`ovp_validate_r0.py` is a read-only, standard-library validator of a **synthetic** CoObject/OVP closure fixture. It checks role coverage, dependency references, pinned versions, source digest shape, explicit unknown receiver, critical freshness, no effect grants, noncritical fallback and absence of cycles. The tests include negative cases. It makes no network requests, starts no workers and changes no prodlet heads. `fixture_rickbar_x2_source_only.json` deliberately records `X2_RECEIVER_NOT_OBSERVED`; even all fixture tests passing leaves the real product held.

## Next actual product proof, without rick as mailman

Reuse the existing native/on-host rickBar and local Ollama task when an authorized X2/CoStead path exists. Independently observe **one** real prompt -> local model answer -> visible rickBar result -> durable WorkID/receipt -> clean restart -> same task resumed, with baseline timings and native escape. Then verify the exact receiver-side readback and whether it outperforms a strong simple UI. The receiver produces the receipt. No such result is claimed in this packet.

## Crosswalk, bound to existing public sources

- [CoObject+ vitality/metabolism](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COOBJECT_VITALITY_METABOLISM_R0_20261027.md) (Git blob `abe9e9bbac373fd64308ba87a92f5c924550c19b`).
- [CoGrace+ phase-relative sufficiency](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COGRACE_PHASE_RELATIVE_STEWARDSHIP_R0_20261101.md) (Git blob `9fb74d5bfb6c2b06979d856d7b576c80dd31ee85`).
- [CoMVP+ / CoLockStep+](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COMVP_COLOCKSTEP_SOURCE_RELEASE_R0_20261109.md) (Git blob `bf69a16af06a54e39dfd303e1ac9b482680fdc2e`).
- [CoAckRewise+ CoObject -> CoOrbWare -> CoMVP](https://github.com/CoCivium/CoCivium/blob/main/docs/Evolution/COACKREWISE_COOBJECT_CIV3_FRONTIER_R0_20261109.md).
- [CoGoAll outstanding receiver proof](https://github.com/CoCivium/CoCivium/blob/main/docs/Operations/COGOALL_OUTSTANDING_REGISTER_20261108.md).
- [CoQuestionCommons+](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COQA_QUESTION_COMMONS_R0.md); [CoExperimentSelector+](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COEXPERIMENT_SELECTOR_R0.md).
- [CoEmergence/DhP research, draft PR #445](https://github.com/CoCivium/CoCivium/pull/445). Research cards may inform prodlet questions, but do not make a working receiver path.

## Promotion gates

`C0_PROPOSED -> C1_SOURCE_PINNED -> C2_TESTED_SOURCE -> C3_REAL_RECEIVER_TASK -> C4_RESTART_AND_SURVIVAL -> C5_PUBLIC_USABLE`.

Current packet: **source-level closure validator and synthetic fixtures only**. No claim to C3-C5, G_d instruction, sentience, all-front adoption, CoEx ACK, or a deployed OVP scheduler. Preserve actual prior CoMVP controller as the owner of selected-source release behavior.

**Rails:** `OBJECT_NE_COMPLETE_TASK | SOURCE_CLOSURE_NE_RECEIVER_CLOSURE | OVP_NE_GLOBAL_OPTIMUM | GRACE_NE_SENTIENCE | TEST_PASS_NE_INSTALLED_APP | INDEPENDENT_FRONTS_NE_GLOBAL_LOCK | COOBJECT_CARETS_NE_AUTHORITY | FALLBACK_NE_GREENWASH | UNKNOWN_NE_HEALTHY`.
