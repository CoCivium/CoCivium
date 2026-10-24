# CoDoodleNexus+ / CoZombie R0 | Shadow experiment compiler

**2026-10-24 | Offline, standard-library Python. No live AI experiments or provider calls.**

This bounded prototype addresses a practical question: can large, repetitive, richly relational CoDoodles seed *finite, adversarially challengeable* work without spawning uncontrolled agents? Yes, at the level of logical descriptions and read-only triage. It has not proved that those experiments improve work, that the device UI is integrated, or that resources are unlimited.

## The source-backed prior

Existing CoCivium work has a [CoLens living-media twin](https://github.com/CoCivium/CoCivium/tree/main/examples/colensmedia), [CoStageReview R0](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COREVIEW_PANEL_LIFECYCLE_R0.md), [CoResourceAttractor R0](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/CORESOURCE_ATTRACTOR_R0.md), and the [CoMousePalette R0 research PR](https://github.com/CoCivium/CoCivium/pull/231). These are donor sources, **not** proof of universal runtime integration.

The original text of the Synthkind declaration has not been authenticated here. Planck and quantum references are genuine scientific terms but this artifact does not investigate new physics. G_d, spirit, aura and imagined non-human civilizations are optional ethical, fictional or hypothetical lenses, never evidence of physical contact, rights, or mechanism.

## Use without providers

Requires Python 3.10+ for the core. No packages to install:

```sh
python3 -m unittest discover -s tests -v
python3 nexus.py --seed 17 --sample 512 --select 12
python3 cozombie_audit.py
python3 verify_evidence.py
```

Open `CoDoodleNexus_Viewer.html` in a browser. The browser viewer is independent of Python once generated. It performs no clipboard or network operations. One isolated Chromium browser test passed through injected HTML; direct `file://` navigation was blocked in the test environment.

To compile a personally written note, provide it deliberately as a local UTF-8 text file:

```sh
python3 nexus.py --input ./my-private-note.txt --out ./private_output/shadow.json
```

**Do not publish** the private output. The compiler stores only recognized generic tags and the input SHA-256, never full input text, but a digest may be linkable to a guessable input. It reads no keystrokes or clipboard, and follows no links.

## CoDoodle -> bounded experiment candidate

- `CoIn`: incoming task or explicit user input, not universal surveillance.
- `CoBetween`: ambiguity, gaps and relations that deserve inspection.
- `CoInv`: inverse, counterexample, alternative and negative evidence.
- `CoOut`: proposed output, always with scope and provenance.
- `CoProof`: independent test, preserved FAIL, review and recovery boundary.

The versioned, ordered fifteen-dimensional index has **1,411,465,305,600 logical combinations**. With seed 17 it samples 512 configurations and selects 12 *descriptions*, not deployed agents. Changing option names or order changes the manifest digest, so historical index numbers must not be silently reused after such a change. The compiler explicitly rejects stale namespaces and edited candidates.

The candidate ranking uses arbitrary **synthetic scores**, not experimental utility. The calibrated fixture wins 20/20 trial seeds; inverted scoring loses 20/20. Promotion is therefore **HOLD**.

## CoZombie triage

`cozombie_audit.py` accepts five fictional status snapshots by default. It distinguishes recent activity, stale heartbeat with unknown owner, separately observed dead owner and expired lease, revoked permission, and provider rate limits. No owner is contacted, no process examined, no lease reclaimed, no device scanned, and nothing is restarted. A future supervisor needs fresh authority and exact checkpoint readproof before any effect.

## Source review, test harness and humans

Follow the existing CoStageReview lifecycle: Discovery -> Hypothesis -> Design -> Build -> Experiment -> Release -> Operation -> Recovery -> ReEvo. At each transition do a cheap prior-art/provenance check and preserve negative evidence; the effort of an external review panel scales with consequence and independence. Reviewer *seats* do not imply seven real people or seven independent models.

**Human-time urgency:** The design should favor quick visible liveness and useful next steps rather than silent infinite loops. Suggested future targets: first local response within seconds, clear stalled/held status on inspection, bounded retries, cancelable experiments, and explicit wall-clock budgets. Targets are not validated guarantees.

## Evidence

- 45/45 Python tests passed (after one corrected test-harness assumption).
- 12 Chromium injected-page checks passed for desktop/mobile; zero observed external HTTP requests or JS exceptions. Standalone local-file navigation was environment-blocked.
- 30-entry pinned `output/benchmark_evo.jsonl` retains 18 PASS, 4 FAIL, 3 HOLD and 5 NOT_RUN events. Use `verify_evidence.py` to inspect integrity, **not** as a cryptographic signature.
- In this isolated environment, compiling 256 descriptions took median **3.022 ms** across seven repetitions. That is not submicrosecond per-candidate execution; neither real model inference nor energy was measured.
- No X2 remote connection, mouse mapping, actual Perixx keyboard event capture, physical touch, provider work, public broadcasting, receiver pickup, or independent user outcome.

## A practical CoCivium-scale next step

1. Independently run one cold-source workload on X2 or Mac, with exact source identity and a provable stop action.
2. Prove a different machine can reconstruct the work from durable custody without contacting an original provider session.
3. Evaluate a stranger's first task against a competent plain-interface baseline, not an artificial firehose.
4. Add opt-in source-aware CoOrb/CoMap projections only if they shorten human time and don't hide uncertainty.
5. Keep the optional MX4 thumb button mapped separately via the user's Logitech application. Do not replace an existing macro or OS middle-click without a physical accept/revert test.

**Resilience means many independent recovery paths, not an unkillable central process.** Size itself is a liability if it masks shared credentials, failure domains and single-person operational burden.

`POSSIBILITY_NE_EXECUTION | PAUSE_NE_INTENT | KILL_CANDIDATE_NE_PERMISSION | POINTER_NE_ACK | SPEED_NE_HUMAN_VALUE`
