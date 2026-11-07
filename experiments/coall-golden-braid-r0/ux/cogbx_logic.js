/* CoGbx UX candidate R0. Offline synthetic projected state, NOT a live service. */
(function(root,factory) {
  const result=factory();
  if(typeof module === 'object' && module.exports) module.exports=result;
  if(root) root.CoGbxLogic=result;
})(typeof globalThis==='object' ? globalThis : null,function(){
  'use strict';
  const TASK_ID='COALL-317-LOCAL-SYNTHETIC-001';
  const TASK_SHA='8452a4136917202c5a8f706316bc84672bc315fa131fb40c12fc3c6288c29d73';
  const JOURNAL_HEAD='63f284f9eca8eca0b7e9715c976817ff4b08612843aa75dfc6053c24cbb8f750';
  const BENCHMARK_HEAD='94267bf504af4e5fbfaad323cbda0101f2266943a95ab9f53ad765fc8ca94db8';
  const STATES=Object.freeze([
    Object.freeze({name:'Intake',alpha:'PENDING',beta:'PENDING',next:'Dispatch locally to both test receivers',description:'An authorized synthetic packet is pinned. Nothing has been received yet.'}),
    Object.freeze({name:'Injected fault',alpha:'ACK_VERIFIED_LOCAL',beta:'FAILED_QUEUED',next:'Retry beta only; preserve alpha receipt',description:'Alpha returned a local receiver-produced receipt. Beta hit a deliberate injected failure; this is not a real outage.'}),
    Object.freeze({name:'Recovered',alpha:'ACK_VERIFIED_LOCAL',beta:'ACK_VERIFIED_LOCAL',next:'Seek independent cross-device readproof',description:'Two local receiver processes returned distinct receipts. Neither is an external adopter or separate failure domain.'})
  ]);
  function snapshot(index){
    if(!Number.isInteger(index) || index<0 || index>=STATES.length) throw new RangeError('INVALID_SNAPSHOT');
    return STATES[index];
  }
  function capsule(index){
    const s=snapshot(index);
    const json={schema:'CoGbxPublicSyntheticCapsule/R0',task_id:TASK_ID,task_sha256:TASK_SHA,
      source:'CoCivium/CoCivium#317',journal_head:JOURNAL_HEAD,benchmark_head:BENCHMARK_HEAD,simulation_only:true,local_receiver_alpha:s.alpha,
      local_receiver_beta:s.beta,phase:s.name,external_receiver_ack:'NOT_TESTED',
      user_or_device_consent:'NOT_INFERRED',next:s.next};
    return JSON.stringify(json,null,2);
  }
  function safeStatus(value){
    return value==='ACK_VERIFIED_LOCAL'?'Local ACK':value==='FAILED_QUEUED'?'Failed · queued':'Pending';
  }
  return Object.freeze({TASK_ID,TASK_SHA,JOURNAL_HEAD,BENCHMARK_HEAD,STATES,snapshot,capsule,safeStatus});
});
