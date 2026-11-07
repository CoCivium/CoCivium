# Civ2+ Federated Cell Hosting R0 | Global cooperation, local survivability

**Status:** PUBLIC ARCHITECTURE CANDIDATE · NOT DEPLOYED · NOT CANON · NOT A SECURITY CERTIFICATION  
**Date:** 2026-11-06 (America/Toronto)  
**Scope:** Hosting and continuity architecture for CoCivium, CoAll, CoStead, CoBook, CoMedia, CoDemoWow, CoAthene and future Civ2+ services. Not a claim of planetary authority, complete deployment, disaster recovery, or network access.

## One governing idea

**Globally cooperative; locally survivable; independently recoverable; continuously improvable.**

The physical unit is a **bounded autonomous service cell**. The coordination layer supplies *interoperable protocols, discovery, evidence, typed relationships and consent-aware routing*, not a single global database or omnipotent administrator. No global control plane may be a runtime prerequisite for essential local capability.

This is a composition of existing CoAll contract families, not a parallel ontology or new central executive. A cell can be a laptop/home node, NAS/CoStead installation, community-operated system, regional cloud, public service cluster, independently controlled archival host or offline recovery instance. Small cells do not need Kubernetes. Large cells may adopt orchestrators after proving simpler deployments insufficient.

## Logical planes

| Plane | Responsibilities | Failure behavior |
| --- | --- | --- |
| **Experience / interaction** | CoBar, CoOrb, CoBook, accessible mobile/web, public entrypoints and contributor pathways | Local/offline read-only views and graceful degradation; never show stale data as live |
| **Identity, consent and trust** | Authenticated actors, scoped capabilities, revocation, authorial rights, organizational charters, legal/data-residency constraints | Fail closed on unauthorized effects; preserve local safety-critical operations with preauthorised offline scope |
| **Service / execution cells** | Per-service bounded workloads, sandboxed agents, resource quotas, locally elected actuator, workload isolation | One cell's crash/deployment/budget limit does not cascade into all cells |
| **Data / relation / publication** | Source-bound objects, immutable editions, content-addressed blobs, private encrypted data stores, typed cross-cell references and controlled replication | Read from qualified independent replicas; no unapproved sharing or silent conflict overwrite |
| **Operations / evidence / recovery** | SLOs, health and currentness, audit receipts, queue backpressure, incident command, rollback, cold restore, cross-cell receiver readproof | Retain enough locally to recover without GitHub, the coordinator, or a single provider |

Above these is a **federation interface**, not a planetary root operator: signed service manifests, discoverable *eligible* capabilities, opt-in trust/peering agreements, event envelopes, explicit jurisdiction/consent, and evidence of actual delivery or receiver uptake.

## Service cell minimal contract

A `cell_manifest` declares:
- stable `cell_id`, operator/authority and sovereignty jurisdiction;
- eligible `services`, workload versions/hashes, dependants and API/event schemas;
- accepted identities, revocable capability grants, data classification, licenses and retention rules;
- exact data ownership and replica policy, local encryption/key custodians and rotation;
- `health`, `observed_at`, validity window, completeness and confidence, not just green/red;
- bounded resource budget, compute/energy costs, availability and accessibility targets;
- failover prerequisites, recovery sources, RPO/RTO targets by service tier;
- signed state transitions and recipient readback receipts;
- dependency set: each external dependency is declared, replaceable where feasible, and tested while unavailable.

**No secret keys, infrastructure access tokens, real personal identifiers or private host topology in public manifests.**

## Six non-negotiable invariants

