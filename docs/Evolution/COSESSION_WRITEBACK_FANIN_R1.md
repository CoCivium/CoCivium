# CoSession Write-Back Fan-In R1

**State:** `FRESH_MAIN_FANIN_CANDIDATE__STATIC_CI_PASS__CURRENT_MAIN_FIXTURE_REPLAY_PENDING__NO_RUNTIME`

R1 forward-ports the unique session-to-CoEvo/receiver machinery from draft PR #23 onto current main after the CoEvo convergence, virtual-first lifecycle, CoPulse R0G, evidence, subscription, and highlight descendants have already landed.

The forward relation is:

`CoSession relational projection -> CoEvoDelta+ -> fan-in -> receiver-relative fanout -> packet compile -> repository route OR public CoPulse projection -> delivery evidence -> receiver readproof -> pickup eligibility`

## Why this matters

Virtual-first autocycling is useful only if sessions can contribute durable, typed deltas without becoming permanent provider tabs or requiring Rick to ferry their findings.

This pipeline gives bounded sessions an explicit write-back path while preserving:

- one semantic CoEvo substrate rather than a rival session-specific ontology;
- receiver-relative routing;
- current-head and confidentiality gates;
- packet compilation distinct from delivery;
- delivery distinct from pickup;
- pickup distinct from integration.

## Forward-ported exact donor objects

The scripts and schemas were copied by exact Git blob identity from PR #23's donor branch. They are not silently rewritten during the fan-in.

The historical donor canary is also preserved:

- packet `packet:50AC4F6AFA73BA9A8256C473`;
- packet blob `deeea8811c06ddce652b782fdaaad153ccf76f79`;
- receipt blob `06cd4dac599029cb4d8d6f3f0e750eda3e855081`;
- lifecycle `LANDED`;
- receiver pickup `UNPROVEN`.

`LANDED_NE_PICKED_UP`

## Fresh-main gate

Before merge, read-only CI must:

1. Python-compile the five forward-ported scripts;
2. parse the seven JSON schemas;
3. parse the historical packet and receipt objects;
4. assert the historical receipt does not claim receiver pickup or integration;
5. assert no executable workflow permissions beyond `contents: read`.

That proves syntax/parse integrity only.

A later current-main fixture replay is still required before claiming the donor canaries reproduce on the new combined mainline.

`STATIC_CI_NE_RUNTIME_CANARY`

## Virtual-session relation

The virtual-first lifecycle may use this path when a bounded work unit produces a material relation:

`work unit -> material delta -> session projection -> CoEvo compile -> fan-in/dedupe -> receiver routing -> sleep`

No material delta and no bound wake predicate still routes to sleep.

## Rails

`SESSION_PROJECTION_NE_PARALLEL_SEMANTIC_STANDARD`  
`COMPILATION_NE_ACCEPTANCE`  
`PROJECTION_NE_DELIVERY`  
`DELIVERY_NE_PICKUP`  
`PICKED_UP_NE_INTEGRATED`  
`PUBLIC_SAFE_LABEL_NE_PUBLICATION_APPROVAL`  
`STATIC_CI_NE_RUNTIME_CANARY`  
`NO_NEWEST_WINS`


## Static CI result

Fresh PR CI passed on workflow run `35959750310` for branch head `2fc33fdea4c595d281bd118a0c8025e651483d18`.

The CI first exposed a real donor defect: `CoEvoReceiverFanoutPlanner.py` contained an unterminated newline literal. That narrow defect was repaired. A second CI attempt correctly revealed that searching serialized receipt text for the token `PICKED_UP` falsely treated explicit nonclaims such as `LANDED_NE_PICKED_UP` as positive lifecycle claims; the guard was repaired to validate the positive lifecycle fields and required nonclaims separately.

This negative knowledge is part of the fan-in evidence. A donor branch being historically useful does not make every byte executable on a newer mainline.

`DONOR_HISTORY_NE_CURRENT_EXECUTABILITY`  
`NONCLAIM_TEXT_NE_POSITIVE_CLAIM`
