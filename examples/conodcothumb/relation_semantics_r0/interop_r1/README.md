# CoMiddle+ Cross-Schema Bridge R1 | No blind relation migration

**2026-10-26 · Review-only candidate · ZERO OS/input/provider effects · dependent on CoMiddle R0 draft PR #295.**

This is a **small source-bound interop canary**, not a new mouse controller, display rail, knowledge root, tool account, independent reviewer or CoEx publication. It reconciles the two existing typed-relation candidates:

- [CoMiddle R0, PR #295](https://github.com/CoCivium/CoCivium/pull/295): 20 typed relations, explicit subject/object types, synthetic-only provenance/valid-time/privacy, source-bound converse.
- [CoMiddle R2, PR #249](https://github.com/CoCivium/CoCivium/pull/249): 36 typed relation IDs, candidate-only converse/negation/alternative operators.
- [CoContextRail R1](https://github.com/CoCivium/CoCivium/blob/main/examples/conodcothumb/context_rail_r1/README.md): elected human-first preview. Native middle-click passes through. **Do not install two hotkey/mouse controllers.**

## The meaningful incompatibility

| Class | R0 relation | R0 converse | R2 form | This bridge |
| --- | --- | --- | --- | --- |
| Same label only | CITES / CITED_BY, PRECEDES / FOLLOWS, SUPERSEDES / SUPERSEDED_BY | Exactly paired | Six names match | **SHADOW_NAME_MATCH_ONLY**, not semantic certification |
| Qualifiable spelling | DEPENDS_ON | REQUIRED_BY | DEPENDS_ON / IS_DEPENDENCY_OF | **HELD_EXPLICIT_ALIAS_REVIEW** |
| Qualifiable spelling | CONTAINS | PART_OF | CONTAINS / CONTAINED_BY | **HELD_EXPLICIT_ALIAS_REVIEW** |
| Unqualified semantic candidate | DERIVED_FROM, SOURCE_FOR, RELATES_TO | See original registry | DERIVES_FROM, IS_SOURCE_FOR, RELATED_TO | **HELD_SEMANTIC_NON_EQUIVALENCE_RISK** |
| Must not silently equate | SUPPORTS / SUPPORTED_BY, CONFLICT_CANDIDATE_WITH | See original registry | HAS_EVIDENCE / EVIDENCE_FOR, CONTRADICTS | **HELD_SEMANTIC_NON_EQUIVALENCE_RISK** |

**R0 has twenty relation IDs. This bridge emits NO approved schema migration for any of them.** It may produce a *documentary* same-name preview or a *held* proposed alias only. It never constructs a runnable R2 request from an R0 source. R0 uses qualified synthetic:// fixture references while R2 uses declared sha256: pointers. Automatically interchanging them would counterfeit source verification.

## Run the small check

On the candidate branch, with Node 22:

    node --test examples/conodcothumb/relation_semantics_r0/interop_r1/test_bridge.mjs

The local fixture check (which modelled the R0 function signatures, **not an exact original R0 byte replay**) returned 32 PASS / 1 SKIP / 0 FAIL. A separate GitHub CI job on this branch additionally pins and imports the **exact R0 and R2 source blobs**. Its run must be observed before declaring cross-branch integration PASS.

The code:
- requires explicit source version, public-synthetic privacy, qualified source marker, valid time and scope;
- preserves source identity, uncertainty, status and direction;
- refuses all unknown, private or malformed assertions and unexpected source drift;
- withholds misleading name matches;
- never writes clipboard contents, captures keys, sends, accesses accounts, executes models, changes input mappings or grants authority;
- intentionally keeps the **Q&A&@+** and glyph labels in the existing R1 human interface.

## Stage and next actual deed

**STATIC SOURCE CANARY**, pending the cross-branch GitHub CI result. No X2 OS/runtime proof, real Logitech MX Master gesture, CoBar integration, native CoOrb display, media transfer or independent user acknowledgment. X2 Desktop Commander remote observer was offline at the most recent inspection. Remote offline **is not** a power-status determination.

Next, a consenting newcomer should use **existing R1**, not this code-only bridge, to distinguish one DEPENDS_ON converse, a NOT question, and a real undo action in ordinary language. Record their time-to-understand, failure points, successful cancel and genuine recipient-origin response.

**FAIL remains preserved:** R0/R2 blind name-based union was rejected in the 2026-10-26 source audit. This patch does not retroactively convert that earlier FAIL into PASS.

\`SAME_NAME_NE_SAME_SEMANTICS\` · \`CONVERSE_NE_NEGATION\` · \`CONVERSE_NE_UNDO\` · \`SCOPED_SOURCE_NE_TRUTH\` · \`SOURCE_POINTER_NE_READPROOF\` · \`BRIDGE_REVIEW_NE_NATIVE_GLYPH_RAIL\` · \`GITHUB_CI_NE_INDEPENDENT_USER\`.

FOSS Forever | CoGoAll | Working Together Respectfully | privacy by design | inclusive and optional.
