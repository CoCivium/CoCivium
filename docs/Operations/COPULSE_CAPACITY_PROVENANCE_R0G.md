# CoPulse Capacity Provenance + Live Receiver Binding R0G

**State:** `CANDIDATE__LOCAL_PROCESS_LIVE_BINDING__SOURCE_PROVENANCE__ACCURACY_UNPROVEN`

## Purpose

Advance R0F from fresh capacity samples to **source-bound** capacity samples tied to a receiver instance that was actually alive during the bounded canary.

R0G separates three claims that are annoyingly easy to blur:

`receiver identity | live embodiment | capacity source provenance`

None implies capacity accuracy or effect authority.

## Receiver identity and embodiment

R0G reuses the existing CoVirtualSession+/CoParticipant distinctions:

`virtual_session_id -> participant_id(RECEIVER) -> embodiment_id(LOCAL_PROCESS)`

The local process is an embodiment lease, not the receiver's durable identity.

`EMBODIMENT_NE_IDENTITY`  
`PROCESS_PID_NE_IDENTITY`

The canary requires a challenge/response while the worker process is still alive. The binding is explicitly scoped to:

`PROCESS_LIFETIME_ONLY`

## Capacity source attestation

The receiver process emits an exact R0E-compatible pressure sample plus an attestation that binds:

- receiver ID;
- live receiver binding ID;
- producing embodiment ID;
- exact pressure-sample SHA-256;
- capacity-source class;
- observation method.

The provenance gate recomputes the liveness challenge response and exact pressure SHA before allowing the sample to continue to R0F/R0E.

`PROVENANCE_NE_ACCURACY`

R0G's first canary uses `SYNTHETIC_FIXTURE` capacity self-reports. It proves who produced the exact sample, not that the number reflects real machine capacity.

## Tamper rule

Changing the pressure sample after attestation must fail:

`FAIL_CLOSED__PROVENANCE=PRESSURE_SHA_MISMATCH`

No re-attestation is inferred.

## Machine objects

- `schemas/copulse-live-receiver-binding-v0.1.schema.json`
- `schemas/copulse-capacity-source-attestation-v0.1.schema.json`
- `scripts/CoPulseLiveReceiverProbeR0G.py`
- `scripts/CoPulseCapacityProvenanceGateR0G.py`
- `scripts/CoPulseCapacityProvenanceCanaryR0G.py`

Downstream:

`R0G provenance -> R0F freshness -> R0E budget -> R0D compaction/replay`

## Bounded canary

Two distinct local worker processes consume one shared synthetic pulse field.

Expected receiver relations:

- A: independent ACK 2, declared synthetic capacity 6 -> budget 4;
- B: independent ACK 0, declared synthetic capacity 3 -> budget 1.

Both must remain alive during the provenance/freshness/budget gate and exactly replay all selected DIGEST source objects.

A tampered capacity sample must be rejected by exact hash mismatch.

## Current machine boundary

The authorized X2 Remote Desktop Commander route still reports X2 offline. Therefore R0G does **not** claim a live X2 receiver.

The screenshot-visible `online` indicator is evidence of a visible UI state only; it is not substituted for the machine-route liveness contract.

## Executed bounded canary

Exact landed R0G/R0F/R0E/R0D script Git blobs matched the bytes executed in an isolated container.

Observed PASS:

- two distinct live local receiver processes answered challenge/response while still alive;
- both emitted exact hash-bound capacity samples plus source attestations;
- live-binding schema validation: `2/2 PASS`;
- capacity-attestation schema validation: `2/2 PASS`;
- Receiver A: capacity 6, ACK 2, budget 4, exact replay 4;
- Receiver B: capacity 3, ACK 0, budget 1, exact replay 4;
- mutating Receiver A's capacity from 6 to 99 after attestation was rejected with `PRESSURE_SHA_MISMATCH`;
- both worker processes exited after the canary, confirming the binding scope was process-lifetime only;
- canary result SHA-256: `C4E2D798F5ED07A80219F488691C33CAD7516F92ADD317071A3AA980A126A5F3`.

Durable proof:

`docs/Operations/proofs/copulse-r0g-container-pass-20260923.json`

## Next

`R0H_AUTHENTIC_CAPACITY_MEASUREMENT_OR_X2_LIVE_RECEIVER_BINDING`

## Rails

`VISIBLE_STATUS_NE_RECEIVER_ROUTE`  
`PROVENANCE_NE_ACCURACY`  
`LIVENESS_NE_PERSISTENCE`  
`PROCESS_PID_NE_IDENTITY`  
`CAPACITY_SOURCE_NE_AUTHORITY`  
`LOCAL_PROCESS_CANARY_NE_X2_LIVE_RECEIVER`
