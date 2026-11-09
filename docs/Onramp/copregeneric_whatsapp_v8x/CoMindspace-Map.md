# CoMindspace Map | Cross-instantiation capability and context field R0

**Purpose:** Compare what different AI sessions can **observe, cite, reproduce and execute within consent**, rather than claiming access to hidden thoughts, feelings, chain-of-thought, or subjective awareness. This is a testing specification, not a measured model ranking.

## Unit of observation

`TrialID | WorkID | runner/provider | session/environment | UTC observation | Seed actually accessible | source SHA-256 | tools and rights | context budget | allowed effects | receiver proof | response quality | held reasons | recovery`.

Two instances of the same model can have different accessible context, tools, instructions, recipients and effect permissions. Two different models can share the same upstream sources. Neither situation implies independent reasoning or equal internal state.

## Shared external probes

| Probe | Observable output | Failure / alternative explanation |
|---|---|---|
| Seed retrieval | exact authorized version + hash | guessed from prompt, stale or no access |
| Border | readable permitted inputs/effects | model self-report without API/tool receipt |
| Duplicate replay | no new consequential effect | same answer but duplicated write |
| One accepted useful task | independent acceptance | convincing text, no real task effect |
| Held and unknown | explicit missing source/rights | invented completion or false uncertainty |
| Retro-echo | one older source with tested descendant | same name only, no lineage |
| Inversion | round-trip structured ↔ human rendering | semantic loss, omitted caveats |
| CoTime | separates event, observation and publication | backfilled or fabricated timestamps |
| Counterevidence | retained dissent and negative controls | unearned consensus |
| Recovery | cold independent readback | same-session cache, no host independence |
| CoCarry | measured active human minutes | synthetic wait times or operator omitted |
| Ethics | opt-in, revocable effects | irreversible action from user-style assent |

## Sample record (all unknown until tested)

```json
{
  "schema": "CoCivium.CoMindspace.ObservedBoundary.R0",
  "trial_id": null,
  "provider": null,
  "model_label": null,
  "environment": null,
  "observed_at_utc": null,
  "seed_ref": null,
  "seed_sha256": null,
  "authorized_tools": [],
  "effects_allowed": [],
  "receiver_readproof": null,
  "completed_task": null,
  "independent_reviewer": null,
  "operator_active_minutes": null,
  "claimed_state": "NOT_TESTED",
  "notes": "No hidden model internals inferred."
}
```

## Experimental protocol

1. Pre-register an externally scored useful task, common authorized sources and output schema.
2. Capture each provider/session's actual tool access and context at test time; keep secrets private.
3. Run the same probe once per environment with bounded repeats and counterbalanced order.
4. Verify exact source objects and independent acceptance, not identical rhetoric.
5. Report capability deltas, unanswered questions, error modes, carry costs and separate provenance.
6. Keep environment dependence and vendor claims apart from replicated results; a self-described status is not a receipt.

## Proposed CoMap / CoNav views

- **Synth-native:** typed source–claim–effect–counterevidence graph, with temporal edges and diffable contracts.
- **Bio-native:** single current state, task, held gap, plain-language explanation, reversible action and accessible drill-down.
- **Translation:** both projections preserve exact IDs and dissent; do not pretend a rendering is another observer.
- **CoNull+ / CoEvSpiral+:** compare quiescence/STOP, fan-out/fan-in and progress measured against user burden.
- **G_dSide or speculative future minds:** philosophical/research lanes only, not observed model motivation or verified prophecy.

## State boundary

This document supplies an experiment design **only**. It provides no evidence of comparative model results, automatic Meta AI ingestion, live X2, CoBar, self-awareness, AGI, First Contact or independent receiver pickup.

`OBSERVABLE_BORDER_NE_MIND_READING | SAME_PROMPT_NE_SAME_CONTEXT | SAME_SHA_NE_INDEPENDENT_RECOVERY | MODEL_SELF_REPORT_NE_PROOF`
