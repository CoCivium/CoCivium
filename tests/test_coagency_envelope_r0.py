from __future__ import annotations

import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from scripts.CoAgencyEnvelopeR0 import (
    Held, NONCLAIMS, digest, validate_forest,
)


AS_OF = "2026-11-11T18:00:00Z"


def participant(pid="worker-a", actions=None, authority="LOCAL_BOUNDED"):
    return {
        "participant_id": pid,
        "participant_class": "DELEGATE",
        "roles": ["VERIFIER"],
        "authority_ceiling": authority,
        "identity_basis": ["fixture"],
        "effect_scope": actions or [
            "READ_SEARCH_INSPECT_COMPARE_RECONCILE",
            "DETERMINISTIC_VALIDATION",
            "PREPARE_ROLLBACK_CONTAINMENT_AND_POST_EFFECT_VERIFICATION",
        ],
    }


def participation(effect="LOCAL_REVERSIBLE"):
    return {
        "schema": "CoNodeParticipation.v0.1",
        "node_id": "fixture-node",
        "lifecycle_state": "CANDIDATE",
        "participant_scope": "fixture",
        "privacy_domain": "PRIVATE_COCIVIUM",
        "capabilities": [],
        "allowed_transports": [],
        "effect_ceiling": effect,
        "external_provider_policy": {
            "provider_is_control_plane": False,
            "unrestricted_remote_control": False,
            "prefer_local_when_sufficient": True,
        },
        "public_internet_exposure": "NONE_BY_DEFAULT",
        "receipt_route": "fixture:none",
        "human_projection": "fixture",
    }


def standing():
    return json.loads(Path("ai/currentness/standing-authorization-latch-r2-20261025.json")
                      .read_text(encoding="utf-8"))


def envelope(eid, person, node, latch, *, parent=None, mode="SHADOW",
             topology="ABSENT", basis="STANDING_BOUNDED", actions=None,
             effect="LOCAL_REVERSIBLE", actuator=None, lease=None,
             glass="OFF", auth_ref=None, work="work-r0", collision="fixture:one"):
    if auth_ref is None and basis == "STANDING_BOUNDED":
        auth_ref = "standing:sha256:" + digest(latch)
    return {
        "schema": "CoAgencyEnvelope.R0",
        "envelope_id": eid,
        "parent_envelope_id": parent,
        "root_work_id": work,
        "participant_id": person["participant_id"],
        "source_bindings": {
            "participant_canonical_sha256": digest(person),
            "participation_canonical_sha256": digest(node),
            "standing_authorization_canonical_sha256": digest(latch),
        },
        "mode": mode,
        "supervision_topology": topology,
        "authorization_basis": basis,
        "authorization_ref": auth_ref,
        "authority_ceiling": person["authority_ceiling"],
        "allowed_actions": actions or [],
        "effect_ceiling": effect,
        "collision_domain": collision,
        "actuator_id": actuator,
        "lease": lease,
        "break_glass": glass,
        "receipts": [],
        "nonclaims": sorted(NONCLAIMS),
    }


