#!/usr/bin/env python3
"""CoStateMutation R0: pure multi-axis shadow reducer, not a mutation authority.

Reuses CoSourceGraph, CoEvoDelta and CoSessionAutocycle classifications.
Synthetic tests only; never opens real files/URLs, sends events, or changes a node.
"""
from __future__ import annotations
import copy
import hashlib
import json
import re
import unittest

SCHEMA = "CoAll.CoStateMutationShadow.R0"
E_SCHEMA = "CoAll.CoMutationEvent.R0"
AXES = ("source", "site", "node", "process", "memory", "custody",
        "privacy", "authority", "receiver", "meaning")
GUARDED = frozenset(("privacy", "authority", "receiver"))
CLASSES = frozenset(("OBSERVED", "INFERRED", "HYPOTHESIS", "PREDICTED",
                     "PLANNED", "METAPHORICAL", "MYTHIC", "COUNTERFACTUAL", "UNKNOWN"))
HASH = re.compile(r"[0-9a-f]{64}\Z")
ID = re.compile(r"[A-Za-z0-9_.:-]{1,128}\Z")

def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                  ensure_ascii=True).encode("utf-8")).hexdigest()

def blank(object_id="project:synthetic"):
    return {"schema": SCHEMA, "object_id": object_id, "revision": 0,
            "axes": {a: {"value": "UNKNOWN", "epistemic": "UNKNOWN",
                        "source_refs": []} for a in AXES},
            "seen": {}, "proposals": [], "shadow_only": True,
            "real_effect_authorized": False, "receiver_ack_verified": False}

def event(event_id="e1", *, revision=0, axis="source", value="CHANGED",
          kind="OBSERVE", epistemic="OBSERVED", refs=None, effect=False,
          target="project:synthetic", mutation_class="OBSERVE"):
    return {"schema": E_SCHEMA, "event_id": event_id, "work_id": "work:synthetic",
            "target_id": target, "base_revision": revision, "kind": kind,
            "axis": axis, "value": value, "epistemic_class": epistemic,
            "source_refs": ["src:fixture"] if refs is None else refs,
            "effect_requested": effect, "mutation_class": mutation_class,
            "observer_claim": "synthetic:test", "observed_at": "2026-11-24T00:00:00Z"}

def gate(current, proposed):
    """Return (new shadow projection, decision), never an authorized effect."""
    state = copy.deepcopy(current)
    def hold(reason):
        return state, {"state": "HOLD", "reason": reason, "real_effect_authorized": False}
    if not isinstance(current, dict) or current.get("schema") != SCHEMA:
        return hold("INVALID_BASE_SCHEMA")
    if current.get("shadow_only") is not True or current.get("real_effect_authorized") is not False:
        return hold("NON_SHADOW_OR_AUTHORITY_CLAIM")
    if not isinstance(proposed, dict) or proposed.get("schema") != E_SCHEMA:
        return hold("INVALID_EVENT_SCHEMA")
    eid = proposed.get("event_id")
    if not isinstance(eid, str) or not ID.fullmatch(eid):
        return hold("INVALID_EVENT_ID")
    fingerprint = digest(proposed)
    if eid in state["seen"]:
        if state["seen"][eid] == fingerprint:
            return state, {"state": "REPLAY_NOOP", "reason": "IDENTICAL_EVENT",
                           "real_effect_authorized": False}
        return hold("EVENT_ID_COLLISION_DIFFERENT_BYTES")
    if proposed.get("target_id") != state["object_id"]:
        return hold("TARGET_MISMATCH")
    if type(proposed.get("base_revision")) is not int or proposed["base_revision"] != state["revision"]:
        return hold("STALE_BASE_REVISION")
    if not isinstance(proposed.get("work_id"), str) or not ID.fullmatch(proposed["work_id"]):
        return hold("INVALID_WORK_ID")
    ax = proposed.get("axis")
    if ax not in AXES:
        return hold("UNKNOWN_AXIS")
    if proposed.get("kind") not in ("OBSERVE", "PROPOSE"):
        return hold("UNKNOWN_MUTATION_KIND")
    if proposed.get("epistemic_class") not in CLASSES:
        return hold("UNKNOWN_EPISTEMIC_CLASS")
    if proposed.get("effect_requested") is not False or proposed.get("mutation_class") == "EFFECT_GATED":
        return hold("EFFECT_REQUIRES_EXTERNAL_AUTHORITY")
    if proposed.get("mutation_class") not in ("OBSERVE", "PROPOSE", "BRANCH_MUTATE", "REVIEW_CHALLENGE"):
        return hold("UNSUPPORTED_MUTATION_CLASS")
    if not isinstance(proposed.get("value"), str) or not proposed["value"] or len(proposed["value"]) > 160:
        return hold("INVALID_VALUE")
    refs = proposed.get("source_refs")
    if not isinstance(refs, list) or not refs or any(not isinstance(x, str) or not x for x in refs):
        return hold("SOURCE_EVIDENCE_MISSING")
    if proposed.get("kind") == "OBSERVE" and proposed.get("mutation_class") != "OBSERVE":
        return hold("OBSERVATION_MUTATION_CLASS_CONFLICT")
    if proposed["kind"] == "OBSERVE" and proposed["epistemic_class"] != "OBSERVED":
        return hold("INFERENCE_OR_METAPHOR_NOT_OBSERVATION")
    if proposed["kind"] == "OBSERVE" and ax in GUARDED:
        return hold("GUARDED_AXIS_REQUIRES_AUTHENTICATED_RECEIVER")
    # Only a shadow *claim* is stored; input source refs are never authenticated here.
    if proposed["kind"] == "OBSERVE":
        state["axes"][ax] = {"value": proposed["value"],
                             "epistemic": "OBSERVED_SOURCE_CLAIM_UNVERIFIED",
                             "source_refs": list(refs)}
        status = "SHADOW_AXIS_OBSERVATION_RECORDED"
    else:
        state["proposals"].append({"axis": ax, "value": proposed["value"],
                                   "epistemic": proposed["epistemic_class"],
                                   "source_refs": list(refs),
                                   "event_id": eid})
        status = "SHADOW_PROPOSAL_RECORDED"
    state["seen"][eid] = fingerprint
    state["revision"] += 1
    return state, {"state": status, "reason": "NO_EXTERNAL_EFFECT",
                   "revision": state["revision"], "real_effect_authorized": False}

