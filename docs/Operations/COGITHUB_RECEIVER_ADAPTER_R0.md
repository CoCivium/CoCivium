# CoGitHubReceiverAdapter R0

**State:** `PUBLIC_CANDIDATE__BOUNDED_GITHUB_LANDING_ADAPTER__PICKUP_UNPROVEN`

## Purpose

Use the authorized GitHub content route as a bounded destination adapter for exact PUBLIC-safe CoEvo receiver packets.

This adapter proves **landing on a named candidate branch** and permits exact destination readback. It does not pretend that GitHub storage is an active semantic receiver.

`DESTINATION_READBACK_NE_RECEIVER_PICKUP`

## Authority envelope

R0 is limited to:

- the already-open candidate branch `cocivia260923/session-relational-delta-r0`;
- deliberately PUBLIC-safe synthetic or reviewed packets;
- append-only, packet-ID-derived inbox paths;
- no main-branch mutation;
- no sibling-repository write;
- no provider-session push;
- no runtime/device authority;
- no dependent-device enrollment or remote-control authority.

The dependent-device security contract remains orthogonal:

`DEVICE_SERVICE_ID_NE_PERSONAL_LOGIN`  
`PRIMARY_ROUTE_FIRST__DEPENDENT_ENDPOINT_SECOND`

## Destination

Candidate inbox:

`ai/receiver-inbox/github-r0/<packet-hash>.json`

A packet must bind the exact candidate-branch head observed immediately before the write.

The GitHub create-file operation is the no-clobber primitive: the adapter does not overwrite an existing inbox object.

## Receipt

Receipt contract:

`schemas/coevo-github-delivery-receipt-v0.1.schema.json`

A successful receipt binds:

- packet ID and SHA-256;
- destination repository and branch;
- exact precondition head;
- destination path;
- landing commit;
- Git blob SHA;
- exact destination readback at the landing commit;
- recovery pointer;
- lifecycle state `LANDED`;
- receiver pickup state `UNPROVEN`.

## Lifecycle boundary

Successful adapter delivery may prove:

`PACKET_COMPILED -> LANDED`

It does **not** prove:

`PICKED_UP | INTEGRATED | COEX | CANON | MAIN`

PICKED_UP requires an elected receiver to provide exact-object readproof distinct from sender-side destination verification.

## Recovery

The packet exists only on the candidate branch. Recovery is an explicit reviewed revert/delete of that candidate-branch object. No destructive cleanup is automatic.

## UX

Routine successful delivery belongs behind evidence drill-down. Foreground only a material collision, stale-currentness failure, confidentiality failure, adapter failure, or receiver pickup failure.

## Rails

`PACKET_NE_DELIVERY`  
`DELIVERY_NE_PICKUP`  
`DESTINATION_READBACK_NE_RECEIVER_PICKUP`  
`BRANCH_NE_MAIN`  
`LANDED_NE_INTEGRATED`  
`MERGED_NE_CANON`
