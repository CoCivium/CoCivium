# CoAlways Prior Migration Checklist R0

**State:** `CANDIDATE__DRAFT_PR__NO_CANON_RUNTIME_OR_AUTHORITY_CHANGE`

## Purpose

Convert useful prior artifacts, sessions and relations into explicit always-mode posture **without reopening old embodiments merely to keep them alive**.

`PRIOR_NE_PROCESS`  
`OUTLIVE_EMBODIMENT_NE_RUN_FOREVER`

## Per-object migration

For each prior object or relation:

1. **Identify**
   - stable identity or best available lineage key;
   - source artifact/session;
   - observed/currentness time.

2. **Classify value**
   - still relevant;
   - dormant but potentially useful;
   - superseded but provenance-relevant;
   - duplicate/compost;
   - unknown.

3. **Assign always modes**
   - persist;
   - discoverability;
   - reconsider;
   - challenge;
   - watch;
   - wake;
   - AutoEvo;
   - CoOomph;
   - successor;
   - verify;
   - execute;
   - external effect.

4. **Bind wake predicates**
   - source/evidence change;
   - receiver request;
   - contradiction;
   - capability availability;
   - dependency satisfaction;
   - stale/currentness threshold;
   - successor gap;
   - scheduled bounded review where justified.

5. **Bind successor/currentness**
   - predecessor;
   - elected candidate successor;
   - superseded-by relation;
   - unresolved divergence where no successor is elected.

6. **Bind authority/effect ceiling**
   - observe/propose/challenge/verify;
   - branch mutate;
   - local reversible;
   - effect-gated.

7. **Bind evidence**
   - exact source refs;
   - uncertainty;
   - receiver pickup if proven;
   - no inferred ACK/adoption.

8. **Disposition embodiment**
   - remain active;
   - sleep/dormant;
   - close-safe;
   - superseded/compost;
   - recovery-only.

## Default posture

Unless stronger evidence requires otherwise:

`PERSIST = ALWAYS`  
`DISCOVERABLE = ALWAYS`  
`RECONSIDERABLE = ALWAYS`  
`CHALLENGEABLE = ALWAYS`  
`AUTOEVO_ELIGIBLE = ALWAYS`  
`WAKEABLE = YES_UNLESS_EXPLICITLY_NOT`  
`COOOMPH_GOVERNED_WHEN_ACTIVE = YES`  
`EXECUTING = NO_BY_DEFAULT`  
`EXTERNAL_EFFECT = TRIGGERED_OR_AUTHORIZED`

## Migration output

A migration result SHOULD expose:

`object_id | source_refs | lineage_state | currentness | always_modes | wake_conditions | authority_ceiling | successor_refs | embodiment_disposition | uncertainty | evidence_refs | receiver_state`

## Anti-resurrection rails

`MIGRATION_NE_REOPEN_SESSION`  
`DORMANT_NE_DEAD`  
`CLOSE_SAFE_NE_FORGOTTEN`  
`SUPERSEDED_NE_DELETED`  
`WAKE_NE_EXECUTE`  
`AUTOEVO_ELIGIBLE_NE_AUTO_MUTATE`  
`PERSIST_NE_HOT`

## Relation to CoPromptEcology+

This checklist is the bounded prior-estate intake companion to:

- `docs/Architecture/COPROMPT_ALWAYS_ECOLOGY_R0.md`
- `ai/coprompt-always-ecology-r0.json`

The prompt ecology may propose migration candidates, but a claimed migrated state still requires evidence appropriate to the target surface.

`PROMPTED_MIGRATION_NE_MIGRATED`
