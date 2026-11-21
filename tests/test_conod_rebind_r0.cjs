'use strict';
const assert=require('node:assert/strict');
const {test}=require('node:test');
const owned=require('../examples/conodcothumb/context_rail_r1/CoOwnedWorkR0.js');
const {preview}=require('../scripts/CoNodRebindPreviewR0.cjs');
const fixed=owned.fixture();
function storage(){
 const state=new Map();let writes=0;
 return {getItem:k=>state.has(k)?state.get(k):null,
  setItem:(k,v)=>{writes++;state.set(k,v)},
  writes:()=>writes,setRaw:(k,v)=>state.set(k,v),
  getRaw:k=>state.get(k)};
}
function req(over={}){return {token:"'",origin:'EXPLICIT_KEYBOARD',
 presence:'PRESENT',scope:'PUBLIC_SYNTHETIC',effect:'PREVIEW_ONLY',
 pressure:'HEALTHY',work_id:fixed.work_id,...over};}
function prepared(){
 const s=storage();
 const r=owned.preserve(s,{privacy:'PUBLIC',context:'RESEARCH',
  question:'WHAT_ELSE',gesture:'EXPLICIT_RING',preview_state:'PROPOSED_ONLY'});
 assert.equal(r.state,'COMMITTED_BROWSER_LOCAL');
 return s;
}
test('one explicit nod reads an existing WorkID without writes',()=>{
 const s=prepared(),before=s.writes(),out=preview(req(),s);
 assert.equal(out.state,'PREVIEW_ONLY_BROWSER_LOCAL');
 assert.equal(out.work_id,fixed.work_id);
 assert.equal(s.writes(),before);
 assert.equal(out.authority,'NONE');
 assert.ok(Object.values(out.effects).every(x=>x===0));
 assert.equal(out.source_verified,false);
 assert.equal(out.receiver_ack,false);
});
test('repeated nod previews are identical and do not enqueue work',()=>{
 const s=prepared(),a=preview(req(),s),b=preview(req(),s);
 assert.deepEqual(a,b);assert.equal(s.writes(),1);
});
test('unrecognized token cannot trigger',()=>assert.equal(preview(req({token:'go'}),prepared()).state,'HOLD_NOT_NOD'));
test('missing WorkID held',()=>assert.equal(preview(req({work_id:''}),prepared()).state,'HOLD_UNBOUND_WORKID'));
test('foreign WorkID held',()=>assert.equal(preview(req({work_id:'other'}),prepared()).state,'HOLD_UNBOUND_WORKID'));
test('no durable record held',()=>assert.equal(preview(req(),storage()).state,'HOLD_NO_VERIFIED_LOCAL_WORK'));
test('revoked record held',()=>{const s=prepared();owned.revoke(s);assert.equal(preview(req(),s).state,'HOLD_REVOKED');});
test('forged ACK in stored record held',()=>{
 const s=prepared(),row=JSON.parse(s.getRaw(owned.STORAGE_KEY));
 row.receiver_ack=true;s.setRaw(owned.STORAGE_KEY,JSON.stringify(row));
 assert.equal(preview(req(),s).state,'HOLD_NO_VERIFIED_LOCAL_WORK');
});
test('fake latest source label held',()=>assert.equal(preview(req({source_hint:'latest'}),prepared()).state,'HOLD_SOURCE_CONFLICT'));
test('matching hint cannot assert independent source verification',()=>{
 const out=preview(req({source_hint:fixed.source_ref}),prepared());
 assert.equal(out.state,'PREVIEW_ONLY_BROWSER_LOCAL');
 assert.equal(out.source_verified,false);
});
test('saturated pressure proposes handoff without starting worker',()=>{
 const s=prepared(),out=preview(req({pressure:'SATURATED'}),s);
 assert.equal(out.proposed_action,'PREVIEW_LOCAL_CHECKPOINT_AND_STOP');
 assert.equal(out.effects.jobs_enqueued,0);assert.equal(s.writes(),1);
});
test('unknown pressure yields only safe preview',()=>{
 const out=preview(req({pressure:'UNKNOWN'}),prepared());
 assert.equal(out.proposed_action,'PREVIEW_ONE_SAFE_NEXT_DEED');
 assert.equal(out.real_session_recovery,false);
});
test('absent user cannot imply apostrophe',()=>assert.equal(preview(req({presence:'ABSENT'}),prepared()).state,'HOLD_NOT_EXPLICIT'));
test('unverified wear sensor cannot trigger',()=>assert.equal(preview(req({origin:'IN_EAR_SENSOR'}),prepared()).state,'HOLD_NOT_EXPLICIT'));
test('private scope is not delegated',()=>assert.equal(preview(req({scope:'PRIVATE'}),prepared()).state,'HOLD_AUTHORITY'));
test('execution intent is not preview authority',()=>assert.equal(preview(req({effect:'RUN_ALL'}),prepared()).state,'HOLD_AUTHORITY'));
test('unknown admin field is rejected',()=>assert.equal(preview(req({admin:true}),prepared()).state,'HOLD_INVALID_REQUEST'));
test('null request held',()=>assert.equal(preview(null,prepared()).state,'HOLD_INVALID_REQUEST'));
test('missing receiver held without writing',()=>assert.equal(preview(req(),null).state,'HOLD_NO_VERIFIED_LOCAL_WORK'));
test('unknown pressure is not silently defaulted',()=>assert.equal(preview(req({pressure:'FOREVER'}),prepared()).state,'HOLD_PRESSURE_UNKNOWN'));

