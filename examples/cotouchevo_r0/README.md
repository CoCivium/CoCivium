# CoTouchEvo+ R0 | a changed thing may cause a *candidate* ripple

**Status:** `PUBLIC_SAFE_SYNTHETIC_SHADOW__NO_RUNTIME__NO_PROVIDER_CALL__NO_AUTOMATIC_MUTATION`

**CoHereNow.** Extend existing `CoEvoDelta+`, `CoSubscriptionEcology+`, `CoSourceGraph+` and `CoPulse+` with one small, bounded *impact selector*. A change in any object or relation may suggest other objects or receivers worth revisiting. The suggestion must not become an unauthorized write, human notification, provider worker, source of truth, or flood of sessions.

> `CHANGE -> FOLLOW GROUNDED DEPENDENCIES (MAX 3 HOPS) -> RECEIVER-RELATIVE PROPOSAL -> CoTurtle CHALLENGE -> EXPLICIT FUTURE AUTHORIZED EFFECT/RECEIPT OR SLEEP`
>
> `INSPIRED_BY -> REVIEW ONLY`, not automatic dependency propagation.

The supplied fixture is entirely **synthetic**. Terms such as `source:colens`, `co-private`, or `memo:private` describe a dummy graph; they are **not** actual current CoLens source changes, confidential records, live receiver subscriptions or approved operating policies.

## Tested contracts, reuse not replacement

Upstream architecture and exact Git file blobs observed 2026-10-25:

- `docs/Architecture/COSUBSCRIPTION_ECOLOGY_R0.md`, Git blob `4ea7a938bf72128cff2fe944f6738b8f4ea3b50c`: interest and wake subscriptions are not consent or authority.
- `docs/Architecture/COSOURCE_GRAPH_R0.md`, Git blob `301c8951e566de9f9ec0bde16a6b991bd177bd47`: source identity, private access, currentness and evidence differ.
- `docs/Evolution/COALL_GITHUB_EVOLUTION_FABRIC_R0.md`, Git blob `71ae3b819520f16d15c52febb2d60ae59fbefa0a`: CoEvoDelta has object, relation, epistemic, source, scope and mutation classes; external effects are gated.
- `docs/Operations/COLOGICAL_SPAWN_PLANNER_R2.md`, Git blob `daf79b6d88898f5bc49a5f283d00e3871db433ee`: logical work is not live materialization.
- `docs/Operations/COPULSE_SUBSCRIPTION_ROUTER_R0A.md`, Git blob `5afd516966e750cf15442f2993100b06115f2fdb`: delivery candidates cannot advance receiver ACK.

This file is **not a new global bus**. The standalone Python reference never imports credentials or calls GitHub, a provider, X2, a native mouse hook or a scheduler. The next integration should bind a vetted `CoEvoDelta+` to the input contract, not change user devices.

## Run

From this directory with Python 3.11+ (standard library only):

```sh
python3 -m unittest discover -s . -p 'test_*.py' -v
python3 touch_impact.py fixture.json
```

R0 fixture demonstrates 2-hop impact: one changed source, map/text views, one dependent verification test, one private dependent candidate, an ungrounded front-door relation, a private `INSPIRED_BY` candidate, and two **public-only** review suggestions (`CONTRADICTS`, `INSPIRED_BY`).

The pure selector returns sorted, stable proposals and leaves effects exactly at zero. Output names identify *simulation targets only*; no recipient is contacted. A `last_acked_event_id` **input** suppresses replay but the program never advances acknowledgments itself. The reference uses coarse PUBLIC/PRIVATE/RESTRICTED labels as a conservative illustrative gate; it is not an ABAC engine, entitlement resolver or a replacement for credential/device/consent checks.

### Bounded envelopes

| Property | R0 reference ceiling |
| --- | --- |
| Nodes | 250 |
| Edges | 500 |
| Receiver descriptions | 50 |
| Propagation depth | 3 |
| Distinct visited objects | 64 |
| Wake/review proposals | 20 / 12 |
| Per receiver wake proposals | 12 |
| Provider/network/worker/OS effects | **0** |

