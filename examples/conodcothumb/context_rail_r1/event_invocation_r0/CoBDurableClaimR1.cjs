'use strict';
// TEST DONOR ONLY. No production admission, authentication, or independent receiver.
// Filesystem writes are confined to the caller-supplied isolated fixture directory.
const fs = require('node:fs');
const path = require('node:path');
const crypto = require('node:crypto');
const SCHEMA = 'CoAll.CoBDurableClaim.ShadowR1';
const EFFECTS = Object.freeze({device:0,network:0,send:0,account:0,publication:0});
const FIELDS = new Set(['event_id','work_id','operation','privacy','observed_ms','expires_ms']);
const ident = s => typeof s === 'string' && /^[A-Za-z0-9][A-Za-z0-9_.:-]{0,63}$/.test(s);
function receipt(state, reason, fields={}) {
  return {schema:SCHEMA,state,reason,external_effects:{...EFFECTS},
    authority:'SYNTHETIC_POLICY_ONLY',receiver_readproof:'NOT_TESTED',...fields};
}
function validate(route, event, now_ms) {
  if (!['BUTTON','COB_EVENT'].includes(route) || !Number.isSafeInteger(now_ms) || now_ms < 0 ||
      !event || typeof event !== 'object' || Array.isArray(event) ||
      Object.keys(event).some(k => !FIELDS.has(k))) return 'UNTRUSTED_ROUTE_OR_PACKET';
  if (!ident(event.event_id) || !ident(event.work_id)) return 'INVALID_ID';
  if (event.operation !== 'REFRESH_LOCAL_STATUS' || event.privacy !== 'PUBLIC_SYNTHETIC') return 'NOT_ALLOWLISTED';
  if (!Number.isSafeInteger(event.observed_ms) || !Number.isSafeInteger(event.expires_ms) ||
      event.observed_ms > now_ms || now_ms > event.expires_ms ||
      event.expires_ms - event.observed_ms > 60000) return 'STALE_FUTURE_OR_UNBOUNDED';
  return null;
}
function syncDir(dir) {
  // Windows may reject fsync on directories; fail closed before the effect.
  const fd = fs.openSync(dir, 'r');
  try { fs.fsyncSync(fd); } finally { fs.closeSync(fd); }
}
function atomicJson(file, obj) {
  const tmp = file + '.tmp.' + process.pid;
  const fd = fs.openSync(tmp, 'wx', 0o600);
  try { fs.writeFileSync(fd, JSON.stringify(obj)+'\n'); fs.fsyncSync(fd); }
  finally { fs.closeSync(fd); }
  fs.renameSync(tmp, file);
  syncDir(path.dirname(file));
}
// A completion claim is accepted only when its full local evidence chain agrees.
// These fixture records are not authenticated receiver acknowledgements.
function safeJson(file) {
  try {
    const stat=fs.lstatSync(file);
    if(!stat.isFile()||stat.isSymbolicLink()||stat.size<3||stat.size>4096)return null;
    const obj=JSON.parse(fs.readFileSync(file,'utf8'));
    return obj&&typeof obj==='object'&&!Array.isArray(obj)?obj:null;
  } catch(_) {return null;}
}
function checkedCompletion(dir,work_id,operation) {
  const claim=safeJson(path.join(dir,'claim.json'));
  const effect=safeJson(path.join(dir,'synthetic_effect.json'));
  const complete=safeJson(path.join(dir,'completed.json'));
  if(!claim||!effect||!complete)return null;
  if(claim.work_id!==work_id||claim.operation!==operation||
     !ident(claim.event_id)||!['BUTTON','COB_EVENT'].includes(claim.route)||
     claim.phase!=='CLAIMED')return null;
  if(effect.work_id!==work_id||effect.operation!==operation||
     effect.event_id!==claim.event_id||effect.effect!=='LOCAL_FIXTURE_MARKER')return null;
  if(complete.work_id!==work_id||complete.operation!==operation||
     complete.event_id!==claim.event_id||complete.phase!=='COMPLETED')return null;
  return {work_id,first_event_id:claim.event_id};
}
function invoke({root,route,event,now_ms=1000,inject_crash=null}) {
  const bad = validate(route,event,now_ms);
  if (bad) return receipt('HELD',bad);
  // The test-root is chosen by the host, never the untrusted packet.
  // Refuse non-existing or symlinked roots, including symlinked ancestors.
  if (typeof root !== 'string' || !path.isAbsolute(root)) return receipt('HELD','ISOLATED_ROOT_REQUIRED');
  try {
    const stat=fs.lstatSync(root);
    if(!stat.isDirectory()||stat.isSymbolicLink()||fs.realpathSync(root)!==path.resolve(root))
      return receipt('HELD','ISOLATED_ROOT_UNVERIFIED');
  } catch(_) {return receipt('HELD','ISOLATED_ROOT_UNVERIFIED');}
  const key = crypto.createHash('sha256').update(event.work_id+'\0'+event.operation).digest('hex');
  const dir = path.join(root,key);
  try { fs.mkdirSync(dir); syncDir(root); }
  catch (e) {
    if (e.code !== 'EEXIST') throw e;
    try {
      const stat=fs.lstatSync(dir);
      if(!stat.isDirectory()||stat.isSymbolicLink())
        return receipt('HELD','CLAIMED_OR_RECOVERY_REQUIRED',{work_id:event.work_id});
    } catch(_){return receipt('HELD','CLAIMED_OR_RECOVERY_REQUIRED',{work_id:event.work_id});}
    const prior=checkedCompletion(dir,event.work_id,event.operation);
    if(prior)return receipt('DEDUPED','DURABLE_COMPLETION_FOUND',prior);
    return receipt('HELD','CLAIMED_OR_RECOVERY_REQUIRED',{work_id:event.work_id});
  }
  // Failure before the claim is durable cannot produce an effect.
  atomicJson(path.join(dir,'claim.json'),{work_id:event.work_id,operation:event.operation,
    event_id:event.event_id,route,phase:'CLAIMED'});
  if (inject_crash==='AFTER_CLAIM') process.exit(71);
  // A marker in an isolated fixture is the ONLY simulated effect.
  atomicJson(path.join(dir,'synthetic_effect.json'),{work_id:event.work_id,
    operation:event.operation,event_id:event.event_id,effect:'LOCAL_FIXTURE_MARKER'});
  if (inject_crash==='AFTER_EFFECT') process.exit(72);
  atomicJson(path.join(dir,'completed.json'),{work_id:event.work_id,
    operation:event.operation,event_id:event.event_id,phase:'COMPLETED'});
  return receipt('LOCAL_ONLY_EXECUTED','SYNTHETIC_FIXTURE_MARKER',{work_id:event.work_id,event_id:event.event_id});
}
if (require.main===module) {
  const [root,route,event_json,inject_crash] = process.argv.slice(2);
  try { const result=invoke({root,route,event:JSON.parse(event_json),inject_crash});
    process.stdout.write(JSON.stringify(result)+'\n'); }
  catch (e) {process.stderr.write('FIXTURE_ERROR: '+e.code+'\n'); process.exitCode=73;}
}
module.exports={invoke,validate,SCHEMA};
