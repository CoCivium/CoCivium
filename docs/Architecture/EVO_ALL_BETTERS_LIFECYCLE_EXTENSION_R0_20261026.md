# EVO ALL BETTERS+ Lifecycle Extension R0

**State:** `PROPOSED_LIFECYCLE_CONTRACT__BRANCH_ONLY__NOT_AUTOMATED_RUNTIME`  
**Branch:** `evo/all-betters-lifecycle-r0`

## Purpose

Extend the CoAllBloom+ operating braid beyond produce/verify/preserve to include delivery, adoption evidence, maintenance, recovery, recombination, retirement, and learning. The lifecycle is a reusable contract, not a claim that every stage is implemented or continuously running.

## Lifecycle

`DISCOVER → QUALIFY → RELATE → RESOURCE → EXPERIMENT → PRODUCE → VERIFY → PRESERVE → DELIVER → OBSERVE_ADOPTION → MONITOR → MAINTAIN → RECOVER → EXTEND → RECOMBINE → RETIRE_OR_COMPOST → REOPEN`

Stages may branch, repeat, run in parallel where safe, or be skipped with a reason. A consequential action still needs its own authorization and receipt.

1. **DISCOVER** — find existing artifacts, resources, source events, versions, prior decisions and alternatives before rebuilding.
2. **QUALIFY** — check relevance, evidence type, freshness, capability, cost, privacy, permission and uncertainty.
3. **RELATE** — create or update canonical relations with provenance, dependencies, inversions, permutations, alternatives, contradictions and not-thoses.
4. **RESOURCE** — select an available, qualified, authorized worker/tool/resource; record unavailable capabilities rather than pretending access.
5. **EXPERIMENT** — select the smallest reversible test, measurable acceptance criteria and rollback.
6. **PRODUCE** — create a versioned artifact or bounded result.
7. **VERIFY** — perform the relevant checks and record actual results, including failures and unknowns.
8. **PRESERVE** — store durable source refs, lineage, receipts, decision rationale, unresolved work and recovery instructions.
9. **DELIVER** — make a verified result available through an authorized route; distinguish drafted, queued, sent, delivery-unknown, delivered and acknowledged.
10. **OBSERVE_ADOPTION** — collect evidence of use, feedback, understanding or adoption only when available; never infer adoption from delivery or visibility.
11. **MONITOR** — check currentness, drift, regressions, resource use, accessibility, security and continuing usefulness at an explicit cadence or trigger.
12. **MAINTAIN** — repair defects and refresh dependencies within approved scope; changes require their own authorization where needed.
13. **RECOVER** — restore from durable source pointers, reroute unavailable work if authorized, and record recovery outcomes.
14. **EXTEND** — propose improvements with rationale, expected benefit, cost, risks and acceptance tests.
15. **RECOMBINE** — compose compatible artifacts/relations while retaining lineage and recording semantic loss or conflicts.
16. **RETIRE_OR_COMPOST** — retire unsafe, redundant, obsolete or unsuccessful work with reason; preserve useful lessons, dependencies and migration/rollback notes.
17. **REOPEN** — use observed outcomes, unresolved questions, failures and new resources as input to a new discovery cycle.

## Status invariant

Every useful unfinished item remains `QUEUED`, `BLOCKED_WITH_REASON`, `DEFERRED_WITH_WAKE`, or `IN_PROGRESS_WITH_OWNER_AND_NEXT_CHECK`; intentionally abandoned work becomes `CANCELLED_WITH_REASON` or `RETIRED_WITH_REASON`; only evidence-backed results become `VERIFIED_COMPLETE`.

## Better record

Each proposed better should record:
- stable `better_id` and parent/prior version;
- changed relation, rule, artifact or workflow;
- source evidence and assumptions;
- predicted benefit and affected users/surfaces;
- acceptance criteria and smallest reversible test;
- observed outcome, regressions, uncertainty and cost;
- decision: `KEEP`, `REVISE`, `REJECT`, or `DEFER`;
- rollback, successor, and next recheck/wake.

Novelty, length, or a new name is not evidence of improvement.

## Evergreen AI/IA onramp

An onramp remains evergreen through versioned bootstrap pointers, currentness checks, provider-neutral capability declarations, bounded task packets, source-linked deltas, review, and explicit wake/receiver mechanisms. It is not evergreen in operation merely because a file exists. Idle sessions do not necessarily refresh or wake themselves. No universal synchronization, continuous operation, or blanket authority is implied.

## Cross-domain relations

The relation envelope may represent physical/material, software, formal/symbolic, social, subjective/experiential, cultural/spiritual, mystical, hypothetical, simulated, metaphorical, unknown, and mixed-domain claims. Preserve the frame and epistemic type. Inclusion in the graph does not establish the independent truth of a claim.

Space, non-space, dimension, in-between, time, chaos, drift, evolution, inversion, permutation, combination, alternative, and exclusion relations may be composed where meaningful. Avoid enumerating every possible combination; generate candidates on demand, qualify them, and preserve only those that provide useful information or evidence.

## First experiment and completion boundary

Start with a synthetic fixture. Test that lifecycle transitions preserve provenance, authority, stale/missing data, contradictory alternatives, delivery-state distinctions, retirement reasons and rollback. Record which tests actually ran and their outputs. A document or commit is not proof that tests ran, a runtime is deployed, or benefits are measured.

**LATCHED EVERMORE** means durable versioned continuity, refreshable source pointers, recoverable lineage and permissioned renewal—not perpetual execution, infinite compute, universal synchronization or irreversible lock-in.