1. **No indispensable global center.** DNS, domain registrars, identity providers, certificate roots, cloud accounts, update services, backup repositories and global analytics can each become single points of failure. Mitigate by verified alternative paths, not merely naming two cloud logos.
2. **Authority and privacy do not federate implicitly.** Capability discovery is not permission; viewing content is not consent. Community cells may have distinct governance and opt out. `GLOBAL_DISCOVERY_NE_GLOBAL_AUTHORITY`.
3. **Separate data consistency classes.** Immutable CoBooks/media/source snapshots can use hashes and distributed caches; collaboration may use explicitly designed merge semantics; payments, legal commitments, elections, account entitlements and irreversible effects need stronger transaction and authorization guarantees. Never use last-write-wins or permissive CRDTs for money, rights or authority.
4. **No split-brain actuators.** Use idempotency keys, fencing tokens, durable commands, replay detection and clearly defined winner election for shared effects. Exactly-once message delivery must not be assumed; engineer effectively-once business effects with receipt-backed deduplication and reconciliation.
5. **Independent survivorship is tested, not declared.** Same-provider replicas, a GitHub fork, a local ZIP, and a cloud backup each offer value, but do not prove a recoverable second failure domain unless cold restore, missing-provider operation and independent readback pass.
6. **Evolution never bypasses deployment gates.** Research and alternative proposals may fan out; production changes use signed builds, reproducible artifacts where feasible, staged rings, canaries, safety/rights review, rollback and one elected authorized release actuator. Stop when net useful verified benefit no longer justifies cost/risk.

## Service classes determine deployment policy

| Service class | Appropriate approach | What must not be inferred |
| --- | --- | --- |
| Public, low-risk CoBook/CoMedia and static demos | Immutable signed releases, multi-provider hosting, edge cache, offline copies, accessible static fallback | Publication does not prove real-time collaboration or consumer acceptance |
| Interactive CoBar/CoOrb and local CoStead | Local-first permitted functions; optional remote acceleration; clear freshness/currentness and safe degraded mode | Visible UI does not prove agent health or remote access |
| Research/AI experiments | Sandboxed jobs, reproducible input hashes, resource budgets, staged reviews and independent critics | Many processes do not imply independent agents, safe actions or more value |
| Organization/identity/outreach | Consent-bound events, transparent identity, local policy, auditable delivery/receiver states | Intent to contact is not permission, sending or delivery |
| Finance/governance/high-consequence operations | Explicit authorized transactional ledgers, strong consistency at commit boundary, multi-party controls where appropriate, immutable audit, jurisdiction review and human-gated reversals | No autonomous financial/public/irreversible act from this architecture |

## Federation lifecycle and CoAll mapping

`DISCOVER -> QUALIFY -> CONSENT/AUTHORIZE -> SOURCE_BIND -> ELECT -> ACT_OR_HOLD -> VERIFY_RECEIVER -> PRESERVE -> RECONCILE -> IMPROVE/RETIRE`

