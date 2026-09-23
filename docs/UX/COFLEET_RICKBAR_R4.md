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
