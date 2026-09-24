# CoNod+ Delegation Gesture R1

**Date:** 2026-09-24  
**State:** `CANDIDATE__BRANCH_ONLY__NO_CANON_RUNTIME_OR_PROVIDER_UI_EFFECT`  
**Scope:** human delegation gesture semantics across chat, RickBar/CoDesktop, CoNode, CoSession, CoBoogie/CoRegroup, CoWorkFabric and future machine-owned surfaces.

## Lead

`CoNod+` is a compact human delegation gesture: "continue within the currently proven mission and rails without making me restate the obvious."

The preferred default gesture remains the single apostrophe:

`'`

The literal word `etc` SHOULD NOT be required for the default gesture.

Why: `etc` carries useful human meaning ("and related adjacent material"), but as an execution token it is deliberately vague and can widen scope unpredictably. The bounded default should therefore be encoded in the CoNod contract, not in extra characters Rick must type.

`CONOD_NE_UNBOUNDED_ETC`  
`HUMAN_SHORTHAND_NE_BLANKET_AUTHORITY`

## Current semantic contract

A bare `'` means:

1. Rebind only the current mission/scope/currentness needed for the next deed.
2. Inspect available durable evidence before relying on conversational inference.
3. Choose the highest-value **bounded** safe deed that advances the current mission.
4. Prefer machine-owned/local or connected tool execution when it reduces human relay and preserves evidence.
5. Respect privacy, authority, effect, collision, currentness and wake/close rails.
6. Externalize a compact receipt/state delta when materially useful.
7. Stop after the bounded deed or explicit HOLD.
8. Do not ask Rick to act as heartbeat, clipboard router or mailman when a safe machine route exists.

Candidate compact gloss:

> **CoNod = proceed one useful bounded notch.**

## Relation to historical apostrophe bootstrap

Historical CoNod material used the apostrophe as a broad bootstrap/rebind invocation, including CoBeacon, broadcast, CoPrime scope, registries and mandate pointers.

That remains useful lineage, but should not require a global full bootstrap on every click.

Modern CoNod SHOULD use **need-relative rebind**:

`gesture -> identify current mission -> check material currentness dependencies -> rebind only required rails -> deed`

This reduces repeated scanning, provider load and human latency.

`REBIND_WHAT_MATTERS_NE_RELOAD_EVERYTHING`

## Relation to session lifecycle

A generic apostrophe MUST NOT by itself reawaken a close-safe/dormant source session whose bound wake predicates remain false.

Therefore:

- active/working session + `'` -> elect one bounded deed;
- twilight session + `'` -> harvest/externalize/prepare succession when useful;
- close-safe/dormant session + `'` -> remain dormant unless a bound wake predicate is true;
- blocked session + `'` -> test the smallest plausible unblock condition, otherwise emit HOLD;
- session with material new evidence + `'` -> bounded CoBoogie/CoRegroup as required.

`GENERIC_NOD_NE_WAKE_PREDICATE`

## What "etc" should mean

`etc` remains useful as a **breadth modifier in natural language**, not as a required keystroke.

Candidate interpretation when Rick explicitly writes `' etc` or equivalent:

> perform the normal bounded CoNod deed, while also harvesting materially adjacent relation candidates that have unusually high reuse value, without silently expanding authority or effect scope.

Adjacency harvest may include:
- relation aliases;
- obvious predecessor/successor links;
- reusable rails;
- negative knowledge;
- CoLex/CoIndex candidate links;
- current GitHub projection opportunities;
- wake/succession conditions;
- high-value CoTheoryAll / CoOps+ / CoMythOps+ relations.

Adjacency harvest SHOULD normally remain proposal/externalization work. It does not authorize extra irreversible effects.

`ETC_EXPANDS_DISCOVERY_NE_EFFECT_AUTHORITY`

## Mouse/keyboard gesture

For a dedicated CoNod mouse shortcut, the safest semantic payload is still just:

`'`

followed by submit.

A macro of:

`<Enter> ' <Enter>`

