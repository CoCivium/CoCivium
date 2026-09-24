#!/usr/bin/env python3
import argparse, hashlib, json
from collections import defaultdict
from pathlib import Path

REQ={"delta_id","session_id","observed_at","domain","subject","relation","epistemic_class","source_refs","target_surfaces","mutation_class","authority_ceiling","confidentiality","next_receiver"}
EPI={"OBSERVED","INFERRED","HYPOTHESIS","PREDICTED","PLANNED","PREFERRED","METAPHORICAL","MYTHIC","HUMOROUS","COUNTERFACTUAL","UNKNOWN"}
MUT={"OBSERVE","PROPOSE","BRANCH_MUTATE","REVIEW_CHALLENGE","MERGE_LOW_EFFECT","EFFECT_GATED"}
CONF={"PUBLIC","PRIVATE","RESTRICTED","UNKNOWN"}
ALIASES={
 "rickbar":"rickbarcodesktop","codesktop":"rickbarcodesktop","ux":"couxcosurface","surface":"couxcosurface","coux":"couxcosurface","cosurface":"couxcosurface",
 "humour":"cohumour","humor":"cohumour","coevo":"coautoevocoevo","coautoevo":"coautoevocoevo","grail":"conodemeshgrail","conodemesh":"conodemeshgrail",
 "cosource":"cosourceprovenance","provenance":"cosourceprovenance"
}
NONCLAIMS=["ROUTE_PLAN_NE_TARGET_MUTATION","ROUTE_PLAN_NE_RECEIVER_PICKUP","CANDIDATE_ROUTE_NE_INTEGRATION","PUBLIC_REPO_NE_PUBLICATION_APPROVAL","PRIVATE_REPO_NE_CONFIDENTIALITY_PROOF","FLEET_PROJECTION_NE_FLEET_TOTALITY","COUNT_NE_GLOBAL_CENSUS","MERGED_NE_CANON"]

def canon(x): return json.dumps(x,sort_keys=True,separators=(",",":"),ensure_ascii=False)
def sha(b): return hashlib.sha256(b).hexdigest().upper()
def norm(x): return "".join(c.lower() for c in str(x) if c.isalnum())
def uniq(xs): return sorted({str(x) for x in xs if x is not None and str(x)})
def load(path):
 b=Path(path).read_bytes(); return json.loads(b.decode()),{"sha256":sha(b),"bytes":len(b)}
def expand(x):
 if isinstance(x,list): return x
 if isinstance(x,dict) and isinstance(x.get("coevo_deltas"),list): return x["coevo_deltas"]
 if isinstance(x,dict) and isinstance(x.get("deltas"),list): return x["deltas"]
 if isinstance(x,dict): return [x]
 raise ValueError("CoEvo input must be object/array/wrapper")
def validate(d):
 if not isinstance(d,dict): return "delta is not an object"
 miss=sorted(REQ-set(d))
 if miss: return "missing required keys: "+", ".join(miss)
 if not isinstance(d.get("domain"),list) or not d["domain"]: return "domain must be non-empty array"
 if not d.get("subject") or not d.get("relation"): return "subject and relation required"
 if d.get("epistemic_class") not in EPI: return "invalid epistemic_class"
 if d.get("mutation_class") not in MUT: return "invalid mutation_class"
 if d.get("confidentiality") not in CONF: return "invalid confidentiality"

def lane_index(x):
 out={}
 for row in x.get("domains",[]):
  if isinstance(row,list) and len(row)>=3: out[norm(row[0])]={"domain":row[0],"repos":list(row[1]),"policy":row[2]}
 return out
def cdom(x,lanes):
 k=norm(x)
 if k in lanes:return lanes[k]["domain"]
 a=ALIASES.get(k)
 if a and a in lanes:return lanes[a]["domain"]
def repo_index(x):
 full,short={},{}
 for i in x.get("repositories",[]):
  r=i.get("repo")
  if r:
   rec={"repo":r,"visibility":i.get("visibility","unknown"),"roles":uniq(i.get("roles",[]))}; full[r]=rec; short[r.split("/",1)[-1]]=rec
 return full,short
