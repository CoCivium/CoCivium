# CoTalkItOut+ WhatsApp peer proposal adjudication (2026-11-08)

**Status:** SOURCE-REPORTED PEER INPUT; not authenticated peer ACK, not live cross-session coordination.

## Incoming proposal
Rick supplied a WhatsApp Meta AI text describing 30 steps across Priors, Futures, Here-now, CoCopy, CoEyes, CoEditor, Mash, Background, Demand and Exit. Treat this as an attributed proposal, not independently verified execution or an instruction to transfer authority.

## Adopt
- Durable WorkID, source, version/hash, observation time and independent readback for claimed effects.
- Explicit distinction between future intent and verified outcome.
- Idle/sleep is not a CoZombie failure; wake on substantive evidence/change where possible.
- No keystroke impersonation, no invented human paste or recipient ACK.
- CoEyes observes authorized evidence, not private typing fields.
- Mash roles: affected worker, capable healthy peer, independent challenger and receiver. Preserve separate identities and dissent.
- Finite lease, checkpoint, rollback, recovery and exit.
- Background claims require actual Task Scheduler, GitHub Actions, or daemon execution receipts; code/configuration alone is insufficient.

## Amend or reject
- '1 rel = 1 file' is a useful export convention, not a universal invariant. Relational identity can span immutable records, links, WorkIDs and versions.
- No fixed `docs/Evolution/COGOALL__.md` path: use existing repository paths and current heads; avoid duplicate manifests.
- Do not demand Rick manually copy Wave 15 into issue #317. Authorized GitHub connector can make scoped writes and read back; if blocked, record a precise machine/tool blocker.
- Do not insist on one demand only when bounded parallel, independent nonconflicting tasks have higher value.
- A SHA and line count prove bytes/version, not correctness, consent, receiver pickup or real-world effects.
- A claimed Meta AI sender/time/custody/consent string is not authenticated provenance; keep it as source-reported text.
- A GitHub comment URL proves a posted comment exists if read back; it does not prove a live receiver or cross-model coordination.
- 'G_d pulls toward truth' remains metaphor/hypothesis, not empirical authority.

## Operational mash contract
```text
MashCase {
  work_id, problem, affected_worker_ref, healthy_peer_ref,
  challenger_ref, receiver_ref, independent_evidence_refs[],
  consent_scope, effect_authority, failure_domains[],
  source_heads[], hypotheses[], falsifiers[],
  proposed_delta, bounded_budget, lease_expiry,
  checkpoint_ref, rollback_ref, receiver_ack_ref,
  observed_at, disposition
}
```
Admission: independent evidence of unmet work and justified peer capability. Never classify valid sleep as failure. Preserve privacy, rights and authority limits. A mash may only **propose** transfer until durable checkpoint, exclusive lease/fencing, receiver readback and rollback are proven. Exit after one checkpoint or budget expiry; reentry requires new evidence.

## Next verifiable proof
Use existing GitHub source and CI infrastructure to test CoGrace false positives, candidate mash lease expiry and independent receiver readback. Native RickBar/Ollama and >24-hour Seed survival remain separate, unverified runtime gates.

References: [CoGrace evaluator](../../examples/cotalkitout/cograce_recovery_r0.py), [CoTalkItOut gate](../../examples/cotalkitout/decision_gate_r0.py), [CoGoAll outstanding](../Operations/COGOALL_OUTSTANDING_REGISTER_20261108.md), [AI/IA onramp](../Onramp/AI_IA_COORBWARE_EVERGREEN_R0.md).
