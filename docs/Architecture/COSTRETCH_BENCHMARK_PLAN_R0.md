# CoStretch Benchmark Plan R0

**State:** `BENCHMARK_PLAN_ONLY__NO_WORKLOAD_EXECUTION`

CoStretch+ is a bounded benchmark-planning layer. It defines how far to test only after correctness, evidence, resource budgets, and stop predicates are explicit.

It does not mean "keep every resource at maximum utilization." High utilization can be waste, queueing, thermal throttling, coordination debt, or provider cost with no receiver benefit.

## Benchmark ladder

The planner produces a geometric ladder over:

- logical work-item population;
- active-concurrency ceiling;
- repetitions;
- wall-time budget;
- memory budget;
- optional cost budget.

Logical population may be much larger than active concurrency. A concurrency ceiling is permission to consider at most that many simultaneous units for a later canary; it is not a utilization target and does not start workers.

Every step N+1 requires step N to pass.

## High-bar vector

Do not collapse system quality into one score. Record at least:

- correctness;
- throughput;
- median, p95, and p99 latency;
- error rate;
- memory peak;
- CPU time and wall time;
- cost;
- energy/power when actually measured;
- currentness debt;
- proof debt;
- receiver value.

A faster result that loses correctness, provenance, recoverability, or receiver usefulness is not a champion.

## Stop predicates

A later executable benchmark must stop on bounded conditions including correctness regression, excessive errors or tail latency, memory/time/cost bounds, thermal or power guards when available, coordination debt exceeding receiver value, or a full step with no verified material improvement.

## Champion rule

`NO_NEWEST_WINS`

The benchmark champion is a Pareto-like evidence record, not whoever has the newest model or highest throughput. Preserve tradeoffs and bind exact inputs, runtime/version, and repeated measurements.

## Relation to CoPressure

CoPressure remains multi-dimensional. Stretch testing should discover useful operating envelopes and failure knees, then contract before coordination debt dominates useful work.

The aim is:

`verified_receiver_value / total_resource_and_coordination_cost`

not maximum resource consumption.

## R0 boundary

R0 only compiles benchmark plans. It starts no workers or provider sessions and performs no stress workload.

Next gate: run one small local or CI canary with real measurements, pin its baseline, and only then expand the ladder.
