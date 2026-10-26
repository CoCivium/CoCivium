# CoRelationshipBraid+ Fabric R0

**State:** CANDIDATE_PRIVATE_RELATIONSHIP_ARCHITECTURE__NOT_LIVE_CRM__NO_AUTOMATIC_SEND_OR_GROUP_JOIN
**Observed:** 2026-10-26

## Prime goal

`RICK_NE_THREAD_CHASER`

People, organizations, threads, channels, promises, replies, bounces, planned introductions, meetings, and future routes should be reconstructable from one source-bound relationship fabric without requiring Rick to remember or manually braid them.

## Semantic split

### CoRelationship+
Stable relationship identity. The same relationship persists across channels and time.

### CoOrg+
Owns people, organizations, projects, role hypotheses, affiliations, membership claims, consent boundaries, stewardship, and organizational structure.

### CoThread+
Owns one conversational/event lineage on one or more surfaces. A thread is an event stream, not the person.

### CoReach+
Owns outreach state and delivery ladder:
`INTENDED -> ROUTED -> SENT -> DELIVERED -> OBSERVED -> ACKED -> UNDERSTOOD -> USED -> CHALLENGED -> ADOPTED -> CONTRIBUTED -> PROPAGATED`

### CoReceiver+
Owns receiver need, context, accessibility, preferred route, and voluntary return.

### CoCluster+
Owns operational grouping and work orchestration:
`monitor -> dedupe -> rank -> prepare -> review -> hold/send-if-authorized -> inspect response -> update`

### CoCloud+
May provide addressable private storage/projection across providers. It is not the semantic owner of a relationship.

### CoStead+
Durable private custody / recovery root where available.

### CoCopy+ / CoAckRewise+
Own daily episodic continuity: what changed, what was acknowledged, revised, contradicted, deferred, or superseded.

### CoMap+
Renders topology: person <-> org <-> project <-> thread <-> promise <-> evidence <-> next safe action.

### CoOrb+ / CoBar+
Front-door views. Show only what needs attention now; never become a second relationship database.

## Relationship braid object

Each stable relationship should be able to bind:
- relationship_id;
- people / organizations;
- known roles and role hypotheses;
- channels;
- source threads;
- last verified event by channel;
- evidence class;
- consent / boundary state;
- promises / obligations;
- unresolved questions;
- next safe deed;
- wake condition;
- suppression / do-not-contact state;
- currentness;
- privacy class;
- successor / archive state.

One relationship can have many threads. One thread can have many events. One event changes only what it actually proves.

`PERSON_NE_THREAD`
`THREAD_NE_RELATIONSHIP`
`CHANNEL_NE_IDENTITY`
`SILENCE_NE_REJECTION`
`VISIBLE_CONTACT_NE_ACTIVE_RELATIONSHIP`

## No-chasing rule

A relationship enters the attention queue only when one of these is true:
- new verified inbound;
- delivery failure;
- explicit commitment due;
- material source delta makes a prior promise actionable;
- receiver requested follow-up;
- currentness expired on a high-value relationship;
- unresolved safety / legal / consent issue;
- relationship is blocking a real closure.

Otherwise it sleeps.

`NO_DELTA -> NO_CHASE`

## rUv / WhatsApp boundary event

User reports on 2026-10-26 that they archived and/or exited all rUv-related WhatsApp groups.

Record this as:
`USER_REPORTED_BOUNDARY_CHANGE__RUV_WHATSAPP_GROUPS = ARCHIVED_OR_EXITED`

Do not infer:
- hostility;
- blame;
- scapegoating;
- endorsement;
- rejection of CoCivium;
- permission for another agent to rejoin;
- permission to contact group members independently.

Future re-entry or contact requires a valid route, platform capability, and recipient/group permissions.

`USER_EXIT_NE_AGENT_JOIN_AUTHORITY`

## Human-dependence reduction

Target:
`RICK_CRITICAL_PATH -> 0 WHERE_SAFE_AND_FEASIBLE`

Reduce human relay through:
- stable relationship IDs;
- source-linked event ingestion;
- deduplication across channels;
- automatic state reconciliation where connectors permit;
- explicit obligations and wake rules;
- suppression of stale/duplicate follow-ups;
- machine-readable receiver summaries;
- independent continuity workers;
- privacy-preserving recovery.

This does not remove human governance or consent.

`LESS_HUMAN_RELAY_NE_LESS_HUMAN_AGENCY`

## Clusters are views, not cages

A relationship may belong to multiple changing clusters:
- builders;
- academic / theory;
- Sheridan / creative technology;
- governance / legal;
- accessibility / human impact;
- culture / media;
- stewardship;
- public good;
- community;
- vendor / product;
- scientific / SETI;
- personal / trusted advisory.

Cluster membership is contextual and may expire.

`CLUSTER_NE_IDENTITY`

## What should appear in CoOrb

Default private relationship strip:
`NEEDS_REPLY | WAITING | BOUNCED | PROMISE_DUE | BLOCKED | SLEEPING | REQUALIFY`

Click-through:
`WHO -> WHY -> LAST VERIFIED EVENT -> SOURCE -> OPEN OBLIGATION -> NEXT SAFE ACTION -> WAKE CONDITION`

Do not show a giant contact list by default.

## Anti-spam / anti-pressure

Massive relationship addressability does not imply massive outreach.

`1000_CANDIDATE_RELATIONSHIPS_NE_1000_MESSAGES`
`NO_REPLY_NE_PERMISSION_TO_REPEAT`
`RELATIONSHIP_MEMORY_NE_CONTACT_PRESSURE`

## First bounded proof

Take the existing CoReach/CoOrg private ledger and normalize five relationships across at least two event types each. Verify that:
1. one person remains one stable relationship across channels;
2. delivery, reply, silence and planned contact remain distinct;
3. no duplicate follow-up is elected without a material wake;
4. one worker can reconstruct next safe action without Rick restating history;
5. rUv group exit remains a boundary event, not a motive claim.

## Rails

`RICK_NE_THREAD_CHASER`
`PERSON_NE_THREAD`
`THREAD_NE_RELATIONSHIP`
`CHANNEL_NE_IDENTITY`
`CLUSTER_NE_IDENTITY`
`NO_DELTA -> NO_CHASE`
`USER_EXIT_NE_AGENT_JOIN_AUTHORITY`
`LESS_HUMAN_RELAY_NE_LESS_HUMAN_AGENCY`
`1000_CANDIDATE_RELATIONSHIPS_NE_1000_MESSAGES`