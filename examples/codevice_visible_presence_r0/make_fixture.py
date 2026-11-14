#!/usr/bin/env python3
"""Creates a disposable, explicitly synthetic eight-camera observation set."""
import json
from CoDeviceVisiblePresenceR0 import EXPECTED, SCHEMA
now = "2026-11-03T22:10:00+00:00"
data = {"schema": SCHEMA, "as_of": now, "inventory_scope": "EIGHT_SYNTHETIC_CAMERAS_UNBOUND_TO_DEVICES",
        "policy": {"fresh_seconds": 60, "acknowledgement_seconds": 4, "cooldown_seconds": 45, "no_network": True, "hardware_effects": False},
        "cameras": []}
for i, name in enumerate(EXPECTED):
    data["cameras"].append({"name":name,"source":"NONE","observed_at":None,"link":"UNKNOWN",
        "event":"NONE","event_at":None,"night":False,"privacy":"LOCAL_ONLY",
        "capabilities":{"verified":False,"low_glare_light":False,"ptz":False},"last_ack_at":None})
# The following three non-live observations are explicitly invented for synthetic behavior tests.
for i, event, at in [(0,"PERSON",now),(1,"NONE",None),(2,"MOTION","2026-11-03T22:08:59+00:00")]:
    c = data["cameras"][i]
    c.update(source="SYNTHETIC_HA_EVENT" if event != "NONE" else "SYNTHETIC_HEALTH_POLL",
        observed_at=now if i != 2 else "2026-11-03T22:08:59+00:00", link="OBSERVED_REACHABLE", event=event,event_at=at)
# A synthetic PTZ with actual capability verified *only inside the invented fixture*.
data["cameras"][0]["night"] = True
data["cameras"][0]["capabilities"] = {"verified":True,"low_glare_light":True,"ptz":True}
print(json.dumps(data,indent=2,sort_keys=True))
