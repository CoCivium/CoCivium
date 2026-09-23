# CoReceiverReadproof R0

**State:** `PUBLIC_CANDIDATE__EXACT_RECEIVER_ACK_CONTRACT__NO_PICKUP_YET`

## Purpose

Define the minimum exact-object proof a **distinct elected receiver** must return before a landed CoEvo packet is eligible to advance from `LANDED` to `PICKED_UP`.

Sender-side destination readback is insufficient.

`DESTINATION_READBACK_NE_RECEIVER_PICKUP`

## Required proof

A readproof binds:

- receiver identity;
- receiver context/instance;
- packet ID and SHA-256;
- delivery receipt identity;
- destination repository/path;
- landing commit and Git blob SHA;
- receiver read method;
- exact-object match;
- exact-packet-only coverage;
- receiver disposition.

Machine contract:

`schemas/coevo-receiver-readproof-v0.1.schema.json`

## Lifecycle rule

A valid receiver-produced readproof may make:

`LANDED -> PICKED_UP`

eligible.

It does not itself prove:

- semantic acceptance;
- baseline integration;
- CoEx;
- canon;
- runtime effect;
- scientific or factual correctness.

`PICKED_UP_NE_INTEGRATED`  
`READ_NE_ACCEPTED`

## Receiver disposition

The receiver may return:

- `READ_ONLY_ACK`
- `ACCEPTED_FOR_REVIEW`
- `DEFERRED`
- `REJECTED`

All four can prove that the exact packet was read. Only the latter fields describe receiver disposition; none silently imply integration.

A rejection is useful negative knowledge, not a transport failure.

## Canary status

GitHub adapter canary packet:

`packet:50AC4F6AFA73BA9A8256C473`

Delivery receipt:

`receipt:github-r0:50AC4F6AFA73BA9A8256C473`

Current proven lifecycle state:

`LANDED`

Current receiver pickup state:

`UNPROVEN`

No readproof is fabricated merely because the sender can read the destination back.

## Rails

`NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`  
`DESTINATION_READBACK_NE_RECEIVER_PICKUP`  
`PICKED_UP_NE_INTEGRATED`  
`READ_NE_ACCEPTED`  
`REJECTED_NE_USELESS`
