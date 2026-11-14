#!/usr/bin/env python3
"""Fresh-process, temporary-directory demo. No network, no external effects."""
import hashlib
import json
import pathlib
import subprocess
import sys
import tempfile

HERE = pathlib.Path(__file__).resolve().parent
TOOL = HERE / "coobject_capsule_r0.py"


def call(*args):
    r = subprocess.run([sys.executable, str(TOOL), *map(str, args)], text=True, capture_output=True)
    if r.returncode != 0:
        raise RuntimeError(f"CLI_FAIL_{r.returncode}:{r.stdout}:{r.stderr}")
    return json.loads(r.stdout)


def run():
    with tempfile.TemporaryDirectory() as td:
        root = pathlib.Path(td)
        src = root / "first.txt"
        src.write_text("Questions can be complete without an answer.\n", encoding="utf-8")
        aux = root / "second.txt"
        aux.write_text("An exact recovery path is more useful than a glowing label.\n", encoding="utf-8")
        a = root / "capsule_a"
        b = root / "capsule_b"
        before = call("pack", src, a, "--title", "Question fragment", "--kind", "question", "--purpose", "Read exact question")
        call("pack", aux, b, "--title", "Recovery counterpoint", "--kind", "document", "--purpose", "Read exact note")
        assert before["status"] == "READY_LOCAL_TWO_COPIES"
        (a / "payload.bin").unlink()
        degraded = call("check", a)
        assert degraded["status"] == "DEGRADED_LOCAL_ONE_COPY"
        restored = root / "restored.txt"
        outcome = call("restore", a, restored)
        assert restored.read_bytes() == src.read_bytes()
        bridge = call("relate", a, b, "--seed", "53")
        assert bridge["state"] == "SERENDIPITY_CANDIDATE_ONLY"
        assert bridge["new_relation_granted"] is False
        assert outcome["receiver_ack"] is False
        return {
            "schema": "CoCivium.CoObject.OfflineCapsule.DemoResult.R0",
            "scope": "FRESH_PROCESS_LOCAL_TEMPFILES_ONLY",
            "object_status_before": before["status"],
            "object_status_after_local_loss": degraded["status"],
            "restoration_status": outcome["state"],
            "restored_sha256": hashlib.sha256(restored.read_bytes()).hexdigest(),
            "source_sha256": hashlib.sha256(src.read_bytes()).hexdigest(),
            "exact_bytes_equal": restored.read_bytes() == src.read_bytes(),
            "serendipity_state": bridge["state"],
            "serendipity_lens": bridge["lens"],
            "serendipity_seed": bridge["seed"],
            "candidate_relation_proven": False,
            "independent_fault_domain_proven": False,
            "original_author_verified": False,
            "external_receiver_verified": False,
            "end_to_end_x2_product_verified": False,
            "higher_authority_granted": False,
        }


if __name__ == "__main__":
    print(json.dumps(run(), sort_keys=True, indent=2))
