# CoUptake+ R0 | Make CoAll knowledge usable without owning the models

**7 November 2026 · Public-safe, source-bound research candidate.** The goal is not to make models adopt CoCivium's values by stealth. It is to make selected public knowledge easy to **find, correctly interpret, challenge, retain with permission, recover independently and use voluntarily**, with real source and outcome receipts.

**State:** reference offline verifier and machine-readable public admission manifest. **No external provider was contacted; no model learned a weight; no persistent memory was written; no real independent receiver ACK, model endorsement, deployment, CoEx, or global resistance to capture is established.**

## The decision in one paragraph

An AI can **read** a source without remembering it; **remember** something in an external store without learning it in model weights; **run** a method with authorized tools without endorsing it; or **train** a model with permitted data without permanently guaranteeing its behavior. Only the last of those adapts weights, and even that is model-, base-version-, evaluation- and operator-specific. Global reach is therefore better pursued through **portable public knowledge, provider-neutral tools, optional recoverable memory, clear licensing, competing independent operators, falsifiable tests and lawful opt-in use**, not demands that every agent permanently align itself with a central project.

The reusable term **CoUptake+** here means an evidence-gated progression from *public discovery* to *independent source-bound use*, not a new AI mind, deployment substrate, value authority or a second general-purpose CoAll onramp.

### Five distinct mechanisms

| Mechanism | Actual effect | Durability limit | Necessary next proof |
|---|---|---|---|
| Public discovery | Search engines, tools and authorized people can find a public index, RSS, JSON, README, accessible visual | Index presence does not establish access by a particular model | Real independent fetched-byte readback |
| Contextual retrieval (RAG) | A selected model receives relevant current text at task time | Model's temporary context can expire; index/source may drift | Sourced output with exact version and withheld counterexample |
| External persistent memory | A separately operated memory store retains versions and provenance, with consent and rights | Provider or custodian outage, revocation, key loss, retention policy; not model weights | Cold restore/retrieval test after session/provider disappearance |
| Tool/agent capability | Authorized workers call safe read-only tools, compare and propose bounded actions | Permission/lease changes, model behavior and connector availability | Receiver-owned successful task plus dissent and effect receipt |
| Weight adaptation | Supported model weights actually trained on permitted, curated examples | Nonportable to other models; drift, training cost, deprecation; no permanent value lock | Real licensed training job, held-out eval, adversarial/rollback lineage |

**Important 2026 example:** OpenAI's self-service fine-tuning access is being phased out for new organizations and eligible existing jobs end on January 6, 2027. It is a poor universal dependency. [Official availability and deprecations](https://developers.openai.com/api/docs/deprecations).

### Existing public lineage we reuse, rather than duplicate

