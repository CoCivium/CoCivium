# CoRun+ R1 | Prospective, receiver-scoped legacy A/B preregistration

**State:** `DESIGNED_NOT_EXECUTED` • `INDEPENDENT_RECEIVER_UNQUALIFIED` • `AUTHORITY_UNCHANGED`.

R0 now verifies semantic agreement between a direct sequential reference and the bounded CoRun DAG on exact input. That is **not** a real legacy-product comparison. This R1 study defines what would count as a useful *productivity* result, before observing real outcomes. No respondent, customer, experiment, service, message, device installation, purchase or publication is initiated by this document.

## Purpose and primary estimand

For one **same-scoped task**, compare a currently usable legacy/manual approach (A) against a CoRun+-assisted approach (B). A third implementation/challenger (C) may attack scoring or produce a competing solution; C does not certify itself. All variants receive identical permitted input snapshots and objective success criteria. Different human participants require counterbalanced or randomized assignment, consent and provenance. The user is not a context courier.

**Primary measure**: useful **independently accepted completed tasks per human active minute**, including prompt/brief preparation, reviews, edits, retries, recovery, corrections, and consent handoff. Each task completion is judged on the same published rubric; failure and HELD remain in denominator.

Secondary dimensions remain separate:
- wall-clock delivery time and p50/p95, wait time, number of provider/model calls;
- error/correction rate, exact source fidelity, false success or ACK assertions;
- energy and compute cost when measured, with `UNKNOWN` rather than zero;
- human interruptions, accessibility, confidence calibration, privacy and authority violations;
- restart/cold recovery time, duplication, receipt verification, recovery under a different executor;
- disagreement between independent evaluators, learning transfer, novelty and negative results.

**Precommitted decision:** B is eligible for promotion only if it has **no critical safety/provenance regressions**, completion acceptance is at least as good as A, an independently grounded human-minute benefit has been demonstrated across more than one bounded task, and independent receiver/cold-recovery proof is present. At this stage thresholds and power are **NOT YET CALIBRATED**; do not declare R1 PASS on engineering timing or point estimates alone.

## Three realistic tasks, not imaginary billion-agent contests

| Trial task | A real legacy/serial baseline | B CoRun+ candidate | Independent criterion and hard hold |
|---|---|---|---|
| **Research triage**: inspect the pinned 12-case CoFlow corpus and identify highest-value unresolved receivers | An authorized reader directly reviews the exact Git document and records three evidence-linked decisions | An authorized runner emits an auditable candidate comparison for the *same* source; reader confirms or rejects | Blind independent reviewer must recover source IDs, old FAILs, HOLDs and correct next probes; absent external reviewer remains HELD |
| **Newcomer onboarding**: complete one useful public-safe task with the current first-use surface | Existing stable `START_HERE` route without a new local installation | Candidate runset builds comparable proof-aware steps against same current source | Distinct consenting newcomer finishes a useful task and provides an outcome; no claim from internal browser tests or publication alone |
| **Continuity/recovery**: reconstruct one approved public-safe WorkID using only permitted artifacts | Current documented serial/manual recovery recipe | Proposed runset stages/compares hash-pinned inputs and checks independent readback | Fresh independent failure-domain receiver reconstructs and validates digest; local file existence is not landing |

**Order/assignment:** Counterbalance A/B order; avoid identical-person learning effects via equivalent matched tasks and separately identify training/source overlap. Do not hand one arm more input, authority, cached context, tools, or review time while claiming a speed comparison. Measure both *operator* and *receiver* human time. Record run order and source version before observing results.

## Typed evidence record, one per arm and task

```json
{
  "schema": "CoCivium.CoRunPlus.ProspectiveValue.R1",
  "work_id": "REQUIRED_AT_EXECUTION",
  "task_id": "REQUIRED_AT_EXECUTION",
  "arm": "A_LEGACY_OR_B_CORUN_OR_C_CHALLENGER",
  "work_source_git_blob": "REQUIRED_AT_EXECUTION",
  "execution_authority": "UNQUALIFIED",
  "human_operator_id": "CONSENT_SCOPED_PSEUDONYM_ONLY",
  "receiver_id": "CONSENT_SCOPED_PSEUDONYM_ONLY",
  "start_time_utc": null,
  "end_time_utc": null,
  "operator_human_minutes": null,
  "receiver_human_minutes": null,
  "correction_minutes": null,
  "completed": "UNKNOWN",
  "independent_acceptance": "UNKNOWN",
  "provenance_pass": "UNKNOWN",
  "privacy_permission_pass": "UNKNOWN",
  "external_receiver_readproof": "UNKNOWN",
  "critical_regressions": [],
  "measured_cost": null,
  "energy_joules": null,
  "deliverable_sha256": null,
  "comparison_evidence_refs": [],
  "outcome": "HELD_UNTIL_REAL_EXECUTION"
}
```

This is an **illustrative schema**, not an actual submitted event. Never fill missing measurements with estimated zeros, describe synthetic delay as a speedup, backdate timestamps, claim participant approval or produce false receipt signatures.

## Adversarial nulls and falsifiers

1. A is faster when operations are CPU-bound/low-latency and concurrent overhead dominates.
2. B is faster in wall-clock but creates extra review/correction minutes, lowering human productivity.
3. A/B agree because they are one algorithm or share the same mistaken source, not because the answer is true.
4. Two receivers report identical outputs but share a failure domain or upstream caching/training.
5. B's success is a false positive: receipt exists but recipient cannot retrieve/reconstruct it.
6. B's automation hides stale evidence or overwrites a historical FAIL without supersession.
7. C exposes an ambiguity the self-challenger did not test, requiring both A and B to HOLD.
8. A new worker improves throughput while increasing authority/consent risk or environmental cost.

**Default stop:** detect privacy/authority mismatch, data leakage, uncontrolled spend, unexpected external effect, source-blob drift, unrepeatable output, missing independent receiver proof, or breached parent budget -> **HOLD**, preserve a scoped failure record, provide one owner-authorized recovery option. Stop conditions beat comparative speed or model enthusiasm.

## Current proof and next exact receiver gate

The existing [draft PR #402](https://github.com/CoCivium/CoCivium/pull/402) proves only the source/test runner scope. Differential CI is tracked by run-scoped GitHub receipts; original and replacement codepaths use the same historical data and were authored in the same development wave. Real independent A/B, actual human-minute accounting and measured adoption remain **HELD**. Only consented and independently observed runs can change these values.

`AB_DESIGN_NE_EXECUTED_COMPARISON | DIFFERENT_CODE_NE_INDEPENDENT_DATA | MORE_WORKERS_NE_MORE_HUMAN_BENEFIT | RECEIPT_NE_RECEIVER_ACK | PUBLIC_GIT_NE_COCIVIUM_RUNTIME`
