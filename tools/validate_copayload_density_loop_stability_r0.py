#!/usr/bin/env python3
import json
from pathlib import Path

d = json.loads(Path("fixtures/relations/copayload_density_loop_stability_r0.json").read_text(encoding="utf-8"))
assert d["payload_density"]["maximize_blindly"] is False
assert d["loop_policy"]["all_relations_should_loop"] is False
assert d["observer_gap"]["literal_awareness_claim"] is False
assert d["runtime_effect"] is False
assert d["public_effect"] is False
print("PASS_COPAYLOAD_DENSITY_LOOP_STABILITY_R0")
