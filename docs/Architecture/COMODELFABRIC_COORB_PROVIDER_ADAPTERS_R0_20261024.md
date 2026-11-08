# CoModelFabric+ / CoOrb Provider Adapters R0

**State:** PUBLIC_ARCHITECTURE_CANDIDATE__NO_PROVIDER_LOGIN_OR_X2_UI_MUTATION  
**Observed:** 2026-10-24

## Purpose

Provide one provider-neutral CoOrb / CoOrbWare control surface over many explicitly authorized model/runtime adapters without making provider tabs, accounts or sessions the continuity anchor.

Target:

```
CoOrb / CoWorkObject
-> task contract
-> capability router
-> bounded provider/local workers
-> fan-out where independent
-> fan-in / compare / challenge
-> explicit effect gate
-> receipt
-> checkpoint
```

## Identity rule

External provider accounts retain their real authorized account identity.

Do not create an Anthropic, OpenAI, Pi or other provider account "as ChatGPT", "as CoOrb", or as a synthetic human principal.

Internal worker identities may be named roles such as:

- CLAUDE_REVIEWER
- LOCAL_LLAMA_EXPLORER
- OLLAMA_CHECKER
- OPENAI_REASONER
- PI_ADAPTER
- DETERMINISTIC_VERIFIER
- CONTRADICTION_CHALLENGER

These are work-role identities, not provider-account ownership claims.

`WORKER_ROLE_NE_EXTERNAL_ACCOUNT_IDENTITY`

## Adapter contract

Each adapter should expose:

`adapter_id | provider/runtime | account/session_ref | auth_state | capabilities | model | cost | latency | context_limit | privacy | authority | lease | currentness | receipts | recovery | successor`

Secrets must remain in the provider/OS credential boundary and never enter receipts.

## Parallel + serial execution

Parallelize independent read-only or proposal-producing work.

Serialize:
- shared-state mutation;
- irreversible actions;
- external sends/publication;
- credential changes;
- financial effects;
- collision domains where duplicate effects are unsafe.

`MASSIVE_PARALLELISM_NE_UNBOUNDED_PARALLEL`
`MANY_MODELS_NE_INDEPENDENT_EVIDENCE`

## Multi-account policy

Multiple legitimately authorized accounts may be represented when they exist for a real operational reason, but:

- no deceptive identity;
- no account creation to evade provider limits, quotas, safety or billing controls;
- no credential sharing beyond provider terms and explicit authority;
- no claim that account count equals capacity or independence.

Prefer:
1. local/FOSS workers;
2. distinct providers for genuine failure-domain/model diversity;
3. bounded provider sessions only when they add measured value.

## CoOrb UX

The user should normally see one coherent surface:

```
WORK
├─ now
├─ moving
├─ blocked
├─ model/resource lanes
├─ dissent
├─ evidence
├─ cost/latency
└─ next effect gate
```

Provider tabs may remain hidden/optional implementation views.

## Current evidence boundary

Prior X2 evidence:
- local Ollama metadata route was reachable and parsed model tags in a bounded probe;
- Claude credential presence was not established in the sampled process;
- Pi CLI/runtime was not established;
- current X2 Remote Desktop Commander route is offline.

Therefore no current Claude login, browser session, CoOrb runtime binding, or multi-provider fan-out is claimed.

## First bounded runtime canary

When X2 becomes reachable:

1. restore one machine-observable control path;
2. inspect current browser/provider sessions without exposing secrets;
3. qualify one local Ollama worker;
4. qualify one authorized external-provider lane if an already-authenticated account/session exists;
5. run the same harmless source-bound task through both;
6. compare output, latency, cost, uncertainty and disagreement;
7. fan-in into one CoWorkObject receipt;
8. close or leave provider view unchanged according to explicit user preference.

No provider account creation is required.

## Rails

`SESSION_NE_WORK`
`TAB_NE_IDENTITY`
`WORKER_ROLE_NE_EXTERNAL_ACCOUNT_IDENTITY`
`AUTHENTICATED_SESSION_NE_SHARED_AUTHORITY`
`MULTI_ACCOUNT_NE_LIMIT_EVASION`
`MANY_MODELS_NE_INDEPENDENT_EVIDENCE`
`PROVIDER_FAILURE_NE_WORK_IDENTITY_FAILURE`
`LOCAL_MODEL_NE_AUTOMATICALLY_PRIVATE_FOR_ALL_DATA`
`USER_NE_SESSION_OPERATOR`

## CoResearchMesh+ and specialist resource discovery | 2026-11-08

