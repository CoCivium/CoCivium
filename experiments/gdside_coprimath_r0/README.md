# G_dSide+ / CoPriMath+ R0: executable synthetic comparison and mnemonic atlas

**Status:** Public-safe research candidate, proposed for review. NOT a civilization-scale economic law, validated causal model, revelation/divine preference, operating allocator, canon, merged release, or evidence of a deployed CoAll product.

This package extends the existing [CoCivium G_dSide+ / CoPriMath+ issue #377](https://github.com/CoCivium/CoCivium/issues/377) with one deliberately small, falsifiable comparative simulation and a memorable, explicit set of conceptual mnemonics. It builds on earlier [CoAllBloom](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COALLBLOOM_OPTIONALITY_BASIN_R0_20261026.md), [CoMeasure](https://github.com/CoCivium/CoCivium/issues/367), and CoMetaAttractor/CMA (a speculative philosophical framing, not a verifiable divine preference) hypotheses without promoting metaphor into authority.

## Human front door

**CoPriMath+: The mathematics of what happens between things.** An interpretive introduction, not a formal algebraic definition.

- **PRIMATH**: Provenance, Relations, Inbetweens, Membranes, Attractors, Tests, Horizons. Each is a lens requiring its own rigorous typed definition, examples, and falsifiers.
- **SIDE**: Stewardship, Inclusion, Dignity, Ecology. Only a *subset* of possible criteria for candidate G_dSide futures. Not a complete welfare function or statement about divine intentions.
- **MEME**: Memorable, Explainable, Measurable, Evolvable. A quality rubric for public education, not behavioral manipulation.

All three acrostics are verified in `test_mnemonics.py`. Spell-check correctness is *not* evidence of scientific usefulness or name distinctiveness. Preserve aliases and test collision/translation/comprehension with participants before promoting names.

## The toy world

Four communities have different needs, starting wealth and productive efficiencies. A shared renewable stock regenerates according to `0.27 * stock * (1 - stock/1800)`. Each period draws common stochastic demand/productivity shifts, shocks and replenishment disturbances, precommitted by seed. Every policy observes the same history under the same seed; its action changes only its resource allocation and extraction level.

- **Demand**: allocate proportional to need × wealth / productivity; spend the permitted extraction budget.
- **Supply**: allocate proportional to productivity squared; spend the permitted extraction budget.
- **Hybrid**: combine need-oriented and capacity-oriented shares, using 92% of the permitted budget.
- **G_dSide candidate**: equalize group satisfaction ratios using 84% of the permitted extraction budget. This intentionally encodes fairness and lower extraction *as preferences*, not as demonstrated divine requirements.
- **Random control**: random allocation shares, using the permitted budget.

All policies are constrained by `min(0.14 * current_stock, sum(need_i/efficiency_i))`. Policies have equal information and number of decision opportunities, but *different chosen extraction rates* by construction. These toy definitions are simplifications, not faithful representations of real economic schools.

## Results (80 paired seeds × 36 periods)

| Method | Mean group satisfaction | Worst-served group satisfaction | Mean productive output | Ecological stock at finish | Rights-threshold violations / run |
| --- | ---: | ---: | ---: | ---: | ---: |
| Demand | 0.76255 | 0.47758 | 149.79651 | 812.50987 | 23.4875 |
| Supply | 0.73907 | 0.49922 | 154.60392 | 812.50987 | 31.7125 |
| Hybrid | **0.82138** | 0.75427 | **141.26516** (vs G_dSide) | 894.89877 | 0.15 |
| G_dSide | 0.79163 | **0.79163** | 133.67071 | **986.30995** | **0** |
| Random | 0.71590 | 0.66718 | 141.73398 | 812.50987 | 37.9375 |

**Important correction:** Supply, not hybrid, has the highest *overall* mean productive output in this particular run. Hybrid beats G_dSide on mean output and average satisfaction. G_dSide beats hybrid on worst-served satisfaction, retained ecology, and rights violations. No single policy dominates the whole metric vector. Metrics are not commensurable without an independently chosen aggregation rule.

Rights violations here means group satisfaction below 0.5 in one period, not a legal or moral judgment. Average and worst-served satisfaction differ, as do output and useful consumption. The G_dSide algorithm's ratio equalizer directly drives its fairness metric, so its fairness advantage is expected from the model construction. A fair adversarial evaluation must vary policy weights, structural assumptions, stakeholder values, shocks, measurement access and action costs rather than report this fixed scenario as a general win. Real-world human allocation authority is not granted.

## Recursive CoGoldenBraid: SupplySide × DemandSide × G_dSide (research extension)

**Status:** proposed relational design and test plan; **not implemented in this package**, not an outcome of the numerical results above, not independent validation, and not a new economic law. This extension develops the [public CoGoldenBraid note](https://github.com/CoCivium/CoCivium/issues/317#issuecomment-6726682941) and [recursive tri-side research contribution](https://github.com/CoCivium/CoCivium/issues/377#issuecomment-6726700303) within the existing research lineage. The separate [multiobjective candidate](https://github.com/CoCivium/CoCivium/tree/candidate/gdside-multiobjective-r0-20261108) must not be silently overwritten or treated as equivalent.

**Idea:** SupplySide (capacities and constraints), DemandSide (expressed and unrepresented needs), and G_dSide (plural, revisable, future-oriented possibilities) are *lenses over one evidence-bearing graph*. Each lens can contain the other two: production depends on inputs and future resilience; present demand depends on supply feasibility and unheard needs; candidate futures themselves have resource demands, feasible supply and competing values. Recursion is bounded by explicit depth, time horizon and compute budget, never an infinite background loop.

**Typed relation proposal:** Every proposed connection retains `edge_id | subject_ref | relation_type | object_ref | source_uri | source_hash | observed_at | valid_interval | perspective | units | evidence_class | uncertainty | contradiction_refs | permission_scope | receiver_receipt?`. Distinguish observed causal effects, modeled dependencies, normative choices, contested semantics and unknowns. A content hash proves identity, not truth; absence or unknown is not zero. A future scenario is not an authorization token.

**Falsifiable next fixture:** The first **executed scoped relation probe** in `recursive_braid.py` compares (A) a one-hop flat graph and (B) a two-hop typed braid, holding the exact supplied graph and node budget fixed. The two-hop traversal recovers a seeded, unrepresented need that the one-hop query cannot reach, but this is a structural tautology of the fixture, **not** proof of predictive value, better social allocation or true causes. The false-edge negative control deliberately produces a false positive, showing why link provenance, adversarial evaluation and real source evidence are required. `test_recursive_braid.py` checks this behavior, bounded depth, graph cycles, missing sources and unbound edges. **The earlier proposed two-period allocation trial with equal compute costs, independent receiver readback, and an actual exogenous ecological shock is NOT implemented here.** Do not claim it has run.

**Measure and publish:** prediction error, worst-served outcomes, rights/consent violations, ecological stock, future option retention, recovery after shocks, uncertainty calibration, relation retrieval accuracy, source traceability, computational and coordination cost, and user intervention count. Pre-register a losing condition: recursion is *not* retained if it worsens regret, harms, instability, privacy, inference fabrication, or cost without a measured compensating benefit. Report confidence intervals and negative cases; do not re-label the existing 80 × 36 toy results as braid evidence.

**G_d boundary:** G_d remains a philosophical/metaphorical referent. Operational G_dSide denotes testable, rights-constrained candidate-future ensembles with multiple stakeholders and revisable assumptions. No proposed interpretation claims divine preferences, authority, scientific proof, production deployment, or permission to overrule humans.

## Recursive probe evidence boundary

The relationship traversal fixture is an original deterministic executable test of source-linked reachability and explicit negative controls, not a causal model or economic forecast. The flat and recursive variants have unequal allowed traversal depth by design; this means their direct cost is **not** matched and no performance advantage can be inferred. No G_dSide welfare preference, model training, external API or live allocator is involved. More rigorous blinded comparisons under matched costs, information and shock seeds remain open.

## Reproducibility

Requirements: Python 3.9+, standard library only.

```bash
python3 -m unittest discover -p 'test_*.py' -v
python3 simulate.py --seeds 80 --steps 36 --out results.json
```

Review `results.json` for full assumptions, fixed seeds and all metrics. The run is deterministic with common exogenous shock streams per seed. There is no empirical data, fitted forecasting model, or claim of statistical power. For scientific claims: preregister a wider parameter sweep and ablations; add independent outcome criteria, sensitivity intervals, controlled shocks, multiple comparator classes, and at least one case in which G_dSide loses.

## Evidence-and-authority gradients

`MEANING -> SYMBOLIC_HYPOTHESIS -> FORMAL_OBJECT -> TEST_FIXTURE -> MODEL_PASS -> FIELD_REPLICATION -> GOVERNANCE_REVIEW -> AUTHORIZED_REAL_EFFECT`.

Crossings are risk-dependent and require independent evidence, consent and reversibility. No lane (including supply, demand, G_dSide, CoMythOps, CoAura or CoTele) gets an epistemic promotion merely because it carries an attractive name.

## Public contribution and repository boundary

The included source and fixtures are AI-assisted original synthetic examples. They contain no user chat logs, personal information, credentials, device addresses, private repository paths, or private operational receipts. The surrounding CoCivium repository carries its [GPL-3.0 license](https://github.com/CoCivium/CoCivium/blob/main/LICENSE). Review rights, attribution, and dependencies before any downstream redistribution.

This package is offered as a **reviewable public research candidate**; an open PR does not mean the work has been merged, accepted, published to a production website, independently replicated, or validated on real people or economies. The related separate mathematical model on `candidate/gdside-multiobjective-r0-20261108` should be compared, not overwritten.
