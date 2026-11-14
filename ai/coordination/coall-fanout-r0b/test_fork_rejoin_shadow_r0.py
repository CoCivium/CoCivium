"""Bounded synthetic provider-split and rejoin acceptance tests, no provider access."""
from __future__ import annotations

import copy
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "scripts"))
from CoAllForkRejoinShadowR0 import inspect_pair


def delta(key, sha, *, kind="PROPOSAL", effect_key=None):
    return {"delta_id": key, "sha256": sha * 64,
            "kind": kind, "effect_key": effect_key}


def view(surface, provider, head, *,
         visible="b", base="a", deltas=None, **changes):
    result = {
        "surface_id": surface, "provider_id": provider,
        "work_id": "work.same", "base_sha256": base * 64,
        "visible_sha256": visible * 64, "head_sha256": head * 64,
        "deltas": ([delta("delta.common", "d")] if deltas is None else deltas),
        "privacy": "SYNTHETIC_PUBLIC_SAFE", "observed_at": 1050,
        "source_access": "MANIFEST_ONLY", "receipt_state": "NOT_ESTABLISHED",
    }
    result.update(changes)
    return result


def pair():
    a = view("surface.x2", "provider.alpha", "c",
             deltas=[delta("delta.common", "d"), delta("delta.x2", "e")])
    b = view("surface.phone", "provider.alpha", "f",
             deltas=[delta("delta.common", "d"), delta("delta.phone", "f")])
    return a, b


def run(a=None, b=None, **kw):
    if a is None or b is None:
        default_a, default_b = pair()
        a = default_a if a is None else a
        b = default_b if b is None else b
    return inspect_pair(
        a, b, event=kw.pop("event", "VISIBLE_REJOIN_OBSERVED"),
        now=kw.pop("now", 1100), **kw
    )


