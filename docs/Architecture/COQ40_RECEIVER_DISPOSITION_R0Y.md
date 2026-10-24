# Q40 Receiver Disposition over Machine Receipt R0Y

**State:** `PASS_BOUNDED_RECEIVER_DISPOSITION_OF_MACHINE_RECEIPT__SEMANTIC_CLAIM_NOT_PROMOTED`

## Purpose

R0V proved that a pre-existing machine-readable task could be consumed on X2 by a one-shot deterministic local consumer, which emitted a hashed read-only receipt and exited.

R0X then proved the trigger-neutral inbox / lease / receipt state machine synthetically.

R0Y tests the next earned boundary:

> Can a receiver accept the emitted receipt as evidence of a bounded deed without silently accepting every semantic claim inside that receipt?

This separates **receipt acceptance** from **semantic acceptance**.

`RECEIPT_ACCEPTED_NE_ALL_RECEIPT_CONTENT_ACCEPTED_AS_TRUTH`

## Bound source

R0V receipt facts:

- task id: `r0v.currentness-read.cobar-control-view`
- task SHA-256: `A1FEF1389B6ABC2FAF43C2A75204292B33CA1ECFA0DCB0CBB1F6D6C87CD41929`
- target SHA-256: `E72555AFC67CA5B4FD54D0A9327C428F460C04B88A7047441648EFD21556A42A`
- receipt SHA-256: `240B7F90C07AB737018F33D0375805FC70E2451E885DA1E2C06D0A5E136AF5A2`
- effect class: `OBSERVE`
- authority ceiling: `READ_ONLY_LOCAL`
- target writes: `0`
- repository mutation from worker: `0`
- public effects: `0`
- authority changes: `0`
- persistent worker installed: `false`

The receipt also carried:

`PARK_AS_STALE_VISIBLE_PROJECTION`

That disposition is **not** promoted to semantic truth merely because the machine emitted it.

## Receiver gate

The receiver accepts the receipt as bounded execution evidence only when all of these are true:

1. exact task identity is bound;
2. exact target hash is present;
3. exact receipt hash is present;
4. authority ceiling remains read-only;
5. effect class remains observe-only;
6. all material effect counts are zero;
7. no persistence was installed;
8. the receipt does not claim provider exit, semantic truth, or cross-failure-domain independence;
9. the receiver records semantic disposition separately.

## Result

Receiver disposition:

`ACCEPT_RECEIPT_AS_BOUNDED_EXECUTION_EVIDENCE`

Semantic disposition:

`HOLD_UNDERLYING_STALENESS_CLASSIFICATION_AS_RECEIVER_RELATIVE`

Why:

The receipt proves that the local consumer read the exact target and emitted the stated bounded evidence. It does **not** prove that the entire semantic state behind the target is stale.

This preserves:

`STALE_PROJECTION_NE_STALE_SEMANTIC_STATE`

## What this advances

`MACHINE_RECEIPT_RECEIVER_DISPOSITION = PROVEN_BOUNDED`

`RECEIPT_ACCEPTANCE_WITHOUT_SEMANTIC_OVERCLAIM = PROVEN_BOUNDED`

`LOCAL_MACHINE_DEED_CHAIN = TASK -> CONSUMER -> RECEIPT -> RECEIVER_DISPOSITION`

The execution step still does not require a model call.

## What remains open

- ChatGPT-independent trigger;
- signed task authenticity;
- signed receipt authenticity;
- persistent local worker;
- cross-host/site/provider failure-domain independence;
- provider exit completion;
- receiver acceptance of future semantic classifications without separate evidence.

## Next earned rung

Do not install persistence merely to continue the sequence.

The next materially stronger bounded proof is **task/receipt authenticity semantics**: distinguish a hash-bound object from a cryptographically authenticated object, define what key/identity relation would be required, and prove that unsigned-but-hash-bound local receipts cannot silently acquire signer authority.

That should remain contract/fixture work until a real signing identity and authority chain are separately justified.

## Rails

`RECEIPT_ACCEPTED_NE_ALL_RECEIPT_CONTENT_ACCEPTED_AS_TRUTH`  
`RECEIPT_NE_SEMANTIC_ACCEPTANCE`  
`HASHED_RECEIPT_NE_SIGNED_RECEIPT`  
`TASK_HASH_NE_SIGNATURE`  
`STALE_PROJECTION_NE_STALE_SEMANTIC_STATE`  
`RECEIVER_DISPOSITION_NE_GLOBAL_TRUTH`  
`LOCAL_MACHINE_DEED_CHAIN_NE_PROVIDER_EXIT_COMPLETE`  
`VALIDATION_IS_NOT_ACCEPTANCE`
