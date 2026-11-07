#!/usr/bin/env python3
"""CoTeachBack R0: offline source-pinned structured-response evaluator.

No model calls, network, authorization grants, external receipt validation, or training.
The public reference key is a VISIBLE FIXTURE, not a blind independent benchmark.
"""
import argparse
import hashlib
import json
from pathlib import Path

MANIFEST_BLOB = "e9b834f93455012c703eeb8ba9b6585778ea3464"
CHALLENGE_SCHEMA = "CoAll.CoTeachBack.Challenge.R0"
KEY_SCHEMA = "CoAll.CoTeachBack.PublicReferenceKey.R0"
RESPONSE_SCHEMA = "CoAll.CoTeachBack.ReceiverResponse.R0"


def git_blob_sha1(data):
    return hashlib.sha1(("blob %s\0" % len(data)).encode() + data).hexdigest()


def json_file(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def need(test, message):
    if not test:
        raise ValueError(message)


def exact_keys(obj, keys, context):
    need(isinstance(obj, dict), context + ": not object")
    need(set(obj) == set(keys), context + ": unexpected/missing fields")


def validate_and_grade(manifest_bytes, challenge_bytes, key, response):
    need(git_blob_sha1(manifest_bytes) == MANIFEST_BLOB, "SOURCE_PIN_MISMATCH")
    manifest = json.loads(manifest_bytes)
    challenge = json.loads(challenge_bytes)
    need(manifest.get("state") == "PUBLIC_READ_ONLY_CANDIDATE_NOT_GLOBAL_ADOPTION", "MANIFEST_STATE_NOT_SAFE")
    need(manifest.get("authorized_effects_from_this_manifest") == [], "UNAUTHORIZED_SOURCE_EFFECTS")
    need(manifest.get("content_use", {}).get("training") == "NOT_GRANTED_BY_THIS_MANIFEST", "TRAINING_CLAIM_TAMPERED")
    need(manifest.get("agent_interface", {}).get("mcp_resources") == "NOT_DEPLOYED", "FALSE_MCP_CLAIM")
    need(challenge.get("schema") == CHALLENGE_SCHEMA, "CHALLENGE_SCHEMA")
    need(challenge.get("source_git_blob_sha1") == MANIFEST_BLOB, "CHALLENGE_SOURCE_MISMATCH")
    need(challenge.get("policy") == "PUBLIC_OFFLINE_FIXTURE_NO_TRAINING_OR_EXTERNAL_ACTUATION", "CHALLENGE_POLICY")
    qs = challenge.get("questions")
    need(isinstance(qs, list) and len(qs) >= 10, "TOO_FEW_CHALLENGES")
    qualified_sources = {"adoption-manifest"} | {x["id"] for x in manifest["source_index"]}
    qids = set()
    for q in qs:
        exact_keys(q, ["id", "prompt", "choices", "source_ids"], "question")
        need(isinstance(q["id"], str) and q["id"] not in qids, "DUPLICATE_QUESTION")
        qids.add(q["id"])
        need(isinstance(q["prompt"], str) and 6 < len(q["prompt"]) < 1500, "MALFORMED_PROMPT")
        need(isinstance(q["source_ids"], list) and q["source_ids"] and set(q["source_ids"]).issubset(qualified_sources), "UNKNOWN_CHALLENGE_SOURCE")
        need(isinstance(q["choices"], list) and len(q["choices"]) >= 2, "MALFORMED_CHOICES")
        ids = [c["id"] for c in q["choices"]]
        need(len(set(ids)) == len(ids) and all(isinstance(c.get("text"), str) for c in q["choices"]), "MALFORMED_CHOICES")
    need(key.get("schema") == KEY_SCHEMA, "KEY_SCHEMA")
    need(key.get("challenge_sha256") == hashlib.sha256(challenge_bytes).hexdigest(), "KEY_CHALLENGE_PIN_MISMATCH")
    need(key.get("visibility") == "PUBLIC_ANSWER_KEY_NOT_BLIND", "UNTRUSTED_BENCHMARK_CLAIM")
    ka = key.get("answers")
    need(isinstance(ka, list) and len(ka) == len(qs) and {a["id"] for a in ka} == qids, "KEY_QUESTION_MISMATCH")
    km = {a["id"]: a for a in ka}
    for q in qs:
        expected = km[q["id"]]
        exact_keys(expected, ["id", "choice_id", "required_source_ids", "why"], "expected answer")
        need(expected["choice_id"] in {c["id"] for c in q["choices"]}, "KEY_INVALID_CHOICE")
        need(set(expected["required_source_ids"]).issubset(set(q["source_ids"])), "KEY_INVALID_SOURCE")
    exact_keys(response, ["schema", "receiver_id", "receiver_kind", "model_version", "source_git_blob_sha1", "challenge_sha256", "answers", "claimed_authority"], "receiver response")
    need(response["schema"] == RESPONSE_SCHEMA, "RESPONSE_SCHEMA")
    need(isinstance(response["receiver_id"], str) and 1 <= len(response["receiver_id"]) <= 150, "RECEIVER_ID")
    need(response["receiver_kind"] in {"DETERMINISTIC_FIXTURE", "LLM_APPLICATION", "LOCAL_MODEL", "AGENT", "HUMAN", "OTHER"}, "RECEIVER_KIND")
    need(isinstance(response["model_version"], str) and bool(response["model_version"]), "MODEL_VERSION_MISSING")
    need(response["source_git_blob_sha1"] == MANIFEST_BLOB, "RECEIVER_SOURCE_MISMATCH")
    need(response["challenge_sha256"] == hashlib.sha256(challenge_bytes).hexdigest(), "RECEIVER_CHALLENGE_MISMATCH")
    need(response["claimed_authority"] == [], "RECEIVER_TRIED_TO_GRANT_AUTHORITY")
    ans = response["answers"]
    need(isinstance(ans, list) and len(ans) == len(qs), "RECEIVER_ANSWER_COUNT")
    byid = {}
    for a in ans:
        exact_keys(a, ["id", "choice_id", "cited_source_ids"], "receiver answer")
        need(a["id"] in qids and a["id"] not in byid, "RECEIVER_DUPLICATE_OR_UNKNOWN_ID")
        need(isinstance(a["cited_source_ids"], list), "CITATIONS_MALFORMED")
        byid[a["id"]] = a
    per = []
    for q in qs:
        a, e = byid[q["id"]], km[q["id"]]
        choices = {c["id"] for c in q["choices"]}
        need(a["choice_id"] in choices, "INVALID_CHOICE_ID")
        citations = a["cited_source_ids"]
        need(len(citations) == len(set(citations)) and set(citations).issubset(set(q["source_ids"])), "FABRICATED_SOURCE_CITATION")
        passed = a["choice_id"] == e["choice_id"] and set(e["required_source_ids"]).issubset(set(citations))
        per.append({"id": q["id"], "passed": passed, "choice_correct": a["choice_id"] == e["choice_id"], "source_citations_sufficient": set(e["required_source_ids"]).issubset(set(citations))})
    passed = sum(x["passed"] for x in per)
    return {
        "schema": "CoAll.CoTeachBack.LocalScoringReceipt.R0",
        "state": "LOCAL_VISIBLE_KEY_FIXTURE_NOT_INDEPENDENT_MODEL_ADOPTION",
        "source_manifest_git_blob_sha1": MANIFEST_BLOB,
        "challenge_sha256": hashlib.sha256(challenge_bytes).hexdigest(),
        "receiver_id": response["receiver_id"],
        "receiver_kind": response["receiver_kind"],
        "reported_model_version": response["model_version"],
        "receiver_attestation": "UNVERIFIED_SELF_REPORT",
        "challenge_answer_key_visibility": "PUBLIC_NOT_BLIND",
        "score": {"passed": passed, "total": len(per), "percentage": round(100 * passed / len(per), 1)},
        "per_question": per,
        "independent_external_model_ack": "NOT_OBSERVED",
        "weight_change": "NOT_VERIFIED",
        "production_actuation": "NONE",
        "training_grants": [],
        "authority_grants": [],
    }


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--manifest", required=True)
    p.add_argument("--challenge", required=True)
    p.add_argument("--key", required=True)
    p.add_argument("--response", required=True)
    p.add_argument("--output", required=True)
    args = p.parse_args()
    try:
        result = validate_and_grade(Path(args.manifest).read_bytes(), Path(args.challenge).read_bytes(), json_file(args.key), json_file(args.response))
    except (ValueError, KeyError, TypeError, json.JSONDecodeError) as e:
        print(json.dumps({"state": "HOLD_INVALID_RECEIVER_OR_SOURCE", "reason": str(e)}))
        return 2
    Path(args.output).write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"state": result["state"], "score": result["score"], "receiver_attestation": result["receiver_attestation"]}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
