# CoExperimentSelector+ R0

**State:** `SELECTOR_OUTPUT__ZERO_EXECUTION`

## Purpose

Select a tiny, explainable experiment frontier from a bounded candidate pool without executing experiments and without inventing value estimates from descriptor names.

The selector consumes candidate descriptors plus explicit benefit and penalty estimates. Every estimate must carry an evidence reference.

## Benefit dimensions

- information gain
- falsifiability
- receiver value
- novelty
- independence

## Penalty dimensions

- cost
- latency
- risk
- coordination debt
- proof debt

Each value is an integer from 0 through 100. R0 does not claim that these scales are universally calibrated or commensurable. They are explicit planning estimates whose supporting evidence must be inspectable.

`METRIC_ESTIMATE_NE_MEASUREMENT_UNLESS_EVIDENCE_SUPPORTS_IT`

## No magic score

R0 does not collapse all dimensions into a single quality number.

Selection proceeds by:

1. Pareto-layer decomposition;
2. reserved-lane election;
3. preference for lower facet similarity to already selected candidates;
4. lower worst penalty;
5. higher worst benefit;
6. higher total benefit;
7. lower total penalty;
8. deterministic ID hash tie-break.

The ordering is policy, not truth.

`PARETO_NE_TRUTH`

## Reserved lanes

The input may reserve bounded slots for:

- `CHALLENGE`
- `EXPLORATION`
- `WEIRD`
- `REPLAY`
- `FAULT`

A reserve asks the selector to keep a lane represented when eligible candidates exist. It does not materialize or execute anything.

Unfilled reserves are reported explicitly rather than silently backfilled under the requested label.

## Diversity

Facet diversity is used only as a selection preference.

It does not prove evidence independence, model independence, source independence, or methodological independence.

`DIVERSITY_NE_INDEPENDENCE`

## Boundary

R0 starts no workers, provider sessions, or experiments, performs no external mutation, and grants no authority.

A selected descriptor must still move through the experiment promotion ladder:

`STATIC_VALIDATION -> SHADOW -> MICRO_CANARY -> ...`

Selection is therefore a scheduling recommendation over a bounded candidate pool, not execution authority.

## Why this helps CoStretch+

The raw CoExperimentSpace+ contains hundreds of quadrillions of syntactic descriptors. The selector makes that scale operationally useful by competing a small annotated pool for a tiny frontier rather than enumerating or materializing the entire grammar.

Future selectors can be compared as experiments themselves. The selection policy must therefore remain inspectable, versioned, falsifiable, and replaceable.

## Next

Bind the selector to a generated CoExperimentSpace+ sample and a small evidence-backed annotation fixture. Then test whether one selected micro-canary produces more verified information per unit cost than deterministic random or first-N baselines.
