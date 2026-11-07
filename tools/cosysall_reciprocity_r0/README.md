# CoAll <-> CoSysAll+ Reciprocity Bridge R0

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
