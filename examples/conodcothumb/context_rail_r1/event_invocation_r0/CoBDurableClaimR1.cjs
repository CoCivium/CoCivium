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
function invoke({root,route,event,now_ms=1000,inject_crash=null}) {
  const bad = validate(route,event,now_ms);
  if (bad) return receipt('HELD',bad);
  // The test-root is not chosen from untrusted event fields.
  if (typeof root !== 'string' || !path.isAbsolute(root)) return receipt('HELD','ISOLATED_ROOT_REQUIRED');
  const key = crypto.createHash('sha256').update(event.work_id+'\0'+event.operation).digest('hex');
  fs.mkdirSync(root,{recursive:true});
  const dir = path.join(root,key);
  try { fs.mkdirSync(dir); syncDir(root); }
  catch (e) {
    if (e.code !== 'EEXIST') throw e;
    const completed = path.join(dir,'completed.json');
    if (fs.existsSync(completed)) {
      // Conservative: treat unreadable/corrupt completed evidence as HELD.
      try {
        const data = JSON.parse(fs.readFileSync(completed,'utf8'));
        if (data.work_id===event.work_id && data.operation===event.operation)
          return receipt('DEDUPED','DURABLE_COMPLETION_FOUND',{work_id:event.work_id,first_event_id:data.event_id});
      } catch (_) { /* fail closed */ }
    }
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
