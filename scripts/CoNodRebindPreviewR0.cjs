'use strict';
/* CoNod -> CoPre WorkID: synthetic, read-only preview candidate.
 * Apostrophe is intent, not a credential, a work object, or an executor.
 * No keyboard/mouse hooks, private reads, network, timers, jobs or writes.
 */
const owned=require('../examples/conodcothumb/context_rail_r1/CoOwnedWorkR0.js');
const SCHEMA='CoAll.CoNod.CoPre.RebindPreview.R0';
const {createHash}=require('node:crypto');
// Two immutable source witnesses; neither asserts that the named branch is still
// current. A new version must be separately reviewed and explicitly pinned.
const SOURCE_VERSIONS=Object.freeze({
  HISTORICAL_COPRE_R0:Object.freeze({
    repository:'CoCivium/CoCivium',path:'CoPre.md',
    commit:'63b41ead8797e5a781699f32bcbc77b78bdbd7af',
    git_blob_sha1:'eb677f0bc5760ddcaf33baf9f6b7787aef9886a6',
    source_ref:'CoCivium/CoCivium:CoPre.md@63b41ead8797e5a781699f32bcbc77b78bdbd7af'
  }),
  OBSERVED_MAIN_20261120:Object.freeze({
    repository:'CoCivium/CoCivium',path:'CoPre.md',
    commit:'090c532627cd014e6c41355ddd70b90a56cc03ff',
    git_blob_sha1:'7a1d9c2eada9432115a423bcb621793f474a4d28',
    source_ref:'CoCivium/CoCivium:CoPre.md@090c532627cd014e6c41355ddd70b90a56cc03ff'
  })
});
function sourceWitness(w){
  const held=(reason)=>({state:reason,source_digest_matched:false,
    branch_current:false,authority:'NONE',receiver_ack:false});
  if(!w||typeof w!=='object'||Array.isArray(w)||
     Object.keys(w).sort().join('|')!=='bytes|source_ref|version'||
     typeof w.version!=='string'||typeof w.source_ref!=='string'||
     !Buffer.isBuffer(w.bytes)||w.bytes.length===0||w.bytes.length>1048576)
    return held('HOLD_BAD_SOURCE_WITNESS');
  if(!Object.prototype.hasOwnProperty.call(SOURCE_VERSIONS,w.version))
    return held('HOLD_UNRECOGNIZED_VERSION');
  const pin=SOURCE_VERSIONS[w.version];
  if(w.source_ref!==pin.source_ref) return held('HOLD_UNPINNED_SOURCE_REF');
  const blob=createHash('sha1').update(Buffer.from('blob '+w.bytes.length+'\\0')).update(w.bytes).digest('hex');
  if(blob!==pin.git_blob_sha1) return held('HOLD_SOURCE_BYTES_DRIFT');
  return {state:'PINNED_SOURCE_BYTES_VERIFIED_ONLY',
    version:w.version,source_ref:pin.source_ref,
    source_git_blob_sha1:blob,source_sha256:createHash('sha256').update(w.bytes).digest('hex'),
    source_digest_matched:true,branch_current:false,authority:'NONE',receiver_ack:false};
}
const COPRE93_LEGACY_R0="' CoPre9.3+|CoGo+|Recover>Restart|State>Chat|Outcome>Session|Names!=Roles|JobsRecruitWorkers|Priory+Deps+Risk|Capability!=Authority|NSubstantialJobs|AdaptiveCheckpoints|MaxSafeParallel|1Job=1Receipt|1Actuator/Scope|FanIn=1|AutoNext+ReplaySafe|WorkSteal+Recover|BreakGlass!=Routine|CoGuardian:Gates|LocalFirst|Sites:3->40|Pub=URL+log+shot+test|3ind/HOLD|Rick=0Routine|NoPhantomACK";
// This is one exact compatibility spelling, not dynamic authority or latest-source proof.
function isNodIntent(token){
  if(typeof token!=='string')return false;
  const text=token.trim();
  return text==="'" || text===COPRE93_LEGACY_R0;
}
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
function preview(request,storage,witness){
  if(!request||typeof request!=='object'||Array.isArray(request)||
     Object.keys(request).some(k=>!KEYS.has(k)))
    return base('HOLD_INVALID_REQUEST','Malformed or augmented CoNod input');
  if(!isNodIntent(request.token))
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
  // A supplied source witness can validate pinned bytes but never elect a new
  // WorkID source. Changed main content is a migration HOLD, not a silent replay.
  let sourceProof=null;
  if(witness!==undefined){
    sourceProof=sourceWitness(witness);
    if(sourceProof.state!=='PINNED_SOURCE_BYTES_VERIFIED_ONLY')
      return base('HOLD_SOURCE_WITNESS',sourceProof.state);
    if(sourceProof.source_ref!==fixed.source_ref)
      return base('HOLD_SOURCE_MIGRATION_REQUIRED',
        'Pinned source differs from the stored WorkID; consent and migration unproven',
        {observed_source_ref:sourceProof.source_ref,source_digest_matched:true,
          branch_current:false});
  }
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
      detached_session_supported:false,cold_readback_supported:false,
      source_digest_matched:sourceProof!==null,
      source_sha256:sourceProof?.source_sha256||null,
      branch_current:false
    });
}
module.exports={SCHEMA,preview,sourceWitness,SOURCE_VERSIONS};