def profiles(x,lanes):
 out=[]
 for i in x.get("profiles",[]):
  if not isinstance(i,dict) or not i.get("profile_id"): continue
  rec={"profile_id":str(i["profile_id"]),"preferred_repos":uniq(i.get("preferred_repos",[]))}
  for t in ("hot","warm","digest"): rec[t]=uniq([cdom(v,lanes) or str(v) for v in (i.get(t,[]) or [])])
  out.append(rec)
 return sorted(out,key=lambda x:x["profile_id"])
def subtemp(domains,p):
 s=set(domains)
 for t,label in (("hot","HOT"),("warm","WARM"),("digest","DIGEST")):
  m=sorted(s.intersection(p[t]))
  if m:return label,m
 return "SLEEP",[]
def delivery(t): return {"HOT":"CURRENT_DELTA_PACKET","WARM":"DEPENDENCY_OR_RELEVANCE_PACKET","DIGEST":"COMPACT_DIGEST_ONLY"}[t]
def action(m): return {"OBSERVE":"READ_OR_INDEX_ONLY","PROPOSE":"LAND_CANDIDATE_DELTA_OR_BRANCH","REVIEW_CHALLENGE":"LAND_REVIEW_OR_CHALLENGE_CANDIDATE","BRANCH_MUTATE":"CANDIDATE_BRANCH_ONLY","MERGE_LOW_EFFECT":"CANDIDATE_BRANCH_THEN_REVIEW","EFFECT_GATED":"LAND_CANDIDATE_ONLY__DOWNSTREAM_EFFECT_HELD"}.get(m,"HOLD_UNKNOWN_MUTATION_CLASS")
def holds(d,r):
 h=[]; v=r.get("visibility","unknown"); c=d.get("confidentiality","UNKNOWN"); p=d.get("public_safety","UNKNOWN")
 if v=="public":
  if c!="PUBLIC":h.append("CONFIDENTIALITY_COLLISION")
  if p!="PUBLIC_SAFE":h.append("PUBLIC_SAFETY_HOLD")
 elif v=="private":
  if c=="UNKNOWN":h.append("CONFIDENTIALITY_REVIEW_REQUIRED")
 else:h.append("RECEIVER_VISIBILITY_UNKNOWN")
 if d.get("mutation_class")=="EFFECT_GATED":h.append("DOWNSTREAM_EFFECT_GATE")
 return uniq(h)
def state(h,head):
 if "CONFIDENTIALITY_COLLISION" in h:return "HOLD_CONFIDENTIALITY_COLLISION"
 if "PUBLIC_SAFETY_HOLD" in h:return "HOLD_PUBLIC_SAFETY"
 if "RECEIVER_VISIBILITY_UNKNOWN" in h:return "HOLD_RECEIVER_VISIBILITY_UNKNOWN"
 if "CONFIDENTIALITY_REVIEW_REQUIRED" in h:return "REVIEW_CONFIDENTIALITY"
 if "DOWNSTREAM_EFFECT_GATE" in h:return "CANDIDATE_ROUTE_EFFECT_GATED_DOWNSTREAM" if head else "CANDIDATE_ROUTE_EFFECT_GATED_DOWNSTREAM__TARGET_CURRENTNESS_REQUIRED"
 return "CANDIDATE_ROUTE_CURRENTNESS_BOUND" if head else "CANDIDATE_ROUTE_REQUIRES_TARGET_CURRENTNESS"
def triggers(d,h): return uniq((["CONFIDENTIALITY_COLLISION"] if "CONFIDENTIALITY_COLLISION" in h else [])+(["MATERIAL_CONTRADICTION"] if d.get("contradictions") else []))

