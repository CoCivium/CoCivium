# CoVirtualSubstrate+ / CoPre+ / CoPromptRel+ / CoInventory+ R0

**State:** `CANDIDATE_SYMBOLIC_PREFIX_AND_RELATIONAL_INVENTORY__NO_RUNTIME_MAGIC_NO_AUTHORITY_CHANGE`

## Lead

Yes: a visible input can be treated as only a **projection** of a larger relational substrate.

The useful candidate shorthand is:

```text
⊊ ' CoEvoAll+
```

where `⊊` means:

> the visible utterance is a proper subset/projection of a larger **inspectable** relation envelope.

This can function as a `CoPre+` / `CoPromptRel+` glyph in virtual sessions, input fields, machine-to-machine messages, and compact UX.

But the glyph is only a projection hint. It is not a secret instruction, authority token, spell, or magical compressed copy of the whole substrate.

`GLYPH_NE_FULL_SEMANTICS`

`PREFIX_NE_AUTHORITY`

## Why `⊊` rather than relying on `⊂`

The user's `⊂` idea is strong visually, but mathematical conventions differ on whether `⊂` means strict subset or merely subset.

R0 therefore elects:

`⊊` = canonical strict-projection glyph

and allows:

`⊂` = display alias only, canonicalized to `⊊` when strictness is actually proven.

If strictness is not proven, the alias must not pretend otherwise.

`SYMBOL_ALIAS_NE_CANONICAL_SEMANTIC_IDENTITY`

## CoPromptRel+

The semantic object is not the character. It is the relation envelope.

Candidate fields:

```text
visible_projection
substrate_refs
authority_scope
provenance_refs
currentness
projection_loss
unresolved_ambiguity
visibility_projection
```

That allows an input field to remain beautifully small while the system still knows which relations make it meaningful.

Example:

```text
visible:
  ⊊ ' CoEvoAll+

relational envelope:
  delegation
  authority envelope
  current project state
  continuity pointers
  active rails
  receiver/custody state
  unresolved questions
```

The default UX may show only the one glyph.

A debug/audit projection must still expose what it points at.

`HIDDEN_FROM_DEFAULT_UX_NE_UNAUDITABLE`

`HIDDEN_CONTEXT_NE_HIDDEN_AUTHORITY`

## The glyph is optional

The relation semantics must survive without the glyph.

```text
' CoEvoAll+
```

can resolve through the same `CoPromptRel+` object.

So:

`GLYPH_REQUIRED_FOR_SEMANTICS = false`

This keeps copy/paste, accessibility, speech, plain terminals, and foreign surfaces from depending on one Unicode character.

## CoPre+

`CoPre+` can generalize beyond prompt text.

A prefix relation may say:

```text
PREPENDS
QUALIFIES
PROJECTS_FROM
BINDS_CONTEXT
DECLARES_SCOPE
DECLARES_LOSS
DECLARES_PROVENANCE
DECLARES_CURRENTNESS
```

The visible prefix can therefore be tiny while the actual relation remains typed.

Again:

`PREFIX_NE_SECRET_INSTRUCTION`

## Invisible substrate matter

"Invisible" should mean **not occupying default human attention**, not unknowable.

Good invisible substrate candidates include:

- provenance;
- exact hashes;
- CLI transport details;
- currentness stamps;
- relation IDs;
- known negative knowledge;
- authority ceilings;
- receiver bindings;
- budget/cost metadata;
- projection-loss metadata;
- stale/retired pointers;
- wake conditions.

They remain queryable and auditable.

The user sees meaning first, machinery second.

## CoInventory+ / CoI+

Yes, inventories now need a substantial evolution.

A static list of files is too primitive. A useful CoInventory is a **relational index of bounded inventory shards**.

Candidate shards include:

- terms / meanings;
- relations;
- entities / identities;
- surfaces;
- capabilities;
- authority;
- tasks / backlogs;
- questions / CoQ&A+;
- budgets / CoBudget+;
- receipts / proofs;
- dependencies;
- provenance;
- negative knowledge;
- wake conditions;
- unresolved conflicts;
- stale / retired objects;
- unknown / unscanned regions;
- provider dependencies;
- public correspondence surfaces;
- failure domains;
- current runtime/materialization state.

The inventory of inventories becomes `CoI+`: a compact index that points to authoritative shards rather than copying everything into one gigantic blob that becomes stale before breakfast.

## Inventory is not reality

Every inventory must carry an explicit coverage boundary.

A valid inventory can say:

```text
KNOWN:
  these 43 shards

UNKNOWN:
  these roots/surfaces have not been scanned

STALE:
  these pointers need currentness refresh

EXCLUDED:
  these classes are intentionally outside scope
```

It may not say "this is everything" merely because it found many objects.

`INVENTORY_NE_REALITY`

`UNKNOWN_NE_EMPTY`

`DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY`

## Custody stays separate

Being listed in CoInventory does not promote lifecycle.

```text
VERIFIED_LOCAL
  + appears in inventory
  != LANDED
```

Likewise, duplicate hashes may create a `DuplicateOf` relation without creating supersession.

`INVENTORY_INCLUSION_NE_LIFECYCLE_PROMOTION`

`DUPLICATE_HASH_NE_SUPERSESSION`

This preserves:

`DISCOVERED_LOCAL -> VERIFIED_LOCAL -> LANDED -> PICKED_UP -> INTEGRATED -> COEX`

as a proof sequence rather than an inventory decoration.

## Virtual inventory projections

The full machine inventory can stay largely virtual.

Default human UX should show something like:

```text
CoI+
Current      118
Needs proof   12
Stale          7
Blocked        3
Unknown        ?
Next proof: receiver readback
```

The audit projection may expose every object and relation.

So the same inventory can support:

`machine_query_projection`

`operator_debug_projection`

`human_compact_projection`

`audit_projection`

without making Rick inspect 80,000 rows of system entrails merely to learn whether anything needs attention.

## Better consequence

Once `CoPromptRel+` and `CoI+` are related, inputs can declare which inventory slice they bind.

Example:

```text
⊊[CoI:frontier/current] ' CoEvoAll+
```

could eventually mean:

> interpret this visible projection against the current elected frontier inventory slice.

The bracketed form is a debug/explicit projection. Normal UX could still render only `⊊`.

This should remain a relation lookup, not hidden prompt injection.

## Rails

`VISIBLE_TEXT_NE_TOTAL_RELATIONAL_CONTEXT`  
`GLYPH_NE_FULL_SEMANTICS`  
`PREFIX_NE_SECRET_INSTRUCTION`  
`PREFIX_NE_AUTHORITY`  
`HIDDEN_CONTEXT_NE_HIDDEN_AUTHORITY`  
`HIDDEN_FROM_DEFAULT_UX_NE_UNAUDITABLE`  
`SYMBOL_ALIAS_NE_CANONICAL_SEMANTIC_IDENTITY`  
`INVENTORY_NE_REALITY`  
`INVENTORY_INDEX_NE_OBJECT_CUSTODY`  
`INVENTORY_INCLUSION_NE_LIFECYCLE_PROMOTION`  
`DUPLICATE_HASH_NE_SUPERSESSION`  
`STALE_NE_DELETED`  
`UNKNOWN_NE_EMPTY`  
`DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY`  
`LOCAL_IS_NOT_LANDED`  
`VALIDATION_IS_NOT_ACCEPTANCE`  
`NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`  
`NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE`
