# CoMeasure+ R0.1.2: reproduce, challenge, improve

> **Public research draft, not a standard, certification, production service, or CoCivium governing canon.** This page accompanies [draft PR #365](https://github.com/CoCivium/CoCivium/pull/365). Check its current commit, CI, review status and open objections before using or citing results.

CoMeasure+ explores a **typed measurement commons** for people, AIs, agents and other future participants. The central question is not simply *what number appeared?* It is *what was measured, how, for whom, when, under which evidence and authority boundary, and which comparisons are justified?*

The [proposed contract](../../docs/Architecture/COALL_MEASUREMENT_R0_CANDIDATE.md) and [machine-readable R0.1.2 registry](registry_r0_1.json) contain **21 unit/semantic variants** and **7 candidate operational metric families**. They distinguish physical dimensions from quantity kinds and separate observed zero from missing, unknown and redacted values. SI, UCUM and QUDT are methodological donors; this work does **not** redefine those standards.

## Reproduce the current draft

Use a clean, disposable checkout of the exact current PR head, not an old local receipt. Python 3.12 and its standard library are sufficient. Running the verifier creates a local scoped receipt; keep it out of shared source directories if you want an independent replay.

```sh
python ai/measurement/verify_registry_r0_1.py
python -O ai/measurement/verify_registry_r0_1.py
python -m unittest discover -s tests -p 'test_comeasure_optimized_failclosed_r0.py' -v
python -m unittest discover -s tests -p 'test_counits_v6_7_crosswalk.py' -v
python -m unittest discover -s tests -p 'test_copredict_drift_r0.py' -v
python -m unittest discover -s tests -p 'test_observation_domain_r0.py' -v
python -O -m unittest discover -s tests -p 'test_observation_domain_r0.py' -v
```

The [GitHub Actions workflow](../../.github/workflows/comeasure-r0-ci.yml) runs registry and optimized-mode checks, rejects malformed definitions and conflicting receipts, and executes the observation-domain tests in **ordinary and optimized Python**. [CI run #42467581856](https://github.com/CoCivium/CoCivium/actions/runs/42467581856) completed **SUCCESS** for exact code commit `f3f6483c08e15110aa5390686e4ce85c931454d9`. This documents the proof of that code commit; **a subsequent documentation change is a new Git head and must not silently inherit its CI status**. Hosted CI validates only declared synthetic/source-level checks, not physical calibration, authentic observations, independent receiver acceptance or certification.

### Known failure modes and tests to challenge

1. **Interpreter optimization:** historically, correctness-critical Python `assert` statements disappeared under `python -O`; a corrupted centimetre conversion falsely reported `PASS_FOR_SCOPE`. The current draft replaces these checks with always-on failures and regression tests.
2. **Registry integrity:** duplicate unit IDs, wrong dimension vectors (including Hz), zero/negative scales, mismatched metric quantity kinds and invalid temperature offsets must fail closed.
3. **Ambiguous input:** duplicate JSON keys and non-finite JSON constants must not silently become trusted registry values.
4. **Receipt conflicts:** a changed registry must not overwrite a prior matching-status receipt as though the source were unchanged.
5. **Semantic domains:** arithmetic alone is insufficient. [The R0 synthetic observation-domain validator](observation_domain_r0.py) now checks all **seven registered operational metric IDs** against their quantity kind, unit, value state, timestamp/observer/source-hash *format*, uncertainty declaration, and applicable numeric domain. For receiver pickup fractions it requires exact, scoped numerator/denominator counts, positive denominator, an allowed window and an exact fraction match. [Its 29 adversarial/positive unittest methods](../../tests/test_observation_domain_r0.py) run under both Python modes. The output is **`DOMAIN_CONSISTENT_ONLY`**, never a claim of authentic telemetry, verified signature, independent receiver ACK, true user value or a certified SI traceability chain. Physical constraints and metric-specific domain policies beyond the seven listed profiles remain open.
6. **Evidence quality:** an event heartbeat is not a successful task, one machine is not independent redundancy, local PASS is not receiver ACK, and a named model does not constitute an authenticated evaluator.

Please retain negative, inconclusive and adversarial results. A repaired self-check should not erase the proof that the old check failed.

## Proposed contribution contract

Contribute a **single bounded and reversible** improvement: exact source version, a small failing counterexample or new use case, proposed invariant, automated test, reproducible outcome, rights/license provenance, and explicit limits. Prefer improvements that work under both ordinary and optimized execution and can be replayed by an independent operator. Keep historical metric versions frozen; a new definition starts a new series or a documented bridge.

Useful unsolved areas include **authenticating** observations, independent receiver readproof, uncertainty propagation and calibration, timing/skew and method provenance, additional domain policies beyond R0's seven profiles, SI/UCUM/QUDT interoperability, accessible first-use examples, and cross-model or cross-substrate transfer. The [repository contribution guide](../../CONTRIBUTING.md) describes general expectations.

**Consent and governance:** Reading public source is not an invitation to run probes against private infrastructure, discover or message unrelated agents, collect personal data or vote as an unverified model identity. CoTheoryAll, G_d and CoPriMath may supply challengeable research hypotheses, not mandatory scientific beliefs or scoring authority.

**Status ladder:** publicly readable **draft-branch source** → exact-head synthetic/source checks pass for their declared scope → independent external review/challenge → receiver-produced real-world outcome and acceptance → reviewed default-branch or product release. The last three stages are **not established** by this guide. Public GitHub accessibility is not mainline merge, an official measurement standard, CoEx, broad session pickup, or product deployment. External readers are free to disagree, fork, retest and report CoCivium losses.
