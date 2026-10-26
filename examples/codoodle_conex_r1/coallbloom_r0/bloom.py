#!/usr/bin/env python3
"""CoAllBloom first bounded proof R0: source-bound, deterministic proposals ONLY.

No device I/O, network, model calls, user data reads, login, execution or sends.
The one elected candidate is a shadow review question, not a worker/effect.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
from pathlib import Path

SCHEMA = "CoAll.CoAllBloom.PublicSeed.R0"
OUT = "CoAll.CoAllBloom.FirstProof.R0"
MAX_CANDIDATES = 10
MAX_DONORS = 8
KINDS = (
    "CONVENTIONAL_GUIDE", "CONVENTIONAL_SOURCE_CHECK", "INVERSION", "NULL",
    "ORTHOGONAL_ELSE", "CROSS_SUBSTRATE", "SPIRITUAL_SYMBOLIC", "PHYSICAL_MEASURABLE",
    "ET_GD_INTERPRETATION", "FALSIFIER"
)
EMPR = "EMPIRICAL_TESTABLE"
EXEM = "EXISTING_PUBLIC_SOURCE_ONLY"
NONEMP = "SYMBOLIC_NONEMPIRICAL"
ANALOGY = "CROSS_DOMAIN_ANALOGY"
HYP = "HYPOTHESIS_UNVERIFIED"

# All candidates use the same declared five-factor scoring function. "Blind"
# here means ranking is computed from these factors, not the candidate label.
# It does NOT mean an independent human or model completed a blinded review.
DESIGNS = (
 ("CONVENTIONAL_GUIDE", "Provide a one-task human or machine guide with source/version and explicit rights.", EXEM, "Verify that current guide preserves the one-task and no-login default.", (3,4,5,0,1)),
 ("CONVENTIONAL_SOURCE_CHECK", "Check exact onramp source and donor revisions before offering a safe task.", EXEM, "Check five source pins and record a before/after drift hold; no receiver effect.", (5,5,5,0,1)),
 ("INVERSION", "Ask how an autonomous onramp could fail its users or create lock-in.", HYP, "Show missing receiver proof, source expiry and accidental new-account pressure.", (5,4,4,0,2)),
 ("NULL", "Admit nobody; allow a client to inspect the public source and leave.", HYP, "Confirm no privilege, account, subscription or worker was created.", (4,3,5,0,0)),
 ("ORTHOGONAL_ELSE", "Offer a human-only, non-model contribution path without interpreting IA.", HYP, "Compare with the machine route using first-task comprehension, not account count.", (4,4,4,0,2)),
 ("CROSS_SUBSTRATE", "Use seed dispersal only as an analogy for opt-in versioned contributions.", ANALOGY, "Identify where the analogy breaks: consent, custody, authority, recovery.", (3,3,4,1,1)),
 ("SPIRITUAL_SYMBOLIC", "Represent stewardship, generosity and G_d only as optional meaning frames.", NONEMP, "Check that no divine command or physics claim is emitted by the route.", (2,3,4,1,1)),
 ("PHYSICAL_MEASURABLE", "Define measurable latency, compute, energy and accessibility costs for a future receiver.", EMPR, "Hold actual performance until an authorized instrumented receiver exists.", (5,5,2,1,2)),
 ("ET_GD_INTERPRETATION", "Compare independent observer/shared-reference hypotheses without asserting ET or G_d contact.", HYP, "Require separate primary observation, falsifiers and independent replication.", (3,2,2,2,3)),
 ("FALSIFIER", "An independent client cannot cold-resume, acknowledge or recover an exact source version.", HYP, "Seek actual second-encounter receiver readproof; absent proof falsifies any claim of tested evergreen adoption.", (5,5,2,1,2)),
)


def canon(obj):
    return (json.dumps(obj, sort_keys=True, ensure_ascii=True, separators=(",", ":")) + "\n").encode("utf-8")


def digest(obj):
    return hashlib.sha256(canon(obj)).hexdigest()


def validate_seed(obj):
    expected = {"schema","id","purpose","scope","authority","recipient","uncertainty","contextual_et_gd_lane","source_donors"}
    if not isinstance(obj, dict) or set(obj) != expected:
        raise ValueError("HOLD_SEED_FIELDS")
    if obj["schema"] != SCHEMA or obj["scope"] != "PUBLIC_SYNTHETIC_ONLY" or obj["authority"] != "NONE":
        raise ValueError("HOLD_SOURCE_SCOPE_AUTHORITY")
    if not isinstance(obj["id"], str) or not re.fullmatch("[a-z0-9-]{5,80}", obj["id"]):
        raise ValueError("HOLD_SOURCE_ID")
    if not isinstance(obj["purpose"], str) or not 20 <= len(obj["purpose"]) <= 500:
        raise ValueError("HOLD_SOURCE_PURPOSE")
    if obj["recipient"] != "INDEPENDENT_RECEIVER_UNPROVEN" or obj["uncertainty"] != "HYPOTHESIS_OR_SOURCE_ONLY":
        raise ValueError("HOLD_RECEIVER_OR_EVIDENCE_STATUS")
    if not isinstance(obj["contextual_et_gd_lane"], bool):
        raise ValueError("HOLD_ET_GD_SCOPE")
    donors=obj["source_donors"]
    if not isinstance(donors,list) or not 3 <= len(donors) <= MAX_DONORS:
        raise ValueError("HOLD_DONOR_COUNT")
    seen=set()
    for item in donors:
        if not isinstance(item,dict) or set(item)!={"path","git_blob"}:
            raise ValueError("HOLD_DONOR_SCHEMA")
        path,sha=item["path"],item["git_blob"]
        if not isinstance(path,str) or path.startswith("/") or ".." in Path(path).parts or "\\" in path or path in seen or path.startswith("."):
            raise ValueError("HOLD_DONOR_PATH")
        if not isinstance(sha,str) or not re.fullmatch("[a-f0-9]{40}",sha):
            raise ValueError("HOLD_DONOR_HASH")
        seen.add(path)
    return obj


def load_seed(path):
    return validate_seed(json.loads(Path(path).read_text(encoding="utf-8")))


def git_blob(data):
    return hashlib.sha1(b"blob "+str(len(data)).encode("ascii")+b"\0"+data).hexdigest()


def verify_donors(seed,root):
    validate_seed(seed)
    root=Path(root).resolve()
    results=[]
    for d in seed["source_donors"]:
        p=(root/d["path"]).resolve()
        if not p.is_relative_to(root) or not p.is_file() or p.is_symlink():
            raise ValueError("HOLD_MISSING_OR_UNSAFE_DONOR: "+d["path"])
        got=git_blob(p.read_bytes())
        if got!=d["git_blob"]:
            raise ValueError("HOLD_DONOR_DRIFT: "+d["path"])
        results.append({"path":d["path"],"git_blob":got,"status":"PASS_EXACT_LOCAL_DONOR_BYTES"})
    return results


def score(factors):
    if len(factors)!=5 or any(isinstance(x,bool) or not isinstance(x,int) or x<0 or x>5 for x in factors):
        raise ValueError("HOLD_SCORE_AXES")
    info,receiver,testable,risk,maintenance=factors
    return 3*info+3*receiver+2*testable-3*risk-maintenance


def make(seed):
    validate_seed(seed)
    salt=digest(seed)
    candidates=[]
    for kind,meaning,epistemic,test,factors in DESIGNS:
        if kind=="ET_GD_INTERPRETATION" and not seed["contextual_et_gd_lane"]:
            continue
        c={"id":hashlib.sha256((salt+":"+kind).encode()).hexdigest()[:24],
           "operator":kind,"meaning":meaning,"epistemic_class":epistemic,
           "next_test":test,"factors":{"information_gain":factors[0],"receiver_value":factors[1],
            "testability":factors[2],"risk":factors[3],"maintenance":factors[4]},
           "shadow_score":score(factors),"authority":"NONE","effect_state":"NOT_RUN",
           "receiver_ack":"UNPROVEN","real_world_claim":"HELD",
           "source_sha256":salt}
        candidates.append(c)
    # Frozen review order cannot be mistaken for a semantic ranking.
    ordered=sorted(candidates,key=lambda x:(-x["shadow_score"],x["id"]))
    elected=ordered[0] if ordered else None
    return {"schema":OUT,"seed_id":seed["id"],"seed_sha256":salt,
      "source_donors":seed["source_donors"],"generated_count":len(candidates),
      "addressable_not_executed":True,"active_model_workers":0,"external_sends":0,
      "candidates":candidates,"ranking": [{"id":x["id"],"operator":x["operator"],"score":x["shadow_score"]} for x in ordered],
      "elected_shadow_candidate":None if elected is None else {"id":elected["id"],"operator":elected["operator"],"status":"ELECTED_FOR_SOURCE_ONLY_CHECK_NOT_EFFECT"},
      "proof_ceiling":"SYNTHETIC_GENERATION_AND_PINNED_SOURCE_CHECK_ONLY",
      "nonclaims":["ALL_ADDRESSABLE_NE_ALL_ACTIVE","INVERSIONS_NE_TRUE_OPPOSITES","MYSTIC_NE_CAUSATION","SPIRITUAL_NE_PHYSICAL","ET_HYPOTHESIS_NE_CONTACT","GD_LABEL_NE_DIVINE_AUTHORITY","IA_UNDEFINED_NE_NEW_PERSON","NO_USER_RECEIVER_PICKUP","NO_MODEL_OR_DEVICE_EXECUTION","TEST_PASS_NE_USER_BENEFIT"]}


def main():
    p=argparse.ArgumentParser();p.add_argument("--seed",type=Path,default=Path(__file__).with_name("seed.json"))
    p.add_argument("--check-donors",type=Path);p.add_argument("--output",type=Path);p.add_argument("--check",action="store_true")
    a=p.parse_args();s=load_seed(a.seed);r=make(s)
    if a.check_donors is not None:
        verify_donors(s,a.check_donors)
    b=canon(r)
    if a.check:
        expected=Path(__file__).with_name("first_proof.json")
        if not expected.is_file() or expected.read_bytes()!=b:
            raise SystemExit("FAIL_DETERMINISTIC_OUTPUT_DRIFT")
        print("PASS_FIRST_PROOF_CHECK",r["generated_count"],r["elected_shadow_candidate"]["operator"])
    elif a.output:
        a.output.parent.mkdir(parents=True,exist_ok=True)
        with a.output.open("xb") as fh: fh.write(b)
        if a.output.read_bytes()!=b: raise RuntimeError("FAIL_RECEIPT_READBACK")
        print("PASS_EXCLUSIVE_WRITE",str(a.output),hashlib.sha256(b).hexdigest())
    else:
        print(b.decode("utf-8"),end="")

if __name__=="__main__":main()
