# CoMindspace Map | Observable model-instantiation comparison R0

**Status:** instrument proposal, not a scan of private model thoughts, hidden chain-of-thought, accounts, source-code internals or a census of connected sessions.

A **model-session observation** is a bounded external record of what an authorized instantiation can demonstrably access and do, not a literal map of a mind. The same named model in two sessions can have different tool access, context windows, policies, available files and received source heads. Compare observed behavior under equivalent tasks, with consent and privacy protection.

## Minimal typed observation
| Field | Meaning |
| --- | --- |
| session_role_alias | Authorized pseudonymous role, not private account handle |
| observed_at | Time of the test; record wall-clock and source version separately |
| model_or_adapter_claim | What the provider or harness declares, if known |
| input_fixture_ref | Public-safe challenge task and exact version |
| source_work_id / source_sha256 | Which authorized WorkID bytes actually read |
| source_readproof | Receiver-produced exact digest or HOLD |
| tool_capabilities | Observable capability set; never inferred global privileges |
| effective_authority | What was authorized for this specific task |
| output_delta_digest | Hash of intentionally public, redacted outcome |
| evidence_level | PROPOSED / TESTED / LANDED / RECEIVER_PICKUP / INTEGRATED |
| held_or_unknown | Explicit inaccessible fields, privacy boundaries and known gaps |
| distinct_improvement | Measured effect or information gain relative to a baseline |
| next_wake | Typed condition for another test rather than a generic ping |

## Cross-instantiation test
1. Present the same rights-cleared source and bounded task to two separately authorized receiver identities.
2. Record direct readback, content version, capabilities, independently observable output and verified failures.
3. Change one variable at a time: source head, rights, model, tool access, timing, or bootstrap prompt.
4. Compare unique outcomes and conflicts; no hidden thoughts, unverifiable empathy, claims of consciousness or automatic authority.
5. Preserve any dissent and exact historical evidence. No model self-report is automatically proof of deployed action.

**Possible output:** accessible CoMap, machine JSON and human summary generated from the same observational records, with disclosed projection losses. No real cross-provider observations have been collected by this file.

Links: [CoPreGeneric](CoPreGeneric-v1.0-DRAFT.md) · [CoAckRewise](CoAckRewise-v8.74-SOURCE-SAFE.md) · [CoFeedLoop](CoFeedLoop-Devs-R0.md).
