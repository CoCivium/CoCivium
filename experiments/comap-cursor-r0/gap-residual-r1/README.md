# CoNull+ / G_dRes+ R1 | typed non-relations and discovery residuals

**State:** `PUBLIC_SAFE_R_AND_D_CANDIDATE__OFFLINE_TESTED__NOT_RUNTIME__NOT_RECEIVER_ACKED`

**CoHereNow:** One small, provider-neutral JavaScript module and reproducible Node tests extend the existing CoMap/CoOrb work with typed nulls, bounded residual measurement, and zero-process logical CoNullSeat selection. The result is a **conformance donor to PR #215 / issue #214**, not a second source of truth or a deployed CoVIA/CoOrbWare service.

## Source lineage / fit

- Existing CoMapCursor implementation, **draft PR #215**, uses one synthetic graph, four projections, explicit forecast labels, and source-bound checkpoints.
- Existing predictive input contract **merged PR #216** keeps `RAW_INPUT -> ACK_RAW -> SHADOW_PREDICT -> EXPLICIT_DECISION -> LOCAL_RECEIPT` separate.
- **Draft PR #218** provides a semantic, preview-only CoThumb center-moustache control. This R1 neither remaps an OS mouse button nor claims hardware access.
- [CoSubscriptionEcology R0](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COSUBSCRIPTION_ECOLOGY_R0.md) requires typed non-relations, privacy classes, and receiver-scoped interest. Older CoSteward experiments already suggested `CoNullSeat+` and comparison of expected versus observed signals. No new claim of independent physics is implied.
- [RD1 CoVIA parity R2](https://github.com/CoCivium/CoCivium/blob/public-projection-20261016-coevoall/rd1/covia-parity-r2/README.md) is a separate, source-bound same-host readback canary; its 20 checks are not counted toward R1's tests.

## Semantics

`CoNull+` means **why an edge is missing, withheld, or unqualified**. Valid states include `UNKNOWN`, `NOT_OBSERVED`, `OBSERVED_ABSENT`, `EXPLICIT_DISCONNECTED`, `INACCESSIBLE`, `INTENTIONALLY_PRIVATE`, `INCOMPATIBLE`, `EXPIRED`, `REJECTED`, `NOT_MATERIALIZED`, `PREDICTED_ONLY`, and `NOT_APPLICABLE`.

`OBSERVED_ABSENT` is only admissible when an observation has both a dated evidence reference and an explicit closed-world scope reference. In a partial graph, absence of an expected edge remains `UNRESOLVED`, not `DISCONFIRMED`. `INTENTIONALLY_PRIVATE` never appears, not even as an item count or identifier, in the public/ambient projection.

`G_dRes+` is **provisionally defined here** as the *discoverability / discrepancy residual* between a declared expectation and evidence. Numeric comparisons require units, explicit tolerance, comparable valid-time, two named sources and an independence claim for discovery scoring. An observation may arrive later than the event it describes. For graph comparisons, `unexpected` observed links and `disconfirmed` expected links are distinct; incomplete coverage prevents disconfirmation. Tolerance-normalized differences are **not** automatically calibrated z-scores.

This `G_dRes+` is a **local engineering usage of an ambiguous label**, not a redefinition of all earlier `G_d` references, and absolutely not empirical evidence for nonmaterial entities, spiritual claims, extraterrestrial contact, or a novel physical field. Metaphorical, theological and exploratory interpretations may remain separately typed but cannot authorize effects.

`CoNullSeat+` selects at most ten logical *read-only investigation options* by explicit marginal expected information gain minus estimated cost. It always reports zero materialized workers, zero outgoing actions and no inferred consent. Inputs are developer-assigned synthetic scores, **not trained or scientifically calibrated utility values**. A seat can remain unfilled.

## Reproduction

Run with **Node 22+** without installing packages:

```sh
node --test --test-reporter=tap conull-gdres-r1.test.mjs
python3 build_ledger.py
python3 /path/to/CoStretch-Evergreen-R5/verify_benchmark_evo.py benchmark_evo_r1.jsonl
```

The Python builder reads the TAP outcome and seals `benchmark_evo_r1.jsonl` and `RECEIPT.json` without clobbering existing outputs. New runs should use a clean directory. Outputs are fixture/contract tests, not 37 independent scientific experiments or a production SLA.

## Testable boundaries

1. Distinguish unknown, not observed, proven absence, explicit disconnect and predictions.
2. Do not convert missing/zero to each other.
3. Require closed-world evidence for negative relation claims.
4. Keep measurement valid-time distinct from observation/receipt time.
5. Reject mismatched units, correlated evidence, stale windows and synthetic links masquerading as observed.
6. Hide private nulls *and their metadata* from every public/ambient view.
7. Deduplicate identities; keep map/orb/text projections stable; ambient is summary-only.
8. Deny effect authority, spawn and hidden model inference by construction.
9. Gate optional investigation by authorization, testability, recovery and positive bounded marginal score.
10. Carry every unrun external/device/provider/media test as `NOT_RUN`, never green by default.

**Missing independent proofs:** Real hardware middle/thumb binding, actual CoVIA receiver readproof, live provider/model inference, Andrew-style first-use, Pi/Claude compatibility, Gmail Primary timing, public URL latency, media quality, retained state after provider-account retirement, and multi-device failure-domain recovery. No external messages, site updates, provider sessions, or user-device changes from this package.

`NO_EDGE_NE_NO_INFORMATION | OBSERVED_ABSENCE_REQUIRES_COVERAGE | UNKNOWN_NE_FALSE | NULL_NE_ZERO | PREDICTION_NE_INTENT | RESIDUAL_NE_ENTITY | SYMBOLIC_NE_CAUSAL | MORE_VIEWS_NE_MORE_TRUTH | EVIDENCE_NE_EFFECT_AUTHORITY | LOCAL_NE_RECEIVER_ACK`