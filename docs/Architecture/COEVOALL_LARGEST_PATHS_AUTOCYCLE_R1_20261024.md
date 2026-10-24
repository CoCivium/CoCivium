# CoEvoAll+ R1 — Largest Payload Paths + Bounded AutoCycle

**State:** PUBLIC_ARCHITECTURE_CANDIDATE__NO_ALWAYS_ON_RUNTIME_CLAIM  
**Observed:** 2026-10-24

## Purpose

Extend CoPayload+/CoThumb+/CoCopy+ from small and ordinary rich-media handoffs into a scale-graded transfer and evolution fabric that can represent very large objects and corpora without turning every transfer into a clipboard blob, every logical session into a process, or every cycle into an always-on daemon.

The target is:

```
large logical possibility
-> qualified need
-> smallest adequate representation
-> bounded parallel preparation
-> explicit effect boundary
-> receipt
-> checkpoint
-> sleep
-> wake on meaningful delta
```

## Payload ladder

### P0 INLINE
Short text / compact structured data.

Requirements:
- start/end sentinel where integrity matters;
- byte count;
- SHA-256;
- no silent truncation.

### P1 CHUNKED
Long structured text or proof bundle that must cross a narrow transport.

Requirements:
- chunk IDs;
- per-chunk SHA-256;
- aggregate SHA-256;
- chunk count;
- missing-tail detection;
- resumable receive.

### P2 FILE_BACKED
Ordinary large files and proof-critical media.

Requirements:
- exact source identity;
- size;
- SHA-256;
- MIME/type;
- preview where useful;
- explicit receiver;
- separate source/effect receipt.

### P3 CONTENT_ADDRESSED
Large immutable or deduplicable objects.

Requirements:
- content ID;
- manifest;
- object-store locator(s);
- verification recipe;
- recovery pointer;
- receiver readproof before PICKED_UP.

### P4 ARCHIVE / CORPUS
Multi-file bundles, repositories, datasets, model packs, media sets.

Requirements:
- manifest tree;
- per-object hashes;
- aggregate root hash;
- provenance;
- dependency graph;
- privacy/authority partition;
- selective materialization;
- cold reconstruction test.

### P5 STREAMING / WINDOWED
Objects too large or dynamic to materialize in one worker context.

Requirements:
- bounded windows/chunks;
- sequence identity;
- checkpoint;
- resume;
- duplicate suppression;
- ordering/reassembly proof;
- backpressure;
- resource budget.

### P6 FEDERATED / DISTRIBUTED
Objects or work graphs spanning multiple independent storage/compute failure domains.

Requirements:
- named custodians/receivers;
- authority scope;
- replica/currentness policy;
- conflict/fork handling;
- network partition behavior;
- no assumption that replica count equals independence;
- rebuild from at least one independently proven path.

`LARGER_PAYLOAD_NE_LARGER_CLIPBOARD`

## Largest-path rule

For any payload, choose the **smallest adequate transport class**.

Do not inline what should be file-backed.  
Do not file-copy what should be content-addressed.  
Do not materialize a whole corpus when a verified slice suffices.  
Do not stream forever when a checkpointed bounded window is enough.

## Parallelism

Allowed internal parallel preparation may include:

- hashing;
- manifest generation;
- type/media metadata;
- thumbnail/preview;
- dedupe;
- prior lookup;
- CoOrg classification;
- CoMap relation discovery;
- privacy/authority classification;
- receiver-fit checks;
- compression candidate;
- chunk/window planning;
- recovery-path validation;
- test-harness selection.

These may fan out under a shared parent budget.

Consequential effects remain serialized per collision domain.

`PARALLEL_PREPARATION_NE_PARALLEL_EFFECTS`

## AutoCycle+

AutoCycle means **event-driven bounded recurrence**, not permanent hot looping.

State machine:

```
DORMANT
-> WAKE_TRIGGER
-> QUALIFY_DELTA
-> LEASE_BUDGET
-> RUN_BOUNDED_WAVE
-> TEST
-> RECEIPT
-> CHECKPOINT
-> RELEASE_RESOURCES
-> SLEEP
```