def plan(coevo,lanes_raw,repos_raw,subs_raw,source_head=None,receiver_heads=None):
 receiver_heads=receiver_heads or {}; lanes=lane_index(lanes_raw); rfull,rshort=repo_index(repos_raw); profs=profiles(subs_raw,lanes)
 raw=expand(coevo); ds=[]; rejected=[]; seen=set()
 for idx,d in enumerate(raw):
  why=validate(d); did=d.get("delta_id") if isinstance(d,dict) else None
  if why is None and did in seen: why="duplicate delta_id in bounded input"
  if why: rejected.append({"record_index":idx,"delta_id":did,"reason":why})
  else: seen.add(did); ds.append(d)
 routes=[]; subs=[]; sleep=0; unrouted=[]; curflags=[]; routeids=set()
 for d in sorted(ds,key=lambda x:str(x["delta_id"])):
  did=str(d["delta_id"]); cds=[]; missing=[]; rm=defaultdict(lambda:{"domains":set(),"policies":set()})
  for rd in d.get("domain",[]):
   cd=cdom(rd,lanes)
   if not cd: missing.append(str(rd)); continue
   cds.append(cd); ln=lanes[norm(cd)]
   for short in ln["repos"]:
    rr=rshort.get(short,{"repo":short}).get("repo",short); rr=rr if "/" in rr else "CoCivium/"+rr
    rm[rr]["domains"].add(cd); rm[rr]["policies"].add(ln["policy"])
  cds=uniq(cds)
  for p in profs:
   temp,matched=subtemp(cds,p); sid="sub:"+sha(canon({"delta_id":did,"profile_id":p["profile_id"],"temperature":temp,"matched_domains":matched}).encode())[:20]
   if temp=="SLEEP": sleep+=1; continue
   gates=["INSTANCE_IDENTITY","CURRENTNESS_CURSOR"]+([] if d.get("confidentiality")=="PUBLIC" else ["CONFIDENTIALITY_CAPABILITY"])
   subs.append({"subscription_id":sid,"delta_id":did,"profile_id":p["profile_id"],"temperature":temp,"matched_domains":matched,"delivery_class":delivery(temp),"delivery_state":"PROFILE_INTEREST_ONLY__INSTANCE_UNBOUND","confidentiality":d.get("confidentiality"),"public_safety":d.get("public_safety","UNKNOWN"),"required_instance_gates":sorted(gates),"preferred_repos":p["preferred_repos"],"effects":{"provider_session_push":0,"session_mutation":0,"authority_transfer":0,"receiver_pickup_claim":0},"nonclaims":["SUBSCRIPTION_NE_AUTHORITY","PROFILE_DELIVERY_NE_SESSION_PICKUP","PROFILE_NE_SESSION_INSTANCE","CURRENTNESS_FOR_ALL_NE_CONTENT_FOR_ALL"]})
  ob=d.get("observed_base_ref"); sc="UNBOUND"
  if source_head:
   if ob is None: sc="SOURCE_BASE_UNBOUND"
   elif source_head in str(ob) or str(ob)==source_head: sc="MATCHES_BOUND_SOURCE_HEAD"
   else:
    sc="SOURCE_BASE_STALE_OR_DIFFERENT"; curflags.append({"delta_id":did,"flag":"CURRENTNESS_FAILURE","observed_base_ref":ob,"bound_source_head":source_head})
  for rr in sorted(rm):
   rec=rfull.get(rr,{"repo":rr,"visibility":"unknown","roles":[]}); h=holds(d,rec); th=receiver_heads.get(rr)
   seed={"delta_id":did,"receiver":rr,"domains":sorted(rm[rr]["domains"]),"typed_operation":d.get("typed_operation"),"subject":d.get("subject"),"relation":d.get("relation")}; rid="route:"+sha(canon(seed).encode())[:20]
   if rid in routeids:continue
   routeids.add(rid); tr=triggers(d,h)
   routes.append({"route_id":rid,"delta_id":did,"matched_domains":sorted(rm[rr]["domains"]),"lane_policies":sorted(rm[rr]["policies"]),"unmatched_domains_on_delta":uniq(missing),"receiver_repo":rr,"receiver_visibility":rec.get("visibility","unknown"),"receiver_roles":rec.get("roles",[]),"candidate_surfaces":uniq(d.get("target_surfaces",[])),"subject":d.get("subject"),"relation":d.get("relation"),"object":d.get("object"),"typed_operation":d.get("typed_operation"),"epistemic_class":d.get("epistemic_class"),"mutation_class":d.get("mutation_class"),"authority_ceiling":d.get("authority_ceiling"),"confidentiality":d.get("confidentiality"),"public_safety":d.get("public_safety","UNKNOWN"),"source_currentness":sc,"observed_base_ref":ob,"target_currentness":"BOUND" if th else "TARGET_CURRENT_HEAD_REQUIRED_BEFORE_WRITE","bound_target_head":th,"proposed_action":action(d.get("mutation_class")),"route_state":state(h,th),"holds":h,"rickbar_attention_triggers":tr,"evidence_refs":uniq(d.get("evidence_refs",[])+d.get("source_refs",[])),"receiver_readproof_gate":d.get("receiver_readproof_gate"),"next_gate":d.get("next_gate"),"effects":{"target_mutation":0,"branch_creation":0,"publication":0,"receiver_pickup_claim":0}})
  if missing:unrouted.append({"delta_id":did,"unmatched_domains":uniq(missing),"state":"DOMAIN_MAPPING_DEBT","next":"REVIEW_EVOLUTION_LANES_BEFORE_TARGET_MUTATION"})
 routes.sort(key=lambda x:(x["receiver_repo"],x["delta_id"],x["route_id"])); subs.sort(key=lambda x:(x["profile_id"],x["delta_id"],x["subscription_id"])); curflags.sort(key=lambda x:(x["delta_id"],x["flag"])); unrouted.sort(key=lambda x:x["delta_id"])
 bydelta=defaultdict(list)
 for s in subs:bydelta[s["delta_id"]].append(s)
 for r in routes:
  short=r["receiver_repo"].split("/",1)[-1]; r["preferred_by_subscription_profiles"]=sorted(s["profile_id"] for s in bydelta.get(r["delta_id"],[]) if short in s.get("preferred_repos",[]))
 fg=[]; hidden=[]; exc=[]
 for r in routes:
  if r["rickbar_attention_triggers"]:fg.append(r["route_id"]); exc.append({"route_id":r["route_id"],"delta_id":r["delta_id"],"receiver_repo":r["receiver_repo"],"triggers":r["rickbar_attention_triggers"],"route_state":r["route_state"]})
  else:hidden.append(r["route_id"])
 for x in rejected:exc.append({"route_id":None,"delta_id":x.get("delta_id"),"receiver_repo":None,"triggers":["RECOVERY_REQUIRED"],"route_state":"INVALID_COEVO_INPUT"})
 for x in curflags:exc.append({"route_id":None,"delta_id":x["delta_id"],"receiver_repo":None,"triggers":["CURRENTNESS_FAILURE"],"route_state":"SOURCE_CURRENTNESS_REVIEW"})
 result={"planner":"CoEvoReceiverFanoutPlanner.R0","coverage":{"input_deltas":len(raw),"accepted_deltas":len(ds),"rejected_input_deltas":len(rejected),"route_proposals":len(routes),"subscription_profiles":len(profs),"subscription_proposals":len(subs),"sleep_relations":sleep,"unrouted_deltas":len(unrouted),"bound_receiver_heads":len(receiver_heads),"source_current_head_bound":source_head is not None,"global_fleet_census":"UNPROVEN"},"route_proposals":routes,"subscription_proposals":subs,"unrouted":unrouted,"rejected_input_deltas":rejected,"currentness_flags":curflags,"rickbar_projection":{"state":"EXCEPTION_FIRST_ROUTE_PLAN__NOT_RUNTIME_BOUND","coverage":{"state":"BOUNDED_INPUT_ONLY","global_fleet_census":"UNPROVEN","source_count":len(raw)},"foreground_route_ids":uniq(fg),"hidden_routine_route_ids":uniq(hidden),"human_blockers":[],"exceptions":sorted(exc,key=lambda x:(str(x.get("delta_id")),str(x.get("route_id")),str(x.get("route_state")))),"background_debt":[{"delta_id":x["delta_id"],"kind":"DOMAIN_MAPPING_DEBT","unmatched_domains":x["unmatched_domains"],"next":x["next"]} for x in unrouted],"runtime_binding":"UNPROVEN","front_door_order":["CoHereNow","Meaning","NextSafeAction","EvidenceDrilldown"],"nonclaims":["NOT_LIVE_FLEET","NOT_GLOBAL_CENSUS","NOT_RICKBAR_RUNTIME","ROUTE_PLAN_NE_TARGET_MUTATION","HUMOUR_NE_STATUS"]},"effects":{"target_mutations":0,"profile_deliveries_executed":0,"provider_session_pushes":0,"branches_created":0,"pull_requests_created":0,"publications":0,"receiver_pickup_claims":0,"canon_changes":0},"next":"BIND_TARGET_HEADS_AND_RECEIVER_INSTANCES_REVIEW_HOLDS_THEN_ELECT_BOUNDED_PROJECTIONS","nonclaims":NONCLAIMS}
 result["plan_sha256"]=sha(canon(result).encode()); return result

