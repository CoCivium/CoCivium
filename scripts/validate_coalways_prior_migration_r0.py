#!/usr/bin/env python3
import json, sys
from pathlib import Path

p = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("ai/examples/coalways-prior-migration-example-r0.json")
d = json.loads(p.read_text(encoding="utf-8"))

required = [
    "object_id","source_refs","lineage_state","currentness","always_modes",
    "wake_conditions","authority_ceiling","successor_refs","embodiment_disposition",
    "uncertainty","evidence_refs","receiver_state"
]
for k in required:
    if k not in d:
        raise SystemExit("FAIL_CLOSED__MISSING_" + k.upper())

modes = d["always_modes"]
required_modes = [
    "persist","discoverable","reconsiderable","challengeable","autoevo_eligible",
    "wakeable","cooomph_governed_when_active","executing","external_effect"
]
for k in required_modes:
    if k not in modes:
        raise SystemExit("FAIL_CLOSED__MISSING_ALWAYS_MODE_" + k.upper())

allowed_dispositions = {
    "ACTIVE","DORMANT","CLOSE_SAFE","SUPERSEDED","COMPOST","RECOVERY_ONLY","UNKNOWN"
}
if d["embodiment_disposition"] not in allowed_dispositions:
    raise SystemExit("FAIL_CLOSED__INVALID_EMBODIMENT_DISPOSITION")

if not isinstance(d["source_refs"], list) or len(d["source_refs"]) < 1:
    raise SystemExit("FAIL_CLOSED__SOURCE_REFS_REQUIRED")

if modes["executing"] == "ALWAYS":
    raise SystemExit("FAIL_CLOSED__ALWAYS_EXECUTION_NOT_DEFAULT_SAFE")

print("PASS_BOUNDED_COALWAYS_PRIOR_MIGRATION_SHAPE")
print("object_id=" + str(d["object_id"]))
print("embodiment_disposition=" + str(d["embodiment_disposition"]))
