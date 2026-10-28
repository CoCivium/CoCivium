/* CoOmniIO+/CoNotSpace+ candidate overlay R1. No I/O or authority. GPL-3.0. */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  if(typeof window!=='undefined')window.CoOmniCore=api;
})(this,function(){
  'use strict';
  const KINDS=new Set(['PROPOSED','MISSING_PREREQUISITE','INTENTIONAL_BOUNDARY','UNKNOWN_UNSURVEYED','HYPOTHESIS_ONLY','REJECTED_INFERENCE']);
  const ROLES=new Set(['INPUT','OUTPUT','CONNECTOR','CONSTRAINT','ABSENCE','HYPOTHESIS','QUESTION','CHALLENGE','REPAIR']);
  const CONSENT=new Set(['NOT_REQUESTED','NOT_APPLICABLE','WITHHELD']);
  function check(condition,error){if(!condition)throw new Error(error);}
  function record(x){return x!==null&&typeof x==='object'&&!Array.isArray(x);}
  function safeUrl(value){return typeof value==='string'&&/^https:\/\/github\.com\/CoCivium\/[A-Za-z0-9._/+#?-]+$/.test(value)&&!/[\s<>]/.test(value);}
  function validateOverlay(overlay,graph){
    check(record(overlay)&&overlay.schema==='CoOmniIO.NotSpaceOverlay/R1','BAD_OMNI_SCHEMA');
    check(overlay.source_policy==='PUBLIC_ONLY__NO_REMOTE_EFFECT','UNSAFE_OVERLAY_SOURCE_POLICY');
    check(overlay.run_mode==='OFFLINE_CANDIDATE__NO_AUTHORITY','BAD_RUN_MODE');
    check(/^[a-f0-9]{64}$/.test(overlay.base_graph_sha256||''),'MISSING_GRAPH_DIGEST');
    check(record(graph)&&graph.schema==='CoMapPulseGraph/R0','BAD_BASE_GRAPH');
    check(overlay.base_graph_snapshot===graph.snapshot,'GRAPH_SNAPSHOT_DRIFT');
    check(Array.isArray(overlay.items)&&overlay.items.length>=1&&overlay.items.length<=18,'BAD_OMNI_COUNT');
    const nodes=new Set(graph.nodes.map(n=>n.id)); const ids=new Set();const result={};
    for(const item of overlay.items){
      check(record(item)&&/^[a-z0-9-]{3,60}$/.test(item.id||'')&&!ids.has(item.id),'BAD_OR_DUPLICATE_OMNI_ID');ids.add(item.id);
      check(KINDS.has(item.status),'BAD_OMNI_STATUS');
      check(nodes.has(item.from),'UNKNOWN_OMNI_SOURCE_NODE');
      if(item.to===null){
        check(item.status==='HYPOTHESIS_ONLY'||item.status==='UNKNOWN_UNSURVEYED','UNBOUND_ENDPOINT_MUST_BE_UNKNOWN');
        check(typeof item.frontier_label==='string'&&item.frontier_label.length>=2&&item.frontier_label.length<=60,'MISSING_HYPOTHESIS_LABEL');
      }else{
        check(nodes.has(item.to)&&item.to!==item.from,'UNKNOWN_OR_SELF_OMNI_TARGET');
        check(item.frontier_label===null,'FRONTIER_LABEL_WITH_BOUND_NODE');
      }
      check(Array.isArray(item.roles)&&item.roles.length>=1&&item.roles.length<=5&&item.roles.every(x=>ROLES.has(x))&&new Set(item.roles).size===item.roles.length,'INVALID_OMNI_ROLES');
      check(typeof item.reason==='string'&&item.reason.length>=16&&item.reason.length<=400,'MISSING_EXPLANATION');
      check(typeof item.next_test==='string'&&item.next_test.length>=12&&item.next_test.length<=400,'MISSING_FALSIFIABLE_NEXT_TEST');
      check(item.source_ref===null||safeUrl(item.source_ref),'PRIVATE_OR_UNQUALIFIED_OMNI_SOURCE');
      check(item.effect_authority==='NONE'&&item.receiver_ack==='NOT_OBSERVED','OMNI_EFFECT_OR_ACK_SPOOF');
      check(CONSENT.has(item.consent_state),'INVALID_OMNI_CONSENT');
      check(item.privacy_class==='PUBLIC','NON_PUBLIC_OMNI_INPUT');
      check(item.reversible===true,'NONREVERSIBLE_OMNI_PROPOSAL');
      check(item.is_material_observation===false,'OMNI_CLAIM_OF_MATERIAL_OBSERVATION');
      check(item.network_effect===false,'OMNI_NETWORK_EFFECT');
      check(item.status!=='INTENTIONAL_BOUNDARY'||item.consent_state==='WITHHELD','INTENTIONAL_BOUNDARY_NEEDS_WITHHELD_CONSENT');
      check(item.status!=='HYPOTHESIS_ONLY'||item.source_ref===null,'HYPOTHESIS_CLAIMED_EXTERNAL_EVIDENCE');
      result[item.status]=(result[item.status]||0)+1;
    }
    return {total:ids.size,counts:result,source_binding:'R1_SHA256_PINNED_BY_OFFLINE_TESTS',external_effects:0};
  }
  function candidates(overlay,graph){
    validateOverlay(overlay,graph);
    return overlay.items.map(item=>({
      id:item.id,from:item.from,to:item.to,frontier_label:item.frontier_label,roles:item.roles.slice(),
      status:item.status,reason:item.reason,next_test:item.next_test,source_ref:item.source_ref,
      receiver_ack:'NOT_OBSERVED',action:'INSPECT_ONLY',draw_as_proven_edge:false,
      confidential_content_copied:false,authority:'NONE'
    }));
  }
  return Object.freeze({validateOverlay,candidates,safeUrl});
});
