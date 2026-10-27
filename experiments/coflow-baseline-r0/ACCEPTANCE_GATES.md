# CoFlowBaseline+ | From synthetic rate to operational evidence

## 0. What is *not* measured here

This R0 contains ten hand-authored fixture runs on *illustrative* environments.
`X2-SYNTHETIC`, `OTHER-SYNTHETIC`, and `SYNTHETIC_ACK` are labels, not
observations or receiver endorsements. No work is sent, no private resources
are scanned, and no operational data from X2 or a remote device are ingested.

## 1. Comparable cohort contract

A performance result belongs to a cohort only when its workload version,
dataset version, device/environment class, and quality contract match. Production
adapters should additionally pin model/runtime versions, thermal/power state,
network boundaries, receiver identity, authority scope, and observation time.

## 2. I/O stage funnel (future adapter)

Capture *separately*: discovered -> qualified -> authorized -> enqueued ->
started -> completed -> correct -> receipted -> independently accepted -> useful.
Keep retries, duplications, errors, cancellations and missing observations.
Never promote production counts into receipt counts by assuming success.

## 3. Three different performance records

- **Peak:** a single qualified, comparable observation. Keep even if it never recurs.
- **Repeat-min:** lowest observed rate of at least three comparable, qualified
  fixture observations. Not a guarantee, lower confidence bound, or availability SLA.
- **Promotion candidate:** a benchmark challenger whose repeat-min beats the
  comparator on *this one dimension*. Production promotion also requires
  correctness, p95/p99, recoverability, energy, cost, rights, and measured
  receiver usefulness where applicable.

## 4. Resource graph and I/O surfaces

Inventory *references* to repositories, files, devices, agents, models,
subscriptions, people (with opt-in), and interface surfaces using existing
CoResourceAttractor descriptors. Track their discovery, authority, freshness,
currentness, cost, failure domain, and alternatives. Unknown or unavailable
resources are not treated as currently usable. Do not bulk copy private
inventories, screen contents, clipboards, credentials, or contacts.

The CoMap, CoOrb, CoBar, and CoOrbWare views should project the *same* typed
work and measurement objects. Projection does not grant permission, create a
worker, perform an effect, or acknowledge a delivery.

## 5. Evolution ladder / stop conditions

1. Replay these fixed synthetic fixtures from source and compare hashes.
2. Choose one real, authorized, small task with a known competent comparator.
3. Record a pinned raw receipt, quality verdict, time, resource use, and cost.
4. Repeat on multiple occasions under matched conditions, including interruptions.
5. Include a fresh independent receiver verdict and a recovery test.
6. Promote only the dimension justified by the evidence. Sleep or retire
   ineffective alternatives, preserving reversible lineage where allowed.

Stop when the quality gate regresses, tail latency or cost exceeds budget,
authentication/authority expires, receiver congestion dominates output, or an
increment fails to show sufficient benefit. Evolving forever does not mean
running forever.

## 6. Evidence gates for current R0

`16 TEST PASS | 7 FIXTURE LEDGER EVENTS | LIVE X2 NOT_RUN |
REAL RECEIVER NOT_RUN | ADOPTION NOT_PROVEN | PROVIDER CALLS 0`

`PEAK_NE_FLOOR | INCREASED_ACTIVITY_NE_BENEFIT | INVENTORY_NE_AUTHORITY |
SHARED_VIEW_NE_SHARED_RIGHTS | RECEIPT_NE_CAUSAL_PROOF`
