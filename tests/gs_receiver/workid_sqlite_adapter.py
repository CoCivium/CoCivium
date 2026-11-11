"""Fail-closed synthetic browser-proposal to existing SQLite WorkID adapter.

Local test substrate only: never authenticates a user or external receiver.
"""
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'scripts'))

from workid_convergence import inspect_with_source
from CoNarrativeWorkIDR0 import (
    SCHEMA, Held, commit_once, readback, validate,
)


def adapt_proposal(packet, authorization, source_path):
    """Convert only a source-byte-matched synthetic browser proposal."""
    gate = inspect_with_source(packet, authorization, source_path)
    if gate.get("state") != "PROPOSAL_SOURCE_BYTES_MATCHED_ONLY":
        raise Held("BROWSER_PROPOSAL_HELD:" + str(gate.get("state")))
    # Construct the receiver's exact versioned schema. Never trust a caller's
    # consent_epoch: it comes from the separately supplied synthetic test scope.
    converted = {
        "schema": SCHEMA,
        "work_id": packet["work_id"],
        "source_ref": packet["source_ref"],
        "source_sha256": packet["source_sha256"],
        "narrative_summary": packet["narrative_summary"],
        "prior_decisions": list(packet["prior_decisions"]),
        "open_blockers": list(packet["open_blockers"]),
        "next_safe_deed": packet["next_safe_deed"],
        "privacy": "PUBLIC_SYNTHETIC",
        "consent": "SYNTHETIC_TEST_ONLY",
        "consent_epoch": 1,
        "lease_epoch": packet["lease_epoch"],
    }
    validate(converted)
    return converted


def commit_proposal(db_path, packet, authorization, source_path, *, fault=None):
    """Source gate -> one local commit -> independent readonly verification."""
    converted = adapt_proposal(packet, authorization, source_path)
    committed = commit_once(db_path, converted, fault=fault)
    cold = readback(db_path, expected_packet=converted, source_path=source_path)
    if cold["state"] != "COLD_SOURCE_RECONSTRUCTED":
        raise Held("COLD_READBACK_NOT_ACTIVE")
    return {
        "state": "SYNTHETIC_LOCAL_READBACK_ONLY",
        "work_id": converted["work_id"],
        "new_commits": committed["new_commits"],
        "duplicate": committed["duplicate"],
        "packet_sha256": cold["packet_sha256"],
        "receipt_sha256": cold["receipt_sha256"],
        "external_receiver_ack": False,
        "authenticated_user_consent": False,
        "independent_provider": False,
        "survived_24h": False,
    }
