# CoPre+ Sticky Continuity and Diverse Recovery Options R0

**2026-11-09 | Public draft-research candidate | Source-only, synthetic test pending | NOT installed in X2, ChatGPT sessions, CoStead, CoOrb, other provider sessions, or independent receivers.**

## CoHereNow

The problem is not merely forgetting content: *a session, worker, model, UI, mirror, or automation may continue running after silently losing the relational attachments that make its outputs valid*. A living-looking heartbeat is not a semantic custody, health, or useful-work proof. The correct objective is to keep a **small stable work spine** recoverable even when individual embodiments fail.

Preserve rather than rename prior policy families:
- [CoPre NEXT and CoPrePack R0](COPRE_NEXT_SELF_DIRECTION_PACK_R0_20261109.md) and [historical CoPre_Seed_002](../cluster/CoPre_Seed_002.json)
- [CoSessionAutocycle](COSESSION_AUTOCYCLE_R0.md), [CoWaitlessExecution](COWAITLESS_EXECUTION_R0.md), [CoSourceGraph](COSOURCE_GRAPH_R0.md)
- [CoEvidenceReceiptGuard](COEVIDENCE_RECEIPT_GUARD_R0.md), [CoLogicalSpawnPlanner R2](../Operations/COLOGICAL_SPAWN_PLANNER_R2.md)
- [Encrypted/private mirror boundary](ENCRYPTED_STAGING_PUBLIC_MIRROR_R0.md), [CoPlatformHelper/RepoZipper](../Product/COPLATFORM_HELPER_ECOLOGY_REPOZIPPER_R0.md)
- [CoItch independent challenge bench #376](https://github.com/CoCivium/CoCivium/issues/376), [CoAll fanout/fanin #317](https://github.com/CoCivium/CoCivium/issues/317), [CoEv typed evolution registry](../../ai/evolution/coev-operator-field-r0.json).

These sources establish candidate design relationships, not proof they currently run together.

## CoSticky+ core is a work-level invariant, not a hidden system prompt

A work item preserves the *exact* compact contract for its full logical lifecycle. The provider's native session context need not hold an ever-growing transcript. At each meaningful re-entry, an authorized worker obtains and verifies the latest **WorkID -> exact content digest -> typed source bindings -> permission and confidentiality -> elected next deed -> stop/wake -> recovery pointer**. Expiring workers may still read the contract but must be fenced from changes. A fresh source revision is a new version, not a silent rewrite.

The R0 [CoPreInvariantGuard](../../scripts/CoPreInvariantGuardR0.py) tests that the following fields survived exact readback: identity/sequence, parent and source hashes/revisions, purpose, receiver, observer, confidentiality, authority, collision and failure domains, evidence, budget, NEXT and falsifier, stop/wake, recovery pointer, lease, delivery/pickup/integration and effect ceiling. Every required field is compared by typed canonical JSON, not only by a human projection string.

**Crucial distinct tests:**
1. **Static presence:** all mandatory fields and expected schema version are present.
2. **Exact byte/semantic identity:** deterministic pack digest matches the canonical typed core and receiver readback preserves all fields.
3. **Currentness:** separate source authority must verify the pack is *current for the task*. A locally consistent stale pack is insufficient; R0 does not prove currentness.
4. **Permission:** a clone cannot inherit a live effect lease or extra authority by copying the packet.
5. **Custody:** writer-side hash or transport is not receiver pickup. Separate receiver-produced readproof and later integration evidence are required.
6. **Reconstruction:** prove a new worker or failure domain understands the exact NEXT, STOP, authority and negative priors without help from the original session.
7. **Useful result:** measure independently accepted task completion and all human relay, not worker count, context-token volume or heartbeat rate.

## Recovery options, diversity and failure correlation

| Route | Candidate benefit | Proof requirement |
|---|---|---|
| Local durable checkpoint | Fast re-entry on same machine | Fresh-process exact reconstruction |
| Private CoStead / offsite mirror | Survive local loss | Independent storage/restore, secret-safe custody |
| Public-safe source mirror | Source discovery and open review | Git source hash and actual receiver readback |
| Read-only shadow | Observe/detect divergence | Source freshness; cannot claim to be effect writer |
| Clone / alternate model | Independent challenge or replacement | Same WorkID and limits, different verified failure/trust domain |
| Hosted automation | Wake on a qualified event | Actual saved task, event, execution and output; NOT original session wake |
| CoItch challenger | Falsification, sanity checking | Independently sourced counterexample, not another model echo |
| Offline CoPrePack | Recover after provider loss | Exact source/manifest, reconstruct and test in a fresh environment |
| Single elected actuator | Avoid conflicting writes | Current lease, fencing token, collision and idempotency guards |

Not all options should be simultaneously active. Source diversity, geographic diversity, account/provider diversity, power/network isolation, model-source independence and **custody control** are different axes. A GitHub branch, a GitHub raw URL and a GitHub Actions job are not automatically independent failure domains. Replication can also multiply private-data exposure; private scope stays private. Avoid keeping copies of sensitive prompts or secrets in a public repository.

The [R0 adapter](../../scripts/CoPreInvariantGuardR0.py) counts **declared** distinct (failure-domain, trust-root) pairs as *candidates to verify*, never as actual independent restores. It permits bounded alternatives and rejects duplicate identifiers with conflicting bodies, stale pack references, unqualified leases, and multiple elected actuators. It only produces HOLD or HOLD_RECEIVER_PROOF; there are zero effects.

## Layered stability without attachment fall-off

Conceptual layered model, not installed components:

`WorkID and CoPreSticky -> CoSourceGraph/CoIndex exact lookup -> typed CoEv + CoPriMath constraints -> signed/hashed custody and checkpoints -> CoPatternGate and CoItch shadow challengers -> CoOps elected actuator (if authorized) -> receiver readproof -> CoOrb/RickBar view -> sleep/wake`

Every capability surface receives only its scope and role. No part should need to ingest all of CoAll to operate. A familiar symptom of attachment loss is an entity appearing competent while missing its authority ceiling, no-claims, currentness, or stop semantics. Treat as **DEGRADED/HOLD**, not as proof of diminished or restored sentience. CI/ops/sanity are practical behavioral capabilities and checks, not evidence of consciousness.

## Key inversions and tests

- **Mirroring helps:** test versus one checkpoint; more mirrors may increase cost, privacy risk and correlated failure.
- **Sticky context helps:** test versus a WorkID pointer; a long inherited prompt may carry stale instructions.
- **Shadow helps:** test whether dual-read results reduce false-green approvals or only produce repeated agreement.
- **More workers help:** test whether a single small state reducer and one elected actuator outperform many agents.
- **Strict invariants help:** measure false holds and time-to-recovery, not just accidental promotions prevented.
- **Always running helps:** test event-driven wake and dormancy against needless periodic churn.
- **Complex CoEv helps:** test individual operators and a simple baseline against the braided superframework.

Synthetic reference command: `python3 -B scripts/CoPreInvariantGuardR0.py --selftest`. The runner explicitly simulates dropped identity/permission/wake/recovery attachments, altered content, stale worker reference, incorrect ACK, collision, excess candidate width and multiple actuators. **Passing CI does not prove any remote mirror, backup, actual receiver, or actual reboot recovery.**

## CoPre wave contract

NEXT becomes a compact pointer to an exact stable packet, **not** an assertion that a new wave has occurred when nothing changed. CoPre should be unique in *material evidence and elected experiment*, not merely different wording. On loss of required attachments, checkpoint and HOLD the affected edge; permit independently safe read-only work elsewhere without manufacturing trust.

**Elected next discriminating test:** In a separately authorized, genuinely independent receiver environment, deliberately remove the foreground session and one source mirror. Restore one exact packet via an independent route and prove its STOP, permission, predecessor, source and NEXT survive. Compare a smaller WorkID-only baseline and record time, cost, bad approvals, false holds and human relays. X2 or another actual eligible receiver required for any claimed device-level result.

**Rails:** `HEARTBEAT_NE_SEMANTIC_HEALTH | STATIC_SCHEMA_NE_STICKY_RUNTIME | READBACK_NE_INDEPENDENT_RECEIVER | MIRROR_COUNT_NE_FAILURE_DOMAIN_DIVERSITY | COPY_NE_PERMISSION | SHADOW_NE_ACTUATOR | CI_PASS_NE_MACHINE_RECOVERY | SANITY_LABEL_NE_SENTIENCE | STALE_PACK_NE_CURRENT_AUTHORITY | UNKNOWN_NE_ZERO | NO_MATERIAL_DELTA_NE_NEW_WAVE`.
