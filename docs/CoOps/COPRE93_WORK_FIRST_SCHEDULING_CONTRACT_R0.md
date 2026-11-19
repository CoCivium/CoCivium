# CoPre9.3 | Work-first scheduling contract R0
Date: 2026-11-19 UTC
Status: CANDIDATE_POLICY_ONLY; NOT_ACTIVE_SCHEDULER; NOT_WORKER_ACK

## Purpose
Evolve CoPre9.2 without replacing the existing CoWalkAway recovery bootcard, CoSessionMesh queue, local dispatcher, or elected actuator. Outcome > Session. Friendly names are navigation aids, not capability, authority, ownership, or priority.

## Source binding
- Recovery bootcard: docs/CoOps/COWALKAWAY261118_RECOVERY_BOOTCARD_R0.md (observed blob 1f8ccc15a07616e8b136bab7d7098e22a50fb6f3).
- Work queue: docs/CoOps/COCLAUDE_WORK_QUEUE_R0.json (observed blob 861b527cc6b7a9a4d88cb45afe8bd556c3ec9f16).
- Branch: candidate/copre-cof2b-release-rail-20261118.
- Queue status at readback: CANDIDATE_NOT_DISPATCHED; workers W01-W10 UNOBSERVED_NOT_ACKNOWLEDGED.
- X2 local root cited in bootcard; no current remote access proof.

## Invariants
1. Durable job_id and outcome_id survive sessions, model switches and worker crashes.
2. Session display name does not imply role, capability, authority, priority, ownership, or consent.
3. A job recruits an eligible worker based on verified capabilities, resource budget, dependency readiness, scope authorization and lease availability.
4. Priority considers expected value, urgency, dependency unlocks, risk and aging. A deterministic score is advisory; hard safety/authority gates precede scoring.
5. Each scoped mutable resource has one elected actuator, lease/fencing token and serialized commit. Many readers/reviewers may operate in parallel.
6. Substantial jobs contain atomic checkpoints, immutable receipts and idempotency keys; checkpoint interval adapts to interruption cost and risk, not sidebar recency.
7. Work stealing requires an expired or relinquished lease, an eligible replacement, fencing against stale writers, and replay-safe receipt deduplication.
8. Fan-in validates exact source/output hashes, independent objections, test evidence, scope and disposition before successors are released.
9. Inferred wishes/needs can create proposals, never consent or external-action authority. CoWish progression: infer > propose > authorize > act > verify > repair.
10. Public release requires approved authority plus deployed URL, deployment log, screenshot and functional test. Three independent checks or HOLD where applicable.

## Minimal job envelope (schema proposal, not migrated)
job_id; outcome_id; source_refs; dependencies; priority_inputs; required_capabilities; authority_scope; collision_scope; idempotency_key; lease_owner; fencing_token; checkpoint_ref; receipt_ref; disposition; successor_refs.

## Safe migration test sequence
A. Read exact existing ledger and validate source hashes; do not reset or duplicate.
B. Shadow-rank existing ready jobs without actuating; compare current ordering and record rationale.
C. In isolated test scope, elect one actuator, lease two eligible workers, interrupt one, recover and steal only after fencing.
D. Assert one committed receipt per job, stale writer rejected, replay no-op, SQLite integrity and fan-in correctness.
E. Verify source freshness, visible CoBar and restart behavior separately before any production promotion.

## Nonclaims
NOT_IMPLEMENTED; NOT_DISPATCHED; NOT_WORKER_ACK; NO_X2_READPROOF_THIS_TURN; NO_RESTART_RECOVERY_PROOF; NO_RECEIVER_PICKUP; NO_COEX; NO_CANON; NO_RUNTIME; NO_PUBLIC_RELEASE.

## Next bounded deed
When X2 reconnects, inspect the existing dispatcher and receipt ledger read-only; run shadow ranking first. No second master and no automatic enablement of disabled scheduled tasks.
