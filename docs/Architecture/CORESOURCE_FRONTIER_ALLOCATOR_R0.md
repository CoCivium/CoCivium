# CoResourceFrontier+ / CoStretchAllocator+ R0

**State:** CANDIDATE_ARCHITECTURE__PUBLIC_WORKING_NOTE

## Lead

CoCivium should maximize useful frontier discovery from every available resource without confusing maximum utilization with maximum value.

`DISCOVER -> QUALIFY -> PRICE -> SCORE -> ALLOCATE -> EXECUTE -> MEASURE -> RECEIPT -> REEVO`

## Resource classes

A resource MAY be:
- deterministic CPU work;
- local GPU/NPU capacity;
- local/open-source models;
- remote/provider models;
- cached results;
- historical artifacts;
- code/tools;
- datasets;
- devices/nodes;
- human attention;
- receiver capacity;
- storage/bandwidth;
- experimental substrates;
- dormant virtual sessions;
- negative evidence / null resources / blocked resources.

## Allocation objective

Prefer work that maximizes expected useful information gain and receiver value under current constraints.

Candidate score dimensions:
- expected information gain;
- receiver value;
- novelty;
- reuse factor;
- falsification value;
- independence;
- privacy/locality advantage;
- reversibility;
- latency;
- cost;
- energy/resource pressure;
- coordination debt;
- proof debt;
- risk.

No single score is assumed timeless. Keep Pareto fronts where tradeoffs matter.

## CoStretch ladder

Scale only through measured steps:

`1 -> 2 -> 4 -> 8 -> ...`

At each step record:
- throughput;
- correctness;
- p95 latency;
- failure rate;
- resource use;
- duplicate work;
- new information;
- proof debt;
- receiver value.

Stop when marginal value collapses.

`HIGH_UTILIZATION_NE_HIGH_VALUE`

## CoTurtle relation

The allocator is itself testable:

`resource -> descriptor -> selector -> allocation -> result -> selector benchmark -> challenge -> receipt`

Recursive review remains bounded by aggregate budget, authority and marginal value.

## CoFiniteInfinity relation

Candidate spaces may be effectively unbounded while execution remains finite:

`UNBOUNDED_POSSIBILITY -> FINITE_WAVE -> RECEIPT -> UPDATED_FRONTIER -> DORMANCY_OR_NEXT_WAVE`

No infinite simultaneous compute, spend, authority, retention or self-replication is implied.

## CoReduce relation

Reduced views are not automatically permanent or canonical.

A reduction MAY be lossless, reversible, lossy, receiver-specific, temporary, cached, learned, superseded or compostable.

`REDUCED_NE_SOURCE`
`SUMMARY_NE_CANON`
`PRESERVE_MEANINGFUL_LINEAGE_NE_PRESERVE_EVERY_RENDER_FOREVER`

## CoOrbWare relation

CoOrbWare should render the active frontier while hiding low-value backend complexity.

Candidate depth:

`GLANCE -> CONSTELLATION -> OBJECT -> RELATION -> EVIDENCE -> RAW_SOURCE`

The surface SHOULD expand disagreement, uncertainty, stale evidence, blocked resources and authority gates while collapsing repeated agreement and duplicated work.

## Historical ReEvo

Historical artifacts remain immutable lineage inputs. Re-run only selected high-value cells and compare against pinned predecessors.

`NEWER_NE_BETTER`
`HISTORICAL_SUMMARY_NE_HISTORICAL_SOURCE`

## Million-session relation

Prefer:

`huge logical reserve -> bounded selector -> small active frontier -> receipts -> sleep/wake/reuse`

Avoid fake-human swarms, provider-limit evasion, uncontrolled spend and silent self-replication.

## Existing candidate test gates

Preserve these as thresholds, not assumed passes:

- media size >300KB;
- thumbnail OK;
- ffprobe parse;
- blackdetect 0 unintended black segments;
- GitHub HTTP 200 <2s from a timed probe;
- Gmail Primary <60s only with recipient-side observation;
- execution/send ID logged;
- Pi compatibility <2s;
- Claude credential-presence probe <1s without secret disclosure;
- local Llama/Ollama packet parse <3s.

`PROPOSED_THRESHOLD_NE_MEASURED_RESULT`

## Values

LoLs = lots of layers, laughs, love, learning.
Pay forwards + sideways.
FOSS Forever.
CoGoAll.
Working Together Respectfully.
Privacy-by-design.
Inclusive, respectful, optional participation.
Display required where evidence/identity/status must be visible; wear optional.
FFFF / zero holdings remains a design phrase, not an audited financial state.

## Rails

`UNBOUNDED_SPACE_NE_UNBOUNDED_EXECUTION`
`HIGH_UTILIZATION_NE_HIGH_VALUE`
`SELECTED_NE_EXECUTED`
`RESOURCE_AVAILABLE_NE_AUTHORIZED`
`CHEAPER_NE_BETTER_UNLESS_MEASURED`
`NEWER_NE_BETTER`
`REDUCED_NE_SOURCE`
`ADDRESSABLE_NE_BROADCAST`

## Next bounded deed

Build one deterministic allocator canary over a public resource corpus, compare allocation policies (random, first-N, keyword-only, evidence-weighted, novelty-weighted, challenge-heavy), and write PASS/FAIL/HOLD with measured cost and receiver-value proxies to `ai/benchmark-evo.jsonl`.
