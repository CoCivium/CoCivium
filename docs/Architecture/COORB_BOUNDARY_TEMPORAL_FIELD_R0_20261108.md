# CoOrbBoundary+ | Permeable, Projective, Temporal Field R0

Status: PUBLIC RESEARCH CONTRACT / NOT DEPLOYED. Date: 2026-11-08.
Scope: CoOrb, RickBar, CoTime, CoFuturePull, CoMeasureFabric, CoSuccession.
No claim of live telemetry, autonomous foresight, or X2 receiver integration.

## Thesis
The Orb's boundary is an inspectable relational interface, not a decorative perimeter. Version identity must bind core state, boundary policy, outward projections, temporal claims, and recovery evidence. The display is a projection of evidence, never its source.

## Typed primitives
- **OrbVersion**: stable orb_id, immutable revision id, parent revisions, core state hash, boundary policy hash, projection set root, observation time, valid-time range, provenance, receiver status.
- **BoundaryFacet**: facet_id, direction (inbound/outbound/bidirectional), capability/resource/relationship type, authority principal, consent scope, trust zone, expiry, quota, revocation path, ingress/egress receipt.
- **ProjectionRay**: origin version, target identity/domain, direction vector (semantic, spatial, temporal or capability), horizon, predicted effect, expected receiver, confidence method, falsifier, cost, authority, status.
- **TemporalEnvelope**: event_time, observed_time, recorded_time, valid_from/to, forecast_horizon, clock source, uncertainty, causal predecessors. Do not collapse future forecast into present fact.
- **CrossingReceipt**: WorkID, source and target identities, policy decision, input/output hashes, checkpoint, timestamp, observer identity, effect evidence, receiver ACK or HELD.
- **FieldObservation**: measurement name, unit, method, instrument version, baseline, uncertainty, coverage, last observed, evidence reference.

## Temporal modes
Past = sourced and versioned records, with revision history; Present = current observations with freshness/coverage; Future = conditional forecasts and proposed interventions, never facts; Counterfactual = separately labeled alternatives. CoTime is a typed coordinate and uncertainty model, not merely a clock label.

## Version change and visual semantics
An Orb revision changes when its material core, boundary policy, authorized crossings, projection graph, or verified observations change. Display-only changes have a separate renderer version. No silent overwrite; record parent and supersession. Show observed core, policy boundary, pending projections and speculative halo differently. Never use glow, size, or color alone to assert verified capability. Accessible text labels and evidence links remain primary.

## CoOmni projection
Project across space, devices, institutions, models, relations, scale, and temporal horizons. Each ray must be finite, typed, budgeted, and independently challengeable. An infinite-looking UI is not permission for unbounded network, compute, financial, or privacy effects.

## Evaluation
1. Can an independent observer reconstruct OrbVersion and its parent from receipts?
2. Can an unauthorized crossing be rejected and logged without leaking its payload?
3. Can a permitted crossing be revoked and recovery proven?
4. Can an outdated observation be distinguished from a fresh one?
5. Can a forecast be scored later against a specified outcome and baseline?
6. Can a projected receiver independently ACK a WorkID?
7. Does the Orb survive a restart with the same evidence lineage?
8. Can a different model reproduce the same field view from the same signed or hashed source set?
9. Does a boundary-policy revision visibly alter only authorized facets?
10. Can a human distinguish observed, predicted, proposed and unknown without reading a CLI?

## First product test
In existing CoBar/CoOrb, expose a read-only OrbVersion card with revision, source head, observation age, boundary policy, projected WorkIDs, forecast horizon, and receiver status. One authorized local crossing from RickBar -> Ollama -> durable receipt -> independent receiver is the first effectful test. Until then mark SOURCE_ONLY or HELD, never ACTIVE/ACK.

## Anti-confusion rails
Public technical design by default; personal data, secrets, device identifiers and credentials remain protected. No cross-session impersonation. One elected actuator per fenced effect. Predictions cannot authorize their own execution. Independent receiver evidence cannot be replaced by agent testimony. Preserve null, unknown, failed and contradictory observations rather than forcing false precision.
