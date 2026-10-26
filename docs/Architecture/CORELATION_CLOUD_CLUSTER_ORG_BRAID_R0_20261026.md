# CoRelationCloud+ / CoCluster+ / CoOrg+ / CoBraid+ R0

**State:** CANDIDATE_RELATIONSHIP_FABRIC__NOT_CRM_RUNTIME__NOT_CONTACT_AUTHORITY__NOT_BULK_OUTREACH
**Observed:** 2026-10-26

## Prime invariant

`RICK_MUST_NOT_CHASE_THREADS`

Any person, group, institution, thread, planned introduction, sent message, received reply, deferred contact, failed route, or future relationship candidate should bind to one durable relationship object with provenance and currentness.

## Layering

### CoRelationCloud+
Canonical addressable relationship field.

Stores pointers and typed relations, not one giant flat contact list.

Objects may include:
- person;
- household/family;
- organization;
- institution;
- team;
- project;
- publication;
- community;
- role;
- thread;
- channel;
- introduction;
- outreach event;
- planned contact;
- response;
- delivery failure;
- consent/preference;
- next wake;
- source/evidence.

### CoCluster+
Dynamic views over CoRelationCloud.

Examples:
- active advisors;
- academic/research;
- legal/governance;
- education;
- accessibility/human-technology;
- media/publication;
- friends/family;
- pending introductions;
- no-response yet;
- replied/challenged;
- route failed;
- dormant/high-option-value;
- needs human gate.

`CLUSTER_NE_IDENTITY`
`CLUSTER_NE_AUTHORITY`

### CoOrg+
Explicit organizational/role structures where evidence supports them.

Examples:
- board candidate;
- reviewer;
- contributor;
- collaborator;
- guest;
- steward;
- advisor;
- working group;
- project team.

`INVITATION_NE_APPOINTMENT`
`ROLE_NE_PERSON`
`MEMBER_NE_AUTHORITY`
`CANDIDATE_NE_MEMBER`

### CoBraid+
Temporal and causal relationship trace.

`INTENT -> INTRODUCTION -> ROUTE -> SEND -> DELIVERY_STATE -> OBSERVED_REPLY -> ACK -> UNDERSTOOD/USED(if proven) -> RETURN -> NEXT_WAKE`

CoBraid carries chronology and evidence state. It must not infer missing stages.

### CoList+
List is a projection only.

Useful lists:
- who needs attention;
- who was contacted this week;
- who has not replied;
- who has a broken route;
- who asked for follow-up;
- who is waiting on us;
- planned contacts not yet attempted;
- dormant relations worth requalifying.

`LIST_NE_SOURCE_OF_TRUTH`

## Minimum relationship object

Each durable relationship object should carry:
- stable relation_id;
- display name or privacy-safe alias;
- entity type;
- exact known routes;
- route provenance;
- current relation state;
- why this relation exists;
- source thread/message IDs;
- last material touch;
- last verified inbound;
- delivery/route state;
- consent/preference state where known;
- role candidates;
- active clusters;
- next wake condition/date;
- owner/worker;
- privacy class;
- evidence ceiling;
- unresolved questions;
- successor/merged aliases.

## Status grammar

`DISCOVERED | PLANNED | INTRO_REQUESTED | ROUTE_VERIFIED | DRAFTED | SENT | DELIVERY_UNKNOWN | DELIVERY_FAILED | REPLIED | ACKED | CONVERSATION_ACTIVE | WAITING_ON_US | WAITING_ON_THEM | DEFERRED | DORMANT | DECLINED | CLOSED | REQUALIFY`

`SENT_NE_DELIVERED`
`DELIVERED_NE_READ`
`READ_NE_UNDERSTOOD`
`REPLIED_NE_ADOPTED`

## Thread chasing replacement

Desired flow:
`SOURCE_EVENT -> ENTITY_RESOLUTION -> RELATION_OBJECT -> BRAID_APPEND -> CLUSTER_RECOMPUTE -> NEXT_WAKE -> COORB_PROJECTION`

Rick should see only exceptions such as:
- ambiguous identity;
- conflicting routes;
- privacy/consent gate;
- consequential outreach gate;
- unresolved recipient state;
- relationship requiring human judgment.

## CoOrb view

Candidate top strip:
`NOW | WAITING_ON_US | WAITING_ON_THEM | BROKEN_ROUTE | PLANNED | DORMANT | REPLIED`

Each card:
`NAME/ALIAS | WHY | LAST_MATERIAL_TOUCH | STATE | NEXT_WAKE | SOURCE | ONE_NEXT_DEED`

## Privacy / inference rails

`CONTACT_ROUTE_NE_AUTHORITY`
`MATCHING_NE_PSYCHOGRAPHIC_TARGETING`
`PRIVATE_RELATIONSHIP_NE_OUTREACH_CONTENT`
`LIST_NE_SOURCE_OF_TRUTH`
`VISIBLE_CONTACT_NE_ACTIVE_RELATION`
`RELATIONSHIP_OBJECT_NE_OWNERSHIP`

## First bounded proof

Bind 12 representative privacy-safe relationship objects from existing evidence, each with source pointer, current state, next wake, duplicate check, and no unsupported delivery/read/adoption claim. Then render one CoOrb relationship view and compare it against manual thread chasing.