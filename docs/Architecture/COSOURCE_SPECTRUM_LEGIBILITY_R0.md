# CoSourceSpectrum+ / CoLegibility+ R0

**Date:** 2026-09-24  
**State:** `CANDIDATE__BRANCH_ONLY__NO_CANON_RUNTIME_PUBLIC_OR_LEGAL_EFFECT`

## Lead

CoAll should model software and technical systems on a spectrum rather than as only:

`SOURCE_AVAILABLE | SOURCE_UNAVAILABLE`

Useful understanding can arise from many lawful evidence classes even when original implementation source is not available.

`OBSERVABLE_NE_PUBLIC_DOMAIN`  
`INFERABLE_NE_FREE_TO_COPY`  
`CAPABILITY_NE_PERMISSION`

## Evidence spectrum

Candidate classes:

- `DISCLOSED_SOURCE`
- `LICENSED_SOURCE`
- `PUBLIC_SOURCE`
- `EXECUTABLE_ARTIFACT`
- `PUBLIC_SPECIFICATION`
- `API_OR_PROTOCOL_SCHEMA`
- `DOCUMENTED_INTERFACE`
- `FILE_OR_DATA_FORMAT`
- `PUBLIC_BEHAVIOR`
- `LAWFULLY_OBSERVED_RESULT`
- `VERSION_DELTA`
- `COMPATIBILITY_TEST_RESULT`
- `INDEPENDENT_BEHAVIORAL_SPEC`
- `INFERRED_MODEL`
- `INDEPENDENT_IMPLEMENTATION`
- `UNKNOWN_OR_INACCESSIBLE_INTERNALS`

These classes are not a trust ranking.

`SOURCE_AUTHORITY_IS_CLAIM_RELATIVE`

## CoLegibility+

CoLegibility+ is the degree to which materially relevant relations can be observed, tested, explained or independently modeled by a particular observer with particular capabilities, authority and time.

`legibility(system, observer, capability_set, time, access_scope)`

The same artifact may be opaque to one observer and highly legible to another.

`OPAQUE_NE_INTRINSICALLY_UNKNOWABLE`

Candidate dimensions:

- interface legibility;
- behavioral legibility;
- protocol legibility;
- format legibility;
- architectural legibility;
- provenance legibility;
- state-transition legibility;
- dependency legibility;
- semantic legibility.

## CoDerivability+

CoDerivability+ is the degree to which a useful compatible or functionally equivalent implementation can be independently created from admissible evidence.

Track:

- available evidence;
- compatibility target;
- test coverage;
- ambiguity;
- provenance;
- independent-development boundary;
- legal/contractual constraints;
- residual unknowns;
- validation results.

`DERIVABLE_NE_IDENTICAL`  
`COMPATIBLE_NE_CLONED`

## Epistemic limit

Observed behavior does not uniquely determine implementation.

Different implementations can satisfy the same observed contract.

`BEHAVIORAL_EQUIVALENCE_NE_SAME_IMPLEMENTATION`  
`OBSERVATIONAL_EQUIVALENCE_NE_INTERNAL_IDENTITY`

## Publicly observable is not public domain

Public visibility, availability or observability does not by itself establish public-domain legal status.

Software can expose public behavior while separate rights and obligations continue to apply.

`PUBLICLY_OBSERVABLE_NE_PUBLIC_DOMAIN`  
`PUBLICLY_AVAILABLE_NE_UNRESTRICTED_RIGHT_TO_COPY`

## Trade-secret relation

Trade-secret protection is not identical to patent-style exclusivity.

Independent development and lawful analysis can have different treatment from acquisition through improper means, and exact rules vary by jurisdiction and contract.

CoAll should therefore record legal/access context as a separate relation rather than treating technical capability as permission.

`TECHNICAL_CAPABILITY_NE_LEGAL_AUTHORITY`

## Existing CoCivium boundary

The current MasterPlan already prefers public specifications, public documentation, permissively licensed code and clean independent implementations where appropriate, while avoiding ingestion of proprietary competitor material.

That boundary should become machine-readable provenance.

Candidate states:

