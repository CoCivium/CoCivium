"""Synthetic adversarial CoFocus causal attribution, no OS/window control."""
import copy
from datetime import datetime, timedelta, timezone
import unittest

from focus_causal_challenge import classify, SOURCE, SCHEMA

NOW = datetime(2026, 11, 12, 12, 28, tzinfo=timezone.utc)
ID_A = "other-sha256-" + "a" * 16
ID_B = "other-sha256-" + "b" * 16


def fixture():
    return {
        "schema": SOURCE,
        "state": "READ_ONLY_LOCAL_WINDOWS_SNAPSHOT",
        "observed_at_utc": (NOW - timedelta(seconds=30)).isoformat(),
        "raw_command_lines_emitted": False,
        "credentials_or_tokens_emitted": False,
        "no_registry_or_task_writes": True,
        "no_network_or_external_effect": True,
        "visible_popup_attribution": "NOT_TESTED",
        "observation_errors": [],
        "existing_scheduler_action_history": {
            "state": "OBSERVED_TASK_ACTION_HISTORY_ONLY",
            "window_minutes": 60,
            "max_events": 512,
            "events_read": 30,
            "truncated": False,
            "raw_event_xml_task_names_paths_arguments_or_instance_ids_emitted": False,
            "candidate_groups": [
                {
                    "task_identity": ID_A,
                    "launcher_class": "POWERSHELL7",
                    "task_category": "COALL_RELATED_CANDIDATE",
                    "starts_last_60m": 12,
                    "starts_last_15m": 5,
                    "starts_previous_15m": 3,
                    "paired_actions_le_3s": 8,
                    "console_flash_possible": True,
                    "popup_attributed": False,
                },
                {
                    "task_identity": ID_B,
                    "launcher_class": "CMD",
                    "task_category": "UNRELATED_OR_UNKNOWN",
                    "starts_last_60m": 7,
                    "starts_last_15m": 2,
                    "starts_previous_15m": 1,
                    "paired_actions_le_3s": 2,
                    "console_flash_possible": True,
                    "popup_attributed": False,
                }
            ],
        }
    }


