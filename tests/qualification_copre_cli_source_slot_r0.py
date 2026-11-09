#!/usr/bin/env python3
"""Actual CoPre candidate through the existing source-only CoMVP release slots.

A clean temporary source root copies exact checked-in bytes, pins a
minimum-use contract, stages and promotes one source head, then attempts a
regressive self-passing successor. No native deployment or TASK_MVP claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from CoMVPLockStepR0 import CoMVPSlots, Held

SLOT = "copre_issue403"
ARTIFACT = "scripts/CoMVPCoPreFirstUseR0.py"
DONOR = "scripts/CoPreContinuationR0.py"
SOURCE_TEST = "tests/source_copre_cli_candidate_r0.py"
ACCEPTANCE = "tests/acceptance_copre_cli_minimum_use_r0.py"
SLOT_CONTROLLER = "scripts/CoMVPLockStepR0.py"
FILES = (ARTIFACT, DONOR, SOURCE_TEST, ACCEPTANCE, SLOT_CONTROLLER)
SCHEMA = "CoMVP.CoPreSourceSlot.R0"


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def canonical(value) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def prove():
    with tempfile.TemporaryDirectory(prefix="comvp-copre-proof-") as name:
        root = Path(name)
        for relative in FILES:
            dest = root / relative
            dest.parent.mkdir(parents=True, exist_ok=True)
            src = ROOT / relative
            assert src.is_file() and not src.is_symlink(), "UNBOUND_CANDIDATE"
            shutil.copyfile(src, dest)
            assert sha(src.read_bytes()) == sha(dest.read_bytes())
        db = root / "state" / "selected.sqlite"
        db.parent.mkdir()
        store = CoMVPSlots(db, root)
        try:
            staged = store.stage(SLOT, ARTIFACT, SOURCE_TEST,
                                 acceptance_rel=ACCEPTANCE)
            assert staged["acceptance_contract_pinned"]
            head = staged["revision"]
            assert head == sha((ROOT / ARTIFACT).read_bytes())
            tested = store.qualify(SLOT, head)
            assert tested["state"] == "CONTRACT_TESTED_LOCAL_ONLY", tested
            first = store.promote_cohort({SLOT: head}, {SLOT: None})
            assert first["active"][SLOT] == head
            assert not first["receiver_qualified"]
            assert not first["native_runtime_updated"]

            # A worse successor can pass its own candidate test, but cannot
            # displace the independently pinned local minimum-use contract.
            bad = root / "scripts" / "CoMVPCoPreBadR0.py"
            weak = root / "tests" / "weak_candidate_check.py"
            bad.write_text("print('newer but not a working CoPre')\n", encoding="utf-8")
            weak.write_text("pass\n", encoding="utf-8")
            bad_rev = store.stage(SLOT, "scripts/CoMVPCoPreBadR0.py",
                                  "tests/weak_candidate_check.py")["revision"]
            rejected = store.qualify(SLOT, bad_rev)
            assert rejected["state"] == "HELD_ACCEPTANCE_REGRESSION", rejected
            try:
                store.promote_cohort({SLOT: bad_rev}, {SLOT: head})
            except Held as exc:
                assert str(exc) == "UNQUALIFIED_RELEASE_VERSION"
            else:
                raise AssertionError("REGRESSIVE_CANDIDATE_PROMOTED")
            assert store.active()[SLOT] == head
            audit = store.audit_chain()
        finally:
            store.close()

        # The only selected revision must still exist in a cold Python process.
        read = subprocess.run(
            [sys.executable, "-B", str(root / SLOT_CONTROLLER),
             "--root", str(root), "--db", str(db), "status"],
            cwd=root, text=True, capture_output=True, timeout=8, check=True,
        )
        status = json.loads(read.stdout)
        assert status["active"] == {SLOT: head}
        assert status["audit"]["events_checked"] == audit["events_checked"]
        assert status["receiver_qualified"] is False

        evidence = {
            "schema": SCHEMA, "state": "C2_SOURCE_CONTRACT_AND_SELECTED_LOCAL_HEAD",
            "source_scope": "CANDIDATE_PR_BRANCH_NOT_MAIN_RELEASE",
            "work_id": "CoMVP.CoPrePilot.20261109",
            "slot": SLOT, "candidate_path": ARTIFACT,
            "candidate_source_sha256": head,
            "donor_source_sha256": sha((ROOT / DONOR).read_bytes()),
            "candidate_test_sha256": sha((ROOT / SOURCE_TEST).read_bytes()),
            "pinned_minimum_use_sha256": sha((ROOT / ACCEPTANCE).read_bytes()),
            "acceptance_result": tested["state"],
            "candidate_test_log_sha256": tested["test_log_sha256"],
            "promotion": first["state"],
            "selected_source_head": status["active"][SLOT],
            "older_source_head_preserved": True,
            "regressive_candidate_result": rejected["state"],
            "regressive_candidate_selected": False,
            "cold_process_readback": True,
            "audit_events_checked": audit["events_checked"],
            "independent_consumer_validation": False,
            "real_issue_403_ci": "CHECK_SEPARATE_EXISTING_STEP",
            "external_receiver_ack": False,
            "user_task_mvp": "NOT_QUALIFIED",
            "native_x2_deployment": False,
            "actual_service_release": False,
        }
        evidence["receipt_sha256"] = sha(canonical(evidence))
        return evidence


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--report", help="Optional create-only JSON receipt")
    a = p.parse_args()
    result = prove()
    if a.report:
        target = Path(a.report)
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("x", encoding="utf-8") as out:
            json.dump(result, out, sort_keys=True, indent=2)
            out.write("\n")
            out.flush()
            os.fsync(out.fileno())
    print(json.dumps({"state": result["state"],
                      "work_id": result["work_id"],
                      "candidate_source_sha256": result["candidate_source_sha256"],
                      "pinned_minimum_use_sha256": result["pinned_minimum_use_sha256"],
                      "regression_rejected": not result["regressive_candidate_selected"],
                      "cold_process_readback": result["cold_process_readback"],
                      "receipt_sha256": result["receipt_sha256"],
                      "user_task_mvp": result["user_task_mvp"]}, sort_keys=True))


if __name__ == "__main__":
    main()
