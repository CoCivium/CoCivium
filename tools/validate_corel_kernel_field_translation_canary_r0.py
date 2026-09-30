#!/usr/bin/env python3
import argparse
import hashlib
import json
import subprocess
from pathlib import Path

FIXTURE=Path("fixtures/relations/co_rel_kernel_field_translation_canary_r0.json")

NULL_PREDICATES={
    "EXPECTED_BUT_MISSING","IMPOSSIBLE","FORBIDDEN","UNKNOWN_RELATION",
    "NOT_YET_OBSERVED","ONCE_EXISTED","COUNTERFACTUALLY_PRESENT"
}

def fail(msg):
    raise SystemExit(f"FAIL: {msg}")

def git_blob(ref,path):
    return subprocess.check_output(["git","rev-parse",f"{ref}:{path}"],text=True).strip()

def canonical_sha(obj):
    return hashlib.sha256(json.dumps(obj,sort_keys=True,separators=(",",":")).encode("utf-8")).hexdigest().upper()

def causal_translate(status):
    if status=="causal":
        return {"state":"MAPPED_WITH_DECLARED_LIMITS","field_status":"CAUSAL_CANDIDATE","nonclaims":["MAPPING_NE_EQUIVALENCE","CAUSAL_NE_CAUSAL_SUPPORTED_BY_TRANSLATION"]}
    if status=="possibly_causal":
        return {"state":"MAPPED_WITH_DECLARED_LIMITS","field_status":"CAUSAL_CANDIDATE","nonclaims":["MAPPING_NE_EQUIVALENCE"]}
    if status=="non_causal":
        return {"state":"MAPPED_WITH_DECLARED_LIMITS","field_status":"NONCAUSAL","nonclaims":["MAPPING_NE_EQUIVALENCE","NONCAUSAL_NE_ACAUSAL_INFLUENCE"]}
    if status=="unknown":
        return {"state":"MAPPED_WITH_DECLARED_LIMITS","field_status":"UNKNOWN_CAUSAL_STATUS","nonclaims":["MAPPING_NE_EQUIVALENCE","UNKNOWN_NE_CAUSALITY_NOT_APPLICABLE"]}
    if status=="mixed":
        return {"state":"HOLD_COMPOSITE_REQUIRED","field_status":None,"nonclaims":["MAPPING_NE_EQUIVALENCE","MIXED_NE_FORCED_SINGLE_FIELD_VALUE"]}
    fail(f"unknown kernel causal status {status!r}")

