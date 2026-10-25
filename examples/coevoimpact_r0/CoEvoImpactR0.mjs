// CoEvoImpact R0: source-to-dependent impact planning; SHADOW ONLY.
// This module does not execute, notify, post, mutate files, call models or grant authority.
// The simulated graph uses typed edges dependent -> prerequisite. Invalidation walks the reverse.
import {readFileSync} from 'node:fs';
import {fileURLToPath} from 'node:url';
import {resolve} from 'node:path';

export const SCHEMA = 'CoCivium.CoEvoImpact.ShadowR0';
export const EDGE_WEIGHTS = Object.freeze({
  TESTS:100, CHALLENGES:90, DEPENDS_ON:80, RENDERS:70,
  DOCUMENTS:60, IMPLEMENTS:60, USES_AS_PRIOR:35
});
export const NON_PROPAGATING = Object.freeze([
  'MAY_INSPIRE', 'SIMILAR_TO', 'CONVERSE_OF', 'RELATED_TO',
  'BELONGS_TO', 'AUTHORIZED_BY', 'SENT_TO', 'ACKED_BY'
]);
const VALID_ID = /^[a-zA-Z][a-zA-Z0-9_.-]{0,79}$/;
const HEX64 = /^[a-f0-9]{64}$/;
function object(x){return x && typeof x==='object' && !Array.isArray(x);}
function validate(graph, event, options){
  if(!object(graph) || graph.schema!=='CoEvoImpact.SyntheticGraph.R0' ||
     !Array.isArray(graph.nodes) || !Array.isArray(graph.edges) ||
     graph.nodes.length>256 || graph.edges.length>512) throw Error('HOLD_GRAPH_BOUNDS_OR_SCHEMA');
  if(!object(event)||event.schema!=='CoEvoImpact.SyntheticChange.R0' ||
     event.evidence_class!=='SYNTHETIC_FIXTURE'||event.kind!=='SOURCE_BYTES_CHANGED'||
     !HEX64.test(event.before_sha256||'')||!HEX64.test(event.after_sha256||'')||
     !VALID_ID.test(event.changed_id||'')) throw Error('HOLD_UNQUALIFIED_SOURCE_CHANGE');
  if(!Number.isInteger(options.max_depth)||options.max_depth<1||options.max_depth>3 ||
     !Number.isInteger(options.max_proposals)||options.max_proposals<1||options.max_proposals>16||
     !Number.isInteger(options.max_visits)||options.max_visits<1||options.max_visits>128) throw Error('HOLD_UNBOUNDED_BUDGET');
  const nodes = new Map();
  for(const node of graph.nodes){
    if(!object(node)||!VALID_ID.test(node.id||'')||nodes.has(node.id)||
       !['PUBLIC','PRIVATE','UNKNOWN'].includes(node.privacy)||
       !['CURRENT','STALE','UNKNOWN'].includes(node.currentness)||
       !['EXPLICIT_SHADOW','NONE'].includes(node.subscription)||
       !['NONE','REQUIRES_APPROVAL'].includes(node.authority))
       throw Error('HOLD_INVALID_NODE');
    nodes.set(node.id,node);
  }
  if(!nodes.has(event.changed_id)) throw Error('HOLD_MISSING_CHANGE_SOURCE');
  const seen=new Set();
  for(const edge of graph.edges){
    if(!object(edge)||!VALID_ID.test(edge.from||'')||!VALID_ID.test(edge.to||'')||
       !nodes.has(edge.from)||!nodes.has(edge.to)|| edge.from===edge.to ||
       !/^[A-Z_]+$/.test(edge.kind||'')||
       !['SYNTHETIC_DECLARATION','UNVERIFIED'].includes(edge.evidence))
       throw Error('HOLD_BAD_RELATION');
    const key=edge.from+'|'+edge.kind+'|'+edge.to;
    if(seen.has(key))throw Error('HOLD_DUPLICATE_RELATION');
    seen.add(key);
  }
  return nodes;
}
export function planImpact({graph,event,max_depth=2,max_proposals=4,max_visits=64}={}){
  const options={max_depth,max_proposals,max_visits};
  const nodes=validate(graph,event,options);
  const diagnostics={
    reviewed_edges:0, held_privacy:0, held_authority:0,
    held_unsubscribed:0, held_stale:0, held_unverified:0,
    nonpropagating_relations:0, cycle_deduped:0,
    visit_budget_held:0, proposal_budget_held:0
  };
  const baseline={
    schema:SCHEMA,authority:'NONE',effect_authority:'NONE',
    evidence_scope:'DECLARED_SYNTHETIC_GRAPH_NOT_OBSERVED_DEPENDENCIES',
    change_evidence:'SYNTHETIC_FIXTURE_NOT_VERIFIED_SOURCE_BYTES',
    budget:options,diagnostics,
    effects:{network:0,send:0,device:0,clipboard:0,model:0,worker_spawn:0,
      source_mutation:0,subscription_mutation:0,receiver_ack:0},
    nonclaims:['IMPACT_NE_CHANGE','RELATED_NE_DEPENDENT','DEPENDENCY_CANDIDATE_NE_FACT',
      'PROPOSAL_NE_EXECUTION','CONVERSE_NE_CAUSATION','MAY_EVOLVE_NE_AUTHORIZED_MUTATION',
      'SOURCE_CHANGE_CLAIM_NE_VERIFIED_BYTES','INFINITY_NE_UNBOUNDED_COMPUTE',
      'CURRENTNESS_FOR_ALL_NE_CONTENT_FOR_ALL','NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF']
  };
  const root=nodes.get(event.changed_id);
  if(root.privacy!=='PUBLIC'||root.authority!=='NONE') return {
    ...baseline,status:'HELD_SOURCE_PRIVACY_OR_AUTHORITY',proposals:[],
    candidate_count:0,no_effects:true
  };
  if(root.currentness!=='CURRENT') return {
    ...baseline,status:'HELD_SOURCE_CURRENTNESS_UNKNOWN_OR_STALE',proposals:[],
    candidate_count:0,no_effects:true
  };
  if(event.before_sha256===event.after_sha256) return {
    ...baseline,status:'HELD_NO_EXACT_DIGEST_CHANGE',proposals:[],
    candidate_count:0,no_effects:true
  };
  const bySource=new Map();
  for(const e of graph.edges){
    if(!bySource.has(e.to))bySource.set(e.to,[]);
    bySource.get(e.to).push(e);
  }
  const rank=(edge)=>(EDGE_WEIGHTS[edge.kind]||0);
  for(const list of bySource.values())list.sort((a,b)=>rank(b)-rank(a)||a.from.localeCompare(b.from)||a.kind.localeCompare(b.kind));
  const seenNodes=new Set([event.changed_id]), queue=[{id:event.changed_id,depth:0,via:null}];
  const candidates=[];
  for(let i=0;i<queue.length;i++){
    const current=queue[i];
    if(current.depth>=max_depth)continue;
    for(const edge of bySource.get(current.id)||[]){
      diagnostics.reviewed_edges++;
      if(!Object.hasOwn(EDGE_WEIGHTS,edge.kind)){diagnostics.nonpropagating_relations++;continue;}
      if(edge.evidence!=='SYNTHETIC_DECLARATION'){diagnostics.held_unverified++;continue;}
      const receiver=nodes.get(edge.from);
      // A private or unknown neighbor never appears by id in the public output.
      if(receiver.privacy!=='PUBLIC'){diagnostics.held_privacy++;continue;}
      if(receiver.authority!=='NONE'){diagnostics.held_authority++;continue;}
      if(receiver.currentness!=='CURRENT'){diagnostics.held_stale++;continue;}
      if(receiver.subscription!=='EXPLICIT_SHADOW'){diagnostics.held_unsubscribed++;continue;}
      if(seenNodes.has(receiver.id)){diagnostics.cycle_deduped++;continue;}
      if(seenNodes.size>=max_visits){diagnostics.visit_budget_held++;continue;}
      seenNodes.add(receiver.id);
      const depth=current.depth+1;
      const impact_kind=depth===1?'DIRECT_REVIEW_CANDIDATE':'DEFERRED_POSSIBLE_IF_PRIOR_ACTUALLY_CHANGES';
      candidates.push({
        dependent_id:receiver.id,changed_or_predicted_source_id:current.id,
        relationship_type:edge.kind,depth,impact_kind,
        rank_heuristic:rank(edge),
        proposed_deed:depth===1?'REVIEW_DEPENDENT_SOURCE_AND_RUN_EXISTING_CHECKS':'WAIT_FOR_VERIFIED_INTERMEDIATE_CHANGE',
        required_proof:depth===1?'EXACT_SOURCE_DIFF_PLUS_TARGET_TEST_AND_RECEIVER_APPROVAL':'VERIFIED_INTERMEDIATE_SOURCE_DELTA',
        auto_effects:0,model_calls:0,worker_count:0
      });
      queue.push({id:receiver.id,depth,via:current.id});
    }
  }
  candidates.sort((a,b)=>a.depth-b.depth||b.rank_heuristic-a.rank_heuristic||
    a.dependent_id.localeCompare(b.dependent_id));
  const proposals=candidates.slice(0,max_proposals);
  diagnostics.proposal_budget_held=candidates.length-proposals.length;
  return {
    ...baseline,status:proposals.length?'PASS_SYNTHETIC_SHADOW_PLAN':'HELD_NO_QUALIFIED_DEPENDENTS',
    changed_source_id:event.changed_id,
    source_digests:{before_sha256:event.before_sha256,after_sha256:event.after_sha256},
    proposals,candidate_count:candidates.length,
    next:'Select at most one proposed read-only review. Execute no effect from this plan. Requalify source bytes, rights, and receiver before further action.',
    no_effects:true
  };
}
const invoked=process.argv[1]&&resolve(process.argv[1])===fileURLToPath(import.meta.url);
if(invoked){
  try {
    const graphPath=process.argv[2], eventPath=process.argv[3];
    if(!graphPath||!eventPath)throw Error('Usage: node CoEvoImpactR0.mjs fixture/graph.json fixture/event.json');
    const plan=planImpact({graph:JSON.parse(readFileSync(graphPath,'utf8')),event:JSON.parse(readFileSync(eventPath,'utf8'))});
    console.log(JSON.stringify(plan,null,2));
  }catch(e){console.error(JSON.stringify({status:'FAIL_CLOSED',error:String(e.message||e)}));process.exitCode=1;}
}
