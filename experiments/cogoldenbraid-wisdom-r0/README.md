# CoGoldenBraid Wisdom R0 | Candidate Lens

**Status:** OFFLINE PUBLIC-SAFE RESEARCH CANDIDATE. Not canon, independent wisdom, an installed CoOrbWare, or an always-running service.

## Purpose

Convert a potentially unbounded stream of "wise words" into a bounded, challengeable source of useful hypotheses. This project does **not** aim to make an endless prompt stream or elevate artificial aphorisms to verified truths.

`QUESTION -> CANDIDATE PRINCIPLE -> CONTEXT -> EXCEPTION -> DISCRIMINATING TEST -> RECEIVER EFFECT -> REVISION / RETIREMENT`

The source-of-truth work spine is the **existing** CoCivium Golden Braid, not a competing control plane:

`INTENT -> SOURCE -> MEANING -> DECISION -> BOUNDED_DEED -> RECEIPT -> RECEIVER -> EFFECT -> LEARNING -> SUCCESSOR`

- `seed.json`: 14 **original candidate** heuristics, with when/exception/test; 8 typed support, tension, guard or dependency links. Wording is new to this fixture. Referenced public architecture sources are context, not empirical proof or quotations.
- `braid.py`: strict schema and authority validation, source identity, conservative lexical routing, explicit abstention/ambiguity, non-executing Golden Braid packets.
- `CoGoldenBraid_Viewer.html`: one-file local browser view with one-at-a-time CoOrb focus, inspectable limits, and optional explicit copy of public capsules. It does not upload input, read clipboards in the background, store visitor information, or launch agents.
- `tests/`: deterministic tests, including authority, provenance, schema and ledger-tamper rejection.
- `fixture.json`: same-author, hand-written test phrases, **not** independent or production-grade routing evaluation.
- `benchmark_evo.jsonl`: pinned 23-event evidence chain (initial browser harness mistake, routing miss, and unrun real-user gates kept visible).

## Local first use

Open `CoGoldenBraid_Viewer.html` in a browser. Choose any candidate. See its exception and what test might disprove or qualify it. A local task search can suggest **at most two** candidate IDs using simple phrase matching. Unknown or ambiguous matches do not grant authority.

## Reproduce with Python 3.11+

```sh
python3 -m unittest discover -s tests -v
python3 verify_evidence.py
python3 braid.py
```

To check that generated seed and viewer match the bundled source, first preserve local changes separately, then run:

```sh
python3 create_seed.py
python3 build_viewer.py
```

A separate local Chromium + Playwright browser injection canary was run (13/13), but local `file://` navigation, native desktop integration and outside-user usability remain **NOT RUN**. The browser canary requires Playwright and Chromium and is not part of the Python-only tests.

## Results and honest limits

- Core tests: 21 PASS. Combined ledger, viewer and core tests: 36 PASS after local verification.
- Browser interaction checks: 13 PASS in injected-content mode, zero outbound network requests observed.
- Hand-authored lexical fixture: **13/14** match expected labels. The "several mirrors all depend on one corporate platform" phrasing is missed: an actual **FAIL**, not evidence that multi-provider recovery is solved.
- Browser test harness initially FAILED because `inner_text()` excluded content inside a collapsed `<details>` element. Corrected to `text_content()`; logged in the evidence chain.
- Downstream usefulness, independent newcomer comprehension, true wisdom quality, operating scheduler delivery, X2 native CoOrb, CoVIA pickup and external publication: **not established by the offline test**.

## Existing sources

The pinned Git blob SHA-1 for each public document is in `seed.json`. The source pointers document the architectural context, **not validation of each saying**:

1. `docs/Architecture/COSPEEDO_EXPONENTIAL_PROOF_AND_RECURRENCE_INTERNALIZATION_R0_20261026.md` - Golden Braid, usefulness and recurrence.
2. `docs/Governance/COREVIEW_SPINE_R0.md` - right-sized challenge, review and authorization.
3. `docs/Architecture/COORBWARE_BEYOND_COSOFTWARE_R0_20261024.md` - projections versus underlying evidence/identity.
4. `docs/Architecture/COAI_EVERGREEN_ONRAMP_COORBWARE_R0_20261026.md` - evergreen != always-running, source-bound onboarding.

## Continuous evolution without endless noise

Reuse the existing **CoEvoAll Pulse** (hourly condition watch) and **CoTidy Evolution Review** (daily) if a qualified operator independently chooses to incorporate this research. This ZIP creates **no new scheduler**, and those existing automations have **not been updated** by it.

A future wave should retrieve one current problem, check against prior work and external donor practices, offer at most a couple of candidates, challenge a false case, test one decision, record receiver impact, and either accept, revise, park or retire the candidate. It should send no public notification absent a real material delta and valid route. A review surface is not receiver adoption.

The quality target is **verified useful improvements per unit of attention**, not wise-word count or token throughput.

GPLv3 intended within the CoCivium core repository, subject to normal repository review. No external model, device, or private account was accessed by the builder.
