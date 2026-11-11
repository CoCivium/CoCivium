# CoAlienMath R0C | A simpler challenger found four false greens

**Status:** Public-safe, reproducible synthetic review candidate. Not CoAll canon, a released product, or independent human/receiver review. Date: 2026-11-11. Existing review target: [public CoAlienMath draft PR #368](https://github.com/CoCivium/CoCivium/pull/368).

## Why

A large population of models can produce attractive answers and still share a subtle error. Scaling useful discovery needs **independent failure modes, bounded challenges and deduplication before fan-in**, not repeated copies of the same opinion. This experiment checks whether the existing typed CoAlienMath R0 model is actually safer than a plain Python dictionary/JSON implementation for the same explicitly stated finite decisions.

## Frozen, inspectable inputs and fairness limits

- `ai/coalienmath/baseline_cases_r0c.json` defines **27 explicit cases** and expected outcomes, spanning typed observation/nulls, numeric residuals, log-likelihood evidence, authority restriction, observer-domain counting, decision factorization and observable differences.
- `ai/coalienmath/plain_json_baseline_r0c.py` is a separate, standard-library implementation using plain dictionaries. It deliberately does not import `model_r0.py`. It validates an explicit JSON-contract shape. The comparator `test_baseline_r0c.py` invokes **both implementations against the same recorded inputs**.
- **Same author, two implementations:** this is not an independent reviewer, double-blind test or a statistically sampled workload. It cannot establish that plain JSON is universally superior or that CoPriMath adds no value elsewhere.
- Identical expected output cannot substitute for empirical truth; fixtures cannot demonstrate real receiver acceptance, trustworthy physical observation, human comprehension or X2 user-value improvement.
- The baseline makes its own assumptions about canonical string identifiers and finite real measurements. These are explicit requirements of *this* finite contract, not a universal mathematical law.

## Prepatch adversarial outcome

Predecessor public exact Git blob `d4c3285002bc252fbee8a1f368be28136619ffd0` for `ai/coalienmath/model_r0.py`. The plain JSON implementation passed all 27 recorded decisions. The richer implementation returned a false positive or unsupported numeric result in **four distinct cases**:

| Case | Expected | Prepatch richer result | Correction |
| --- | --- | --- | --- |
| `OBS07` | HOLD for numeric subject identifier | ALLOW | Require canonical nonblank string subject/type/unit |
| `OBS08` | HOLD for numeric unit identifier | ALLOW | Same canonical-type guard |
| `RES04` | HOLD for nonfinite residual | positive infinity | Check finite subtraction and conversion; fail closed |
| `WIT03` | HOLD for numeric failure-domain label | counted as second witness domain | Require canonical nonblank string domain label |

A later narrow negative control also rejects a whitespace-aliased failure-domain label. These are **synthetic false-green defects**, not field incidents. The original failing test run is retained in the local authoring environment; its fail cases are reproducible from the above predecessor blob plus this public test package.

## Corrected candidate and outcome

- After correction: the plain dictionary baseline **27/27** and the CoAlienMath candidate **27/27**, exact outcome agreement on this finite fixture corpus.
- The existing **23** R0B unit tests are retained; **six** direct regression tests and **five** baseline comparison tests yield **34/34** unit tests, in ordinary Python and in `python -O` (local authoring run). Hosted CI must still re-run at the exact new PR head; do not borrow the prior head's green status.
- No superiority is demonstrated: **tie on the sampled decisions**. This is a useful result. CoPriMath must earn additional complexity with an independently scored held-out task and a simpler baseline.
- **Scope of claim:** source/falsifier implementation only. No receiver readproof, CoEx, public release, runtime or new mathematical discovery is inferred.

## CoOomph / CoSpeedo measurement bridge

**Unit of progress:** one externally accepted, nonduplicated, receiver-verifiable *useful closure* per eligible unit time, with cost, effort, uncertainty, failure-domain independence and beneficiary reported separately. Do not measure throughput in raw chats, prompts, tokens, worker count, files, tests or CI greens.

If the generator rate is `lambda` distinct candidates per hour, and the trusted evaluator can settle only `mu` candidates per hour, a simplified backlog changes by `lambda - mu` per hour when the queue is nonempty. Increasing workers beyond the evaluator's acceptance capacity grows proof debt. This is queue arithmetic, not a measured CoCivium production rate.

Proposed candidate decision rules, reusing [CoWaitlessExecution R0](../../Architecture/COWAITLESS_EXECUTION_R0.md), [CoLogicalSpawnPlanner R2](../../Operations/COLOGICAL_SPAWN_PLANNER_R2.md), and [CoSystemic Metabolism R0](../../Architecture/COSYSTEMIC_METABOLISM_SELF_INTERFERENCE_AUDIT_R0_20261026.md):

1. **Discover / dedupe:** bind exact work object, source version, quantity kind, authority, confidentiality, receiver and collision domain; collapse only genuinely equivalent candidates. Preserve dissenting alternatives.
2. **Admit / challenge:** limit active challenge rate by available independent verifier capacity, not by number of eager generators. Do not equate copies of one upstream source with independent witnesses.
3. **Buffer / quarantine:** keep unqualified but potentially useful hypotheses in a durable, cheap, wakeable queue. Mark `SATURATED`, `CONTRADICTORY`, `BLOCKED`, `STALE`, `DORMANT`, or `READY_FOR_CHALLENGE` instead of painting all green.
4. **Elect / actuate:** many logical explorers and passive challengers, one authorized actuation per collision domain. A passing synthetic benchmark does not mint receiver trust or authority.
5. **Release / learn:** measure independent receiver usefulness and false-green reductions against a strong simple baseline. Retire branches where additional complexity has negative marginal verified value.

**Proposed future benchmark:** 1 / 2 / 4 / 8 *genuinely instantiated authorized* workers, same bounded issue corpus, stable verifier/receiver budgets, and predeclared work-quality criteria. Compare marginal independently accepted closures, elapsed time, coordination/dedup overhead, source diversity, invalid promotions and energy/compute. Without actual workers and independent receiver evidence, these values remain **UNKNOWN**. The 18-tab manual cycling trick is not that experiment.

## Rails

`R0C_LOCAL_TEST_PASS_NE_HOSTED_PASS`; `CASE_AGREEMENT_NE_EMPIRICAL_TRUTH`; `TYPED_JSON_BASELINE_NE_INDEPENDENT_HUMAN_REVIEW`; `MORE_WORKERS_NE_MORE_ACCEPTED_CLOSURES`; `VIRTUAL_SESSION_NE_LIVE_PROCESS`; `OUTPUT_VOLUME_NE_BENEFIT`; `FAILURE_DOMAIN_LABEL_NE_PROVEN_INDEPENDENCE`; `NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`; `DO_NOT_DROP_PRIORS`.

**Next bounded proof:** same exact-head hosted CI run, then blinded independent task-level comparison, then a real receiver challenge. Do not merge, create another scheduler, mutate X2, or make a public release automatically.