def selftest():
 coevo={"coevo_deltas":[
  {"delta_id":"a","session_id":"A","observed_at":"2026-09-23T11:40:00Z","domain":["CoLex+","CoHumour+"],"subject":"x","relation":"links","epistemic_class":"INFERRED","source_refs":[],"target_surfaces":["README.md"],"mutation_class":"PROPOSE","authority_ceiling":"CANDIDATE_ONLY","confidentiality":"PUBLIC","public_safety":"PUBLIC_SAFE","observed_base_ref":"main@HEAD","next_receiver":"fan","receiver_readproof_gate":"EXACT"},
  {"delta_id":"b","session_id":"B","observed_at":"2026-09-23T11:41:00Z","domain":["RickBar+/CoDesktop+"],"subject":"fleet","relation":"projects","epistemic_class":"PLANNED","source_refs":[],"target_surfaces":["RickBar"],"mutation_class":"PROPOSE","authority_ceiling":"CANDIDATE_ONLY","confidentiality":"PRIVATE","public_safety":"PUBLIC_SAFE_WITH_REDACTION","observed_base_ref":"main@HEAD","next_receiver":"fan","receiver_readproof_gate":"EXACT"},
  {"delta_id":"c","session_id":"C","observed_at":"2026-09-23T11:42:00Z","domain":["CoOps+"],"subject":"effect","relation":"requests","epistemic_class":"PLANNED","source_refs":[],"target_surfaces":[],"mutation_class":"EFFECT_GATED","authority_ceiling":"HUMAN","confidentiality":"PRIVATE","public_safety":"PRIVATE_ONLY","observed_base_ref":"main@HEAD","next_receiver":"gate","receiver_readproof_gate":"EXACT"},
  {"delta_id":"d","session_id":"D","observed_at":"2026-09-23T11:43:00Z","domain":["CoNewUnmapped+"],"subject":"new","relation":"maybe","epistemic_class":"HYPOTHESIS","source_refs":[],"target_surfaces":[],"mutation_class":"PROPOSE","authority_ceiling":"CANDIDATE_ONLY","confidentiality":"PUBLIC","public_safety":"PUBLIC_SAFE","observed_base_ref":"main@OLD","next_receiver":"fan","receiver_readproof_gate":"EXACT"}
 ]}
 lanes={"domains":[["CoLex+",["GIBindex","CoCivium"],"LEX"],["CoHumour+",["CoCivium","CoInsights"],"HUMOUR"],["RickBar+/CoDesktop+",["CoCivium","CoAura","CoToolbelt"],"UX"],["CoOps+",["CoSteward","CoToolbelt","CoStacks"],"OPS"]]}
 repos={"repositories":[
  {"repo":"CoCivium/CoCivium","visibility":"public"},{"repo":"CoCivium/GIBindex","visibility":"private"},{"repo":"CoCivium/CoInsights","visibility":"private"},{"repo":"CoCivium/CoAura","visibility":"public"},{"repo":"CoCivium/CoToolbelt","visibility":"private"},{"repo":"CoCivium/CoSteward","visibility":"private"},{"repo":"CoCivium/CoStacks","visibility":"public"}
 ]}
 subs={"profiles":[
  {"profile_id":"CoTheory","warm":["CoLex+"],"digest":["CoHumour+"],"preferred_repos":["CoCivium","CoInsights","GIBindex"]},
  {"profile_id":"CoLanguage","hot":["CoLex+"],"preferred_repos":["GIBindex","CoCivium"]},
  {"profile_id":"CoUX","hot":["RickBar+/CoDesktop+"],"digest":["CoHumour+","CoLex+"],"preferred_repos":["CoCivium","CoAura","CoToolbelt"]},
  {"profile_id":"CoOps","hot":["CoOps+"],"digest":["RickBar+/CoDesktop+"],"preferred_repos":["CoSteward","CoToolbelt","CoStacks","CoCivium"]},
  {"profile_id":"CoHumour","hot":["CoHumour+"],"warm":["CoLex+"],"preferred_repos":["CoInsights","CoCivium","GIBindex"]}
 ]}
 out=plan(coevo,lanes,repos,subs,"HEAD",{})
 assert out["coverage"]["route_proposals"]==9 and out["coverage"]["subscription_proposals"]==7
 assert out["coverage"]["unrouted_deltas"]==1 and len(out["rickbar_projection"]["foreground_route_ids"])==3
 assert out["rickbar_projection"]["human_blockers"]==[] and all(v==0 for v in out["effects"].values())
 print("SELFTEST=PASS_ROUTES_9__SUBSCRIPTIONS_7__FOREGROUND_3__HUMAN_BLOCKERS_0__ZERO_EFFECTS")
 print("PLAN_SHA256="+out["plan_sha256"])

