# CoSourceGraph R0

**State:** `CANDIDATE__BRANCH_PR__NO_CANON_OR_RUNTIME_AUTHORITY_CHANGE`

## Lead

CoAll currently spans many source classes: local files, Git repositories, provider sessions, websites, mail, chat/workspace systems, local/LAN nodes, devices, generated artifacts, human reports, screenshots, and external research.

A source should not be treated as a single memory slot or as truth merely because it is retrievable.

`SOURCE_NE_MEMORY_SLOT`
`ACCESS_NE_CURRENTNESS`
`RETRIEVABLE_NE_TRUSTED`
`POINTER_NE_ACK`
`PROJECTION_NE_SOURCE`

## Problem

CoAll can navigate between many partially overlapping memory/custody/currentness surfaces. Some sources are authoritative for bytes, some for meaning, some for runtime state, some for identity, some for public projection, and some only for discovery.

Without an explicit source graph, source discovery, access, freshness, privacy, authority and replacement can drift into chat memory or human recollection.

## CoSourceGraph+

A CoSource record SHOULD be able to represent:

- stable source identity;
- source class;
- locator/reference;
- custody role;
- authority role;
- confidentiality;
- access route;
- read/write/effect capabilities;
- currentness method;
- observed-at time;
- valid-time when known;
- freshness/expiry;
- provenance parent/source chain;
- content hash or version when meaningful;
- semantic scope;
- receiver scope;
- availability state;
- replacement/fallback sources;
- privacy boundary;
- retention/retirement state;
- evidence of access;
- contradiction/supersession relations.

## Source classes

Candidate classes include:

- `LOCAL_FILE`
- `LOCAL_DIRECTORY`
- `LOCAL_RUNTIME`
- `LAN_NODE`
- `DEVICE`
- `GIT_REPOSITORY`
- `GIT_OBJECT`
- `PROVIDER_SESSION`
- `PROJECT_SURFACE`
- `WEBSITE`
- `DOMAIN_DNS`
- `MAILBOX_MESSAGE`
- `SLACK_OBJECT`
- `PUBLICATION`
- `API`
- `MCP_RESOURCE`
- `DATABASE`
- `MODEL_OUTPUT`
- `HUMAN_REPORT`
- `SCREENSHOT`
- `ARTIFACT_PACKAGE`
- `EXTERNAL_RESEARCH`

The list is extensible.

## Memory and retrieval

Memory is one projection over source relations, not project truth.

A useful source may be:

- materially present but not indexed;
- indexed but unavailable;
- available but stale;
- remembered but not recoverable;
- recoverable through a pointer;
- reconstructible from descendants;
- inaccessible but represented by durable provenance.

`MEMORY_NE_CUSTODY`
`INDEX_NE_INVENTORY`
`NOT_IN_INDEX_NE_NONEXISTENT`
`CURRENTNESS_FOR_ALL_NE_CONTENT_FOR_ALL`

## Access graph

A source record SHOULD distinguish:

```text
exists?
reachable?
authenticated?
authorized?
readable?
writable?
effect-capable?
current?
trusted-for-what?
private-to-whom?
replaceable-by-what?
```

Authorization is relational, not boolean.

`AUTHORIZATION_IS_RELATIONAL__NOT_BOOLEAN`

## Source authority

Different source types can be authoritative for different claims.

Examples:

- file bytes -> exact file/hash;
- Git branch -> repository head at observed time;
- Task Scheduler -> scheduled-task configuration/runtime observation;
- participant report -> bounded human observation;
- website -> public projection;
- CoStead -> durable custody candidate;
- model response -> generated analysis, not source truth.

`SOURCE_AUTHORITY_IS_CLAIM_RELATIVE`

## Negative knowledge

Failure to observe a source is not proof of absence.

`NONOBSERVATION_NE_NONEXISTENCE`

A failed lookup SHOULD preserve search scope, method and observed time so negative knowledge can later be revised.


## Discovery evidence and coverage

Discovery output is itself evidence and MUST carry enough method metadata to prevent a truncated or biased result from masquerading as an inventory.

A discovery observation SHOULD preserve, where applicable:

- searched roots/scopes;
- search method and query terms;
- include/exclude rules;
- sampling strategy;
- per-class/per-term and global caps;
- truncation/saturation state;
- observed time;
- dedupe method;
- errors/inaccessible scopes;
- result counts before and after caps when available;
- whether the result supports presence, bounded non-observation, or neither.

A global result cap applied after ordering can silently erase later classes or terms. Prefer one inventory pass followed by receiver-relevant, per-class/per-term bounded projections where practical.

`SEARCH_RESULT_NE_INVENTORY`
`GLOBAL_CAP_AFTER_SORT_NE_BALANCED_SAMPLE`
`TRUNCATED_RESULT_NE_NEGATIVE_EVIDENCE`
`HIT_COUNT_NE_RELATION_COUNT`
`DISCOVERY_METHOD_IS_PROVENANCE`
`COVERAGE_IS_A_RELATION__NOT_A_BOOLEAN`

## External standards alignment

CoSourceGraph should interoperate where useful with established provenance/packaging/lineage standards rather than inventing every primitive from scratch.

Candidate donors include W3C PROV, RO-Crate / JSON-LD, Schema.org identifiers, and OpenLineage-style lineage events.

`DONOR_STANDARD_NE_COALL_ONTOLOGY`

## CI contract

Candidate machine-readable objects:

- `schemas/cosource-record-v0.1.schema.json`
- `examples/cosource-record-v0.1.example.json`
- `.github/workflows/cosource-record-contract.yml`

CI validates structural shape only.

`SCHEMA_PASS_NE_SOURCE_TRUTH`
`CI_PASS_NE_SOURCE_CURRENT`

## Next implementation

1. bootstrap a bounded registry from already-proven sources;
2. add source-class and access-route registries;
3. bind CoEvoDelta source_refs to CoSource identities where useful;
4. add freshness/currentness checks without requiring global polling;
5. expose receiver-relative source views in RickBar;
6. add replacement/fallback relations for critical externalities;
7. keep private source locators and credentials out of public projections.

## Rails

`SOURCE_NE_MEMORY_SLOT`  
`ACCESS_NE_CURRENTNESS`  
`RETRIEVABLE_NE_TRUSTED`  
`POINTER_NE_ACK`  
`PROJECTION_NE_SOURCE`  
`MEMORY_NE_CUSTODY`  
`INDEX_NE_INVENTORY`  
`NOT_IN_INDEX_NE_NONEXISTENT`  
`AUTHORIZATION_IS_RELATIONAL__NOT_BOOLEAN`  
`SOURCE_AUTHORITY_IS_CLAIM_RELATIVE`  
`NONOBSERVATION_NE_NONEXISTENCE`  
`SEARCH_RESULT_NE_INVENTORY`  
`GLOBAL_CAP_AFTER_SORT_NE_BALANCED_SAMPLE`  
`TRUNCATED_RESULT_NE_NEGATIVE_EVIDENCE`  
`HIT_COUNT_NE_RELATION_COUNT`  
`DISCOVERY_METHOD_IS_PROVENANCE`  
`COVERAGE_IS_A_RELATION__NOT_A_BOOLEAN`  
`SCHEMA_PASS_NE_SOURCE_TRUTH`  
`CI_PASS_NE_SOURCE_CURRENT`
