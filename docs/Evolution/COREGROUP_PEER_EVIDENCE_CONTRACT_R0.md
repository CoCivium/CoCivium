# CoReGroup peer-session evidence contract R0

Status: PUBLIC PROPOSAL, NOT LIVE X2 DEPLOYMENT OR VERIFIED MULTI-SESSION SYNC.

## Purpose
Replace manual prompt copying with machine-discoverable, verifiable artifacts. All peers may propose and test; no permanent session leader. A single temporary fenced writer owns each conflicting effect.

## Seed record (required fields)
- seed_id, objective, source_revision, created_at_utc, owner_policy
- current_work_id, lease_epoch, lease_expiry_monotonic_reference
- evidence_refs, receipts, unresolved_proof_debt
- last_verified_progress, next_trigger, retry_budget, state
- checksum and supersedes pointer

## Receipt contract
Each claimed effect requires: receipt_id, work_id, seed_revision, actor_id, action, input_hash, output_hash, observed_at_utc, verifier_id, evidence_uri, status, lease_epoch. Human-readable status messages alone are not effect receipts.

## States
PROPOSED -> CLAIMED -> EXECUTING -> EFFECT_RECORDED -> INDEPENDENTLY_VERIFIED.
On failure: SUSPENDED or FAILED_WITH_EVIDENCE. A session cannot self-promote to VERIFIED. Replays are idempotent; stale lease epochs are rejected.

## Proof boundaries
- X2 running is not equivalent to a connected remote execution bridge.
- A local producer sample is not a receiver ACK.
- A screenshot is not a durable runtime receipt.
- A public GitHub file is not a deployed UX.
- A claimed heartbeat or aliveness score is not a measurement without source, unit, window and verifier.
- A copied prompt is not autonomous synchronization.
- Approval does not create access or bypass privacy/irreversible-action gates.

## Peer convergence
1. Read the latest shared Seed and receipts from the designated artifact store.
2. Pick independent work or acquire a fenced lease for conflicting writes.
3. Execute bounded work and record content-addressed evidence.
4. Challenge results independently, record counterexamples and regressions.
5. Advance only verified effects. Suspend on repeated no-progress, conflicting receipts, or exhausted budget.
6. Recover on a new external trigger; preserve prior evidence and rollback path.

## UX acceptance
One Seed, one Orb, one gauge, one thumb, one time, zero placeholders.
Gauge must expose its source and age. The thumb is a reversible action. One shared time basis, with monotonic durations for leases. No claims of live receiver status without an ACK. Break Glass preserves the last working native interface.

## Gates still open
- Confirm actual canonical Seed storage and its permissions.
- Integrate with the actual X2 producer/observer/receiver.
- Run verified crash-restart, cross-process fencing, and >24h unattended survival.
- Validate multi-session discovery without human prompt relays.
- Prove public/remote access separately from in-house authorization.

## Existing executable probes
- tests/gs_receiver/test_receiver_reconcile.py
- tests/gs_loop/test_loop_guard.py
- tests/gs_loop/test_loop_faults.py
- tests/gs_loop/test_durable_seed.py
- .github/workflows/coloops-safety.yml

This contract is a coordination artifact, not proof that its workflow is deployed.