// Exact long-form compatibility is an intent alias, NOT a new authority or currentness proof.
const COPRE93_LEGACY_R0="' CoPre9.3+|CoGo+|Recover>Restart|State>Chat|Outcome>Session|Names!=Roles|JobsRecruitWorkers|Priory+Deps+Risk|Capability!=Authority|NSubstantialJobs|AdaptiveCheckpoints|MaxSafeParallel|1Job=1Receipt|1Actuator/Scope|FanIn=1|AutoNext+ReplaySafe|WorkSteal+Recover|BreakGlass!=Routine|CoGuardian:Gates|LocalFirst|Sites:3->40|Pub=URL+log+shot+test|3ind/HOLD|Rick=0Routine|NoPhantomACK";
test('exact CoPre9.3 fallback equals bare nod for the same verified local work',()=>{
 const s=prepared(),before=s.writes();
 const short=preview(req(),s),long=preview(req({token:COPRE93_LEGACY_R0}),s);
 assert.deepEqual(long,short);
 assert.equal(s.writes(),before);
 assert.equal(long.authority,'NONE');
 assert.equal(long.receiver_ack,false);
 assert.equal(long.source_verified,false);
 assert.equal(long.real_session_recovery,false);
});
test('quoted and padded CoPre9.3 fallback remains equivalent but changes nothing',()=>{
 const s=prepared();
 const out=preview(req({token:'  """  '+COPRE93_LEGACY_R0+'  """  '}),s);
 assert.equal(out.state,'HOLD_NOT_NOD');
 const padded=preview(req({token:'  '+COPRE93_LEGACY_R0+'  '}),s);
 assert.equal(padded.state,'PREVIEW_ONLY_BROWSER_LOCAL');
});
test('altered or future CoPre variants cannot silently replace the exact pinned alias',()=>{
 const s=prepared();
 for(const token of [COPRE93_LEGACY_R0.replace('CoPre9.3+','CoPre9.4+'),
   COPRE93_LEGACY_R0.replace('NoPhantomACK','PhantomACK'),
   COPRE93_LEGACY_R0+'|EXTERNAL_SEND', '""" '+COPRE93_LEGACY_R0+' """'])
  assert.equal(preview(req({token}),s).state,'HOLD_NOT_NOD');
});
test('long-form fallback cannot weaken privacy, presence, or effect gates',()=>{
 const s=prepared();
 assert.equal(preview(req({token:COPRE93_LEGACY_R0,scope:'PRIVATE'}),s).state,'HOLD_AUTHORITY');
 assert.equal(preview(req({token:COPRE93_LEGACY_R0,effect:'RUN_ALL'}),s).state,'HOLD_AUTHORITY');
 assert.equal(preview(req({token:COPRE93_LEGACY_R0,presence:'ABSENT'}),s).state,'HOLD_NOT_EXPLICIT');
});

