# CoAgencyEnvelope R0

**State:** candidate source and static tests only

**WorkID:** `CoAgencyEnvelope.R0.20261111`

**Effects executed by this validator:** `0`

## Why this exists

CoPre can remain the expressive human intake grammar until a demonstrably better universal interface exists. It should not also be treated as an execution permission. `CoAgencyEnvelope R0` is the thin machine boundary underneath: exact sources, bounded actions, effect ceiling, human-supervision topology, collision domain, one actuator, lease, lineage and receipts.

It composes rather than replaces:

- [CoParticipant principal relation](../../schemas/coparticipant-principal-v0.1.schema.json)
- [CoNode participation](../../schemas/conode-participation-v0.1.schema.json)
- [standing authorization latch](../../ai/currentness/standing-authorization-latch-r2-20261025.json)
- [session autocycle minimum spawn contract](COSESSION_AUTOCYCLE_R0.md#minimum-spawn-contract)
- [CoEvo universal relation envelope and CoSituation issue](https://github.com/CoCivium/CoCivium/issues/185)

The [structural schema](../../schemas/coagency-envelope-v0.1.schema.json) supports interchange. The [semantic validator](../../scripts/CoAgencyEnvelopeR0.py) enforces relations JSON Schema cannot express.

## Terms stay distinct

| Term | Job |
|---|---|
| `CoAgencyEnvelope+` | Exact permission and effect boundary for one bounded work lineage |
| `CoModality+` | Input/output modality such as text, voice, vision, touch or device |
| `CoSupervisionTopology+` | Human relation to the work: in-loop, on-loop, on-call, after-loop or absent |
| `CoSituation+ / CoSit+` | Context, lifecycle, staleness and wake relations tracked by the broader relation envelope |
| `CoTurtle+` | A recursive child envelope that can preserve or narrow its parent, never amplify it |

No term is an authority source merely because it is visible, named, nested or repeated.

## In-between states

`SHADOW -> PROPOSE -> ATTENDED or DELEGATED -> WITNESSED -> QUIET`

Any active state may narrow to `HELD` where its transition table permits. `QUIET` and `HELD` do not silently wake or elevate themselves. A new proof-bound root is required when an old lineage cannot safely transition.

These are state relations, not a maturity ladder that automatically unlocks effects. In particular:

- `ATTENDED` means a human is present; it does not mean the human consented.
- `DELEGATED` requires a source-bound authorization basis and still obeys all parent ceilings.
- `WITNESSED` records an observation relation; it does not prove receiver ACK or authorize another effect.
- `QUIET` has no allowed action and no actuator.
- `HELD` preserves the blocked edge without inventing permission.

## Inversions

1. Human absence narrows presumed authority. It does not widen it. An absent active actuator must use the checked standing-bounded delegation and `DELEGATED` mode.
2. Human presence is meaningful choice, not routine routing labor. Explicit-current authorization needs an independent verifier; the command-line validator intentionally has none.
3. Silence is no new consent. `NONE` authorization is effectless even if the mode says `ATTENDED`.
4. Break Glass freezes or recovers inside the existing envelope. It cannot add an action, raise an effect ceiling, change a collision domain or create an actuator.
5. `EFFECT_GATED` is a lock, not a higher permission. A child cannot relabel it as a shared write.
6. More clones, sessions, models or turtles do not multiply authority.
7. A receipt string is evidence to inspect, not proof of delivery, readproof, ACK, runtime, canon or CoEx.
8. Diversity is not mandatory novelty. Exact replay remains valid for control, recovery and reproducibility; divergent waves require matched controls and the same envelope rails.

## Recursive turtle invariants

Every child must:

- keep the root WorkID and collision domain;
- use the same node-participation and standing-authorization source digests;
- bind its selected participant manifest exactly;
- retain the validator-pinned bytes of both donor schemas and the standing latch;
- choose a permitted next mode;
- use a subset of the parent's actions;
- keep or narrow the parent's effect ceiling;
- keep or remove the parent's authorization basis, never escalate it;
- stay within depth `16` in R0; and
- share the single elected actuator for its collision domain, if any.

An active `FREEZE` or `RECOVER` state cannot silently return to `OFF` inside the same lineage. A separately evidenced successor root is required.

The validator also rejects cycles, unknown parents, stale or longer-than-24-hour effect leases, source-hash substitutions, action-scope escapes and self-asserted explicit permission.

## Proof boundary

Passing means only that checked JSON objects form a bounded static composition under the current candidate rules. It does not prove:

- live X2, CoStead, CoBus, CoOrbWare or provider integration;
- a human consent event;
- an executed effect;
- a receiver pickup, readproof or ACK;
- uninterrupted survival beyond 24 hours;
- canon, CoEx, merge, deployment or public adoption.

The next stronger proof is not more terminology. It is one independently verified explicit-authorization adapter or one live standing-bounded local effect with cold receiver readback, revocation and recovery evidence.
