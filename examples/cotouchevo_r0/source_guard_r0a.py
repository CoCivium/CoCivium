#!/usr/bin/env python3
"""CoTouchEvo R0A: pin an exact public donor before any shadow impact proposal.

This is a deterministic, no-network, zero-effect integration canary.  It does
NOT authenticate an earlier revision, a real change event, rights, consent, or
the proposed receivers.  Never use it to authorize publication or a worker.
"""
from __future__ import annotations

import copy
import hashlib
import re
from pathlib import Path

from touch_impact import propose

PUBLIC_DONOR = Path("examples/colensmedia/manifest.json")
PUBLIC_DONOR_BLOB = "b5a87427f2a6bf3c5e4928b7aa2c64e3a46deb01"
LIMIT_BYTES = 256 * 1024
KINDS = frozenset({"CONTENT", "RIGHTS_CHANGE", "RETRACTION", "RELATION_EDIT", "RULE_EDIT"})
ZERO_EFFECTS = {"worker_starts": 0, "network_calls": 0, "provider_calls": 0,
                "external_writes": 0, "ack_advances": 0}


def git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\x00" + raw).hexdigest()


def preview(repo_root: Path, fixture: dict, *, expected_current_blob: str,
            previous_blob: str, kind: str = "CONTENT") -> dict:
    """Return shadow source-change proposals, or a clearly gated no-effect hold.

    The 'previous_blob' argument is an UNVERIFIED scenario input.  A current
    source matching the public pin is useful exact-byte evidence, but never
    proves that any real historic change occurred.
    """
    if kind not in KINDS:
        raise ValueError("unknown change kind")
    if not all(isinstance(s, str) and re.fullmatch("[0-9a-f]{40}", s)
               for s in (expected_current_blob, previous_blob)):
        raise ValueError("git blobs must be lowercase 40-hex")
    if not isinstance(fixture, dict):
        raise ValueError("fixture must be a mapping")

    result = {
        "schema": "CoAll.CoTouchEvo.SourceGuard.R0A",
        "kind": kind,
        "source_path": PUBLIC_DONOR.as_posix(),
        "source_git_blob_sha1": None,
        "source_sha256": None,
        "source_identity": "NOT_VERIFIED",
        "previous_pin_authenticity": "UNVERIFIED_SCENARIO_INPUT",
        "change_event_origin": "NOT_AUTHENTICATED",
        "state": "HELD",
        "shadow_proposals": [],
        "review_only": [],
        "interested_receiver_count": 0,
        "sleeping_receiver_count": 0,
        "effects": dict(ZERO_EFFECTS),
        "nonclaims": [
            "EXACT_SOURCE_BYTES_NE_AUTHENTICATED_CHANGE",
            "OLD_BLOB_ARGUMENT_NE_VERIFIED_HISTORY",
            "RIGHTS_EVENT_NE_FILE_CONTENT_CHANGE",
            "SHADOW_PROPOSAL_NE_ACTUATION",
            "RECEIVER_SUBSCRIPTION_NE_CONSENT",
            "SOURCE_READBACK_NE_RECEIVER_PICKUP",
            "NO_UNLIMITED_TOKENS_COMPUTE_OR_WORKERS",
        ],
    }
    base = Path(repo_root)
    path = base / PUBLIC_DONOR
    # Fail closed on symlinked inputs rather than following an alternative donor.
    for part in [base, base / "examples", base / "examples" / "colensmedia", path]:
        if part.is_symlink():
            result["state"] = "HELD_SOURCE_SYMLINK"
            return result
    if not path.is_file():
        result["state"] = "HELD_SOURCE_MISSING"
        return result
    if path.stat().st_size > LIMIT_BYTES:
        result["state"] = "HELD_SOURCE_OVERSIZE"
        return result
    raw = path.read_bytes()
    current = git_blob_sha1(raw)
    result["source_git_blob_sha1"] = current
    result["source_sha256"] = hashlib.sha256(raw).hexdigest()
    if current != expected_current_blob:
        result["state"] = "HELD_CURRENT_BLOB_MISMATCH"
        return result
    if current != PUBLIC_DONOR_BLOB:
        result["state"] = "HELD_UNREVIEWED_CURRENT_DONOR"
        return result
    result["source_identity"] = "EXACT_PUBLIC_DONOR_BYTES_VERIFIED"

    # Revocation/rights changes can occur with *unchanged* source content.
    # No target identifiers are disclosed until an independent rights/event
    # authority and receiver ACL have been authenticated.
    if kind in {"RIGHTS_CHANGE", "RETRACTION"}:
        result["state"] = "HELD_RIGHTS_EVENT_AND_RECEIVER_AUTHORIZATION"
        return result
    if kind in {"RELATION_EDIT", "RULE_EDIT"}:
        result["state"] = "HELD_TYPED_RELATION_OR_RULE_ORIGIN"
        return result

    # Matching exact blobs means no evidenced CONTENT delta.  Suppress the
    # entire proposed cascade, even when the old fixture says 'changed'.
    if previous_blob == current:
        result["state"] = "NO_CONTENT_DELTA"
        return result

    change = fixture.get("change")
    if not isinstance(change, dict) or change.get("subject") != "source:colens":
        result["state"] = "HELD_FIXTURE_SOURCE_MISMATCH"
        return result
    if change.get("evidence") == "HYPOTHESIS":
        result["state"] = "HELD_HYPOTHETICAL_CHANGE"
        return result

    # A different *claimed* previous pin is only a simulation.  Force the
    # underlying selector into SYNTHETIC evidence, not OBSERVED authority.
    candidate = copy.deepcopy(fixture)
    candidate["change"] = {
        "subject": "source:colens",
        "event_id": "synthetic:colens-source-guard",
        "revision_sha256": result["source_sha256"],
        "evidence": "SYNTHETIC",
    }
    shadow = propose(candidate)
    result["state"] = "SIMULATED_CONTENT_DELTA_SHADOW_ONLY"
    result["shadow_proposals"] = shadow["proposals"]
    result["review_only"] = shadow["review_only"]
    live = {p["receiver"] for p in shadow["proposals"]}
    result["interested_receiver_count"] = len(live)
    result["sleeping_receiver_count"] = sum(
        1 for r in candidate["receivers"] if r["id"] not in live
    )
    return result
