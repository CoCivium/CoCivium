# CoAll <-> CoSysAll+ Reciprocity Bridge R0

## CURRENT READPROOF | 2026-11-07 08:12 UTC

**Hosted GitHub Actions proof is now VERIFIED FOR SCOPE.** Draft [PR #359](https://github.com/CoCivium/CoCivium/pull/359) exercised the **read-only** `pull_request` event on branch `proof/cosysall-r1-pr-readonly-20261107`; it remains **OPEN / DRAFT / UNMERGED**. [Run #42354438680](https://github.com/CoCivium/CoCivium/actions/runs/42354438680) concluded `success`. Job `source-replay` (#128349307547) and all seven substantive/pre-post steps completed successfully. The actual job log reports **33/33 Python regression tests passed**; its exact-graph replay step passed.

**Artifact inspected, not merely a green badge:** GitHub Actions artifact #13566363382, `cosysall-r1-full-source-readproof-42354438680`, had one JSON receipt, SHA-256 `81babde22307059b81c0ddd0a5e5b4901e9fa17b818f73a8f0eee21b2154f874`. It reports source Git blob `9cc47926d2f61f439db1818702127382f78d693f`, 56 objects / 61 relations, identical projected structured-claim digests, reversed-edge and forged-permission rejection, and `HYPOTHESIS/PROPOSE/NO_EXTERNAL_EFFECTS__REVIEW_ONLY`. [Independent connector-artifact inspection record](hosted_ci_readback_20261107.json) is source-controlled and read back. The original ZIP and manifest were separately stored in the private CoCivium PublicationPackets Library, materialized again, and SHA-256 matched. GitHub's own artifact copy expires **2026-11-14 08:12 UTC**, but separate Library custody exists.

**Scope boundary:** The previous no-run observations below are **historical, superseded for hosted PR CI**. The initial *push-triggered* run specifically remains unexamined. This PR-run verifies hosted code/fixture behavior only: **NOT** independent human comprehension, policy acceptance, real visual accessibility equivalence, X2/CoOrb runtime, independent hosting, CoEx or global semantic federation. `independent_reader_ack=NOT_OBSERVED` remains unchanged. Do not close the broader issue.

**NEXT:** One uncoached, independently qualified reader completes [Reader Challenge R0](../../examples/cosysall/reader-challenge-r0.html) and produces verifiable reader-relative evidence. No one should act as Rick's relay by default. This is a test request, not a claimed receiver ACK.

**Scope:** Tested, non-actuating local Python reference adapter. Not canon, installed runtime, global federation, authenticated semantic reviewer or autonomous graph ingestion.

**Upstream:** The existing public `ai/comap-source-projection-r0.json` source graph; `schemas/coevo-delta-v0.1.schema.json` for proposal shape. Both are maintained separately in `CoCivium/CoCivium`.

**CoAll to CoSysAll:** `project` reads a qualified graph snapshot and creates a bounded whitelist-only `machine`, `accessible_list` or `none` projection, with explicit `source_snapshot_live=false`, `grants_effect_authority=false`, `actual_draw_calls=0` and `network_fetches=0`. The adapter emits data only. A separate authorized renderer may draw it.

**CoSysAll to CoAll:** `make_proposal` turns an actually registered two-hop graph path into a **hypothesis-class** CoEvoDelta `PROPOSE` packet. It carries edge IDs, source refs, a deterministic canonical graph SHA-256, reviewer handoff, and no external effect authority. Two-hop proximity is never asserted as an independently verified direct relation.

**Usage after cloning with Python 3.11+**:

```shell
python tools/cosysall_reciprocity_r0/reciprocity.py --graph ai/comap-source-projection-r0.json --focus domain:CoStrategy+ --surface machine
python tools/cosysall_reciprocity_r0/reciprocity.py --graph ai/comap-source-projection-r0.json --focus domain:CoStrategy+ --surface none
python tools/cosysall_reciprocity_r0/reciprocity.py --graph ai/comap-source-projection-r0.json --propose repo:CoCivium/MasterPlan domain:CoStrategy+ repo:CoCivium/CoCivium e1 e2 --delta-id candidate:strategy-path --observed-at 2026-11-07T02:53:30Z
python -m unittest discover -s tools/cosysall_reciprocity_r0 -p 'test_*.py' -v
```

The **explicit** `--observed-at` is required for proposals; no silent old timestamp or claimed receiver ACK. The fixture included here copies *only two public registered relation examples* from the existing graph, as a bounded test donor, not an independent full corpus mirror. No network access, system mutation, automatic ingest, private file reads or remote actions.

**Acceptance boundary:** The 17 standalone Python tests include invalid schema, orphan/spoofed sources, unsupported surface, budget zero, missing privacy authorization, fabricated edges, candidate-edge self-promotion, invalid time and a full valid source->candidate path. Full original-source integration, complete JSON Schema validation, external receiver pickup, rights/legal review, UI/visual QA and >24h recovery remain separate proof gates.

**Why it matters:** CoAll can provide contracts and evidence for selective CoSysAll display. CoSysAll can return *reviewable hypotheses* about missing relations, confusing views and resource waste. The system should never let a visualization, reader metric or model observation silently authoritatively rewrite its own rules.
## CV01 + CV05 R1 | Source-pinned cross-surface parity

**Bounded deed:** [R1 code](reciprocity_r1.py), [16 new R1 tests](test_reciprocity_r1.py), [pinned full-source replay](full_source_replay_r1.py), and [CI workflow](../../.github/workflows/cosysall-reciprocity-r1.yml). Preserve R0 and its 17 tests unchanged.

**Defect in R0's assurance:** A supplied edge could be reversed while the adapter still emitted the same undirected two-hop hypothesis. No true/executed authority was implied, but the unsigned source-link proof was insufficient. R1 adds an *explicit caller-supplied graph SHA-256 pin*, preserves `from/to` and `source_id/source_url` in all three projection claim manifests, and calls a two-hop shared neighbor a **noncausal hypothesis** rather than a directional path. The hash must come from an independent qualified source; recomputing it from a hostile document and passing it straight back is **not** authentication.

**Locally verified:** `python -m unittest discover -s tools/cosysall_reciprocity_r0 -p 'test_*.py'` returned **33/33 PASS** (R0 17 + R1 16). CV01: visual manifest, accessible-list and machine packet have identical SHA-256 digest over the same source-bound claims, while `none` has no payload and no draws. A visual *manifest* is not a running renderer, nor has human readability equivalence been independently established. CV05: bounded feedback produces an existing CoEvoDelta `HYPOTHESIS/PROPOSE` with `NO_EXTERNAL_EFFECTS__REVIEW_ONLY`. Malformed/time-ambiguous feedback, injected authority, spoofed ACK, candidate edges, private targets and graph/edge tampering fail closed.

**Full repo source path:** `python tools/cosysall_reciprocity_r0/full_source_replay_r1.py --graph ai/comap-source-projection-r0.json --schema schemas/coevo-delta-v0.1.schema.json --output /tmp/cosysall-r1-receipt.json`. Source Git blob must match the readback-qualified `9cc47926d2f61f439db1818702127382f78d693f`, or HOLD. The workflow is **installed on main**, triggering for relevant source/tests changes. **No CI run result is claimed here until a workflow run and its output are independently read back.** Commit status API returning no checks does not prove PASS or FAIL. This is a read-only workflow: no production deployment, X2 access, policy change, external action or live receiver ACK.

**Next:** Obtain completed CI full-source receipt and readback. Then compare actual rendered/accessible task outcomes with an independently qualified reader. Preserve the defect and negative tests as useful CoEvo evidence. Do not infer global acceptance from a GitHub job.

**Additional local 56/61 regression (not canonical GitHub source replay):** The older local CoMap embedded snapshot was normalized to the same 56 public-registered objects and 61 edge IDs for a **source-equivalent derivative**. The three structured projection claim hashes matched, a deliberately reversed edge failed the explicit source pin, and the resulting sample remained `HYPOTHESIS/PROPOSE`. [Scoped readproof](cv01_cv05_fullsize_local_receipt.json). This **does not** substitute for the exact GitHub source file test: GitHub CI full-source status remains **unverified** by the accessible connector.

## 2026-11-07 | Exact Git-source local replay completed

**Qualified local replay now complete:** The `ai/comap-source-projection-r0.json` public source was reconstructed byte-for-byte from the registered source families. Local `git hash-object` returned **`9cc47926d2f61f439db1818702127382f78d693f`**, matching the original GitHub-readback qualified blob. The `schemas/coevo-delta-v0.1.schema.json` reconstruction likewise returned the original **`5aa1bfc62a47492f41b422331d51dbfcccc831c4`**. This is identical Git object content, not just equivalent counts.

The exact-source `full_source_replay_r1.py` then passed: 56 registered objects / 61 edges, identical structured claim digests across `visual_manifest`, `accessible_list` and `machine`, both e1/e2 source orientations unchanged, derived feedback `HYPOTHESIS / PROPOSE / NO_EXTERNAL_EFFECTS__REVIEW_ONLY`; tampered direction and fabricated permission both rejected. The full suite was rerun **33/33 PASS**. [Public sanitized exact-source local receipt](full_source_pinned_public_readproof_r1.json) is also preserved in the private CoCivium PublicationPackets Library as `libfile_2063fd1d6f5c81919973f0e95f22c5a5`. The receipt SHA-256 at creation was `61583de0d2de6d4db6e91e26bb50633703b3e66f4329809714e89c9e37e84d43`.

**Effect boundary:** This is strong *local exact-source replay*, not a proven hosted GitHub Actions run. The GitHub connector exposes push workflows only indirectly; the Action's completed status/artifact has not been observed. It is also not three actual live visual/accessible browser implementations, external reader acceptance, X2 runtime, legal/consent certification or independent provider hosting.

**Next:** Observe the actual GitHub Actions run artifact when available through an authorized, reliable run listing; otherwise preserve HOLD. Then have a distinct qualified reader independently detect an injected false reverse edge without being told which link is false.