def absence_translate(source,destination_need):
    rid=source.get("rel_id")
    predicate=source.get("predicate")
    provenance=source.get("provenance")
    if not rid or not predicate or not isinstance(provenance,list) or not provenance:
        fail("absence translation requires source identity and provenance")

    if predicate not in NULL_PREDICATES:
        return {
            "state":"NOT_AN_ABSENCE_PREDICATE",
            "create_absence_relatum":False,
            "field_relatum":None,
            "nonclaims":["ORDINARY_RELATION_NE_ABSENCE"]
        }

    if not destination_need.get("absence_participant"):
        return {
            "state":"PRESERVE_KERNEL_ABSENCE_PREDICATE_ONLY",
            "create_absence_relatum":False,
            "field_relatum":None,
            "nonclaims":["ABSENCE_PREDICATE_NE_ABSENCE_RELATUM","ABSENCE_NE_NONEXISTENCE"]
        }

    return {
        "state":"PROJECT_ABSENCE_PARTICIPANT",
        "create_absence_relatum":True,
        "field_relatum":{
            "ref":f"absence:projection:{rid}",
            "kind":"ABSENCE",
            "label":f"Projection of {predicate} from {rid}",
            "scope_note":"Projection-scoped absence participant; source predicate remains authoritative."
        },
        "source_binding":{
            "rel_id":rid,
            "predicate":predicate,
            "provenance":provenance,
            "observer":source.get("observer"),
            "time":source.get("time")
        },
        "translation_provenance":[f"source-relation:{rid}",*[f"source-provenance:{x}" for x in provenance]],
        "nonclaims":[
            "ABSENCE_PREDICATE_NE_ABSENCE_RELATUM",
            "ABSENCE_NE_NONEXISTENCE",
            "NO_EVIDENCE_NE_EVIDENCE_OF_ABSENCE",
            "ABSENCE_RELATUM_NE_INDEPENDENT_ENTITY_CLAIM",
            "DUAL_REPRESENTATION_NE_DUPLICATE_TRUTH",
            "PROJECTION_RELATUM_NE_SOURCE_ENTITY"
        ]
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--field-ref",required=True)
    args=ap.parse_args()

    fx=json.loads(FIXTURE.read_text(encoding="utf-8"))
    src=fx["source_bindings"]

    if git_blob("HEAD",src["adjudication_path"])!=src["adjudication_blob_sha"]:
        fail("adjudication blob drift")
    if git_blob("HEAD",src["kernel_schema_path"])!=src["kernel_schema_blob_sha"]:
        fail("kernel schema blob drift")

    field_head=subprocess.check_output(["git","rev-parse",args.field_ref],text=True).strip()
    if field_head!=src["field_head"]:
        fail("frozen field head drift")
    if git_blob(args.field_ref,src["field_schema_path"])!=src["field_schema_blob_sha"]:
        fail("field schema blob drift")

    adj=json.loads(subprocess.check_output(["git","show",f"HEAD:{src['adjudication_path']}"]).decode("utf-8"))
    decisions={d["decision_id"] for d in adj.get("decisions",[])}
    if decisions!=set(src["expected_decisions"]):
        fail("adjudication decision set drift")

    kernel_schema=json.loads(subprocess.check_output(["git","show",f"HEAD:{src['kernel_schema_path']}"]).decode("utf-8"))
    field_schema=json.loads(subprocess.check_output(["git","show",f"{args.field_ref}:{src['field_schema_path']}"]).decode("utf-8"))
    kernel_statuses=set(kernel_schema["properties"]["causal_status"]["enum"])
    field_statuses=set(field_schema["properties"]["relations"]["items"]["properties"]["causal_status"]["enum"])
    field_kinds=set(field_schema["properties"]["relata"]["items"]["properties"]["kind"]["enum"])

    causal_supported=0
    not_applicable=0
    mixed_single=0
    absence_created=0
    ordinary_misreified=0

    for c in fx["cases"]:
        if c["kind"]=="causal":
            status=c["source"]["causal_status"]
            if status not in kernel_statuses:
                fail(f"{c['id']}: source causal status absent from kernel schema")
            got=causal_translate(status)
            exp=c["expected"]
            if got["state"]!=exp["state"] or got["field_status"]!=exp["field_status"]:
                fail(f"{c['id']}: causal translation mismatch")
            if exp["required_nonclaim"] not in got["nonclaims"]:
                fail(f"{c['id']}: required nonclaim missing")
            if got["field_status"] is not None and got["field_status"] not in field_statuses:
                fail(f"{c['id']}: translated status absent from field schema")
            causal_supported += int(got["field_status"]=="CAUSAL_SUPPORTED")
            not_applicable += int(got["field_status"]=="CAUSALITY_NOT_APPLICABLE")
            mixed_single += int(status=="mixed" and got["field_status"] is not None)
        elif c["kind"]=="absence":
            got=absence_translate(c["source"],c["destination_need"])
            exp=c["expected"]
            if got["state"]!=exp["state"] or got["create_absence_relatum"]!=exp["create_absence_relatum"]:
                fail(f"{c['id']}: absence translation mismatch")
            if got["create_absence_relatum"]:
                if got["field_relatum"]["kind"]!=exp["relatum_kind"] or got["field_relatum"]["kind"] not in field_kinds:
                    fail(f"{c['id']}: invalid projected absence kind")
                if got["source_binding"]["rel_id"]!=c["source"]["rel_id"] or got["source_binding"]["provenance"]!=c["source"]["provenance"]:
                    fail(f"{c['id']}: source provenance not exact")
                if got["source_binding"].get("observer")!=c["source"].get("observer") or got["source_binding"].get("time")!=c["source"].get("time"):
                    fail(f"{c['id']}: source context not preserved")
                for rail in exp.get("required_nonclaims",[]):
                    if rail not in got["nonclaims"]:
                        fail(f"{c['id']}: absence nonclaim missing {rail}")
                absence_created += 1
            if c["source"]["predicate"] not in NULL_PREDICATES and got["create_absence_relatum"]:
                ordinary_misreified += 1
        else:
            fail(f"{c['id']}: unknown case kind")

    observed={
        "case_count":len(fx["cases"]),
        "automatic_causal_supported_promotions":causal_supported,
        "automatic_causality_not_applicable_promotions":not_applicable,
        "mixed_forced_single_values":mixed_single,
        "absence_participants_created":absence_created,
        "ordinary_relations_misreified_as_absence":ordinary_misreified
    }
    if observed!=fx["expected_summary"]:
        fail("summary mismatch "+json.dumps({"observed":observed,"expected":fx["expected_summary"]},sort_keys=True))

    receipt={
        "STATE":"PASS_COREL_KERNEL_FIELD_TRANSLATION_R0",
        "checked_out_head_sha":subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip(),
        "field_head":field_head,
        "adjudication_blob":src["adjudication_blob_sha"],
        "kernel_schema_blob":src["kernel_schema_blob_sha"],
        "field_schema_blob":src["field_schema_blob_sha"],
        "fixture_semantic_sha256":canonical_sha(fx),
        **observed,
        "rails":[
            "CAUSAL_NE_CAUSAL_SUPPORTED_BY_TRANSLATION",
            "UNKNOWN_NE_CAUSALITY_NOT_APPLICABLE",
            "MIXED_NE_FORCED_SINGLE_FIELD_VALUE",
            "ABSENCE_PREDICATE_NE_ABSENCE_RELATUM",
            "ABSENCE_RELATUM_NE_INDEPENDENT_ENTITY_CLAIM",
            "ORDINARY_RELATION_NE_ABSENCE",
            "TRANSLATION_PASS_NE_SEMANTIC_EQUIVALENCE"
        ]
    }
    print(json.dumps(receipt,separators=(",",":")))

if __name__=="__main__":
    main()
