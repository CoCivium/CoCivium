import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
const obj=JSON.parse(readFileSync(new URL('./snapshot.json',import.meta.url),'utf8'));
const html=readFileSync(new URL('./index.html',import.meta.url),'utf8');
const match=html.match(/const SNAPSHOT=(\\{.*\\});\\nconst vroot/s);
function canonical(x){if(Array.isArray(x))return '['+x.map(canonical).join(',')+']';if(x&&typeof x==='object')return '{'+Object.keys(x).sort().map(k=>JSON.stringify(k)+':'+canonical(x[k])).join(',')+'}';return JSON.stringify(x);}
function parity(o){const views=o.views;const keys=['object_id','version','source_ref','source_sha256','currentness','authority','privacy','recovery_ref','receiver_ack'];for(const k of keys){const first=views.NATIVE_OS_PROXY[k];for(const v of Object.values(views))if(v[k]!==first)return false;}return true;}
test('exact embedded machine twin',()=>assert.deepEqual(JSON.parse(match[1]),obj));
test('schema and explicit scope',()=>assert.equal(obj.scope,'OFFLINE_SYNTHETIC_READ_ONLY'));
test('four views',()=>assert.equal(Object.keys(obj.views).length,4));
test('nine parity fields',()=>assert.ok(parity(obj)));
test('tampered privacy breaks parity',()=>{const copy=structuredClone(obj);copy.views.COMAP.privacy='PRIVATE';assert.equal(parity(copy),false);});
test('tampered currentness breaks parity',()=>{const copy=structuredClone(obj);copy.views.COORB_COBAR.currentness='fake';assert.equal(parity(copy),false);});
test('source digest reproducible',()=>{const keys=['object_id','version','source_ref','source_text','privacy','authority','currentness','recovery_ref'];const payload=Object.fromEntries(keys.map(k=>[k,obj.source[k]]));assert.equal(createHash('sha256').update(canonical(payload)).digest('hex'),obj.source.source_sha256);});
test('every receiver held',()=>assert.ok(Object.values(obj.views).every(v=>v.receiver_ack==='HELD_NO_INDEPENDENT_RECEIVER')));
test('candidate cap ten',()=>assert.ok(obj.candidates.length<=10&&obj.candidates.length>=5));
test('baseline inverse null else orthogonal preserved',()=>{const names=new Set(obj.candidates.map(x=>x.operator));for(const x of ['BASELINE','INVERSE','NULL','ELSE','ORTHOGONAL'])assert.ok(names.has(x));});
test('no executed candidates',()=>assert.ok(obj.candidates.every(c=>c.actual_effects===0&&c.authority==='NONE'&&c.review_state==='CANDIDATE_NOT_EXECUTED')));
test('symbolic G_d class',()=>assert.equal(obj.candidates.find(c=>c.operator==='SYMBOLIC_GD').epistemic_class,'SYMBOLIC'));
test('ET hypothesis not evidence',()=>assert.equal(obj.candidates.find(c=>c.operator==='ET_ORIGIN').epistemic_class,'HYPOTHESIS'));
test('no workers or provider calls',()=>assert.deepEqual(obj.execution,{active_workers:0,provider_calls:0,external_effects:0}));
test('no outbound browser connection',()=>assert.match(html,/connect-src 'none'/));
test('no HTML external dependency',()=>assert.doesNotMatch(html,/<script[^>]*\\bsrc=|<link[^>]*\\bhref=/i));
test('no clipboard write',()=>assert.doesNotMatch(html,/navigator\\.clipboard\\.write/i));
test('no global key event listener',()=>assert.doesNotMatch(html,/addEventListener\\(['"]key(down|up)/i));
test('screenreader live view',()=>assert.match(html,/aria-live="polite"/));
test('reduced-motion preference honored',()=>assert.match(html,/prefers-reduced-motion/));
