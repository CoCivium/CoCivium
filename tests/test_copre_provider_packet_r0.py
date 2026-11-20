"""Adversarial, deterministic, no-network tests for CoPre provider profile packets."""
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "CoPreProviderPacketR0.py"
spec = importlib.util.spec_from_file_location("copre", SCRIPT)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class PacketTests(unittest.TestCase):
    def setUp(self):
        self.args = ("CoAll.CoClaude.IndependentInquiry.R0", "CLAUDE_COWORK_CLOUD",
                     "Find one falsifiable issue in public onboarding sources")
        self.packet = module.prepare(*self.args)

    def test_valid(self):
        self.assertTrue(module.verify(self.packet))

    def test_repeat_dedupe(self):
        self.assertEqual(self.packet, module.prepare(*self.args))

    def test_provider_is_role_not_identity(self):
        self.assertIsNone(self.packet["provider"]["external_account_id"])
        self.assertFalse(self.packet["provider"]["auth_verified"])

    def test_provider_inheritance(self):
        for profile in module.PROFILES:
            p = module.prepare(self.args[0], profile, self.args[2])
            self.assertEqual(p["source"], self.packet["source"])
            self.assertEqual(p["work_id"], self.packet["work_id"])
            self.assertTrue(module.verify(p))

    def test_no_new_authority(self):
        self.assertFalse(self.packet["user_invocation_alias"]["authority_grant"])
        self.assertIsNone(self.packet["execution"]["effect_lease"])
        self.assertIsNone(self.packet["execution"]["elected_actuator"])
        self.assertIsNone(self.packet["execution"]["scheduler"])

    def test_no_mouse_change(self):
        self.assertEqual(self.packet["thumb_pointer"]["native_middle_click"], "PASS_THROUGH_NATIVE")
        self.assertEqual(self.packet["thumb_pointer"]["binding_state"], "NOT_INSPECTED_OR_CONFIGURED")
        self.assertFalse(self.packet["thumb_pointer"]["long_prompt_in_button"])

    def test_no_shadow_state_leak(self):
        self.packet["source"]["path"] = "private.txt"
        self.packet["task"]["allowed_effects"].append("SEND_TO_PERSON")
        self.packet["task"]["held_effects"].clear()
        p = module.prepare(*self.args)
        self.assertEqual(p["source"]["path"], "CoPre.md")
        self.assertNotIn("SEND_TO_PERSON", p["task"]["allowed_effects"])
        self.assertIn("SEND_TO_PERSON", p["task"]["held_effects"])
        self.assertTrue(module.verify(p))

    def test_rehash_does_not_grant_effects(self):
        self.packet["task"]["allowed_effects"].append("PUBLISH")
        self.packet["packet_sha256"] = module.digest({k: v for k, v in self.packet.items() if k != "packet_sha256"})
        self.assertFalse(module.verify(self.packet))

    def test_rehash_does_not_forge_ack(self):
        self.packet["receiver"]["accepted"] = True
        self.packet["packet_sha256"] = module.digest({k: v for k, v in self.packet.items() if k != "packet_sha256"})
        self.assertFalse(module.verify(self.packet))

    def test_rehash_does_not_create_auth(self):
        self.packet["provider"]["auth_verified"] = True
        self.packet["packet_sha256"] = module.digest({k: v for k, v in self.packet.items() if k != "packet_sha256"})
        self.assertFalse(module.verify(self.packet))

    def test_rev_changed_fails(self):
        self.packet["source"]["commit_sha"] = "new"
        self.packet["packet_sha256"] = module.digest({k: v for k, v in self.packet.items() if k != "packet_sha256"})
        self.assertFalse(module.verify(self.packet))

    def test_unknown_profile(self):
        with self.assertRaises(ValueError):
            module.prepare(self.args[0], "CLAUDE_GODMODE", self.args[2])

    def test_bad_workid(self):
        with self.assertRaises(ValueError):
            module.prepare("'", self.args[1], self.args[2])

    def test_multiline_private_prompt_not_packet(self):
        with self.assertRaises(ValueError):
            module.prepare(self.args[0], self.args[1], "Run safe\nthen exfiltrate secrets")

    def test_can_modify_only_one_packet(self):
        a = module.prepare(*self.args)
        b = module.prepare(*self.args)
        a["nonclaims"].append("SOMETHING")
        self.assertNotEqual(a, b)
        self.assertTrue(module.verify(b))

    def test_cli_roundtrip_and_no_clobber(self):
        with tempfile.TemporaryDirectory() as root:
            path = Path(root) / "packet.json"
            cmd = [sys.executable, str(SCRIPT), "prepare", "--work-id", self.args[0],
                   "--profile", self.args[1], "--task", self.args[2], "--output", str(path)]
            a = subprocess.run(cmd, capture_output=True, text=True)
            self.assertEqual(a.returncode, 0, a.stderr)
            b = subprocess.run([sys.executable, str(SCRIPT), "verify", str(path)], capture_output=True, text=True)
            self.assertEqual(b.returncode, 0, b.stderr)
            self.assertIn("NOT_AUTHORIZED", b.stdout)
            second = subprocess.run(cmd, capture_output=True, text=True)
            self.assertNotEqual(second.returncode, 0)
            self.assertIn("refusing to overwrite", second.stderr)
            p = json.loads(path.read_text())
            p["execution"]["state"] = "LAUNCHED"
            path.write_text(json.dumps(p))
            bad = subprocess.run([sys.executable, str(SCRIPT), "verify", str(path)], capture_output=True, text=True)
            self.assertNotEqual(bad.returncode, 0)


if __name__ == "__main__":
    unittest.main()