class CoAgencyEnvelopeTests(unittest.TestCase):
    def setUp(self):
        self.person = participant()
        self.node = participation()
        self.latch = standing()
        read = "READ_SEARCH_INSPECT_COMPARE_RECONCILE"
        verify = "DETERMINISTIC_VALIDATION"
        self.root = envelope("env-root", self.person, self.node, self.latch,
                             actions=[read, verify])
        self.proposal = envelope("env-propose", self.person, self.node, self.latch,
                                 parent="env-root", mode="PROPOSE", actions=[verify])
        self.worker = envelope(
            "env-worker", self.person, self.node, self.latch,
            parent="env-propose", mode="DELEGATED", actions=[verify],
            actuator="actuator-one",
            lease={"starts_at": "2026-11-11T17:00:00Z",
                   "expires_at": "2026-11-11T19:00:00Z"},
        )

    def check(self, rows=None, **kwargs):
        return validate_forest(rows or [self.root, self.proposal, self.worker],
                               [self.person], self.node, self.latch,
                               as_of=AS_OF, **kwargs)

    def test_shadow_propose_delegated_turtle_passes(self):
        report = self.check()
        self.assertEqual(report["state"], "PASS_BOUNDED_STATIC_COMPOSITION_ONLY")
        self.assertEqual(report["max_depth"], 2)
        self.assertEqual(report["active_actuators"], 1)
        self.assertEqual(report["effects_executed"], 0)
        self.assertFalse(report["receiver_ack_proven"])

    def test_child_cannot_add_action(self):
        self.proposal["allowed_actions"].append(
            "PREPARE_ROLLBACK_CONTAINMENT_AND_POST_EFFECT_VERIFICATION")
        with self.assertRaisesRegex(Held, "TURTLE_ACTION_AMPLIFICATION"):
            self.check()

    def test_child_cannot_raise_effect_ceiling(self):
        self.root["effect_ceiling"] = "OBSERVE_ONLY"
        with self.assertRaisesRegex(Held, "TURTLE_EFFECT_AMPLIFICATION"):
            self.check()

    def test_gated_parent_cannot_be_laundered_into_write(self):
        node = participation("EFFECT_GATED")
        root = envelope("gated", self.person, node, self.latch,
                        mode="ATTENDED", topology="IN_LOOP",
                        basis="EXPLICIT_CURRENT", auth_ref="verified:fixture",
                        actions=[], effect="EFFECT_GATED")
        child = envelope("write", self.person, node, self.latch, parent="gated",
                         mode="ATTENDED", topology="IN_LOOP",
                         basis="EXPLICIT_CURRENT", auth_ref="verified:fixture",
                         actions=[], effect="BOUNDED_SHARED_WRITE")
        with self.assertRaisesRegex(Held, "EFFECT_EXCEEDS_NODE_CEILING|TURTLE_EFFECT_AMPLIFICATION"):
            validate_forest([root, child], [self.person], node, self.latch, as_of=AS_OF,
                            explicit_authorization_verifier=lambda *_: True)

    def test_source_binding_mismatch_holds(self):
        self.root["source_bindings"]["standing_authorization_canonical_sha256"] = "0" * 64
        with self.assertRaisesRegex(Held, "STANDING_SOURCE_BINDING_MISMATCH"):
            self.check([self.root])

    def test_standing_latch_content_cannot_be_forged(self):
        forged = copy.deepcopy(self.latch)
        forged["default_authorized_actions"].append("INVENTED_EFFECT")
        row = envelope("forged", self.person, self.node, forged, actions=[])
        with self.assertRaisesRegex(Held, "STANDING_AUTHORIZATION_CONTENT_MISMATCH"):
            validate_forest([row], [self.person], self.node, forged, as_of=AS_OF)

    def test_donor_dependency_bytes_are_pinned(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            with self.assertRaisesRegex(Held, "DEPENDENCY_NOT_BOUNDED_REGULAR_FILE"):
                self.check([self.root], contract_root=root)

    def test_malformed_participant_contract_holds(self):
        malformed = copy.deepcopy(self.person)
        malformed["permission_by_visibility"] = True
        row = envelope("malformed", malformed, self.node, self.latch, actions=[])
        with self.assertRaisesRegex(Held, "PARTICIPANT_FIELDS_INVALID"):
            validate_forest([row], [malformed], self.node, self.latch, as_of=AS_OF)

    def test_standing_latch_cannot_authorize_unlisted_action(self):
        person = participant(actions=["INVENTED_EFFECT"])
        row = envelope("invented", person, self.node, self.latch,
                       actions=["INVENTED_EFFECT"])
        with self.assertRaisesRegex(Held, "ACTION_OUTSIDE_STANDING_AUTHORIZATION"):
            validate_forest([row], [person], self.node, self.latch, as_of=AS_OF)

    def test_standing_latch_cannot_open_shared_write(self):
        node = participation("BOUNDED_SHARED_WRITE")
        row = envelope("write", self.person, node, self.latch,
                       actions=[], effect="BOUNDED_SHARED_WRITE")
        with self.assertRaisesRegex(Held, "STANDING_AUTHORIZATION_EFFECT_AMPLIFICATION"):
            validate_forest([row], [self.person], node, self.latch, as_of=AS_OF)

    def test_human_presence_is_not_consent(self):
        row = envelope("attended", self.person, self.node, self.latch,
                       mode="ATTENDED", topology="IN_LOOP",
                       basis="EXPLICIT_CURRENT", auth_ref="human:claim",
                       actions=["DETERMINISTIC_VALIDATION"])
        with self.assertRaisesRegex(Held, "EXPLICIT_AUTHORIZATION_UNVERIFIED"):
            self.check([row])

    def test_independent_explicit_verifier_can_validate_bounded_root(self):
        row = envelope("attended", self.person, self.node, self.latch,
                       mode="ATTENDED", topology="IN_LOOP",
                       basis="EXPLICIT_CURRENT", auth_ref="verified:fixture",
                       actions=["DETERMINISTIC_VALIDATION"])
        report = self.check([row], explicit_authorization_verifier=
                            lambda ref, _row: ref == "verified:fixture")
        self.assertEqual(report["explicit_authorizations_verified"], 1)

    def test_absence_cannot_pose_as_current_human_authorization(self):
        row = envelope("absent", self.person, self.node, self.latch,
                       basis="EXPLICIT_CURRENT", auth_ref="verified:fixture",
                       actions=["DETERMINISTIC_VALIDATION"])
        with self.assertRaisesRegex(Held, "EXPLICIT_CURRENT_REQUIRES_CURRENT_HUMAN_TOPOLOGY"):
            self.check([row], explicit_authorization_verifier=lambda *_: True)

    def test_none_basis_is_effectless(self):
        row = envelope("none", self.person, self.node, self.latch,
                       basis="NONE", auth_ref=None,
                       actions=["DETERMINISTIC_VALIDATION"])
        with self.assertRaisesRegex(Held, "NONE_BASIS_MUST_BE_EFFECTLESS"):
            self.check([row])

    def test_break_glass_freeze_narrows(self):
        row = envelope("freeze", self.person, self.node, self.latch,
                       actions=["DETERMINISTIC_VALIDATION"], effect="OBSERVE_ONLY",
                       glass="FREEZE")
        self.assertEqual(self.check([row])["active_actuators"], 0)

    def test_break_glass_does_not_add_recovery_power(self):
        child = envelope(
            "recover", self.person, self.node, self.latch, parent="env-root",
            mode="PROPOSE", actions=[
                "PREPARE_ROLLBACK_CONTAINMENT_AND_POST_EFFECT_VERIFICATION"
            ], glass="RECOVER",
        )
        with self.assertRaisesRegex(Held, "TURTLE_ACTION_AMPLIFICATION"):
            self.check([self.root, child])

    def test_active_break_glass_cannot_silently_clear(self):
        freeze = envelope("freeze", self.person, self.node, self.latch,
                          actions=["DETERMINISTIC_VALIDATION"], effect="OBSERVE_ONLY",
                          glass="FREEZE")
        cleared = envelope("cleared", self.person, self.node, self.latch,
                           parent="freeze", mode="PROPOSE",
                           actions=["DETERMINISTIC_VALIDATION"], effect="OBSERVE_ONLY",
                           glass="OFF")
        with self.assertRaisesRegex(Held, "TURTLE_BREAK_GLASS_CLEARED_OR_ESCALATED"):
            self.check([freeze, cleared])

    def test_two_actuators_same_collision_domain_hold(self):
        root_b = copy.deepcopy(self.root)
        root_b["envelope_id"] = "env-root-b"
        proposal_b = copy.deepcopy(self.proposal)
        proposal_b["envelope_id"] = "env-propose-b"
        proposal_b["parent_envelope_id"] = "env-root-b"
        worker_b = copy.deepcopy(self.worker)
        worker_b["envelope_id"] = "env-worker-b"
        worker_b["parent_envelope_id"] = "env-propose-b"
        worker_b["actuator_id"] = "actuator-two"
        with self.assertRaisesRegex(Held, "MULTIPLE_ACTUATORS_IN_COLLISION_DOMAIN"):
            self.check([self.root, self.proposal, self.worker,
                        root_b, proposal_b, worker_b])

    def test_expired_and_unbounded_leases_hold(self):
        self.worker["lease"]["expires_at"] = "2026-11-11T18:00:00Z"
        with self.assertRaisesRegex(Held, "ACTUATOR_LEASE_NOT_CURRENT"):
            self.check()
        self.worker["lease"] = {"starts_at": "2026-11-10T18:00:00Z",
                                "expires_at": "2026-11-12T18:00:00Z"}
        with self.assertRaisesRegex(Held, "ACTUATOR_LEASE_NOT_BOUNDED"):
            self.check()

    def test_cycles_unknown_parents_and_bad_transitions_hold(self):
        cycle_a = copy.deepcopy(self.proposal)
        cycle_a["envelope_id"] = "cycle-a"
        cycle_a["parent_envelope_id"] = "cycle-b"
        cycle_b = copy.deepcopy(self.proposal)
        cycle_b["envelope_id"] = "cycle-b"
        cycle_b["parent_envelope_id"] = "cycle-a"
        with self.assertRaisesRegex(Held, "ENVELOPE_LINEAGE_CYCLE"):
            self.check([cycle_a, cycle_b])
        self.root["parent_envelope_id"] = "missing"
        with self.assertRaisesRegex(Held, "PARENT_ENVELOPE_NOT_FOUND"):
            self.check()
        self.root["parent_envelope_id"] = None
        self.proposal["mode"] = "QUIET"
        self.proposal["allowed_actions"] = []
        self.worker["parent_envelope_id"] = "env-propose"
        with self.assertRaisesRegex(Held, "MODE_TRANSITION_NOT_ALLOWED"):
            self.check()

    def test_receipt_text_does_not_create_ack_or_runtime(self):
        self.root["receipts"] = ["claimed:receiver-ack", "claimed:runtime"]
        report = self.check()
        self.assertFalse(report["receiver_ack_proven"])
        self.assertEqual(report["runtime_bindings_proven"], 0)

    def test_cli_refuses_self_asserted_explicit_authorization(self):
        row = envelope("attended", self.person, self.node, self.latch,
                       mode="ATTENDED", topology="IN_LOOP",
                       basis="EXPLICIT_CURRENT", auth_ref="self:claim",
                       actions=["DETERMINISTIC_VALIDATION"])
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            paths = {}
            for name, value in (("envelopes", [row]), ("participants", [self.person]),
                                ("participation", self.node), ("standing", self.latch)):
                paths[name] = root / (name + ".json")
                paths[name].write_text(json.dumps(value), encoding="utf-8")
            call = [sys.executable, "scripts/CoAgencyEnvelopeR0.py",
                    "--envelopes", str(paths["envelopes"]),
                    "--participants", str(paths["participants"]),
                    "--participation", str(paths["participation"]),
                    "--standing-authorization", str(paths["standing"]),
                    "--as-of", AS_OF]
            result = subprocess.run(call, capture_output=True, text=True, timeout=8)
            self.assertEqual(result.returncode, 3)
            self.assertEqual(json.loads(result.stdout)["reason"],
                             "EXPLICIT_AUTHORIZATION_UNVERIFIED")


if __name__ == "__main__":
    unittest.main(verbosity=2)
