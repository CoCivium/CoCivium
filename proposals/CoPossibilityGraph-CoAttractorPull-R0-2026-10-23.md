# CoPossibilityGraph+ / CoAttractorPull+ R0

Status: proposed schema, not runtime, deployment, or proof of discovery. Public research branch; no private resources included.

## Design
A federated, opt-in graph of **resources, hypotheses, absences, alternatives, contradictions and refusals**. Discoverability is not accessibility. References are not consent or receiver acknowledgments.

## Minimal descriptor
```json
{
  "schema": "copossibility-resource-r0",
  "id": "urn:example:resource:1",
  "kind": "material|software|information|relationship|abstract|experiential|hypothesis|absence",
  "capabilities": [],
  "relations": [{"predicate":"depends_on|alternative_to|contradicts|complements|absent_from|unknown_relation","target":"urn:example:resource:2","evidence":"unknown"}],
  "provenance": {"source":"self-described","observed_at":"unknown"},
  "authority": {"access":"unknown","consent":"not_granted","revocable":true},
  "evidence": {"status":"NOT_TESTED","receipts":[]},
  "portability": {"export_formats":[],"substitutes":[]},
  "recovery": {"custody":"unknown","receiver_ack":false},
  "uncertainty": ["capability_not_verified"]
}
```

## Epistemic categories
Material and informational resources can have directly observable operations. Abstract and counterfactual objects can have formal or simulation tests. Experiential or CoSpirit+ descriptions may represent voluntary personal meaning; they do not establish supernatural causation or external operational authority. Unknown or undiscovered resources cannot be enumerated or claimed accessible.

## CoGlueKeys+ and turtle rules
Each relation has source, confidence, test, counterexample, permission boundary and replacement path. Follow dependencies recursively with cycle detection and a fixed work budget. Stop at verified observations, explicit assumptions or unresolved boundaries. Preserve negative evidence and refusal.

## CoAttractorPull+ behavior
1. Ingest authorized manifests, never covertly scrape private devices or accounts.
2. Canonicalize identities while retaining aliases and provenance.
3. Suggest complements, alternatives, incompatibilities and missing capabilities.
4. Rank bounded tests by expected information gain, reversibility and cost.
5. Offer opt-in integrations, portable export and revocation.
6. Emit PASS, FAIL, BLOCKED or NOT_TESTED with receipts; pointer != ACK.

## CoCopy+ thumb/middle-button
Default = inspect selected object and show provenance. Optional follow-up actions = copy portable reference, find relationships, prepare bounded experiment, share to a named authorized receiver. No global mouse hook or broadcasting is implied by this document. Provide keyboard and accessibility alternatives.

## First falsifiable experiment
Test five descriptors: local file, repository, local model, agent workflow and hypothetical absent resource. Assert: schema validation; no unauthorized access; unknown fields preserved; cycle-safe traversal; revocation; exact source provenance; portable export/import; explicit receipt states. Compare against a plain file catalogue on discovery accuracy, human time, false associations, portability and cost.

## Distribution boundary
This is a GitHub research projection only. It is not merged, deployed to X2/CoVIA/nodes, or acknowledged by CoStead or any relationship recipient.

FOSS Forever. Working Together Respectfully. Privacy by design. Optional participation. LoLs = lots of layers, laughs, love and learning.
