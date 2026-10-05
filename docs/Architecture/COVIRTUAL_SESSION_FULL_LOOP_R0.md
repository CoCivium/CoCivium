# CoVirtualSession Full-Loop Reconciliation R0

**State:** `CANDIDATE_VIRTUAL_FIRST_SESSION_FULL_LOOP__NO_PROVIDER_UI_OR_RUNTIME_AUTHORITY_CHANGE`

All session-like work should be representable as a virtual session relation first, including manual/provider chats. A visible chat, CLI, local worker, model process, CI job, RickBar pane, watcher, or human-led work period is an embodiment of a logical session, not the session's durable identity.

`SESSION_NE_PROVIDER_TAB`
`MANUAL_SESSION_NE_SPECIAL_IDENTITY_CLASS`
`CLI_NE_USER_WORKSPACE`
`EMBODIMENT_NE_IDENTITY`

The mature UX target is: `many logical sessions -> few materialized embodiments -> almost no backend/session machinery exposed to the user`.

## CoBoogie+ / CoRegroup+

CoBoogie asks what materially changed, drifted, stalled, disappeared, contradicted, became stale, recovered, or gained a new route. It emits a bounded delta field, not a verdict.

CoRegroup reconciles that evidenced delta field into finite dispositions such as `KEEP_CURRENT`, `SUPERSEDE_FOR_SCOPE`, `RETAIN_HISTORICAL_WITNESS`, `MERGE_RELATION_ONLY`, `HOLD_MISSING_EVIDENCE`, `WAKE_RECEIVER`, `ROUTE_TO_LOCAL_EXECUTION`, `PARK_DORMANT`, or `CLOSE_SAFE_BOUNDED`.

`COBOOGIE_NE_BLIND_RESCAN`
`COREGROUP_NE_NEWEST_WINS`

## Relations of relations

Higher-order relations are first-class. A relation may itself be the subject or object of another relation. Traversal is bounded by receiver purpose, evidence need, authority, currentness, and compute/attention budget.

`META_RELATION_NE_TRUTH`
`RELATIONAL_RECURSION_REQUIRES_BUDGET`
`DEPTH_NE_IMPORTANCE`

## CoSync+

CoSync aligns verified state between relevant receivers after Boogie/Regroup has determined what warrants alignment.

`verified_delta + receiver_scope + authority + confidentiality + currentness -> sync_packet`

`SYNC_NE_DISCOVERY`
`DELIVERY_NE_PICKUP`

## CoAckRewise+ candidate

CoAckRewise is a candidate receiver-side acknowledgement plus reconsideration relation. It is stronger than byte-arrival ACK and weaker than universal acceptance.

Candidate dispositions: `ACK_EXACT_OBJECT`, `ACCEPT_FOR_SCOPE`, `REWISE`, `CHALLENGE`, `HOLD`, `SUPERSEDED`, `NOT_APPLICABLE`.

`ACK_NE_ACCEPTANCE`
`ACCEPT_FOR_SCOPE_NE_CANON`
`REWISE_NE_REWRITE_HISTORY`

## Full verified loop

`OBSERVE -> CoBoogie -> CoRegroup -> CoSync/CoResync when warranted -> DELIVERY -> EXACT PICKUP/READPROOF -> CoAckRewise -> REVERIFY RESULT AGAINST INTENT + RECEIVER -> FAN-IN/SUPERSEDE/HOLD -> UPDATE CURRENTNESS + WAKE CONDITIONS -> SLEEP/CLOSE-SAFE/NEXT BOUNDED DEED`

The loop repeats only on material delta or bound wake conditions.

`FULL_LOOP_NE_PERMANENT_LOOP`
`NO_DELTA_NE_RETRY_PERMISSION`

## Manual sessions and CLI

Manual/provider sessions are foreground projections, useful for conversation, provider-only capability, creative work, explicit human authority gates, or visual review. They should not remain required for durable identity, currentness, queue ownership, routine retries, transport, orchestration, or liveness truth.

CLI, shell, PIDs, logs, transport protocols, model endpoints, file paths, and orchestration details are substrate relations. Default UX should hide them unless diagnosis, explicit user request, authority/security, or the actual work product requires visibility.

`HUMAN_CONVERSATION_NE_CONTROL_PLANE`
`RICK_NE_SESSION_SCHEDULER`
`CLI_EXISTS_NE_CLI_MUST_BE_VISIBLE`
`SUBSTRATE_DETAIL_NE_USER_DECISION`
`INVISIBLE_NE_UNAUDITABLE`

## Acceptance ladder

1. `VIRTUAL_IDENTITY_BOUND`
2. `CURRENTNESS_SOURCE_BOUND`
3. `BOOGIE_DELTA_EVIDENCED`
4. `REGROUP_DISPOSITION_EVIDENCED`
5. `SYNC_PACKET_COMPILED_IF_NEEDED`
6. `DELIVERY_PROVEN`
7. `PICKUP_READPROOF_PROVEN`
8. `ACKREWISE_DISPOSITION_PROVEN`
9. `RESULT_REVERIFIED`
10. `CURRENTNESS_AND_WAKE_STATE_UPDATED`
11. `QUIESCENCE_OR_NEXT_DEED_ELECTED`

No lower rung implies a higher one.

## Nonclaims

No provider UI mutation, provider tab creation/closure, runtime authority change, canon promotion, or public effect is performed by this candidate.
