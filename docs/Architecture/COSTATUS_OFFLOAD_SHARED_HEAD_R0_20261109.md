# CoStatusOffload+ | Session-cache separation and portable work checkpoints R0

**2026-11-09 | PUBLIC REVIEW CANDIDATE | NOT PRIVATE CUSTODY, LIVE REMOTE STORAGE, COEX OR DEPLOYED MULTI-WORKER SERVICE**

## CoHereNow

A model/session stores working context; it does not own durable truth. Off-session CoAll work needs a recoverable, versioned **WorkID state spine** shared by authorized workers. Prior architecture already includes [CoVirtualSession morphology](COVIRTUAL_SESSION_MORPHOLOGY_R0.md), [CoSessionAutocycle](COSESSION_AUTOCYCLE_R0.md), [RickBar SQLite/WAL continuity](RICKBAR_CONTINUITY_R1_20261108.md), [CoSessionShadowLedger](../Operations/COSESSION_SHADOW_LEDGER_R1.md), [CoLocalModelWorker/Ollama](../Operations/COLOCAL_MODEL_WORKER_R3.md), [CoSourceGraph](COSOURCE_GRAPH_R0.md), and the [CoPre and CoEx draft](https://github.com/CoCivium/CoCivium/pull/401). Reuse them. A public branch is neither a private vault nor a universal model session backend.

## Separate the layers and availability

1. **Session cache:** ephemeral reasoning, working memory and conversational context, possibly limited by provider. Never sole custody.
2. **Stable WorkID and exact checkpoint:** versioned data, references, NEXT, authority/consent, observer, provenance and status; immutable digest and explicit parent.
3. **Durable elected head:** one version of the work *actually accepted* under a permissioned compare-and-swap writer. A candidate commit or merged draft cannot self-elect.
4. **Replica/transport:** Git branch, local filesystem, CoStead private NAS, remote service, backup or offline packet. Each has independently verified read/write authority, reachability and failure domain.
5. **Worker embodiment:** local Ollama, hosted model, deterministic script, browser/ChatGPT, external service; no inherited ability to wake another provider tab.
6. **Receiver readproof and outcome:** exact receiver-produced acknowledgment, integration and measured usefulness; not merely existence of source.

Offshore state can offer greater capacity and more sharing options, but **not unconditionally**. Test read latency, outage/recovery, available bandwidth, permissions, privacy, costs, portability, legal jurisdiction, independent failure and exit. Inversion: an encrypted local/offline copy may be more available than the allegedly 'offshore' copy. Never copy secrets into a public source store.

## Proposed wave cycle

`SOURCE + BEGIN_RENDER -> CHECK CURRENT HEAD -> READ/COLD RESTORE -> SCOPED STAGE CANDIDATE (many read-only parallel workers) -> VERIFY SOURCE AND PREDECESSOR -> DETECT FIELD COLLISION -> REVIEW DISJOINT CANDIDATE MERGE -> AUTHORIZE/ELECT ONE WRITER -> ATOMIC HEAD COMMIT + READBACK -> RECEIVER ACK IF CLAIMED -> END_RENDER -> CoPre NEXT/Wake`.

Immutable candidate staging scales; authoritative mutation is serialized per collision domain. Each update should retain the full WorkID head lineage and avoid positional transcript dependencies. Candidate states can be materialized with pointers to exact evidence, not the entire session memory dump.

## Actual source-only R0

[CoStatusOffloadR0.py](../../scripts/CoStatusOffloadR0.py) is a *pure* Python standard-library reference, not a new database/service. It defines a bounded public-safe work checkpoint with canonical JSON/SHA-256, stable WorkID, source revision, linked predecessor, next-wake, stop, authority, privacy and six typed section namespaces. It accepts independent source-bound candidate changes, rejects stale/mismatched base and duplicate candidate IDs, identifies overlapping same-field changes, constructs a reversible candidate successor for disjoint fields, and can cold-reconstruct exact state in a separate Python process.

The code **does not write an accepted head**, upload to remote storage, create provider sessions, run Ollama or private models, encrypt data, use a real network, or prove a separate receiver ACK. Source-only self-tests simulate candidate merges; a separate interpreter process confirms pure restart recovery, not independent storage or power/network failover.

**Important R0 limitations:** no cryptographic signer identity or authority validation, cross-host lease/fencing, observed currentness, comprehensive semantic merges, competing alias/definition interpretation, storage transaction, receiver engagement, private-data transport or content redaction. SHA-256 identity detects changes but does not establish validity, ownership, privacy or correctness.

## Design test and negative priors

Run `python3 -B scripts/CoStatusOffloadR0.py --selftest` with read-only CI; test loss of state fields, tampering, different source revisions, duplicate WorkIDs, identical parent sibling conflict, sibling updates on separate semantic keys, private scope, unexpected effect authority, process restart and nonpromoted outcomes.

**Future proof gates:** 1) source verified and synthetic CI; 2) exact source-head currentness; 3) one separately authorized receiver reads the correct checkpoint from a durable independently reachable location; 4) source-collision fencing across real workers and failure domains; 5) 24-hour recovery with one mirror unavailable; 6) real receiver utility and total human relay vs small WorkID-only baseline; 7) provider-specific APIs and local model runtime only when verified. Never stage private session/transcript data in this public example.

## CoIndex and CoTerm role

The index points from a WorkID to one qualified current checkpoint and historical/branch candidates. It preserves provenance and negative knowledge, rather than rewriting definitions. Indexing is not every object already ingested. A session may privately reason about a prospective fact, but its durable contribution must be a typed sourced claim or a held hypothesis.

## CoLOT+ continuation

Priorities: CoObject/CoTerm exact semantic intake, CoSourceGraph currentness, CoIndex recall/alias collision, local Ollama model-adapter acceptance, independent CoStead recovery, CoPre and CoEx two-render wave lifecycle, and sparse impact-triggered validation. Prefer a few independent workers with sound shared state over masses of duplicate agreement. Do not add new always-on automations without verified worker substrate and useful receiver value.

**Nonclaims:** `CHAT_MEMORY_NE_CANON | CANDIDATE_MERGE_NE_ACCEPTED_HEAD | TWO_PROCESSES_NE_TWO_FAILURE_DOMAINS | COMMIT_NE_RECEIVER_PICKUP | GITHUB_NE_PRIVATE_CUSTODY | SQLITE_WAL_NE_DISTRIBUTED_LEASE | OLLAMA_ADAPTER_NE_LIVE_OLLAMA | SOURCE_NE_AUTONOMOUS_WORKER | OFFSHORE_NE_ALWAYS_AVAILABLE`.
