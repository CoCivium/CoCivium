# CoTerms Public Pilot R0

A small, public-facing glossary for recurring CoCivium language. It is deliberately **not** the whole CoLex estate.

Terms can evolve. Publication makes these meanings inspectable and discussable; it does not magically make them eternal canon, because apparently vocabulary also needs version control.

## How to read this

- **Meaning** is the current public explainer for this pilot.
- **Does not mean** protects against common overreadings.
- **Status** distinguishes mature internal usage from working candidates and naming experiments.
- Corrections, supersession, disagreement, and archival history should remain visible over time.

## Public UX rule

**Complexity behind; consequence in front.** Public surfaces should lead with the user's intent and the material consequence of an action. Transport, routing, retries, leases, adapters, bridge matrices, and other machinery stay behind progressive disclosure unless they are necessary to understand privacy, consent, cost, public exposure, or irreversibility.

For bridges specifically, ordinary users should see actions such as **Share this**, **Bring this here**, **Continue elsewhere**, **Ask another AI**, **Save**, **Publish**, or **Keep private**. The system may select an admissible bridge behind that intent. Power-user and operator views may expose route, provenance, pickup state, diagnostics, and receipts.

## CoCivium

**Meaning:** A developing civic, social, and knowledge software environment for humans and AI systems to coordinate through explicit relationships, inspectable evidence, consent, and portable trust.

**Does not mean:** Not a government, political party, religion, claim of AI sentience, or proof that every described capability is already deployed.

**Status:** `MATURE_INTERNAL_USE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoAll`, `CoPublic`, `CoGateway`, `CoAlive`

## CoAll

**Meaning:** The wider relational workspace and architecture that connects CoCivium projects, artifacts, terms, modules, receipts, histories, and coordination surfaces.

**Does not mean:** Not a claim to contain all knowledge, all data, one universal truth, or one monolithic authority.

**Status:** `MATURE_INTERNAL_USE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoCivium`, `CoRelation`, `CoFarm`, `CoStead`

## CoTerm

**Meaning:** A named semantic handle whose meaning, context, relationships, provenance, and version can be tracked explicitly.

**Does not mean:** A CoTerm is not automatically canonical, permanent, universally agreed, or context-free.

**Status:** `MATURE_INTERNAL_USE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoTerms`, `CoLex`, `CoMeaning`, `CoRelation`

## CoTerms

**Meaning:** The evolving collection of CoTerms together with their meanings, relationships, alternatives, disagreements, versions, and provenance.

**Does not mean:** Not a frozen dictionary and not proof that every historic term should be publicly served.

**Status:** `MATURE_INTERNAL_USE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoTerm`, `CoLex`, `CoMeaning`

## CoLex

**Meaning:** An evolving lexicon or registry for CoTerms, meanings, relationships, anti-meanings, versions, and schema bindings.

**Does not mean:** Not necessarily the sole authority for meaning, and a rendering of CoLex is not itself canon.

**Status:** `MATURE_INTERNAL_USE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoTerm`, `CoTerms`, `CoMeaning`, `CoRelation`

## CoMeaning

**Meaning:** A meaning record that can carry context, time, scope, source, alternatives, and changes instead of pretending a word has one timeless definition.

**Does not mean:** Not an assertion that meaning is arbitrary or that contradictions should be erased.

**Status:** `WORKING_CANDIDATE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoTerm`, `CoLex`, `CoTime+`

## CoRelation

**Meaning:** An explicit typed relationship between things, such as depends-on, derived-from, conflicts-with, supersedes, receives, or projects-to.

**Does not mean:** A relation does not imply causation, authority, equivalence, or currentness unless its type and evidence say so.

**Status:** `MATURE_INTERNAL_USE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoAll`, `CoMeaning`, `CoConfluence`

## CoFarm

**Meaning:** The internal durable workbench and custody layer for artifacts, receipts, schemas, advisory work, and append-only project evidence.

**Does not mean:** Not the public website and not proof that every file present there is accepted, current, or canonical.

**Status:** `MATURE_INTERNAL_USE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoStead`, `CoReceipt`, `CoPublic`

## CoStead

**Meaning:** The stewardship and continuity layer for provenance, receipt indexes, durable handoffs, planning roots, and long-lived project memory.

**Does not mean:** Not an infallible memory oracle and not a substitute for exact evidence or currentness checks.

