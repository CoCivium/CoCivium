# CoVirtualWorker cold-recovery test contract R0
Date: 2026-11-20 UTC
Status: CANDIDATE ONLY. Not executed on X2 or CoStead.

## Reuse, do not fork
- Main source: examples/comodelfabric/rickbar_continuity_r1.py blob b793b3e3fab51f053998099efd985308b45cc834
- Main source: examples/comodelfabric/provider_exit_readiness_r0.py blob faa66a13c3bc241e7c2f9091ddc9f1729b4ccafd
- Main source: docs/Architecture/RICKBAR_CONTINUITY_R1_20261108.md blob 7849b55a41a0051d099067a4670d2499b43d2859
These establish a same-host SQLite/epoch prototype and pure provider-exit decision, not a distributed scheduler or real external effect receipt.

## Proposed bounded acceptance sequence
1. Confirm current elected local owner and X2/CoStead availability. Do not launch an overlapping actuator.
2. Select one authorized, non-sensitive, reversible WorkID with typed input, expected effect and authority ceiling.
3. Snapshot existing durable state and record hash and initial elected epoch.
4. Run one qualified worker, persist a checkpoint and a unique idempotency key.
5. Terminate that worker process, leaving the durable WorkID and receipt unchanged.
6. Start a new authorized worker/process, recover WorkID from disk without chat-history replay.
7. Attempt the same idempotency key again. Verify one accepted effect only and stale-epoch rejection.
8. Obtain independent exact-object receiver readback and log PASS or scoped HOLD.
9. Negative canaries: corrupt checkpoint, revoke authority, receiver unavailable; fail closed without blocking unrelated WorkIDs.
10. Record model identity, license, host, wall-clock cost, result quality and independent failure-domain limits.

## CoIA+ successor-neutral substitution canary
This is an extension of the same WorkID test, not a new scheduler, identity hierarchy or claim that IA is a settled technical category.
- Define the worker contract by capabilities, input/output schema, evidence interface and scoped authority, not labels AI, IA, successor IA, human or hybrid.
- Replace the first qualified worker with a distinct qualified successor implementation at a new fenced epoch. Retain the same WorkID, idempotency key and effect scope.
- Record worker implementation, model/provider, qualifications, lineage and independence limits. Do not count multiple personas of the same model as independent witnesses.
- Verify successor readback of the original checkpoint and authority ceiling. Reject stale-epoch actions and any attempted self-extension of authority.
- Require comparable result quality and an exact receiver-confirmed outcome. A successor's claim of superiority is not acceptance evidence.
- Negative canaries: incompatible schema, lower qualification, withdrawn lease, corrupted checkpoint, unknown worker provenance. HOLD only affected work.
- No assumption of consciousness, personhood or transfer of personality; continuity belongs to the work record.
- CoPre macro variant `Priority=ValRisk` is observed, but its formula is not defined here. Preserve the earlier explicit Value+Urgency+Deps+Risk factors pending an authoritative scoring definition; do not silently replace the scheduler.
- PASS requires an actual witnessed cross-implementation recovery. This document alone is NOT_EXECUTED.

## PASS requirements
- WorkID survives worker death and process restart.
- One elected actuator per collision scope, stale epoch fenced.
- No duplicated accepted effect; indeterminate cases explicitly HOLD.
- Exact source, input, output and receiver receipt hashes preserved.
- Independent receiver confirms the effect, not merely a local log.
- Recovery and negative canaries are reproducible with no Rick routine relay.

## HOLD conditions
X2 owner stale/offline; no approved WorkID; no qualified worker; no actual receiver; inability to distinguish model output from effect; no independent evidence; privacy or financial/publication gate unresolved.

## Lifecycle and nonclaims
This contract is an auditable test proposal, not a completed test or scheduler registration.
LOCAL_IS_NOT_LANDED; VALIDATION_IS_NOT_ACCEPTANCE; NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF; NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE; HASHING_IS_NOT_SEMANTIC_INGESTION; DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY; NO_X2_ACTIVATION; NO_GLOBAL_SESSION_ACK.
