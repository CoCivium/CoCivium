#!/usr/bin/env python3
import json
from pathlib import Path
p = Path("schemas/coqa-object-v0.1.schema.json")
d = json.loads(p.read_text(encoding="utf-8"))
required = set(d.get("required", []))
expected = {"schema","qa_id","question","answers","currentness","benefit_posture","authority_ceiling","confidentiality","nonclaims"}
missing = sorted(expected - required)
if missing:
    raise SystemExit("FAIL_CLOSED__MISSING_REQUIRED_" + "_".join(missing))
print("PASS_BOUNDED_QUESTION_ANSWER_SCHEMA_CANARY")
print("required_count=" + str(len(required)))
