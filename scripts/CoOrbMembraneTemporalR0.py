"""CoOrb membrane R0: a versioned boundary and temporal relation projection.

Pure, bounded, deterministic renderer metadata. It never grants a worker
permission, predicts reality, moves a UI, or authenticates receiver pickup.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone

CLASSES={"OBSERVED","PREDICTED","PLANNED","PREFERRED","COUNTERFACTUAL","UNKNOWN"}
DIRECTIONS={"INBOUND","OUTBOUND","CROSS_BOUNDARY","INTERNAL"}
MAX_EDGES=256

@dataclass(frozen=True)
class BoundaryEvent:
    edge_id:str
    object_id:str
    relation:str
    direction:str
    epistemic_class:str
    source_revision:str
    source_uri:str
    observed_at:str
    valid_at:str
    target_version:str
    receiver_ack:bool=False
    confidence:float|None=None

def _instant(s):
    dt=datetime.fromisoformat(s.replace("Z","+00:00"))
    if dt.tzinfo is None:
        raise ValueError("TIMEZONE_REQUIRED")
    return dt.astimezone(timezone.utc)

def project(current_version:str, events:tuple[BoundaryEvent,...], *,
            as_of:str, work_id:str, max_visible:int=12)->dict:
    if not current_version or not work_id:
        raise ValueError("MISSING_IDENTITY")
    now=_instant(as_of)
    if len(events)>MAX_EDGES or max_visible<1 or max_visible>MAX_EDGES:
        raise ValueError("UNBOUNDED_PROJECTION")
    if len({e.edge_id for e in events})!=len(events):
        raise ValueError("DUPLICATE_EDGE")
    out=[]
    for e in events:
        if not (e.edge_id and e.object_id and e.relation and e.source_revision
                and e.source_uri and e.target_version):
            raise ValueError("UNBOUND_EDGE")
        if e.direction not in DIRECTIONS or e.epistemic_class not in CLASSES:
            raise ValueError("INVALID_RELATION_TYPE")
        if e.confidence is not None and (not 0<=e.confidence<=1):
            raise ValueError("INVALID_CONFIDENCE")
        observed=_instant(e.observed_at)
        valid=_instant(e.valid_at)
        if observed>now:
            raise ValueError("FUTURE_OBSERVATION")
        # Visible future rays remain explicitly hypothetical, even when
        # the user wishes for them or they score high in a model.
        ray=e.epistemic_class!="OBSERVED" or valid>now
        out.append({
            "edge_id":e.edge_id, "object_id":e.object_id,
            "direction":e.direction,
            "kind":"FORECAST_RAY" if ray else "OBSERVED_EDGE",
            "epistemic_class":e.epistemic_class,
            "version_relation":"CURRENT" if e.target_version==current_version else "OTHER_VERSION",
            "source_revision":e.source_revision,"source_uri":e.source_uri,
            "observed_at":e.observed_at,"valid_at":e.valid_at,
            "receiver_ack":"CLAIMED_NOT_AUTHENTICATED" if e.receiver_ack else "UNPROVEN",
        })
    out.sort(key=lambda x:(x["kind"]!="OBSERVED_EDGE",x["version_relation"]!="CURRENT",x["edge_id"]))
    return {"work_id":work_id,"version":current_version,"as_of":as_of,
            "membrane_edges":out[:max_visible],
            "hidden_count":max(0,len(out)-max_visible),
            "version_upgrade_claimed":False,"native_renderer_changed":False,
            "predictive_authority":False}
