# CoGainLatch+ Shadow R0 | verified-gain retention, inversion and cross-surface proposal

**Observed:** 2026-11-04 22:00 UTC  
**State:** LOCAL_BOUNDED_TEST_PASS__SHADOW_ONLY__NOT_X2_RUNTIME__NOT_RECEIVER_ACK  
**Authority:** analyze, compare, and propose; **zero external device, provider, financial, publishing or outbound-message effects**.

## Why this exists

This is a **companion to**, not replacement for:

- `docs/Architecture/COBASELINE_FRONTIER_REGISTRY_R0_20261027.md`: comparable incumbents and Pareto tradeoffs;
- `docs/Architecture/COSPEEDO_EXPONENTIAL_PROOF_AND_RECURRENCE_INTERNALIZATION_R0_20261026.md`: utility-normalized, multiwindow metrics;
- `docs/Architecture/COEVOALL_MIDDLE_LATCH_R0_20261024.md`: durable user intent and wake-on-delta;
- `docs/Architecture/COSESSION_AUTOCYCLE_R0.md`: bounded lifecycle, elected effect lease;
- `docs/Architecture/COORB_LOCAL_UX_REGENERATIVE_R0_20261026.md`: calm X2 UX and inversion lenses;
- `scripts/CoEvoReceiverFanoutPlanner.py`: public-safe route planning, never proof of receipt.

`CoGainLatchShadowR0.py` adds a deterministic **shadow promotion gate** for a proposed tuning. It does not actually measure UI performance, inspect the environment, authenticate evidence references, modify configuration, or broadcast to any receiver.

## Progression

`RECEIVER-MEASURED BASELINE -> CONFIG CHALLENGER -> INVERSION/FALSIFIER -> RECOVERY TEST -> COMPARE WITHIN ENVELOPE -> SHADOW ELIGIBILITY -> AUTHORIZED MICRO-CANARY -> RECEIVER READPROOF -> LATCHED SUCCESSOR -> NEXT CHALLENGER`

A script can only establish the stage `SHADOW ELIGIBILITY`. A successful canary, real measurements, exact rollback restore and receiver proof require separately executed adapters.

## Gain gate

The candidate must:

1. Match the incumbent workload, environment, receiver, authority, privacy and measurement protocol.
2. Carry an observed UTC timestamp within a declared freshness window.
3. Bind an incumbent ID, predecessor configuration hash, new configuration hash and rollback target.
4. Have all required finite, non-boolean metrics.
5. Stay above correctness/recovery floors and **not regress any required metric**.
6. Strictly improve at least one required metric.
7. Bind source, independent challenge, inverse-falsifier and recovery-test references.
8. Be reported only as an **eligible shadow proposal**, never as a proved runtime change.

Actual references and numeric claims **must be reverified independently** before a real promotion. Missing evidence means HOLD, not an invented PASS. A tradeoff that violates simple non-regression may enter a sibling Pareto frontier under a later policy, but cannot auto-latch via this gate.

## Inverse relations / anti-gains

- Faster but incorrect -> HOLD.
- Larger fleet but greater fan-in debt -> HOLD unless verified receiver value grows.
- More event emissions but more attention burden -> HOLD.
- New UI but broken cold restart -> HOLD.
- Public-safe candidate but private receiver data -> HOLD.
- No eligible gain -> retain incumbent and sleep until a material wake condition.
- Repeated identical tuning -> dedupe; do not replay for cosmetic activity.

## X2 exemplar and cross-surface distribution

At observation time, Desktop Commander showed X2's **remote observer route** OFFLINE. The device itself may still be operating. Never infer local runtime from a previous screenshot or last saved configuration.

When a real authorized receiver adapter is available, start with a **read-only** UI/process/latency/currentness census, then one reversible private-local micro-canary, then restart and independent receiver readproof. Do not create a duplicate reconnect watcher.

Cross-surface reuse is not mass push. A candidate must be requalified against each receiver environment and consent/authority. Output route plans stay proposals. `ROUTE_PLAN_NE_TARGET_MUTATION; ROUTE_PLAN_NE_RECEIVER_PICKUP`.

## No forced exponential claim

Compare multiple time windows with stable definitions and actual human-time, compute, energy and receiver-usefulness normalization. Allow plateau, contraction and retirement. Unbounded self-generated traffic is not compounding.

## Run local synthetic demo

```
python3 scripts/CoGainLatchShadowR0.py --input ai/gainlatch/cogainlatch-synthetic-fixture-r0.json --out cogainlatch-report.json
python3 -m unittest discover -s tests -p 'test_cogainlatch_shadow_r0.py' -v
```

The synthetic fixture uses **invented values and sample:// reference names** only to exercise code paths. It is not X2 measurement or evidence of a working receiver.

## Validation

15 tests pass locally on Python 3.13 (2026-11-04). Exact source SHA-256 values and a receipt are preserved in `receipt.json` in this test package. Runtime, CoEx, canon, mass broadcast, public adoption and external integration are **unproven**.
