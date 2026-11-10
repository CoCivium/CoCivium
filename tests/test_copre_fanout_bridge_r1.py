"""CoPreGeneric -> existing CoAllFanoutR0 synthetic boundary proof.

Two deterministic, repo-local projections with separate receipts and recovery.
No network, external receivers, public publication, or system-wide authority.
Run: python3 -B tests/test_copre_fanout_bridge_r1.py
"""
import copy
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "ai/continuity/copre-synth-bio-gd-coterms-r1-20261109.json"
HUMAN = ROOT / "docs/CoPreGeneric/CoPre_SynthBio_Gd_CoTerms_Candidate_R1_20261109.md"
PACKET_TEMPLATE = ROOT / "ai/coordination/coall-fanout-r0/task-packet.json"
INVENTORY_TEMPLATE = ROOT / "ai/coordination/coall-fanout-r0/receiver-inventory.json"
FANOUT_RUNNER = ROOT / "scripts/CoAllFanoutR0.py"
DESTINATIONS = ("synthetic-local-a", "synthetic-local-b")


def git_blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()


def json_write(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bound_packet(source_bytes, human_text, packet, inventory):
    """Reject source/projection drift before any synthetic local dispatch."""
    obj = json.loads(source_bytes)
    work_id = obj["work_id"]
    labels = [t["label"] for t in obj["terms"]]
    links = obj["relations"]
    if len(labels) != 72 or len(links) != 22 or len(set(labels)) != 72:
        raise ValueError("CoPre source content is not the qualified 72/22 structure")
    if obj.get("effect_authority") != "NONE":
        raise ValueError("CoPre source unexpectedly grants effects")
    if not all("**" + label + "**" in human_text for label in labels):
        raise ValueError("Human projection omitted a source term")
    if any(t.get("status") != "UNQUALIFIED_PUBLIC_CANDIDATE" for t in obj["terms"]):
        raise ValueError("Unapproved candidate promotion")
    source_rel = SOURCE.relative_to(ROOT).as_posix()
    human_rel = HUMAN.relative_to(ROOT).as_posix()
    source_digest = git_blob_sha(source_bytes)
    packet["task_id"] = "copre-r1-447-source-bound-fanout"
    packet["source"] = {
        "pointer": source_rel,
        "version": "git-blob:" + source_digest,
        "source_type": "PUBLIC_REPOSITORY_SOURCE_CANDIDATE",
        "work_id": work_id,
    }
    packet["intent"] = "Synthetic CoPre source-bound two-destination fanout/recovery without real outreach"
    packet["owner"] = "SYNTHETIC_TEST_ONLY_NOT_HUMAN_DELEGATION"
    packet["receiver_inventory"] = "receiver-inventory.json"
    packet["runtime_relpath"] = ".coall-runtime/copre-r1-fanout"
    packet["destinations"] = list(DESTINATIONS)
    packet["scope"]["permissions"] = [
        "READ_LOCAL_TEST_FIXTURES", "WRITE_LOCAL_SYNTHETIC_RUNTIME",
        "WRITE_LOCAL_SYNTHETIC_RECEIPTS",
    ]
    packet["scope"]["forbidden"] = [
        "EXTERNAL_EMAIL_SEND", "EXTERNAL_MESSAGE_SEND", "CREDENTIAL_ACCESS",
        "DEVICE_MUTATION", "CANON_PROMOTION", "PUBLIC_DEPLOYMENT",
    ]
    packet["payload"] = {
        "type": "COPRE_R1_SOURCE_BOUND_CANDIDATE",
        "work_id": work_id,
        "source_git_blob_sha": source_digest,
        "projection_refs": {
            "synth": source_rel, "bio": human_rel,
        },
        "expected_terms": 72,
        "expected_relations": 22,
        "projection_loss": "NOT_INDEPENDENTLY_EVALUATED",
        "dissent": "PRESERVE",
        "effect_authority": "NONE",
        "receiver_authority": "SYNTHETIC_LOCAL_TEST_ONLY",
        "receiver_readproof": "NOT_ESTABLISHED",
    }
    inventory["destinations"] = [
        d for d in inventory["destinations"] if d["destination_id"] in DESTINATIONS
    ]
    if {d["destination_id"] for d in inventory["destinations"]} != set(DESTINATIONS):
        raise ValueError("Unqualified synthetic destinations")
    if not all(d["external_effects"] is False for d in inventory["destinations"]):
        raise ValueError("External effect receiver detected")
    return packet, inventory


def runner(cmd, packet_path, cwd, expect_success=True):
    proc = subprocess.run(
        [sys.executable, "-B", str(FANOUT_RUNNER), cmd, "--packet", str(packet_path)],
        cwd=cwd, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=20,
        check=False,
    )
    if expect_success and proc.returncode:
        raise AssertionError(cmd + " failed: " + proc.stderr[-1400:])
    if not expect_success:
        return proc
    return json.loads(proc.stdout)


class CoPreBoundedFanout(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source_bytes = SOURCE.read_bytes()
        cls.human_text = HUMAN.read_text(encoding="utf-8")
        cls.base_packet = json.loads(PACKET_TEMPLATE.read_text(encoding="utf-8"))
        cls.base_inventory = json.loads(INVENTORY_TEMPLATE.read_text(encoding="utf-8"))

    def fixture(self, directory):
        packet, inventory = bound_packet(
            self.source_bytes, self.human_text,
            copy.deepcopy(self.base_packet), copy.deepcopy(self.base_inventory),
        )
        root = Path(directory)
        inventory_path = root / "receiver-inventory.json"
        packet_path = root / "packet.json"
        json_write(inventory_path, inventory)
        json_write(packet_path, packet)
        return packet_path, packet, inventory

    def test_source_drifts_fail_before_dispatch(self):
        changed = self.source_bytes.replace(b'"effect_authority": "NONE"',
                                             b'"effect_authority": "ALL"', 1)
        self.assertNotEqual(changed, self.source_bytes)
        with self.assertRaises(ValueError):
            bound_packet(changed, self.human_text, copy.deepcopy(self.base_packet),
                         copy.deepcopy(self.base_inventory))
        with self.assertRaises(ValueError):
            bound_packet(self.source_bytes, self.human_text.replace("**CoClaimAltitude+**", ""),
                         copy.deepcopy(self.base_packet), copy.deepcopy(self.base_inventory))

    def test_two_synthetic_receivers_recover_without_relay_or_duplicate(self):
        with tempfile.TemporaryDirectory(prefix="copre-r1-fanout-") as tmp:
            packet_path, packet, inventory = self.fixture(tmp)
            root = Path(tmp)
            first = runner("init", packet_path, root)
            self.assertEqual(first["state"], "INITIALIZED")
            dispatched = runner("dispatch", packet_path, root)
            self.assertEqual(dispatched["state"], "DISPATCH_CYCLE_COMPLETE")
            partial = runner("reconcile", packet_path, root)
            self.assertEqual(partial["overall_state"], "PARTIAL_RECOVERABLE")
            by_id = {d["destination_id"]: d for d in partial["destinations"]}
            self.assertEqual(by_id[DESTINATIONS[0]]["state"], "ACKED")
            self.assertEqual(by_id[DESTINATIONS[1]]["state"], "RETRY_QUEUED")

            # Each command is a fresh OS process, and recovery reads durable local receipts.
            recovery = runner("recover", packet_path, root)
            self.assertEqual(recovery["before_state"], "PARTIAL_RECOVERABLE")
            self.assertEqual(recovery["after_state"], "COMPLETE_ACKED_LOCAL")
            accepted = runner("verify", packet_path, root)
            self.assertEqual(accepted["state"],
                             "PASS_SYNTHETIC_TWO_DESTINATION_FANOUT_AND_RECOVERY")
            self.assertTrue(all(accepted["checks"].values()))
            before_replay = accepted["final_status"]["receipt_count"]
            repeated = runner("dispatch", packet_path, root)
            self.assertEqual([r["result"] for r in repeated["results"]],
                             ["ALREADY_ACKED", "ALREADY_ACKED"])
            after_replay = runner("reconcile", packet_path, root)
            self.assertEqual(after_replay["receipt_count"], before_replay)
            self.assertTrue(all(v == 0 for v in after_replay["effects"].values()))

            # Receiver artifacts are local projection copies, never actual receiver pickup.
            runtime = root / packet["runtime_relpath"]
            for destination_id in DESTINATIONS:
                materialized = runtime / "destinations" / destination_id / (
                    packet["task_id"] + ".json"
                )
                projection = json.loads(materialized.read_text(encoding="utf-8"))
                self.assertEqual(projection["source"], packet["source"])
                self.assertEqual(projection["payload"], packet["payload"])
                self.assertEqual(projection["authority"], "SYNTHETIC_LOCAL_TEST_ONLY")
                self.assertEqual(projection["payload"]["effect_authority"], "NONE")
                self.assertEqual(projection["payload"]["receiver_readproof"], "NOT_ESTABLISHED")

    def test_external_destination_refused_without_effect(self):
        with tempfile.TemporaryDirectory(prefix="copre-r1-deny-") as tmp:
            packet_path, packet, inventory = self.fixture(tmp)
            inventory["destinations"][0]["external_effects"] = True
            json_write(Path(tmp) / "receiver-inventory.json", inventory)
            result = runner("init", packet_path, Path(tmp), expect_success=False)
            self.assertNotEqual(result.returncode, 0)
            self.assertFalse((Path(tmp) / packet["runtime_relpath"]).exists())


if __name__ == "__main__":
    unittest.main()
