#!/usr/bin/env python3
import argparse
import hashlib
import json
from collections import defaultdict
from pathlib import Path

REQUIRED_DELTA = {
    "delta_id",
    "source_session",
    "created_at",
    "target_domains",
    "operations",
    "authority_ceiling",
    "public_safety",
    "nonclaims",
    "next_gate",
}
ALLOWED_PUBLIC_SAFETY = {
    "PUBLIC_SAFE",
    "PUBLIC_SAFE_WITH_REDACTION",
    "PRIVATE_ONLY",
    "UNKNOWN",
}
ALLOWED_OPS = {
    "ADD",
    "QUALIFY",
    "CHALLENGE",
    "LINK",
    "INDEX",
    "HIGHLIGHT",
    "DEPRECATE",
    "RESTRUCTURE",
    "PROJECT",
}
NONCLAIMS = [
    "FANIN_NE_FANOUT",
    "DUPLICATE_OPERATION_NE_DUPLICATE_INTENT",
    "COLLISION_CANDIDATE_NE_CONTRADICTION",
    "VALIDATION_NE_ACCEPTANCE",
    "BRANCH_NE_INTEGRATED",
    "MERGED_NE_CANON",
    "PUBLIC_SAFE_LABEL_NE_PUBLICATION_APPROVAL",
]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest().upper()


def normalize_operation(op):
    return {
        "op": op.get("op"),
        "subject": op.get("subject"),
        "relation": op.get("relation"),
        "object": op.get("object"),
        "qualifiers": op.get("qualifiers", {}),
        "evidence_refs": sorted(op.get("evidence_refs", [])),
    }


def expand_payload(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("deltas"), list):
        return payload["deltas"]
    if isinstance(payload, dict):
        return [payload]
    raise ValueError("top level must be an object, array, or {'deltas': [...]} object")


def validate_delta(delta):
    if not isinstance(delta, dict):
        return "delta is not an object"
    missing = sorted(REQUIRED_DELTA - set(delta))
    if missing:
        return "missing required keys: " + ", ".join(missing)
    if delta.get("public_safety") not in ALLOWED_PUBLIC_SAFETY:
        return "invalid public_safety"
    if not isinstance(delta.get("target_domains"), list) or not delta["target_domains"]:
        return "target_domains must be a non-empty array"
    if not isinstance(delta.get("operations"), list) or not delta["operations"]:
        return "operations must be a non-empty array"
    for i, op in enumerate(delta["operations"]):
        if not isinstance(op, dict):
            return f"operation {i} is not an object"
        if op.get("op") not in ALLOWED_OPS:
            return f"operation {i} has invalid op"
        if not op.get("subject") or not op.get("relation"):
            return f"operation {i} requires subject and relation"
    return None