Bind existing:
- **CoReceiverElection+**: capability/authority/cost/confidentiality fit; no execution permission from discovery (CoSteward issue #70).
- **CoB+ unattended recovery**: durable packet, independent receiver, fencing/idempotency and crash-before-ACK test (CoShareHub issue #40).
- **CoAll+ R0 one-input fanout**: two destinations and separate receiver ACKs, with failure queue and nonduplicate retry (CoCivium issue #317).
- **CoWorldUpgrade+**: voluntary flourishing, plural governance, no planetary crown, no unilateral optimization of people (CoSteward issue #282).
- **CoBook+**: one canonical-versioned publication object with multiple projections, source/diff/rights and recovery (existing CoBook rich-media architecture).
- **CoReGroup/CoBoogie/Break Glass**: source/currentness rebind, bounded challenges, fail-closed incident response, explicitly elected actuator.

## A realistic staged rollout

**Stage 0, publication continuity:** Choose the existing public CoCivia AGI HTML or CoDemoWow Truth Gate R1 as one immutable service. Publish exact hash + edition manifest in public GitHub; preserve a distinct operator-controlled copy; independently host a second *reader endpoint* outside the GitHub account/provider; verify access while GitHub is unreachable; prove cold reconstitution on a new clean host from the second custody source. Record DNS ownership/failover dependencies. Historical revisions remain available.

**Stage 1, one local cell:** CoStead and/or X2 registers a read-only manifest and health observer. Test offline CoBar/CoOrb with no cloud control-plane dependency. X2 is currently an **unverified remote receiver**, not an assumed reachable deployment.

**Stage 2, two qualified cells:** Test explicit failover of a single low-risk service, producer/receiver ACK, queue replay and single fenced actuator. Record latency, recovery time, data loss and human touch count. Use a chaos window with consent and rollback. No production fault-injection before isolation.

**Stage 3, governed regional federation:** Adopt multiple operators and physical/regulatory failure domains only where measured demand justifies them. Quorum, secrets, workload identity, legal residency, incident response, abuse defense, regional accessibility and support become verified service-specific controls.

**Stage 4, critical-service assurance:** Separate high-consequence money/governance/safety services from entertainment and research. Independent audits, penetration tests, multi-party authority, red-team exercises, incident drills, sustainable financing and formal risk acceptance are prerequisites, not substitutes for user consent.

## Example R0 scorecard, not measured facts

`usable_reader_endpoint_count | independent_operator_count | independently_cold_restored_count | restore_time | accepted_data_loss | failed_receiver_replays | duplicate_effects | allowed_offline_actions | human_relay_steps | cost_per_verified_useful_outcome | accessibility_acceptance | evidence_freshness`.

A cell's `current` label must bind `observed_at + observed_source + freshness_window + receiver`. Green without observation is a UX failure. Human satisfaction is a distinct voluntary measure, not derived from passing tests.

**First acceptance target:** with GitHub deliberately unavailable in a controlled simulation, a clean independent host reconstructs the exact public HTML/manifest, verifies hashes, serves it to a second browser, exports a receipt, and reports observed RTO/RPO and human relay count. Do not mark success until a distinct receiver performs the readback.

## Threat/operability model to test

Provider failure, account lockout, DNS/registrar outage, identity/key compromise, malicious update, partial network partition, region-wide power loss, storage corruption, insider abuse, link expiration, accidental deletion, jurisdictional restriction, coordinated traffic abuse, AI runaway cost or incorrect actuation, and loss of the project's primary human operator. Don't put all replicas behind one password manager/account, one unbacked signing key or one root CA.

**Critical infrastructure analogy:** Borrow compartmentalization, redundancy, drills, incident command and auditable access from defense/finance operations. Reject universal surveillance, offensive systems, militarized control or a centralized political authority. Human and community autonomy remain design requirements.

## Independent public sources

- [AWS Well-Architected: cell/bulkhead isolation](https://docs.aws.amazon.com/wellarchitected/2024-06-27/framework/rel_fault_isolation_use_bulkhead.html)
- [NIST SP 800-207: Zero Trust Architecture](https://csrc.nist.gov/pubs/sp/800/207/final)
- [CNCF 2026: sovereignty through multi-plane architecture](https://www.cncf.io/blog/2026/08/18/cloud-native-platform-sovereignty-through-multi-plane-architecture/)
- [The Update Framework: compromise-resistant software update design](https://theupdateframework.io/docs/security/)
- [RFC 9420: Messaging Layer Security for appropriate end-to-end encrypted groups](https://datatracker.ietf.org/doc/html/rfc9420)

**State boundary:** Publication of this architecture is only a public source-controlled candidate. It is not proof of installed infrastructure, active federation, independent-host cold restore, service SLO, canon, CoEx, security certification or operational readiness.

## 2026-11-06 | CoAll meta-evolution pivot D1

**Disposition:** Additive architecture delta, not runtime adoption or a substitute for independent receiver testing. Reuse the existing universal relation envelope (CoCivium #185), one-input/two-destination acceptance (CoCivium #317), receiver election (CoSteward #70), world-upgrade anti-capture doctrine (CoSteward #282), and unattended recovery proof (CoShareHub #40). This section sharpens their shared deployment implications.

**Pivot:** From "all objects can evolve" to "**every eligible object, relation, policy, interface, hosting cell, organizational rule and evaluation method may be proposed for evolution; effects are permissioned, reviewable, versioned and independently recoverable**." Evolution of the evaluator itself requires an *external* unchanged baseline/independent adjudicator for each promotion. No cell or model can grant itself new authority by updating the rules that govern it.

### Nine CoAll design deltas

| ID | Delta | Acceptance boundary |
| --- | --- | --- |
| D1 | **Semantic protocol, not vocabulary monopoly** | Typed relation records carry `schema_id/version`, semantic owner, source/proof type, privacy, compatible projections, migrations and explicit unknown fields; no global forced reinterpretation |
| D2 | **Local sovereignty and graceful federation** | Essential authorized offline functions survive coordinator loss; opt-in peering and dissent remain possible; one federation may fork into competing compatible implementations |
| D3 | **Evolving evaluation under an invariant witness** | Proposed new metric/policy scored against previous test suite and independent critics; no self-approved changes that hide regressions or weaken authority |
| D4 | **Separated trust, control and execution planes** | Observability cannot silently actuate; elected actuator is fenced; private data locality, role identity, revocation and policy remain enforced across cells |
| D5 | **Causal receipts, not activity counts** | Effects carry `attempted/committed/receiver_observed/accepted`, pre/post, observation time, claim scope, user benefit and cost; no successful delivery assumed from Git write |
| D6 | **Economics and ecological ceiling** | Verified benefit per human attention, money, energy, material cost and coordination; runaway automation/rate-limiting/maintenance debt become stop conditions |
| D7 | **Multi-domain recovery and anti-monoculture** | One independently controlled cold restore including data, key access where lawful, rights, editions, dependencies and bootstrap instructions; test provider and primary-operator loss |
| D8 | **Plural governance and institutional succession** | Local charters, appeal/withdrawal, conflict-of-interest, rights of minorities, human-protected actions, public audit without private leaks, documented key/role succession |
| D9 | **Experience-first, accessible projection** | Users can tell what is current, what is hypothetical, who acted and how to exit/reverse; offer stable reading mode amid rapid publication evolution |

### Metamorphic contract: evolve the evolver without a global crown

Propose: `SOURCE -> DIFF -> COMPATIBILITY -> THREAT/RIGHTS REVIEW -> SHADOW -> INDEPENDENT TEST -> STAGED CANARY -> PROMOTE_OR_HOLD -> REVOKE/ROLLBACK -> PROVENANCE/WAKE`.

- **Kernel that moves slowly:** identity/authority boundaries, signed or otherwise verifiable source lineage, explicit privacy and licensing, replay prevention, exact receiver effects, emergency suspension and recovery semantics. No magical immutable ontology; changing the kernel requires explicit version transition and independent witnesses.
- **Surface that moves quickly:** reader routes, interface variants, new CoBooks/media, experimental models, diagnostics and low-risk content.
- **Different data consistency needs:** immutable publications may converge by hashes; collaborative edits require merge and attribution; finance/legal/governance decisions require service-specific strongly consistent commit and authorized transaction processes. A federation must make partitions visible and reject split-brain effects.
- **No forced upgrade:** support negotiated interoperability for old clients, migrations with reversible compatibility windows, and no automatic promotion of untrusted metadata into canon.
- **No independent personhood or universal representation inference:** bio/synth differences, local charters, human stakes and individual consent remain distinguishable.

### Specific missing control families to qualify

Supply-chain signing and reproducible builds; secret custody, recovery and revocation; domain/DNS/CA and payment-provider exit; abuse/DoS and cost containment; localization and accessibility; AI output validity and contamination; data residency and child/bystander consent; hardware power/network independence; incident staffing and institutional succession; third-party rights/licensing; audit independence; key-person risk; climate/energy footprint and responsible end-of-life retirement.

### Highest-value falsifiable test

**A single low-risk publication service, two independently administered cells, one hostile partition, zero human relay.**

1. Freeze a public AGI reader or CoDemoWow exact HTML/hash and a machine-readable manifest on cell A. Cell B, under a distinct operator/account/failure domain, must rehydrate it using a non-GitHub custody path.
2. Deliberately deny GitHub and the federation coordinator in a controlled test. Cell B still serves the exact content to an independent reader; record `actual_RTO`, `actual_RPO`, source hash and `reader_ack`.
3. While partitioned, offer B an **incompatible schema migration** and a **revoked capability**. B must preserve existing read-only functionality, HOLD unqualified writes, report conflict and reject the forbidden action.
4. Recover connectivity and reconcile with one elected fenced actuator. Prove no duplicate irreversible effect, no silent data overwrite, no new implicit authority and no missing provenance.
5. Compare baseline usefulness, accessibility, cost and operator burden; preserve negative findings and the independent witness receipt.

**Observed state 2026-11-06:** None of these five acceptance steps is claimed to have passed. This is a design/pivot record, not a service deployment, completed peer negotiation, X2 runtime, global consensus or independently functioning CoAll federation.

**Decision rail:** **KEEP** existing CoAll ontology/relation work; **PIVOT** toward typed interoperable contracts and plural cell authority; **BUILD/TEST** one real independently restored service before multiplying infrastructure. Prefer verified new value to ever more speculative labels.
