# CoStageReview+ / CoReviewPanel+ R0 | Every lifecycle transition should be challengeable

**2026-10-24 | PUBLIC_SAFE_BOUNDED_REVIEW_POLICY | NOT_RUNTIME_ENFORCEMENT | NOT_FIREWORKS_READY**

**CoHereNow:** CoCivium already has a seven-seat **design** in [CoRoleSpace R0](../Architecture/COROLE_SPACE_PREVIEW_R0.md), a bounded [CoTurtle+ review grammar](COEXPERIMENT_SPACE_TURTLES_R0.md), the [research-evidence validator](../../scripts/validate_coresearch_evidence_r0.py), an [existing 14-gate CoSpiff+ survivability scorecard](../../ai/resilience/cospiff-fireworks-r1.json) and a [failure-safe launch analysis](../Strategy/COSPIFF_FIREWORKS_SURVIVABILITY_R1.md). The purpose of R0 is to **bind these existing donors into one *read-only review-coverage* adapter**, not create a new government, backend or notification system.

## Nine covered stages and where evidence is needed

| Stage | Necessary evidence | Candidate seats (never auto-appointed) |
| --- | --- | --- |
| Discovery | Source, duplicates, prior work, competing alternatives, scoped absence | Provenance check |
| Hypothesis | Falsifiable prediction, explicit assumptions, counterexamples, prior art | Proposal, challenge |
| Design | Consent, authority, security/privacy, accessibility, reversibility | Formal check, perspective, challenge |
| Build | Exact revision, software rights, dependencies, reproducible test/build | Formal check, provenance check |
| Experiment | Pinned baseline, negative controls, latency/cost, faults, reproducible outcome | Empirical check, challenge |
| Release | Independent human task, rights, safe public destination, challenge and rollback | Empirical, challenge, provenance, synthesis |
| Operation | Currentness, receiver-origin acknowledgment, incident/revocation capability | Empirical, formal |
| Recovery | Independent failure domain, different steward, complete cold restore | Empirical, provenance, challenge |
| ReEvo | Historical replay, comparison, preserved dissent and regressions | Challenge, provenance, synthesis |

**The common requirements at every stage are a bounded prior-work check and preserved negative results.** An explicit `NOT_TESTED` or `HELD` is valid; only actual evidence can satisfy a promotion gate. A failed stage does not stop independent safe work on unrelated lanes.

## Seven seats are not seven independent people

Reuse CoRoleSpace's Proposal, Formal Check, Empirical Check, Challenge, Perspective, Provenance Check, and Synthesis positions. A seat may be unassigned, run sequentially, or be implemented as a read-only local audit. No seat assignment or reviewer consent occurs by listing it. Neither multiple agent prompts nor distinct provider labels establish independent sources if they reuse one model family, artifact, owner or infrastructure. Real high-stakes adjudication requires identifiable authorized humans, explicit authority, conflict disclosures and a separately validated decision.

CoTurtles+ review depth is capped at **two** with **two rounds** and an **aggregate inherited budget**. A child cannot mint money, permissions, credentials or a fresh recursive budget. A million logical session descriptions remain dormant descriptions until a concrete bounded task and execution grant exist.

The public [policy](../../ai/review/stage-review-policy-r0.json) specifies the exact existing G01-G14 dependencies and the nine stage slots. [Code](../../scripts/CoStageReviewGateR0.py) checks the policy and Git blob SHA-1 of four pinned public donors against exact checked-out file bytes, then emits per-stage `HELD_...` rather than inventing approvals. Git's object hash is an exact *source identity* check, **not** a cryptographic signature, source truth, external pickup or durable custody guarantee.

## How the bounded canary runs

From a repository checkout with Python 3.9+ standard library:

```sh
python3 -m unittest discover -s tests -p 'test_stage_review_gate_r0.py' -v
python3 scripts/CoStageReviewGateR0.py --repo-root .
```

The optional `--report FILE` writes a JSON report using exclusive create and checks local byte readback; do **not** point it at an existing path. The program has no network calls, no provider login, no hardware or device control, no panel assignment, and no external send. All scorecard statuses remain as published, including observed failures, partials, required reviews, and unverified receivers. A changed donor source fails closed until an explicit new policy version pins the revised bytes.

