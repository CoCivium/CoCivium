# CoPulseSubscriptionRouter R0A

**State:** `DETERMINISTIC_PUBLIC_SAFE_PACKET_COMPILER__NO_RECEIVER_PICKUP`

This forward-port binds the earlier CoAllPulseField+ architecture to the now-landed CoSessionSubscription+ profiles.

The router is intentionally small:

`public pulses + profile + last ACK cursor -> receiver-specific packet`

It does not mutate provider context, advance an ACK cursor, or operate on private pulses.

## Why PUBLIC-only first

GitHub is a public/shared currentness surface. Private/restricted pulses belong on private custody and must not be routed through a public-safe compiler merely because the schema supports confidentiality labels.

Any non-PUBLIC pulse in the R0A input fails closed.

## Delivery classes

- HOT
- WARM
- DIGEST
- SLEEP

R0A still carries DIGEST-class pulse entries individually and marks them `DIGEST_CLASS__NOT_YET_COMPACTED`. Actual compaction with explicit loss reporting is a later rung.

## Cursor rule

The input cursor is `last_acked_cursor`.

R0A may compute a `candidate_delivered_cursor`, but:

`CANDIDATE_DELIVERED_CURSOR_NE_ACK_CURSOR`

Only a receiver-produced exact packet readproof may advance ACK state.

## Profile validation

Every HOT/WARM/DIGEST domain in the chosen profile must exist in `ai/evolution-lanes.json`. Domain drift fails closed before routing.

## Next

Run the deterministic fixture, then prove two distinct receiver processes can read the same exact packet independently and maintain different ACK cursors without contaminating each other.

`DELIVERY_NE_PICKUP`  
`PUBLIC_ROUTER_NE_PRIVATE_BUS`  
`SUBSCRIPTION_NE_AUTHORITY`


## R0A1 epistemic-schema repair

The first forward-port fixture correctly used `HYPOTHESIS` and `HUMOROUS`, but the inherited pulse schema still exposed the older narrower epistemic enum. R0A1 aligns CoPulse+ with the landed CoEvoDelta+ epistemic classes and makes public-router validation explicit.

The public router also requires at least one evolution domain for every routable pulse and rejects unknown confidentiality labels before routing.

`FIXTURE_VALIDITY_NE_SCHEMA_VALIDITY_UNLESS_CHECKED`
