# CoLivingHighlight+ / CoHighlightAsset+ R0

**State:** `CANDIDATE__BRANCH_PR__NO_PUBLIC_RELEASE_CANON_OR_RUNTIME_AUTHORITY_CHANGE`

## Lead

A highlight asset is not a frozen brochure object. It is a relational object with stable identity, evolving versions, multiple projections, provenance, challenge paths, currentness, successors, and receiver-relative renderings.

`HIGHLIGHT_NE_STATIC_PAGE`
`ASSET_IDENTITY_NE_CURRENT_RENDERING`
`READ_VIEW_NE_GLOBAL_CURRENTNESS`

Existing CoAll public-transition work already requires each highlight to carry a human projection, machine twin, provenance, uncertainty, challenge path, and successor/currentness relation. This R0 makes the living-read semantics explicit.

## Living asset model

A living highlight SHOULD be able to carry:

- stable asset identity;
- source lineage;
- source-time and observed-time;
- current elected version or frontier;
- predecessor/successor relations;
- public/private projection boundaries;
- human-readable projection;
- machine-readable twin;
- rigorous/technical projection;
- poetic/metaphorical projection;
- memeable/quotable projection;
- visual/interactive projection;
- uncertainty/nonclaims;
- challenge/contradiction relations;
- receiver scope;
- read cursor or snapshot binding;
- change feed;
- transformation/projection loss;
- public readiness;
- retention/history policy.

## Read while evolving

An asset may evolve while a participant is reading it.

That SHOULD NOT silently rewrite the meaning of the bytes/relations already read.

A receiver SHOULD be able to bind to one of:

- a stable snapshot/version;
- an observed-time cursor;
- a live view with explicit update markers;
- a diff from the reader's current cursor to a newer frontier.

`EVOLVING_WHILE_READ_NE_SILENT_REWRITE`
`LIVE_VIEW_NE_UNBOUNDED_MUTATION`
`READ_CURSOR_NE_GLOBAL_LOCK`
`NEWER_NE_INVALIDATES_PRIOR_OBSERVATION`

A live surface MAY update in place when the receiver has elected live mode, but important claim changes SHOULD expose a visible currentness/diff signal.

## Projection ladder

A single semantic object may legitimately have many projections.

Candidate ladder:

```text
stable identity
  -> one-line hook
  -> memeable / quotable line
  -> poetic / metaphorical projection
  -> plain-language explanation
  -> visual / interactive surface
  -> rigorous technical rendering
  -> machine twin / schema
  -> provenance / evidence / challenge
  -> historical versions / successors
```

No one projection is the whole asset.

`MEME_NE_MEANING_COMPLETE`
`POETIC_NE_PROOF`
`TECHNICAL_NE_ONLY_VALID_PROJECTION`
`MACHINE_TWIN_NE_HUMAN_EXPERIENCE`

## CoMetaphorical+ relation

Metaphor is a typed transformation, not decoration.

A metaphor projection SHOULD preserve:

- source domain;
- target domain;
- structural relation being carried;
- useful invariant/similarity;
- ambiguity;
- projection loss;
- receiver context;
- source/provenance;
- whether the metaphor is explanatory, speculative, humorous, poetic, operational, or mythic.

`METAPHOR_NE_EQUIVALENCE`
`MEMORABLE_NE_TRUE`
`VIRAL_NE_VALIDATED`

## Moving public framing

Repository descriptions, taglines, headlines, hero copy, and public summaries are projections with their own currentness and audience relations.

They SHOULD be allowed to evolve without pretending the project ontology changed merely because the public tagline changed.

Candidate public framing stack:

### Tiny / memeable
- **Everything relates. Make the relations visible.**
- **Software that remembers how things relate.**
- **Turn silos into relations. Turn relations into options.**
- **CoAll: less app. More living relation.**
- **Civ2+: make the connections count.**

### Poetic
- **What if software stopped trapping the world in boxes, and started learning how everything touches everything else?**
- **CoCivium is an attempt to let software remember not only things, but the living relations between them.**
- **The map should be allowed to breathe while the territory changes.**
- **Old hardware, new relations; old knowledge, new meanings; one evolving field.**

