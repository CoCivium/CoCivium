# CoFleetProjection+ / RickBar R4 UX Contract

**State:** `UX_CONTRACT_READY__NO_LIVE_GLOBAL_FLEET_CENSUS`

## Lead

The user should interact with **work, fronts, exceptions, and currentness**, not a wall of provider sessions.

RickBar / CoDesktop should therefore project a bounded `CoFleetProjection+` over logical sessions, virtual sessions, materialized workers, models, fronts, and effect leases.

The projection is intentionally smaller than the underlying ecology.

`USER_WORKSPACE_NE_PROVIDER_SESSION`  
`FLEET_PROJECTION_NE_FLEET_TOTALITY`

## One-screen default

The default compact surface may show:

- active workspaces;
- materialized workers;
- virtual contexts by temperature;
- currentness age/status;
- CoPressure summary;
- active effect leases;
- human blockers;
- material warnings/exceptions.

Backend session IDs, provider tabs, receipt hashes, raw queues, and detailed worker telemetry stay behind drill-down unless material.

## Priority order

1. **CoHereNow** — what is materially active for the user.
2. **Meaning** — what changed and why it matters.
3. **NextSafeAction** — only when human action is actually required.
4. **Evidence drill-down** — exact sessions, hashes, leases, receipts, sources.
5. **Backend archaeology** — provider/runtime/session details.

`RICKBAR_FIRST__RECEIPTS_BEHIND`

## Fleet classes

A projection may summarize:

- `WORKSPACE`
- `VIRTUAL_SESSION`
- `MATERIALIZED_WORKER`
- `PROVIDER_SESSION`
- `MODEL_RUNTIME`
- `FRONT`
- `SERVICE_PRINCIPAL`
- `EFFECT_LEASE`
- `WAKE_CONDITION`
- `EXCEPTION`

The classes are not mutually exclusive identities.

## Temperature

Logical work may appear as:

- `HOT`
- `WARM`
- `COOL`
- `DORMANT`
- `COMPOST`
- `ARCHIVE`

Only a bounded HOT/WARM subset normally deserves user-visible prominence.

## Exception-first attention

Raise an item toward foreground only when materially useful, such as:

- human authority needed;
- confidentiality collision;
- effect lease contention;
- currentness failure;
- receiver/pickup failure;
- unresolved destructive/irreversible edge;
- material contradiction;
- provider/local-runtime degradation that blocks work;
- recovery required.

Do not surface routine success merely because a machine produced a receipt.

`SUCCESS_NE_NOTIFICATION_REQUIRED`

## Counts and uncertainty

Counts must carry coverage.

Example:

```json
{
  "virtual_sessions": 83,
  "coverage": "BOUNDED_LEDGER_ONLY",
  "global_fleet_census": "UNPROVEN"
}
```

Never display a bounded count as though it were the entire fleet.

`COUNT_NE_GLOBAL_CENSUS`

## Human blockers

A human blocker exists only when a currently material next transition requires human authority or information.

No human blocker merely because:

- a task exists;
- a virtual session is dormant;
- an AI disagrees;
- a worker is waiting behind another effect lease;
- a local model is unavailable but another safe route exists.

`RICK_NE_HEARTBEAT`

## CoPressure projection

Do not collapse all pressure into one false-precision score.

The compact UX may use a categorical headline such as `LOW / MODERATE / HIGH / DEGRADED`, but evidence drill-down should retain dimensions such as:

- attention debt;
- unexternalized work;
- stale currentness;
- collision pressure;
- fan-in deficit;
- receiver backlog;
- materialization load;
- provider pressure;
- proof debt;
- orphan exposure.

## Humour

Humour may be used in low-stakes presentation or memorable exception wording, but never to obscure an error, safety boundary, uncertainty, or required human decision.

`HUMOUR_NE_STATUS`

## Example compact projection

Illustrative only:

```
CoHereNow
  4 workspaces
  7 materialized workers
  83 virtual contexts
  currentness: healthy
  CoPressure: moderate
  effect leases: 1
  human blockers: 0

Meaning
  Routine work is continuing below the visible horizon.
```

The numbers above are examples, not current claims.

## Data contract

`CoFleetProjection+` should bind:

`projection_id | observed_at | observer | coverage | workspaces | virtual_sessions | materialized_workers | provider_sessions | model_runtimes | fronts | effect_leases | currentness | pressure | human_blockers | exceptions | evidence_refs | nonclaims`

## Runtime boundary

R4 currently defines the UX/data contract only.

It does not prove:

- a global live fleet census;
- RickBar ingestion of this schema;
- provider session discovery;
- live Ollama materialization;
- cross-node fleet currentness;
- automatic user-visible rendering.

Those require separate receiver/runtime evidence.

## Rails

`FLEET_PROJECTION_NE_FLEET_TOTALITY`  
`COUNT_NE_GLOBAL_CENSUS`  
`USER_WORKSPACE_NE_PROVIDER_SESSION`  
`RICKBAR_FIRST__RECEIPTS_BEHIND`  
`SUCCESS_NE_NOTIFICATION_REQUIRED`  
`RICK_NE_HEARTBEAT`  
`HUMOUR_NE_STATUS`


