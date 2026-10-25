# CoOrbWare / CoEvo relation-impact shadow R0

**State:** `PUBLIC_SOURCE_CANDIDATE__DETERMINISTIC_READ_ONLY__NO_EFFECTS__NOT_X2_RUNTIME__NOT_CANON`.

## Why

The user elected `[ EVO ALL BETTERS + ]` as an invitation to evolve **everything eligible**, including the relations among objects, hypotheses, evidence, media, workers, interfaces and resources. The safe implementation is not an uncontrolled transitive write. It is a **read-only impact preview**: given one changed or proposed object, determine what *might require review*, preserve unverified connections as optional inquiry, and emit no effect.

**Relation objects are first-class nodes.** For example:

```
evidence.a --DEPENDS_ON (public/current/asserted)--> relation.r
relation.r --PROJECTS_FROM (public/current/asserted)--> view.v
```

If `evidence.a` changes, `relation.r` and `view.v` become **REVIEW_CANDIDATE_ONLY**. They are not marked false, modified, or authorized. If the second edge is only proposed, it is not traversed as a verified dependency. An inverted-view or analogy link is optional exploration, not causal propagation.

## Interfaces

- `planRelationImpact.mjs`: deterministic ES module, zero side effects and no imports.
- `planRelationImpact.test.mjs`: Node 22 policy tests; cycles, transitive dependencies, direction, relation-as-node, private-source non-disclosure, missing/currentness limits, proposed/analogy/contrast, truncation, invalid metadata, no effects.

```sh
node --test examples/conodcothumb/context_rail_r1/relation_impact_r0/planRelationImpact.test.mjs
```

Input fields: `seed_id`, `nodes`, `edges`, optional `max_depth` (0-8, default 4), optional `max_candidates` (1-32, default 24), optional `change_state` (`CANDIDATE_DELTA`, `HYPOTHETICAL`, `OBSERVED_DELTA_REF_ONLY`). All public nodes have `id`, `kind`, `privacy:"PUBLIC"`; edges have `id`, `from`, `to`, `kind`, `status`, `currentness`, `privacy:"PUBLIC"`. **Edges point upstream prerequisite to downstream affected object**, not automatically in both directions. A link of status `VERIFIED_DEPENDENCY` must be independently qualified upstream by the caller. This canary does not authenticate those labels.

Outputs: sorted candidate review list with depth and via-edge identity; optional one-hop unlike/proposed exploration; explicit depth/count truncation; `receiver_ack:false`; effects counters all zero; retained nonclaims. If a private/unknown source is unavailable for a public preview it is indistinguishable from a missing source. This PUBLIC-only canary must never be fed private or sensitive metadata in violation of its scope. It does not enforce an OS-level privacy boundary, and is not a general graph database.

## Use existing contracts, not a new authority

- [CoEvo evolution regimes](../../../..//docs/CoEvo/CoEvoTheory_v0__2026-03-24.md) for proposal versus selected mutation.
- [CoOmni context/resource fabric](../../../../docs/Architecture/COOMNI_CONTEXT_RESOURCE_FABRIC_R0_20261024.md) for bounded capacity, proof budgets, recoverable work.
- [CoMap/CoOrb temporal views](../../../../docs/Architecture/COMAP_COORB_COAHEAD_TEMPORAL_R0A_20261023.md) for visualizing lineage/currentness.
- [Existing CoEvo receiver fan-out planner](../../../../scripts/CoEvoReceiverFanoutPlanner.py) for *separate* target mapping and delivery gates.
- [CoTurtle/CoOrbWare context rail](../README.md) for the existing elected interface, rather than another gesture or controller.

This R0 only identifies **candidate downstream dependencies**. It must not submit changes to the fan-out planner, push to sessions, notify people, access models/devices, or infer receiver pickup. A future read-only adapter may consume its selected candidates, qualify exact evidence and currentness, and then produce a separate mutation proposal with review and authority. No automatic propagation of truth, falsity, rights, or consent.

### Proof ladder

`SOURCE_EXISTS -> SOURCE_READBACK -> NODE_POLICY_TEST -> CI -> INDEPENDENT_REVIEW -> CANARY_EFFECT -> RECEIVER_READPROOF -> ADOPTED`

Before explicit source-bound performance tests, neither performance gains nor reduction in human work is established. The graph is bounded to 128 PUBLIC nodes, 256 PUBLIC edges, max traversal depth 8 and max 32 candidate outputs. The **logical universe is much larger than the active preview**. Cycles terminate; cap exhaustion is reported as incomplete rather than quietly suggesting full coverage.

`TOUCH_NE_MUTATION | ALIAS_NE_IDENTITY | RELATED_NE_DEPENDENT | EDGE_LABEL_NE_INDEPENDENT_PROOF | CANDIDATE_NE_ACCEPTED | NO_RELAY_WITHOUT_RECEIVER | LATCHED_EVERMORE_NE_ALWAYS_ON_EXECUTION`.
