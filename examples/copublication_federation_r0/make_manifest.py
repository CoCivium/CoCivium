#!/usr/bin/env python3
"""Create one bounded, public-source-only CoPublication prototype manifest."""
import json
from pathlib import Path
root = Path(__file__).resolve().parent
source = {
    "repo": "CoCivium/CoCivium",
    "path": "docs/Architecture/COGREAT_REFACT_R0_20261025.md",
    "git_blob_sha1": "9202ab5a8d0bfef509922c8c047363ea7a346ce2",
    "url": "https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COGREAT_REFACT_R0_20261025.md",
    "observed_utc": "2026-10-25",
    "status": "PUBLIC_ARCHITECTURE_CANDIDATE_NOT_RUNTIME"
}
claims = [
    {"id":"C01","text":"Great ReFact proposes that products could expose useful capabilities, not only separate application destinations.","evidence":"PROPOSED_ARCHITECTURE"},
    {"id":"C02","text":"Combining capabilities should preserve identities, disagreements and translation losses rather than pretending products have merged.","evidence":"PROPOSED_ARCHITECTURE"},
    {"id":"C03","text":"Cross-product actions require appropriate permissions and should prefer documented interfaces and reversible, user-authorized adapters.","evidence":"REQUIRED_DESIGN_BOUNDARY"},
    {"id":"C04","text":"A proposed CoOrbWare interaction is an interface direction, not proof of a native multi-device runtime.","evidence":"CURRENT_NONCLAIM"},
    {"id":"C05","text":"A valid first product augmentation canary should leave vendor-native behavior intact and demonstrate removal or rollback.","evidence":"PROPOSED_ACCEPTANCE_TEST"},
    {"id":"C06","text":"Actual time saved, capability gain and independent reader adoption remain hypotheses until measured with appropriate receivers.","evidence":"CURRENT_NONCLAIM"}
]
ids=[c['id'] for c in claims]
source_url=source['url']
other = {
    "public_status":"https://github.com/CoCivium/CoCivium/blob/main/PRELAUNCH.md",
    "first_essay":"https://github.com/CoCivium/CoCivium/blob/main/docs/Outreach/AI_WARS_YOU_WERE_NEVER_SUPPOSED_TO_BE_THE_OPERATING_SYSTEM_R1.md",
    "developer_demo":"https://github.com/CoCivium/CoCivium/blob/main/examples/coprecursor/README.md",
    "research_note":"https://github.com/CoCivium/CoCivium/blob/main/docs/Public/CoTheoryAll_Substack_Draft_2026-10-06.md",
    "public_feedback":"https://github.com/CoCivium/CoCivium/issues"
}
routes = [
    {"id":"curious","label":"Curious reader","headline":"You were never supposed to be the operating system.","promise":"A simple question: could your tools cooperate without turning you into the courier?","entry":"Explore a proposed future where your existing apps remain useful while permitted capabilities connect. No new AI empire is assumed.","task":"Read the AI Wars field note; identify one chore you would like to stop relaying manually.","action_label":"Read the public field note","action_url":other['first_essay'],"claims":ids,"counterpoint":"The simplest improvement might be better built-in app integrations, not an agent layer."},
    {"id":"developer","label":"Developer","headline":"Compose one capability without taking over the product.","promise":"Start with an authorized surface, a testable input and a clean rollback.","entry":"Try a narrow local UI proposal or API adapter with explicit permission, no hidden keyboard interception and exact receipts.","task":"Inspect the CoPreCursor demo and write down an independent acceptance test.","action_label":"Inspect developer example","action_url":other['developer_demo'],"claims":ids,"counterpoint":"An extra orchestration layer may increase failure modes and maintenance costs."},
    {"id":"operator","label":"Vendor or operator","headline":"Your product can stay intact while becoming easier to improve.","promise":"The opportunity is controlled interoperability, not an unauthorized vendor rewrite.","entry":"Consider documented capability interfaces, permission checks, export, audit events, rollback and user choice as product advantages.","task":"Review the Great ReFact checklist; select one reversible pilot with a measurable user benefit.","action_label":"Inspect capability checklist","action_url":source_url,"claims":ids,"counterpoint":"Some tightly integrated native workflows may outperform cross-vendor composition."},
    {"id":"researcher","label":"Researcher","headline":"Can composable interfaces reduce human coordination cost?", "promise":"A falsifiable question, not an assumed improvement.","entry":"Compare an unchanged baseline with an explicitly authorized composed workflow. Report uncertainty, privacy cost and failure cases.","task":"Define a preregistered task measure and a negative control before declaring synergy.","action_label":"Inspect related research framing","action_url":other['research_note'],"claims":ids,"counterpoint":"Observed improvement might result from task familiarity or UI changes, not cross-model intelligence."},
    {"id":"journalist","label":"Journalist","headline":"What exists, what is proposed, and what is missing?", "promise":"One source trail with explicit nonclaims and a challenge path.","entry":"CoCivium has public architectural research and prototypes. A universal CoOrbWare deployment and independent adoption are not established by these source documents.","task":"Check the public readiness statement against the architecture. Write one disconfirming question.","action_label":"Read the public readiness record","action_url":other['public_status'],"claims":ids,"counterpoint":"A polished prototype or published plan is not evidence that people independently use it."},
    {"id":"educator","label":"Educator","headline":"What changes when an app becomes a capability?", "promise":"A classroom-ready comparison with source checking and space for disagreement.","entry":"Contrast a sealed app workflow with a permissioned composition of two abilities. Invite learners to identify data ownership, failure recovery and access barriers.","task":"Ask students to distinguish a design claim from one observed fact and one testable prediction.","action_label":"Read the plain-language field note","action_url":other['first_essay'],"claims":ids,"counterpoint":"A charming diagram can conceal inaccessible controls or ambiguous permissions."}
]
axes = {
 "audience": ["curious","developer","operator","researcher","journalist","educator","artist","librarian","accessibility_reviewer","skeptic"],
 "interest": ["productivity","interoperability","privacy","education","research","accessibility","culture","resilience","open_source","counterexamples"],
 "use_case": ["read","build","compare","challenge","teach","research","document","design","reproduce","archive"],
 "medium": ["essay","short_note","static_diagram","interactive","audio_script","video_storyboard","checklist","code_example","FAQ","plain_text"],
 "depth": ["glance","3_minute","10_minute","deep_dive","expert","intro","historical","current","next_steps","transcript"],
 "lens": ["evidence","accessibility","privacy","economics","operations","history","ethics","design","science","labeled_speculation"],
 "temporal": ["snapshot","current_pointer","difference","timeline","near_future","far_future","historical","planned","counterfactual","unknown"],
 "epistemic": ["observed","source_bound","method_only","synthetic","proposed","contested","held","rejected","unknown","needs_replication"],
 "access": ["keyboard","captions","low_bandwidth","mobile","desktop","large_print","audio_description","high_contrast","translation_candidate","plain_text"],
 "participation": ["inspect","read","reproduce","challenge","compare","comment_opt_in","fork","subscribe_opt_in","share_opt_in","no_action"],
 "receiver": ["individual","group","classroom","makerspace","laboratory","newsroom","vendor_team","public_commons","cross_discipline","unknown"],
 "outcome": ["clarity","source_found","question_recorded","spec_drafted","evidence_improved","bug_found","time_saved_candidate","accessible_result","critique_received","no_effect"]
}
assert len(axes)==12 and all(len(v)==10 for v in axes.values())
manifest = {
 "schema":"CoAll.CoPublicationFederation.FirstProof.R0",
 "version":"R0.2_LOCAL_SYNTHETIC_EDITORIAL",
 "created_utc":"2026-10-25",
 "status":"STATIC_INTERACTIVE_CANDIDATE_NOT_SUBSTACK_POSTED_NOT_READER_TESTED",
 "purpose":"Six human-legible editorial routes over one pinned public Great ReFact source, preserving source facts, consent and recoverable versions.",
 "source":source,
 "related_source_links":other,
 "claims":claims,
 "claim_ids_required_in_every_route":ids,
 "routes":routes,
 "edition_history":[
    {"id":"r0.1","kind":"LOCAL_SYNTHETIC_PREDECESSOR","name":"Initial plain-language projection","description":"Focus on compatible capabilities and a reader-chosen task. This is an illustrative predecessor, not an earlier public publication.","predecessor":None},
    {"id":"r0.2","kind":"LOCAL_SYNTHETIC_SUCCESSOR","name":"Proof-and-recovery projection","description":"Adds explicit authority, measurement, rollback and source status. Same claim IDs and original source identity.","predecessor":"r0.1"}
 ],
 "current_edition":"r0.2",
 "logical_axes":axes,
 "logical_candidate_space":"1000000000000",
 "materialized_editorial_routes":6,
 "actual_substack_posts_created":0,
 "external_sends":0,
 "tracking":False,
 "interest_inference":False,
 "reader_feedback_writeback":"NONE_LOCAL_PREVIEW_ONLY",
 "giggle_lens":{
    "status":"HUMOROUS_SOURCE_LINKED_PROJECTION_NOT_EVIDENCE",
    "default":"OFF_UNTIL_EXPLICIT_READER_CLICK",
    "classification":"HUMOROUS",
    "source_claim_ids":ids,
    "privacy":"NO_INFERENCE_NO_STORAGE_NO_TRANSMISSION",
    "nonclaims":["HUMOR_NE_EVIDENCE","PUNCHLINE_NE_PERFORMANCE_METRIC","LAUGHTER_NE_READER_ADOPTION","OPT_IN_NE_CONSENT_TO_SEND","JOKE_NE_ENDORSEMENT"],
    "examples":[
        {"route_id":"curious","claim_id":"C01","quip":"Congratulations! You are Chief Copy-and-Paste Officer. The promotion comes with twelve browser tabs and no salary.","translation":"The proposal is to reduce the work people do transferring context between apps.","challenge":"Ordinary built-in integrations might solve the job more simply."},
        {"route_id":"developer","claim_id":"C03","quip":"We built a bridge between two APIs. The bridge immediately requested administrator access and a throne. We declined.","translation":"A connector is only useful when its permissions are narrow and its effects are reversible.","challenge":"An extra integration layer might introduce more bugs than it removes."},
        {"route_id":"operator","claim_id":"C05","quip":"Your dashboard is lovely. But customers should be able to export their data without an archaeological expedition.","translation":"Useful vendor capabilities should keep working and remain portable through documented interfaces.","challenge":"Some native applications are clearer and safer than a composed workflow."},
        {"route_id":"researcher","claim_id":"C06","quip":"Our workflow was 400 percent faster, until someone noticed we had stopped measuring the part that takes time.","translation":"Measure actual task outcomes against a fixed baseline; do not infer benefit from an attractive demo.","challenge":"Familiarity or a simpler interface may explain any improvement."},
        {"route_id":"journalist","claim_id":"C04","quip":"Breaking: prototype announces that it changed civilization. Civilization says it has not received the memo.","translation":"An architecture or passing test is not evidence of deployment or independent adoption.","challenge":"A working native integration requires separate operational proof."},
        {"route_id":"educator","claim_id":"C02","quip":"The group project involves six apps. Five forgot the password and the sixth brought a licensing committee.","translation":"Relating tools requires knowing what each owns, where it fails and what is lost during translation.","challenge":"A playful story can itself hide missing accessibility or data rights."}
    ]
 },
 "reader_choice":"EXPLICIT_LOCAL_CLICK_NO_BROWSER_STORAGE",
 "urgency":{"mode":"NONE_NO_REAL_DEADLINE_VERIFIED","countdowns":False,"deliberately_expiring_links":False},
 "publication_candidates":["one umbrella with reader-chosen Sections","separate publications only if independent editorial needs and capacity warrant"],
 "nonclaims":["TRILLION_DESCRIPTORS_NE_TRILLION_POSTS","INTEREST_CHOICE_NE_PERSONAL_PROFILE","SUBSTACK_SECTION_NE_SEPARATE_CANON","LOCAL_PREVIEW_NE_SUBSTACK_PUBLISHED","EDITED_WEB_POST_NE_CHANGED_SENT_EMAIL","TEMPORAL_FOCUS_NE_DELETED_HISTORY","READER_VIEW_NE_AUTHORIZED_SOURCE_MUTATION","OPEN_SOURCE_CODE_NE_RUNTIME_ADOPTION","SOURCE_CLAIM_NE_OBSERVED_TIME_SAVINGS","NO_UNVERIFIED_SCARCITY_OR_GUARANTEED_VIRALITY"]
}
(root/'manifest.json').write_text(json.dumps(manifest,indent=2,ensure_ascii=True,sort_keys=True)+'\n',encoding='utf-8')
print('manifest',len(routes),'routes',len(claims),'claims',10**12,'logical indices')
