#!/usr/bin/env python3
"""Fail-closed draft CoIndexRedir manifest validator; does not claim deployment."""
import json
from pathlib import Path
from urllib.parse import urlparse
import sys
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"ai"/"coindexredir-route-register-r0.json"
obj=json.loads(p.read_text(encoding="utf-8"))
errors=[]
if obj.get("schema")!="CoIndexRedir.RouteRegister.r0": errors.append("schema mismatch")
if obj.get("status")!="DRAFT_NOT_DEPLOYED": errors.append("must not claim deployment")
if obj.get("published_at") is not None: errors.append("published_at must be null before public readproof")
seen=set()
for route in obj.get("routes",[]):
    slug=route.get("slug","")
    if not slug.startswith("/") or slug in seen: errors.append("bad or duplicate slug: "+slug)
    seen.add(slug)
    target=route.get("target","")
    if target.startswith("https://"):
        if urlparse(target).hostname!="github.com": errors.append("target origin not allowed: "+target)
    elif target:
        fp=ROOT/target
        if target.startswith("/") or ".." in Path(target).parts or not fp.is_file(): errors.append("missing target: "+target)
    else: errors.append("missing target for "+slug)
    fb=route.get("fallback","")
    if not fb.startswith("https://github.com/CoCivium/CoCivium"):errors.append("unsafe fallback: "+slug)
    if route.get("state")=="DRAFT_BRANCH" and slug=="/start" and obj.get("status")!="DRAFT_NOT_DEPLOYED":errors.append("unreviewed live start")
if not all(k in obj.get("nonclaims",[]) for k in ["NO_LIVE_REDIRECT","NO_PUBLIC_DOMAIN_CONTROL"]):errors.append("missing release nonclaims")
# CoBestFace+ R0 is a source-level audience projection contract only.
# Fail closed if any front silently inherits authority or if release proof is invented.
bf=obj.get("best_face_candidate")
if not isinstance(bf,dict):
    errors.append("missing CoBestFace candidate")
else:
    if bf.get("alias")!="CoBF+": errors.append("CoBF alias mismatch")
    if bf.get("state")!="SOURCE_CANDIDATE_ONLY_NOT_GLOBAL_OR_DEPLOYED":
        errors.append("CoBF may not imply global deployment")
    front_types={"PUBLIC_HUMAN","PUBLIC_MACHINE","PRIVATE_OPERATOR","HEADLESS_WORKER"}
    if set(bf.get("front_types",[]) if isinstance(bf.get("front_types"),list) else [])!=front_types:
        errors.append("CoBF missing explicit audience-specific fronts")
    for key, expected in {
        "canonical_human_source":"START_HERE.md",
        "canonical_machine_source":"ai/index.json",
        "canonical_evidence_source":"EVERGREEN.md",
    }.items():
        if bf.get(key)!=expected or not (ROOT/expected).is_file():
            errors.append("CoBF missing expected mainline source: "+key)
    if bf.get("proposed_front_door_route")!="/start" or "/start" not in seen:
        errors.append("CoBF target route unqualified")
    rules=set(bf.get("selection_rules",[]) if isinstance(bf.get("selection_rules"),list) else [])
    for needed in [
        "QUALIFIED_LAST_GOOD_GT_UNVERIFIED_NEWEST",
        "SHARED_EVIDENCE_DIFFERENT_RECEIVER_RELATIVE_PROJECTIONS",
        "DISCLOSURE_NE_PUBLISH_PRIVATE_DATA",
        "NO_UNSOLICITED_FOREGROUND_FOCUS_OR_AUDIO",
        "ROUTE_STATUS_NE_WEB_DEPLOYMENT",
        "RECEIVER_ACCEPTANCE_NE_SOURCE_CI",
        "FOREGROUND_VIEW_OPTIONAL_FOR_HEADLESS_WORKERS",
        "SOURCE_CURRENTNESS_AND_SAFE_ROLLBACK_REQUIRED",
    ]:
        if needed not in rules: errors.append("CoBF missing safety rule: "+needed)
    validations=bf.get("validation_targets")
    if not isinstance(validations,dict) or not all(
        isinstance(validations.get(k),str) and len(validations[k])>=20
        for k in ("human_15s","human_60s","machine","operator","release")
    ):
        errors.append("CoBF audience acceptance tests incomplete")
    fed=bf.get("federation_profile")
    if not isinstance(fed,dict):
        errors.append("missing CoFedGRAILS federation profile")
    else:
        if (fed.get("alias")!="CoFedGRAILS+"
                or fed.get("state")!="SOURCE_AND_SYNTHETIC_SHADOW_ONLY"
                or fed.get("epistemic_status")!="GRAILS_ACRONYM_UNRESOLVED_DO_NOT_REDEFINE"):
            errors.append("CoFedGRAILS must remain bounded and meaning-preserving")
        if fed.get("bridge")!="scripts/CoFedGRAILSShadowBridgeR0.py":
            errors.append("CoFedGRAILS bridge pointer missing")
        if fed.get("source_tests")!="scripts/test_cofedgrails_shadow_bridge_r0.py":
            errors.append("CoFedGRAILS test pointer missing")
        for k in ("bridge","source_tests"):
            ref=fed.get(k)
            if not isinstance(ref,str) or not (ROOT/ref).is_file():
                errors.append("CoFedGRAILS broken source pointer: "+k)
        sources=fed.get("governing_public_sources")
        if (not isinstance(sources,list) or len(sources)<4
                or any(not isinstance(p,str) or not (ROOT/p).is_file() for p in sources)):
            errors.append("CoFedGRAILS missing governing source links")
        if fed.get("proof_state")!={"peer_authentication":None,
                                    "independent_receiver_ack":None,
                                    "cold_restore":None,
                                    "live_cross_cell_federation":False}:
            errors.append("CoFedGRAILS claims unverified live federation or receiver ACK")
        constraints=set(fed.get("universal_constraints",[])
                        if isinstance(fed.get("universal_constraints"),list) else [])
        if not {"GLOBAL_DISCOVERY_NE_GLOBAL_AUTHORITY",
                "PRIVATE_NE_PUBLIC_BY_FEDERATION",
                "ONE_ELECTED_ACTUATOR_PER_EFFECT_DOMAIN",
                "SOURCE_CI_NE_FEDERATION_DEPLOYMENT"}.issubset(constraints):
            errors.append("CoFedGRAILS missing local autonomy or safety constraints")
    if bf.get("proof_state")!={"public_host_readproof":None,
                             "independent_first_use":None,
                             "receiver_ack":None,
                             "live_global_binding":False}:
        errors.append("CoBF cannot claim deployment, receiver, or user acceptance")
    nonclaims=set(bf.get("nonclaims",[]) if isinstance(bf.get("nonclaims"),list) else [])
    if not {"THIS_MANIFEST_NE_DEPLOYED_COBF","SOURCE_OR_CI_NE_USER_ACCEPTANCE"}.issubset(nonclaims):
        errors.append("CoBF nonclaims missing")

html=(ROOT/"docs"/"Launch"/"coindexredir_r0"/"index.html").read_text(encoding="utf-8")
for invariant in ['<svg','<title id="artTitle">','aria-live="polite"','prefers-reduced-motion','<script>','No autoplay audio']:
    if invariant not in html: errors.append("missing accessible UI invariant: "+invariant)
print(json.dumps({"state":"FAIL" if errors else "PASS","errors":errors,"scope":"source and structural checks only; not live browser, HTTPS or redirect proof"},indent=2))
sys.exit(bool(errors))
