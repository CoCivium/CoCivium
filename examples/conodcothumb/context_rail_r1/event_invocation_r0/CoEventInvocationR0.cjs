'use strict';
// CoContextRail R1 donor: synthetic direct operation invocation, not UI automation.
// No OS, network, filesystem, account, scheduler or remote receiver effects.
const SCHEMA = 'CoAll.CoEventInvocation.ShadowR0';
const NO_EXTERNAL_EFFECTS = Object.freeze({device:0, network:0, send:0, clipboard:0, account:0, publication:0});
const FIELDS = new Set(['event_id','work_id','operation','privacy','observed_ms','expires_ms']);
const OPERATION = 'REFRESH_LOCAL_STATUS';
function goodId(x){ return typeof x==='string' && /^[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}$/.test(x); }
function createHarness({now_ms=1000,budget=1,receiver_ready=true}={}) {
  if (!Number.isSafeInteger(now_ms)||now_ms<0||!Number.isInteger(budget)||budget<0||budget>100)
    throw Error('INVALID_FIXTURE');
  let remaining=budget, count=0;
  const completed=new Map();
  function receipt(state,reason,work_id=null,extra={}){
    return Object.freeze({schema:SCHEMA,state,reason,work_id,local_refresh_count:count,
      external_effects:{...NO_EXTERNAL_EFFECTS},receiver_readproof:'NOT_TESTED',
      authority:'SYNTHETIC_POLICY_ONLY',...extra});
  }
  function invoke(route,event){
    // Trusted route identity is supplied by the harness entrypoint, NOT the event packet.
    if (!event||typeof event!=='object'||Array.isArray(event)||
        Object.keys(event).some(key=>!FIELDS.has(key)))
      return receipt('HELD','UNDECLARED_OR_INVALID_FIELDS');
    if (!goodId(event.event_id)||!goodId(event.work_id)) return receipt('HELD','INVALID_ID');
    const work_id=event.work_id;
    if (event.privacy!=='PUBLIC_SYNTHETIC') return receipt('HELD','PRIVACY_NOT_QUALIFIED',work_id);
    if (!['BUTTON','COB_EVENT'].includes(route)||event.operation!==OPERATION)
      return receipt('HELD','OPERATION_NOT_ALLOWED',work_id);
    if (!Number.isSafeInteger(event.observed_ms)||!Number.isSafeInteger(event.expires_ms)||
        event.observed_ms>now_ms||now_ms>event.expires_ms||
        event.expires_ms-event.observed_ms>60000)
      return receipt('HELD','STALE_FUTURE_OR_UNBOUNDED',work_id);
    const key=work_id+'|'+event.operation;
    if (completed.has(key)) return receipt('DEDUPED','ONE_OPERATION_ALREADY_EXECUTED',work_id,
      {first_event_id:completed.get(key)});
    if (!receiver_ready) return receipt('HELD','RECEIVER_NOT_READY',work_id);
    if (remaining===0) return receipt('HELD','BUDGET_EXHAUSTED',work_id);
    // Exactly one in-memory synthetic operation. Not a real health probe.
    remaining--;count++;completed.set(key,event.event_id);
    return receipt('LOCAL_ONLY_EXECUTED','SYNTHETIC_REFRESH',work_id,{event_id:event.event_id});
  }
  const fromButton=event=>invoke('BUTTON',event);
  const fromCoBEvent=event=>invoke('COB_EVENT',event);
  const snapshot=()=>Object.freeze({local_refresh_count:count,remaining,
    unique_operations:completed.size,external_effects:{...NO_EXTERNAL_EFFECTS}});
  return Object.freeze({fromButton,fromCoBEvent,snapshot});
}
module.exports={SCHEMA,NO_EXTERNAL_EFFECTS,createHarness};