is useful **only when the leading Enter is intentionally meant to submit whatever is already in the current input box before issuing the separate CoNod turn**.

The leading Enter is not part of CoNod semantics and can be hazardous if partial/unintended text is sitting in a focused input.

Preferred UI-level actions:

- **CoNod button:** insert `'` and submit.
- **Send+CoNod button:** submit current message, then submit `'` as a separate turn.
- **CoNod+Adjacency:** submit `' etc` or, preferably, emit a typed internal `ADJACENCY_HARVEST=true` relation without making Rick type more.

The visible shortcut may stay tiny while the typed machine meaning is richer.

## Candidate typed machine form

```json
{
  "gesture": "CoNod",
  "version": "R1-candidate",
  "deed_budget": 1,
  "rebind": "NEED_RELATIVE",
  "adjacency_harvest": false,
  "authority_expansion": false,
  "wake_override": false,
  "human_relay": "AVOID_WHEN_SAFE_ROUTE_EXISTS"
}
```

For explicit `' etc`:

```json
{
  "gesture": "CoNod",
  "version": "R1-candidate",
  "deed_budget": 1,
  "rebind": "NEED_RELATIVE",
  "adjacency_harvest": true,
  "authority_expansion": false,
  "wake_override": false
}
```

## Distinguish CoNod from CoNode

`CoNod+` = delegation gesture / minimal continuation signal.

`CoNode+` = bounded participant-owned execution/projection surface.

Do not let typography collapse these.

`CONOD_NE_CONODE`

A CoNod MAY be received by a CoNode:

`participant --CoNod--> CoNode --elects--> bounded CoDeed`

but the gesture is not the node, capability or authority.

## CoBoogie / CoRegroup relation

A CoNod can elect CoBoogie/CoRegroup when currentness risk is material:

`CoNod -> currentness check -> [material drift?] -> CoBoogie -> CoRegroup -> bounded deed`

It SHOULD NOT force a full CoBoogie on every invocation.

`NOD_NE_FULL_REGROUP_EVERY_TIME`

## CoWant / CoPressure / CoEnerget relation

The deed election MAY consider:
- current CoWant/objective direction;
- CoPressure/backlog or integration mismatch;
- CoEnerget/capacity;
- currentness;
- reversibility;
- proof debt;
- receiver readiness;
- human attention cost.

More available compute/capacity does not increase authority.

`MORE_ENERGET_NE_MORE_AUTHORITY`

## CoSignal relation

CoNod is also a signal, but a very constrained one.

`CoNod --is_a--> delegation signal`

It carries:
- continuation intent;
- bounded action permission within existing authority;
- expectation of currentness-aware choice;
- preference for low human attention.

It does not carry:
- arbitrary new scope;
- irreversible consent;
- public-release permission;
- financial authority;
- deletion authority;
- identity/credential changes.

`SIGNAL_NE_AUTHORITY`

## UX implication

Rick should not need to remember the expanding semantic payload.

The button can remain one tiny gesture while the system evolves the interpreter behind it with versioned, inspectable semantics.

That is the point: **payload density in the relation, not finger gymnastics.**

## Rails

`CONOD_NE_UNBOUNDED_ETC`  
`HUMAN_SHORTHAND_NE_BLANKET_AUTHORITY`  
`REBIND_WHAT_MATTERS_NE_RELOAD_EVERYTHING`  
`GENERIC_NOD_NE_WAKE_PREDICATE`  
`ETC_EXPANDS_DISCOVERY_NE_EFFECT_AUTHORITY`  
`CONOD_NE_CONODE`  
`NOD_NE_FULL_REGROUP_EVERY_TIME`  
`MORE_ENERGET_NE_MORE_AUTHORITY`  
`SIGNAL_NE_AUTHORITY`  
`RICK_NE_HEARTBEAT`  
`RICK_IS_NOT_THE_MAILMAN`

## Nonclaims

This R1 candidate does not prove:
- provider-native shortcut integration;
- local X2 mouse macro state;
- MCP pickup;
- PS7 execution;
- main-branch acceptance;
- canon/runtime effect.
