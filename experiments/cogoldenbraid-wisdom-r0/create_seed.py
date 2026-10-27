#!/usr/bin/env python3
"""Generate original, noncanonical, public-safe design heuristics."""
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parent
sources={
 "golden": {"repo":"CoCivium/CoCivium", "path":"docs/Architecture/COSPEEDO_EXPONENTIAL_PROOF_AND_RECURRENCE_INTERNALIZATION_R0_20261026.md", "git_blob":"717945816cc6cb18dc8a9b5b87093fbab6bb906a"},
 "review": {"repo":"CoCivium/CoCivium", "path":"docs/Governance/COREVIEW_SPINE_R0.md", "git_blob":"e7cf641a991338d6826c586740f188b5db6cb941"},
 "orb": {"repo":"CoCivium/CoCivium", "path":"docs/Architecture/COORBWARE_BEYOND_COSOFTWARE_R0_20261024.md", "git_blob":"cde7189918f48072d86a83fe6d2f16ce6a99f751"},
 "onramp": {"repo":"CoCivium/CoCivium", "path":"docs/Architecture/COAI_EVERGREEN_ONRAMP_COORBWARE_R0_20261026.md", "git_blob":"d7854196975e0590aab2858183cb9be2d13b0ef5"},
}
P=[]
def add(id, text, domain, when, exception, test, keys, source, stage):
 P.append({"id":id,"statement":text,"domain":domain,"applies_when":when,"limitation":exception,
   "next_test":test,"match_phrases":keys,"design_reference":source,"braid_stage":stage,
   "kind":"NORMATIVE_HEURISTIC","status":"CANDIDATE_UNVALIDATED","privacy":"PUBLIC","authority":"NONE"})
