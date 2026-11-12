"""Public source-only logical autocycle tests: never start X2 or provider tabs."""
from __future__ import annotations
import copy
import importlib.util
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from CoSessionAutoTurnR1 import compile_turn, WORKSET, OUT_SCHEMA

NOW = "2026-11-12T20:30:00Z"
HEAD = "a" * 40
RUN = "43299999999"
ATTEMPT = "1"


class AutoTurnTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        workset = json.loads((REPO / WORKSET).read_text(encoding="utf-8"))
        self.items = workset["work_items"]
        for rel in [WORKSET] + [w["source_path"] for w in self.items]:
            p = self.root / rel
            p.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(REPO / rel, p)

    def edit(self, rel, transform):
        p = self.root / rel
        data = json.loads(p.read_text(encoding="utf-8"))
        transform(data)
        p.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def turn(self):
        return compile_turn(self.root, NOW, RUN, ATTEMPT, HEAD)

    def test_three_source_contexts_qualified(self):
        r = self.turn()
        self.assertEqual(r["schema"], OUT_SCHEMA)
        self.assertEqual(r["state"], "ONE_SOURCE_WORKID_RECHECKED_AND_LOGICAL_FLEET_PROJECTED")
        self.assertEqual(r["co_speedo"]["qualified_public_source_objects"], 3)
        self.assertEqual(r["co_speedo"]["bounded_logical_work_contexts"], 3)

    def test_one_elected_workid_and_two_shadow_only(self):
        r = self.turn()
        self.assertEqual(r["elected"]["role"], "X2_DESKTOP_RECOVERY")
        self.assertEqual(len(r["other_workids"]), 2)
        self.assertTrue(all(x["state"] == "LOGICAL_SHADOW_NOT_MATERIALIZED" for x in r["other_workids"]))

    def test_actual_lifecycle_compiler_reused(self):
        r = self.turn()
        ledger = r["shadow_ledger"]
        self.assertEqual(ledger["state"], "SHADOW_LEDGER_COMPILED__NO_PROVIDER_MUTATION")
        self.assertEqual(len(ledger["sessions"]), 3)
        self.assertEqual([s["projection"] for s in ledger["sessions"]],
                         ["SUCCESSOR_READY", "WAITING", "DEGRADED"])

    def test_no_provider_or_native_effect(self):
        r = self.turn()
        self.assertFalse(r["receiver_ack"])
        self.assertFalse(r["external_work_effect_claimed"])
        self.assertEqual(r["elected"]["performed_effect"], "VERIFY_PUBLIC_SOURCE_BYTES_ONLY")
        self.assertEqual(r["elected"]["owner_effect_lease"], "NONE")
        self.assertEqual(r["co_speedo"]["x2_processes_started"], 0)
        self.assertEqual(r["co_speedo"]["provider_tabs_cycled"], 0)
        self.assertTrue(all(x == 0 for x in r["shadow_ledger"]["effects"].values()))

    def test_currentness_not_inferred(self):
        r = self.turn()
        self.assertIsNone(r["co_speedo"]["current_native_x2_worker_count"])
        self.assertIsNone(r["co_speedo"]["current_focus_interruptions_per_minute"])
        self.assertIsNone(r["co_needle"]["predicted_productivity_improvement"])

    def test_stable_output_and_no_source_mutation(self):
        before = {p.relative_to(self.root):p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(self.turn(), self.turn())
        after = {p.relative_to(self.root):p.read_bytes() for p in self.root.rglob("*") if p.is_file()}
        self.assertEqual(before, after)

    def test_unpinned_source_state_held(self):
        rel=self.items[0]["source_path"]
        self.edit(rel, lambda x:x.update(state="FOCUS_CURED"))
        with self.assertRaisesRegex(ValueError,"HOLD_SOURCE_IDENTITY_OR_STATE_DRIFT"):self.turn()

    def test_mismatched_workid_held(self):
        rel=self.items[1]["source_path"]
        self.edit(rel, lambda x:x.update(work_id="Different"))
        with self.assertRaisesRegex(ValueError,"HOLD_SOURCE_IDENTITY_OR_STATE_DRIFT"):self.turn()

    def test_duplicate_workid_held(self):
        self.edit(WORKSET, lambda x:x["work_items"][1].update(work_id=x["work_items"][0]["work_id"]))
        with self.assertRaisesRegex(ValueError,"HOLD_WORKID_IDENTITY_COLLISION"):self.turn()

    def test_duplicate_priority_held(self):
        self.edit(WORKSET, lambda x:x["work_items"][1].update(priority=x["work_items"][0]["priority"]))
        with self.assertRaisesRegex(ValueError,"HOLD_PRIORITY_BOUNDS_OR_COLLISION"):self.turn()

    def test_unknown_authority_held(self):
        self.edit(WORKSET, lambda x:x["work_items"][0].update(native_effects_authorized=True))
        with self.assertRaisesRegex(ValueError,"HOLD_EFFECT_AUTHORITY"):self.turn()

    def test_illegal_external_receiver_ack_held(self):
        self.edit(WORKSET, lambda x:x["work_items"][0].update(external_receiver_pickup=True))
        with self.assertRaisesRegex(ValueError,"HOLD_EFFECT_AUTHORITY"):self.turn()

    def test_private_source_escape_held(self):
        self.edit(WORKSET, lambda x:x["work_items"][0].update(source_path="../private-chat.json"))
        with self.assertRaisesRegex(ValueError,"HOLD_SOURCE_SCOPE_COLLISION"):self.turn()

    def test_source_file_missing_holds(self):
        (self.root / self.items[0]["source_path"]).unlink()
        with self.assertRaisesRegex(ValueError,"HOLD_SOURCE_MISSING_OR_LINKED"):self.turn()

    def test_future_source_holds(self):
        rel=self.items[1]["source_path"]
        self.edit(rel, lambda x:x.update(observed_utc="2040-11-12T20:28:00Z"))
        with self.assertRaisesRegex(ValueError,"HOLD_SOURCE_FROM_FUTURE"):self.turn()

    def test_owner_redirect_holds(self):
        self.edit(WORKSET, lambda x:x["work_items"][0].update(owner="https://example.net/new-authority"))
        with self.assertRaisesRegex(ValueError,"HOLD_OWNER_SCOPE"):self.turn()

    def test_evidence_class_inflation_holds(self):
        self.edit(WORKSET, lambda x:x["work_items"][2].update(expected_state="X2_DEPLOYED"))
        with self.assertRaisesRegex(ValueError,"HOLD_SOURCE_IDENTITY_OR_STATE_DRIFT"):self.turn()

    def test_no_global_chats_or_manual_private_context_exposed(self):
        s=json.dumps(self.turn())
        for v in ("D:\\CoCivium","C:\\Users\\Owner","@inseed.com","access_token","PRIVATE_CHAT_LOG"):
            self.assertNotIn(v,s)

    def test_repeat_source_turn_has_zero_new_work(self):
        # Two separate run IDs with unchanged byte-verified source objects
        # must not be credited as discovery or independently useful work.
        from CoSessionAutoTurnR1 import compare_public_source_turns
        earlier = self.turn()
        later = compile_turn(self.root, "2026-11-12T21:30:00Z", "43300000000", "1", HEAD)
        delta = compare_public_source_turns(earlier, later)
        self.assertEqual(delta["classification"], "UNCHANGED_PUBLIC_SOURCES_RECHECK")
        self.assertEqual(delta["source_digests_changed"], 0)
        self.assertEqual(delta["verified_useful_work_outcomes"], 0)
        self.assertEqual(delta["novel_public_source_objects"], 0)
        self.assertFalse(delta["receiver_ack"])

    def test_changed_public_source_does_not_infer_useful_work(self):
        from CoSessionAutoTurnR1 import compare_public_source_turns
        earlier = self.turn()
        rel = self.items[1]["source_path"]
        self.edit(rel, lambda x: x["nonclaims"].append("SOURCE_REVIEW_CHANGE_ONLY"))
        later = compile_turn(self.root, "2026-11-12T21:30:00Z", "43300000000", "1", HEAD)
        delta = compare_public_source_turns(earlier, later)
        self.assertEqual(delta["classification"],
                         "PUBLIC_SOURCE_DIGEST_CHANGE_REQUIRES_SEMANTIC_REVIEW")
        self.assertEqual(delta["source_digests_changed"], 1)
        self.assertEqual(delta["verified_useful_work_outcomes"], 0)
        self.assertIsNone(delta["novel_public_source_objects"])

    def test_same_run_replay_not_an_independent_execution(self):
        from CoSessionAutoTurnR1 import compare_public_source_turns
        earlier = self.turn()
        delta = compare_public_source_turns(earlier, earlier)
        self.assertEqual(delta["classification"], "SAME_RUN_REPLAY_NOT_NEW_EVIDENCE")
        self.assertEqual(delta["verified_useful_work_outcomes"], 0)

    def test_changed_workset_requires_rebase_not_false_delta(self):
        from CoSessionAutoTurnR1 import compare_public_source_turns
        earlier = self.turn()
        self.edit(WORKSET, lambda x: x["work_items"][2].update(
            next_safe_deed="ANOTHER_PUBLIC_READ_ONLY_PROPOSAL"))
        later = compile_turn(self.root, "2026-11-12T21:30:00Z", "43300000000", "1", HEAD)
        with self.assertRaisesRegex(ValueError, "HOLD_DELTA_WORKSET_IDENTITY_DRIFT"):
            compare_public_source_turns(earlier, later)

    def test_source_delta_rejects_forged_effect_ack(self):
        from CoSessionAutoTurnR1 import compare_public_source_turns
        earlier = self.turn()
        earlier["receiver_ack"] = True
        with self.assertRaisesRegex(ValueError, "HOLD_DELTA_EFFECT_AUTHORITY"):
            compare_public_source_turns(earlier, self.turn())

    def test_source_delta_rejects_corrupt_digest(self):
        from CoSessionAutoTurnR1 import compare_public_source_turns
        earlier = self.turn()
        earlier["sources"][0]["source_sha256"] = "not-a-digest"
        with self.assertRaisesRegex(ValueError, "HOLD_DELTA_SOURCE_SHAPE"):
            compare_public_source_turns(earlier, self.turn())

    def test_reject_invalid_execution_identifiers(self):
        for run,attempt,head in [("0","1",HEAD),("1","0",HEAD),("1","1","BAD")]:
            with self.assertRaisesRegex(ValueError,"HOLD_"):
                compile_turn(self.root,NOW,run,attempt,head)


if __name__ == "__main__":
    unittest.main()
