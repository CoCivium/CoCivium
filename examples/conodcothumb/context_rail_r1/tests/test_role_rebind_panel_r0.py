"""Source/UX projection guards for existing CoContextRail CoLocal role rebind.

No browser/device/provider effects. The HTML snapshot is not X2 currentness.
"""
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
UI = ROOT / "examples/conodcothumb/context_rail_r1"
BOOT = json.loads((ROOT / "ai/session-bootstrap.json").read_text("utf-8"))
LANE = BOOT["role_scoped_rebind"]
SOURCE = ROOT / LANE["source"]["path"]
RAW = SOURCE.read_bytes()
INCIDENT = json.loads(RAW)
PAYLOAD_PATTERN = re.compile(r'<script type="application/json" id="coRoleRebindSnapshot">(\{.*?\})</script>', re.S)


def payload(page: Path):
    contents = page.read_text("utf-8")
    match = PAYLOAD_PATTERN.search(contents)
    if not match:
        raise ValueError("HOLD_REBIND_DATA_MISSING")
    return json.loads(match.group(1))


def gitblob(data):
    return hashlib.sha1(f"blob {len(data)}\0".encode("ascii") + data).hexdigest()


class TestRoleRebindPanel(unittest.TestCase):
    def setUp(self):
        self.template = (UI / "template.html").read_text("utf-8")
        self.index = (UI / "index.html").read_text("utf-8")
        self.data = payload(UI / "index.html")

    def test_pinned_source_is_actual_incident(self):
        self.assertEqual(gitblob(RAW), "7350c0bdc3661c6ccbc803df11a16c960da85675")
        self.assertEqual(LANE["source"]["git_blob_sha1"], gitblob(RAW))
        self.assertEqual(INCIDENT["state"], "PARTIAL_NATIVE_CONTAINMENT_VERIFIED__FOCUS_CURE_HELD")

    def test_embedded_snapshot_matches_bootstrap_and_incident(self):
        self.assertEqual(self.data["source_blob_sha1"], LANE["source"]["git_blob_sha1"])
        self.assertEqual(self.data["source_path"], LANE["source"]["path"])
        self.assertEqual(self.data["work_id"], INCIDENT["work_id"])
        self.assertEqual(self.data["source_observation_date"], LANE["source"]["source_observation_date"])

    def test_version_and_owner(self):
        self.assertEqual(self.data["schema"], "CoAll.CoContextRail.RoleRebindProjection.R0")
        self.assertEqual(self.data["owner"], LANE["incumbent_owner"])
        self.assertEqual(self.data["owner"], INCIDENT["current_rails"]["incident_owner"])

    def test_exact_relevant_role_whitelist(self):
        self.assertEqual(self.data["role_topics"], LANE["role_topics"])
        self.assertEqual(len(set(self.data["role_topics"])), 4)
        self.assertNotIn("BOOK_EDITOR", self.data["role_topics"])

    def test_no_effect_or_ack_promotion(self):
        self.assertIs(self.data["operation_authorized"], False)
        self.assertIs(self.data["live_x2_currentness_verified"], False)
        self.assertIs(self.data["external_receiver_ack"], False)

    def test_template_and_generated_html_have_exact_same_payload(self):
        self.assertEqual(self.data, payload(UI / "template.html"))

    def test_role_interface_is_off_by_default(self):
        self.assertIn('<option value="NONE">Other work (no X2 incident content)</option>', self.index)
        self.assertIn('id="rebindState" aria-live="polite">NOT REQUESTED', self.index)
        self.assertIn('id="rebindOwner" hidden', self.index)
        self.assertNotIn('id="rebindPanel" open', self.index)

    def test_role_inspect_is_explicit_only(self):
        self.assertIn("byId('rebindInspect').addEventListener('click',render)", self.index)
        self.assertNotIn("roleRebindAutoLaunch", self.index)
        self.assertIn("data.role_topics.includes(role)", self.index)
        self.assertIn("NO_RELEVANT_INCIDENT_CONTENT", self.index)

    def test_one_state_and_one_next_deed(self):
        self.assertIn("CoHereNow: ", self.index)
        self.assertIn(" CoNext: ", self.index)
        self.assertEqual(self.index.count('id="rebindInspect"'), 1)

    def test_safe_rendering(self):
        self.assertIn("byId('rebindNarrative').textContent", self.index)
        self.assertIn("byId('rebindIdentity').textContent", self.index)
        self.assertIn("HOLD_UNSAFE_PROJECTION", self.index)
        self.assertNotIn("rebindNarrative').innerHTML", self.index)

    def test_source_not_merged_with_private_workid(self):
        self.assertIn("Synthetic CoPre example only", self.index)
        self.assertIn("not live recovery", self.index.lower())
        self.assertIn("source snapshot", self.index.lower())
        self.assertIn("this is not live recovery", self.index.lower())

    def test_no_private_personal_data_inside_embedded_projection(self):
        raw=json.dumps(self.data)
        for term in ("D:\\CoCivium", "C:\\Users\\Owner", "@inseed.com",
                     "password", "access_token", "PRIVATE_CONVERSATION"):
            self.assertNotIn(term, raw)

    def test_existing_context_surface_still_present(self):
        for widget_id in ("workPreserve","workRecover","workRevoke","preview","context","question","gesture"):
            self.assertIn('id="'+widget_id+'"', self.index)

    def test_r1_evidence_never_assumes_cured_focus(self):
        self.assertIn("unverified", self.data["cohere"].lower())
        self.assertIn("No duplicate PS7 diagnostics", self.data["conext"])
        self.assertNotIn("X2_READY", self.data["cohere"])

    def test_offline_contract_preserved(self):
        self.assertIn("connect-src 'none'", self.index)
        self.assertIn("default-src 'none'", self.index)
        self.assertNotRegex(self.index, r"<script\s+src=")


if __name__ == "__main__":
    unittest.main()