Wake triggers may include:

- new exact source object;
- failed regression;
- receiver ACK/readproof;
- changed dependency/version;
- stale currentness threshold;
- scheduled bounded review;
- explicit user intent;
- newly qualified resource.

No wake trigger may silently expand authority.

## AutoEvo+

AutoEvo may:

- discover candidate deltas;
- compare against pinned priors;
- generate bounded alternatives;
- run deterministic/local tests;
- retain FAILs;
- propose promotion;
- retire obviously duplicated candidates with lineage preserved;
- queue human-gated consequential decisions.

AutoEvo may **not** silently:

- rewrite its own authority ceiling;
- erase priors/dissent;
- publish externally;
- spend/transact;
- change credentials;
- expand privacy scope;
- infer receiver adoption;
- create unbounded recursion or worker counts.

## CoTurtle+ recursion

Every evaluator may itself be challenged, but recursion must carry:

`Purpose | DepthBudget | CostBudget | EvidenceGain | StopRule | Recovery | Receipt`

Default pattern:

```
experiment
-> challenge
-> verifier
-> receipt
-> flatten
-> next wave
```

## Million-session rule

Logical identities may be vast; active embodiments remain bounded.

```
huge logical reserve
-> selector
-> tiny active frontier
-> checkpoint
-> sleep/wake
```

`LOGICAL_SESSION_NE_ACTIVE_PROCESS`  
`ADDRESS_SPACE_NE_WORKER_COUNT`  
`MILLION_SESSIONS_NE_MILLION_PROVIDER_TABS`

## Test gates retained

Historical scoped evidence must remain distinct from fresh runtime claims.

Known existing scoped evidence includes:
- one FORK01 local media canary >300 KB with exact SHA-256, thumbnail, ffprobe PASS and blackdetect zero;
- scoped GitHub HTTP 200 <2 s canaries;
- ID/message identifiers logged for prior sends;
- local Ollama metadata parse under 3 s in earlier bounded probes.

Still HELD unless separately re-proved:
- physical thumb/middle gesture to rich-media receiver path;
- Gmail recipient Primary <60 s;
- Pi compatibility <2 s;
- Claude safe credential-presence <1 s;
- local Llama/Ollama completion-quality + response parse acceptance;
- CoStead/CoVIA/node/site receiver pickup where no exact readproof exists.

## Largest-path acceptance tests

A future runtime should test at minimum:

1. P0 exact inline roundtrip.
2. P1 missing-chunk rejection + resume.
3. P2 large file exact hash + preview.
4. P3 duplicate object dedupe without identity loss.
5. P4 corpus cold reconstruction from manifest.
6. P5 interrupted stream resume without duplicate effect.
7. P6 independent receiver/custodian readproof across a named failure domain.
8. Same work object survives provider/model substitution.
9. Active worker count stays under configured ceiling while logical population increases.
10. AutoCycle wakes only on admitted trigger and returns to zero active work after checkpoint.

## Rails

`AUTO_NE_UNBOUNDED`  
`AUTOEVO_NE_SELF_AUTHORITY`  
`WAKE_NE_ALWAYS_RUNNING`  
`LARGEST_PATH_NE_MAXIMUM_MATERIALIZATION`  
`CHUNKED_NE_COMPLETE_UNTIL_AGGREGATE_VERIFIED`  
`REPLICA_NE_INDEPENDENT_FAILURE_DOMAIN`  
`POINTER_NE_PAYLOAD`  
`POINTER_NE_ACK`  
`LOCAL_IS_NOT_LANDED`  
`VALIDATION_IS_NOT_ACCEPTANCE`  
`NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`

## Next bounded runtime proof

When X2 is reachable:

- observe one real physical thumb/middle gesture;
- bind one non-sensitive media file >300 KB;
- run P2 exact hash + preview;
- optionally derive a P3 content-addressed manifest;
- perform one explicit local receiver action;
- checkpoint and return worker count to zero;
- append PASS/FAIL/HELD to `ai/benchmark-evo.jsonl`.

No external send is required for this proof.
