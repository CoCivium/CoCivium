/*
 * Relation impact R0: bounded, deterministic PUBLIC-only, read-only shadow.
 * All nodes including relations may be evolution candidates; neither
 * possibility nor a graph edge gives authority to mutate/send/publish.
 * Input direction: from = upstream prerequisite; to = downstream dependent.
 */
export const SCHEMA='CoAll.CoOrbWare.RelationImpactShadow.R0';
const ID=/^[A-Za-z0-9_.:-]{1,96}$/;
const KINDS=new Set(['OBJECT','RELATION','EVIDENCE','WORK','VIEW','MEDIA','RESOURCE','RECEIVER']);
const DEPENDENCIES=new Set(['DEPENDS_ON','DERIVED_FROM','PROJECTS_FROM','USES_EVIDENCE_FROM','RECEIVES_DELTA_FROM']);
const INSPIRATIONS=new Set(['INSPIRED_BY','ANALOGOUS_TO','CONTRASTS_WITH','CHALLENGES','INVERTS_VIEW_OF']);
const EDGE_STATUS=new Set(['VERIFIED_DEPENDENCY','PROPOSED','UNKNOWN']);
const CHANGE_STATES=new Set(['CANDIDATE_DELTA','HYPOTHETICAL','OBSERVED_DELTA_REF_ONLY']);
const NONCLAIMS=[
  'TOUCHED_NE_MUTATED','POTENTIALLY_RELATED_NE_CONFIRMED_DEPENDENCY',
  'RELATION_NE_AUTHORITY','DEPENDENCY_NE_FALSEHOOD_PROPAGATION',
  'PROPOSAL_NE_PROOF','GRAPH_STATUS_LABEL_NE_INDEPENDENT_VERIFICATION','CHANGE_PREVIEW_NE_CHANGE_EXECUTION',
  'INSPIRATION_NE_CAUSATION','OBSERVED_DELTA_REF_ONLY_NE_INDEPENDENT_PROOF',
  'PLAN_NE_RECEIVER_ACK','NO_EXTERNAL_EFFECTS',
  'FINITE_FRONTIER_NE_FINITE_POSSIBILITY','G_D_SYMBOLIC_NE_EMPIRICAL_MECHANISM'
];
const has=(v)=>typeof v==='string'&&ID.test(v);
const cmp=(a,b)=>a.localeCompare(b);
function base(){
  return {schema:SCHEMA,state:'HOLD_INVALID_INPUT',seed:null,seed_kind:null,
    change_state:'CANDIDATE_DELTA',candidates:[],optional_explore:[],
    candidate_count:0,depth_truncated:false,count_truncated:false,
    executed_mutations:0,receiver_ack:false,materialized_bytes:0,
    effects:{network:0,send:0,execute:0,write:0,device_control:0},
    nonclaims:NONCLAIMS};
}
function hold(state){return {...base(),state};}
function validNode(x){
  return x&&typeof x==='object'&&!Array.isArray(x)&&has(x.id)&&KINDS.has(x.kind);
}
function validEdge(x){
  return x&&typeof x==='object'&&!Array.isArray(x)&&has(x.id)&&
    has(x.from)&&has(x.to)&&
    (DEPENDENCIES.has(x.kind)||INSPIRATIONS.has(x.kind))&&
    EDGE_STATUS.has(x.status)&&
    ['CURRENT','STALE','UNKNOWN'].includes(x.currentness);
}
export function planRelationImpact(req){
  if(!req||typeof req!=='object'||Array.isArray(req))return hold('HOLD_INVALID_INPUT');
  const {seed_id,nodes,edges}=req;
  const max_depth=req.max_depth??4,max_candidates=req.max_candidates??24;
  const state=req.change_state??'CANDIDATE_DELTA';
  if(!has(seed_id)||!Array.isArray(nodes)||!Array.isArray(edges)||
    !Number.isInteger(max_depth)||max_depth<0||max_depth>8||
    !Number.isInteger(max_candidates)||max_candidates<1||max_candidates>32||
    !CHANGE_STATES.has(state))return hold('HOLD_INVALID_INPUT');

  // Only PUBLIC records can influence this PUBLIC-facing plan.
  const pubNodes=nodes.filter(x=>x&&x.privacy==='PUBLIC');
  const pubEdges=edges.filter(x=>x&&x.privacy==='PUBLIC');
  if(pubNodes.length>128||pubEdges.length>256)
    return hold('HOLD_PUBLIC_INPUT_BUDGET');
  if(!pubNodes.every(validNode)||!pubEdges.every(validEdge))
    return hold('HOLD_INVALID_PUBLIC_METADATA');
  if(new Set(pubNodes.map(x=>x.id)).size!==pubNodes.length ||
    new Set(pubEdges.map(x=>x.id)).size!==pubEdges.length)
    return hold('HOLD_PUBLIC_IDENTITY_COLLISION');

  const byId=new Map(pubNodes.map(x=>[x.id,x]));
  const seed=byId.get(seed_id);
  if(!seed)return hold('HOLD_PUBLIC_SEED_UNAVAILABLE');

  // Bad endpoint or private endpoint cannot be inferred or leaked.
  const qualified=pubEdges.filter(x=>byId.has(x.from)&&byId.has(x.to));
  const deps=qualified.filter(x=>DEPENDENCIES.has(x.kind)&&
    x.status==='VERIFIED_DEPENDENCY'&&x.currentness==='CURRENT');
  const adj=new Map(),explore=new Map();
  for(const e of deps){
    if(!adj.has(e.from))adj.set(e.from,[]);
    adj.get(e.from).push(e);
  }
  for(const e of qualified.filter(x=>INSPIRATIONS.has(x.kind)||x.status!=='VERIFIED_DEPENDENCY'||x.currentness!=='CURRENT')){
    if(!explore.has(e.from))explore.set(e.from,[]);
    explore.get(e.from).push(e);
  }
  for(const [,arr] of adj)arr.sort((a,b)=>cmp(a.to,b.to)||cmp(a.id,b.id));
  for(const [,arr] of explore)arr.sort((a,b)=>cmp(a.to,b.to)||cmp(a.id,b.id));

  const visited=new Set([seed_id]);
  const queue=[{id:seed_id,depth:0}],candidates=[];
  let depthTruncated=false;
  for(let i=0;i<queue.length;i++){
    const item=queue[i],following=adj.get(item.id)||[];
    if(item.depth>=max_depth){
      if(following.some(x=>!visited.has(x.to)))depthTruncated=true;
      continue;
    }
    for(const e of following){
      if(visited.has(e.to))continue;
      visited.add(e.to);
      const dest=byId.get(e.to);
      candidates.push({id:dest.id,kind:dest.kind,depth:item.depth+1,
        via:e.id,dependency_kind:e.kind,disposition:'REVIEW_CANDIDATE_ONLY'});
      queue.push({id:dest.id,depth:item.depth+1});
    }
  }
  candidates.sort((a,b)=>a.depth-b.depth||cmp(a.id,b.id));
  const visible=candidates.slice(0,max_candidates);
  const exploreSeed=(explore.get(seed_id)||[]).map(e=>({id:e.to,kind:byId.get(e.to).kind,
    relation:e.kind,state:'EXPLORE_NOT_PROPAGATE'})).slice(0,16);
  const partial=depthTruncated||candidates.length>visible.length;
  return {...base(),state:partial?'PARTIAL_REVIEW_CANDIDATES':'REVIEW_CANDIDATES_ONLY',
    seed:seed.id,seed_kind:seed.kind,change_state:state,
    candidates:visible,optional_explore:exploreSeed,candidate_count:visible.length,
    depth_truncated:depthTruncated,count_truncated:candidates.length>visible.length};
}
