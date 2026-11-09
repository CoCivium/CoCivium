# CoFuturePull+ / G_dSide+ R0

**Status:** public candidate architecture; not an empirical demonstration of future causation, theological authority, or a live optimizer.

## Thesis
A specification says what to build. A CoFuturePull model proposes multiple desirable futures, compares them with plausible futures and authorized actions, then changes its recommendations as evidence arrives. The 'pull' is an optimization/design metaphor, not a verified physical force. G_dSide is a symbolic, exploratory hypothesis lane with no automatic privilege.

## Typed relation
```text
FutureCandidate {
  future_id, version, horizon, observer, observed_at,
  desired_outcomes[], predicted_outcomes[], uncertainty[],
  evidence_refs[], falsifiers[], competing_futures[],
  rights_constraints[], consent_constraints[], authority_ceiling,
  supply_refs[], demand_refs[], braid_refs[], resource_refs[],
  interventions[], reversible_steps[], rollback_plan,
  metric_ids[], baselines[], challenge_refs[],
  cost_budget, compute_budget, expiry_or_refresh_trigger,
  status, successor_ref
}
```
Keep goals, forecasts and permissions separate. No goal becomes a prediction; no prediction becomes permission. Stable identity and versioned evidence permit recovery and independent readback.

## Pull vector, not magical scalar
A candidate has a **typed vector** of outcome improvements and costs. Dimensions may include:
- verified utility and task completion;
- user agency, consent, fairness and affected-party rights;
- reversibility, recoverability, ecological cost and resource efficiency;
- epistemic quality, contradiction discovery, coverage and uncertainty;
- latency, money, energy and opportunity cost;
- long-horizon resilience, optionality and unexpected beneficial discovery.

Units, scales, measurement methods, baselines, directionality and uncertainty must be registered in CoMeasureFabric. Never sum unlike units or assign weights silently. Use Pareto comparisons and sensitivity analysis; show where candidates lose. Do not invent measurements or treat '325 metrics' as already available.

## Decision process
1. Form at least two candidate futures, plus a null/no-action baseline.
2. Separate normative preferences from empirical forecasts and legal/consent constraints.
3. Discover resources and competing models; explicitly record shared upstream dependencies.
4. Use CoPriMath typed relations and bounded CoGoldenBraid recombination to generate interventions.
5. Independent challengers try to falsify forecasts, find harms, or demonstrate a simpler alternative.
6. Run a reversible, cost-bounded experiment; preserve negative results.
7. Verify effect at receiver with WorkID, durable receipt, readback and recovery.
8. Update confidence, version and successors; stop when marginal expected information gain is below cost, not when someone declares 'best forever.'

## First practical benchmark: RickBar receiver
Compare:
A. source-only roadmap and more specification;
B. synthetic receiver contract with reproducible test;
C. live authorized RickBar -> Ollama -> WorkID -> durable receipt -> receiver readback -> restart recovery.

Score evidence gained per effort, measured user-visible usefulness, error/rollback rate and whether the result survives restart. A and B are legitimate stages, but must not be labeled C.

## Failure tests
- Attractive future with no causal path or measurable intermediate step.
- Spec expansion without delivered receiver result.
- One-model consensus disguised as independent confirmation.
- Optimizing a proxy metric at the expense of user benefit.
- Contradictory evidence or future forecast changes.
- Permission/rights boundary violated by an apparently high-value future.
- Recursive graph/cost explosion, stale evidence, missing metric units.
- False claims of deployment, autonomy, authority or peer acknowledgment.

## Next gate
A machine-readable candidate schema and deterministic evaluator with baseline and property tests, then an actual measured experiment. No runtime claims without independent evidence.

Anchors: [G_dSide and CoGoldenBraid](GDSIDE_COPRIMATH_GSLOOP_PUBLIC_R0.md), [CoResourceDiscovery](../Architecture/CORESOURCE_DISCOVERY_MULTIAI_R0.md), [CoGoAll outstanding](../Operations/COGOALL_OUTSTANDING_REGISTER_20261108.md).