class CoForkRejoinTests(unittest.TestCase):
    def held(self, result, reason):
        self.assertEqual(result["state"], "HOLD", result)
        self.assertIn(reason, result["holds"])
        self.assertEqual(result["effect"], "NONE")
        self.assertFalse(result["actuator_elected"])
        self.assertFalse(result["provider_delete_safe"])
        self.assertFalse(result["merged_transcript"])

    def test_views_appear_synced_but_two_unique_deltas_survive_as_candidates(self):
        r = run()
        self.assertTrue(r["visible_views_match"])
        self.assertFalse(r["heads_match"])
        self.assertEqual(r["state"], "SHADOW_FORK_DIFF_REQUIRES_SOURCE_READBACK")
        self.assertEqual(r["shared_delta_count"], 1)
        self.assertEqual(r["unique_left_delta_count"], 1)
        self.assertEqual(r["unique_right_delta_count"], 1)
        self.assertEqual(r["candidate_delta_refs"],
                         ["delta.common", "delta.phone", "delta.x2"])
        self.assertIn("VISIBLE_SYNC_ONLY_WITH_UNRESOLVED_CONTENT_DIFF", r["holds"])
        self.assertFalse(r["source_bytes_recovered"])
        self.assertFalse(r["provider_delete_safe"])

    def test_identical_manifest_never_implies_content_complete(self):
        a, b = pair()
        b["head_sha256"] = a["head_sha256"]
        b["deltas"] = copy.deepcopy(a["deltas"])
        r = run(a, b)
        self.assertEqual(r["state"], "SHADOW_VIEWS_MATCH_SOURCE_COVERAGE_UNKNOWN")
        self.assertEqual(r["global_completeness"], "UNKNOWN")
        self.assertEqual(r["receiver_readproof"], "NOT_ESTABLISHED")
        self.assertFalse(r["merged_transcript"])

    def test_two_providers_do_not_change_authority(self):
        a, b = pair()
        b["provider_id"] = "provider.beta"
        r = run(a, b)
        self.assertEqual(r["work_id"], "work.same")
        self.assertEqual(r["provider_independence"], "SCHEMA_ONLY_NO_LIVE_ADAPTER")
        self.assertFalse(r["anti_capture_proven"])
        self.assertFalse(r["coCivium_brand_grants_authority"])

    def test_two_synthetic_vendor_free_ids_are_supported(self):
        a, b = pair()
        a["provider_id"] = "independent.local"
        b["provider_id"] = "independent.federated"
        self.assertEqual(run(a, b)["surface_count"], 2)

    def test_clock_tick_does_not_create_handoff(self):
        r = run(event="TIMER_TICK")
        self.assertEqual(r["state"], "QUIET_NO_QUALIFIED_CHANGE")
        self.assertIn("TIMER_ALONE_CANNOT_TRIGGER_HANDOFF", r["holds"])
        self.assertEqual(r["candidate_delta_refs"], [])

    def test_exact_work_identity_is_required(self):
        a, b = pair()
        b["work_id"] = "work.other"
        self.held(run(a, b), "WORK_ID_CONFLICT")

    def test_exact_common_base_is_required(self):
        a, b = pair()
        b["base_sha256"] = "a" * 63 + "f"
        self.held(run(a, b), "COMMON_ANCESTOR_NOT_ESTABLISHED")

    def test_same_surface_cannot_fake_independent_view(self):
        a, b = pair()
        b["surface_id"] = a["surface_id"]
        self.held(run(a, b), "SAME_SURFACE_NOT_INDEPENDENT_VIEW")

    def test_duplicate_effect_intent_fenced_not_executed(self):
        a, b = pair()
        a["deltas"].append(delta("delta.action.x2", "c", kind="EFFECT_INTENT", effect_key="effect.mail"))
        b["deltas"].append(delta("delta.action.phone", "e", kind="EFFECT_INTENT", effect_key="effect.mail"))
        r = run(a, b)
        self.assertEqual(r["effect_intent_collisions"], 1)
        self.assertIn("DUPLICATE_EFFECT_INTENT_MUST_BE_FENCED_EXTERNALLY", r["holds"])
        self.assertEqual(r["duplicate_effects_executed"], 0)
        self.assertFalse(r["actuator_elected"])

    def test_same_delta_id_different_source_is_held(self):
        a, b = pair()
        b["deltas"][0]["sha256"] = "f" * 64
        r = run(a, b)
        self.assertEqual(r["state"], "HOLD_CONFLICTING_DELTA_REVISIONS")
        self.assertEqual(r["delta_conflict_count"], 1)
        self.assertIn("NEVER_LAST_WRITER_WINS", r["holds"])
        self.assertEqual(len(r["candidate_delta_refs"]), 3)

    def test_matching_visible_screens_do_not_override_disjoint_source_history(self):
        r = run()
        self.assertTrue(r["visible_views_match"])
        self.assertIn("PRESERVE_BOTH_SOURCE_BRANCHES", r["holds"])

    def test_out_of_date_metadata_is_held(self):
        a, b = pair()
        b["observed_at"] = 1
        self.held(run(a, b, max_age=100), "MISSING_OR_UNQUALIFIED_SOURCE_MANIFEST")

    def test_future_dated_observation_is_held(self):
        a, b = pair()
        b["observed_at"] = 2000
        self.held(run(a, b), "MISSING_OR_UNQUALIFIED_SOURCE_MANIFEST")

    def test_boolean_time_is_not_integer_time(self):
        self.held(run(now=True), "INVALID_TIME")

    def test_wrong_privacy_scope_fails_closed(self):
        a, b = pair()
        a["privacy"] = "PRIVATE_FULL_TEXT"
        self.held(run(a, b), "MISSING_OR_UNQUALIFIED_SOURCE_MANIFEST")

    def test_unexpected_transcript_payload_fails_closed(self):
        a, b = pair()
        a["messages"] = [{"content": "private text"}]
        r = run(a, b)
        self.held(r, "MISSING_OR_UNQUALIFIED_SOURCE_MANIFEST")
        self.assertNotIn("private text", str(r))

    def test_fake_receiver_ack_not_permitted(self):
        a, b = pair()
        b["receipt_state"] = "ACKED"
        self.held(run(a, b), "MISSING_OR_UNQUALIFIED_SOURCE_MANIFEST")

    def test_fake_source_bytes_not_permitted(self):
        a, b = pair()
        b["source_access"] = "COMPLETE_PROVIDER_EXPORT"
        self.held(run(a, b), "MISSING_OR_UNQUALIFIED_SOURCE_MANIFEST")

    def test_unbounded_number_of_deltas_held(self):
        a, b = pair()
        a["deltas"] = [delta("delta.%02d" % i, "c") for i in range(17)]
        self.held(run(a, b), "MISSING_OR_UNQUALIFIED_SOURCE_MANIFEST")

    def test_duplicate_delta_id_held(self):
        a, b = pair()
        a["deltas"].append(delta("delta.common", "d"))
        self.held(run(a, b), "MISSING_OR_UNQUALIFIED_SOURCE_MANIFEST")

    def test_no_effect_key_on_non_effect_intent(self):
        a, b = pair()
        a["deltas"][0]["effect_key"] = "effect.mail"
        self.held(run(a, b), "MISSING_OR_UNQUALIFIED_SOURCE_MANIFEST")

    def test_missing_effect_key_for_effect_intent(self):
        a, b = pair()
        a["deltas"].append(delta("delta.send", "c", kind="EFFECT_INTENT"))
        self.held(run(a, b), "MISSING_OR_UNQUALIFIED_SOURCE_MANIFEST")

    def test_deterministic_swapped_view_summaries(self):
        a, b = pair()
        x, y = run(a, b), run(b, a)
        self.assertEqual(x["candidate_delta_refs"], y["candidate_delta_refs"])
        self.assertEqual(x["state"], y["state"])
        self.assertEqual(x["unique_left_delta_count"], y["unique_right_delta_count"])
        self.assertEqual(x["unique_right_delta_count"], y["unique_left_delta_count"])

    def test_source_metadata_not_mutated(self):
        a, b = pair()
        orig = copy.deepcopy([a, b])
        run(a, b)
        self.assertEqual([a, b], orig)

    def test_no_provider_or_brand_can_grant_effect(self):
        r = run()
        self.assertFalse(r["coCivium_brand_grants_authority"])
        self.assertEqual(r["provider_action"], "NONE")
        self.assertFalse(r["public_release_authorized"])
        self.assertFalse(r["provider_delete_safe"])
        self.assertFalse(r["anti_capture_proven"])

    def test_no_provider_centric_primitives(self):
        code = (Path(__file__).resolve().parents[3] / "scripts" /
                "CoAllForkRejoinShadowR0.py").read_text(encoding="utf-8")
        for token in ("subprocess", "requests.", "socket", "http.client",
                      "urllib.request", "os.system", "git push", "delete_chat"):
            self.assertNotIn(token, code)


if __name__ == "__main__":
    unittest.main()
