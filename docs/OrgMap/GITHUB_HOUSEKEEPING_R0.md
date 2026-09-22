# CoCivium GitHub Housekeeping R0

**State:** `CANDIDATE_ORG_TOPOLOGY__NO_RENAME_DELETE_VISIBILITY_OR_DEFAULT_BRANCH_MUTATION`

The GitHub account should be cleaned **before** large migration waves turn today's ambiguity into tomorrow's archaeology.

## CoHereNow

A live census currently exposes 21 repositories: 9 public, 12 private, none archived. The immediate problem is not raw repo count. It is overlapping roles, inconsistent default branches, public placeholders/transients, and several repos whose names or READMEs imply stronger source-of-truth status than the relational architecture should grant them.

### High-signal anomalies

- `CoSources` reports default branch `we-cocarry_hold_landing_20260127T222705Z`.
- `CoAura` and `CoAcademy` still default to `master`.
- `CoRails`, `CoAcademy`, and `CoSources` did not yield a README at the reported default branch/path in the bounded sample.
- `TEMP` is public and explicitly ephemeral-by-policy.
- `CoPolitic-site` is a public placeholder scaffold.
- No repo is archived, so obsolete/parked history is not visible at repo level.
- `MasterPlan`, `GIBindex`, `CoInsights`, and other surfaces use words such as “canonical”; those claims need typed scope, not a crown fight.

## Proposed topology

| Family | Repositories | Intended relation |
|---|---|---|
| Public front doors | CoCivium, EntMent, CoAura, CoAcademy, CoPolitic-site | Human/public projections |
| Index / knowledge / sources | GIBindex, CoInsights, CoSources, MasterPlan | Terms, atoms, sources, plans |
| Coordination / automation | CoBusMirror, CoStacks, CoRails, CoToolbelt | Rails, mirrors, automation, utilities |
| Private stewardship | CoSteward, CoShareHub, CoTrustedWindow, .github | Ops, navigation, trusted views |
| Vaults | CoCrownJewelVault, CoLegalVault | Special-purpose restricted custody |
| Research / futures | CoFutures | Epistemically typed research |
| Transient | TEMP | Expiring ingress only |

The categories are **candidate relations**, not irreversible folder labels. A repo may participate in more than one relation later.

## Migration rule

Do not pour migrated objects into GitHub until the destination has:

1. typed role and effect ceiling;
2. current default-branch proof;
3. exposure classification;
4. collision/duplicate policy;
5. receiver/readproof contract;
6. supersession/retirement pointer policy.

`MIGRATION_RATE_MUST_NOT_EXCEED_RECONCILIATION_AND_RECEIVER_CAPACITY`

## R0 non-actions

No repository was renamed, deleted, archived, made public/private, or switched to another default branch in this wave.

## R1

Run a deeper **read-only** census of branch topology, READMEs, workflows, releases, pointers, stale automation, duplicated schemas and source-of-truth claims. Then produce a typed topology diff before any mutation.

## Rails

`REPOSITORY_NE_ONTOLOGY`  
`GITHUB_NE_CUSTODY_ROOT`  
`DIRECTORY_TREE_NE_SEMANTIC_TREE`  
`LATEST_COMMIT_NE_CURRENT_SEMANTIC_HEAD`  
`RENAME_NE_MIGRATION`  
`ARCHIVE_NE_DELETE`  
`PUBLIC_NE_CANON`