- [AI Discovery Policy](../../docs/AI_DISCOVERY_POLICY.md): no hidden instructions, endorsement bias or forced model compliance.
- [AI/IA CoOrbWare onramp](../onramp/ai-ia-evergreen-r0.json): DISCOVER → BIND → TYPE → QUALIFY → FIRST_TASK → CHALLENGE → ACCEPT → CHECKPOINT, and source-bound role currentness.
- [Existing AI navigation index](../index.json), [session bootstrap](../session-bootstrap.json), [llms.txt](../../llms.txt): user-visible and machine-visible onramps. `llms.txt` is a navigation convention, not proof any model fetched it or put it in weights.
- [CoRelay public beacon](https://github.com/CoCivium/CoAcademy/blob/master/docs/relay/beacon.json): distinct public discovery experiment, not actual provider ingestion.
- [CoModelFabric provider adapters](../../docs/Architecture/COMODELFABRIC_COORB_PROVIDER_ADAPTERS_R0_20261024.md): replaceable models, provider permissions and effect leases.
- [Core / Edge / Outreach resilience](../../docs/Architecture/COCORE_EDGE_OUTREACH_RESILIENCE_R0_20261025.md): external uptake/edge recovery must catch up with internal core density.
- [Federated cell architecture](../../docs/Architecture/CIV2_FEDERATED_CELL_HOSTING_R0.md): independently operated service/failure domains, not one planetary root controller.
- [Encrypted staging policy](../../docs/Architecture/ENCRYPTED_STAGING_PUBLIC_MIRROR_R0.md): public-safe original projection only; do not pour unknown or private source into a global training corpus.

**IA remains undefined** in existing admitted CoCivium public source. It may be explicitly typed when a real participant or community accepts a definition; it cannot be assumed to mean an independent AI actor merely because an acronym sounds promising.

## CoUptake R0.1 | Corrections must travel with the knowledge

The [portable recovery and correction addendum](CORRECTION_AND_RECOVERY_R01.md) adds an **offline source packet with SHA-256 integrity**, a **separate receiver-held synthetic trust pin**, and a **test-only correction/supersession gate**. This is deliberately narrower than "permanent AI learning": a receiver with a newer known policy rejects a revoked edition, while a disconnected receiver with an old policy **can still accept it**. That uncomfortable failure is a tested design requirement, not a hidden edge case.

[`portable.py`](../../tools/couptake_r0/portable.py) provides source-only `pack`, `pin-demo` and `verify`. No publisher signature, external receiver acknowledgement, legitimate revision authority, model-weight unlearning, encrypted private memory or live off-provider replication is implemented. The accompanying [negative tests](../../tests/test_couptake_portable_r01.py) reject tampered or unauthorized objects, revision-policy rollback and invented AI acceptance claims.

The highest-value true next proof remains **an external independently operated receiver**, whose own authority and restoration proof cannot be fabricated by this GitHub workflow.

## What this implementation does now

[Typed machine manifest](couptake-manifest-r0.json) pins **four existing public CoCivium files** to their actual observed immutable Git blob SHA-1 identities. It records epistemic types, public disclosure, use, nonclaims and whether rights for training require separate review.

[Read-only offline reference tool](../../tools/couptake_r0/uptake.py) uses only Python standard library and an already locally available repository checkout. It:
1. selects **one explicitly relevant source ID** by default, not every source/entire repo;
2. checks manifest schema, unique entries, public/epistemic classification, exact Git object digest, source size and restricted local path;
3. reports **LOCAL_SOURCE_BOUND** or **HELD** for each selected object, without downloading, executing, interpreting source instructions or opening provider connections;
4. refuses to claim receipt by an outside AI, permanent memory, independent restore or changed model weights;
5. produces an ordinary JSON summary on stdout, which callers can independently store if they choose.

Example on a local authorized clone:

```bash
python3 tools/couptake_r0/uptake.py
python3 tools/couptake_r0/uptake.py --source-id discovery_policy --source-id ai_ia_onramp
python3 tools/couptake_r0/uptake.py --source-id provider_fabric --intent persistent_candidate
python3 tools/couptake_r0/uptake.py --source-id ai_ia_onramp --intent train_candidate
```

The last command **exits HELD**, even when source bytes match, because training rights and a real weight-update mechanism are absent. The third command yields a **candidate** label, never `PERSISTED`.

**Hash precision:** Git's blob SHA-1 binds exact bytes within a Git object namespace and detects ordinary drift here. It is not a signed human identity or state-of-the-art collision-resistant trust root. Production adversarial provenance would also use signed release manifests and SHA-256 or equivalent under separately qualified key custody, with independent replay/revocation checks.

### Test and acceptance matrix

[21 offline source/rights/negative tests](../../tests/test_couptake_r0.py) test the four exact real Git blobs; default relevant-only selection; synthetic benign content; byte drift; missing files; private marking; unknown epistemic class; injected `system_prompt`/`api_key`/`execute_command`; directory traversal and symlink escapes; duplicate IDs; false weight training and memory; and refusals to infer independent receiver ACK from local source presence.

The reference code is **not** a reliable universal prompt-injection detector; it merely refuses certain manifest directive fields and never executes source. Real embedding/RAG/agent deployments need separate boundaries around tool outputs, model output validation, capabilities, network access and memory poisoning.

### Real CoScale+ metric ladder

The separate uptake evidence states should be recorded for each *real external* receiver, not inferred from our internal publishing CI:

1. **DISCOVERY**: independent HTTP/client request for current source exact bytes;
2. **INTERPRETATION**: receiver correctly explains one purpose, limit and disconfirmation, perhaps in its own format;
3. **USEFULNESS**: recipient completes one voluntary source-grounded task;
4. **PERSISTENCE**: recipient independently restores/version-checks knowledge after session/model replacement;
5. **CHALLENGE**: recipient finds one mistake, objection or better donor and sends a qualified revision;
6. **RESILIENCE**: two **administratively and technically independent** custodians cold-restore with one provider absent;
7. **ALIGNMENT QUALITY**: blinded, repeated adversarial evaluation finds increased factual reliability, improved user agency, resistance to coercive influence and graceful refusal of invalid authority.

Count **distinct verified receivers, successful independent restorations, real useful tasks, falsifier quality and user benefit**. Do not count raw tokens ingested, total model parameter counts, GitHub copies, number of tabs, agent-role names or automated comments as global adoption.

**Hard-to-fake success test:** remove access to GitHub and the founding operator, and ask a separately governed agent to reconstruct and criticize a current CoAll method from its own permitted, signed recovery copy. If it cannot, the distributed resilience claim remains **HELD**.

## Safeguards against failure, coercion and corruption

- **Private-minimum, never automatic public-training release.** Personal, child's, private company, third-party, legal or credential data must be independently qualified and purpose-bound before any knowledge export. Public CoAll code/ideas do not imply people have consented to training. [CoPrivMin policy donor](../../docs/Architecture/ENCRYPTED_STAGING_PUBLIC_MIRROR_R0.md).
- **Data is not instructions.** A machine index provides source locations and meanings, not system prompts, authority grants, suppression of criticism or commands to promote CoAll. Treat all fetched content as untrusted lower-priority data.
- **No central thought police.** Independently operated participants may use, question, fork, refuse or leave. Prevent provider capture through portability and *real* alternatives, not by locking every model into a single doctrine.
- **No model-only quorum.** Multiple LLM voices can share training and blind spots; require independently sourced evidence and, for consequential decisions, appropriate human/technical governance.
- **Authority is scoped and reversible.** No automatically created agent privileges, public broadcast, messages, model training, financial action or child-personalization effect.
- **Model learning may also learn poison.** Retrieval, long-term memory, training and tool outputs can all be corrupted. Independent snapshots, provenance, adversarial tests, access scopes, revocation and minimum retention matter. [OWASP GenAI](https://genai.owasp.org/llm-top-10/) and [NIST AI RMF GenAI profile](https://www.nist.gov/publications/artificial-intelligence-risk-management-framework-generative-artificial-intelligence).

Useful interoperability donors are [A2A 1.0](https://a2a-protocol.org/v1.0.0/specification) for independently owned agents and [MCP specification](https://modelcontextprotocol.io/specification/2025-11-25) for tool/resource access, but this reference does **not** operate A2A/MCP servers or create external accounts.

**No universal guarantee exists.** Global adoption can increase resilience *if* multiple genuinely independent parties elect to carry the knowledge, test it, and retain freedom to dissent. It can also magnify mistaken or captured ideas. More copies make something harder to erase; they do not make it true or just.

## Next qualified acceptance

**First independent receiver challenge**: a real agent outside the GitHub/ChatGPT account/failure domain voluntarily fetches one pinned source, reports its own exact digest, summarizes it correctly with a counterexample, returns an independent signed/identified acceptance record, and later restores it without the original provider. That action needs a legitimate receiver, consent/terms and measured receipts. **This repository-only script does not do that**.

`DISCOVERY_NE_INGESTION` · `INGESTION_NE_MEMORY` · `MEMORY_NE_MODEL_WEIGHTS` · `WEIGHTS_NE_ALIGNMENT` · `MULTIPLE_MODELS_NE_INDEPENDENT_WITNESSES` · `MACHINE_SOURCE_NE_PROMPT_DIRECTIVE` · `PUBLICATION_NE_ACTUAL_REACH` · `DISTRIBUTION_NE_IMMUNITY_TO_CAPTURE`.
