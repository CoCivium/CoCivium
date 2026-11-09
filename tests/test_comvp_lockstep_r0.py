"""CoMVP+ R0 tests: usable source heads, cohort locks and fail-closed rollback.

All fixtures are local and synthetic. They do not certify real installed
X2 prodlets, functional user MVPs, reviewer independence or public release.
"""
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

from scripts.CoMVPLockStepR0 import CoMVPSlots, Held


class CoMVPTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.db = self.root / "release-heads.sqlite"
        self.store = CoMVPSlots(self.db, self.root)

    def tearDown(self):
        self.store.close()
        self.tmp.cleanup()

    def candidate(self, slot="orb", label="one", deps=(), fail=False, qualify=True):
        data = slot + ":" + label
        name = slot + "-" + label
        artifact = name + ".txt"
        test = name + "-test.py"
        (self.root / artifact).write_text(data, encoding="utf-8")
        if fail:
            script = "raise SystemExit(9)\n"
        else:
            script = ("from pathlib import Path\n"
                      "assert Path(" + repr(artifact) + ").read_text() == " + repr(data) + "\n")
        (self.root / test).write_text(script, encoding="utf-8")
        result = self.store.stage(slot, artifact, test, deps)
        rev = result["revision"]
        if qualify:
            qualification = self.store.qualify(slot, rev)
            self.assertEqual(qualification["state"],
                             "HELD_TEST_FAILED" if fail else "SOURCE_TESTED_LOCAL_ONLY")
        return rev

    def activate(self, slot, rev, old=None):
        return self.store.promote_cohort({slot: rev}, {slot: old})

    def test_staging_never_displaces_active_head(self):
        rev = self.candidate(qualify=False)
        self.assertEqual(self.store.active(), {})
        with self.assertRaisesRegex(Held, "UNQUALIFIED_RELEASE_VERSION"):
            self.activate("orb", rev)
        self.assertEqual(self.store.active(), {})

    def test_qualifying_does_not_displace_active_head(self):
        self.candidate()
        self.assertEqual(self.store.active(), {})

    def test_one_source_head_promotes_with_local_scope(self):
        rev = self.candidate()
        out = self.activate("orb", rev)
        self.assertEqual(out["active"]["orb"], rev)
        self.assertFalse(out["receiver_qualified"])
        self.assertFalse(out["native_runtime_updated"])

    def test_failed_candidate_keeps_prior_useable_source_head(self):
        old = self.candidate()
        self.activate("orb", old)
        broken = self.candidate(label="broken", fail=True)
        with self.assertRaisesRegex(Held, "UNQUALIFIED_RELEASE_VERSION"):
            self.activate("orb", broken, old)
        self.assertEqual(self.store.active()["orb"], old)

    def test_independent_prodlets_advance_without_global_barrier(self):
        orb1 = self.candidate("orb", "one")
        self.activate("orb", orb1)
        worker1 = self.candidate("worker", "one")
        self.activate("worker", worker1)
        orb2 = self.candidate("orb", "two")
        self.activate("orb", orb2, orb1)
        self.assertEqual(self.store.active(), {"orb": orb2, "worker": worker1})

    def test_dependency_prevents_half_upgraded_system(self):
        engine1 = self.candidate("engine", "one")
        ui1 = self.candidate("ui", "one", deps=(("engine", engine1),))
        self.store.promote_cohort({"engine": engine1, "ui": ui1},
                                  {"engine": None, "ui": None})
        engine2 = self.candidate("engine", "two")
        with self.assertRaisesRegex(Held, "COHORT_DEPENDENCY_INCOMPATIBLE"):
            self.activate("engine", engine2, engine1)
        self.assertEqual(self.store.active(), {"engine": engine1, "ui": ui1})

    def test_compatible_pair_advances_atomically(self):
        engine1 = self.candidate("engine", "one")
        ui1 = self.candidate("ui", "one", deps=(("engine", engine1),))
        self.store.promote_cohort({"engine": engine1, "ui": ui1},
                                  {"engine": None, "ui": None})
        engine2 = self.candidate("engine", "two")
        ui2 = self.candidate("ui", "two", deps=(("engine", engine2),))
        out = self.store.promote_cohort({"engine": engine2, "ui": ui2},
                                        {"engine": engine1, "ui": ui1})
        self.assertEqual(out["active"], {"engine": engine2, "ui": ui2})
        self.assertEqual(len(out["changed"]), 2)

    def test_failed_cohort_upgrade_is_all_or_nothing(self):
        engine1 = self.candidate("engine", "one")
        ui1 = self.candidate("ui", "one", deps=(("engine", engine1),))
        self.store.promote_cohort({"engine": engine1, "ui": ui1},
                                  {"engine": None, "ui": None})
        engine2 = self.candidate("engine", "two")
        ui2 = self.candidate("ui", "broken", deps=(("engine", engine2),), fail=True)
        with self.assertRaisesRegex(Held, "UNQUALIFIED_RELEASE_VERSION"):
            self.store.promote_cohort({"engine": engine2, "ui": ui2},
                                      {"engine": engine1, "ui": ui1})
        self.assertEqual(self.store.active(), {"engine": engine1, "ui": ui1})

    def test_rollback_requires_compatible_cohort(self):
        e1 = self.candidate("engine", "one")
        u1 = self.candidate("ui", "one", deps=(("engine", e1),))
        self.store.promote_cohort({"engine": e1, "ui": u1},
                                  {"engine": None, "ui": None})
        e2 = self.candidate("engine", "two")
        u2 = self.candidate("ui", "two", deps=(("engine", e2),))
        self.store.promote_cohort({"engine": e2, "ui": u2},
                                  {"engine": e1, "ui": u1})
        with self.assertRaisesRegex(Held, "COHORT_DEPENDENCY_INCOMPATIBLE"):
            self.activate("engine", e1, e2)
        out = self.store.promote_cohort({"engine": e1, "ui": u1},
                                        {"engine": e2, "ui": u2})
        self.assertEqual(out["active"], {"engine": e1, "ui": u1})
        self.assertEqual(out["changed"]["engine"]["from"], e2)

    def test_stale_writer_cannot_clobber_current_head(self):
        one = self.candidate()
        two = self.candidate(label="two")
        self.activate("orb", one)
        peer = CoMVPSlots(self.db, self.root)
        try:
            self.activate("orb", two, one)
            with self.assertRaisesRegex(Held, "STALE_RELEASE_HEAD"):
                peer.promote_cohort({"orb": one}, {"orb": one})
            self.assertEqual(peer.active()["orb"], two)
        finally:
            peer.close()

    def test_qualify_then_mutate_artifact_holds_release(self):
        one = self.candidate()
        (self.root / "orb-one.txt").write_text("surreptitious edit")
        with self.assertRaisesRegex(Held, "ACTIVE_SOURCE_CHANGED"):
            self.activate("orb", one)
        self.assertFalse(self.store.active())

    def test_mutate_test_after_qualification_holds_release(self):
        one = self.candidate()
        (self.root / "orb-one-test.py").write_text("pass\n# changed")
        with self.assertRaisesRegex(Held, "ACTIVE_SOURCE_CHANGED"):
            self.activate("orb", one)

    def test_missing_dependency_does_not_create_head(self):
        rev = self.candidate("ui", "one", deps=(("engine", "a" * 64),))
        with self.assertRaisesRegex(Held, "COHORT_DEPENDENCY_INCOMPATIBLE"):
            self.activate("ui", rev)
        self.assertEqual(self.store.active(), {})

    def test_duplicate_manifest_for_one_revision_refused(self):
        rev = self.candidate(qualify=False)
        (self.root / "other-test.py").write_text("pass\n")
        with self.assertRaisesRegex(Held, "REVISION_REGISTRATION_CONFLICT"):
            self.store.stage("orb", "orb-one.txt", "other-test.py")
        self.assertEqual(self.store.active(), {})

    def test_bad_source_path_refused(self):
        with self.assertRaisesRegex(Held, "SOURCE_OUTSIDE_ROOT"):
            self.store.stage("orb", "../out-of-root.txt", "orb-one-test.py")

    def test_empty_cas_expectation_refused(self):
        rev = self.candidate()
        with self.assertRaisesRegex(Held, "MISSING_CAS_EXPECTATIONS"):
            self.store.promote_cohort({"orb": rev}, {})

    def test_duplicate_dependency_refused(self):
        (self.root / "orb-one.txt").write_text("orb:one")
        (self.root / "orb-one-test.py").write_text("pass\n")
        with self.assertRaisesRegex(Held, "INVALID_DEPENDENCY_IDENTITY"):
            self.store.stage("orb", "orb-one.txt", "orb-one-test.py",
                             (("engine", "a" * 64), ("engine", "b" * 64)))

    def test_no_op_promotion_does_not_mint_extra_event(self):
        rev = self.candidate()
        self.activate("orb", rev)
        first = self.store.audit_chain()["events_checked"]
        out = self.store.promote_cohort({"orb": rev}, {"orb": rev})
        self.assertEqual(out["changed"], {})
        self.assertEqual(self.store.audit_chain()["events_checked"], first)

    def test_chain_detects_manual_row_tamper(self):
        rev = self.candidate()
        self.activate("orb", rev)
        self.store.db.execute("UPDATE events SET action='FAKE' WHERE id=1")
        with self.assertRaisesRegex(Held, "EVENT_DIGEST_MISMATCH"):
            self.store.audit_chain()

    def test_reopen_database_recovers_exact_heads(self):
        rev = self.candidate()
        self.activate("orb", rev)
        self.store.close()
        reader = subprocess.run([
            sys.executable, "-B", "-c",
            "import json,sys; from scripts.CoMVPLockStepR0 import CoMVPSlots; "
            "s=CoMVPSlots(sys.argv[1],sys.argv[2]); "
            "print(json.dumps({'active':s.active(),'audit':s.audit_chain()})); s.close()",
            str(self.db), str(self.root)
        ], cwd=str(Path(__file__).resolve().parents[1]),
           capture_output=True, text=True, timeout=8, check=True)
        recovered = json.loads(reader.stdout)
        self.assertEqual(recovered["active"]["orb"], rev)
        self.assertGreater(recovered["audit"]["events_checked"], 1)
        self.store = CoMVPSlots(self.db, self.root)

    def test_failed_test_cannot_promote_even_after_reentry(self):
        bad = self.candidate(label="broken", fail=True)
        self.assertEqual(self.store.qualify("orb", bad)["state"], "HELD_TEST_FAILED")
        with self.assertRaisesRegex(Held, "UNQUALIFIED_RELEASE_VERSION"):
            self.activate("orb", bad)

    def test_source_test_timeout_is_held(self):
        (self.root / "orb-slow.txt").write_text("orb:slow")
        (self.root / "orb-slow-test.py").write_text("import time\ntime.sleep(1)\n")
        rev = self.store.stage("orb", "orb-slow.txt", "orb-slow-test.py")["revision"]
        with patch("scripts.CoMVPLockStepR0.MAX_TEST_SEC", 0.02):
            self.assertEqual(self.store.qualify("orb", rev)["state"], "HELD_TEST_TIMEOUT")
        self.assertEqual(self.store.active(), {})

    def test_rollback_requires_exact_staged_source(self):
        one = self.candidate()
        two = self.candidate(label="two")
        self.activate("orb", one)
        self.activate("orb", two, one)
        (self.root / "orb-one.txt").write_text("broken old source")
        with self.assertRaisesRegex(Held, "ACTIVE_SOURCE_CHANGED"):
            self.activate("orb", one, two)
        self.assertEqual(self.store.active()["orb"], two)

    def cli(self, *args):
        script = Path(__file__).resolve().parents[1] / "scripts" / "CoMVPLockStepR0.py"
        process = subprocess.run([sys.executable, "-B", str(script),
                                  "--root", str(self.root), "--db", str(self.db),
                                  *args], cwd=str(self.root), capture_output=True,
                                 text=True, timeout=10, check=False)
        return process.returncode, json.loads(process.stdout)

    def test_cli_end_to_end_local_slot_in_independent_processes(self):
        (self.root / "real-fixture.txt").write_text("one functional local artifact")
        (self.root / "real-test.py").write_text(
            "from pathlib import Path\nassert Path('real-fixture.txt').read_text() == "
            "'one functional local artifact'\n")
        code, staged = self.cli("stage", "--slot", "demo",
                                "--artifact", "real-fixture.txt", "--test", "real-test.py")
        self.assertEqual(code, 0)
        self.assertEqual(staged["state"], "STAGED_OR_EXISTING")
        rev = staged["revision"]
        code, tested = self.cli("qualify", "--slot", "demo", "--revision", rev)
        self.assertEqual(code, 0)
        self.assertEqual(tested["state"], "SOURCE_TESTED_LOCAL_ONLY")
        code, promoted = self.cli("promote", "--changes-json",
                                  json.dumps({"demo":rev}), "--expected-json",
                                  json.dumps({"demo":None}))
        self.assertEqual(code, 0)
        self.assertEqual(promoted["active"], {"demo":rev})
        code, status = self.cli("status")
        self.assertEqual(code, 0)
        self.assertEqual(status["active"]["demo"], rev)
        self.assertFalse(status["receiver_qualified"])
        self.assertGreaterEqual(status["audit"]["events_checked"],3)

    def test_cli_bad_json_cannot_replace_old_head(self):
        rev = self.candidate()
        self.activate("orb", rev)
        code, held = self.cli("promote", "--changes-json", "{not-json",
                              "--expected-json", '{"orb":null}')
        self.assertEqual(code, 3)
        self.assertEqual(held["state"], "HELD")
        self.assertEqual(self.store.active()["orb"], rev)

    def test_cli_failed_candidate_is_not_mvp(self):
        old = self.candidate()
        self.activate("orb", old)
        bad = self.candidate(label="bad", qualify=False, fail=True)
        code, failed = self.cli("qualify", "--slot", "orb", "--revision", bad)
        self.assertEqual(code, 3)
        self.assertEqual(failed["state"], "HELD_TEST_FAILED")
        code, held = self.cli("promote", "--changes-json", json.dumps({"orb":bad}),
                              "--expected-json", json.dumps({"orb":old}))
        self.assertEqual(code, 3)
        self.assertEqual(held["state"], "HELD")
        self.assertEqual(self.store.active()["orb"], old)

    def test_cli_multi_prodlet_cohort_uses_one_atomic_commit(self):
        e1=self.candidate("engine","one")
        ui1=self.candidate("ui","one",deps=(("engine",e1),))
        code, result=self.cli("promote", "--changes-json",
                              json.dumps({"engine":e1,"ui":ui1}),
                              "--expected-json", json.dumps({"engine":None,"ui":None}))
        self.assertEqual(code, 0)
        self.assertEqual(result["active"],{"engine":e1,"ui":ui1})
        self.assertEqual(len(result["changed"]),2)

    def test_all_states_are_source_scoped(self):
        rev = self.candidate()
        result = self.activate("orb", rev)
        self.assertEqual(result["state"], "SOURCE_HEADS_COMMITTED_LOCAL_ONLY")
        self.assertFalse(result["receiver_qualified"])
        self.assertFalse(self.store.audit_chain()["independent_custody"])


if __name__ == "__main__":
    unittest.main(verbosity=2)
