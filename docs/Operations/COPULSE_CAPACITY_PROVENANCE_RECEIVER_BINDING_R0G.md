# CoPulse Capacity Provenance + Live Receiver Binding R0G

**State:** `CANDIDATE__PROVENANCE_CONTRACT_READY__REAL_LIVE_RECEIVER_GATE_HELD_UNTIL_ROUTE_PROVEN_ONLINE`

## Purpose

R0F proves that a fresh pressure sample can drive receiver-relative capacity election. R0G adds the two evidence relations needed before that sample receives operational weight:

1. **where the capacity claim came from**;
2. **which live receiver instance the claim belongs to**.

These are separate gates.

`PROVENANCE_NE_LIVE_RECEIVER_BINDING`

## Capacity-source provenance

Machine contract:

`schemas/copulse-capacity-provenance-v0.1.schema.json`

Verifier:

`scripts/CoPulseCapacityProvenanceR0G.py`

Every provenance object binds the exact pressure-input SHA-256 **and an exact source object whose bytes are reread by the verifier**, plus:

- sample ID;
- receiver ID;
- source class;
- source identity;
- source method;
- evidence refs;
- authority ceiling and confidentiality.

Source-object floor:

- every source class requires `source_object_ref` + exact `source_object_sha256`;
- the verifier rereads the supplied source object and fails closed on hash drift;
- `MEASURED` identifies measurement evidence;
- `DECLARED` identifies an exact declaration object and remains declaration, not measurement;
- `SYNTHETIC_FIXTURE` binds an exact fixture object and is never promoted to measurement evidence.

`PROVENANCE_NE_MEASUREMENT_ACCURACY`  
`DECLARATION_NE_MEASUREMENT`

## Live receiver binding

Machine contract:

`schemas/copulse-live-receiver-binding-v0.1.schema.json`

Gate:

`scripts/CoPulseReceiverBindingGateR0G.py`

A live receiver binding names:

- receiver ID;
- virtual-session identity;
- current embodiment ID;
- separate service identity;
- route adapter;
- observed route state;
- explicit observation time;
- currentness cursor;
- authority/confidentiality envelope;
- evidence refs.

The gate requires a fresh `ONLINE` route observation before emitting:

`PASS_LIVE_RECEIVER_BINDING`

`OFFLINE`, `UNKNOWN`, future-dated, or stale observations are held.

`ROUTE_ONLINE_NE_RECEIVER_PICKUP`  
`EMBODIMENT_NE_IDENTITY`  
`SERVICE_IDENTITY_NE_PERSONAL_LOGIN`

## Composition with R0F/R0E

Operational capacity weight requires all of:

`CAPACITY_PROVENANCE_BOUND + PRESSURE_FRESH + LIVE_RECEIVER_BINDING + AUTHORITY_COMPATIBLE`

Only then may R0E budget election influence the receiver-relative DIGEST projection.

No one gate implies the others.

## Current real-route boundary

The currently authorized primary machine route is not proven online by the machine connector at this wave's observation point.

Therefore:

`REAL_LIVE_RECEIVER_BINDING = HELD`

A browser/UI "online" indicator is useful visual evidence of that UI surface only. It does not replace the machine-route observation required by this gate.

No public artifact records device secrets, tokens, or personal-login identity.

## Next

When a real receiver route is proven online:

`BIND_VIRTUAL_SESSION + EMBODIMENT + SERVICE_IDENTITY + ROUTE_OBSERVATION -> RUN_LIVE_BINDING_GATE -> BIND_CAPACITY_PROVENANCE -> R0F_FRESHNESS -> R0E_BUDGET`

Until then, R0G can prove contract mechanics and capacity-source provenance without claiming a live receiver.

## Rails

`PROVENANCE_NE_MEASUREMENT_ACCURACY`  
`PROVENANCE_NE_LIVE_RECEIVER_BINDING`  
`LIVE_BINDING_NE_AUTHORITY`  
`ROUTE_ONLINE_NE_RECEIVER_PICKUP`  
`EMBODIMENT_NE_IDENTITY`  
`SERVICE_IDENTITY_NE_PERSONAL_LOGIN`  
`CAPABILITY_NE_AUTHORITY`

## Bounded contract canary

Exact landed verifier/schema blobs were reproduced before execution.

Contract result:

`PASS_R0G_CONTRACT_CANARY__EXACT_SOURCE_PROVENANCE__LIVE_BINDING_GATE_BEHAVIOR__NO_REAL_LIVE_RECEIVER_CLAIM`

Observed:

- MEASURED provenance: PASS;
- DECLARED provenance: PASS;
- SYNTHETIC_FIXTURE provenance: PASS;
- source-object byte drift: fail-closed with `SOURCE_OBJECT_HASH_MISMATCH`;
- synthetic ONLINE binding: PASS;
- synthetic OFFLINE binding: HOLD;
- synthetic STALE binding: HOLD;
- synthetic UNKNOWN binding: HOLD;
- provenance-schema validation: 3/3;
- live-binding-schema validation: 4/4;
- contract canary SHA-256: `E3D73E61919F44F0A7C51FFB0C6DA88E825901DCDE7340B244CFF1A328D658C7`.

Durable evidence:

`docs/Operations/proofs/copulse-r0g-contract-pass-live-binding-hold-20260923.json`

The real primary machine route remained `OFFLINE` at the post-canary connector check, so no real `PASS_LIVE_RECEIVER_BINDING` is claimed.

`SYNTHETIC_ONLINE_FIXTURE_NE_REAL_LIVE_RECEIVER`
