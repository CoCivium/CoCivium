"""Synthetic WorkID source-and-proposal convergence. No transport or ACK."""
from workid_handoff_gate import inspect
from workid_source_pin import verify_source


def inspect_with_source(packet, authorization, source_path):
    """Both independent local checks must pass; never elevate to receiver ACK."""
    proposal = inspect(packet, authorization)
    if proposal.get("state") != "PROPOSAL_ONLY":
        return proposal
    source = verify_source(source_path, packet["source_ref"], packet["source_sha256"])
    if source.get("state") != "SOURCE_BYTES_MATCH_FIXTURE_PIN":
        return {"state": "HELD_SOURCE_PROOF", "source_state": source["state"], "receiver_ack": False}
    return {"state": "PROPOSAL_SOURCE_BYTES_MATCHED_ONLY", "work_id": proposal["work_id"],
            "source_sha256": source["sha256"], "authenticated_origin": False,
            "authorization_authenticated": False, "receiver_ack": False}
