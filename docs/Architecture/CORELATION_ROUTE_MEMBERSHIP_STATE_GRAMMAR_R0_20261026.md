# CoRelation Route + Membership State Grammar R0

**State:** CANDIDATE_ARCHITECTURE__NOT_LIVE_SYNC__NOT_SEND_AUTHORITY
**Observed:** 2026-10-26

## Why

A relationship can persist while a particular carrier route, group membership, permission, or send capability changes.

Do not flatten these into one status.

## Independent dimensions

### Identity
Who or what is the stable person, group, organization, or project?

### Relationship
What historical or current relation is evidenced?

### Route
Which carrier/surface can represent or transport interaction?

### Membership
Is the actor currently a member/participant on that route?

### Permission
What operations are allowed by the carrier and by human authority?

### Reachability
Can the route currently be reached?

### Delivery
Was a message actually accepted by the carrier?

### Read / Ack / Return
What receiver-side evidence exists?

## Candidate state vector

`RELATION_STATE = {identity, relationship, route, membership, permission, reachability, delivery, read, ack, return, currentness}`

Example from the 2026-10-26 WhatsApp screenshot:

- identity: group thread identified
- relationship: historic participation visible
- route: WhatsApp group
- membership: ended / unavailable
- send permission: blocked
- history visibility: retained
- alternate route: unknown
- receiver acknowledgement: not established

## Route transition grammar

`DISCOVERED -> QUALIFIED -> AVAILABLE -> JOINED -> ACTIVE -> MUTED / DORMANT -> LEFT / REMOVED -> READ_ONLY_HISTORY -> REQUALIFY / ARCHIVE`

Possible causes remain separately typed:

- USER_LEFT
- ADMIN_REMOVED
- GROUP_CLOSED
- ACCOUNT_CHANGED
- POLICY_BLOCK
- UNKNOWN

Never infer a cause from send failure alone.

## Flow / anchor relation

A stable relationship identity is an anchor.

A carrier route is a replaceable flow path.

Good architecture preserves:
- identity and history when a route disappears;
- source-bound evidence;
- consent boundaries;
- alternate-route possibility without auto-routing;
- requalification before renewed contact.

Bad architecture treats:
- one broken route as a dead relationship;
- one visible thread as current membership;
- one historical membership as permanent authority.

## CoOrb / CoRelations UX

Show these separately:

`RELATION: HISTORIC / CURRENT / UNKNOWN`
`ROUTE: WHATSAPP`
`MEMBERSHIP: ENDED`
`SEND: BLOCKED`
`HISTORY: VISIBLE`
`ALT ROUTES: UNKNOWN / QUALIFIED`
`NEXT: HOLD / REQUALIFY / ARCHIVE`

## Rails

`RELATIONSHIP_NE_ROUTE`
`ROUTE_NE_MEMBERSHIP`
`MEMBERSHIP_NE_AUTHORITY`
`HISTORY_NE_CURRENTNESS`
`VISIBLE_NE_REACHABLE`
`REACHABLE_NE_DELIVERED`
`DELIVERED_NE_READ`
`READ_NE_ACK`
`ACK_NE_AGREEMENT`
`BROKEN_ROUTE_NE_BROKEN_PERSON_RELATION`
