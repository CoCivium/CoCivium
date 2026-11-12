"""Single effect boundary for PUBLIC_SYNTHETIC WorkID proposals.

Caller-provided authorization is a test fixture, NOT authenticated consent.
No network, human authority, real receiver ACK, or deployment.
"""
import importlib.util
from pathlib import Path

from workid_convergence import inspect_with_source

SCRIPT = Path(__file__).resolve().parents[2] / "scripts" / "CoNarrativeWorkIDR0.py"


def _receiver():
    spec = importlib.util.spec_from_file_location("conarrative_workid_r0", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def commit_guarded(db_path, proposal, authorization, source_path, *, fault=None):
    """Gate and write in one callable boundary; hold before creating a DB."""
    gate = inspect_with_source(proposal, authorization, source_path)
    if gate.get("state") != "PROPOSAL_SOURCE_BYTES_MATCHED_ONLY":
        return {"state": "HELD_BEFORE_WRITE", "gate_state": gate.get("state"),
                "external_receiver_ack": False, "local_commit": False}
    receiver = _receiver()
    packet = dict(proposal, schema=receiver.SCHEMA, consent_epoch=1)
    receiver.validate(packet)
    result = receiver.commit_once(db_path, packet, fault=fault)
    cold = receiver.readback(db_path, expected_packet=packet, source_path=source_path)
    return {"state": "SYNTHETIC_LOCAL_READBACK_ONLY",
            "new_commits": result["new_commits"], "duplicate": result["duplicate"],
            "receipt_sha256": cold["receipt_sha256"], "readback_state": cold["state"],
            "external_receiver_ack": False, "authenticated_authority": False,
            "real_world_effects": 0}
