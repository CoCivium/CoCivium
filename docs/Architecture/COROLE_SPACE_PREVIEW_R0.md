# CoRoleSpace Preview R0

**State:** `CENSUS_AND_PREVIEW_ONLY__PANELS_AND_STORAGE_DESIGN_ONLY`

## Purpose and existing contracts

This preview counts a bounded configuration space in existing registries and samples it for inspection. It helps choose useful work descriptions without instantiating workers, assigning participants, granting authority, or declaring the combinations meaningful.

The source basis is CoCivium main at [`4d3d3ba7b3758c648705f37c347e644f9e340cdd`](https://github.com/CoCivium/CoCivium/tree/4d3d3ba7b3758c648705f37c347e644f9e340cdd), observed 2026-10-22. Reuse [CoVirtualSession](COVIRTUAL_SESSION_MORPHOLOGY_R0.md), the [CoSpawn schema](../../schemas/cospawn-contract-v0.1.schema.json), [CoSourceGraph](COSOURCE_GRAPH_R0.md), and [CoLineageCompactor](COLINEAGE_COMPACTOR_R0.md). The existing [logical spawn planner](../Operations/COLOGICAL_SPAWN_PLANNER_R2.md) already elects operational roles. This preview adds no alternative election or execution path.

## Six registry axes and the count

| Axis | Single-choice values | Exact input |
|---|---:|---|
| `operational_role` | 12 | `schemas/cospawn-contract-v0.1.schema.json` |
| `morphology` | 19 | `ai/virtual-session-policy.json` |
| `persistence_mode` | 10 | `ai/virtual-session-policy.json` |
| `participant_class` | 12 | `ai/virtual-session-policy.json` |
| `domain` | 21 | `ai/evolution-lanes.json` |
| `epistemic_class` | 11 | `schemas/coevo-delta-v0.1.schema.json` |

The source-version calculation is:

`12 × 19 × 10 × 12 × 21 × 11 = 6,320,160`

These are **raw single-choice tuples**. The axes describe different layers: operational function, session organization, persistence, participant classification, domain, and assertion classification. They are not six orthogonal definitions of a job. Existing contracts can allow multiple domains or persistence modes; this calculation deliberately projects each axis to one choice.

The number is neither all possible roles nor the number of valid contracts, meaningful distinct jobs, eligible assignments, active workers, or independent judges. No permission axis exists. Selecting `OBSERVED` does not supply an observation; selecting `HUMAN_PRINCIPAL` does not identify or create a person. Semantic eligibility remains unknown.

Possible roles remain open-ended because missions, subjects, relations, constraints, and descriptions can evolve. Every particular registry snapshot and bounded description grammar has a finite enumeration. An extensible grammar is not an accomplished exhaustive inventory. A future semantic count would need explicit admissibility and equivalence rules; this preview implements neither.

## CLI contract

Run from the repository:

```sh
python scripts/CoRoleSpacePreviewR0.py --limit 7 --seed '0'
python scripts/CoRoleSpacePreviewR0.py --filter operational_role=CHALLENGER --filter domain=CoPriMath+ --limit 5
```

`--filter AXIS=VALUE` accepts repeated filters on distinct axes, each selecting an exact registry value. `--limit` accepts 0 through 100, default 7; zero requests counts without samples. `--seed` is a string, default `0`.

Output binds the four exact input files by SHA-256, declares filters and sampling parameters, reports the raw product and product after exact filters, and includes sampled configurations. `eligible_configuration_count` is `null`. The filtered product counts syntactic choices only. Unknown axes or values and repeated axes are invalid inputs.

The sampler is `SHA256_SEEDED_COPRIME_STRIDE_V1`, bounded by the requested limit. Identical source bytes, filters, seed, and implementation reproduce the preview. A bounded sample is not proof of balanced coverage, representativeness, or semantic validity. Record the sampler version when comparing outputs. Counts are computed from the files actually read; the table above records this source snapshot. File hashes bind bytes and provide no proof that those files are current.

The CLI reads local inputs and emits output. It makes no remote calls, launches no workers, and performs no file writes. A sampled tuple is not a CoSpawn contract and cannot bypass its authority, confidentiality, currentness, receiver, lease, collision, budget, or recovery checks.

## Definition, assignment, evidence, and authority

Keep four records separate: a role definition describes a function; an assignment binds an identified participant to that function for a task; an evidence channel records how claims were obtained; an authority binding specifies permitted effects and constraints. Embodiment and lease describe concrete execution separately.

[W3C PROV-DM](https://www.w3.org/TR/prov-dm/) distinguishes agents, activities, entities, their associations, and derivations. [NIST RBAC](https://csrc.nist.gov/projects/role-based-access-control/faqs) separately models user-role assignment, permission-role assignment, activation, and separation of duty. Here, descriptive role labels confer no security permissions. Existing authorization governs every assignment and effect.

## Seven-seat advisory panel template — DESIGN_ONLY

Instantiate seats only for a named question, pinned inputs, decision owner, acceptance criteria, and declared budget. Seats can remain unassigned or run sequentially.

| Seat | Existing operational role | Required contribution |
|---|---|---|
| Proposal | `WORKER` | Candidate answer and explicit assumptions |
| Formal check | `VERIFIER` | Derivation, invariants, or precise proof gap |
| Empirical check | `OBSERVER` | Actual observations, method, and missing measurements |
| Challenge | `CHALLENGER` | Counterexamples, alternative explanations, falsifiers |
| Perspective | `TRANSLATOR` | Relevant ethical, experiential, spiritual, or other interpretation |
| Provenance check | `VERIFIER` | Source lineage, currentness, and dependence audit |
| Synthesis | `PROJECTION_COMPILER` | Supported conclusions, dissent, and unresolved next gates |

Each contribution records claim, epistemic class, exact source bindings, observation method and time where applicable, uncertainty, counterevidence, and next verification step. Disclose participant/model identity, shared model families, shared source artifacts, and shared tools. Independent-source status defaults to unknown until established. Seven seats do not imply seven independent observations. [Multiagent debate research](https://arxiv.org/abs/2305.14325) reports task-specific gains; its results do not validate every panel or convert generated agreement into external evidence.

Spiritual, experiential, ethical, and formal lenses are explicit perspectives. A reported experience can be retained as a human report while its explanation remains a separate claim. Physical assertions require suitable observations, tests, and corroboration regardless of the perspective producing them. Roles do not establish beings, capabilities, consciousness, or physical effects. Preserve dissent without forcing consensus or treating vote share as confidence.

The template permits at most two review rounds and nesting depth two. Before assignment, declare maximum running and pending tasks, elapsed time, tokens or cost, and effect scope. All children share one aggregate remaining parent budget; each allocation reduces that same budget. Children remain within the parent's authority ceiling, and nesting cannot replenish budget or authority. Stop on acceptance, exhausted budget, or a complete round without a verified material improvement. Preserve unresolved questions and resumable dependencies. [Ray's running-task](https://docs.ray.io/en/latest/ray-core/patterns/limit-running-tasks.html) and [pending-task](https://docs.ray.io/en/latest/ray-core/patterns/limit-pending-tasks.html) patterns illustrate distinct concurrency and queue bounds; resource declarations still require operational enforcement.

## Relation and storage experiment — DESIGN_ONLY

Use a bounded corpus under CoSourceGraph and CoLineageCompactor. Deduplicate immutable source artifacts by byte identity only within compatible custody and confidentiality boundaries, retaining custody locators, hashes, versions, and readproofs. Preserve multiple provenance associations for identical bytes. Store typed relations such as `derived_from`, `contradicts`, and `projection_of`; retain ambiguity and original locators. Semantic relationships may cycle even when immutable version dependencies form a DAG.

Build disposable views for three queries: sources behind a claim, unresolved contradictions, and receiver-relevant current candidates. Bind every view to source hashes, transformation version, and freshness cutoff. [Merkle DAGs](https://docs.ipfs.tech/concepts/merkle-dag/) motivate shared content-addressed structure; [materialized views](https://learn.microsoft.com/en-us/azure/architecture/patterns/materialized-view) motivate query-specific projections with explicit refresh and consistency rules. Neither requires adopting a new service.

Compare direct queries with derived views on identical inputs. Measure stored bytes including indexes, build time, query time, refresh cost, and staleness. Verify reconstructed artifact byte equality and query-result equality; an unexplained mismatch fails the experiment. Content identity does not prove truth or [continued availability](https://docs.ipfs.tech/concepts/persistence/). No benchmark improvement, novel physical substrate, live panel, or runtime adoption is claimed.