## CoTalkItOut+ peer blocker resolution and RickBar predecessor recovery (R0 proposal, 2026-11-08)

**Boundary:** public UX/agent coordination specification, **not** proof of a deployed protocol, automatic session access, or repaired X2. Preserve earlier working RickBar/CoBar versions and their receipts until independently inventoried; never presume the newest prototype supersedes them.

### Why this belongs in the fleet UX contract

A question, disagreement or missing tool capability should not automatically become a user task. CoTalkItOut+ is a typed, bounded, evidence-first protocol for workers to exchange *resolvable uncertainties* without turning the user into a session courier. A human conversation is one possible escalation, not the default transport.

**Blocker classification:** `EVIDENCE_MISSING | AUTHORITY_REQUIRED | CAPABILITY_MISSING | RECEIVER_UNAVAILABLE | LEASE_CONFLICT | AMBIGUOUS_GOAL | CONTRADICTORY_PROOFS | RESOURCE_LIMIT | UNKNOWN`. An unavailable provider does not block work if a safe authorized alternative exists. Safety or authority cannot be manufactured by a model vote.

**Proposed exchange record:** `talk_id, work_id, seed_revision, blocker_type, question, competing_hypotheses[], source_refs[], source_hashes[], requester_role, responder_roles[], permission_scope, response_budget, deadline_or_wake, proposed_probes[], evidence_refs[], dissent[], adjudication, resolved_state, owner_of_next_effect, nonclaims[]`. Reuse IDs and existing receipts; do not add an unrelated canonical memory store.

### Bounded resolution loop

1. Discover the exact WorkID and relevant older RickBar/CoBar implementation versions, deployment paths and previous observed working behavior. Classify each predecessor as SOURCE_ONLY, OBSERVED_WORKING, RECEIVER_VERIFIED or UNKNOWN. Preserve old versions; avoid silent overwrite.
2. Fetch only source-bound evidence needed for the unresolved question, including contrary evidence and the X2 bridge's *separate* connection status.
3. Ask qualified independent peers for distinct hypotheses or probes. Record who saw which evidence; same model or same source is not independent confirmation.
4. Execute bounded authorized **read-only** tests in parallel. For conflicting writes, use one elected fenced actuator; require idempotency and receipts.
5. Decide RESOLVED_WITH_EVIDENCE, PARTIALLY_RESOLVED, WAITING_ON_EVENT, ESCALATED_FOR_AUTHORITY or FAILED_WITH_EVIDENCE. Record counterexamples, measured cost and next wake condition. A failed experiment is useful, but not a success receipt.
6. Project only material meaning into RickBar: what changed, what remains unproven, and one reversible human action **only when needed**. Never show a permanent wall of agent discussion.
7. Preserve the exchange and source revisions with WorkID/Seed lineage so a successor can resume without replaying chat manually.

### Recovery and adapter acceptance

Implement versioned adapters rather than forcing old RickBar/CoBar to be rewritten. First establish the actual host receiver and an authorized local API or event bridge. Confirm prompt -> local Ollama -> durable WorkID -> visible receiver output -> clean restart -> independent readback. The source CLI and a screenshot are not receiver ACKs. If X2's Desktop Commander connector is offline, report BRIDGE_OFFLINE without claiming X2 itself is off. Keep legacy/native UI and Break Glass usable even if all model workers stop.

### CI+ and operations probes

- Ten repeated equivalent blocker messages produce one unresolved work item, no duplicate user alerts or effects.
- Missing evidence triggers one bounded retrieval; a mock recovered source unblocks without a human message.
- Two disagreeing peers preserve dissent and cannot self-declare independent verification.
- Two concurrent actors contend for the same effect; exactly one fenced writer commits.
- Simulated receiver unavailable results in WAITING_ON_EVENT, not fake ACK.
- A predecessor marked OBSERVED_WORKING remains recoverable after a failed successor migration.
- Restart from the exact Seed revision reconstructs unresolved questions, evidence, lease and next wake without chat-history dependence.
- Authority-required actions escalate once and do not auto-execute on peer consensus.
- Validate round-trip latency, human interventions per WorkID, resolution rate, false resolutions, and regression to previous working UX.

**Nonclaims:** `TALK_PROTOCOL_NE_LIVE_MESSAGING`; `CONSENSUS_NE_INDEPENDENT_EVIDENCE`; `SCREENSHOT_NE_RECEIVER_ACK`; `BRIDGE_OFFLINE_NE_HOST_OFF`; `SOURCE_ONLY_NE_RUNTIME`; `OLD_VERSION_NE_OBSOLETE`. Existing [CoReGroup peer evidence contract](../Evolution/COREGROUP_PEER_EVIDENCE_CONTRACT_R0.md) remains authoritative for proof boundaries.
