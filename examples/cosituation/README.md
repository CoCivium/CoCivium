# CoSituation R0 | Cross-substrate relation-envelope acceptance (shadow)

**Status: synthetic candidate / no runtime, device or authority integration.**

This implements the *specific unproven acceptance step* in [CoCivium issue #185](https://github.com/CoCivium/CoCivium/issues/185), without introducing a parallel lifecycle, a new scheduler, any sensors or a giant collection of CoTerms.

## What this actually tests

One tiny envelope can represent five different kinds of candidate CoObjects:

1. software (digital executable);
2. device (physical device, **not** a measurement of X2);
3. session (replaceable logical work identity, **not** a live ChatGPT tab);
4. future branch (counterfactual/hypothesis, **not** present fact);
5. mythic/symbolic object (interpretation, **not** empirical G_d/ET evidence).

Each has a stable scoped identity, **declared and unverified source hash**, independent source/observation/expiry times, privacy, no effect authority, existing lifecycle state, `CoSit` wake relation, typed relations, and optional `CoReverence` significance. Relation metadata can itself have a meta-relation. Meta-relations are finite, acyclic and limited to two nested levels. The reference code is pure and uses only Python's standard library.

## CoSit and stale wake gate

`CoSit` is **not** a new authority-bearing lifecycle state: it refers to one of `QUIESCENT`, `COOL`, `DORMANT`, `COTWILIGHT`, `CLOSE_SAFE`, `ARCHIVE`. An event not bound to the subject stays dormant/held. After the fixture's freshness boundary, a matching wake without revalidation returns `HELD_STALE_REVALIDATION_REQUIRED`. A changed source digest returns `HELD_SOURCE_REVISION_CHANGED_REBIND_REQUIRED`; no unchanged predecessor is silently promoted. Even a structurally matching **synthetic** readback yields only `SHADOW_REVALIDATION_CANDIDATE_EFFECTS_HELD`. **No source proof, task execution, receiver pickup, consent or authority is established by the fixture.**

`CoReverence` may inform preservation and interpretation. It cannot grant permission, truth or ownership. Future/mythic fixtures are explicitly typed so symbolic and prospective branches cannot impersonate observed physical events.

## Run

From this folder:

```sh
python3 -B -m unittest -v test_situation_r0.py
```

Or from repository root:

```sh
python3 -B -m unittest discover -s examples/cosituation -p 'test_situation_r0.py' -v
```

The five fixtures are in `fixtures.json`, not fetched from machines or repositories. The **46 synthetic/adversarial tests** cover ontology/type isolation, provenance/authority denial, relation-of-relation integrity, cycle/depth rejection, negative/uncertain evidence, stale wake/rebind, time ordering, privacy classes, symbolic reverence and zero side effects. No model, network, clipboard, local file scan, event installation, mouse remap or operating-system process runs from the library module.

## Next proof, not completed here

A real, named receiver would need to read an exact source, bind the verified revision and authority, observe a genuine wake event, and independently prove that the right view/action improved a task while preserving stop/revoke and recovery. Another device/host is not simulated to be an independent failure domain by five fixture kinds. This work remains a draft proposal until reviewed and an actual receiver qualifies.

**Invariant rails:**

`EVERYTHING_MAY_EVOLVE_NE_EVERYTHING_MUST_RUN` · `RELATION_OF_RELATION_NE_PROOF` · `SAME_ENVELOPE_NE_SAME_MECHANISM` · `CO_SIT_NE_STALE_TRUTH` · `WAKE_NE_EFFECT` · `REVERENCE_NE_AUTHORITY` · `SYNTHETIC_PASS_NE_X2_RUNTIME` · `FICTION_NE_SCIENCE` · `EVO_NE_TERM_PROLIFERATION` · `POINTER_NE_ACK`.