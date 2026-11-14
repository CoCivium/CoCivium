# CoMVP+ / CoLockStep+ R0 | Usable plateaus amid continuous evolution

**Status:** `PUBLIC_RESEARCH_CANDIDATE` / `SOURCE-ISLAND_GUARD_PROPOSED` / `NO_RUNTIME_SWITCH` / `MVP_UNQUALIFIED`.  
**Observed:** 2026-11-09.  
**Scope:** release safety, compatibility and recovery. This does not supersede or auto-enforce older CoCivium release/quality gates.

## The problem we are actually solving

CoAll contains many subsystems that advance through **partially functioning states**. Some new states are improvements as research and *regressions* as user-facing products, because they interrupt one complete task, remove a fallback, change a dependency, increase hidden recovery burden or loosen safety. A high count of source tests can coexist with zero accepted receiver tasks.

Do not demand that the entire constellation evolve in one global lockstep. That is a synchronized failure and bottleneck. Instead, form **local stability islands** around an actual task and receiver. A release island is the smallest closed set of components, versions and external dependencies sufficient to reproduce that task with its proof and rollback. Independently evolving islands may use different versions of the same provider API, connected through typed adapters.

`STABLE_SOURCE_NE_USABLE_PRODUCT` and `NEWER_NE_BETTER_FOR_RECEIVER`.

## Use two different axes, not one cheerfully green progress bar

| Dimension | Allowed assessment | Strongest source-only claim |
|---|---|---|
| Research maturity | idea -> design -> isolated tests -> cross-code source verification | **SOURCE_COHERENT** |
| Receiver readiness | unknown -> documented task -> witnessed completion -> reliable recovery -> operated with currentness | **UNKNOWN** until the exact receiver independently proves a task |
| Compatibility | unresolved dependencies -> exact pinned interfaces -> regression tests -> qualified switch | **SOURCE_COMPATIBLE** |
| Custody and authority | local file -> public source -> independent receiver readproof -> authorized deployment | **PUBLIC_SOURCE_ONLY** in this PR |

An island can be advanced in one dimension and unqualified in another. **CoMVP-qualified is contextual**, e.g. `CoRun vX is usable for <one specified task> on <one permitted receiver> at <one measured time>`. It does not mean universal adoption or suitability for every capability. Every positive claim needs an actor, version, workload, environment, measured result, and independent proof boundary.

## CoMVP qualification gates per prodlet

A candidate crosses from "source demo" into **MVP for a named audience and task** only when:

1. **Whole-task completion**: an actual authorized person or independent receiver completes one defined, useful task on the intended accessible surface; output and acceptance match an objective rule. Internal mock/demo is not an independent user.
2. **Reproducibility**: source/build/object identity fixed, dependencies and supported environment declared, essential positive and negative checks repeatable.
3. **Fail-safe operation**: no unauthorized effect; failure stops safely, preserves data and prior stable version; undo/revocation is tested for permitted effects.
4. **Continuity**: exact checkpoint and durable recovery source; real restart/resume with no duplicate consequential effects and receiver readback.
5. **Supportability**: one legible entrypoint, version/currentness display, documented working fallback, observed error path and bounded upkeep.
6. **Receiver-relative truth**: no "ACK", CoStead, CoEx, canon, public availability, or useful completion inferred from the existence of code, receipts or a successful same-provider CI run.
7. **Measurable value**: a baseline of task acceptance and human active minutes; superiority claims require prospective comparison with corrections, error burden, costs and receiver benefit.

Failure or absence at a mandatory gate means `HELD_FOR_THAT_SCOPE`. An isolated partial PASS stays a partial PASS; it does not become global MVP. Later **operational qualification** adds real SLOs, monitoring/currency, incident/revocation, canary replacement and independently verified cold restore.

## CoLockStep++ versioned local release train

1. **Protect current plateau:** identify the last genuinely usable version, source revision, observable behavior, permitted receiver, active dependencies, rollback and independent readproof. If there is no previously proven usable version, mark it `SOURCE_BASELINE_ONLY`, never invent a stable product.
2. **Allow wide candidate evolution:** CoRun/CoTurtle/CoNex and alternatives work independently on immutable candidates; negative results and adversarial variants remain recoverable. Experiments cannot mutate or quietly unseat the plateau.
3. **Compile change impact:** for each changed component, traverse the typed *consumer/provider* dependency edges and check interface major, schema semantics, effects/authority, data migrations, security/consent, UX/accessibility, privacy, time/currentness and recovery. Unrelated islands do **not** wait.
4. **Compatibility gate:** reproduce the protected baseline, verify all required links, preserve old failures, run regression and explicit adversarial tests. An incompatible candidate is held, not used as a new global lowest common denominator.
5. **Shadow/canary at qualified effect boundary:** compare with the actual working task, not just an alternative thread configuration. Measure task completion, active human minutes including correction, quality, faults and rollback. Retain baseline A and evaluate independent alternative C.
6. **Elect exactly one authorized switch:** a qualified operator/actuator promotes only the affected island when mandatory receiver, authority and recovery evidence holds. Failure immediately preserves/reverts to the previous qualified plateau, with durable receipt and no hidden clobber.
7. **Release/fan-in:** update contract and downstream consumers only after exact source/effect/receiver receipts. Keep incompatible but interesting experimental branches addressable, labeled, and safely dormant.

