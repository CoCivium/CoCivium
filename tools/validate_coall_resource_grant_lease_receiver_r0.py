#!/usr/bin/env python3
import copy
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
    return True

def main():
    d=json.loads(FIXTURE.read_text(encoding="utf-8"))
    gs=json.loads(GRANT_SCHEMA.read_text(encoding="utf-8"))
    ls=json.loads(LEASE_SCHEMA.read_text(encoding="utf-8"))
    src=d["source_bindings"]
    for path_key,sha_key in [
        ("convergence_projection_path","convergence_projection_blob_sha"),
        ("coevo_union_schema_path","coevo_union_schema_blob_sha")
    ]:
        if git_blob(src[path_key])!=src[sha_key]:
            fail("SOURCE_DRIFT:"+src[path_key])

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
        got="VALID" if simple_validate(base,schema) else "INVALID"
        if got!=n["expected"]: fail("NEGATIVE:"+n["id"]+":"+got)

    print(json.dumps({
        "STATE":"PASS_COALL_RESOURCE_GRANT_LEASE_INTERFACE_RECEIVER_R0",
        "grant_schema":"CoResourceGrant.R0",
        "lease_schema":"CoResourceLease.R0",
        "energet_projection":energet,
        "coops_projection":coops,
        "negative_case_count":len(d["negative_cases"]),
        "real_resource_execution_count":0,
        "runtime_adoption":False,
        "rails":d["rails"]
    },separators=(",",":")))

if __name__=="__main__":
    main()
