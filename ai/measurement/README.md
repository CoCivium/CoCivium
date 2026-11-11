# CoMeasure+ R0.1.2: reproduce, challenge, improve

> **Public research draft, not a standard, certification, production service, or CoCivium governing canon.** This page accompanies [draft PR #365](https://github.com/CoCivium/CoCivium/pull/365). Check its current commit, CI, review status and open objections before using or citing results.

CoMeasure+ explores a **typed measurement commons** for people, AIs, agents and other future participants. The central question is not simply *what number appeared?* It is *what was measured, how, for whom, when, under which evidence and authority boundary, and which comparisons are justified?*

The [proposed contract](../../docs/Architecture/COALL_MEASUREMENT_R0_CANDIDATE.md) and [machine-readable R0.1.2 registry](registry_r0_1.json) contain **21 unit/semantic variants** and **7 candidate operational metric families**. They distinguish physical dimensions from quantity kinds and separate observed zero from missing, unknown and redacted values. SI, UCUM and QUDT are methodological donors; this work does **not** redefine those standards.

## Honest UX placeholders: CoIb / CoEther / CoAsym (R0 candidate)

The user correctly challenged the original “0 placeholders” slogan. The defensible rule is **zero misleading placeholders**. An empty slot can preserve a legitimate future measurement without pretending it has already been observed.

[ux_placeholder_r0.py](ux_placeholder_r0.py) supplies **three declared, nonnumeric candidate slots**, with [fail-closed tests](../../tests/test_ux_placeholder_r0.py). They do not add a new live status monitor, operating metric or registry. Render them only if a future separately authorized UI chooses a slot; never place invented numbers between CPU and available memory.

- **CoIb**: unmeasured *inter-component handoff/readback*. Display **Awaiting independent evidence** until the same WorkID, exact source and genuine receiver-origin readproof exist. It **references** the already defined `CoMx.receiver_pickup_fraction` but does not claim a measured fraction.
- **CoEther (open parent)**: a deliberately **unresolved relational interstice**, reserving room for gaps between physical observations, virtual representations/simulations, human interpretations, mythos, observer limitations and G_dSide philosophical/theological questions. Display **Open questions; no empirical bridge established**. It has no number, unit, asserted common mechanism or automatically established metric. It is not an assertion that a physical ether, supernatural signal, divine intent, extraterrestrial source, consciousness or hidden causal bridge exists.
- **CoEther.Transport (optional child)**: the *separate measurable transport-quality* research path. Display **Not yet measured** until sourced timing, latency/loss windows, instrumentation and an independent receiver readproof qualify. This child may reference existing `CoTime.source_age`, but it cannot define or replace all of CoEther. A fresh local screenshot or “Signal Clean” is not proof of transport health.
- **CoAsym**: conceptual research label for alternatives and asymmetric relations. Display **Research concept; no numeric metric**. It needs a falsifiable observation protocol before becoming any quantity.

### Open CoEther merger relations: preserve differences until proved otherwise

CoEther is an **epistemic and design placeholder**, not a proposed new substance or scientific unit. The typed *facets* currently reserved for independent inquiry are `PHYSICAL_OBSERVATION`, `VIRTUAL_REPRESENTATION`, `MYTHOS_NARRATIVE`, `PHILOSOPHICAL_G_D_INQUIRY`, and `UNKNOWN_OBSERVER_GAP`. These are *questions or ways of describing things*, not equivalent ontologies, and no finite taxonomy can preclude future better facets.

Possible **candidate** edges include `MODELS`, `REPRESENTS`, `ANALOGY_TO`, `INTERPRETED_AS`, `CONTRADICTS`, `FAILS_TO_EXPLAIN`, `MERGER_HYPOTHESIS` and (only when independently justified) `SAME_REFERENT`. A candidate relation never authorizes an identity collapse, automatic cross-domain inference, new sensor reading or public claim. Where empirical hypotheses are proposed, require operational definitions, source/provenance, alternatives, a falsifier or discriminating prediction, and an independent evaluation. For **mythos and G_dSide**, preserve philosophical, narrative and theological inquiry as such without treating it as experimental evidence or asserting that G_d directed any event. The absence of a measurable test is not a zero observation.

Better merger proposals may **supersede a particular interpretation**, but retain the original claim, scope and dissent; promote only the proven relation, never the entire open umbrella. If a future accepted term names the gap more precisely than CoEther, maintain a provenance-aware alias/crosswalk rather than silently renaming old receipts. Distinguish `CoEther` (open research) from `CoEther.Transport` (technical unmeasured child); do not add live CoBar readings from either.

Placeholders have null value/unit/observation time, no evidence receipts, no authority, and false `receiver_ack`/`measurement_verified` flags. Distinct states are `UNKNOWN`, `AWAITING_EVIDENCE` (requires specific wake condition), `NOT_APPLICABLE` (requires explanation), and `RESEARCH_CONCEPT` (CoAsym only, requires limitation). Both code and tests reject fake numeric zero, forged ACK, fake Clean status, timestamp, extra telemetry, bogus metric linkage and removed nonclaims.

The **Meta AI brainstorm is inspiration, not a source of telemetry, an action directive, evidence of a completed script, or permission to publish a screenshot**. Treat the suggested FixWorld/YouTube actions and “0 min old = sync” claims as unverified proposals. Do not run them from this source note.

**Qualification:** synthetic source/CI only; no X2 native installation, receiver ACK, SI standard, product acceptance, CoEx or deployment. Next, an independent actual receiver-origin measurement and human-tested, calm single-bar status. Any changes to live CoSpeedo require separate authority and receipts.

## First-use synthetic CoSpeedo example

Run `python ai/measurement/first_use_demo_r0.py` from the repository root to see eight explicit examples of typed measurement admissibility. The [public first-use script](first_use_demo_r0.py) uses only the elected R0.1.2 registry and observation-domain validator, does not access live devices, and writes no data files. It illustrates a synthetic 3-of-4 pickup fraction, two fictitious human interventions and a synthetic useful-delta rate, along with deliberately rejected claims: a fraction above one, zero denominator, wrong time window, fractional human intervention and unknown-as-zero.

Expected: **8 of 8 declared outcomes matched** (`passed=8`, `total=8`), with rejected inputs correctly held and accepted inputs labeled `DOMAIN_CONSISTENT_ONLY`. Reproduce with both ordinary and optimized Python:

```sh
python ai/measurement/first_use_demo_r0.py
python -O ai/measurement/first_use_demo_r0.py
```

These are **test fixtures, not actual CoMx acknowledgments, real CoSpeedo values, measured performance, user benefit, or live CoOrb telemetry**. A 3-of-4 *synthetic* fraction is not a report that any three receivers accepted work. The deliberately repeated `a` source hash proves only that the code checks hash **syntax**, not source authenticity. Independent receiver-origin pickup/readback and meaningful user outcome remain separate open acceptance gates. The existing [CoMeasure CI workflow](../../.github/workflows/comeasure-r0-ci.yml) now invokes this example in both interpreter modes; check the *current exact head* CI conclusion before citing a run as PASS.

## CoMVP+ / CoLockStep+ source-pinned survival canary

The [CoLockStep R0 survival harness](colockstep_survival_r0.py) is a deliberately bounded test of a **previously reproducible source baseline** against one broken experimental successor. The baseline is not yet a qualified MVP or stable release: it has no independent real-user or receiver acceptance. See the existing [public CoMVP+/CoLockStep architecture delta](https://github.com/CoCivium/CoCivium/issues/24#issuecomment-6738181525).

The harness pins the prior source identities of the R0.1.2 registry, verifier, observation-domain checker and eight-case first-use example. It copies them to disposable isolated directories, corrupts only the **experimental** centimetre conversion (`1/100` to `1/10`), then exercises the baseline before and after. Both normal and optimized Python must preserve baseline source hashes, matching synthetic checks and no-clobber receipt. A seemingly successful successor first-use demo does **not** qualify the successor: its independent registry verifier must reject the bad conversion without producing a success receipt. The original source tree is neither edited nor used as a writable test directory.

```sh
python -B ai/measurement/colockstep_survival_r0.py
python -O -B ai/measurement/colockstep_survival_r0.py
```

The output is a **synthetic within-one-failure-domain process-isolation receipt**, not live rollback, supervisor restart, a working user product, independent receiver ACK, public release, CoEx or CoAll-wide synchronized evolution. The existing [CoMeasure CI workflow](../../.github/workflows/comeasure-r0-ci.yml) invokes both commands. Inspect the exact HEAD run before calling this canary green. The next acceptance gate requires an independent receiver-origin useful task and tested process failure/recovery in its actual intended environment.

## Browser-level CoLockStep R1 canary (separate from source-level R0)

The [browser survival test](../../tests/test_colockstep_browser_r0.py) reuses the existing **public CoDemoWow Truth Gate R1** at [its source file](../../examples/codemow/truth-gate-r1.html), Git blob `2d3a1248e63b409436b6def098755f93065ebebb`, without modifying it. It opens the original offline HTML in one headless Chromium process and exercises the reader's **Run truth gate**, **Test unsupported X2 claim**, and **Restore proven scope** controls. A second isolated Chromium process opens a deliberately broken experimental copy that throws during initialization. The canary requires the broken copy to fail to complete the task, interrupts only that second browser, then checks the original still rejects an unsupported claim and restores its 5/5 scoped evidence view, with no JavaScript errors or page-origin network requests.

This protects the existing demo **as an exercised browser UI** during a controlled synthetic successor failure. It does **not** implement automatic traffic switching, recover a crashed baseline, operate on X2, or demonstrate an independent human receiver. GitHub Actions installs Playwright/Chromium in a separate job; a browser setup failure must not be mistaken for a CoMeasure source-verifier failure. Only the CI result for the exact current commit can establish that this new browser test passed.

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
