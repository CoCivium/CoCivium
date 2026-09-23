# CoSession Relational Fan-In R0

**State:** PUBLIC_CANDIDATE__DETERMINISTIC_FANIN__NO_AUTOMATIC_FANOUT

## Purpose

CoSession Relational Fan-In R0 converts many bounded session deltas into one deterministic review surface before any README, schema, CoIndex, CoLex surface, architecture object, RickBar/UX surface, highlight set, or sibling repository is mutated.

The reason is simple: discovery can scale faster than safe integration. Every useful session may contribute; no session needs the entire CoAll graph in working memory and no session receives blanket multi-repository mutation authority.

## Reference implementation

- scripts/CoSessionRelationalFanIn.py
- input contract: schemas/cosession-relational-delta-v0.1.schema.json
- fixture: docs/Operations/fixtures/cosession-relational-fanin-r0-input.json
- expected fixture output: docs/Operations/fixtures/cosession-relational-fanin-r0-expected.json

The implementation uses only the Python standard library.

## Input

Repeat --input for one or more JSON files. A file may contain:

- one delta object;
- an array of delta objects; or
- an object shaped as {"deltas": [...]}.

Exact duplicate source bytes are parsed once. Coverage still records how many input files were presented.

## Output

The compiler emits:

- source SHA-256 identities and byte counts;
- accepted and rejected delta records;
- unique normalized operations;
- exact operation-duplicate groups;
- subject/relation collision candidates;
- target-domain and candidate-surface indices;
- HIGHLIGHT candidates;
- public-fanout holds;
- eligible PUBLIC_SAFE review candidates;
- zero-effect declarations for shared mutation/fanout/canon;
- a canonical compiled SHA-256.

Operation normalization covers:

op | subject | relation | object | qualifiers | evidence_refs

## Collision semantics

If one subject/relation pair has multiple distinct objects, R0 emits:

REVIEW_REQUIRED_NOT_PROVEN_CONTRADICTION

Those variants may be compatible, observer-relative, time-relative, projection-relative, additive, or contradictory. R0 does not decide.

COLLISION_CANDIDATE_NE_CONTRADICTION

## Public-safety semantics

Only PUBLIC_SAFE deltas appear in eligible_public_review_delta_ids.

PUBLIC_SAFE_WITH_REDACTION, PRIVATE_ONLY, and UNKNOWN remain explicit fanout holds. R0 never publishes them.

PUBLIC_SAFE_LABEL_NE_PUBLICATION_APPROVAL

## Bounded executable canary

The fixture contains two session deltas spanning CoLex, Humour, UX, README and RickBar relations.

Observed local canary result:

- accepted deltas: 2
- unique operations: 3
- exact duplicate-operation groups: 1
- collision candidates: 1
- highlight candidates: 1
- public-fanout holds: 1
- compiled canonical SHA-256: C089391EDC4B0B3D3B9A960B245D543910D75AA5E4ADA75B0B9BB27214BE38E6

The same fixture copied to a different filesystem path produced byte-identical compiled output.

This proves bounded mechanical determinism for the fixture. It does not prove semantic equivalence, semantic near-duplicate detection, contradiction truth, receiver acceptance, or correct fanout decisions.

## Example

python3 scripts/CoSessionRelationalFanIn.py \
  --input docs/Operations/fixtures/cosession-relational-fanin-r0-input.json \
  --output /tmp/cosession-relational-fanin.json

Compare the resulting JSON to the expected fixture output when exercising the reference canary.

## Next gate

REVIEW_COLLISIONS_AND_HOLDS_THEN_ELECT_TARGETED_PROJECTIONS

A later projector/router may turn reviewed fan-in results into targeted candidate mutations for CoTheoryAll+, CoLex, CoIndex, CoAll, CoOps+, CoMythOps+, CoPriMath, CoGibberTru, README/docs, RickBar, CoCivia, UX, humour/highlight assets, or sibling repositories.

That later layer must preserve provenance, authority ceilings, collision domains, public/private boundaries, and reversibility.

## Rails

FANIN_NE_FANOUT  
DUPLICATE_OPERATION_NE_DUPLICATE_INTENT  
COLLISION_CANDIDATE_NE_CONTRADICTION  
VALIDATION_NE_ACCEPTANCE  
BRANCH_NE_INTEGRATED  
MERGED_NE_CANON  
ALL_SESSIONS_NE_ALL_STATE
