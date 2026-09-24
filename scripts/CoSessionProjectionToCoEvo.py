#!/usr/bin/env python3
import argparse
import hashlib
import json
from pathlib import Path

REQUIRED_PROJECTION = {
    "projection_of",
    "delta_id",
    "source_session",
    "created_at",
    "target_domains",
    "operations",
    "authority_ceiling",
    "confidentiality",
    "public_safety",
    "next_receiver",
    "nonclaims",
    "next_gate",
}

ALLOWED_EPISTEMIC = {
    "OBSERVED", "INFERRED", "HYPOTHESIS", "PREDICTED", "PLANNED",
    "PREFERRED", "METAPHORICAL", "MYTHIC", "HUMOROUS",
    "COUNTERFACTUAL", "UNKNOWN",
}
ALLOWED_MUTATION = {
    "OBSERVE", "PROPOSE", "BRANCH_MUTATE", "REVIEW_CHALLENGE",
    "MERGE_LOW_EFFECT", "EFFECT_GATED",
}
ALLOWED_PUBLIC_SAFETY = {
    "PUBLIC_SAFE", "PUBLIC_SAFE_WITH_REDACTION", "PRIVATE_ONLY", "UNKNOWN",
}
ALLOWED_CONFIDENTIALITY = {"PUBLIC", "PRIVATE", "RESTRICTED", "UNKNOWN"}
ALLOWED_OPS = {
    "ADD", "QUALIFY", "CHALLENGE", "LINK", "INDEX", "HIGHLIGHT",
    "DEPRECATE", "RESTRUCTURE", "PROJECT",
}

NONCLAIMS = [
    "COMPILATION_NE_ACCEPTANCE",
    "COMPILATION_NE_FANOUT",
    "COMPILATION_NE_INTEGRATION",
    "PUBLIC_SAFE_LABEL_NE_PUBLICATION_APPROVAL",
    "DELIVERY_NE_PICKUP",
    "NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF",
    "MERGED_NE_CANON",
]


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def sha256_bytes(data):
    return hashlib.sha256(data).hexdigest().upper()


def unique_sorted(values):
    return sorted({str(v) for v in values if v is not None and str(v)})


def expand_payload(payload):
    if isinstance(payload, list):
        return payload
    if isinstance(payload, dict) and isinstance(payload.get("deltas"), list):
        return payload["deltas"]
    if isinstance(payload, dict):
        return [payload]
    raise ValueError("top level must be an object, array, or {'deltas': [...]} object")


def validate_projection(delta):
    if not isinstance(delta, dict):
        return "projection is not an object"
    missing = sorted(REQUIRED_PROJECTION - set(delta))
    if missing:
        return "missing required keys: " + ", ".join(missing)
    if delta.get("projection_of") != "CoEvoDelta+":
        return "projection_of must equal CoEvoDelta+"
    if delta.get("public_safety") not in ALLOWED_PUBLIC_SAFETY:
        return "invalid public_safety"
    if delta.get("confidentiality") not in ALLOWED_CONFIDENTIALITY:
        return "invalid confidentiality"
    if not isinstance(delta.get("target_domains"), list) or not delta["target_domains"]:
        return "target_domains must be a non-empty array"
    if not isinstance(delta.get("operations"), list) or not delta["operations"]:
        return "operations must be a non-empty array"
    for idx, op in enumerate(delta["operations"]):
        if not isinstance(op, dict):
            return f"operation {idx} is not an object"
        for field in ("op", "subject", "relation", "epistemic_class", "mutation_class"):
            if field not in op:
                return f"operation {idx} missing required field {field}"
        if op.get("op") not in ALLOWED_OPS:
            return f"operation {idx} has invalid op"
        if not op.get("subject") or not op.get("relation"):
            return f"operation {idx} requires subject and relation"
        if op.get("epistemic_class") not in ALLOWED_EPISTEMIC:
            return f"operation {idx} has invalid epistemic_class"
        if op.get("mutation_class") not in ALLOWED_MUTATION:
            return f"operation {idx} has invalid mutation_class"
        confidence = op.get("confidence")
        if confidence is not None and (
            not isinstance(confidence, (int, float)) or confidence < 0 or confidence > 1
        ):
            return f"operation {idx} has invalid confidence"
    return None


