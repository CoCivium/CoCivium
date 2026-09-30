import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
manifest = json.loads((ROOT / "MODULE.json").read_text(encoding="utf-8"))

required_files = [
    "README.md",
    "MODULE.json",
    "FACILITATOR_GUIDE.md",
    "LEARNER_ACTIVITY.md",
    "EVALUATION.md",
    "SOURCES.md",
]

missing = [name for name in required_files if not (ROOT / name).exists()]

required_rails = {
    "MODEL_NE_WORLD",
    "SIMULATION_NE_EVIDENCE",
    "OBSERVATION_NE_INFERENCE",
    "VR_NE_LEARNING_BY_DEFAULT",
    "LEARNER_NE_ANALYTICS_PROFILE",
}

checks = {
    "state_is_candidate": manifest["state"].startswith("PUBLIC_STRAWBE_CANDIDATE"),
    "non_headset_required": "NON_HEADSET" in manifest["required_modes"],
    "no_persistent_identity_default": manifest["default_data_policy"]["persistent_identity"] is False,
    "no_biometric_retention_default": manifest["default_data_policy"]["biometric_retention"] is False,
    "rails_present": required_rails.issubset(set(manifest["rails"])),
    "required_files_present": not missing,
    "has_learning_objectives": len(manifest["learning_objectives"]) >= 5,
    "has_accessibility_requirements": len(manifest["accessibility_requirements"]) >= 5,
}

failed = [name for name, ok in checks.items() if not ok]

if failed:
    raise SystemExit("FAIL_WATERSHED_EXPLORER_R0: " + ",".join(failed) + (" missing=" + ",".join(missing) if missing else ""))

print("PASS_WATERSHED_EXPLORER_R0")
