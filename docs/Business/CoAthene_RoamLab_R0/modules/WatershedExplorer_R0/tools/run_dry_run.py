import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
module = json.loads((ROOT / "MODULE.json").read_text(encoding="utf-8"))
scenarios = json.loads((ROOT / "DRY_RUN_SCENARIOS.json").read_text(encoding="utf-8"))

rails = set(module["rails"])
required_rails = {
    "MODEL_OBSERVATION_NE_WORLD_OBSERVATION",
    "SAFETY_STOP_OVERRIDES_LESSON_COMPLETION",
    "NON_HEADSET_PATH_MUST_PRESERVE_CORE_OBJECTIVE",
    "SOURCE_CURRENTNESS_REQUIRED_FOR_TIME_SENSITIVE_LOCAL_FACTS",
    "SYNTHETIC_DRY_RUN_NE_REAL_LEARNER_VALIDATION",
}

fallbacks = module.get("failure_fallbacks", {})
priority = module.get("control_priority", [])

scenario_ids = {s["id"] for s in scenarios["scenarios"]}
required_scenarios = {
    "S01_BASELINE",
    "S02_VR_UNAVAILABLE",
    "S03_NETWORK_UNAVAILABLE",
    "S04_MOTION_DISCOMFORT",
    "S05_ACCESSIBILITY_NO_HEADSET",
    "S06_OVERCLAIM",
    "S07_MODEL_VS_WORLD_CONFUSION",
    "S08_SPILL",
    "S09_SOURCE_UNAVAILABLE",
    "S10_TIME_COMPRESSION",
}

checks = {
    "required_rails": required_rails.issubset(rails),
    "all_scenarios_present": required_scenarios.issubset(scenario_ids),
    "vr_fallback": fallbacks.get("vr_unavailable") == "CONTINUE_NON_HEADSET",
    "network_fallback": fallbacks.get("internet_unavailable") == "USE_DATED_OFFLINE_SOURCE_PACK",
    "discomfort_fallback": "STOP_IMMERSIVE_MODE" in fallbacks.get("learner_discomfort", ""),
    "spill_fallback": "STOP_ACTIVITY" in fallbacks.get("spill_near_electronics", ""),
    "time_fallback": "45_MINUTE_MINIMUM_PATH" in fallbacks.get("time_loss", ""),
    "safety_first": len(priority) > 0 and priority[0] == "SAFETY",
    "minimum_path_45": module["duration_minutes"]["minimum_path"] == 45,
    "no_persistent_identity": module["default_data_policy"]["persistent_identity"] is False,
    "no_biometric_retention": module["default_data_policy"]["biometric_retention"] is False,
    "offline_source_required": any("offline" in x.lower() for x in module["required_inputs"]),
}

failed = [name for name, ok in checks.items() if not ok]
if failed:
    raise SystemExit("FAIL_WATERSHED_EXPLORER_R0A_DRY_RUN: " + ",".join(failed))

print("PASS_WATERSHED_EXPLORER_R0A_DRY_RUN")