**Status:** `MATURE_INTERNAL_USE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoFarm`, `CoReceipt`, `CoAll`

## CoReceipt

**Meaning:** A machine-readable evidence object that records what exact action or transition was observed, what it affected, and what remains unproven.

**Does not mean:** A receipt does not by itself prove acceptance, authority, integration, canon, runtime activation, or public release.

**Status:** `MATURE_INTERNAL_USE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoEx`, `CoBreath`, `CoFarm`

## CoEx

**Meaning:** A strong externalization state: an object is appropriately externalized, discoverable, relationally linked, and reusable through its intended surface.

**Does not mean:** Not a synonym for local existence, upload, delivery, canon, runtime activation, or public publication.

**Status:** `MATURE_INTERNAL_USE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoExPublic`, `CoReceipt`, `CoBreath`

## CoExPublic

**Meaning:** A public-safe externalization path or state in which material has crossed explicit privacy, provenance, claim, and release boundaries into a public surface.

**Does not mean:** Not every CoEx is public, and a public-safe candidate is not published until the release edge actually occurs.

**Status:** `WORKING_CANDIDATE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoEx`, `CoPublic`, `CoGateway`

## CoBreath

**Meaning:** A reserved proof term for a demonstrated CoAll mutation with identity, provenance, authority chain, and appropriate merge or readback evidence.

**Does not mean:** Not a progress animation, status message, heartbeat, optimistic summary, or claim that work merely exists.

**Status:** `MATURE_INTERNAL_USE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoReceipt`, `CoPulse`, `CoHeartbeat`, `CoEx`

## CoHereNow

**Meaning:** A compact statement of the best currently supported state at the present observation boundary.

**Does not mean:** Not timeless truth, newest-wins, or a guarantee that every other observer has the same state.

