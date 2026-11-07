# CoIngest+ to CoResourceFrontier+ | Scarcity / Human-Not-In-Loop R0

**State:** PUBLIC-SYNTHETIC_DRAFT_BRANCH / NO_RUNTIME / NO_ACTUATION / NO_ECONOMIC_OUTCOME.

**Question:** Can a bounded, explicit evaluator choose more useful independent work from ingested source-qualified options while keeping routine human involvement at zero and preserving all actual human/legal/financial gates?

This is **not an investment platform**. An ingestor, investor (capacity contributor), model, reviewer, human, device, and resource are different typed roles. A financial investment is specifically blocked without an authorized explicit gate.

## Existing source parents (do not duplicate)

- [CoResourceFrontier+](../../docs/Architecture/CORESOURCE_FRONTIER_ALLOCATOR_R0.md): discover/qualify/price/score/allocate/execute/measure/receipt/reevo, bounded scaling, source-dependent scoring and stop.
- [CoResourceAttractor+](../../docs/Architecture/CORESOURCE_ATTRACTOR_R0.md): provenance-qualified resource discovery and matching.
- [CoOmni ResourcePool+](../../docs/Architecture/COOMNI_CONTEXT_RESOURCE_FABRIC_R0_20261024.md): typed resource leases, owner/authority and privacy.
- [CoBudget Relations](https://github.com/CoCivium/CoSteward/issues/196): budget != spending authority, reviewer-hour != money, person != tradeable asset.
- [CoCheap/Scarcity Migration](https://github.com/CoCivium/CoSteward/issues/212): generation becomes cheap, verification/attention/recovery become scarce.

## CoIngest+ to allocation (candidate relational bridge)

`INGEST_SOURCE -> VERIFY_IDENTITY -> CLASSIFY_CLAIM/RIGHTS -> DEDUPE -> GENERATE_WORK_OPTION -> MAP_SCARCITIES -> ELECT_BOUNDED_WAVE -> VERIFY -> RECEIVE -> MEASURE -> CORRECT/STOP`.

No retrieved document supplies authority. Work is simulated only on a synthetic fixture. *Ingestors* identify candidate tasks; a selector invests scarce capacity. *Investors* in the economic sense require separate verified ownership, authority and rights.

Resources are typed as vector constraints, not flattened into one apparent currency: CPU units, energy units, reviewer minutes, human minutes, cash cents, and worker slots. Confidence and synthetic benefit/risk are deliberately fixed fixture inputs to enable reproducible selection, **not** measured real-world economic returns. No empirical calibration claim. The exhaustive selector compares valid combinations of at most sixteen qualified options, and stops beyond that size.

A zero-human candidate is **not** infinitely efficient: report projected human minutes avoided, projected unattended minutes, human-free candidate count, and *actual* measured autonomy as `NOT_MEASURED`. No ratios with zero denominator. Preserving zero-human execution does NOT erase human rights, permissions or emergency stops.

## Open option space versus bounded embodiment

The potentially unbounded number of future *ingestables*, generated relations, hypothetical work objects and outputs is an **addressable option space**, not a currently allocated workforce or storage guarantee. Actual parallelism depends on finite, time-varying budgets, work independence, proof capacity, privacy/locality and authenticated permissions. Fanning out one flawed source to one million correlated models is not one million independent proofs.

The machine receipt therefore preserves **three distinct sets**: \`selected\` for a bounded simulated choice, \`deferred_qualified_options\` for valid possibilities that remain dormant, and \`held\` for source, authority or safety failures. An increase in verified capacity can re-elect an option from dormancy without inventing a new authority. There are **zero actual executors** in this fixture. A selection or hypothetical 'investment' is neither an investment transaction nor operational deployment.

Amplification should be measured as *accepted beneficiary value and validated information gain per unit of limiting resource* with separate denominators and externalities, not simply by the quantity of input and output objects. Use a Pareto frontier if two values cannot fairly be converted to one scalar. The fixed toy score here demonstrates only reproducible comparisons, not calibrated cross-human or economic value.

**Hypothesis to test over time:** Verified reusable outputs may improve future option generation, selection, verification and recovery, producing compounding useful capacity. Unbounded possible outputs do not imply that an infinite number can be rendered, verified, delivered or adopted in finite wall time.

## Repeatable test

```sh
python -m unittest discover -s examples/coingest_scarcity_r0 -p 'test_*.py' -v
python examples/coingest_scarcity_r0/allocator.py --fixture examples/coingest_scarcity_r0/fixture.json --output /tmp/coingest-scarcity-receipt.json
```

Fixture generation script is a deterministic helper. Runner/CI should test the already committed fixture rather than regenerate it silently.

Compare `first_fit` and `frontier` on exactly the same synthetic data. The latter may score better **on this constructed dataset**; that says nothing about real task benefit, future investor returns, live worker scaling, actual unattended uptime or comparative performance across a representative population.

## Needed real receiver proof

An independent authorized producer ingests a rights-cleared source; a different receiver parses the exact pinned source and creates an option. Separate evaluator checks the source and selected work. Run a baseline and candidate policy with actual time/energy/reviewer costs recorded, preserve null results. Only then consider autonomous *read-only* work on distinct failure domains, and only with bounded leases and rollback. Remain HELD on private data, public outreach, consequential spending, contract approvals, human welfare and control-plane changes.

Rails: `INGESTED_NE_TRUE | OPTION_NE_ALLOCATION | ALLOCATED_NE_EXECUTED | AVAILABLE_NE_AUTHORIZED | HUMAN_ZERO_NE_INFINITE | NO_HUMAN_TOUCH_NE_NO_GOVERNANCE | SELF_GRADE_NE_RECEIVER_PROOF | INVESTOR_NE_INGESTOR | UTILITY_POINTS_NE_DOLLARS | MANY_WORKERS_NE_INDEPENDENCE | HISTORIC_PROOF_NE_CURRENT_DEPLOYMENT`.
