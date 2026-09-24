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
