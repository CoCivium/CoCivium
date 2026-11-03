"""Fail-closed regression checks for packet-derived runtime and --reset scope.

Uses only disposable TemporaryDirectory fixtures, no live routes or credentials.
"""
from __future__ import annotations

import copy
import json
import os
from pathlib import Path
import tempfile
import unittest

from CoAllFanoutR0 import init_runtime, load_packet


class RuntimeBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="coall-boundary-")
        self.addCleanup(self.tmp.cleanup)
        self.previous_cwd = Path.cwd()
        os.chdir(self.tmp.name)
        self.addCleanup(os.chdir, self.previous_cwd)
        self.root = Path.cwd()
        self.packet = {
            "schema": "CoAll.CanonicalTaskPacket.R0.v0.1",
            "task_id": "synthetic-task",
            "source": {"pointer": "test-only", "version": "fixture-v1"},
            "destinations": ["synthetic-local-a", "synthetic-local-b"],
            "runtime_relpath": ".coall-runtime/synthetic-task",
            "receiver_inventory": "inventory.json",
            "payload": {"type": "TEST_ONLY"},
        }
        inventory = {
            "schema": "CoAll.CoordinationReceiverInventory.R0.v0.1",
            "destinations": [
                {
                    "destination_id": name,
                    "availability": "AVAILABLE_AND_VERIFIED",
                    "authority": "AUTHORIZED_FOR_SYNTHETIC_TEST_ONLY",
                    "external_effects": False,
                    "behavior": "ACK_ALWAYS",
                }
                for name in self.packet["destinations"]
            ],
        }
        (self.root / "inventory.json").write_text(json.dumps(inventory), encoding="utf-8")
        self.packet_path = self.root / "packet.json"
        self.write_packet()

    def write_packet(self, update=None):
        packet = copy.deepcopy(self.packet)
        if update:
            packet.update(update)
        self.packet_path.write_text(json.dumps(packet), encoding="utf-8")

    def test_valid_task_scoped_path_resolves_inside_root(self):
        packet, runtime, inventory = load_packet(self.packet_path)
        self.assertEqual(runtime, self.root / ".coall-runtime" / "synthetic-task")
        self.assertEqual(packet["task_id"], "synthetic-task")
        self.assertEqual(len(inventory["destinations"]), 2)

    def test_parent_traversal_is_rejected_before_reset(self):
        outside = self.root / "outside-target"
        outside.mkdir()
        sentinel = outside / "important.keep"
        sentinel.write_text("do not remove", encoding="utf-8")
        self.write_packet({"runtime_relpath": ".coall-runtime/../outside-target"})
        with self.assertRaisesRegex(ValueError, "task-scoped"):
            init_runtime(self.packet_path, reset=True)
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "do not remove")

    def test_nested_parent_traversal_rejected(self):
        self.write_packet({"runtime_relpath": ".coall-runtime/../../other"})
        with self.assertRaises(ValueError):
            load_packet(self.packet_path)

    def test_wrong_task_identity_rejected(self):
        self.write_packet({"runtime_relpath": ".coall-runtime/some-other-task"})
        with self.assertRaisesRegex(ValueError, "task-scoped"):
            load_packet(self.packet_path)

    def test_absolute_runtime_rejected(self):
        self.write_packet({"runtime_relpath": str(self.root / "outside")})
        with self.assertRaisesRegex(ValueError, "repo-relative"):
            load_packet(self.packet_path)

    def test_runtime_root_symlink_rejected(self):
        outside = self.root / "outside-root"
        outside.mkdir()
        (self.root / ".coall-runtime").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "runtime root must not be a symlink"):
            load_packet(self.packet_path)

    def test_task_directory_symlink_rejected(self):
        outside = self.root / "outside-task"
        outside.mkdir()
        runtime_root = self.root / ".coall-runtime"
        runtime_root.mkdir()
        (runtime_root / "synthetic-task").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "runtime task path must not be a symlink"):
            load_packet(self.packet_path)

    def test_legitimate_reset_only_removes_scoped_synthetic_data(self):
        external = self.root / "other-data"
        external.mkdir()
        sentinel = external / "important.keep"
        sentinel.write_text("intact", encoding="utf-8")
        init_runtime(self.packet_path, reset=False)
        self.assertTrue((self.root / ".coall-runtime/synthetic-task/meta.json").is_file())
        init_runtime(self.packet_path, reset=True)
        self.assertTrue((self.root / ".coall-runtime/synthetic-task/meta.json").is_file())
        self.assertEqual(sentinel.read_text(encoding="utf-8"), "intact")


if __name__ == "__main__":
    unittest.main()