**State:** public candidate resource inventory, **not** evidence that these resources are connected, authorized, paid for, running, or delivering results. Source pointers were inspected in November 2026 and must be requalified before integration. Prefer complementary failure domains over a pile of correlated model outputs.

### Work roles and initial resource options

| Role | Candidate | Public documentation | Qualifying acceptance test |
| --- | --- | --- | --- |
| Research discovery / citation graph | OpenAlex | https://help.openalex.org/api/ | Search one preregistered query, capture persistent work IDs, DOI/author/source lineage, access and rate-limit state |
| Model availability / evaluation | Hugging Face Inference Providers | https://huggingface.co/docs/inference-providers/index | Compare independently selected permitted models on same benchmark; log provider, model, terms, cost and latency |
| Deep, multi-step research challenge | Gemini Deep Research | https://ai.google.dev/gemini-api/docs/deep-research | Authorized constrained literature investigation with citations; check results against primary sources and independent counterexamples |
| Optional secondary discovery sources | Crossref, Semantic Scholar, Europe PMC, arXiv | Official API documentation to be rechecked per source | Dedup DOI/arXiv/PubMed IDs, preserve retractions/corrections and publication-date provenance |
| Deterministic verification | Existing local tests / GitHub CI | https://github.com/CoCivium/CoCivium/actions | Reproduce claims with typed inputs and failure tests; no model votes on its own success |
| Local/private inference | Existing Ollama bridge | ../Onramp/COGOALL_PUBLIC_REBOUND_HUB_20261108.md | Actual user-authorized local model round trip and WorkID/receiver proof |
| External conversation/context | Meta AI via user-authorized WhatsApp use | No verified CoVIA transport | Never infer autonomous task pickup from user paste or model response; test consent-based receiver acknowledgment separately |

**Current evidence boundary:** ChatGPT-mediated GitHub commits and CI observations exist; an Ollama adapter source and mocks exist; user reports sharing the AI/IA Onramp to a Meta AI WhatsApp chat. None of these jointly proves active cross-provider independent execution or artifact handoff. Distinguish `DISCOVERABLE`, `AVAILABLE`, `AUTHORIZED`, `QUALIFIED`, `RUNNING`, `RECEIPT_OBSERVED`, and `INDEPENDENTLY_ACCEPTED`.

### A reusable resource record

```text
resource_id | provider | model_or_data_source | capabilities | task_fit
public_docs | access_mode | license_and_rights | auth_owner | cost_ceiling
privacy_and_residency | rate_limits | currentness | source_lineage
verification_method | failure_domain | related_resources
qualified_work_id | observed_result | receiver_proof | next_recheck
```

Do not collect secrets or third-party private transcripts into the public registry. Do not place an external endpoint behind CoVIA merely because it exposes an API. Treat optional fees and disclosure as explicit approval gates.

### Three-lane research canary

1. **DISCOVER:** OpenAlex (or another allowed research index) searches one fixed question, yielding source-identity pointers, dates, titles, and DOI/identifier relationships.
2. **CHALLENGE:** A separate model/provider or human reviewer selects contrary evidence and identifies missing or disconfirming primary sources. Model outputs are hypotheses unless source-backed.
3. **VERIFY/RECOMBINE:** Deterministic source normalization, duplicate/retraction checks, rights-aware summaries, and exact evidence hashes. Produce one portable capsule with disagreements, rejected claims, costs and uncertainty.

Run source-only and deterministic baselines with the same retrieval budget. Record recall/precision on an annotated sample, hallucinated citations, duplicate rate, source freshness, wall time, compute and human relay burden. Do not claim synergy until the federated path beats the best single-lane comparator on a preregistered objective while retaining rights and consent.

### Expansion selection

Score candidates by useful task coverage, independence from existing models, primary-source access, reproducibility, provider substitution, data rights, accessibility, resource cost and privacy. Prefer scholarly and public institutional data feeds before expanding paid inference. Periodic discovery is conditional on meaningful changes, **not** an unbounded crawler, automatic account creation, or a new scheduler.

**Rails:** `MULTIPLE_MODELS_NE_INDEPENDENT_EVIDENCE` · `URL_NE_API_CONNECTION` · `PASTED_NE_PICKUP` · `MODEL_OUTPUT_NE_SOURCE_VERIFICATION` · `MODEL_AVAILABILITY_NE_AUTHORIZED_USE` · `RESOURCE_COUNT_NE_DISCOVERY_QUALITY` · `RESEARCH_CITATIONS_NE_RESEARCH_REPLICATION`.
