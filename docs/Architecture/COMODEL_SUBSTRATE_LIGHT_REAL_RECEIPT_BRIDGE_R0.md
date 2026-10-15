# CoModel substrate-light real receiver receipt bridge R0

**State:** `REAL_RECEIVER_RECEIPT_BRIDGE_CANDIDATE__NO_RUNTIME_NO_CANON_NO_AUTHORITY_CHANGE`

## Purpose

Replace synthetic wave-receipt placeholders with exact, previously produced GitHub-hosted receiver receipts without pretending those receipts already provide a controlled parallelism experiment.

Three prior PR135 fan-in receipts are copied byte-for-byte into a durable candidate evidence surface:

- parameterized-model portability fan-in;
- existing local-worker adapter fan-in;
- exact name+digest bound Ollama-protocol fan-in.

Each copy records:

`Identity | Provenance | ContentHash | LifecycleState | Authority | Owner | Receiver | Dependencies | CollisionDomain | DuplicateOf | Supersedes | VisibleSurface | ProofGate | NextDeed | RetirementCondition`

## Custody shape

The copied receipt objects are **LANDED** on the PR135 candidate branch.

The new workflow elects:

`github-actions:PR135_REAL_RECEIPT_ADVISORY_COMPILER_R0`

as the bounded receiver.

That receiver:

1. downloads the exact historical artifact by run ID + artifact name;
2. verifies live GitHub artifact metadata, including artifact ID, archive digest, source head and expiry state;
3. byte-compares the downloaded receipt with the landed repository copy;
4. verifies the exact content SHA-256 and receipt state;
5. emits its own exact-object readproof.

A successful run may therefore establish:

`PICKED_UP_BY_ADVISORY_COMPILER`

for these three exact landed receipt copies only.

It does **not** establish integration into CoAll runtime, canon or public operation.

## Why the advisory decision must HOLD

These receipts are real receiver-produced CI evidence, but they do not form a controlled same-task experiment comparing:

`physical width 1`

against:

`physical width 3`

under otherwise equivalent conditions.

They also do not contain measured real-world benefit or receiver-pressure observations suitable for causal parallelism attribution.

Therefore the only admissible width decision is:

`HOLD_NO_CONTROLLED_COUNTERFACTUAL_BASELINE`

This is a useful result. Real receipts can enter the loop without pressuring the controller to make up a benefit signal.

## Coverage

The bridge covers only three historical fan-in artifacts produced from PR135 head:

`298fd46c6d78cfecc90fc768d77c09908b36f707`

The source artifacts remain GitHub Actions artifacts with finite retention; the exact receipt bytes are preserved on the candidate branch together with their provenance metadata.

## Next frontier

After this bridge passes, the next bounded experiment is a **paired same-task single-vs-parallel receipt canary** where both modes use the same work object and exact scoring/proof surface.

Only that paired evidence should be eligible to drive the closed-loop width controller.

## Rails

`REAL_RECEIVER_RECEIPT_NE_REAL_WORLD_BENEFIT`  
`ARTIFACT_COUNT_NE_PROGRESS`  
`RECEIVER_COUNT_NE_PARALLELISM_BENEFIT`  
`HISTORICAL_CI_RECEIPT_NE_CONTROLLED_COUNTERFACTUAL`  
`PICKED_UP_BY_ADVISORY_COMPILER_NE_INTEGRATED`  
`LANDED_NE_INTEGRATED`  
`NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`  
`VALIDATION_IS_NOT_ACCEPTANCE`  
`NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE`
