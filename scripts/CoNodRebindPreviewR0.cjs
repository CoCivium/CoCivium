'use strict';
/* CoNod -> CoPre WorkID: synthetic, read-only preview candidate.
 * Apostrophe is intent, not a credential, a work object, or an executor.
 * No keyboard/mouse hooks, private reads, network, timers, jobs or writes.
 */
const owned=require('../examples/conodcothumb/context_rail_r1/CoOwnedWorkR0.js');
const SCHEMA='CoAll.CoNod.CoPre.RebindPreview.R0';
const KEYS=new Set(['token','origin','presence','scope','effect',
                    'pressure','work_id','source_hint']);
const ORIGINS=new Set(['EXPLICIT_KEYBOARD','EXPLICIT_UI_GLYPH']);
const PRESSURES=new Set(['HEALTHY','DEGRADING','SATURATED','UNKNOWN']);
const EFFECTS=Object.freeze({storage_writes:0,shell_launches:0,messages_sent:0,
                            devices_modified:0,public_writes:0,jobs_enqueued:0});
function base(state,reason,extra={}){
  return {schema:SCHEMA,state,reason,input:'CoNod.apostrophe',
    authority:'NONE',source_verified:false,receiver_ack:false,
    real_session_recovery:false,effects:{...EFFECTS},
    nonclaims:['GESTURE_NE_AUTHORITY','PREVIEW_NE_EXECUTION',
      'SOURCE_POINTER_NE_RECEIVER_ACK','SESSION_NE_WORKID',
      'SYNTHETIC_NE_PRODUCTION','NO_WALKAWAY_PROOF'],...extra};
}
function preview(request,storage){
  if(!request||typeof request!=='object'||Array.isArray(request)||
     Object.keys(request).some(k=>!KEYS.has(k)))
    return base('HOLD_INVALID_REQUEST','Malformed or augmented CoNod input');
  if(request.token!=="'")
    return base('HOLD_NOT_NOD','No explicit CoNod token');
  if(!ORIGINS.has(request.origin)||request.presence!=='PRESENT')
    return base('HOLD_NOT_EXPLICIT','No ambient, wear, voice or absent-user trigger');
  if(request.scope!=='PUBLIC_SYNTHETIC'||request.effect!=='PREVIEW_ONLY')
    return base('HOLD_AUTHORITY','No private or externally consequential effect');
  if(!PRESSURES.has(request.pressure))
    return base('HOLD_PRESSURE_UNKNOWN','Pressure must be typed');
  const fixed=owned.fixture();
  if(request.work_id!==fixed.work_id)
    return base('HOLD_UNBOUND_WORKID','Selected WorkID missing or conflicting');
  if(request.source_hint!==undefined&&request.source_hint!==fixed.source_ref)
    return base('HOLD_SOURCE_CONFLICT','A latest/version label is not a verified source');
  const recovered=owned.recover(storage);
  if(recovered.state!=='RECOVERED_BROWSER_LOCAL')
    return base(recovered.state==='HELD_REVOKED'?'HOLD_REVOKED':'HOLD_NO_VERIFIED_LOCAL_WORK',
      'Existing browser-local WorkID not eligible',
      {observed_local_state:recovered.state});
  const pressured=['DEGRADING','SATURATED'].includes(request.pressure);
  return base('PREVIEW_ONLY_BROWSER_LOCAL',
    'Existing synthetic WorkID resolved; action not executed',{
      work_id:recovered.work_id,source_ref:recovered.source_ref,
      narrative_summary:recovered.summary,open_blockers:recovered.blockers,
      next_safe_deed:recovered.next_safe_deed,
      proposed_action:pressured?'PREVIEW_LOCAL_CHECKPOINT_AND_STOP':'PREVIEW_ONE_SAFE_NEXT_DEED',
      replay_semantics:'SAME_WORKID_NO_NEW_COMMIT',
      detached_session_supported:false,cold_readback_supported:false
    });
}
module.exports={SCHEMA,preview};
