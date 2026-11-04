#!/usr/bin/env python3
"""CoAll Golden Braid R0: same-runner SYNTHETIC transport, not integration."""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
SEED = REPO / "ai/evolution-deltas/2026-10-26/coevo-shared-draft-bridge-r0.json"
DESTINATIONS = ("alpha", "beta")
REQUIRED = ("delta_id", "observed_at", "source_refs", "authority_ceiling",
            "confidentiality", "epistemic_class", "mutation_class", "next_receiver")
NONCLAIMS = [
    "SYNTHETIC_RECEIVER_NE_REAL_RECIPIENT",
    "LOCAL_COPY_NE_EXTERNAL_DELIVERY",
    "READBACK_NE_INDEPENDENT_ACCEPTANCE",
    "DISPATCH_ATTEMPT_NE_ACK",
    "REPLAY_NE_ALWAYS_ON_RUNTIME",
    "BRANCH_CI_NE_CUSTODY_OR_PUBLICATION",
    "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
]

def sha(raw):
    return hashlib.sha256(raw).hexdigest()

def encode(value):
    return (json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True) + "\n").encode("utf-8")

def load(path):
    return json.loads(Path(path).read_bytes().decode("utf-8"))

def validate_seed(raw):
    obj = json.loads(raw.decode("utf-8"))
    if not isinstance(obj, dict) or any(not obj.get(key) for key in REQUIRED):
        raise ValueError("HELD_SOURCE_MISSING_REQUIRED_FIELDS")
    if (obj["confidentiality"] != "PUBLIC"
        or not obj["authority_ceiling"].startswith("PUBLIC_SAFE_BRANCH_PROPOSAL_ONLY")
        or obj["mutation_class"] != "PROPOSE"):
        raise ValueError("HELD_NOT_AUTHORIZED_SYNTHETIC_PUBLIC_SOURCE")
    if obj["epistemic_class"] not in ("PLANNED", "HYPOTHESIS", "PROPOSED"):
        raise ValueError("HELD_UNEXPECTED_EVIDENCE_CLASS")
    if not isinstance(obj["source_refs"], list) or not obj["source_refs"]:
        raise ValueError("HELD_SOURCE_PROVENANCE_MISSING")
    return obj

