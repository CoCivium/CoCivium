import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
schema = json.loads((ROOT / "EDUCATOR_REVIEW_SCHEMA.json").read_text(encoding="utf-8"))

required_files = [
    "CURRICULUM_ALIGNMENT_R0B.md",
    "EDUCATOR_REVIEW_PACKET_R0B.md",
    "EDUCATOR_REVIEW_SCHEMA.json",
]

required_rails = {
    "REVIEW_PACKET_NE_REVIEW",
    "REVIEW_NE_APPROVAL",
    "CRITIQUE_NE_ENDORSEMENT",
    "CURRICULUM_ALIGNMENT_NE_CURRICULUM_CERTIFICATION",
    "NO_SILENT_DELETION_OF_MATERIAL_CRITIQUE",
}

checks = {
    "files_present": all((ROOT / x).exists() for x in required_files),
    "packet_not_review": schema["advancement_gate"]["packet_alone_sufficient"] is False,
    "independent_human_required": "AT_LEAST_ONE_IDENTIFIABLE_INDEPENDENT_HUMAN_REVIEW_ARTIFACT" in schema["advancement_gate"]["educator_reviewed_requires"],
    "stop_pilot_available": "STOP_PILOT" in schema["defect_severity"],
    "retire_option_available": "RETIRE_OR_REDESIGN_MODULE" in schema["dispositions"],
    "rails_present": required_rails.issubset(set(schema["rails"])),
}

failed=[k for k,v in checks.items() if not v]
if failed:
    raise SystemExit("FAIL_EDUCATOR_REVIEW_CONTRACT_R0B: "+",".join(failed))

print("PASS_EDUCATOR_REVIEW_CONTRACT_R0B")
