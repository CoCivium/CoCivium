# CoSneak+ / CoQ&A+ Question Metabolism R0D

**State:** `CANDIDATE_QA_METABOLISM_AND_ANTI_THRASH_POLICY__NO_RUNTIME_AUTHORITY_CHANGE`

R0C elected the high-leverage question frontier. R0D controls what happens after a question exists.

```text
question persists as durable object
!=
question remains actively computing
```

Candidate states:

`OPEN | PARTIALLY_RESOLVED | PROVISIONALLY_RESOLVED | CONTESTED | STALE | CLOSED_FOR_SCOPE | PARKED | HOLD_AUTHORITY | REOPEN_ON_EVIDENCE`

Candidate actions:

`CONTINUE | PARK | CLOSE_FOR_SCOPE | REOPEN | HOLD_AUTHORITY | SPLIT_BEFORE_ANSWER | COMPACT_AND_PARK`

Active continuation must earn itself through new evidence, material uncertainty reduction, active challenge, explicit receiver request, or required authority resolution.

`NO_NEW_EVIDENCE_NE_RETRY_PERMISSION`

Parking preserves the durable object while stopping active work.

`PARKED_NE_DELETED`

Closure is receiver/scope relative rather than global finality.

`CLOSED_FOR_SCOPE_NE_CLOSED_FOREVER`

Reopen requires a material delta or explicit receiver request.

`REOPEN_REQUIRES_DELTA_OR_RECEIVER_REQUEST`

GTRAIL depth may contract after closure/parking and deepen again on a material reopen without erasing provenance or history.

`TRAIL_CONTRACTION_NE_HISTORY_ERASURE`

R0D detects candidate CoSneaks including repeated no-delta retries, trail inflation, stale-currentness reopen, authority ambiguity, and bundled questions that should split before answering.

Nine fixture cases validate continue, park/compact, close-for-scope, reopen, authority hold and split-before-answer.

No runtime scheduler mutation, public answering, canon promotion, question deletion or authority change occurs.

## Rails

`OPEN_NE_ACTIVE_COMPUTE`  
`QUESTION_NE_PERMANENT_WAKE`  
`PARKED_NE_DELETED`  
`CLOSED_FOR_SCOPE_NE_CLOSED_FOREVER`  
`REOPEN_REQUIRES_DELTA_OR_RECEIVER_REQUEST`  
`NO_NEW_EVIDENCE_NE_RETRY_PERMISSION`  
`TRAIL_COST_NE_FREE`  
`TRAIL_CONTRACTION_NE_HISTORY_ERASURE`  
`QUESTION_COUNT_NE_PROGRESS`  
`UNCERTAINTY_REDUCTION_NE_TRUTH`  
`AUTHORITY_CONFLICT_NE_ANSWER_BY_FORCE`  
`SPLIT_QUESTION_NE_SPLIT_REALITY`  
`VALIDATION_IS_NOT_ACCEPTANCE`