class FocusTriageTests(unittest.TestCase):
    def test_candidate_rank_is_not_popup_proof(self):
        x = classify(fixture(), at_utc=NOW)
        self.assertEqual(x["schema"], SCHEMA)
        self.assertEqual(x["state"], "CANDIDATES_ONLY_CAUSALITY_UNPROVEN")
        self.assertEqual(x["candidate_count"], 2)
        self.assertEqual(x["candidate_launchers"][0]["opaque_task_ref"], ID_A)
        self.assertFalse(x["popup_source_attributed"])
        self.assertFalse(x["focus_theft_confirmed"])
        self.assertFalse(x["x2_runtime_repaired"])
        self.assertFalse(x["receiver_ack"])

    def test_raw_private_fields_never_pass_through(self):
        x = fixture()
        x["candidate_tasks"] = [{"task_name": "My private file paths and personal data"}]
        x["existing_scheduler_action_history"]["candidate_groups"][0]["secret_arguments"] = "-Token PRIVATE123"
        y = classify(x, at_utc=NOW)
        self.assertNotIn("PRIVATE123", str(y))
        self.assertNotIn("personal data", str(y))
        self.assertEqual(len(y["candidate_launchers"]), 2)

    def test_forged_popup_promotion_fails(self):
        x = fixture()
        x["existing_scheduler_action_history"]["candidate_groups"][0]["popup_attributed"] = True
        self.assertEqual(classify(x, at_utc=NOW)["reason"], "UNSUPPORTED_POPUP_CLAIM")

    def test_historical_stale_source_held(self):
        x = fixture()
        self.assertEqual(classify(x, at_utc=NOW+timedelta(hours=14))["state"], "HOLD_STALE_OR_FUTURE_SNAPSHOT")

    def test_future_source_held(self):
        x=fixture()
        x["observed_at_utc"]=(NOW+timedelta(minutes=3)).isoformat()
        self.assertEqual(classify(x, at_utc=NOW)["state"], "HOLD_STALE_OR_FUTURE_SNAPSHOT")

    def test_no_scheduler_events_not_no_popups(self):
        x=fixture()
        x["existing_scheduler_action_history"]["candidate_groups"]=[]
        x["existing_scheduler_action_history"]["events_read"]=0
        y=classify(x, at_utc=NOW)
        self.assertEqual(y["reason"], "NO_CONSOLE_ACTION_IN_HISTORY_NOT_NO_POPUP")
        self.assertFalse(y["focus_theft_confirmed"])

    def test_inaccessible_history_held(self):
        x=fixture()
        x["existing_scheduler_action_history"]["state"]="UNAVAILABLE_OR_EMPTY_UNQUALIFIED"
        self.assertEqual(classify(x, at_utc=NOW)["state"], "HOLD_SCHEDULER_HISTORY_UNAVAILABLE")

    def test_history_truncated_held(self):
        x=fixture()
        x["existing_scheduler_action_history"]["truncated"]=True
        self.assertEqual(classify(x, at_utc=NOW)["state"], "HOLD_PARTIAL_SCHEDULER_HISTORY")

    def test_history_parse_partial_held(self):
        x=fixture()
        x["observation_errors"]=["TASK_ACTION_HISTORY_PARTIAL_PARSE"]
        self.assertEqual(classify(x, at_utc=NOW)["state"], "HOLD_PARTIAL_SCHEDULER_HISTORY")

    def test_wrong_raw_event_privacy_rejected(self):
        x=fixture()
        x["existing_scheduler_action_history"]["raw_event_xml_task_names_paths_arguments_or_instance_ids_emitted"]=True
        self.assertEqual(classify(x, at_utc=NOW)["reason"], "RAW_TASK_EVENT_PRIVACY_UNQUALIFIED")

    def test_source_authority_cannot_be_forged(self):
        x=fixture()
        x["no_registry_or_task_writes"]=False
        self.assertEqual(classify(x, at_utc=NOW)["reason"], "SOURCE_EFFECTS_UNQUALIFIED")

    def test_duplicate_identity_rejected(self):
        x=fixture()
        x["existing_scheduler_action_history"]["candidate_groups"][1]["task_identity"]=ID_A
        self.assertEqual(classify(x, at_utc=NOW)["reason"], "CANDIDATE_IDENTITY_UNQUALIFIED")

    def test_plain_task_name_not_published(self):
        x=fixture()
        x["existing_scheduler_action_history"]["candidate_groups"][0]["task_identity"]="CoCivium private username"
        self.assertEqual(classify(x, at_utc=NOW)["reason"], "CANDIDATE_IDENTITY_UNQUALIFIED")

    def test_counts_must_be_consistent(self):
        x=fixture()
        x["existing_scheduler_action_history"]["candidate_groups"][0]["starts_last_15m"]=13
        self.assertEqual(classify(x, at_utc=NOW)["reason"], "COUNT_RELATIONS_INCONSISTENT")

    def test_bool_is_not_int_count(self):
        x=fixture()
        x["existing_scheduler_action_history"]["events_read"]=True
        self.assertEqual(classify(x, at_utc=NOW)["reason"], "EVENT_COUNT_UNQUALIFIED")

    def test_no_unsupported_launcher(self):
        x=fixture()
        x["existing_scheduler_action_history"]["candidate_groups"][0]["launcher_class"]="HTML"
        self.assertEqual(classify(x, at_utc=NOW)["reason"], "LAUNCHER_CLASS_UNQUALIFIED")

    def test_missing_history_held(self):
        x=fixture()
        del x["existing_scheduler_action_history"]
        self.assertEqual(classify(x, at_utc=NOW)["reason"], "HISTORY_MISSING_OR_UNKNOWN")

    def test_inverse_relations_explicit_and_incomplete(self):
        x=classify(fixture(), at_utc=NOW)
        self.assertEqual(len(x["relation_chain"]),4)
        self.assertEqual(len(x["inverse_challenges"]),4)
        self.assertTrue(all(z["evidence"] != "PROVEN" for z in x["relation_chain"]))

    def test_read_only_and_input_not_mutated(self):
        source=fixture()
        original=copy.deepcopy(source)
        classify(source, at_utc=NOW)
        self.assertEqual(source,original)


if __name__ == "__main__":
    unittest.main()