def write_once(path, payload):
    """Fail-closed: never overwrite mismatched or partial content."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(str(path), os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    except FileExistsError:
        current = path.read_bytes()
        if current == payload:
            return "ALREADY_IDENTICAL"
        raise ValueError("HELD_CONTENT_COLLISION")
    with os.fdopen(fd, "wb") as fh:
        fh.write(payload)
        fh.flush()
        os.fsync(fh.fileno())
    return "CREATED_EXACT"

def manifest_path(workspace):
    return Path(workspace) / "packet_manifest.json"

def initialize(workspace, source=SEED):
    raw = Path(source).read_bytes()
    obj = validate_seed(raw)
    manifest = {
        "schema": "CoAll.GoldenBraid.SyntheticTransport.R0",
        "delta_id": obj["delta_id"],
        "seed_source": str(Path(source).resolve()),
        "source_sha256": sha(raw),
        "source_bytes": len(raw),
        "source_epistemic_class": obj["epistemic_class"],
        "destinations": list(DESTINATIONS),
        "authority": "SAME_RUNNER_SYNTHETIC_ONLY",
        "external_effects": 0,
        "independent_receiver_ack": False,
        "nonclaims": NONCLAIMS,
    }
    write_once(manifest_path(workspace), encode(manifest))
    return manifest

def verified_source(manifest):
    raw = Path(manifest["seed_source"]).read_bytes()
    if sha(raw) != manifest["source_sha256"] or len(raw) != manifest["source_bytes"]:
        raise ValueError("HELD_SOURCE_CHANGED_SINCE_MANIFEST")
    validate_seed(raw)
    return raw

def require_destination(dest):
    if dest not in DESTINATIONS:
        raise ValueError("HELD_UNKNOWN_OR_UNAUTHORIZED_TEST_DESTINATION")

def inbox_path(workspace, dest):
    require_destination(dest)
    return Path(workspace) / "inbox" / dest / "delta.json"

def receipt_path(workspace, dest):
    require_destination(dest)
    return Path(workspace) / "readbacks" / (dest + ".json")

def dispatch(workspace, dest, inject_failure=False):
    require_destination(dest)
    manifest = load(manifest_path(workspace))
    raw = verified_source(manifest)
    if inject_failure:
        return {"dest": dest, "attempt": "INJECTED_FAILURE", "state": "HELD_NOT_DELIVERED"}
    try:
        state = write_once(inbox_path(workspace, dest), raw)
    except ValueError:
        return {"dest": dest, "attempt": "COLLISION_HOLD", "state": "HELD_INBOX_CONFLICT"}
    return {"dest": dest, "attempt": state, "state": "LOCAL_SYNTHETIC_COPY_ONLY"}

def receiver_process_readback(workspace, dest):
    """Called as its own process; STILL the same CI runner, not an external receiver."""
    require_destination(dest)
    manifest = load(manifest_path(workspace))
    path = inbox_path(workspace, dest)
    if not path.exists():
        raise ValueError("HELD_RECEIVER_INBOX_MISSING")
    actual = path.read_bytes()
    if sha(actual) != manifest["source_sha256"] or len(actual) != manifest["source_bytes"]:
        raise ValueError("HELD_RECEIVER_BYTES_DO_NOT_MATCH")
    record = {
        "schema": "CoAll.GoldenBraid.SyntheticReadback.R0",
        "destination": dest,
        "source_sha256": manifest["source_sha256"],
        "observed_sha256": sha(actual),
        "state": "SYNTHETIC_SAME_RUNNER_READBACK",
        "receiver_kind": "LOCAL_TEST_PROCESS_NOT_INDEPENDENT",
        "external_delivery": "UNPROVEN",
        "human_or_agent_pickup": "UNPROVEN",
        "authority": "NONE",
    }
    return write_once(receipt_path(workspace, dest), encode(record))

def reconcile(workspace):
    manifest = load(manifest_path(workspace))
    result = {}
    for dest in manifest["destinations"]:
        path = inbox_path(workspace, dest)
        actual = path.read_bytes() if path.exists() else None
        inbox = ("ABSENT" if actual is None else
                 "EXACT" if sha(actual) == manifest["source_sha256"] and len(actual) == manifest["source_bytes"]
                 else "CONFLICT")
        proof_path = receipt_path(workspace, dest)
        proof = load(proof_path) if proof_path.exists() else None
        proven = bool(inbox == "EXACT" and proof
                      and proof.get("destination") == dest
                      and proof.get("observed_sha256") == manifest["source_sha256"]
                      and proof.get("state") == "SYNTHETIC_SAME_RUNNER_READBACK")
        result[dest] = {
            "inbox": inbox,
            "local_process_readback": "MATCHED" if proven else "UNPROVEN",
            "external_receiver_ack": "UNPROVEN",
        }
    return {
        "source_sha256": manifest["source_sha256"],
        "delta_id": manifest["delta_id"],
        "destinations": result,
        "all_synthetic_readbacks": all(v["local_process_readback"] == "MATCHED" for v in result.values()),
        "cross_surface_integration": "UNPROVEN",
        "external_effects": 0,
        "nonclaims": NONCLAIMS,
    }

def subprocess_readback(workspace, dest):
    cmd = [sys.executable, str(Path(__file__).resolve()), "read",
           "--workspace", str(workspace), "--destination", dest]
    done = subprocess.run(cmd, check=False, capture_output=True, text=True)
    if done.returncode:
        raise RuntimeError("SYNTHETIC_RECEIVER_PROCESS_FAILED: " + done.stderr.strip())
    return json.loads(done.stdout)

def demo(workspace, source=SEED):
    workspace = Path(workspace)
    initialize(workspace, source)
    alpha_first = dispatch(workspace, "alpha")
    beta_failure = dispatch(workspace, "beta", inject_failure=True)
    subprocess_readback(workspace, "alpha")
    before = reconcile(workspace)
    alpha_repeat = dispatch(workspace, "alpha")
    beta_recovery = dispatch(workspace, "beta")
    subprocess_readback(workspace, "beta")
    recovered = subprocess.run([sys.executable, str(Path(__file__).resolve()),
                                "status", "--workspace", str(workspace)],
                               capture_output=True, text=True, check=True)
    after = json.loads(recovered.stdout)
    if (before["all_synthetic_readbacks"]
        or not after["all_synthetic_readbacks"]
        or alpha_repeat["attempt"] != "ALREADY_IDENTICAL"
        or beta_failure["state"] != "HELD_NOT_DELIVERED"
        or after["cross_surface_integration"] != "UNPROVEN"):
        raise AssertionError("FAIL_SYNTHETIC_RECOVERY_INVARIANTS")
    output = {
        "state": "PASS_SYNTHETIC_SAME_RUNNER_TWO_DESTINATION_CANARY",
        "first_alpha": alpha_first, "injected_beta": beta_failure,
        "before_recovery": before,
        "replay_alpha": alpha_repeat, "replay_beta": beta_recovery,
        "reconstructed_in_fresh_process": after,
        "transport_class": "LOCAL_TEST_RECEIVER_PROCESSES_ONLY",
        "actual_external_deliveries": 0,
        "independent_receiver_acceptances": 0,
    }
    write_once(workspace / "synthetic_result.json", encode(output))
    return output

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("demo", "read", "status"))
    parser.add_argument("--workspace", type=Path, required=True)
    parser.add_argument("--destination", choices=DESTINATIONS)
    args = parser.parse_args()
    if args.command == "read":
        if not args.destination:
            parser.error("--destination required for read")
        out = {"state": receiver_process_readback(args.workspace, args.destination)}
    elif args.command == "demo":
        out = demo(args.workspace)
    else:
        out = reconcile(args.workspace)
    print(json.dumps(out, sort_keys=True, indent=2))

if __name__ == "__main__":
    main()
