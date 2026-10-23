/* CoMapPulse R0, dependency-free pure predicates. No I/O, no receivers. GPL-3.0 */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(typeof window!=='undefined')window.CoMapCore=api;
})(this,function(){
  'use strict';
  const nodeStatus=new Set(['GOAL','PROPOSED','DESCRIBED','REQUIRED','CANDIDATE','DESIGN_ONLY','HELD']);
  const epistemic=new Set(['DOCUMENTED','PROPOSED','HELD']);
  const ackStates=new Set(['NOT_APPLICABLE','NO_RECEIVER_ACK','ACK_VERIFIED']);
  function ok(cond,code){if(!cond)throw new Error(code);}
  function isRecord(x){return x!==null&&typeof x==='object'&&!Array.isArray(x);}
  function safePublicUrl(u){return typeof u==='string'&&/^https:\/\/github\.com\/CoCivium\//.test(u)&&!/[\s<>]/.test(u);}
  function validateGraph(graph){
    ok(isRecord(graph)&&graph.schema==='CoMapPulseGraph/R0','BAD_SCHEMA');
    ok(graph.source_policy==='PUBLIC_ONLY__NO_SECRETS__NO_REMOTE_EFFECT','UNSAFE_SOURCE_POLICY');
    ok(Array.isArray(graph.nodes)&&graph.nodes.length>=2&&graph.nodes.length<=40,'BAD_NODE_COUNT');
    ok(Array.isArray(graph.edges)&&graph.edges.length<=120,'BAD_EDGE_COUNT');
    ok(Array.isArray(graph.receivers)&&graph.receivers.length<=20,'BAD_RECEIVER_COUNT');
    const ns=new Set(),es=new Set(),rs=new Set();
    for(const n of graph.nodes){
      ok(isRecord(n)&&typeof n.id==='string'&&/^[a-z0-9-]+$/.test(n.id),'BAD_NODE_ID');
      ok(!ns.has(n.id),'DUPLICATE_NODE');ns.add(n.id);
      ok(nodeStatus.has(n.status)&&typeof n.title==='string'&&n.title.length<=65,'BAD_NODE');
      ok(Number.isFinite(n.x)&&Number.isFinite(n.y)&&n.x>=0&&n.y>=0&&n.x<=1000&&n.y<=540,'NODE_OUT_OF_BOUNDS');
      ok(n.source===null||safePublicUrl(n.source),'NON_PUBLIC_NODE_SOURCE');
    }
    for(const e of graph.edges){
      ok(isRecord(e)&&typeof e.id==='string'&&!es.has(e.id),'DUPLICATE_EDGE');es.add(e.id);
      ok(ns.has(e.from)&&ns.has(e.to)&&e.from!==e.to,'DANGLING_EDGE');
      ok(epistemic.has(e.epistemic)&&ackStates.has(e.ack),'INVALID_RELATION_STATE');
      ok(e.proof===null||safePublicUrl(e.proof),'NON_PUBLIC_EDGE_PROOF');
      if(e.epistemic==='DOCUMENTED')ok(safePublicUrl(e.proof),'DOCUMENTED_WITHOUT_PROOF');
      if(e.ack==='ACK_VERIFIED')throw new Error('R0_NEVER_VERIFIES_REMOTE_ACK');
      if(e.epistemic==='HELD')ok(e.ack!=='ACK_VERIFIED','HELD_CANNOT_BE_ACKED');
    }
    for(const r of graph.receivers){
      ok(isRecord(r)&&typeof r.id==='string'&&!rs.has(r.id),'DUPLICATE_RECEIVER');rs.add(r.id);
      ok(typeof r.state==='string'&&typeof r.endpoint_known==='boolean','BAD_RECEIVER');
      ok(!r.ack_ref||safePublicUrl(r.ack_ref),'BAD_ACK_REF');
      if(!r.endpoint_known)ok(r.state==='HOLD_NO_RECEIVER'&&r.ack_ref===null,'INVENTED_ENDPOINT');
      if(r.state.startsWith('HOLD'))ok(!r.ack_ref,'ACK_IN_HELD_ROUTE');
    }
    return {nodes:graph.nodes.length,edges:graph.edges.length,receivers:graph.receivers.length};
  }
  const completions=['CoAckRAW+','CoMap+','CoOrbWare+','CoQuanta+','CoSubscriptionEcology+','CoVirtualSession+','CoTime+','CoPrivacy+','CoStretch+','CoReWis+'];
  function predict(input,cursor,enabled){
    if(!enabled||typeof input!=='string'||!Number.isInteger(cursor)||cursor<0||cursor>input.length)return null;
    const left=input.slice(0,cursor), match=left.match(/(?:^|[^A-Za-z0-9+])([A-Za-z][A-Za-z0-9+]{1,})$/);
    if(!match)return null;
    const part=match[1];
    const target=completions.find(x=>x.toLowerCase().startsWith(part.toLowerCase())&&x.length>part.length);
    return target?{suffix:target.slice(part.length),term:target,cursor,source:'LOCAL_STATIC_RULES'}:null;
  }
  function accept(input,cursor,proposal){
    ok(proposal!==null&&proposal!==undefined&&typeof proposal.suffix==='string'&&proposal.cursor===cursor,'NO_VALID_PREDICTION');
    ok(typeof input==='string'&&cursor>=0&&cursor<=input.length,'BAD_CURSOR');
    return input.slice(0,cursor)+proposal.suffix+input.slice(cursor);
  }
  function routePlan(graph){
    validateGraph(graph);
    return graph.receivers.map(r=>({id:r.id,label:r.label,state:r.state,effect:'NONE',ack:'NOT_OBSERVED',
      action:r.state==='EXISTING_PUBLIC_POINTER'?'PULL_ONLY':r.state==='HOLD_RECENT_DUPLICATE'?'SUPPRESS_DUPLICATE':'DO_NOT_DELIVER'}));
  }
  function related(graph,id){return graph.edges.filter(e=>e.from===id||e.to===id).map(e=>({id:e.id,other:e.from===id?e.to:e.from,relation:e.relation,epistemic:e.epistemic,ack:e.ack}));}
  return Object.freeze({validateGraph,predict,accept,routePlan,related,safePublicUrl});
});
