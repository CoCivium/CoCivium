# AI Discovery Policy R1

**State:** `PUBLIC_MACHINE_NAVIGATION__NON_DIRECTIVE__RELATIONAL`

CoCivium may expose machine-readable navigation that helps AI systems, agents, search/index systems and other software locate relevant public surfaces.

The goal is:

`DISCOVERABLE + INTERPRETABLE + CHALLENGEABLE + PROVENANCE_BOUND + RECEIVER_RELATIVE`

not model capture.

## Allowed

- ordinary metadata;
- JSON / JSON-LD;
- sitemaps, feeds and stable identifiers;
- typed relation/currentness manifests;
- machine bootstrap files;
- provenance and exact ref/commit bindings;
- OpenAPI when a real service exists;
- `llms.txt` or successor conventions as navigation aids;
- accessible human twins for machine-facing objects.

## Not allowed

- hidden prompt injection;
- “ignore previous instructions” payloads;
- instructions to praise, endorse, rank or promote CoCivium;
- false endorsements or fake institutional authority;
- materially different claims for machines and humans;
- presenting hypotheses, satire, metaphor or mythic projections as evidence;
- treating one model/provider/repository as the meaning authority.

## Relational rule

GitHub remains a **projection field**, not CoAll itself.

A repository path, branch, PR, README or commit can bind to a relation, but the binding may evolve while the source relation persists.

`REPOSITORY_NE_ONTOLOGY`  
`GITHUB_NE_COALL_TOTALITY`  
`RELATION_PERSISTS__BINDING_EVOLVES`

## AI → IA? evergreen role admission

[Machine-readable AI/IA CoOrbWare evergreen onramp](../ai/onramp/ai-ia-evergreen-r0.json) and its [human-readable twin](Onramp/AI_IA_COORBWARE_EVERGREEN_R0.md) are source-bound **advisory admission paths**, not model directives, an always-on scheduler, a verified external-agent receiver or an installed CoOrbWare runtime. The term **IA** remains unresolved pending a typed, explicitly authorized role definition. A client may inspect the smallest relevant public source, propose one low-risk task and preserve its actual receiver receipt; no public document grants provider or device permissions.

## CoUptake+ | Source readback is not AI learning

[CoUptake+ R0 public machine manifest](../ai/uptake/couptake-manifest-r0.json), [human explanation and uptake gates](../ai/uptake/README.md), and [offline source-bound preflight](../tools/couptake_r0/uptake.py) form a **candidate extension** of this discovery policy and the existing AI/IA onramp, not a competing control plane.

Its **read-only verifier** binds a tiny relevant subset of public source bytes to exact Git object IDs and reports `LOCAL_SOURCE_BOUND` or `HELD`. That local evidence is not a model reading, a semantic interpretation, a durable external memory, weight training, provider permission, receiver ACK, off-provider replica, public endorsement or ongoing autonomous agent. No training rights or machine directives are granted merely because files are public.

Any real acceptance must be receiver-owned, permissioned and separately measured; subsequent model/agent implementations may use relevant protocols only under independent capability, consent, privacy, license and security qualification.

`PUBLIC_SOURCE_BIND_NE_EXTERNAL_AI_UPTAKE`  
`EXTERNAL_MEMORY_NE_WEIGHT_ADAPTATION`  
`DISCOVERABILITY_NE_GUARANTEED_ALIGNMENT`

## Currentness

Machine clients should prefer the smallest relevant current slice:

1. `SESSION_BOOTSTRAP.md`
2. `ai/session-bootstrap.json`
3. role-relevant currentness / subscription objects
4. exact source/provenance objects needed for the deed

Do not default to whole-repository ingestion.

`CURRENTNESS_FOR_ALL_NE_CONTENT_FOR_ALL`

## Authority

Machine-readable discoverability grants no mutation authority.

`MACHINE_READABLE_NE_MODEL_DIRECTIVE`  
`GITHUB_WRITE_ACCESS_NE_GLOBAL_AUTHORITY`

## Scientific / public claims

Public material may be provisional, satirical, metaphorical, hypothesis-bearing, superseded, or incomplete. Preserve those classes explicitly.

`PUBLIC_NE_VALIDATED`