**Global emergency coordination** is reserved for genuinely shared safety, security, identity, schema or effect-contract hazards. It should not serialize unrelated research, media, documentation or candidate experiments. `ALL_CAN_EVOLVE` does not mean `EVERYTHING_REQUIRES_THE_SAME_VERSION`.

## State transitions and measured gates

| State | Actual proof needed | Not inferred |
|---|---|---|
| `EXPERIMENTAL` | Candidate with a bounded objective | Any usable service |
| `SOURCE_COHERENT` | Exact source pins, matching typed interfaces, failure-lineage check, deterministic bounded tests | Human use, reliability, recovery |
| `MVP_QUALIFIED_SCOPE` | Named receiver, end-to-end accepted task, failure/undo/recovery, currentness and scope-bound evidence | Operations across all users |
| `OPERATED_SCOPE` | Repeated observed outcomes, availability/currentness, incident response, cold restore where required | Universal deployment or global authority |
| `REPLACED_WITH_RECEIPT` | Authorized staged switch, old fallback retained, independent readproof | Old version erased, automatic upgrade everywhere |
| `HELD_INCOMPATIBLE` | Concrete regression, missing evidence or dependency mismatch | Retirement or censorship of candidate |

A source gate may output `SOURCE_COHERENT__NOT_MVP`. This is not a low-status product; it is an accurate boundary that can be automated without pretending an independent receiver exists.

## Implemented bounded test adapter in this PR

[Source-island evaluator](colockstep.py) and [pin-bound fixture](colockstep_fixture.json) compare two immutable research snapshots in one **CoRun example**. They protect two existing source-qualified components, allow one additive differential-reference component, require compatible interface majors and dependency closure, preserve declared earlier FAIL identities, refuse pin drift and deny self-promoted MVP. The [negative tests](test_colockstep.py) include interface break, removed predecessor, stale pin, lost failure lineage, fake receiver, authority expansion, dependency cycle, broken baseline and no-clobber receipt.

Run in a checkout with Python 3.13 (no network, provider access, real release switch or subprocess effects):

```sh
python3 -B -m unittest discover -s examples/corun_r0 -p 'test_*.py' -v
python3 -B examples/corun_r0/colockstep.py \
  --manifest examples/corun_r0/colockstep_fixture.json \
  --repo-root . --out /tmp/colockstep-proof-unique
```

`candidate_source_compatible=true` means merely **no observed source-interface break in the limited manifest**. The declared historical failure IDs and source hashes do not independently prove all historical outcomes. Source pins are SHA-1 Git object identifiers, not trust signatures. The receipt SHA-256 binds the emitted local report but does not establish its truth or independent custody.

**Not yet implemented:** an adapter to a real CoBar/CoOrb/CoCivium.exe stable receiver, authenticated effect election, semantic data migrations, user-level rollback, out-of-provider cold restore, actual qualified human MVP, end-to-end capability SLOs, or cross-island production contract enforcement. A draft PR is not a deployed runtime. The existing nine-stage [CoStageReview](../../docs/Architecture/COREVIEW_PANEL_LIFECYCLE_R0.md), [AutoCycle](../../docs/Architecture/COEVOALL_LARGEST_PATHS_AUTOCYCLE_R1_20261024.md), [Civ2 federated cell release policy](../../docs/Architecture/CIV2_FEDERATED_CELL_HOSTING_R0.md), and [CoRun prospective A/B](PROSPECTIVE_AB_R1.md) remain prior contracts and separate evidence gates.

## One highest-value next evidence object

Choose a **known actually usable** CoCivium work path (not merely a green GitHub artifact), preserve the exact working version and one reproducible human/receiver task, then deliberately introduce one breaking candidate in isolation. Prove detection, retained working fallback, independently accepted task outcome, tested rollback and no new Rick relay. Until this is observed, user-facing CoMVP is **HELD**. Other unrelated experiments proceed.

`LOCKSTEP_NE_GLOBAL_BARRIER | OLDER_NE_OBSOLETE | SOURCE_COHERENCE_NE_MVP | CANDIDATE_HELD_NE_EXPERIMENT_STOPPED | COMPATIBILITY_NE_REAL_WORLD_UTILITY | RECEIVER_ACK_NE_SELF_REPORT | ONE_ELECTED_ACTUATOR | NO_SILENT_CLOBBER`