const {sourceWitness,SOURCE_VERSIONS}=require('../scripts/CoNodRebindPreviewR0.cjs');
function witness(version,bytes){
  return {version,source_ref:SOURCE_VERSIONS[version].source_ref,bytes};
}
test('CoPre source witness requires explicit typed bytes, pin and schema',()=>{
  for(const x of [null,{},[],{version:'HISTORICAL_COPRE_R0',source_ref:SOURCE_VERSIONS.HISTORICAL_COPRE_R0.source_ref,bytes:'forged'}]){
    assert.equal(sourceWitness(x).state,'HOLD_BAD_SOURCE_WITNESS');
  }
  const x={version:'HISTORICAL_COPRE_R0',source_ref:SOURCE_VERSIONS.HISTORICAL_COPRE_R0.source_ref,bytes:Buffer.from('forged'),is_admin:true};
  assert.equal(sourceWitness(x).state,'HOLD_BAD_SOURCE_WITNESS');
});
test('unknown version cannot be elevated by an actor-provided source digest',()=>{
  const x={version:'LATEST',source_ref:'any',bytes:Buffer.from('forged')};
  assert.equal(sourceWitness(x).state,'HOLD_UNRECOGNIZED_VERSION');
});
test('exact pin rejects changed source object and misleading path',()=>{
  const x=witness('HISTORICAL_COPRE_R0',Buffer.from('not CoPre'));
  assert.equal(sourceWitness(x).state,'HOLD_SOURCE_BYTES_DRIFT');
  x.source_ref='CoCivium/CoCivium:CoPre.md@main';
  assert.equal(sourceWitness(x).state,'HOLD_UNPINNED_SOURCE_REF');
});
test('source witness rejects non-Buffer bytes and empty or oversized objects',()=>{
  const pin=SOURCE_VERSIONS.HISTORICAL_COPRE_R0;
  for(const bytes of [new Uint8Array([65]),Buffer.alloc(0),Buffer.alloc(1048577)]){
    assert.equal(sourceWitness({version:'HISTORICAL_COPRE_R0',source_ref:pin.source_ref,bytes}).state,'HOLD_BAD_SOURCE_WITNESS');
  }
});
test('untrusted source witness cannot authorize an effect or replace local WorkID',()=>{
  const s=prepared(),before=s.writes();
  const fake=witness('HISTORICAL_COPRE_R0',Buffer.from('forged'));
  const r=preview(req(),s,fake);
  assert.equal(r.state,'HOLD_SOURCE_WITNESS');
  assert.equal(r.authority,'NONE');
  assert.equal(r.receiver_ack,false);
  assert.equal(s.writes(),before);
});
test('missing witness still gives only original zero-authority preview',()=>{
  const r=preview(req(),prepared());
  assert.equal(r.state,'PREVIEW_ONLY_BROWSER_LOCAL');
  assert.equal(r.source_verified,false);
  assert.equal(r.source_digest_matched,false);
  assert.equal(r.branch_current,false);
});
if(process.env.CONOD_SOURCE_WITNESS_CI==='1'){
  const {execFileSync}=require('node:child_process');
  function exactBytes(version){
    const pin=SOURCE_VERSIONS[version];
    return execFileSync('git',['show',pin.commit+':'+pin.path],
      {maxBuffer:1048576});
  }
  test('historical CoPre git object is exact and permits digest-matched preview only',()=>{
    const bytes=exactBytes('HISTORICAL_COPRE_R0');
    const proof=sourceWitness(witness('HISTORICAL_COPRE_R0',bytes));
    assert.equal(proof.state,'PINNED_SOURCE_BYTES_VERIFIED_ONLY');
    assert.equal(proof.branch_current,false);
    assert.equal(proof.receiver_ack,false);
    assert.equal(proof.source_sha256,
      '58f8c722bfbfc34cac41189c072d2effe4b19dbbe8a37be4f8687344d6b00b9a');
    const s=prepared(),before=s.writes(),r=preview(req(),s,witness('HISTORICAL_COPRE_R0',bytes));
    assert.equal(r.state,'PREVIEW_ONLY_BROWSER_LOCAL');
    assert.equal(r.source_digest_matched,true);
    assert.equal(r.source_verified,false);
    assert.equal(r.branch_current,false);
    assert.equal(s.writes(),before);
  });
  test('observed main CoPre is content-verified but held on old WorkID',()=>{
    const bytes=exactBytes('OBSERVED_MAIN_20261120');
    const proof=sourceWitness(witness('OBSERVED_MAIN_20261120',bytes));
    assert.equal(proof.state,'PINNED_SOURCE_BYTES_VERIFIED_ONLY');
    assert.equal(proof.branch_current,false);
    assert.notEqual(proof.source_ref,fixed.source_ref);
    const s=prepared(),before=s.writes(),r=preview(req(),s,witness('OBSERVED_MAIN_20261120',bytes));
    assert.equal(r.state,'HOLD_SOURCE_MIGRATION_REQUIRED');
    assert.equal(r.source_digest_matched,true);
    assert.equal(r.receiver_ack,false);
    assert.equal(r.authority,'NONE');
    assert.equal(s.writes(),before);
  });
  test('tampering with actual historical bytes fails closed',()=>{
    const bytes=exactBytes('HISTORICAL_COPRE_R0');
    bytes[bytes.length-1]^=1;
    const proof=sourceWitness(witness('HISTORICAL_COPRE_R0',bytes));
    assert.equal(proof.state,'HOLD_SOURCE_BYTES_DRIFT');
  });
}
