/* CoOwnedWork R0: one explicit synthetic fixture, one browser-origin WorkID.
   No device binding, remote transport, read of other apps or real authorization. */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports)module.exports=api;
  else root.CoOwnedWorkR0=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const SCHEMA='CoAll.CoOwnedWork.BrowserLocal.R0';
  const STORAGE_KEY='CoCivium.CoContextRail.SyntheticWorkID.R0';
  const HEAD='63b41ead8797e5a781699f32bcbc77b78bdbd7af';
  const SOURCE_SHA256='58f8c722bfbfc34cac41189c072d2effe4b19dbbe8a37be4f8687344d6b00b9a';
  const packet=Object.freeze({
    schema:SCHEMA+'.Packet',
    work_id:'CoPre.ReadyCycle.Synthetic.R0',
    source_ref:'CoCivium/CoCivium:CoPre.md@'+HEAD,
    source_sha256:SOURCE_SHA256,
    narrative_summary:'Recover the public CoPre Ready Cycle as one bounded work object; repeated assent is not a new task.',
    prior_decisions:['Reuse existing CoPre source','One elected writer','Independent challenges have no write authority'],
    open_blockers:['External receiver unverified','24-hour survival unverified','Human-time benefit unmeasured'],
    next_safe_deed:'Verify one independent receiver without requiring human narrative relay.',
    privacy:'PUBLIC_SYNTHETIC',consent:'SYNTHETIC_TEST_ONLY',
    lease_epoch:1
  });
  function fixture(){return JSON.parse(JSON.stringify(packet));}
  function equal(a,b){return JSON.stringify(a)===JSON.stringify(b);}
  function validStored(row){
    return row&&typeof row==='object'&&!Array.isArray(row)&&
      Object.keys(row).sort().join('|')==='commit_sequence|packet|receiver_ack|schema|source_verified_by_browser|state'&&
      row.schema===SCHEMA+'.Record'&&
      (row.state==='ACTIVE'||row.state==='REVOKED')&&
      row.commit_sequence===1&&row.receiver_ack===false&&
      row.source_verified_by_browser===false&&equal(row.packet,fixture());
  }
  function read(storage){
    if(!storage||typeof storage.getItem!=='function')return {state:'HELD_STORAGE_UNAVAILABLE'};
    try{
      const raw=storage.getItem(STORAGE_KEY);
      if(raw===null)return {state:'EMPTY'};
      if(typeof raw!=='string'||raw.length>8192)return {state:'HELD_CONFLICT'};
      const row=JSON.parse(raw);
      return validStored(row)?{state:row.state,row}:{state:'HELD_CONFLICT'};
    }catch(_){return {state:'HELD_STORAGE_UNAVAILABLE'};}
  }
  function write(storage,row){
    if(!storage||typeof storage.setItem!=='function')return {state:'HELD_STORAGE_UNAVAILABLE'};
    try{storage.setItem(STORAGE_KEY,JSON.stringify(row));}catch(_){return {state:'HELD_STORAGE_UNAVAILABLE'};}
    const check=read(storage);
    return check.state===row.state&&equal(check.row,row)?check:{state:'HELD_WRITE_READBACK'};
  }
  function preserve(storage,selected){
    // Only an explicit PUBLIC synthetic intent, never a real selection or hovering.
    if(!selected||selected.privacy!=='PUBLIC'||selected.context!=='RESEARCH'||
       selected.question!=='WHAT_ELSE'||selected.fixture===true||
       !['EXPLICIT_RING','KEYBOARD_FALLBACK'].includes(selected.gesture)||
       selected.preview_state!=='PROPOSED_ONLY')return {state:'HELD_EXPLICIT_SCOPE'};
    const prior=read(storage);
    if(prior.state==='ACTIVE')return {state:'DUPLICATE_SUPPRESSED',work_id:packet.work_id,committed:0};
    if(prior.state!=='EMPTY')return {state:prior.state==='REVOKED'?'HELD_REVOKED':prior.state};
    const row={schema:SCHEMA+'.Record',packet:fixture(),state:'ACTIVE',commit_sequence:1,
       receiver_ack:false,source_verified_by_browser:false};
    const result=write(storage,row);
    return result.state==='ACTIVE'?{state:'COMMITTED_BROWSER_LOCAL',work_id:packet.work_id,committed:1}:
      {state:result.state};
  }
  function recover(storage){
    const result=read(storage);
    if(result.state!=='ACTIVE')return {state:result.state==='REVOKED'?'HELD_REVOKED':result.state};
    const p=result.row.packet;
    return {state:'RECOVERED_BROWSER_LOCAL',work_id:p.work_id,
      summary:p.narrative_summary,decisions:[...p.prior_decisions],blockers:[...p.open_blockers],
      next_safe_deed:p.next_safe_deed,source_ref:p.source_ref,
      source_verified_by_browser:false,receiver_ack:false,live_mouse:false};
  }
  function revoke(storage){
    const prior=read(storage);
    if(prior.state==='REVOKED')return {state:'ALREADY_REVOKED'};
    if(prior.state!=='ACTIVE')return {state:prior.state};
    const row={...prior.row,state:'REVOKED'};
    const saved=write(storage,row);
    return {state:saved.state==='REVOKED'?'REVOKED_BROWSER_LOCAL':saved.state};
  }
  return {SCHEMA,STORAGE_KEY,fixture,preserve,recover,revoke,read};
});
