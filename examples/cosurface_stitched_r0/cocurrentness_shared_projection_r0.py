"""CoCurrentness R0: shared read-only projection for CoBar/CoSpeedo/CoOrb.

One state model, multiple renderers; no live telemetry, network or side effects.
"""
from datetime import datetime, timezone

def _time(value):
    if value is None:
        return None
    if not isinstance(value, str):
        raise ValueError("timestamp must be ISO-8601 text")
    dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if dt.tzinfo is None:
        raise ValueError("timestamp timezone required")
    return dt.astimezone(timezone.utc)

def project(observations, now_utc, max_age_seconds=120):
    """Project source-relative freshness; NEVER infer receiver acceptance.

    observations: source_id -> {observed_at, receipt_ref, receiver_ack}
    Missing observations remain UNKNOWN. Stale sources are not proof of failure.
    """
    now = _time(now_utc)
    if now is None or not 1 <= max_age_seconds <= 86400:
        raise ValueError("invalid clock or bounded threshold")
    if not isinstance(observations, dict) or len(observations) > 32:
        raise ValueError("bounded observation mapping required")
    sources = {}
    for source_id, value in sorted(observations.items()):
        if not isinstance(source_id,str) or not source_id or not isinstance(value,dict):
            raise ValueError("invalid observation")
        observed = _time(value.get("observed_at"))
        age = None if observed is None else int((now-observed).total_seconds())
        receipt = value.get("receipt_ref")
        if receipt is not None and (not isinstance(receipt,str) or not receipt):
            raise ValueError("invalid receipt reference")
        ack = value.get("receiver_ack")
        if ack not in (None,False,True):
            raise ValueError("invalid receiver ACK")
        freshness = ("UNKNOWN" if age is None else
                     "FUTURE_CLOCK_CONFLICT" if age < 0 else
                     "STALE" if age > max_age_seconds else "FRESH")
        sources[source_id] = {
            "freshness": freshness, "age_seconds": age,
            "receipt_state": "REFERENCED_NOT_INDEPENDENTLY_VALIDATED" if receipt else "MISSING",
            "receipt_ref": receipt, "receiver_ack": "CLAIMED_NOT_VERIFIED" if ack is True else
                            "NO" if ack is False else "UNKNOWN"}
    fresh = [x for x in sources.values() if x["freshness"]=="FRESH"]
    observed = [x for x in sources.values() if x["age_seconds"] is not None]
    overall = ("UNKNOWN" if not observed else
               "CONFLICT" if any(x["freshness"]=="FUTURE_CLOCK_CONFLICT" for x in observed) else
               "MIXED_FRESHNESS" if fresh and len(fresh)!=len(sources) else
               "FRESH_OBSERVATIONS_ONLY" if len(fresh)==len(sources) else "STALE_OR_UNKNOWN")
    return {"schema":"CoCurrentness.SharedProjection.R0", "status":overall,
            "sources":sources, "receiver_acceptance":"UNVERIFIED",
            "nonclaims":["FRESH_SAMPLE_NE_WORK_OUTCOME","RECEIPT_REFERENCE_NE_RECEIVER_READPROOF",
                         "SOURCE_IS_NOT_X2_RUNTIME","SCREENSHOT_NE_LIVE_TELEMETRY"]}
