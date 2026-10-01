#!/usr/bin/env python3
import argparse
import copy
import hashlib
import json
import subprocess
from pathlib import Path

GRANT_SCHEMA=Path("schemas/co-resource-grant-r0.schema.json")
LEASE_SCHEMA=Path("schemas/co-resource-lease-r0.schema.json")
FIXTURE=Path("fixtures/cocivia/coall_resource_grant_lease_receiver_canary_r0.json")

def fail(msg):
    raise SystemExit("FAIL:"+msg)

def git_blob(path):
    return subprocess.check_output(["git","rev-parse",f"HEAD:{path}"],text=True).strip()

def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj,sort_keys=True,separators=(",",":")).encode("utf-8")
    ).hexdigest().upper()

def simple_validate(obj, schema):
    if not isinstance(obj, dict):
        return False
    required=set(schema.get("required",[]))
    if not required.issubset(obj):
        return False
    props=schema.get("properties",{})
    if schema.get("additionalProperties") is False and any(k not in props for k in obj):
        return False
    for k,v in obj.items():
        rule=props.get(k,{})
        if "const" in rule and v!=rule["const"]:
            return False
        if "enum" in rule and v not in rule["enum"]:
            return False
        t=rule.get("type")
        allowed=t if isinstance(t,list) else [t] if t else []
        if v is None and "null" in allowed:
            continue
        if t=="string" and not isinstance(v,str): return False
        if t=="integer" and (not isinstance(v,int) or isinstance(v,bool)): return False
        if t=="number" and (not isinstance(v,(int,float)) or isinstance(v,bool)): return False
        if t=="boolean" and not isinstance(v,bool): return False
        if t=="array" and not isinstance(v,list): return False
        if t=="object" and not isinstance(v,dict): return False
        if isinstance(v,str) and rule.get("minLength",0)>len(v): return False
        if isinstance(v,(int,float)) and not isinstance(v,bool) and "minimum" in rule and v<rule["minimum"]: return False
        if isinstance(v,dict) and rule.get("type")=="object":
            if not simple_validate(v,rule): return False
        if isinstance(v,list) and rule.get("type")=="array":
            item=rule.get("items",{})
            for x in v:
                if item.get("type")=="string" and not isinstance(x,str): return False
                if isinstance(x,str) and item.get("minLength",0)>len(x): return False
            if len(v)<rule.get("minItems",0): return False
    if obj.get("schema")=="CoResourceGrant.R0" and obj.get("state")=="ACTIVE":
        consent=obj.get("consent_evidence")
        if not isinstance(consent,dict) or consent.get("explicit_accept") is not True:
            return False
    return True

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--output")
    args=ap.parse_args()

    d=json.loads(FIXTURE.read_text(encoding="utf-8"))
    gs=json.loads(GRANT_SCHEMA.read_text(encoding="utf-8"))
    ls=json.loads(LEASE_SCHEMA.read_text(encoding="utf-8"))
    src=d["source_bindings"]
    for path_key,sha_key in [
        ("convergence_projection_path","convergence_projection_blob_sha"),
        ("coevo_union_schema_path","coevo_union_schema_blob_sha"),
        ("resource_field_aggregation_path","resource_field_aggregation_blob_sha")
    ]:
        if git_blob(src[path_key])!=src[sha_key]:
            fail("SOURCE_DRIFT:"+src[path_key])

    aggregation=json.loads(Path(src["resource_field_aggregation_path"]).read_text(encoding="utf-8"))
    source_grant=next(x for x in aggregation["grants"] if x["grant_id"]=="G-D-COMP")
    g=d["grant"]
    expected_from_source={
        "grant_id":source_grant["grant_id"],
        "participant_or_owner":"participant:"+source_grant["participant_id"],
        "resource_class":source_grant["resource_class"],
        "purpose_scope":source_grant["purposes"][0],
        "privacy_scope":source_grant["privacy_scope"],
        "state":source_grant["state"],
        "capacity":source_grant["capacity_units"],
        "consent_evidence":{
            "explicit_accept":source_grant["explicit_accept"],
            "evidence_ref":"source-object:"+source_grant["grant_id"]
        },
        "revocation":g["revocation"],
        "provenance":["fixtures/cocivia/coall_resource_field_aggregation_r0.json#G-D-COMP"],
        "current":True
    }
    if g!=expected_from_source:
        fail("GRANT_SOURCE_PROJECTION_DRIFT")

    if not simple_validate(d["grant"],gs): fail("GRANT_VALID_CASE")
    if not simple_validate(d["lease"],ls): fail("LEASE_VALID_CASE")

    ep=d["expected_projection"]
    energet={
        "compute":d["grant"]["capacity"],
        "qualitative":f"{d['grant']['state']}_SCOPED_GRANT__{d['grant']['purpose_scope']}"
    }
    coops={
        "reservation_state":d["lease"]["lease_state"],
        "holder":d["lease"]["work_or_holder_id"],
        "fence_or_epoch":d["lease"]["fence_or_epoch"],
        "effect_authority":d["lease"]["effect_authority"]
    }
    if energet!=ep["energet"]: fail("ENERGET_PROJECTION")
    if coops!=ep["coops"]: fail("COOPS_PROJECTION")
    if coops["effect_authority"] is not False: fail("EFFECT_AUTHORITY_DRIFT")

    for n in d["negative_cases"]:
        base=copy.deepcopy(d[n["target"]])
        schema=gs if n["target"]=="grant" else ls
        if "drop" in n: base.pop(n["drop"],None)
        if "extra_key" in n: base[n["extra_key"]]=n["extra_value"]
        if "set_key" in n: base[n["set_key"]]=n["set_value"]
        if "set_consent_explicit_accept" in n:
            base["consent_evidence"]["explicit_accept"]=n["set_consent_explicit_accept"]
        got="VALID" if simple_validate(base,schema) else "INVALID"
        if got!=n["expected"]: fail("NEGATIVE:"+n["id"]+":"+got)

    head=subprocess.check_output(["git","rev-parse","HEAD"],text=True).strip()
    receipt={
        "STATE":"PASS_COALL_RESOURCE_GRANT_LEASE_INTERFACE_RECEIVER_READPROOF_R0",
        "receiver_identity":"github-actions:PR137_RESOURCE_INTERFACE_RECEIVER_R0",
        "checked_out_head_sha":head,
        "exact_objects":[
            {"path":str(GRANT_SCHEMA),"git_blob_sha":git_blob(str(GRANT_SCHEMA))},
            {"path":str(LEASE_SCHEMA),"git_blob_sha":git_blob(str(LEASE_SCHEMA))},
            {"path":str(FIXTURE),"git_blob_sha":git_blob(str(FIXTURE))}
        ],
        "fixture_semantic_sha256":canonical_sha(d),
        "grant_schema":"CoResourceGrant.R0",
        "lease_schema":"CoResourceLease.R0",
        "grant_source_object":"G-D-COMP",
        "grant_explicit_accept_preserved":True,
        "energet_projection":energet,
        "coops_projection":coops,
        "negative_case_count":len(d["negative_cases"]),
        "receiver_exact_object_readproof":"PASS",
        "bounded_lifecycle_interpretation":"PICKED_UP_BY_PR137_RESOURCE_INTERFACE_RECEIVER",
        "integration_state":"UNPROVEN",
        "real_resource_execution_count":0,
        "runtime_adoption":False,
        "rails":d["rails"]+[
            "PICKED_UP_NE_INTEGRATED",
            "SCHEMA_PRESENCE_NE_RUNTIME_ADOPTION"
        ]
    }

    if args.output:
        out=Path(args.output)
        if out.exists(): fail("NO_CLOBBER_OUTPUT")
        out.parent.mkdir(parents=True,exist_ok=True)
        out.write_text(json.dumps(receipt,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(receipt,separators=(",",":")))

if __name__=="__main__":
    main()