**Status:** `MATURE_INTERNAL_USE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `ExState`, `CoTime+`, `CoReceipt`

## ExState

**Meaning:** An explicit account of holds, unknowns, contradictions, boundaries, and important nonclaims around the current state.

**Does not mean:** Not necessarily failure; uncertainty and held effects can be the correct state.

**Status:** `MATURE_INTERNAL_USE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoHereNow`, `CoConfluence`, `CoTime+`

## CoPulse

**Meaning:** A lightweight visible snapshot or signal that useful activity or progress has occurred at an observation boundary.

**Does not mean:** Not proof of mutation, acceptance, authority, or completion.

**History note:** An earlier public March 2026 rendering used `CoPulse` specifically for a snapshot of system state at a wave. This pilot preserves that source-time meaning as a narrower predecessor and broadens the current explainer without deleting the earlier record.

**Status:** `MATURE_INTERNAL_USE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoHeartbeat`, `CoBreath`, `CoAlive`

## CoHeartbeat

**Meaning:** A recurring liveness or progress signal intended to make long-running work visibly recoverable and less dependent on human prompting.

**Does not mean:** Not proof that the signaled work is correct, current, accepted, or authorized.

**Status:** `MATURE_INTERNAL_USE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoPulse`, `CoAlive`, `CoWorkFabric`

## CoAlive

**Meaning:** An observer-first product quality in which system state, progress, recovery, and meaningful next actions are visibly understandable rather than hidden behind opaque automation.

**Does not mean:** Visual activity alone does not prove operational truth, successful execution, or acceptance.

**Status:** `MATURE_INTERNAL_USE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoCivium`, `CoPulse`, `CoHeartbeat`

## CoTime+

**Meaning:** A relational treatment of time that keeps source-time, observation-time, currentness, prediction, supersession, and parallel temporal branches distinct when needed.

**Does not mean:** Not a claim that there is one universal current file, one latest-wins timeline, or that predictions are facts.

**Status:** `WORKING_CANDIDATE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoHereNow`, `ExState`, `CoConfluence`

## CoDeed

**Meaning:** One bounded action with a clear purpose, effect envelope, and proof or completion condition.

**Does not mean:** Not blanket authorization for adjacent actions or an excuse to expand scope silently.

**Status:** `MATURE_INTERNAL_USE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoReceipt`, `CoWorkFabric`, `CoHereNow`

## CoBridge

**Meaning:** A policy-controlled connection that moves information or work between tools, devices, people, AI systems, or custody surfaces while preserving relevant destination, consent, provenance, and delivery state.

**Does not mean:** Not a user-facing catalog of transport internals, not automatic permission, and not proof that delivery became pickup, acceptance, or integration.

**Status:** `MATURE_INTERNAL_USE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoBackchannel`, `CoGateway`, `CoReceipt`

## CoBackchannel

**Meaning:** A shared durable coordination path through which systems can publish needs, offers, receipts, conflicts, pickup evidence, and return signals without making a person relay them manually.

**Does not mean:** Not hidden inter-chat telepathy, not automatic acceptance, and not authority inherited from message delivery.

**Status:** `MATURE_INTERNAL_USE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoWorkFabric`, `CoReceipt`, `CoConfluence`

## CoWorkFabric

**Meaning:** The work-orchestration layer for compiling, deduplicating, routing, scheduling, backpressuring, and fanning-in many bounded work items.

**Does not mean:** A queue entry is not execution, and parallel research does not imply parallel authority expansion.

**Status:** `MATURE_INTERNAL_USE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoDeed`, `CoBackchannel`, `CoConfluence`

## CoConfluence

**Meaning:** A reconciliation role or process for plural, conflicting, or differently timed evidence so that disagreement can be preserved and resolved without silent newest-wins behavior.

**Does not mean:** Not a rule that all branches must collapse into one view, and not automatic authority to select a winner.

**Status:** `MATURE_INTERNAL_USE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoRelation`, `ExState`, `CoTime+`

## CoPublic

**Meaning:** The public memory, beacon, and dissemination layer for material that has been deliberately prepared for public discovery, reuse, critique, and provenance-aware history.

**Does not mean:** Not a dump of private custody, raw sessions, internal receipts, or every preserved artifact.

**Status:** `MATURE_INTERNAL_USE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoGateway`, `CoExPublic`, `CoCivium`

## CoGateway

**Meaning:** The boundary and translation layer that separates internal and external surfaces, including redaction, public/private routing, APIs, authentication, safety, and trust metadata.

**Does not mean:** Translation does not create authority, erase provenance, or make private material public by default.

**Status:** `MATURE_INTERNAL_USE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoPublic`, `CoExPublic`, `CoID`

## CoID

**Meaning:** A structured identity handle that can carry scope, provenance, qualifiers, permissions, relationships, and context for a person, agent, service, or other participant.

**Does not mean:** Not automatic proof of a real-world identity, trustworthiness, personhood, or authority.

**Status:** `WORKING_CANDIDATE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoGateway`, `CoRelation`, `CoReceipt`

## CoModule+

**Meaning:** A modular capability or experience that can be composed into a larger CoCivium environment while retaining explicit inputs, outputs, dependencies, boundaries, and provenance.

**Does not mean:** A named module is not automatically implemented, enabled, safe for every context, or authoritative.

**Status:** `MATURE_INTERNAL_USE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoCivium`, `CoWorkFabric`, `CoGateway`

## CoCommons+

**Meaning:** A working internal semantic umbrella for the shared relational civic and social environment in CoCivium.

**Does not mean:** Not yet a fixed public brand or claim that the shared environment is one homogeneous community.

**Status:** `WORKING_NAME_CANDIDATE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoAgora+`, `CoAg+`, `CoPublic`

## CoAgora+

**Meaning:** A leading working public-facing name for a lively shared place for news, research, communities, humour, challenges, civic participation, and human-plus-AI interaction.

**Does not mean:** Not merely a social-media feed, not a governing authority, and not yet canonized branding.

**Status:** `WORKING_NAME_CANDIDATE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoCommons+`, `CoAg+`, `CoPublic`

## CoAg+

**Meaning:** A compact working shorthand and possible app mark for the public CoAgora+ experience.

**Does not mean:** Not the full semantic substrate, not a finalized trademark claim, and not proof of a released application.

**Status:** `WORKING_NAME_CANDIDATE` · public rendering `PUBLIC_EXPLAINER_CANDIDATE`

**Related:** `CoAgora+`, `CoCommons+`

---

## Pilot boundary

This glossary excludes private paths, raw session records, credentials, internal incident details, and the unreviewed historical CoTerm estate. Public location is not primary custody, and publication does not create canon, runtime authority, or proof that every named product exists.

Machine-readable companion: `coterms-public-r0.json`.
