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


## R0B adaptive trace depth and better-question compiler

The stronger answer to "are CoQ&A+ relations looped and GTRAIL+ed always?" is **no**.

Two distinctions matter:

```text
semantic recurrence != mandatory graph cycle
durable provenance != maximum-depth trace everywhere
```

A useful CoQ&A object may close for a receiver and scope, then wake later when evidence changes. That is a temporal/relational recurrence without requiring an endlessly cyclic graph.

Candidate recurrence forms include:

- optional next question;
- challenge;
- reframe;
- successor answer;
- wake-on-evidence;
- receiver-relative reopen;
- contradiction;
- authority hold;
- explicit closure for scope.

`QA_LOOP_NE_INFINITE_LOOP`

`SEMANTIC_LOOP_NE_GRAPH_CYCLE_REQUIRED`

### Adaptive GTRAIL depth

R0B proposes five candidate trace depths:

```text
NONE      ephemeral, non-durable, low-value interaction
LIGHT     durable identity + provenance + currentness + closure/successor
STANDARD  LIGHT + evidence + challenge/next-question + receiver scope
DEEP      STANDARD + branching + reopen/currentness changes + competing answers
FORENSIC  DEEP + exact hashes + authority/effect chain + custody/readproof timeline
```

Durable Q&A should normally have at least LIGHT traceability.

But everything should not be FORENSIC merely because the machinery can generate metadata until the heat death of the universe.

`GTRAIL_DEPTH_NE_TRUTH_SCORE`

`TRAIL_OVERHEAD_NE_FREE`

`EVERYTHING_FORENSIC_NE_SAFER`

### CoSneak becomes a question generator

A CoSneak signal should usually generate a **diagnostic question** before it becomes a blocker claim.

The local R0A census already supplies a concrete example:

- 216 files carried `LATEST` in their names;
- all 216 were older than 30 days in the bounded scan;
- that supports a currentness/visibility candidate;
- it does **not** prove those files are the causal source of lag.

So better questions include:

1. Which visible projection is the current receiver actually consuming?
2. Is `LATEST` receiver-verified currentness or merely a filename convention?
3. Is an object landed but never picked up by its elected receiver?
4. What changed materially before a supposedly closed question reopened?
5. Is trail depth reducing uncertainty, or only adding proof/attention load?
6. Are unlike metrics being compared as if they shared a calibrated unit?
7. Is a dependency "required", or merely familiar because earlier architecture happened to use it?
8. Is a provider/local/device bottleneck a real dependency, or a stale routing assumption?
9. Is a successful worker producing receiver-useful benefit, or merely green CI?
10. Which relation can be retired if no receiver has used it within its declared currentness horizon?
11. What negative evidence would make us stop pursuing this branch?
12. What information is absent because the system cannot observe it, rather than because the thing does not exist?
13. What work is being repeated because identity/successor relations failed?
14. Which current object has no proven recovery route after provider/device loss?
15. Which automated loop has no explicit termination, sleep, wake, or retirement condition?
16. Where are we confusing more relation density with more understanding?
17. Which questions should remain open rather than receiving a forced answer?
18. Which questions are really several questions bundled by language?
19. Which answers are receiver-relative rather than globally contradictory?
20. Which "spooky" or metaphorical relation has a useful operational projection, and which should remain explicitly metaphorical until evidence exists?

This is a better self-questioning posture than asking the system to create more answers indiscriminately.

`QUESTION_VOLUME_NE_INSIGHT`

`BETTER_QUESTION_NE_MORE_COMPLEX_QUESTION`

### CoSneak classes worth looking for next

Beyond obvious stalls, candidate low-visibility friction includes:

- stale success signals;
- stale authority;
- zombie subscriptions/listeners;
- provider/session concentration;
- local power/dependency concentration;
- silent fallback to weaker capability;
- semantic duplication under different names;
- relation explosion;
- trail inflation;
- false freshness from labels/cache/UI;
- pickup without integration;
- integration without currentness;
- automation that survives its reason for existence;
- retries without new evidence;
- queue fairness starvation;
- irreversible defaults hidden behind "convenience";
- metrics whose units do not match;
- benefit counted multiple times through duplicate receipts;
- privacy/consent scope drift;
- receiver-relative disagreement flattened into one global truth;
- dormant resources treated as live capacity;
- optional dependency accidentally promoted into architectural necessity.

Each remains a candidate relation until measured.

`COSNEAK_SIGNAL_NE_BLOCK`

`FRICTION_SIGNAL_NE_CAUSAL_PROOF`

### R0B machine canary

R0B binds to the existing CoQ&A document/schema, CoSneak R0 fixture, and fresh bounded local census.

It validates five Q&A examples spanning NONE -> FORENSIC trail depth and six diagnostic CoSneak signals.

No runtime mutation, repair, blocking action, canon promotion, or causal claim follows.

