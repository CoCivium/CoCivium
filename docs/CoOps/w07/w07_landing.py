#!/usr/bin/env python3
"""W07 CoLanding envelope builder/verifier (per COSESSIONMESH_COLANDING_CONTRACT_R0, candidate).

build : python3 -I w07_landing.py build <jobs.json> <out_dir>   (run from repo root)
verify: python3 -I w07_landing.py verify <out_dir>              (recomputes envelope + file digests)

envelope_sha256 = sha256(canonical UTF-8 JSON, sorted keys, separators (',',':'), excluding envelope_sha256).
A digest detects changed bytes only; it is not authorship, approval or custody. Disposition here can be at most
PREPARED (worker's own assertion) until an independent reader verifies the remote ref.
"""
import hashlib, json, os, sys


def canon(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def file_sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def seal(env):
    body = {k: v for k, v in env.items() if k != "envelope_sha256"}
    env["envelope_sha256"] = hashlib.sha256(canon(body)).hexdigest()
    return env


FIELDS = ["schema_version", "worker_id", "session_instance_id", "cycle_id", "job_id", "attempt_id", "object_id", "kind",
          "input_refs", "output_refs", "dependency_ids", "produced_utc", "claimed_actor", "evidence", "tests",
          "disposition", "authority_ref_or_null", "reviewer_ids", "collision_scope", "successor_job_ids",
          "hold_reason_or_null", "privacy_class"]


def build(spec_path, out_dir):
    spec = json.load(open(spec_path)); os.makedirs(out_dir, exist_ok=True); common = spec["common"]
    for job in spec["jobs"]:
        env = dict(common, **{k: v for k, v in job.items() if k != "outputs"})
        env["output_refs"] = [dict(uri=f"{common['branch_uri']}:{p}", sha256=file_sha(p)) for p in job["outputs"]]
        env["idempotency_key"] = hashlib.sha256("|".join(
            [env["worker_id"], env["job_id"], json.dumps(env["input_refs"], sort_keys=True),
             *[o["sha256"] for o in env["output_refs"]]]).encode()).hexdigest()
        env["object_id"] = "sha256:" + hashlib.sha256(canon(sorted(o["sha256"] for o in env["output_refs"]))).hexdigest()
        env.pop("branch_uri", None)
        missing = [f for f in FIELDS if f not in env]
        if missing: raise SystemExit(f"{job['job_id']}: missing {missing}")
        seal(env)
        with open(os.path.join(out_dir, f"{env['job_id']}.json"), "w") as f:
            json.dump(env, f, indent=2, sort_keys=True, ensure_ascii=False); f.write("\n")
        print(env["job_id"], env["envelope_sha256"])


def verify(out_dir):
    bad = 0
    for name in sorted(os.listdir(out_dir)):
        if not name.endswith(".json"): continue
        env = json.load(open(os.path.join(out_dir, name))); want = env["envelope_sha256"]
        ok_env = seal(dict(env))["envelope_sha256"] == want
        ok_files = all(file_sha(o["uri"].split(":", 1)[1]) == o["sha256"] for o in env["output_refs"]
                       if os.path.exists(o["uri"].split(":", 1)[1]))
        bad += not (ok_env and ok_files); print(name, "envelope", ok_env, "files", ok_files)
    raise SystemExit(1 if bad else 0)


if __name__ == "__main__":
    {"build": lambda: build(sys.argv[2], sys.argv[3]), "verify": lambda: verify(sys.argv[2])}[sys.argv[1]]()
