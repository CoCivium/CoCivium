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

## CoTalkItOut+ | bounded integration decision gate (2026-11-08)

**Purpose:** When RickBar/R5 native surface, CoVirtualSession+, CoFleet projection, and CoModelFabric adapters disagree about schema, identity, authority, or currentness, turn that disagreement into **one testable integration decision**, not an unbounded peer conversation or another Rick-mediated prompt relay. Reuse [virtual-session morphology](../Architecture/COVIRTUAL_SESSION_MORPHOLOGY_R0.md), [CoFleet/RickBar R4](../UX/COFLEET_RICKBAR_R4.md), [provider-adapter contract](../Architecture/COMODELFABRIC_COORB_PROVIDER_ADAPTERS_R0_20261024.md), and this CoReGroup custody contract.

**Minimal decision packet:** `work_id | decision_id | source_refs | observed versions | alternatives >= 2 | objections | discriminating_experiment | measurement/stop condition | effect_requested | effect_authority | evidence_refs | receiver_scope | next_wake`.

**State transitions:** `OBSERVE -> TALK -> TEST -> CHALLENGE -> QUALIFIED / HELD -> RECEIVER_READPROOF`. A qualified reasoning packet is **not** executable authorization; verified test receipts are not native receiver acceptance. Talk only when alternatives or a test are missing, and do not ask Rick to translate between already-source-addressable artifacts.

**R1 RickBar attachment strategy:**
1. Inventory which of the existing R5 native RickBar and CoBar variants is actually active; preserve source revision and screenshots separately from runtime observations.
2. Keep one stable WorkID and distinguish logical virtual-session identity from worker embodiment and provider tab.
3. Translate an authorized local model response into the existing receipt envelope; do not create another long-lived model host by default.
4. Project the typed result into CoFleet's existing bounded `CoHereNow / Meaning / NextSafeAction / Evidence` view. Retain the prior native interface as Break Glass.
5. Challenge one known mismatch (e.g. adapter response `MODEL_OUTPUT_UNVERIFIED` must not become `INDEPENDENTLY_VERIFIED` on the UI). Test fail-closed and recovery.
6. Test one handoff after process restart and, separately, >24h Seed survival with two independent observers. Neither is established by source tests.

**Executable R0 candidate:** `examples/cotalkitout/decision_gate.py` and `tests/gs_loop/test_talkitout_gate.py` classify decisions with no tool execution, no automatic messages and no authority expansion. CI/source readback may qualify this isolated gate; connecting it to R5, independent workers, and CoStead is a separate release boundary.

**Stop/selection rules:** An objection without a discriminating experiment stays TALK; an unauthorized effect is HELD; duplicate assent does not create a new WorkID; self-asserted verification without external receipt stays HELD. Progress is measured by validated decisions, closed interface mismatches, reduced human relay and successful recovery, **not** tokens exchanged or virtual-session count.

`TALK_NE_ACT` · `QUALIFIED_NE_AUTHORIZED` · `DISCUSSION_NE_RECEIVER_ACK` · `VIRTUAL_SESSION_NE_PROVIDER_TAB` · `PROPOSAL_NE_RUNTIME`.

## CoZombie / CoGrace session recovery triage (2026-11-08)

**Status: synthetic classifier candidate; no live session takeover, cross-provider access, or evidence of AI subjective aliveness.** CoTalkItOut is an escalation/coordination mechanism, not an involuntary session merger. Recover the **work**, preserve independent participant identities, and prefer the same active healthy worker wherever possible.

- **HEALTHY_QUIET:** intentionally dormant, appropriately graceful hold, completed, or no due obligation. No rescue or busywork.
- **UNKNOWN:** missing, conflicting or stale signals require observation, not a zombie label.
- **ACTIVE_OR_WAITING:** progress is recent or obligation not due. Preserve the incumbent.
- **STALLED / DEGRADED:** independently observed overdue obligation and stale progress, or conflicting evidence. Escalate with reason, policy, baseline and retry budget.
- **HUMAN_GATE:** privacy, authority, irreversible effects or recipient consent require a human decision; peer assistance does not bypass it.

### Evidence-driven trigger

A selected **CoPriMath / CoMeasure** policy can eventually use hundreds of registered measurements, but the current number **325 is a requested design target, not an audited inventory**. Each qualifying metric needs `metric_id, units, source, observer, valid_time, freshness, sampling_window, uncertainty, threshold_provenance, decision_relevance, privacy_scope, counterexample`. Measure verified work, healthy sleep, obligation deadlines, lease status, independent receiver effects, bounded recovery and human relay burden. Reject raw activity, model-generated enthusiasm, number of tabs and self-claimed sentience as sole evidence.

The first pure implementation uses nine **metric families**, not fake 325 named metrics: `examples/cotalkitout/session_recovery_r0.py`. It requires joint overdue and stale-progress evidence for a stalled classification. The policy must be calibrated against real positive/negative cases and different phases; it is not a universally optimal time threshold.

### Peer help without unsafe takeover

A stalled WorkID may be presented to an eligible, independently bounded peer, including a healthy high-performing session, **only** when information rights, consent, role capability, available budget and collision domains are compatible. A peer may offer challenge, context reconstruction or a proposal without mutating another session. To actually take over a conflicting effect, fence the old lease, preserve the checkpoint, elect one successor, create a new epoch and independently verify the effect. No silent model identity fusion or global account authority.

When no eligible peer exists, stay held and keep the wake predicate. Do not wake all sessions or demand that rick relay prompts. Merge compatible **findings and source-bound work objects**, not private conversation histories or personalities.

### Acceptance and negative controls

The existing `tests/gs_loop/test_session_recovery.py` verifies 15 synthetic cases: healthy dormancy, graceful hold, unknown metrics, recent work, future due dates, live lease fencing, no peer consent, incompatible peers, one deterministic proposed helper, conflicts, protected human gates, no due obligations, impossible timestamps, insufficient proof and metric-family accounting. Test success **does not demonstrate live takeover, 24h operation or 325 maintained metrics**.

A promotion benchmark must additionally measure: false-positive forced rescue rate, stalled-work recovery yield, human interrupts, duplicated effects, downstream receiver usefulness, energy/cost and successful rollback. Require explicit baselines (do nothing / local retry / peer challenge / qualified handoff); report when intervention performs worse than healthy waiting.

`QUIET_NE_ZOMBIE` · `METRIC_COUNT_NE_METRIC_QUALITY` · `PEER_ASSIST_NE_AUTHORITY_MERGE` · `TAKEOVER_PROPOSAL_NE_EXECUTION` · `LEASE_ACTIVE_NE_SAFE_TO_REPLACE` · `MODEL_BUSY_NE_USEFUL`.
