"""Pure rickBar-facing projection for the existing PS7 Ollama observation.

No file, network, service, model call, or native R5 integration is performed here.
"""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

VALID = {"LOCAL_MODEL_INVENTORY_OBSERVED", "OLLAMA_ENDPOINT_UNREACHABLE",
         "MALFORMED_RESPONSE_HOLD"}

def project(observation: dict[str, Any], *, now_utc: datetime, max_age_seconds: int = 60) -> dict[str, Any]:
    if now_utc.tzinfo is None or now_utc.utcoffset() is None:
        raise ValueError("UTC_REFERENCE_REQUIRED")
    if max_age_seconds < 1:
        raise ValueError("INVALID_FRESHNESS_WINDOW")
    if not isinstance(observation, dict) or observation.get("schema") != "CoLocalModelStatus.R0":
        return {"state": "INVALID_SOURCE_HOLD", "name": "Ollama", "show_in_rail": False,
                "model_count": None, "age_seconds": None, "source": None, "reason": "schema"}
    status = observation.get("status")
    endpoint = observation.get("source")
    stamp = observation.get("observed_at_utc")
    if status not in VALID or endpoint != "http://127.0.0.1:11434/api/tags" or not isinstance(stamp, str):
        return {"state": "INVALID_SOURCE_HOLD", "name": "Ollama", "show_in_rail": False,
                "model_count": None, "age_seconds": None, "source": None, "reason": "source"}
    try:
        observed = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
        if observed.tzinfo is None or observed.utcoffset() is None:
            raise ValueError("naive timestamp")
        age = (now_utc.astimezone(timezone.utc) - observed.astimezone(timezone.utc)).total_seconds()
    except (ValueError, OverflowError):
        return {"state": "INVALID_TIME_HOLD", "name": "Ollama", "show_in_rail": False,
                "model_count": None, "age_seconds": None, "source": endpoint, "reason": "timestamp"}
    if age < -5:
        state = "CLOCK_SKEW_HOLD"
    elif age > max_age_seconds:
        state = "STALE_HOLD"
    else:
        state = status
    count = observation.get("model_count")
    names = observation.get("model_names")
    valid_count = (type(count) is int and count >= 0 and count <= 10000 and
                   isinstance(names, list) and len(names) == count and
                   all(isinstance(n, str) and n and len(n) <= 180 for n in names))
    if status == "LOCAL_MODEL_INVENTORY_OBSERVED" and not valid_count:
        state = "INVALID_INVENTORY_HOLD"
    if status != "LOCAL_MODEL_INVENTORY_OBSERVED" and (count != 0 or names != []):
        state = "INVALID_INVENTORY_HOLD"
    # Exception-first: do not nag for routine healthy local model inventory.
    return {"name": "Ollama", "state": state, "source": endpoint,
            "age_seconds": round(age, 2), "model_count": count if state == "LOCAL_MODEL_INVENTORY_OBSERVED" else None,
            "show_in_rail": state not in {"LOCAL_MODEL_INVENTORY_OBSERVED"},
            "verified_work_effects": 0, "x2_power_state": "NOT_INFERRED"}