- `PUBLIC_OPEN_SOURCE`
- `PUBLIC_SPEC_ONLY`
- `BEHAVIOR_ONLY_OBSERVATION`
- `INDEPENDENT_IMPLEMENTATION_INPUTS`
- `PROVENANCE_REVIEW_REQUIRED`
- `INDEPENDENCE_EVIDENCE_COMPLETE`
- `INDEPENDENCE_UNPROVEN`

`INDEPENDENCE_CLAIM_NE_INDEPENDENCE_PROOF`

## Ethics as relations

Relevant relations include:

- acquisition basis;
- authorization;
- confidentiality;
- privacy;
- purpose;
- necessity and scope;
- publication consequences;
- attribution;
- provenance;
- security and safety impact.

`PURPOSE_NE_PERMISSION`  
`CAN_DISCOVER_NE_SHOULD_DISCLOSE`

## CoNonSource+

"Non-source" should not mean "no evidence."

Candidate CoNonSource+ evidence includes:

- observable behavior;
- compatibility fixtures;
- independently derived schemas;
- behavioral specifications;
- public documentation;
- format exemplars;
- version comparisons.

`NON_SOURCE_EVIDENCE_NE_NO_EVIDENCE`

## Compounding capability

Better models, test generation, comparison, indexing and reusable compatibility knowledge can make future systems easier to understand.

That may create strongly compounding capability across domains.

Do not call the growth mathematically exponential without measurement.

`COMPOUNDING_CAPABILITY_NE_PROVEN_EXPONENTIAL_GROWTH`

## Product implications

Candidate bounded CoModules:

- **CoObserve+**: preserve lawful reproducible observations.
- **CoCompat+**: maintain compatibility tests and behavioral contracts.
- **CoDiff+**: compare versions, implementations or providers.
- **CoSpecForge+**: compile evidence into typed interface specifications.
- **CoIndependentBuild+**: preserve independent-development provenance.
- **CoPort+**: move user-owned data and workflows between implementations.
- **CoLegibility+**: show what is known, inferred, ambiguous, inaccessible or gated.

These can braid with RepoZipper+, CoPlatformHelper+, CoMachineCapability+, CoSourceGraph+ and the Open-Source Donor Ecology.

## Long-run hypothesis

The useful long-run claim is not:

> every proprietary implementation becomes fully visible.

It is:

> increasingly large portions of useful behavioral and relational structure may become independently reproducible from lawful observations, reducing the practical value of opacity alone.

That can increase repair, preservation, interoperability, accessibility, competition, migration and resilience.

It can also increase privacy, safety and disclosure risks.

CoAll should optimize **legibility plus optionality**, not indiscriminate publication.

`TRANSPARENCY_NE_UNIVERSAL_PUBLICATION`  
`LEGIBILITY_NE_DISCLOSURE`

## Immediate frontier

1. extend CoSourceGraph with observation/inference evidence classes;
2. add CoLegibility+/CoDerivability+ as candidate terms;
3. add independent-development provenance states;
4. separate technical capability from legal/access authority;
5. use public/open/licensed fixtures for first compatibility canaries;
6. measure reconstruction quality against known open implementations;
7. feed successes and failures into AutoEvo;
8. connect useful results to CoPlatformHelper+/RepoZipper+.

## Nonclaims

This R0 does not establish public-domain status, universal legal conclusions, original-source recovery, measured exponential growth, canon, runtime or public release.

## Rails

`OBSERVABLE_NE_PUBLIC_DOMAIN`  
`INFERABLE_NE_FREE_TO_COPY`  
`CAPABILITY_NE_PERMISSION`  
`BEHAVIORAL_EQUIVALENCE_NE_SAME_IMPLEMENTATION`  
`OBSERVATIONAL_EQUIVALENCE_NE_INTERNAL_IDENTITY`  
`TECHNICAL_CAPABILITY_NE_LEGAL_AUTHORITY`  
`INDEPENDENCE_CLAIM_NE_INDEPENDENCE_PROOF`  
`PURPOSE_NE_PERMISSION`  
`CAN_DISCOVER_NE_SHOULD_DISCLOSE`  
`NON_SOURCE_EVIDENCE_NE_NO_EVIDENCE`  
`TRANSPARENCY_NE_UNIVERSAL_PUBLICATION`  
`LEGIBILITY_NE_DISCLOSURE`  
`COMPOUNDING_CAPABILITY_NE_PROVEN_EXPONENTIAL_GROWTH`
