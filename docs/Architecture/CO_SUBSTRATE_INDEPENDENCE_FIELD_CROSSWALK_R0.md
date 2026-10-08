# CoSubstrate Independence R0 x CoSubstrateField R0 crosswalk

**State:** `CANDIDATE_CONVERGENCE__NO_CANON_NO_RUNTIME_NO_MERGE_AUTHORITY`

## Finding

CoSubstrate Independence R0 is **not** a new substrate ontology.

Main already contains:

`docs/Architecture/COSUBSTRATE_FIELD_R0.md`

which defines the broader CoSubstrateField+ / CoHardware+ / CoSoftware+ relation field, including:

- substrate classes;
- capability / constraint / privacy / authority relations;
- cross-substrate translation;
- reconstruction;
- invariant preservation;
- loss declaration;
- memory migration;
- replacement / fallback relations;
- a maturity rail explicitly warning against duplicate primitives.

Therefore PR136 is narrowed to a **continuity and migration acceptance profile** over that existing field.

`COSUBSTRATE_INDEPENDENCE_PROFILE_NE_NEW_SUBSTRATE_ONTOLOGY`

## Layering candidate

### Existing CoSubstrateField R0 owns

- descriptive substrate taxonomy;
- substrate relation vocabulary;
- hardware/software/model/network/biological/hybrid substrate relations;
- translation graph;
- loss / approximation / invariant-preservation relations;
- privacy and effect-ceiling dimensions;
- memory-as-substrate relations;
- capability / replacement / fallback relations.

### CoSubstrate Independence R0 owns only

- portability classification for a migration attempt:
  - `PORTABLE`
  - `SUBSTRATE_CONSTRAINED`
  - `SUBSTRATE_BOUND`
  - `UNKNOWN`
- migration acceptance / rejection semantics;
- authority-preservation invariant;
- reconstruction acceptance for declared scope;
- adversarial fixtures proving fail-closed behavior.

## Relation to existing translation graph

Existing CoSubstrateField relations already include:

- `translates_to`
- `emulates`
- `virtualizes`
- `compiles_to`
- `reconstructs_from`
- `approximates`
- `loses_information_to`
- `preserves_invariant_across`
- `incompatible_with`
- `requires_adapter`

PR136 should reuse those relation concepts rather than minting parallel equivalents.

Candidate interpretation:

```text
CoSubstrateField
  describes the substrate + translation relation field

CoSubstrate Independence profile
  evaluates whether one proposed transition preserves
  the invariants / authority / provenance required
  for scoped continuity acceptance
```

## Maturity / lineage matrix

| Concern | Existing CoSubstrateField R0 | PR136 profile | Disposition |
| --- | --- | --- | --- |
| substrate taxonomy | present | referenced only | FIELD owns |
| capability / constraints | present | consumed by validator | FIELD owns |
| translation relations | present | consumed conceptually | FIELD owns |
| loss declaration | present | acceptance input | FIELD owns vocabulary |
| invariant preservation | present | machine-checked | PROFILE owns acceptance check |
| reconstruction | present | machine-checked | layered |
| authority / effect ceiling | present | authority equality enforced | layered |
| portability class | not explicit in current R0 | explicit | PROFILE candidate |
| migration accept/reject | not executable in current R0 | executable synthetic canary | PROFILE candidate |
| runtime substrate scheduler | candidate concept only | not implemented | HOLD |

## Contraction result

No new generic substrate schema is required by PR136 at this stage.

The migration fixture and validator are test/profile surfaces over the existing substrate relation field.

If later work needs a machine-readable shared schema, it should first attempt to extend or project from the existing CoSubstrateField semantics rather than creating a second root.

## Rails

`PROFILE_NE_ONTOLOGY`

`FIELD_NE_ACCEPTANCE_POLICY`

`TRANSLATION_NE_EQUIVALENCE`

`PORTABILITY_CLASS_NE_SUBSTRATE_CLASS`

`MIGRATION_ACCEPTED_NE_IDENTICAL_INSTANCE`

`MIGRATION_ACCEPTED_NE_AUTHORITY_EXPANSION`

`EXISTING_DONOR_NE_AUTO_CANON`

`GREEN_PROFILE_CI_NE_RUNTIME_ADOPTION`

## Next

Keep PR136 draft.

Next useful proof, if earned, is to bind migration fixtures explicitly to CoSubstrateField relation names and verify that the profile can consume a small field projection without duplicating the field vocabulary.