def compile_fanin(paths):
    accepted = []
    rejected = []
    source_files = []
    seen_delta_ids = set()

    raw_sources = []
    for path_text in paths:
        raw = Path(path_text).read_bytes()
        raw_sources.append({
            "sha256": sha256_bytes(raw),
            "bytes": len(raw),
            "raw": raw,
        })

    unique_sources = {}
    for source in raw_sources:
        unique_sources.setdefault(source["sha256"], source)

    for digest in sorted(unique_sources):
        source = unique_sources[digest]
        raw = source["raw"]
        source_files.append({
            "sha256": digest,
            "bytes": source["bytes"],
        })
        try:
            payload = json.loads(raw.decode("utf-8"))
            records = expand_payload(payload)
        except Exception as exc:
            rejected.append({"source_file_sha256": digest, "record_index": None, "reason": str(exc)})
            continue

        for idx, delta in enumerate(records):
            reason = validate_delta(delta)
            if reason is None and delta["delta_id"] in seen_delta_ids:
                reason = "duplicate delta_id in bounded input set"
            if reason is not None:
                rejected.append({"source_file_sha256": digest, "record_index": idx, "reason": reason})
                continue
            seen_delta_ids.add(delta["delta_id"])
            accepted.append({
                "delta": delta,
                "source_file_sha256": digest,
                "record_index": idx,
            })

    op_groups = defaultdict(list)
    collision_groups = defaultdict(lambda: defaultdict(list))
    domain_index = defaultdict(set)
    surface_index = defaultdict(set)
    highlights = []
    public_holds = []

    for item in accepted:
        delta = item["delta"]
        delta_id = delta["delta_id"]
        for domain in delta.get("target_domains", []):
            domain_index[str(domain)].add(delta_id)
        for surface in delta.get("candidate_surfaces", []):
            surface_index[str(surface)].add(delta_id)

        safety = delta["public_safety"]
        if safety != "PUBLIC_SAFE":
            public_holds.append({
                "delta_id": delta_id,
                "public_safety": safety,
                "reason": "requires redaction/review or is not public-safe",
            })

        for op_index, op in enumerate(delta["operations"]):
            normalized = normalize_operation(op)
            op_hash = sha256_bytes(canonical(normalized).encode("utf-8"))
            ref = {
                "delta_id": delta_id,
                "source_session": delta["source_session"],
                "operation_index": op_index,
                "operation_sha256": op_hash,
                "operation": normalized,
            }
            op_groups[op_hash].append(ref)
            collision_key = (str(normalized["subject"]), str(normalized["relation"]))
            object_key = canonical(normalized["object"])
            collision_groups[collision_key][object_key].append(ref)
            if normalized["op"] == "HIGHLIGHT":
                highlights.append(ref)

    unique_operations = []
    duplicate_groups = []
    for op_hash in sorted(op_groups):
        refs = sorted(op_groups[op_hash], key=lambda x: (x["delta_id"], x["operation_index"]))
        unique_operations.append(refs[0])
        if len(refs) > 1:
            duplicate_groups.append({
                "operation_sha256": op_hash,
                "count": len(refs),
                "refs": refs,
            })

    collisions = []
    for (subject, relation), objects in sorted(collision_groups.items()):
        if len(objects) <= 1:
            continue
        variants = []
        for object_key in sorted(objects):
            refs = sorted(objects[object_key], key=lambda x: (x["delta_id"], x["operation_index"]))
            variants.append({
                "object": refs[0]["operation"]["object"],
                "refs": refs,
            })
        collisions.append({
            "subject": subject,
            "relation": relation,
            "state": "REVIEW_REQUIRED_NOT_PROVEN_CONTRADICTION",
            "variants": variants,
        })

    accepted_summary = []
    for item in sorted(accepted, key=lambda x: x["delta"]["delta_id"]):
        d = item["delta"]
        accepted_summary.append({
            "delta_id": d["delta_id"],
            "source_session": d["source_session"],
            "source_file_sha256": item["source_file_sha256"],
            "record_index": item["record_index"],
            "public_safety": d["public_safety"],
            "authority_ceiling": d["authority_ceiling"],
            "next_gate": d["next_gate"],
        })

    result = {
        "compiler": "CoSessionRelationalFanIn.R0",
        "coverage": {
            "input_files_seen": len(raw_sources),
            "unique_source_files": len(source_files),
            "accepted_deltas": len(accepted_summary),
            "rejected_records": len(rejected),
            "unique_operations": len(unique_operations),
            "duplicate_operation_groups": len(duplicate_groups),
            "collision_candidates": len(collisions),
            "highlight_candidates": len(highlights),
            "public_fanout_holds": len(public_holds),
            "semantic_near_duplicate_review": "NOT_COMPUTED_R0",
        },
        "source_files": source_files,
        "accepted_deltas": accepted_summary,
        "rejected_records": sorted(rejected, key=lambda x: (x["source_file_sha256"], -1 if x["record_index"] is None else x["record_index"])),
        "unique_operations": unique_operations,
        "duplicate_operation_groups": duplicate_groups,
        "collision_candidates": collisions,
        "target_domain_index": {k: sorted(v) for k, v in sorted(domain_index.items())},
        "candidate_surface_index": {k: sorted(v) for k, v in sorted(surface_index.items())},
        "highlight_candidates": sorted(highlights, key=lambda x: (x["delta_id"], x["operation_index"])),
        "public_fanout_holds": sorted(public_holds, key=lambda x: x["delta_id"]),
        "eligible_public_review_delta_ids": sorted(
            item["delta"]["delta_id"] for item in accepted if item["delta"]["public_safety"] == "PUBLIC_SAFE"
        ),
        "effects": {
            "shared_target_mutations": 0,
            "automatic_fanout": 0,
            "canon_changes": 0,
        },
        "next": "REVIEW_COLLISIONS_AND_HOLDS_THEN_ELECT_TARGETED_PROJECTIONS",
        "nonclaims": NONCLAIMS,
    }
    compiled_bytes = canonical(result).encode("utf-8")
    result["compiled_sha256"] = sha256_bytes(compiled_bytes)
    return result


def main():
    parser = argparse.ArgumentParser(description="Deterministically fan in CoSession relational delta JSON files.")
    parser.add_argument("--input", action="append", required=True, help="Input JSON file. Repeat for multiple files.")
    parser.add_argument("--output", required=True, help="Output compiled JSON path.")
    args = parser.parse_args()

    result = compile_fanin(args.input)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"STATE=PASS_DETERMINISTIC_RELATIONAL_FANIN_R0")
    print(f"OUTPUT={output}")
    print(f"COMPILED_SHA256={result['compiled_sha256']}")
    print(f"ACCEPTED_DELTAS={result['coverage']['accepted_deltas']}")
    print(f"UNIQUE_OPERATIONS={result['coverage']['unique_operations']}")
    print(f"DUPLICATE_GROUPS={result['coverage']['duplicate_operation_groups']}")
    print(f"COLLISION_CANDIDATES={result['coverage']['collision_candidates']}")
    print(f"PUBLIC_FANOUT_HOLDS={result['coverage']['public_fanout_holds']}")


if __name__ == "__main__":
    main()