Limits are validated. The exact fixture caps more tightly (2 hops / 12 visited / 6 proposals / 3 reviews). If a cap is reached, the result reports `TRUNCATED_HELD` instead of silently claiming exhaustive impact coverage.

### Semantics

- Dependency edges use **dependent -> dependency**, and changes follow **reverse dependency** to ask which dependents may need attention. Only `GROUNDED` instances of `DEPENDS_ON`, `DERIVED_FROM`, `RENDERS_FROM` or `VALIDATES_INPUT` propagate shadow suggestions. Even grounded classification is a **fixture declaration**, not independently verified causal truth.
- `INSPIRED_BY`, `RELATED_TO`, `CONTRADICTS`, `SYMBOLIZES` do **not** propagate execution/wakes. Grounded PUBLIC->PUBLIC nonwake edges can produce a capped `REVIEW_CANDIDATE_NOT_WAKE` suggestion. Private names are withheld from that public-safe suggestion list.
- Proposed dependency edges do not propagate by default. Unknown edge semantics fail validation, rather than being interpreted as broad permission.
- A PRIVATE or RESTRICTED dependency may not automatically drive a lower-classification dependent. Public receivers cannot obtain private or restricted target suggestions. The dummy classifications are inadequate for real organization-specific ACLs: actual receivers must requalify identity and authorization.
- `HYPOTHESIS` changes generate **no** wake suggestions; `SYNTHETIC` and `OBSERVED` inputs both generate only **shadow proposals**. The `revision_sha256` field is format-checked, not fetched or cryptographically authenticated.
- One receiver may care, another may sleep. Acknowledged synthetic event IDs are suppressed only for that receiver. The selector does not deliver, send, merge, launch, modify, persist ACKs or promote any proposal to a task.

## What a real R1 would have to prove

1. A **source-origin observed** exact Git/file delta with independently checked source bytes, scoped authority and currentness, not just a labelled input.
2. Relation semantics grounded by actual citations; negative alternatives and falsifiers included. `RELATED_TO` is never a claim of `DEPENDS_ON`.
3. Independent, receiver-specific subscription and authorization proof across at least two distinct receivers. No proof by same-system echo.
4. No private metadata leaks into public caches, media, logs or discovery graphs. Conflicting roles/permissions must fail closed.
5. Differential testing against no propagation, one-hop and all-dependent propagation, including false positives, missed real dependents, token/energy spend, and attention saved.
6. Actual recipient-origin readproof before updating ACK, and a rollback/recovery demonstration before any live effect.
7. Affected human's right to opt out, remove a subscription or inspect why an object was suggested. Per-lane quotas must prevent unwanted infinite nudges.

## CoOmni+ relation

`COOMNI = ADDRESSABLE + RETRIEVABLE + REHYDRATABLE + ROUTABLE + RECOVERABLE`

The possibility space may be open-ended, but no source, relationship, G_d interpretation, image, model, input event, recipient or physical device inherits authority merely through association. A source-bounded media inspiration becomes a **review-only edge**, never an automatic republishing license. This is also the appropriate interpretation of the user's standing `[ EVO ALL BETTERS + ]`, apostrophe and proposed middle-mouse invocation while native X2 acceptance is unproven.

`IMPACT_NE_MUTATION | INSPIRATION_NE_DEPENDENCY | TOUCH_NE_CONSENT | RETRIEVAL_NE_TRUTH | CHANGE_NE_BROADCAST | MORE_RELATIONS_NE_MORE_WORKERS | PUBLIC_PROPOSAL_NE_PUBLICATION | RECEIPT_NE_ACK | SOURCE_NE_RUNTIME | FUTURE_WORK_NE_BACKGROUND_EXECUTION`

FOSS Forever | CoGoAll | Working Together Respectfully.