add("W01","A good principle says when it would stop being good.","evidence","A claim is treated as a durable rule.","Some ethical commitments are values, not falsifiable empirical predictions.","Find a concrete counterexample and record whether the principle changes.",["falsify","false claim","unfalsifiable","counterexample"],"review","CHALLENGE")
add("W02","Complexity becomes useful only when a newcomer can cross it.","onramp","Visitors face unfamiliar concepts or many paths.","Some specialists legitimately require substantial training.","Compare uncoached first-use success against the plain existing doorway.",["first time","new visitor","newcomer","too many doors","confusing"],"onramp","RECEIVER")
add("W03","A recurring task is not automated until it keeps its promise without rescue.","continuity","Reports or reviews require repeated manual relay.","Human review can be intentionally mandatory for consequential actions.","Miss a scheduled run and independently verify recovery and receiver effect.",["recurring","weekly report","manual relay","every morning","scheduler"],"golden","EFFECT")
add("W04","A thousand workers without a useful handoff are one expensive distraction.","orchestration","Many agents are active but outcomes stall.","Parallel exploration can be valuable before a direct handoff is possible.","Measure independently accepted closures per budget, not agent count.",["agents","workers","swarm","turtles","multiprocess"],"golden","BOUNDED_DEED")
add("W05","Publishing a result makes it addressable, not necessarily noticed.","outreach","Repository links or posts are mistaken for adoption.","Public release is still valuable even before a receiver responds.","Seek opt-in external first-use readproof and record nonresponse honestly.",["published","github","visitors","broadcast","audience"],"golden","RECEIVER")
add("W06","A smaller view stays faithful when its omissions can be inspected.","projection","A graph or work object is reduced to a compact CoOrb.","Intentional deletion, revoked access, and lossy summaries prevent full restoration.","Collapse and expand a pinned object and compare provenance and permissions.",["orb","map","collapse","zoom","hidden evidence","display"],"orb","MEANING")
add("W07","Permission belongs to a particular effect, not to a pleasing interface.","authority","A role, persona, or model proposes an action.","Some public read-only operations require no personal grant.","Attempt an out-of-scope action and prove fail-closed behavior.",["consent","revoked","permission","identity","privacy"],"review","DECISION")
add("W08","A prediction is a question offered early, not an action performed early.","input","A model or UI predicts the next input or recipient.","Safe, explicitly authorized prefetch may be useful when it has no external effect.","Change the input after a suggestion and confirm no stale dispatch or hidden paste.",["predict","suggestion","autocomplete","cursor","typing"],"orb","DECISION")
add("W09","Independence is demonstrated by a loss survived, not an alternate URL listed.","recovery","Several links or mirrors are treated as separate failure domains.","A backup need not run continuously to be useful.","Recover one exact public artifact outside its original provider and check usable state.",["backup","github down","single provider","outage","restore"],"onramp","EFFECT")
add("W10","Retained disagreement is raw material for a better successor.","review","Reviewers or models disagree about a claim.","Repeated unsupported objections can waste scarce attention.","Log one serious challenger objection and test which revision survives.",["reviewer","challenge","dissent","disagree","criticism"],"review","LEARNING")
add("W11","When a predecessor did it better, the next version should learn rather than rename.","priors","A new feature overlaps older code, theory, or outside prior art.","A genuinely new implementation can still add value with measurable differences.","Pin both versions and compare real first-use outcomes, cost, and recovery.",["prior art","old version","duplicate","rewrite","rename"],"review","SOURCE")
add("W12","A trustworthy invitation makes the exit as clear as the entrance.","participation","A visitor is asked to install, enroll, share or contribute.","Exit may require a legally mandated retention period; explain it rather than hide it.","Uninstall or revoke a demo and verify which state is still kept.",["leave","opt out","uninstall","quit","withdraw"],"onramp","RECEIVER")
add("W13","What cannot be measured should remain a question, not become a green light.","uncertainty","A dashboard lacks independent evidence for a reassuring claim.","Action under uncertainty may still be warranted when risks and limits are explicit.","Replace one false-green with a visible UNKNOWN and compare decision quality.",["unknown","dashboard","measurement","no evidence","green status"],"golden","RECEIPT")
add("W14","An evergreen system must know when to sleep, stop and be replaced.","lifecycle","Continuous evolution is mistaken for continuous execution.","Critical safety monitors may require genuinely continuous uptime.","Prove dormancy, wake criteria, bounded budget and a successor handoff.",["evergreen","always on","infinite","endless","dormant"],"onramp","SUCCESSOR")
links=[
 {"from":"W02","to":"W06","kind":"TENSION","reason":"Clarity may require compression, but too much hides evidence."},
 {"from":"W04","to":"W03","kind":"DEPENDENCY","reason":"A team is useful only if completed work reaches a receiver."},
 {"from":"W05","to":"W02","kind":"DEPENDENCY","reason":"A published link needs a newcomer-usable path."},
 {"from":"W08","to":"W07","kind":"GUARD","reason":"Predictions do not create action authority."},
 {"from":"W11","to":"W10","kind":"SUPPORT","reason":"Priors are a form of independent challenge."},
 {"from":"W09","to":"W14","kind":"TENSION","reason":"Dormancy is safe only when restoration is trustworthy."},
 {"from":"W13","to":"W01","kind":"SUPPORT","reason":"Admitting uncertainty makes a rule challengeable."},
 {"from":"W12","to":"W05","kind":"GUARD","reason":"Outreach cannot manufacture a lock-in obligation."}
]
seed={"schema":"CoGoldenBraidWisdomSeed/0.1","state":"PUBLIC_OFFLINE_CANDIDATE_NOT_CANON", "observed_date":"2026-10-27",
 "provenance_note":"Original heuristic wording authored for this prototype. Public architecture links are design context, not empirical proofs or quotations.",
 "design_sources":sources,"principles":P,"typed_relations":links,
 "rails":["HEURISTIC_NE_FACT","CANDIDATE_NE_CANON","PREDICTION_NE_AUTHORITY","ORBIT_VIEW_NE_TRUTH_STORE","ALWAYS_EVOLVE_NE_ALWAYS_RUNNING","VIEW_NE_RECEIVER_ACK"]}
ROOT.joinpath("seed.json").write_text(json.dumps(seed,indent=2,ensure_ascii=True)+"\n",encoding="utf-8")
