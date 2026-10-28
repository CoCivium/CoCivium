#!/usr/bin/env python3
"""CoAliveObject R0: deterministic, offline, SHADOW-ONLY pulse graph.

This is deliberately not a daemon, network transport, or effect executor.
Every output is a suggestion or status; no capabilities are granted by labels.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
from pathlib import Path

SCHEMA = "CoAliveObjectManifest/R0"
SNAPSHOT_SCHEMA = "CoAliveObjectSnapshot/R0"
ALLOWED_KIND = {"SOURCE_DELTA_REPORTED", "TEST_FAILURE_REPORTED", "MISSING_RECEIVER_REPORTED"}
ALLOWED_FIELDS = {"event_id", "object_id", "kind", "source_blob_sha", "scope"}
HEX40 = re.compile(r"^[a-f0-9]{40}$")
ID = re.compile(r"^[a-zA-Z0-9_.:-]{1,96}$")


def reject_duplicate_keys(pairs):
    result = {}
    for k, v in pairs:
        if k in result:
            raise ValueError("DUPLICATE_JSON_KEY")
        result[k] = v
    return result


def canonical_bytes(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=True,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


def digest(value):
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha_bytes(source):
    return hashlib.sha256(source).hexdigest()


class CoAlive:
    """Finite work frontier over large dormant addressable populations."""

    def __init__(self, manifest_bytes: bytes, snapshot=None):
        self.manifest_hash = sha_bytes(manifest_bytes)  # exact-byte pin; not a signature
        self.manifest = json.loads(manifest_bytes, object_pairs_hook=reject_duplicate_keys)
        m = self.manifest
        if set(m) != {"schema", "observed_at", "objects", "relations", "gaps", "policy"} or m["schema"] != SCHEMA:
            raise ValueError("BAD_MANIFEST_SCHEMA")
        if not isinstance(m["objects"], list) or not m["objects"]:
            raise ValueError("NO_OBJECTS")
        self.objects = {}
        for obj in m["objects"]:
            required = {"id", "kind", "source", "privacy", "effect_authority", "metabolism", "review_period_ticks"}
            if set(obj) != required or not ID.fullmatch(obj["id"]) or obj["id"] in self.objects:
                raise ValueError("BAD_OR_DUPLICATE_OBJECT")
            src = obj["source"]
            if set(src) != {"repo", "ref", "path", "git_blob_sha1"} or not HEX40.fullmatch(src["git_blob_sha1"]):
                raise ValueError("BAD_SOURCE_IDENTITY")
            if obj["privacy"] != "PUBLIC_REVIEW" or obj["effect_authority"] != "NONE":
                raise ValueError("NON_SHADOW_OBJECT")
            if type(obj["review_period_ticks"]) is not int or not 1 <= obj["review_period_ticks"] <= 1000000:
                raise ValueError("BAD_REVIEW_PERIOD")
            verbs = obj["metabolism"]
            if not isinstance(verbs, dict) or set(verbs) != {"SENSE", "INTAKE", "TRANSFORM", "RETURN", "REPAIR", "WAKE", "SLEEP"}:
                raise ValueError("BAD_METABOLISM")
            self.objects[obj["id"]] = obj
        self.adjacency = {x: [] for x in self.objects}
        for rel in m["relations"]:
            if set(rel) != {"from", "to", "type", "effect_authority"} or rel["from"] not in self.objects or rel["to"] not in self.objects or rel["effect_authority"] != "NONE":
                raise ValueError("BAD_RELATION")
            self.adjacency[rel["from"]].append(rel)
        for gap in m["gaps"]:
            if set(gap) != {"id", "description", "state"} or gap["state"] not in ("UNKNOWN", "HELD", "NOT_OBSERVED"):
                raise ValueError("BAD_GAP")
        p = m["policy"]
        if set(p) != {"max_work_per_pulse", "max_hops", "max_fanout", "max_pending", "max_seen_entries", "mode"} or p["mode"] != "SHADOW_ONLY":
            raise ValueError("BAD_POLICY")
        for name, low, high in [("max_work_per_pulse", 1, 100), ("max_hops", 0, 10), ("max_fanout", 0, 10), ("max_pending", 1, 10000), ("max_seen_entries", 1, 100000)]:
            if type(p[name]) is not int or not low <= p[name] <= high:
                raise ValueError("UNSAFE_POLICY_LIMIT")
        self.policy = p
        self.seen = {}          # external event ID -> hash of validated event, not raw contents
        self.pending = []       # queued logical work, never executable authority
        self.revoked = []
        self.last_tick = -1
        self.audit = []
        if snapshot is not None:
            self._restore(snapshot)

    def _restore(self, snapshot):
        if not isinstance(snapshot, dict) or set(snapshot) != {"payload", "state_sha256"}:
            raise ValueError("INVALID_SNAPSHOT")
        payload = snapshot["payload"]
        if digest(payload) != snapshot["state_sha256"]:
            raise ValueError("SNAPSHOT_TAMPERED")
        if set(payload) != {"schema", "manifest_sha256", "seen", "pending", "revoked", "last_tick"}:
            raise ValueError("BAD_SNAPSHOT_PAYLOAD")
        if payload["schema"] != SNAPSHOT_SCHEMA or payload["manifest_sha256"] != self.manifest_hash:
            raise ValueError("SPEC_NAMESPACE_CHANGED")
        if (not isinstance(payload["seen"], dict) or not isinstance(payload["pending"], list)
                or not isinstance(payload["revoked"], list) or type(payload["last_tick"]) is not int
                or payload["last_tick"] < -1):
            raise ValueError("INVALID_SNAPSHOT_STATE")
        if (len(payload["seen"]) > self.policy["max_seen_entries"]
                or len(payload["pending"]) > self.policy["max_pending"]):
            raise ValueError("SNAPSHOT_EXCEEDS_RESOURCE_LIMIT")
        if len(set(payload["revoked"])) != len(payload["revoked"]) or any(x not in self.objects for x in payload["revoked"]):
            raise ValueError("UNKNOWN_OR_DUPLICATE_REVOKED_OBJECT")
        for q in payload["pending"]:
            if (not isinstance(q, dict) or set(q) != {"id", "object_id", "kind", "root_id", "depth", "trail"}
                or q["object_id"] not in self.objects or type(q["depth"]) is not int
                or q["depth"] < 0 or q["depth"] > self.policy["max_hops"]
                or not isinstance(q["trail"], list)
                or not q["trail"] or q["trail"][-1] != q["object_id"]
                or len(q["trail"]) != len(set(q["trail"]))
                or len(q["trail"]) != q["depth"] + 1
                or q["root_id"] not in payload["seen"]
                or any(x not in self.objects for x in q["trail"])):
                raise ValueError("INVALID_PENDING_ITEM")
            if q["depth"] == 0 and (q["id"] != q["root_id"] + ":root" or q["kind"] not in (ALLOWED_KIND | {"SOURCE_REVIEW_DUE"})):
                raise ValueError("INVALID_PENDING_ROOT")
            if q["depth"] > 0 and (q["kind"] != "RELATION_CHALLENGE"
                    or any(not any(e["to"] == q["trail"][j+1] for e in self.adjacency[q["trail"][j]]) for j in range(len(q["trail"])-1))):
                raise ValueError("INVALID_PENDING_RELATION")
        if any(not ID.fullmatch(k) or not re.fullmatch(r"[a-f0-9]{64}", v) for k, v in payload["seen"].items()):
            raise ValueError("INVALID_SEEN_STATE")
        self.seen = copy.deepcopy(payload["seen"])
        self.pending = copy.deepcopy(payload["pending"])
        self.revoked = copy.deepcopy(payload["revoked"])
        self.last_tick = payload["last_tick"]

    def snapshot(self):
        payload = {"schema": SNAPSHOT_SCHEMA, "manifest_sha256": self.manifest_hash,
                   "seen": copy.deepcopy(self.seen), "pending": copy.deepcopy(self.pending),
                   "revoked": copy.deepcopy(self.revoked), "last_tick": self.last_tick}
        return {"payload": payload, "state_sha256": digest(payload)}

    def revoke(self, object_id):
        """A local policy stop: revocation can only subtract work, not grant access."""
        if object_id not in self.objects:
            raise ValueError("UNKNOWN_OBJECT")
        if object_id not in self.revoked:
            self.revoked.append(object_id)

    def ingest(self, signal):
        """Admit explicit synthetic shadow signals only, no arbitrary payload strings."""
        if not isinstance(signal, dict) or set(signal) != ALLOWED_FIELDS:
            return "HOLD_MALFORMED_OR_PRIVATE_FIELDS"
        event_id, objid, kind = signal["event_id"], signal["object_id"], signal["kind"]
        if (not isinstance(event_id, str) or not ID.fullmatch(event_id)
                or objid not in self.objects):
            return "HOLD_UNKNOWN_IDENTITY"
        if kind not in ALLOWED_KIND or signal["scope"] != "SYNTHETIC_SHADOW":
            return "HOLD_UNAUTHORIZED_EVENT"
        if signal["source_blob_sha"] != self.objects[objid]["source"]["git_blob_sha1"]:
            return "HOLD_SOURCE_MISMATCH"
        if objid in self.revoked:
            return "HOLD_REVOKED"
        fp = digest(signal)
        if event_id in self.seen:
            return "DEDUPLICATED" if self.seen[event_id] == fp else "HOLD_EVENT_ID_COLLISION"
        if len(self.seen) >= self.policy["max_seen_entries"]:
            return "HOLD_SEEN_CAPACITY"
        if len(self.pending) >= self.policy["max_pending"]:
            return "HOLD_QUEUE_CAPACITY"
        self.seen[event_id] = fp
        self.pending.append({"id": event_id+":root", "object_id": objid,
                             "kind": kind, "root_id": event_id, "depth": 0, "trail": [objid]})
        return "ADMITTED_SHADOW_ONLY"

    def pulse(self, tick, signals=()):
        if type(tick) is not int or tick < 0 or tick < self.last_tick:
            raise ValueError("NONMONOTONIC_TICK")
        self.last_tick = tick
        reports = []
        capacity_holds = 0
        for signal in signals:
            outcome = self.ingest(signal)
            valid_id = (isinstance(signal, dict) and isinstance(signal.get("event_id"),str)
                        and bool(ID.fullmatch(signal["event_id"])))
            reports.append({"event_id": signal["event_id"] if valid_id else "WITHHELD_INVALID_ID",
                            "outcome": outcome})
        # Only review-due ticks propose a review. Not a claim that the source changed.
        for oid, obj in sorted(self.objects.items()):
            period = obj["review_period_ticks"]
            if tick > 0 and tick % period == 0 and oid not in self.revoked:
                eid = f"review:{oid}:{tick}"
                if eid not in self.seen:
                    if (len(self.seen) >= self.policy["max_seen_entries"]
                        or len(self.pending) >= self.policy["max_pending"]):
                        capacity_holds += 1  # explicit lost-review hold; no fake completion
                        continue
                    self.seen[eid] = digest({"internal_review_due": eid, "source": obj["source"]["git_blob_sha1"]})
                    self.pending.append({"id": eid+":root", "object_id": oid,
                                         "kind": "SOURCE_REVIEW_DUE", "root_id": eid, "depth": 0, "trail": [oid]})
        processed, skipped_cycles, suppressed = [], 0, 0
        duplicate_work_suppressed = 0
        inspected_this_wave = set()
        budget = self.policy["max_work_per_pulse"]
        while self.pending and len(processed) < budget:
            item = self.pending.pop(0)
            oid = item["object_id"]
            if oid in self.revoked:
                suppressed += 1
                continue
            action = {"SOURCE_REVIEW_DUE": "PROPOSE_READ_ONLY_SOURCE_CHECK",
                      "SOURCE_DELTA_REPORTED": "PROPOSE_INDEPENDENT_DELTA_VERIFICATION",
                      "TEST_FAILURE_REPORTED": "PROPOSE_REPRODUCE_FAILURE",
                      "MISSING_RECEIVER_REPORTED": "PROPOSE_RECEIVER_DISCOVERY",
                      "RELATION_CHALLENGE": "PROPOSE_RELATION_INSPECTION"}[item["kind"]]
            # Same object/action may be reached from multiple roots. Preserve the
            # root-level provenance in the queue, but avoid duplicate user-visible work.
            work_key = (oid, action)
            if work_key in inspected_this_wave:
                duplicate_work_suppressed += 1
            else:
                inspected_this_wave.add(work_key)
                processed.append({"object_id": oid, "kind": item["kind"],
                                  "depth": item["depth"], "action": action,
                                  "effect_authority": "NONE", "receiver_ack": "NOT_OBSERVED"})
            if item["depth"] >= self.policy["max_hops"]:
                continue
            for rel in sorted(self.adjacency[oid], key=lambda x:(x["to"],x["type"]))[:self.policy["max_fanout"]]:
                target = rel["to"]
                if target in item["trail"]:
                    skipped_cycles += 1
                    continue
                if target in self.revoked:
                    suppressed += 1
                    continue
                if len(self.pending) >= self.policy["max_pending"]:
                    capacity_holds += 1
                    continue
                self.pending.append({"id":item["id"]+":"+target,
                                     "object_id":target, "kind":"RELATION_CHALLENGE",
                                     "root_id":item["root_id"], "depth":item["depth"]+1,
                                     "trail": item["trail"]+[target]})
        result = {"tick":tick, "admissions":reports, "processed":processed,
                  "processed_count":len(processed), "pending_count":len(self.pending),
                  "cycle_edges_suppressed":skipped_cycles, "revocation_suppressed":suppressed,
                  "duplicate_proposals_suppressed":duplicate_work_suppressed,
                  "capacity_holds":capacity_holds,
                  "external_effects":0, "provider_calls":0, "remote_acks_observed":0,
                  "mode":"SYNTHETIC_SHADOW_ONLY"}
        self.audit.append(result)
        return result


def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--manifest", default=str(Path(__file__).with_name("manifest.json")))
    ap.add_argument("--snapshot-in")
    ap.add_argument("--snapshot-out")
    ap.add_argument("--tick",type=int,default=4)
    ap.add_argument("--event-object", default="mouse")
    ap.add_argument("--event-id",default="demo1")
    ap.add_argument("--no-event",action="store_true")
    args=ap.parse_args()
    raw=Path(args.manifest).read_bytes()
    state=json.loads(Path(args.snapshot_in).read_text("utf8"), object_pairs_hook=reject_duplicate_keys) if args.snapshot_in else None
    e=CoAlive(raw,state)
    events=[]
    if not args.no_event:
        obj=e.objects[args.event_object]
        events=[{"event_id":args.event_id,"object_id":args.event_object,
                 "kind":"TEST_FAILURE_REPORTED", "source_blob_sha":obj["source"]["git_blob_sha1"],
                 "scope":"SYNTHETIC_SHADOW"}]
    report=e.pulse(args.tick,events)
    if args.snapshot_out:
        p=Path(args.snapshot_out)
        if p.exists():
            raise ValueError("SNAPSHOT_EXISTS_REFUSE_CLOBBER")
        with p.open("x",encoding="utf8") as f:
            f.write(json.dumps(e.snapshot(),indent=2,sort_keys=True)+"\n")
    print(json.dumps(report,indent=2,sort_keys=True))

if __name__ == "__main__":
    main()
