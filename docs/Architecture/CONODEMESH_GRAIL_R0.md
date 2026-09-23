# CoNodeMesh+ / GRAIL+ Federation R0

**State:** `CANDIDATE_FEDERATED_NODE_ARCHITECTURE__NO_PROVIDER_MUTATION__NO_SECRET_MATERIAL`

## Lead

One GitHub repository plus one private CoStead host is not adequate as the long-term resilience, discovery, publication, collaboration, or execution topology for CoAll.

The target is a **federated relation field across independent failure domains**, where each node has an explicit role, authority ceiling, exposure class, currentness contract, replication contract, and recovery path.

`NODE_NE_REPOSITORY`  
`REPLICA_NE_AUTHORITY`  
`MIRROR_NE_CANON`  
`MORE_NODES_NE_MORE_TRUST`

## Important prior

Historical CoAll/CoStead artifacts already contain `GRAIL` / `GRAIL+` source-registry work and `.nodes / SoT networking` plans.

R0 therefore **does not redefine GRAIL from memory**. It treats GRAIL+ as a prior lineage to recover and reconcile before assigning any new expansion, acronym, or canon meaning.

`GRAIL_PRIOR_NE_RENAME_FROM_MEMORY`

## Public-safe node-role classes

A physical/service node may hold several roles.

| Role | Meaning |
|---|---|
| `CUSTODY` | durable authoritative bytes or receipts |
| `MIRROR` | independently readable replica with explicit source relation |
| `EDGE` | DNS/CDN/public execution or delivery edge |
| `DISCOVERY` | findability, indexes, feeds, machine navigation |
| `COLLAB` | discussion, review, coordination, issue/PR surfaces |
| `INGRESS` | inbound messages/forms/events |
| `EXECUTION` | bounded process/tool capability |
| `OBSERVER` | health/currentness/telemetry projection |
| `EDITORIAL` | long-form public narrative/publication |
| `SOCIAL` | public awareness and community routing |
| `REGISTRAR` | domain ownership/control plane |
| `IDENTITY_CREDENTIAL` | identities, recovery and access material; never a public data bus |

## Visible surface classes

Current user-visible surfaces show several distinct provider classes already exist around CoCivium: public source/collaboration, DNS/edge/runtime, registrar/domain control, editorial publication, team collaboration, email ingress, professional/social outreach, local observability, remote machine capability, and credential custody.

Visibility proves **presence only**. It does not prove synchronization, backup, currentness, integration, failover, or receiver pickup.

## Redundancy vectors

### 1. Private custody redundancy

Critical private CoAll state should eventually have at least:

- primary durable local custody;
- independent off-machine private replica;
- independent encrypted remote/offsite replica;
- periodic restore proof from a replica that is not the primary writer.

A public GitHub mirror does not count as a private-custody replica.

`PUBLIC_MIRROR_NE_PRIVATE_BACKUP`

### 2. Public source redundancy

Public-safe code/specs/assets should be independently reproducible from content-addressed manifests and capable of projection through more than one public host.

Candidate pattern:

`public source -> hashed release bundle -> independent mirrors -> public edge/cache -> machine index/feed`

No mirror silently becomes the semantic source merely because it is reachable.

### 3. Discovery redundancy

Humans and machines should be able to discover the same public object through several independent routes:

- stable domains;
- repository indexes;
- feeds;
- human navigation;
- machine-readable node indexes;
- editorial/social pointers.

Discovery paths may disagree on freshness; currentness must be explicit.

### 4. Coordination redundancy

Chat/workspace/provider sessions are coordination projections, not custody.

Any important decision or state change must be exportable into durable relation/event objects.

`CHAT_NE_CUSTODY`

### 5. Execution redundancy

No single execution adapter should own the capability ontology.

Possible execution routes include resident local workers, MCP-class adapters, browser/web adapters, CI runners, remote workers, local models, and future node runtimes.

Route election depends on capability, authority, privacy, liveness, reversibility, evidence quality, and cost.

## Replication envelope

Every replicated object or event should carry enough relation state to avoid newest-wins collapse:

`object_id | content_hash | source_node | source_role | created_at | recorded_at | valid_from | valid_to | lifecycle_state | authority_ceiling | confidentiality | provenance | supersedes | receiver_scope | replication_cursor | projection_loss`

