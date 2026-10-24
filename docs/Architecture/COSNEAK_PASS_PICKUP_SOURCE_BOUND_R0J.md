# CoSneak source-bound PASS / pickup audit R0J

**State:** `CANDIDATE_SOURCE_BOUND_AUDIT__NO_RUNTIME_EFFECT`

## Why

R0I usefully classified a five-object PASS sample into:

- pickup proven: 2;
- pickup unproven: 3.

But its validator checked the fixture's internal consistency rather than re-reading the five source evidence objects.

That is itself a CoSneak risk:

`FIXTURE_ASSERTION_NE_SOURCE_EVIDENCE`

R0J hardens the audit by exact-binding every sampled source blob and machine-checking the evidence used for each pickup classification.

## Exact source sample

R0J binds these repository objects at exact Git blob SHA:

1. CoEncounter R0C2 receiver qualification gate;
2. CoPulse R0C ACK/backfill;
3. CoPulse R0F pressure/freshness;
4. CoEncounter R0B independent review;
5. CoEncounter Yield R0A.

Any source-byte drift fails the audit.

## Machine evidence rules

### Pickup-proven cases

CoEncounter R0C2 must expose valid 64-hex receiver readproof hashes on both positive replays and `bounded_pickups = 1`.

CoPulse R0C must expose:

`packet_pickup = PROVEN_FOR_BOUNDED_SYNTHETIC_RECEIVER_PACKETS`

plus valid per-receiver `round2_readproof_sha256` values.

Neither case may infer semantic acceptance or integration.

### Pickup-unproven cases

CoPulse R0F must retain:

`NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`

and its local/non-landing boundary.

CoEncounter R0B must retain:

`receiver_pickup_of_match_packet = UNPROVEN`

with integration and CoEx still unproven.

CoEncounter Yield R0A must retain the no-pickup-without-readproof nonclaim.

## Result contract

Expected source-bound result remains:

```text
sample size                 5
pickup proven               2
pickup unproven             3
semantic acceptance proven  0
integration proven          0
```

The sampled scope may be called classified/closed because every object has an evidence-backed disposition.

The repository-wide question remains open.

## Meaning

This is not a new pickup deed. It is stronger evidence that the existing R0I classifications actually correspond to the sampled source objects.

The next inquiry compiler step should therefore choose among the three real pickup gaps, rather than repeatedly proving that the static fixture agrees with itself.

## Rails

`FIXTURE_ASSERTION_NE_SOURCE_EVIDENCE`  
`PASS_NE_PICKUP`  
`PRODUCER_SUCCESS_NE_RECEIVER_SUCCESS`  
`DELIVERY_NE_PICKUP`  
`PICKUP_NE_SEMANTIC_ACCEPTANCE`  
`READPROOF_NE_INTEGRATION`  
`SAMPLED_SCOPE_CLOSED_NE_GLOBAL_CENSUS_COMPLETE`  
`NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`  
`VALIDATION_IS_NOT_ACCEPTANCE`  
`NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE`