The local unit harness tests **40 positive/negative policy conditions** on **synthetic** scorecards and source-binding fixtures. It rejects missing stages, missing prior work, dropped failures, invalid seat identity, depth/budget/authority escalation, spoofed reviewer independence, duplicate gate identities and attempted promotion after self-reported all-green gates. This is a *validator behavior test*, not evidence that the 40 relevant real-world actions took place or that actual reviewers were involved.

[Machine-readable local benchmark record](../../ai/review/benchmark_evo_r0.jsonl) records the 40/40 isolated test result, the public-review coverage hold and the separate receiver-adoption hold. It is not silently appended to an incompatible global JSONL schema.

## Why the fireworks gate remains HELD

Current [CoSpiff+ R1](../../ai/resilience/cospiff-fireworks-r1.json) still reports no externally accepted first task, no verified off-GitHub cold restore by a second steward, and unresolved public-domain/privacy/licensing issues. The separate [CoFireworks R0](../Launch/COFIREWORKS_READINESS_R0_20261024.json) agrees on the distinction between source availability and public value. R0's stage assessment is a review **plan** and a guard against greenwashing, not a production controller installed on all systems.

A credible *first flame* is **one unrelated consenting reviewer** completing one useful task, finding the provenance and optionally submitting a failure. A credible *resilience spark* is **one independently restored public-only capsule** by someone other than the originating operator, while GitHub and X2 are unavailable. Public fireworks additionally need repeatable usability, security/rights, active feedback, accessible delivery, durable correction paths and genuinely separate failure domains.

## Remaining layers and higher bars

- **CoReviewPanel+ / CoPrior+**: decision provenance, licensing/prior art, real reviewer identity, counterevidence, disagreement, independent-source audit.
- **CoTurtle+ / CoStretch+**: bounded test selection by information gain, cost, energy, risk, privacy, and recovery debt; cheap local deterministic checks before expensive provider experiments.
- **CoOrbWare+ / CoSpiff+**: one quiet first-use task and a source-linked tree of which claims are observed, inferred, hypothetical, contradicted, absent in bounded scope, or held for review; not a wall of jargon.
- **CoProvider+**: comparative pinned task harness for local Ollama/Llama, Pi, Claude and others, with current credentials/capabilities measured separately; do not inherit success from an old benchmark.
- **CoRecovery+**: real revoke/stop control, no-clobber checkpoint, second-maintainer restoration, actual external readproof; no claim of offsite durability merely from GitHub cloning.
- **CoReach+**: distinguish indexed pages, page load, first action, user benefit, correction, voluntary repeat engagement and outside contribution; no covert tracking or self-inflated bot metrics.

Prior numeric thresholds (video size >300 KiB, thumbnail decodes and human review, `ffprobe`, zero `blackdetect` segments, GitHub 200 <2 s, Gmail Primary query <60 s, identity logged, Pi compatibility <2 s, Claude credential presence check <1 s, local Ollama packet <3 s) remain **per-run probes**, not evergreen global PASS. None was rerun as part of this R0 review-policy test. Gmail query does not prove delivery; credential presence is not authorization; parsed Ollama inventory is not inference quality.

## Publication and effect boundaries

Public GitHub documents are source-controlled **projections** only. GitHub Actions CI (if installed and actually successful) is a *same-provider* test, not a human reviewer, CoStead landing, CoMx pickup, CoEx, canon, or universal session synchronization. Broadcast needs a known, permitted recipient and an exact-object receipt; no mass Gmail or recursive social fanout is authorized by a slogan or mouse graphic. A middle/thumb action remains a visible, reversible proposal until mapped and inspected by the device owner.

**Rails:** `PANEL_SEAT_NE_REVIEWER | REVIEWER_COUNT_NE_INDEPENDENCE | PRIOR_NE_PROOF | BENCHMARK_NE_ADOPTION | SOURCE_NE_RECEIVER_ACK | FIREWORKS_NE_RELEASE_AUTHORITY | MANY_SESSIONS_NE_MANY_WORKERS | LOCAL_IS_NOT_LANDED | VALIDATION_IS_NOT_ACCEPTANCE | DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY`

FOSS Forever | CoGoAll | Working Together Respectfully | privacy-by-design | inclusive, voluntary participation | visible activity, optional wearables | pay forward and sideways.
