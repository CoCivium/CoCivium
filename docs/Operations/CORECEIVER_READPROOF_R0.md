# CoReceiverReadproof R0

**State:** `CROSS_TRANSPORT_INVARIANT__COPULSE_R0B_PICKUP_PROVEN__GITHUB_LANDED_CANARY_PICKUP_UNPROVEN`

## Purpose

Define the shared lifecycle invariant for advancing an exact delivered object from `LANDED` to `PICKED_UP`:

> an elected receiver, distinct from sender-side destination verification, must read the exact object and return receiver-bound proof.

`DESTINATION_READBACK_NE_RECEIVER_PICKUP`

This document is an invariant/convergence layer. It is **not** a second executable CoPulse readproof protocol.

## Executable CoPulse specialization

Current main provides:

- `scripts/CoPulseReceiverReadproofR0B.py`
- `scripts/CoPulseTwoReceiverCanaryR0B.py`
- `docs/Operations/COPULSE_TWO_RECEIVER_R0B.md`
- `docs/Operations/proofs/copulse-r0b-container-pass-20260923.json`

R0B proves bounded `PICKED_UP` for two exact synthetic PUBLIC CoPulse packets using two distinct receiver processes, receiver identities, role profiles, packet hashes, selected pulse sets, and independent ACK starting states.

It explicitly does **not** prove integration, X2 runtime, provider-session pickup, a live global bus, or two failure domains.

For CoPulse/session-currentness traffic, **R0B is the executable specialization**.

`CORECEIVER_READPROOF_NE_PARALLEL_COPULSE_PROTOCOL`

## GitHub-landed packet profile

The machine schema currently stored at:

`schemas/coevo-receiver-readproof-v0.1.schema.json`

is the **GitHub-landed CoEvo packet profile** of the shared invariant. It binds:

- receiver identity and context;
- exact packet ID and SHA-256;
- the GitHub delivery receipt identity;
- repository/path/landing commit/Git blob;
- receiver read method;
- exact-object match;
- receiver disposition.

That profile is appropriate for the bounded GitHub receiver-adapter canary because its delivery evidence includes a Git commit/blob destination.

It should not be imposed on CoPulse R0B packets, whose executable readproof has its own receiver/process/cursor/selected-pulse evidence.

## Lifecycle rule

A receiver-produced exact-object readproof may support:

`LANDED -> PICKED_UP`

for the exact bounded object it names.

It does not itself prove:

- semantic acceptance;
- ACK commit;
- working-baseline integration;
- CoEx;
- canon;
- runtime adoption;
- factual or scientific correctness.

`PICKED_UP_NE_INTEGRATED`  
`READ_NE_ACCEPTED`  
`ACK_PROPOSAL_NE_ACK_COMMIT`

## Current bounded evidence

### GitHub adapter canary

Packet:

`packet:50AC4F6AFA73BA9A8256C473`

Delivery receipt:

`receipt:github-r0:50AC4F6AFA73BA9A8256C473`

Proven lifecycle:

`LANDED`

Receiver pickup:

`UNPROVEN`

Sender-side exact destination readback is deliberately not promoted to pickup.

### CoPulse R0B canary

Two receiver-produced readproofs on current main prove:

`PICKED_UP`

for the two exact synthetic role-specific packets only.

Shared ACK mutation remains zero. The next currentness rung is explicit per-receiver ACK commit and backfill/replay.

## Convergence rule

Future transports may use different evidence fields, but the shared invariant remains:

`RECEIVER_IDENTITY + EXACT_OBJECT_IDENTITY + RECEIVER_SIDE_READ + COVERAGE_BOUNDARY + DISPOSITION`

Do not force every transport into Git commit fields, process IDs, or provider-tab concepts when those do not apply.

`PROTOCOL_NE_ONTOLOGY`

## Rails

`NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`  
`DESTINATION_READBACK_NE_RECEIVER_PICKUP`  
`CORECEIVER_READPROOF_NE_PARALLEL_COPULSE_PROTOCOL`  
`PICKED_UP_NE_INTEGRATED`  
`READ_NE_ACCEPTED`  
`ACK_PROPOSAL_NE_ACK_COMMIT`