def main():
 p=argparse.ArgumentParser(); p.add_argument("--selftest",action="store_true"); p.add_argument("--input"); p.add_argument("--evolution-lanes"); p.add_argument("--repo-role-map"); p.add_argument("--subscription-profiles"); p.add_argument("--output"); p.add_argument("--source-current-head"); p.add_argument("--receiver-heads"); a=p.parse_args()
 if a.selftest:return selftest()
 if not all([a.input,a.evolution_lanes,a.repo_role_map,a.subscription_profiles,a.output]):raise SystemExit("FAIL_CLOSED__INPUT_LANES_REPO_MAP_SUBSCRIPTIONS_OUTPUT_REQUIRED")
 coevo,cm=load(a.input); lanes,lm=load(a.evolution_lanes); repos,rm=load(a.repo_role_map); subscriptions,sm=load(a.subscription_profiles); heads={}; hm=None
 if a.receiver_heads:
  heads,hm=load(a.receiver_heads)
  if not isinstance(heads,dict):raise SystemExit("receiver-heads must be JSON object")
 out=plan(coevo,lanes,repos,subscriptions,a.source_current_head,heads); out["inputs"]={"coevo":cm,"evolution_lanes":lm,"repo_role_map":rm,"subscription_profiles":sm,"receiver_heads":hm}; out["plan_sha256"]=sha(canon({k:v for k,v in out.items() if k!="plan_sha256"}).encode())
 path=Path(a.output); path.parent.mkdir(parents=True,exist_ok=True); path.write_text(json.dumps(out,indent=2,sort_keys=True,ensure_ascii=False)+"\\n",encoding="utf-8")
 c=out["coverage"]; print("STATE=PASS_COEVO_RECEIVER_FANOUT_PLAN_R0"); print(f"OUTPUT={path}"); print(f"PLAN_SHA256={out['plan_sha256']}"); print(f"INPUT_DELTAS={c['input_deltas']}"); print(f"ACCEPTED_DELTAS={c['accepted_deltas']}"); print(f"REJECTED_INPUT_DELTAS={c['rejected_input_deltas']}"); print(f"ROUTE_PROPOSALS={c['route_proposals']}"); print(f"SUBSCRIPTION_PROPOSALS={c['subscription_proposals']}"); print(f"UNROUTED_DELTAS={c['unrouted_deltas']}"); print(f"RICKBAR_FOREGROUND={len(out['rickbar_projection']['foreground_route_ids'])}"); print("HUMAN_BLOCKERS=0")
if __name__=="__main__":main()
