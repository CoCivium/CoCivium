# CoMiddle+ / CoPriMath+ R0 | 20 trustworthy relation primitives

**Candidate branch for [the existing CoMiddle owner issue #246](https://github.com/CoCivium/CoCivium/issues/246). Not a mouse driver, permission system, validated scientific ontology, live CoOrbWare integration or installed X2 runtime.**

The existing [CoMiddle relation-space index](../../../ai/comiddle_relation_space_r0.json) can address billions of syntactic combinations and [CoContextRail+ R1](../context_rail_r1/README.md) previews up to seven contextual alternatives. The missing technical layer was a **small, testable set of typed relation meanings**. This candidate supplies exactly **20** relation types, **16** accessible question families, and **12** explicit candidate operations without minting another global controller.

## One-minute test

With Node 22 and a clone of this review branch:

```sh
node --test examples/conodcothumb/relation_semantics_r0/test_registry.mjs
```

The test suite uses **public synthetic fixtures only**. It reads the local registry, invokes pure functions and cannot reach the OS input subsystem, accounts, providers, mail, networks or private clipboard contents.

`CoRelationKernelR0.mjs` offers three pure functions:
- `validateSyntheticAssertion(a, registry)`: fail closed on missing, unknown or non-synthetic evidence class.
- `converseView(a, registry)`: swap direction using a declared counterpart, preserving evidence, time, scope, privacy and uncertainty; **no new independent evidence**.
- `negationQuestion(a, registry)`: propose a *falsifiable question*, not assert a negative fact; additionally `effectGate()` always returns **HELD**.

Neither the registry nor this code can automatically send, paste, delete, trade, approve, or remap a mouse.

## Relation algebra: examples that matter

| Source claim | Source-bound converse | **Not** equivalent to |
| --- | --- | --- |
| A `DEPENDS_ON` B | B `REQUIRED_BY` A | "A does not depend on B" |
| Container `CONTAINS` Member | Member `PART_OF` Container | Removing the member from a real filesystem |
| Evidence `SUPPORTS` Claim | Claim `SUPPORTED_BY` Evidence | Proof that the claim is true |
| Projection `RENDERS` Source | Source `RENDERED_BY` Projection | The projection owning or replacing the source |
| X `PRECEDES` Y | Y `FOLLOWS` X | Prediction that the next event will happen |
| Version `SUPERSEDES` Prior | Prior `SUPERSEDED_BY` Version | Deleting historical bytes |
| Claim A `CONFLICT_CANDIDATE_WITH` B | B `CONFLICT_CANDIDATE_WITH` A | A human-independent determination of which is correct |

`CONVERSE` reorients an existing source-bound statement. `NEGATION` proposes a separate statement requiring evidence. `INVERSE` may be a mathematical inverse for an explicitly defined function, but has no automatic meaning for every relationship. `UNDO` is a tested effect-specific rollback, and `COMPENSATE` is a **new authorized effect**, not reversed history. A baseline (`NULL`) means do nothing, **not** that a link is absent.

## First ring and Q&A&@+

The visible rail remains small and progressive: `◎` inspect · `?` unknown/source · `↔` relation · `¬` challenge/negation candidate · `Δ` changed · `⇢` receiver candidate · `⧉` copy candidate · `⟳` revisit. Every glyph must carry accessible text, keyboard/touch/voice equivalents and truthful status.

Questions `WHO/WHAT/WHY/HOW/WHEN/WHERE/WHEREFORE/WHICH/WHAT_IF/WHY_NOT/WHAT_ELSE/NOT_ELSE/FOR_WHOM/HOW_KNOW/HOW_MUCH/WHAT_NEXT` are **inspection or proposal intents**, never email addressing or effect authorization. `@` means receiver candidate or attribution, not a sent message.

## Proof and reuse

[Typed registry](registry.json) inherits pinned source blobs for the public middle relation grammar, CoContextRail, CoDoodle, CoExperimentSpace/CoTurtle and CoReviewSpine. The source is intentionally limited to `synthetic://` inputs and `PUBLIC_SYNTHETIC` privacy for this prototype. Unrecognized fields are discarded, even when they might contain purported credentials or private context.

**No universal graph rewrite:** this review branch does not mutate existing relation objects, migrate user data, update main's `benchmark-evo.jsonl` or silently bind the physical mouse. The [test script](test_registry.mjs) is executable, and the [GitHub CI workflow](../../../.github/workflows/comiddle-relation-semantics-r0.yml) is scope-limited to syntax and tests. A green CI run establishes source constraints only.

**Next useful proof:** have a consenting first-time reader select an object from an approved public-safe demo, inspect `DEPENDS_ON ↔ REQUIRED_BY`, distinguish it from `NOT` and `UNDO`, and confirm that ordinary middle-click still works. Measure comprehension, false invocation, time and ease of cancel. Physical X2 acceptance and independent receiver proof remain HELD.

`RELATION_NAME_NE_VERIFIED_FACT` · `CONVERSE_NE_INDEPENDENT_EVIDENCE` · `NEGATION_NE_FACT` · `GLYPH_NE_AUTHORITY` · `SOURCE_CODE_NE_DEVICE_RUNTIME` · `PUBLIC_BRANCH_NE_MERGED_RELEASE` · `POINTER_NE_ACK` · `LATCHED_INTENT_NE_INFINITE_EXECUTION`.

FOSS Forever · CoGoAll · Working Together Respectfully · privacy-by-design · accessible, optional, reversible.
