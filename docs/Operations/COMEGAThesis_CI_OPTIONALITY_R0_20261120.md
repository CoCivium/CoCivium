# CoMegaThesis CI+ | Operational optionality and release gates R0

**State:** `CANDIDATE_PROOF_CONTRACT__CI_RUN_NOT_VERIFIED__NOT_RUNTIME__NOT_CANON`.  
**Work surface:** [Draft PR #500](https://github.com/CoCivium/CoCivium/pull/500).  
**Purpose:** Turn a selected CoTheoryAll relational narrative into a repeatable, cheap and fail-closed operating loop while keeping speculative ideas, source proofs, browser checks, independent human acceptance, real device runtime and publication separate.

## Current source-to-effect ladder

`CANDIDATE → SOURCE_CHECK → BROWSER_SMOKE(optional) → INDEPENDENT_COMPREHENSION → AUTHORITY_REVIEW → ALLOWED_MERGE → RECEIVER_READBACK → OPTIONAL_DEPLOY → LIVE_RECOVERY`.

Each arrow is an evidence-backed **transition**, never inferred from the presence of a later-looking file.

### Required source CI (fast / no provider lock-in)

- Trigger on changes to the selected thesis, graph, reader, tests and CI workflow in draft PR or the elected candidate branch. Also allow manually invoked source CI when the runner is actually available.
- Use Node 22 built-ins, no npm install, no network dependency in test logic.
- Validate: exact shared WorkID and hypothesis source across 3 projections, retained epistemic class and H0 alternative, no executable HTML script, graph referential integrity, source/gate fields, CoShroud/ET/non-coercion rails, and negative mutations (duplicate node, missing endpoint, missing gate, missing source).
- Emit log, commit reference, SHA256 manifest and nonclaims as one immutable workflow-run artifact. A source CI PASS says **only** that source tests passed on the identified commit.
- Single CI concurrency lane per PR/branch; superseded runs may be canceled, but every release decision must reference the exact successful commit. `CI_GREEN_OLD_SHA_NE_CI_GREEN_HEAD`.

### Optional browser smoke (bounded / not a release prerequisite unless UX claims demand it)

- Opt-in by `workflow_dispatch(run_browser=true)` or PR label `comegathesis-browser`, and only after source CI is successful.
- Use installed Chrome/Chromium, no NPM browser dependency; render desktop and narrow viewports with a short timeout.
- Save two screenshots, dimensions and a separate evidence receipt. Screenshot existence demonstrates only raster output, **not** comprehension, WCAG conformance, readable text or correct mobile layout.
- Local container Chromium smoke attempted on 2026-11-20 and timed out. This is an **observed failure to obtain a local browser proof**, not proof of a defect in the page, and no browser PASS was claimed.
- If optional Chrome is unavailable, `HOLD_BROWSER`; keep source result distinct and do not mark UI acceptance.

### Optional independent newcomer comprehension (real human/receiver required)

One public-safe R0 claim is presented three ways: short reading, CoMap relation table and CoOrb/CoBar-style compact projection. Without coaching, a qualified newcomer should identify:
1. that all three are one source-bound question;
2. that CoForgetToBecome is metaphysical speculation, not established science or ET contact;
3. the ordinary emergence alternative and unresolved test gap;
4. which controls are preview-only and where to retrieve the source.

Record device/assistive context, task result, time, errors, missed alternatives, observed date, consent and independent receiver identity. No independent reviewer or usability acceptance has yet been observed.

### Optional genuine runtime and public deployment (different authorities)

- X2/CoStead receiver, CoOrb/rickBar process, real recovery, public domain delivery and opt-in participation all require their **own** currentness, consent, operational and external-receiver receipts.
- This PR has no permission to publish a domain, send contact messages, invite alleged ET participants, modify accounts or install persistent local daemons.
- No automated CI workflow is an elected release, canonical ontology, independent receiver or authority grant.

## CI+ planes that can grow without new crowns

| Plane | Cheapest current mechanism | Success boundary | Safe fallback |
| --- | --- | --- | --- |
| **Continuous integration** | GitHub Actions source regression | PASS on exact head SHA | Local Node script / manual review remains candidate-only |
| **Continuous inspection** | JSON graph validation and negative guards | Source integrity, not truth | HOLD on missing source/edge |
| **Continuous improvement** | Compare measured newcomer comprehension and failed tests | Demonstrated reduced error or time | Keep prior reader, preserve dissent |
| **Continuous interoperability** | One WorkID/typed source across text, map and Orb-style cards | Source parity on 3 projections | Text-only |
| **Continuous independent verification** | Different receiver, separate tool/host, exact readback | Verified scope-specific proof | HOLD, no invented ACK |
| **Continuous optionality** | Local-first data, script-free HTML, replaceable runner and no-NPM tests | Runnable without one provider | Degrade to source and verified text |
| **Continuous custodial recovery** | Commit + artifact hashes + independent receiver restore | Proven cold restore | No runtime or CoEx claim |

Avoid turning CI+ into always-on expensive polling. Trigger only on a changed source, expiring proof, human receiver request or material runtime fault. A sleeping object is not a failed worker.

## Observed blockers and next actuation

- Workflow file exists on candidate branch, but the connected GitHub `fetch_commit_workflow_runs` and `get_commit_combined_status` queries for the latest source commit reported **zero results** at inspection. This does **not** prove Actions is disabled. It means a source CI PASS is **unverified**.
- The source and browser checks are defined, but a confirmed GitHub run URL/log and artifact readback are still missing.
- X2 remote commander was observed offline at this check, so neither live rickBar nor device restart proof can be inferred.
- The active PR remains draft. No merge, CoEx, canon or publishing effect is authorized by this runbook.

**Next eligible machine-owned deed:** Detect an actual Actions run for the new candidate revision, fetch its job results and artifacts, and record their exact SHA. If there is no runnable workflow, document precise permission/trigger/routing blocker, and keep it on HOLD rather than claiming green. When CI proves source, separately run a newcomer comprehension test.

**Minimal status rail:** `SOURCE_VERIFIED | CI_UNVERIFIED | BROWSER_UNVERIFIED | READER_UNVERIFIED | RUNTIME_UNVERIFIED | NO_MERGE`.

**Nonclaims:** `LOCAL_IS_NOT_LANDED` for files outside the GitHub source surface; `VALIDATION_IS_NOT_ACCEPTANCE`; `NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`; `NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE`; `HASHING_IS_NOT_SEMANTIC_INGESTION`; `DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY`.