def operation_hash(op):
    normalized = {
        "op": op["op"],
        "subject": op["subject"],
        "relation": op["relation"],
        "object": op.get("object"),
        "epistemic_class": op["epistemic_class"],
        "mutation_class": op["mutation_class"],
        "qualifiers": op.get("qualifiers", {}),
        "evidence_refs": unique_sorted(op.get("evidence_refs", [])),
        "confidence": op.get("confidence"),
        "contradictions": unique_sorted(op.get("contradictions", [])),
        "tests": unique_sorted(op.get("tests", [])),
        "expected_benefit": op.get("expected_benefit"),
        "risks": unique_sorted(op.get("risks", [])),
        "wake_conditions": unique_sorted(op.get("wake_conditions", [])),
    }
    return sha256_bytes(canonical(normalized).encode("utf-8"))


def review_flags(delta, op, op_index):
    flags = []
    if not delta.get("observed_base_ref"):
        flags.append("BASE_CURRENTNESS_UNBOUND")
    if not delta.get("receiver_readproof_gate"):
        flags.append("RECEIVER_READPROOF_GATE_UNBOUND")
    if delta.get("public_safety") == "PUBLIC_SAFE" and delta.get("confidentiality") != "PUBLIC":
        flags.append("PUBLIC_SAFE_WITH_NONPUBLIC_CONFIDENTIALITY_REVIEW")
    if op.get("mutation_class") == "MERGE_LOW_EFFECT" and delta.get("public_safety") != "PUBLIC_SAFE":
        flags.append("MERGE_LOW_EFFECT_REQUIRES_PUBLIC_SAFETY_REVIEW")
    return [
        {"delta_id": delta["delta_id"], "operation_index": op_index, "flag": flag}
        for flag in flags
    ]


def compile_record(delta, source_file_sha256, record_index):
    outputs = []
    flags = []
    parent_refs = unique_sorted(delta.get("source_refs", []))
    parent_evidence = unique_sorted(delta.get("evidence_refs", []))
    target_surfaces = unique_sorted(delta.get("candidate_surfaces", []))

    for op_index, op in enumerate(delta["operations"]):
        op_sha = operation_hash(op)
        child_id = f"{delta['delta_id']}::op{op_index:03d}::{op_sha[:12]}"
        evidence_refs = unique_sorted(parent_evidence + list(op.get("evidence_refs", [])))
        source_refs = unique_sorted(parent_refs + evidence_refs)
        coevo = {
            "$schema": "https://github.com/CoCivium/CoCivium/schemas/coevo-delta-v0.2.schema.json",
            "delta_id": child_id,
            "session_id": delta["source_session"],
            "observed_at": delta["created_at"],
            "domain": unique_sorted(delta["target_domains"]),
            "subject": op["subject"],
            "relation": op["relation"],
            "object": op.get("object"),
            "typed_operation": op["op"],
            "epistemic_class": op["epistemic_class"],
            "source_refs": source_refs,
            "evidence_refs": evidence_refs,
            "target_surfaces": target_surfaces,
            "mutation_class": op["mutation_class"],
            "authority_ceiling": delta["authority_ceiling"],
            "confidentiality": delta["confidentiality"],
            "public_safety": delta["public_safety"],
            "qualifiers": op.get("qualifiers", {}),
            "collision_domain": delta.get("collision_domain"),
            "observed_base_ref": delta.get("observed_base_ref"),
            "supersedes": unique_sorted(delta.get("supersedes", [])),
            "next_receiver": delta["next_receiver"],
            "next_gate": delta["next_gate"],
            "receiver_readproof_gate": delta.get("receiver_readproof_gate"),
            "nonclaims": unique_sorted(delta.get("nonclaims", [])),
            "source_projection_id": delta["delta_id"],
            "source_projection_file_sha256": source_file_sha256,
            "source_projection_record_index": record_index,
            "source_operation_index": op_index,
            "source_operation_sha256": op_sha,
        }
        for field in (
            "confidence", "contradictions", "tests", "expected_benefit",
            "risks", "wake_conditions",
        ):
            if field in op:
                value = op[field]
                if field in {"contradictions", "tests", "risks", "wake_conditions"}:
                    value = unique_sorted(value)
                coevo[field] = value
        outputs.append(coevo)
        flags.extend(review_flags(delta, op, op_index))
    return outputs, flags


