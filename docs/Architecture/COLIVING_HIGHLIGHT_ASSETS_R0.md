# CoLivingHighlightAsset+ R0

**State:** `CANDIDATE__BRANCH_PR__NO_CANON_PUBLIC_RELEASE_OR_RUNTIME_AUTHORITY_CHANGE`

## Lead

A highlight is a receiver-relative relation/projection over a CoAll object or relation cluster, not a permanent intrinsic class.

`HIGHLIGHT_NE_INTRINSIC_PROPERTY`
`HIGHLIGHTABLE_NE_PUBLIC`
`HIGHLIGHT_NE_CANON`

Any sufficiently meaningful CoAll object may become highlightable for a receiver, context, time, or purpose when its evidence, provenance, uncertainty, privacy and currentness relations permit the projection.

Candidate families include, without limitation:

- Cognocarta / CC;
- CoTheoryAll+ hypotheses and theory clusters;
- CoPlan+ / CoHP+ / CoHp+ roadmap and proof-bearing projections;
- CoOps+ / CoMythOps+;
- CoPriMath+ / CoGibberTru+;
- RickBar / CoDesktop+;
- CoNode+ / CoHardware+ / CoSoftware+;
- CoMeaning / CoLex / CoRelation exemplars;
- research, cultural, visual, executable, historical, or reconstructed assets.

## Living asset identity

A living highlight asset SHOULD separate:

- stable asset identity;
- source/object bindings;
- current projection;
- version/currentness pointer;
- valid time;
- observed/read time;
- provenance;
- uncertainty/nonclaims;
- privacy/publication class;
- challenge path;
- successor relation;
- projection loss;
- receiver scope;
- change feed / delta relation.

`ASSET_IDENTITY_NE_RENDERING`
`CURRENT_PROJECTION_NE_ONLY_VALID_PROJECTION`
`SUCCESSOR_NE_ERASURE`

## Evolving while being read

A living asset MAY evolve while a participant is reading it.

This MUST NOT mean that the reader loses the ability to know what they actually read.

A compliant surface SHOULD support at least one of:

1. **snapshot pinning** — the current read stays bound to the observed version while a newer successor becomes available;
2. **visible live evolution** — the surface updates but exposes an explicit delta/currentness indicator and preserves a way to recover the prior observed projection;
3. **receiver-relative refresh** — the reader elects when to advance to the newer projection.

`READ_NE_FREEZE_GLOBAL_OBJECT`
`LIVE_UPDATE_NE_SILENT_REWRITE`
`OBSERVED_VERSION_MUST_REMAIN_REFERENCABLE`
`CURRENTNESS_ADVANCE_NE_MEANING_ERASURE`

## Highlight relation

Candidate relation:

```text
highlight_relation {
  asset_id
  receiver_scope
  purpose
  salience_reason
  source_bindings
  projection_ref
  observed_at
  valid_time
  currentness_ref
  readiness
  uncertainty
  privacy_class
  challenge_ref
  successor_ref
  projection_loss
  change_feed_ref
}
```

This allows the same underlying object to be:

- a public-safe highlight for one receiver;
- an internal research highlight for another;
- dormant for a third;
- superseded historically without being deleted.

`SALIENCE_IS_RECEIVER_RELATIVE`
`PUBLIC_HIGHLIGHT_NE_INTERNAL_HIGHLIGHT`

## Relation to CoHP / CoHp / CoPlan / CoOps

- **CoHP+** may supply human/public narrative and intent projection.
- **CoHp+** may supply evidence/currentness/proof-bearing projection.
- **CoPlan+** may supply roadmap, dependency and optionality projection.
- **CoOps+** may supply executable/current operational projection.
- **CoMythOps+** may supply cultural, metaphorical, symbolic and meaning-bearing projection.
- **CoAll+** binds these without requiring them to collapse into one rendering.

A highlight asset may therefore be a synchronized family of projections rather than one document.

`ONE_ASSET_MAY_HAVE_MANY_PROJECTIONS`
`PROJECTION_FAMILY_NE_DUPLICATE_ASSET`

## Mutable sources and reconstruction

A highlight MAY be reconstructed from multiple sources at read time.

If so, the projection SHOULD preserve:

- source set and source versions;
- reconstruction method;
- observed time;
- omitted/lost information;
- contradictions;
- receiver-specific filtering;
- whether the result was materialized before the read or synthesized during it.

`RECONSTRUCTED_HIGHLIGHT_NE_STORED_SINGLE_OBJECT`
`READ_TIME_SYNTHESIS_REQUIRES_PROVENANCE`

## CoAlive behavior

CoAlive highlight surfaces may visibly evolve through:

- new evidence;
- changed uncertainty;
- challenge/response;
- successor theory/plan;
- changed readiness;
- new executable proof;
- receiver/context change;
- changed privacy/publication state;
- changed relation neighborhood.

Visual animation alone is not evolution.

`COALIVE_NE_ANIMATION`
`CHANGE_SIGNAL_NE_CHANGE_PROOF`

## Candidate integration

- `ai/highlight-assets.json` should evolve from a flat registry toward stable asset IDs plus currentness/projection relations.
- public P2 highlight assets should retain human projection + machine twin + provenance + uncertainty + challenge + successor/currentness.
- RickBar should be able to pin, follow, diff, or subscribe to a living highlight.
- CoSourceGraph should provide source/currentness bindings.
- CoMemory/CoTime should preserve observed-version and read-time reconstruction relations.

## Rails

`HIGHLIGHT_NE_INTRINSIC_PROPERTY`  
`HIGHLIGHTABLE_NE_PUBLIC`  
`ASSET_IDENTITY_NE_RENDERING`  
`READ_NE_FREEZE_GLOBAL_OBJECT`  
`LIVE_UPDATE_NE_SILENT_REWRITE`  
`OBSERVED_VERSION_MUST_REMAIN_REFERENCABLE`  
`SALIENCE_IS_RECEIVER_RELATIVE`  
`ONE_ASSET_MAY_HAVE_MANY_PROJECTIONS`  
`READ_TIME_SYNTHESIS_REQUIRES_PROVENANCE`  
`COALIVE_NE_ANIMATION`
