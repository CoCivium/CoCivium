# CoSneak+ / CoQ&A+ Looping / GTRAIL+ Candidate R0

**State:** `CANDIDATE_ANTI_STALL_AND_QA_TRACE_RELATIONS__NO_RUNTIME_AUTHORITY_CHANGE`

## Lead

Some blockers are obvious. Others are sneaky.

A system can look active while hidden friction, stale assumptions, authority ambiguity, duplicate work, receiver mismatch, queue starvation, proof gaps, or invisible dependency pressure quietly slow it down.

`ACTIVITY_NE_PROGRESS`

`LOW_VISIBILITY_FRICTION_NE_LOW_IMPACT_FRICTION`

## CoSneak+

`CoSneak+` is a candidate relation family for **subtle, indirect, delayed, hidden, or compounding impediments**.

It is descriptive, not accusatory.

A CoSneak relation may bind:

`source | affected_object | mechanism | visibility | onset | duration | impact | evidence | confidence | detectability | reversibility | mitigation | recurrence | currentness`

Candidate classes include:

- stale currentness;
- hidden manual dependency;
- authority ambiguity;
- receiver mismatch;
- duplicate work;
- queue starvation;
- contention;
- retry loops;
- excessive context/load;
- silent fallback;
- dependency concentration;
- stale pointer;
- proof deficit;
- visibility deficit;
- coordination overhead;
- false completion signal;
- over-broad scope;
- under-bounded work;
- delayed pickup;
- unowned exception;
- unresolved collision.

`COSNEAK_NE_MALICE`

`BLOCKER_NE_BAD_ACTOR`

`FRICTION_SIGNAL_NE_CAUSAL_PROOF`

The point is to make subtle drag findable before it hardens into architecture.

## CoSneak detection loop

Candidate loop:

`NOTICE -> RELATE -> MEASURE -> CHALLENGE -> MITIGATE -> RECHECK -> RETIRE_OR_RECUR`

A CoSneak should not remain permanently "active" after evidence disappears.

`DETECTED_ONCE_NE_ETERNAL_BLOCKER`

## CoQ&A+ should loop

Existing CoQ&A already supports next questions, challenge refs, answer supersession, currentness and answer timelines.

Therefore the stronger model is not:

`question -> answer -> done`

but:

`question -> answer -> challenge -> next question -> new evidence -> revised answer -> compare -> branch/close -> future wake`

This loop is optional per object. Some questions genuinely terminate for a receiver; others remain living.

`QA_LOOP_NE_INFINITE_LOOP`

`ANSWER_NE_FORCED_NEXT_QUESTION`

`CLOSED_FOR_RECEIVER_NE_CLOSED_FOREVER`

Useful loop edges include:

- `ANSWERED_BY`
- `CHALLENGED_BY`
- `GENERATES_QUESTION`
- `SUPERSEDES`
- `CONTRADICTS`
- `DEPENDS_ON`
- `REOPENS`
- `CLOSES_FOR_SCOPE`
- `WAKE_ON_EVIDENCE`
- `DUPLICATES`
- `REFRAMES`

## GRAIL+ relation

Existing GRAIL+ direction is already a relation/currentness/discovery fabric, not a global authority.

CoQ&A objects should therefore be **GRAIL-addressable/discoverable where useful**, but not obligatorily globally replicated.

`COQA_NE_GLOBAL_BROADCAST`

`GRAIL_DISCOVERABLE_NE_GRAIL_OWNS_OBJECT`

`NETWORK_NE_AUTHORITY`

Questions and answers may expose relation/currentness pointers into GRAIL+/CoNodeMesh+ while private/restricted material remains receiver- and confidentiality-scoped.

## GTRAIL+ candidate

The repository does not currently expose an established `GTRAIL+` meaning.

Treat `GTRAIL+` as a **candidate trace relation**, not canon.

Candidate meaning:

> a traversable provenance/currentness trail through question, answer, evidence, challenge, successor, receiver and node relations.

Possible envelope:

`trail_id | start_object | relation_path | evidence_refs | timestamps | receiver_scope | confidentiality | branch_points | stale_edges | unresolved_edges | endpoint_state`

It may be projected through GRAIL+, but is not synonymous with GRAIL+.

`GTRAIL_CANDIDATE_NE_GRAIL_REDEFINITION`

`TRACE_NE_TRUTH`

`PATH_EXISTS_NE_PATH_IS_CAUSAL`

## Always / many / optional

Not every Q&A object should be forced into every relation.

Candidate default:

- every durable Q&A object gets stable identity + currentness + provenance;
- every answer may have challenge/successor/next-question relations;
- loops are created when materially useful;
- GTRAIL traces are generated on demand or when diagnostic/currentness value exists;
- GRAIL discovery is receiver/confidentiality scoped;
- high-value open questions may have many trails;
- simple settled questions may have none beyond minimal provenance.

`ALWAYS_TRACE_EVERYTHING_NE_USEFULNESS`

`RELATION_DENSITY_NE_QUALITY`

## CoSneak x CoQ&A

CoSneak detection can generate diagnostic questions:

`suspected hidden friction -> diagnostic question -> evidence -> answer -> mitigation -> recheck`

Likewise unresolved Q&A loops can themselves reveal CoSneaks such as stale evidence, missing receiver pickup, circular dependency, or repeatedly reopened ambiguity.

This creates a bounded self-debugging relation:

`CoSneak <-> CoQ&A <-> GTRAIL <-> currentness/provenance`

without making any one layer the control plane.

## Rails

`ACTIVITY_NE_PROGRESS`  
`COSNEAK_NE_MALICE`  
`BLOCKER_NE_BAD_ACTOR`  
`FRICTION_SIGNAL_NE_CAUSAL_PROOF`  
`DETECTED_ONCE_NE_ETERNAL_BLOCKER`  
`QA_LOOP_NE_INFINITE_LOOP`  
`ANSWER_NE_FORCED_NEXT_QUESTION`  
`CLOSED_FOR_RECEIVER_NE_CLOSED_FOREVER`  
`COQA_NE_GLOBAL_BROADCAST`  
`GRAIL_DISCOVERABLE_NE_GRAIL_OWNS_OBJECT`  
`GTRAIL_CANDIDATE_NE_GRAIL_REDEFINITION`  
`TRACE_NE_TRUTH`  
`PATH_EXISTS_NE_PATH_IS_CAUSAL`  
`ALWAYS_TRACE_EVERYTHING_NE_USEFULNESS`  
`RELATION_DENSITY_NE_QUALITY`  
`VALIDATION_IS_NOT_ACCEPTANCE`
