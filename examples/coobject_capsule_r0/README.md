# CoObject+ / CoSeren+ Offline Capsule R0

**State:** PUBLIC_SAFE_SOURCE_DEMONSTRATION, not a deployed CoAll/CoStead product, a runtime agent, a credential, canon, a general restore system, or receiver-qualified recovery.

## Whole at its declared scale

A small CoObject should be a complete **receiver-useful unit**, not merely a file fragment. This demonstration makes a bounded file-bearing object self-describing and locally reconstructable through **existing** CoObject Vitality, CoGrace, CoMVP/CoLockStep, CoOrbWare and OVP vocabulary. Nothing here establishes that a software component can run its dependencies without a runtime, or that every kind of object has a meaningful executable form.

The capsule is a directory with a manifest and two exact, hashed, *same-machine* copies of one finite byte payload. The CLI can pack, inspect, and restore bytes using Python's standard library. The capsule records what it can do, what it cannot prove, and when to fail closed. It never runs packed code or interprets the content as instructions.

Its minimal task is: **given one bounded file, preserve and recover that file after losing one local copy, without clobbering an existing destination.** This is an actual narrow local file task, not a general self-healing platform.

### Scope and nonclaims

- **CoClosure:** identity, source digest, minimum useful purpose, exact bytes, typed class, unknown provenance and no execution authority.
- **CoReconstitution:** restore only from a matching local byte copy. It does not restore from resemblance, similar meaning, another object, or another provider. It does not reconstruct vanished metadata or inaccessible sources.
- **CoSeren:** the optional `relate` command uses a repeatable seed to pose one cross-object question. The question is not a verified relation, novel theorem, physical observation, or right to connect systems.
- **CoHolographic:** the compact manifest points to enough local evidence for its limited task. A manifest is **not** an entire ecosystem and does not by itself establish independent backup custody.
- **CoGrace:** one missing copy produces an honest degraded state, both missing/corrupt copies produce HOLD, and none of the states reports independent receiver acceptance.
- **CoSeren+/CoSerendipity+** are working research labels, **not** new canonical CoPriMath primitives. Check CoLex and prior art before promoting either.

## Run locally

Python 3.11+ with standard library only. From the directory containing these files:

```sh
python3 coobject_capsule_r0.py pack README.md /tmp/coobj-demo --title "Example object" --kind document --purpose "Recover the exact text"
python3 coobject_capsule_r0.py check /tmp/coobj-demo
python3 coobject_capsule_r0.py restore /tmp/coobj-demo /tmp/coobj-restored.md
python3 coobject_capsule_r0.py relate /tmp/coobj-demo /tmp/coobj-other --seed 53
python3 -m unittest -v test_coobject_capsule_r0.py
python3 demo_coobject_capsule_r0.py
```

The `relate` example assumes a second capsule has been packed at `/tmp/coobj-other`; the demonstration script creates its own temporary second capsule. On Windows use a suitable local folder rather than `/tmp`.

`pack` refuses existing output directories, oversized inputs, source symlinks and unsupported types. `restore` creates a **new** file exclusively. `check` classifies available copies as valid, missing, corrupt or unsafe; an irreversible/privileged effect is never authorized.

## Reconstitution limits

1. A copied file and its backup on one drive are **one failure domain** until independently demonstrated otherwise. Both copies can fail together.
2. A self-packaged SHA-256 manifest detects inconsistency relative to its own recorded bytes. It does **not** authenticate the original author, prove what the source *should have been*, or prevent an attacker replacing both content and manifest.
3. A child object may refer to a parent or sibling. That relation is **not** enough to recreate lost bytes; reconstruction needs exact authorized provenance plus a qualified route to matching content or a proved reversible transformation.
4. A document, question and service can all be complete at their *declared* scales. A service needs an independent real runtime, dependencies, security and consumer test before being called a working deployed product.
5. The algorithm is conservative. When uncertain, keep the last qualified bytes, offer read-only inspection where safe, and report `HELD` or explicit degraded state.

## Fractal / overlapping / in-between research

At object, prodlet, local service, product, organization and federation scales, reuse this grammar:

`IDENTITY | PURPOSE | SOURCE | CURRENTNESS | RIGHTS | DEPENDENCIES | FAILURES | RECOVER | RECEIVER | CHALLENGE | SUCCESSOR`

CoSeren research adds a separately typed, reversible **hypothesis edge**:

`A + relation-lens + B -> question(candidate) -> discriminator -> test -> receipt -> keep / revise / reject`

Do not infer identity, consent, causal relation, recoverable bytes or new authority from mere overlap. Independent paths require independently evidenced custody and failure domains. Retain unusual ideas without forcing them into a production dependency.

## Existing source contracts reused

- [CoObject Vitality R0](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COOBJECT_VITALITY_METABOLISM_R0_20261027.md)
- [CoGrace R0](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COGRACE_PHASE_RELATIVE_STEWARDSHIP_R0_20261101.md)
- [CoMVP / CoLockStep R0](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COMVP_COLOCKSTEP_SOURCE_RELEASE_R0_20261109.md)
- [CoOrbWare Beyond CoSoftware R0](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COORBWARE_BEYOND_COSOFTWARE_R0_20261024.md)
- [CoGbx progressive holography R0](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COGBX_UNIVERSAL_UX_EXEMPLAR_R0_20261027.md)
- [CoPriMath / G_dSide bounded research](https://github.com/CoCivium/CoCivium/blob/main/docs/Evolution/GDSIDE_COPRIMATH_GSLOOP_PUBLIC_R0.md)
- [OVP / CoObject^^ source-closure candidate](../ovp_closure_r0/README.md)

## Proof and next gate

The bundled local tests include valid cases and negative fixtures. A fresh-process demo creates two capsules, loses one copy, restores the exact bytes and produces one explicitly unverified CoSeren candidate. Tests do not establish public hosting, long-term resilience, remote readproof, genuinely separate storage, real X2 usage, or an ongoing autonomous worker. Next measured benefit should be tested against a simple `cp` and an ordinary version-controlled file with a strong recovery baseline, not a strawman.

**Rails:** `OBJECT_WHOLE_AT_DECLARED_SCALE != WHOLE_WORLD | COPY_COUNT != INDEPENDENT_REDUNDANCY | MANIFEST_HASH != ORIGIN_AUTHENTICATION | METAPHOR != OBSERVED_SENTIENCE | HYPOTHESIS_EDGE != EVIDENCED_RELATION | SOURCE_PASS != DEPLOYED_PRODUCT`.
