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


## CoDiscovery+ external resource qualification and independent model federation (2026-11-08)

**State:** PUBLIC_RESOURCE_RESEARCH_CANDIDATE; neither credentialed provider enrollment nor autonomous cross-platform pickup is established. This augments the existing adapter contract rather than replacing it. Do not represent a user-reported WhatsApp/Meta AI exchange, local Ollama source, or other ChatGPT window as an independently acknowledged active agent.

### Diverse contributor classes

1. **Local/open models:** Ollama and compatible authorized local runtimes for private, repeatable tasks. Source code and earlier observations do not prove the current X2 runtime.
2. **Hosted frontier and specialist models:** explicitly authorized commercial APIs, with independent failure-domain, task capability, permission, retention, cost and terms checks.
3. **Multi-provider discovery/hosting:** Hugging Face Inference Providers (https://huggingface.co/docs/inference-providers) exposes multiple providers, language/vision/embedding/audio and related tasks. Qualify the *actual underlying model and serving provider*, not merely the common gateway; the same base model hosted twice is not independent evidence.
4. **Scholarly discovery substrate:** OpenAlex (https://help.openalex.org/api/), Semantic Scholar Academic Graph (https://api.semanticscholar.org/api-docs/graphs), and Crossref (https://www.crossref.org/documentation/retrieve-metadata/rest-api/) expose structured works, identifiers, references and/or provenance. Cross-check sources, deduplicate by DOI and other stable IDs, inspect retractions, versions, licenses, dates, and known coverage bias. Metadata is not proof of article claims.
5. **Specialist systems and tools:** search indexes, code execution/test systems, symbolic solvers, libraries, datasets, accessibility and translation tools, domain expert review, deterministic validators. Not every useful contributor needs to be an LLM.
6. **Human contributors:** consenting domain experts and affected communities can contribute knowledge, dissent, qualitative outcomes and governance review. Human assent is not presumed by AI recommendations.

### Discovery-to-production rail

`DISCOVER -> LICENSE/RIGHTS CHECK -> CAPABILITY PROBE -> PRIVACY/COST PREFLIGHT -> BENCHMARK -> DIVERSE CHALLENGE -> QUALIFY -> TASK LEASE -> INDEPENDENT RESULT READBACK -> MONITOR -> REQUALIFY/RETIRE`.

Register `resource_id, stable_provider_id, model_id_and_version, underlying_model_family, modality, capabilities, limitations, license, data_residency, retention, auth_state, terms_checked_at, freshness, cost_basis, latency_sample, benchmark_refs, failure_domain, provenance, permission_scope, current_status, recovery_route, nonclaims`. Unknown fields remain UNKNOWN rather than fabricated. Search and refresh available resources periodically only where an actual authorized scheduler/receiver is installed; merely publishing this contract is not ongoing monitoring.

### Research/curation work object

`question -> search_queries -> source_records -> identity_dedup -> evidence extraction -> contradiction/retraction checks -> independent model syntheses -> expert or deterministic challenge -> uncertainty map -> curated answer -> citations and content-rights -> successor checkpoint`.

Use source IDs/DOIs and verifiable passages, not a generated bibliography alone. Preserve separate evidence quality and model confidence. Avoid copying restricted full texts into public artifacts. Capture missed-findings audits and negative results.

### Anti-monoculture and routing

- Different providers do not guarantee independent reasoning: track model lineage, training overlap, shared sources, prompts and routing provider. Reward *independent checks* rather than number of model responses.
- Split research into independent retrieval, synthesis, adversarial challenge, factual/identifier verification and integration roles. Blind or stagger initial proposals where feasible to reduce anchoring.
- Route simple deterministic work to programs, not expensive models. Escalate specialist tasks only when measured gain exceeds costs and risks.
- Require one fenced effect writer, budget ceilings, consent and privacy gates, independent receiver receipts and a recoverable WorkID.
- Allow healthy idle/sleeping workers; no fake heartbeat or forced participation. External vendor accounts remain separately authenticated.

### First falsifiable federation trial (NOT_RUN)

A public-safe research question with stable source corpus goes to (A) local model, (B) an independently qualified external model, (C) non-LLM scholarly metadata verification, and (D) a challenge/curation reviewer. Compare independent source recall, factual accuracy, citation correctness, contradictory-paper discovery, latency, total cost, privacy exposure, and incremental gain over the best single-worker baseline. Keep errors and cases where the federation loses. A written plan is not proof that these workers executed.

**Priority:** recover a functioning X2 RickBar/CoBar receiver and a local Ollama roundtrip, then attach one authorized external model and an independent structured research source. Preserve the earlier working UX and Break Glass.

### Additional specialist research adapter to qualify (source check: 2026-11-09 UTC)

**Gemini Deep Research**, distinct from ordinary Gemini model inference, is documented as an agentic research workflow through the [Google Interactions API](https://ai.google.dev/gemini-api/docs/deep-research). As of the checked documentation it is **preview**, runs with `background=true` and stored interaction state, and can use Google Search, URL Context and code execution. Its cost, retained data, authorization, provider lineage, prompt-injection exposure and review requirements must be preflighted before any real task. It is **DISCOVERABLE only**, not an authorized CoModelFabric worker, and its citations must be challenged against original sources.

**Low-friction non-LLM complement:** [OpenAlex works endpoint](https://help.openalex.org/api/endpoints/) offers initial keyless public metadata queries; larger usage and cursor paging may require a key and budget according to its [authentication guide](https://help.openalex.org/api/authentication/). Track OpenAlex record IDs, DOI/ORCID/ROR where appropriate, coverage gaps, licensing, version/retraction metadata, and API provenance. A source identifier is not evidence of the scholarly claim itself. Existing Hugging Face provider routing is also a credentialed, possibly billable operation; never count multiple hosts of the same model as independent support.

**One three-lane candidate benchmark (NOT_RUN):** a preregistered public-safe research question, equal retrieval and cost budgets, (1) deterministic OpenAlex/Crossref metadata discovery, (2) independently authorized specialist model challenge such as Gemini Deep Research, and (3) source-identifier/retraction review before final curation. Compare verified citation precision/recall, contradiction discovery, missed-findings rate, user value, latency and net cost against each single-lane baseline. Result status stays `CANDIDATE` until the relevant provider is separately authorized, a real outcome recorded and independently reproduced.

**Rails:** `RESOURCE_POINTER_NE_CONNECTED_WORKER` · `MODEL_PROVIDER_NE_INDEPENDENT_FAILURE_DOMAIN` · `API_PREVIEW_NE_PRODUCTION_READY` · `NO_FEES_CREDENTIALS_OR_PUBLIC_TRANSMISSIONS_WITHOUT_AUTHORIZATION`.
