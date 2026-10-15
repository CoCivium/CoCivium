#!/usr/bin/env python3
import json
from pathlib import Path
d=json.loads(Path("fixtures/relations/coq40_changed_contract_local_canary_r0t.json").read_text())
assert d["attempts"]==1
assert d["strict_structure"] is True and d["semantic_acceptance"] is True
assert d["output"]["action"] in ("PROBE","PARK")
assert set(d["output"]["next_probe"])=={"kind","target","evidence_surface","expected_evidence","negative_evidence","stop_condition"}
assert d["output"]["nonclaim"]=="STALE_FILE_NE_STALE_SEMANTIC_STATE"
assert d["probe_executed"] is False
assert d["persistent_worker_installed"] is False
assert d["chatgpt_independence_proven"] is False
assert d["cross_failure_domain_independence_proven"] is False
assert d["runtime_effects_beyond_canary"]==0 and d["public_effect"] is False
print("PASS: Q40 changed-contract local canary R0T")