### Plain
- **CoCivium is open-source relational infrastructure for humans, AI systems, software, devices, knowledge and public spaces to coordinate without making one provider or interface the permanent center.**

### Technical
- **CoAll is a provenance-aware relational fabric for participant-relative projections, evolving memory, capability routing, bounded authority, currentness, and cross-substrate coordination.**

The public surface MAY elect different projections for different receivers while preserving one provenance spine.

`TAGLINE_NE_ONTOLOGY`
`PUBLIC_COPY_NE_CANON`
`ONE_PROVENANCE_SPINE_MANY_PROJECTIONS`

## Candidate highlight families

Existing public-prelaunch candidates include:

- Cognocarta Consenti / CC;
- CoCivium Salute;
- CoTheoryAll+ / SOWCC / CoMetaphorCarry+;
- CoHP+ / CoHp+ / CoPlan+ / CoOps+;
- RickBar / CoDesktop+;
- CoObject / CoAura / CoPriMath / CoLanguage exemplars;
- CoVirtualSession+;
- CoNodeMesh+ / GRAIL+;
- CoGibberTru+;
- CoAllPulseField+ / CoTime+.

These SHOULD be related, not isolated showcase pages.

## Highlight relation types

Candidate relations include:

- derives_from;
- projects_to;
- explains;
- visualizes;
- challenges;
- contradicts;
- supersedes;
- refines;
- historicizes;
- memeifies;
- poeticizes;
- formalizes;
- operationalizes;
- implements;
- demonstrates;
- depends_on;
- public_projection_of;
- machine_twin_of;
- successor_of;
- receiver_variant_of.

`HIGHLIGHT_RELATION_NE_MARKETING_LINK`

## CoHP / CoHp / CoPlan relation

Existing public-transition work distinguishes:

- `CoHP+`: human narrative / constitutional / public-facing intent and release story;
- `CoHp+`: proof-bearing execution, currentness, provenance, validation, operations, and product trust;
- `CoPlan+ / CoOps+`: executable roadmaps, queues, resource allocation, gates, and receipts;
- `CoAll+`: the relational fabric joining them.

Living highlights SHOULD expose these as linked projections rather than forcing one asset to impersonate all roles.

## Evolution

Highlight assets MAY receive bounded deltas from CoEvo/CoAll evolution lanes.

A delta SHOULD preserve:

- source;
- observed time;
- target asset;
- relation type;
- semantic effect;
- public/private scope;
- evidence/nonclaim;
- whether it changes source semantics or only a projection;
- successor/currentness effect.

`PROJECTION_EVOLUTION_NE_SOURCE_MUTATION`
`HIGHLIGHT_UPDATE_NE_PUBLIC_RELEASE`

## UX

RickBar / CoDesktop / public sites MAY show:

- "updated since you started reading";
- current version/cursor;
- diff highlights;
- live/frozen mode;
- why this changed;
- source/evidence;
- alternate projections;
- historical predecessor;
- next/successor candidate.

A reader should not need to understand the machinery unless they choose to expand it.

## Next

1. inventory current highlight registry and historical highlight assets;
2. recover CC, CoTheoryAll, CoHP/CoHp/CoPlan, CoMetaphorCarry and RickBar lineages from GitHub plus local historical estates;
3. add stable IDs, version/currentness and projection relations;
4. generate a small framing ladder for each highlight;
5. test one live-read asset with explicit snapshot/cursor semantics;
6. expose only public-safe projections.

## Rails

`HIGHLIGHT_NE_STATIC_PAGE`  
`ASSET_IDENTITY_NE_CURRENT_RENDERING`  
`EVOLVING_WHILE_READ_NE_SILENT_REWRITE`  
`READ_CURSOR_NE_GLOBAL_LOCK`  
`MEME_NE_MEANING_COMPLETE`  
`POETIC_NE_PROOF`  
`METAPHOR_NE_EQUIVALENCE`  
`VIRAL_NE_VALIDATED`  
`TAGLINE_NE_ONTOLOGY`  
`ONE_PROVENANCE_SPINE_MANY_PROJECTIONS`  
`PROJECTION_EVOLUTION_NE_SOURCE_MUTATION`