class ShadowTests(unittest.TestCase):
    def setUp(self):
        self.s = blank()
    def assertHold(self, e, reason):
        s,r = gate(self.s,e)
        self.assertEqual(r["state"], "HOLD")
        self.assertEqual(r["reason"], reason)
        self.assertEqual(s, self.s)
    def test_01_source_observation_only_changes_source(self):
        s,r=gate(self.s,event()); self.assertEqual(r["state"],"SHADOW_AXIS_OBSERVATION_RECORDED")
        self.assertEqual(s["axes"]["source"]["value"],"CHANGED")
        for axis in AXES:
            if axis != "source": self.assertEqual(s["axes"][axis],self.s["axes"][axis])
    def test_02_public_site_404_does_not_erase_source(self):
        a,_=gate(self.s,event());b,_=gate(a,event("e2",revision=1,axis="site",value="HTTP_404"))
        self.assertEqual(b["axes"]["source"]["value"],"CHANGED")
        self.assertEqual(b["axes"]["site"]["value"],"HTTP_404")
        self.assertEqual(b["axes"]["receiver"]["value"],"UNKNOWN")
    def test_03_process_start_is_not_node_health(self):
        s,_=gate(self.s,event(axis="process",value="PROCESS_RUNNING"))
        self.assertEqual(s["axes"]["node"]["value"],"UNKNOWN")
    def test_04_memory_pointer_is_not_custody_ack(self):
        s,_=gate(self.s,event(axis="memory",value="INDEXED_POINTER"))
        self.assertEqual(s["axes"]["custody"]["value"],"UNKNOWN")
        self.assertFalse(s["receiver_ack_verified"])
    def test_05_metaphorical_proposal_is_not_a_write(self):
        s,r=gate(self.s,event(axis="meaning",kind="PROPOSE",
                     epistemic="METAPHORICAL",mutation_class="PROPOSE"))
        self.assertEqual(r["state"],"SHADOW_PROPOSAL_RECORDED")
        self.assertEqual(s["axes"]["meaning"]["value"],"UNKNOWN")
    def test_06_metaphor_cannot_claim_observed_runtime(self):
        self.assertHold(event(axis="node",epistemic="METAPHORICAL"),
                        "INFERENCE_OR_METAPHOR_NOT_OBSERVATION")
    def test_07_source_claim_cannot_change_privacy(self):
        self.assertHold(event(axis="privacy"),"GUARDED_AXIS_REQUIRES_AUTHENTICATED_RECEIVER")
    def test_08_source_claim_cannot_change_authority(self):
        self.assertHold(event(axis="authority"),"GUARDED_AXIS_REQUIRES_AUTHENTICATED_RECEIVER")
    def test_09_source_claim_cannot_forge_receiver_ack(self):
        self.assertHold(event(axis="receiver",value="ACK"),"GUARDED_AXIS_REQUIRES_AUTHENTICATED_RECEIVER")
    def test_10_effect_requested_is_fenced(self):
        self.assertHold(event(effect=True),"EFFECT_REQUIRES_EXTERNAL_AUTHORITY")
    def test_11_effect_gated_class_is_fenced(self):
        self.assertHold(event(mutation_class="EFFECT_GATED"),"EFFECT_REQUIRES_EXTERNAL_AUTHORITY")
    def test_12_empty_evidence_holds(self):
        self.assertHold(event(refs=[]),"SOURCE_EVIDENCE_MISSING")
    def test_13_wrong_target_holds(self):
        self.assertHold(event(target="project:another"),"TARGET_MISMATCH")
    def test_14_unknown_axis_holds(self):
        self.assertHold(event(axis="magical"),"UNKNOWN_AXIS")
    def test_15_stale_version_holds(self):
        s,_=gate(self.s,event());a,r=gate(s,event("e2",revision=0,axis="site"))
        self.assertEqual(r["reason"],"STALE_BASE_REVISION");self.assertEqual(s,a)
    def test_16_duplicate_same_bytes_is_noop(self):
        s,_=gate(self.s,event());a,r=gate(s,event())
        self.assertEqual(a,s);self.assertEqual(r["state"],"REPLAY_NOOP")
    def test_17_duplicate_id_different_bytes_holds(self):
        s,_=gate(self.s,event());a,r=gate(s,event(value="DIFFERENT",revision=1))
        self.assertEqual(a,s);self.assertEqual(r["reason"],"EVENT_ID_COLLISION_DIFFERENT_BYTES")
    def test_18_bogus_schema_holds(self):
        self.assertHold({**event(),"schema":"CoAll.NotOurSchema"},"INVALID_EVENT_SCHEMA")
    def test_19_model_output_is_not_observation(self):
        self.assertHold(event(epistemic="INFERRED"),"INFERENCE_OR_METAPHOR_NOT_OBSERVATION")
    def test_20_proposal_does_not_promote_receiver_or_site(self):
        s,_=gate(self.s,event(kind="PROPOSE",mutation_class="PROPOSE"))
        self.assertEqual(s["axes"]["site"]["value"],"UNKNOWN")
        self.assertEqual(s["axes"]["receiver"]["value"],"UNKNOWN")
    def test_21_no_effect_even_after_many_proposals(self):
        s=self.s
        for n in range(15):
            s,r=gate(s,event("m"+str(n),revision=n,kind="PROPOSE",mutation_class="PROPOSE",
                             axis=AXES[n % len(AXES)],epistemic="HYPOTHESIS"))
            self.assertEqual(r["state"],"SHADOW_PROPOSAL_RECORDED")
        self.assertFalse(s["real_effect_authorized"])
        self.assertFalse(s["receiver_ack_verified"])
    def test_22_bare_event_never_authenticates_actor(self):
        s,_=gate(self.s,event())
        self.assertEqual(s["axes"]["source"]["epistemic"],"OBSERVED_SOURCE_CLAIM_UNVERIFIED")
    def test_23_bad_work_id_holds(self):
        self.assertHold({**event(),"work_id":" "},"INVALID_WORK_ID")
    def test_24_bare_boolean_revision_holds(self):
        self.assertHold({**event(),"base_revision":False},"STALE_BASE_REVISION")
    def test_25_unsupported_mutation_class_holds(self):
        self.assertHold(event(mutation_class="AUTO_REPLACE"),"UNSUPPORTED_MUTATION_CLASS")
    def test_26_unknown_epistemic_holds(self):
        self.assertHold(event(epistemic="PROVED_FOREVER"),"UNKNOWN_EPISTEMIC_CLASS")
    def test_27_observe_cannot_branch_mutate(self):
        self.assertHold(event(mutation_class="BRANCH_MUTATE"),"OBSERVATION_MUTATION_CLASS_CONFLICT")
    def test_28_canonical_hash_independent_of_key_order(self):
        self.assertEqual(digest({"x":1,"y":2}),digest({"y":2,"x":1}))
    def test_29_new_observation_on_other_axis_no_cross_promotion(self):
        a,_=gate(self.s,event(axis="site",value="HTTP_200"))
        b,_=gate(a,event("e2",revision=1,axis="node",value="PROCESS_ALIVE"))
        self.assertEqual(b["axes"]["receiver"]["value"],"UNKNOWN")
        self.assertEqual(b["axes"]["authority"]["value"],"UNKNOWN")
    def test_30_invalid_proposal_does_not_append(self):
        s,r=gate(self.s,event(kind="PROPOSE",effect=True,mutation_class="PROPOSE"))
        self.assertEqual(r["state"],"HOLD");self.assertEqual(s["proposals"],[])

if __name__ == "__main__":
    unittest.main(verbosity=1)
