# CoSessionMesh / CoLanding Contract R0
Status: CANDIDATE, NOT GOVERNING. 2026-11-18.

## Problem
Ten Claude workers reportedly cycling at least twice. GitHub branch search for claude/w across CoCivium, InSeed, CoPolitic-site returned zero matches at this inspection. This is NOT evidence that workers did not run: unpushed local work is invisible to GitHub.

## CoObject identity
Each landing is a typed, immutable object envelope with fields:
schema_version, worker_id (W01-W10), session_instance_id (opaque and locally generated), cycle_id, job_id, attempt_id, object_id, kind, input_refs[{uri,sha256_or_commit}], output_refs[{uri,sha256_or_commit}], dependency_ids[], produced_utc, claimed_actor, evidence[{type,uri,hash}], tests[], disposition, authority_ref_or_null, reviewer_ids[], collision_scope, successor_job_ids[], hold_reason_or_null, privacy_class.
Never put session tokens, credential hints, private transcripts or personal identifiers into a public envelope.

## CoSHAT+
Compute SHA-256 over canonical UTF-8 JSON (sorted keys, compact separators), excluding envelope_sha256 and any signature. A digest detects changed bytes; it is not an identity signature, approval, source truth or custody proof. Optional signatures require an independently verified key registry and separate signing authority.

## CoLanding+ state machine
PREPARED -> SOURCE_VISIBLE -> HASH_VERIFIED -> RECEIVER_READBACK -> INTEGRATED (only with separate evidence).
A worker's own assertion is PREPARED at most. GitHub branch and commit readback may establish SOURCE_VISIBLE and HASH_VERIFIED, not Vault custody. A different authorized receiver must prove exact readback before receiver acceptance. Do not collapse candidate, main, CoVault and CoEx.

## CoSessionDirectory+
Discovery is a read-only index keyed by (worker_id, session_instance_id, cycle_id, job_id). Query GitHub candidate branch prefixes and receipt paths, local receipts where access exists, and verified receiver manifests. UNKNOWN means unobserved, not inactive. Display source freshness and transport blockers. GitHub metadata cannot discover unsent Claude chat work.

## CoMetaTrain+ (proposed)
Learn only from provenance-linked outcomes, failure modes and reviewer corrections. Never treat the frequency of a claim, worker vote, repeated chat or claimed model motive as ground truth. Preserve counterevidence, review lineage and consent constraints.

## CoOptimax+
N substantial independent jobs/cycle, atomic steps inside each job. One receipt per completed job, independent verification, one elected actuator per collision scope, deterministic fan-in with minority objections. A scoped HOLD blocks only its unsafe transition. AutoNext requires a REAL scheduler, persisted dependency graph, lease, heartbeat and recovery; this document does not provide them.

## CoRel inversions / failure checks
- Same worker name, different session: never conflate identities.
- Same output bytes, different actors: dedup content without inventing authorship.
- Same actor, different source hashes: preserve both as versions.
- Same hash, false output URI: require remote readback.
- Three reviews from one provider/session lineage: not three independent checks.
- Missing worker branch: UNKNOWN, not failed or acknowledged.
- Watermark in HTML or prose: descriptive only, not cryptographic proof.
- Signed but unauthorized operation: still HOLD.
- Public directory leaks capability targets: sanitize before publication.
- Stale receipt after supersession: retain with EXPIRED/OBSOLETE status; never erase history.

## Next gates
A) Workers land isolated candidate branches and exact receipts when authenticated transport and scoped authority permit.
B) Independent GitHub reader verifies exact refs and hashes.
C) CoFanIn indexes verified envelopes and flags collisions; CoGuardian gates shared state/public release.
No manual Rick courier, no invented worker ACK, no auto-promotion.
