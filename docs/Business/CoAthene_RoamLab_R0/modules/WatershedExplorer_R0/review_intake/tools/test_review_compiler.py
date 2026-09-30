import json
import subprocess
import sys
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
fixture=ROOT/"fixtures"/"SYNTHETIC_REVIEW_FIXTURE.md"
expected=json.loads((ROOT/"fixtures"/"SYNTHETIC_REVIEW_EXPECTED.json").read_text(encoding="utf-8"))

p=subprocess.run(
    [sys.executable, str(ROOT/"tools"/"compile_review.py"), str(fixture)],
    check=True, capture_output=True, text=True
)
actual=json.loads(p.stdout)

checks=[
    actual["reviewer_disposition"]==expected["reviewer_disposition"],
    actual["reviewer_confidence"]==expected["reviewer_confidence"],
    actual["defect"]["summary"]==expected["defect"]["summary"],
    actual["defect"]["where"]==expected["defect"]["where"],
    actual["defect"]["severity"]==expected["defect"]["severity"],
    actual["defect"]["confidence"]==expected["defect"]["confidence"],
    actual["defect"]["suggested_fix"]==expected["defect"]["suggested_fix"],
    actual["project_disposition"]=="UNSET_REQUIRES_SEPARATE_TRIAGE",
    "RAW_REVIEW_NE_DERIVED_DEFECT" in actual["rails"],
    "REVIEWER_CLAIM_NE_PROJECT_FACT" in actual["rails"],
]
if not all(checks):
    raise SystemExit("FAIL_COATHENE_REVIEW_COMPILER_R0C")
print("PASS_COATHENE_REVIEW_COMPILER_R0C")
