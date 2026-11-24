#!/usr/bin/env python3
"""CoLanding envelope builder/verifier per COSESSIONMESH_COLANDING_CONTRACT_R0 (blob bccd5de).
SHA-256 over canonical UTF-8 JSON (sorted keys, compact separators), excluding
envelope_sha256 and signature. Usage:
  envelope.py build <spec.json> <out.json>
  envelope.py verify <envelope.json> [--files-root DIR]
"""
import hashlib, json, os, sys

REQUIRED = ["schema_version", "worker_id", "session_instance_id", "cycle_id", "job_id",
            "attempt_id", "object_id", "kind", "input_refs", "output_refs", "dependency_ids",
            "produced_utc", "claimed_actor", "evidence", "tests", "disposition",
            "authority_ref_or_null", "reviewer_ids", "collision_scope", "successor_job_ids",
            "hold_reason_or_null", "privacy_class"]

def canon(env):
    body = {k: v for k, v in env.items() if k not in ("envelope_sha256", "signature")}
    return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()

def sha(b): return hashlib.sha256(b).hexdigest()

def build(spec_path, out_path):
    env = json.load(open(spec_path))
    missing = [k for k in REQUIRED if k not in env]
    if missing: sys.exit(f"missing fields: {missing}")
    env["envelope_sha256"] = sha(canon(env))
    json.dump(env, open(out_path, "w"), indent=2, sort_keys=True, ensure_ascii=False)
    print(env["envelope_sha256"])

def verify(path, root=None):
    env = json.load(open(path)); errs = []
    missing = [k for k in REQUIRED if k not in env]
    if missing: errs.append(f"missing {missing}")
    if env.get("envelope_sha256") != sha(canon(env)): errs.append("envelope_sha256 mismatch")
    if not str(env.get("worker_id", "")).startswith("W"): errs.append("bad worker_id")
    lifecycle = env.get("disposition", "")
    if any(s in lifecycle for s in ("SOURCE_VISIBLE", "HASH_VERIFIED", "RECEIVER_READBACK", "INTEGRATED")):
        if not any(e.get("type") == "remote_readback" for e in env.get("evidence", [])):
            errs.append("lifecycle state above PREPARED without remote_readback evidence (NoPhantomACK)")
    if root:
        for o in env.get("output_refs", []):
            p = os.path.join(root, o["local_path"]) if o.get("local_path") else None
            if p and os.path.exists(p) and len(o.get("sha256_or_commit", "")) == 64:
                if sha(open(p, "rb").read()) != o["sha256_or_commit"]:
                    errs.append(f"hash mismatch {o['local_path']}")
            elif p and not os.path.exists(p): errs.append(f"missing local file {o['local_path']}")
    blob = json.dumps(env).lower()
    for bad in ("ghp_", "github_pat_", "apppassword\": \"", "bearer "):
        if bad in blob: errs.append(f"possible secret marker {bad!r}")
    print("PASS" if not errs else "FAIL: " + "; ".join(errs)); return not errs

if __name__ == "__main__":
    if sys.argv[1] == "build": build(sys.argv[2], sys.argv[3])
    else:
        root = sys.argv[sys.argv.index("--files-root") + 1] if "--files-root" in sys.argv else None
        sys.exit(0 if verify(sys.argv[2], root) else 1)
