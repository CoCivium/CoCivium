# CoLocal+ | CoSeed and CoPath discovery index R0

**Entry:** [CoRelGRAILS+ CoSeed / CoPath R0](CoLocal2601109_CoRelGRAILS_CoSeed_R0.md)

This is a public **discovery registry**, not CoAll canon, a deployed cross-front event bus, or evidence of automated consumption. Use immutable commit references and exact-content receiver readproof for promotion.

## Discoverable Seed
| Seed ID | Source | Public landing | Candidate fronts | State |
|---|---|---|---|---|
| CoLocal2601109_CoRelGRAILS_R0 | CoLocal2601109, 2026-11-09 | [CoSeed / CoPath](CoLocal2601109_CoRelGRAILS_CoSeed_R0.md) | CoInEx+, CoMap+, CoTime+, CoEv+, CoTurtle+, CoAura+, CoTele+, CoStead+, CoG_dSide+, CoOrb+ | LANDED_PUBLIC_SOURCE; CONSUMER_PICKUP_UNVERIFIED |

## Consumer CoPath
1. Read the Seed and pinned commit; check SHA and provenance of any retrieved object.
2. Evaluate relevance, rights, authority, and scope. Treat speculative relation claims as hypotheses.
3. Create a consumer-owned receipt naming exact source object, reader, timestamp, transformation, and disposition.
4. Link the receipt from the consumer's own index. No automatic promotion to canon or runtime.
5. If integrated, publish tests, functional evidence, rollback and supersession pointer.

## CoSeed contract
Identity, time, source, boundary, relation type, epistemic state, evidence, authority, lineage, lifecycle, inverse candidates, tests, recovery pointer, supersession.

## ExState
- **Verified:** CoRelGRAILS public source was written and fetched by the authoring session.
- **Unverified:** independent downstream pickup, continuous cross-session synchronization, CoFarm/CoStead custody, CoAll canon, public website UI deployment.
- **Not exhaustive:** this index registers only this CoLocal Seed; it does not assert coverage of all historical sessions, fronts, or assets.

## Nonclaims
LOCAL_IS_NOT_LANDED; VALIDATION_IS_NOT_ACCEPTANCE; NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF; NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE; HASHING_IS_NOT_SEMANTIC_INGESTION; DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY.


## CoCurrentnessGate R0 | Public reusable test harness

**[Read the fail-closed evaluator](../../scripts/CoCurrentnessGateR0.py)** · **[Inspect 15 synthetic regression tests](../../scripts/test_CoCurrentnessGateR0.py)** · **[CI workflow](../../.github/workflows/colocal-currentness-r0.yml)**.

This portable, read-only evaluation kernel checks reported heartbeat freshness, separately observed process identity/hash, and progress between two qualified samples. It is available to authorized CoMap/CoSpeedo/CoLocal/CoStead front consumers as a **candidate CoSeed/CoPath**, not automatically adopted runtime policy.

Run `python -m unittest discover -s scripts -p 'test_CoCurrentnessGateR0.py' -v` from the repo root. The authoring environment passed **15/15 isolated synthetic tests**, and the [GitHub Actions source regression passed 15/15](https://github.com/CoCivium/CoCivium/actions/runs/43128120567). The [machine-readable, source-bound CI receipt](../../ai/currentness/colocal-cospeedo-currentness-ci-r0-20261112.json) records the exact run, source commit, Git blobs, artifact digest, evidence class and remaining gates. This CI execution is within GitHub's own failure domain; independent receiver adoption and X2 repair remain unverified. Inputs must be supplied by an actual trusted process observer for operational use; fixture results cannot establish X2 or other device health.

Known historical counterexample: a CoSpeedo morning brief accepted a source status from November 8 as live on November 11, despite the reported receiver PID being absent. The live X2 source and private machine data are not published here. The source-side gate rejects that class of evidence, but has **not been wired into X2's producer or daily schedule**.

**ExState:** PUBLIC_TEST_SOURCE_LANDED; X2_ACTIVATION_UNVERIFIED; EXTERNAL_RECEIVER_PICKUP_UNVERIFIED. No CoAll canon, public runtime, receiver ACK, independent-host durability, or consent/authority promotion inferred.