def compile_paths(paths):
    source_files = []
    rejected = []
    compiled = []
    flags = []
    seen_projection_ids = set()

    raw_sources = []
    for path_text in paths:
        raw = Path(path_text).read_bytes()
        raw_sources.append({"sha256": sha256_bytes(raw), "bytes": len(raw), "raw": raw})

    unique_sources = {}
    for source in raw_sources:
        unique_sources.setdefault(source["sha256"], source)

    for digest in sorted(unique_sources):
        source = unique_sources[digest]
        source_files.append({"sha256": digest, "bytes": source["bytes"]})
        try:
            payload = json.loads(source["raw"].decode("utf-8"))
            records = expand_payload(payload)
        except Exception as exc:
            rejected.append({
                "source_file_sha256": digest,
                "record_index": None,
                "reason": str(exc),
            })
            continue

        for record_index, delta in enumerate(records):
            reason = validate_projection(delta)
            if reason is None and delta["delta_id"] in seen_projection_ids:
                reason = "duplicate projection delta_id in bounded input set"
            if reason is not None:
                rejected.append({
                    "source_file_sha256": digest,
                    "record_index": record_index,
                    "reason": reason,
                })
                continue
            seen_projection_ids.add(delta["delta_id"])
            out, record_flags = compile_record(delta, digest, record_index)
            compiled.extend(out)
            flags.extend(record_flags)

    compiled = sorted(compiled, key=lambda x: x["delta_id"])
    flags = sorted(flags, key=lambda x: (x["delta_id"], x["operation_index"], x["flag"]))
    rejected = sorted(
        rejected,
        key=lambda x: (
            x["source_file_sha256"],
            -1 if x["record_index"] is None else x["record_index"],
        ),
    )

    result = {
        "compiler": "CoSessionProjectionToCoEvo.R0",
        "coverage": {
            "input_files_seen": len(raw_sources),
            "unique_source_files": len(source_files),
            "accepted_projection_records": len(seen_projection_ids),
            "rejected_records": len(rejected),
            "compiled_coevo_deltas": len(compiled),
            "review_flags": len(flags),
        },
        "source_files": source_files,
        "coevo_deltas": compiled,
        "review_flags": flags,
        "rejected_records": rejected,
        "effects": {
            "target_surface_mutations": 0,
            "automatic_fanout": 0,
            "integration_claims": 0,
            "receiver_pickup_claims": 0,
            "canon_changes": 0,
        },
        "next": "FANIN_COMPILED_COEVO_THEN_REVIEW_TARGETED_FANOUT",
        "nonclaims": NONCLAIMS,
    }
    result["compiled_sha256"] = sha256_bytes(canonical(result).encode("utf-8"))
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Compile CoSession relational projections into CoEvoDelta v0.2 candidate objects."
    )
    parser.add_argument("--input", action="append", required=True, help="Input JSON file. Repeat for multiple files.")
    parser.add_argument("--output", required=True, help="Output JSON file.")
    args = parser.parse_args()

    result = compile_paths(args.input)
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(result, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    print("STATE=PASS_SESSION_PROJECTION_TO_COEVO_R0")
    print(f"OUTPUT={output}")
    print(f"COMPILED_SHA256={result['compiled_sha256']}")
    print(f"ACCEPTED_PROJECTIONS={result['coverage']['accepted_projection_records']}")
    print(f"COEVO_DELTAS={result['coverage']['compiled_coevo_deltas']}")
    print(f"REJECTED_RECORDS={result['coverage']['rejected_records']}")
    print(f"REVIEW_FLAGS={result['coverage']['review_flags']}")


if __name__ == "__main__":
    main()
