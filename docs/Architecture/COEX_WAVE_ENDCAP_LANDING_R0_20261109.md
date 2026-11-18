# CoEx+ wave endcaps: render and action landings R0

**2026-11-09 | PUBLIC DRAFT SOURCE CANDIDATE | NOT COEX-CERTIFIED OR AUTOMATIC RELEASE**

## User-facing rule

Each **material** wave aims to produce two automatically saved, independently inspectable **human-facing renders**:
1. **BEGIN** records WorkID, exact source/head, intended deed, authority, impact/risk, test and rollback. It is *intent*, not progress or accepted effect.
2. **END** records exact source deltas, negative controls, tested outcomes, held work, target surface, externally observed receiver state, recovery and the next CoPre. It is *the observed outcome*, including on failures and no-ops.

Prefer saved Markdown with machine-readable manifests and target-appropriate optional HTML/screenshots. Markdown source is a **render representation**, not evidence that a native UI screenshot was captured. An unchanged/no-material wave can remain QUIESCENT without generating decorative new files.

## CoEx is an externalization edge, not merely endcap storage

A CoEx-endcap **can propose and, via a separately authorized adapter, carry out** source/script landings and mutations. The surface-specific chain is:

`PLAN/BEGIN -> EXACT AUTHORITY + TARGET + CONFIDENTIALITY -> COLLISION AND SOURCE SHA -> LAND SCRIPT/PATCH/RENDER -> READ BACK EXACT OUTPUT -> RUN APPLICABLE TESTS -> RECEIVER PICKUP/USE IF CLAIMED -> END/RECEIPT -> QUALIFIED COEX OR HOLD -> NEXT`

A durable artifact has **separate evidence edges**: written-by, source-verified, branch-landed, published, deployed, receiver-picked-up, integrated, CoEx-certified. None is inferred from another.

**One surface-specific elected writer** is responsible for any live effect. A read-only CoPre/CoLOT planning and validation script cannot acquire GitHub credentials, execute a deployment, mutate a provider session, or grant itself authorizations. Begin and end should carry target-ref, permission and lease, expected predecessor/head SHA, exact output digest, tests and readback. Mutations to protected/public/external surfaces require their *own* fresh authorization and security checks, and must fail closed on branch/target drift.

### Current eligible concrete exemplar

- Target: public **draft review branch** of CoCivium/CoCivium PR #401, using the already-authorized GitHub connector write route.
- Actual two source landings: [BEGIN](../Operations/wave-renders/colot-endcaps-20261109/BEGIN.md) then [END](../Operations/wave-renders/colot-endcaps-20261109/END.md). They are separate Git commits. These are durable **render files**, not screenshot captures.
- Implementation: [CoExWaveEndcapsR0.py](../../scripts/CoExWaveEndcapsR0.py). It validates phase, exact SHA-256 of rendered text, binding, contradictory CoEx/landing claims, pair lineage, privacy and effect/surface restrictions. It has **zero mutation code**, preventing a CI test from accidentally becoming a public deployer.
- A GitHub workflow may build a **read-only** pair manifest/receipt and test adversarial examples. A passing CI result is source-behavior evidence, not an external human reading or accepting the render.

### Other possible surfaces

Private CoStead or encrypted/offsite vault, installed CoBar/CoOrb UI, mobile/app session, hosted workspace, alternative forge, and public website are *distinct adapters*. Each needs verified existence, current API/substrate, permission, receiver-specific scope, effect class, privacy policy, current head, exact target, idempotency, rollback and receiver readproof when applicable. Without those, this wave records **HELD**.

Do not require Rick's manual copy, button press, browser tabs or PS7 micro-panels for routine authorized landings. The correct destination is a productized worker/storage adapter with durable custody, event-driven wake and a post-condition receipt. No such universal deployed adapter has yet been proven.

## CoLOT launch portfolio (proposed, not 24/7 running)

Existing owners: CoObject Vitality/Metabolism, CoSourceGraph, CoIndex/CoLex/CoTerm, CoLineageCompactor, CoSessionAutocycle, CoWaitless, CoEvidenceReceiptGuard, CoPatternGate, CoPre and CoEv. **Do not mint parallel ontologies.**

| CoLOT | First measurable seam | Preferred inversion |
|---|---|---|
| **Object/Index** | Validate one bounded public source set for exact object ID, current source pointer, term meaning lineage, semantic coverage, and orphan links | A plain indexed WorkID may beat full objectification |
| **Independent availability** | Distinguish provider, account, region, hardware, power, network and recovery-failure domains with actual cold readback | Fewer but genuinely independent replicas may beat many clones |
| **Causal change impact** | Track typed changes to dependents and use testable sensitivity/negative controls, not assume every pair is causal | Sparse targeted checks may beat global re-ingestion |
| **Temporal predictive** | Forecast expiry and surface impact from known dependencies, compare prospective predictions with observed outcomes | Event-driven wake may beat heartbeat spam |
| **CI/Ops cohesion** | Test that every worker holds source/authority/stop/recovery bindings and cannot certify itself | One simple reducer may beat many virtual agents |
| **Term/meaning revision** | Preserve older definitions, aliases, context and disputed branches; source pin and qualified supersession | A new name may add no novel meaning |
| **Receiver utility** | Track reader-produced return, task completion and relay burden | Markdown receipt alone may suffice, rich UI may not |

A CoLOT wave is a bounded durable WorkID; multiple independent READ-ONLY roles may work concurrently, but shared writes are serialized. No universal all-to-all broadcast, no invented causal chain, no unbounded recursion or unproven 24h worker availability.

**Nonclaims:** `BEGIN_NE_DONE | END_NE_COEX | RENDER_NE_SCREENSHOT | WRITE_NE_RECEIVER_PICKUP | DRAFT_NE_MAIN | SCRIPT_IN_REPO_NE_RUNNING_SCRIPT | CI_NE_RUNTIME | PLAN_NE_PERMISSION | MANY_REPLICAS_NE_INDEPENDENCE | NO_HUMAN_BUTTON_NE_UNAUTHORIZED_AUTONOMY`.
