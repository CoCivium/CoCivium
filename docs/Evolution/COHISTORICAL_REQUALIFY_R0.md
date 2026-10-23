# CoHistoricalRequalify+ / CoBenchmarkEvo+ R0

**State:** `DRAFT_BOUNDED_REQUALIFICATION_CONTRACT__NO_AUTONOMOUS_REPLAY`

## Purpose

Use historical artifacts, older LLM outputs and older agentic designs as a regression corpus.

`PRESERVE_SOURCE -> RECONSTRUCT_OLD_RESULT -> REPLAY_WITH_NEW_METHODS -> COMPARE -> EXPLAIN_DELTA -> RETAIN/MERGE/RETIRE`

## Required historical bindings

Each replay candidate should bind, where recoverable:

- original artifact identity;
- date/version;
- original prompt or task;
- model/agent/tool stack;
- sources available then;
- original output;
- known corrections/failures;
- effect/authority boundaries;
- current replacement candidate;
- replay environment;
- receipt.

Unknown historical fields remain explicit `UNKNOWN`; they are not backfilled by guesswork.

## Replay lanes

A candidate may be tested against:

- deterministic baseline;
- current hosted model;
- current local/open model;
- human review;
- single-agent;
- critic pair;
- role panel;
- simplified/no-agent alternative.

The same frozen task and acceptance criteria should be used where possible.

## Benchmark dimensions

Measure what is actually available:

- evidence coverage;
- unsupported-assertion rate;
- contradiction detection;
- source fidelity;
- useful novelty;
- reproducibility;
- human correction burden;
- latency;
- monetary cost;
- compute/energy estimate;
- privacy exposure;
- authority discipline;
- portability.

No single scalar score is required. Prefer a Pareto frontier where trade-offs matter.

## Experiment-space relation

CoStretch+ may enumerate very large or effectively open-ended candidate spaces, including trillions+ of possible experiment genomes. Enumeration does not imply execution.

`POSSIBLE_NE_INSTANTIATED`
`INSTANTIATED_NE_USEFUL`
`TRILLION_EXPERIMENTS_NE_TRILLION_LIVE_JOBS`

A Turtle+ is one bounded experimental hypothesis with:

- id;
- parent/lineage;
- task;
- role;
- substrate;
- method;
- budget;
- benchmark;
- falsifier;
- result;
- cost;
- provenance;
- disposition;
- receipt.

## Promotion bar

A candidate may progress through:

1. baseline;
2. repetition;
3. perturbation;
4. adversarial challenge;
5. transfer;
6. cross-model;
7. cross-substrate;
8. historical comparison;
9. independent reconstruction;
10. cost-adjusted comparison;
11. human usefulness;
12. simplification challenge.

A benchmark win is not truth or deployment.

## Stop rules

Stop or hold when:

- marginal information value is low;
- evidence is insufficient;
- the comparison is contaminated;
- budget is exhausted;
- independence is not established;
- a simpler method matches the result;
- the claimed effect exceeds authority.

## Output

Append machine-readable benchmark events to `ai/benchmark-evo.jsonl` or a successor elected by review. Historical source identity is preserved even when a successor is promoted.

## Limits

No automated historical replay, model invocation, external outreach, provider session creation, or live swarm is established by this document.
