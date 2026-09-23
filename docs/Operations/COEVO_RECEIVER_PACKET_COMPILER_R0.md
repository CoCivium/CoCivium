# CoEvoReceiverPacketCompiler R0

**State:** `PUBLIC_CANDIDATE__EXACT_BOUND_PACKETS__NOT_DELIVERED`

## Purpose

Compile a reviewed CoEvo fanout plan into exact receiver-specific packet candidates only when the receiver binding required for that packet is explicit.

Repository packets bind an exact target repository head. Session-currentness packets bind an exact receiver instance and currentness cursor.

The compiler does not deliver either class.

`PACKET_NE_DELIVERY`  
`DELIVERY_NE_PICKUP`

## Reference implementation

- `scripts/CoEvoReceiverPacketCompiler.py`
- receiver binding contract: `schemas/coevo-receiver-bindings-v0.1.schema.json`
- packet bundle contract: `schemas/coevo-receiver-packets-v0.1.schema.json`
- upstream route plan: `schemas/coevo-fanout-plan-v0.1.schema.json`

Inputs are:

1. a CoEvo receiver-relative fanout plan;
2. the exact source CoEvoDelta+ objects referenced by that plan;
3. an explicit receiver-binding manifest.

## Repository binding

A repository receiver binding requires:

`receiver_repo | receiver_id | current_head`

A route is held instead of packetized when:

- the source CoEvo delta is absent;
- source currentness already failed upstream;
- confidentiality or public-safety holds remain;
- receiver identity is unbound;
- exact target head is unbound;
- a target head bound during planning has since moved.

A successful repository packet therefore carries:

- exact receiver identity;
- exact expected target head;
- exact route ID;
- full source CoEvoDelta object;
- preserved downstream gates;
- receiver readproof gate;
- packet SHA-256.

It still performs no branch creation, PR creation, target mutation, publication, or pickup claim.

## Session binding

A session receiver binding requires:

`profile_id | instance_id | currentness_cursor | confidentiality_capabilities`

A HOT/WARM/DIGEST profile relation does not identify a live receiver.

The compiler packetizes a session-currentness proposal only after an exact instance and cursor are supplied. The receiver must also explicitly possess the confidentiality capability required by that delta.

`PROFILE_NE_SESSION_INSTANCE`  
`SUBSCRIPTION_NE_AUTHORITY`

The packet remains:

`PACKET_COMPILED__NOT_DELIVERED`

No provider-session push or session mutation occurs.

## Determinism and packet identity

Packet SHA-256 is computed over canonical packet-core JSON before packet identity fields are added.

`packet_id` is the first 24 hexadecimal characters of that packet SHA-256, namespaced with `packet:`.

The bundle receives its own SHA-256 after deterministic ordering.

## Bounded self-test

Before the candidate was committed, the exact candidate script bytes were exercised in an isolated local process:

- repository route proposals: 3
- repository packets compiled: 2
- session subscription proposals: 2
- session packets compiled: 2
- unsafe public route held: 1
- deliveries executed: 0
- every effect counter: 0
- every emitted packet state: `PACKET_COMPILED__NOT_DELIVERED`

Receipt:

`SELFTEST=PASS_REPO_PACKETS_2__SESSION_PACKETS_2__HOLDS_1__ZERO_DELIVERY_EFFECTS`

Bounded self-test bundle SHA-256:

`4796A0C730E218FF826FB128F644A3A5F24733A80163663AC16AC6D9ECC56F00`

Pre-commit candidate script SHA-256:

`A2B07F67BE3D05CF30F0E2BA4FDBBCD62FF03A85E0BFC67BC25B71804FBB1413`

These receipts prove only the bounded self-test behavior. They do not prove delivery, receiver readback, integration, runtime binding, or canon.

## Next gate

`PACKET_COMPILED -> PROVEN_RECEIVER_ADAPTER -> DELIVERY_RECEIPT -> EXACT_PACKET_READPROOF -> PICKUP_ELIGIBLE`

The next rung is therefore not “write everywhere.” It is a narrow receiver adapter with a delivery receipt and exact packet readproof contract.

## Rails

`PACKET_NE_DELIVERY`  
`DELIVERY_NE_PICKUP`  
`PACKET_NE_TARGET_MUTATION`  
`PACKET_NE_PROVIDER_PUSH`  
`PACKET_NE_AUTHORITY_TRANSFER`  
`NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`  
`MERGED_NE_CANON`