Replication transport is replaceable.

`TRANSPORT_NE_ONTOLOGY`

## Failure-domain rule

Two copies in one account/provider are not two independent failure domains.

R0 dimensions include:

- provider/account;
- machine;
- network path;
- credential root;
- physical location;
- software stack;
- operator dependency;
- billing/control plane;
- legal/jurisdictional exposure where material.

`COPY_COUNT_NE_FAILURE_DOMAIN_COUNT`

## Split-brain / currentness

Replication must prefer explicit divergence over silent overwrite.

When two nodes diverge:

1. preserve both;
2. bind source-time and hashes;
3. classify commutative vs colliding changes;
4. auto-merge only proven-safe commutative relations;
5. serialize colliding effects;
6. expose contradiction/currentness;
7. elect or request a receiver/authority decision where needed.

`NO_NEWEST_WINS`

## CoAllPulseField+ relation

CoNodeMesh+ is a natural substrate for CoAllPulseField+.

Each node may publish authorized pulses, subscribe selectively, keep a monotonic cursor, compact under CoPressure+, replay after disconnect, and exchange only the confidentiality classes it is allowed to see.

A global mesh therefore does not require global disclosure.

`GLOBAL_CURRENTNESS_NE_GLOBAL_CONTENT_DISCLOSURE`

## Public-site federation

Public websites should increasingly be generated/projected from shared objects rather than independently hand-edited copies.

Desired relation:

`CoObject -> projection compiler -> repository / web site / editorial surface / machine index / social card / future XR`

Each projection reports source object/version, valid/current time, transformation, omitted relations, accessibility fallback, and supersession pointer.

## Credential / identity separation

Credential stores and provider identities are **control-plane assets**, not CoAll content nodes.

Never replicate secrets into GitHub, public feeds, team chat, or ordinary pulse payloads.

Node manifests reference secret handles/required capabilities, never secret values.

`SECRET_HANDLE_NE_SECRET_VALUE`

## Candidate open-source enablers

R0 has live license captures for the following donor candidates:

- **restic** — encrypted backup/restore workflows;
- **rclone** — multi-provider transport;
- **Syncthing** — peer file replication;
- **NATS Server** — pub/sub and event transport;
- **Headscale** — self-hosted mesh-control candidate;
- **DuckDB** — local analytical/currentness index candidate.

These are not integrated simply by being listed. Prefer replaceable adapters and exact upstream commit pinning before code ingestion.

## Minimum viable resilient topology

```
             [ Public discovery / domains ]
                        |
      +-----------------+------------------+
      |                                    |
[ GitHub public source ]            [ Public web edge ]
      |                                    |
      +------------ public pulses ----------+
                        |
                 [ CoAllPulseField ]
                        |
            +-----------+-----------+
            |                       |
   [ CoStead primary ]      [ private offsite replica ]
            |
   [ resident local workers ]
            |
   [ RickBar / CoDesktop ]
```

Editorial/social/email/collaboration surfaces consume or project bounded public/collaboration deltas; they do not become custody roots.

## R0 next sequence

1. recover exact historical GRAIL+ lineage;
2. create private/public node registry schemas;
3. inventory current surfaces without secrets;
4. classify roles and failure domains;
5. prove one independent private replica + restore canary;
6. prove one public mirror from a release manifest;
7. bind CoAllPulse cursors across two independent receivers;
8. add drift/currentness dashboard to RickBar/CoEyes;
9. only then increase automated cross-provider replication.

## Nonclaims

This document does not prove that any visible account/service is currently integrated, synchronized, backed up, a live CoNode, an independent failure domain, an accepted custody receiver, or healthy merely because its UI is visible.

## Rails

`LOCAL_IS_NOT_LANDED`  
`VALIDATION_IS_NOT_ACCEPTANCE`  
`NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`  
`NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE`  
`HASHING_IS_NOT_SEMANTIC_INGESTION`  
`DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY`  
`NODE_NE_REPOSITORY`  
`COPY_COUNT_NE_FAILURE_DOMAIN_COUNT`  
`PUBLIC_MIRROR_NE_PRIVATE_BACKUP`  
`SECRET_HANDLE_NE_SECRET_VALUE`  
`TRANSPORT_NE_ONTOLOGY`  
`GRAIL_PRIOR_NE_RENAME_FROM_MEMORY`
