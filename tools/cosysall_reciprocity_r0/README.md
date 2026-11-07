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