import test from 'node:test';
import assert from 'node:assert/strict';
import { InputGapShadow, SCHEMA } from './CoInputGapR0.mjs';
function fresh() { const g = new InputGapShadow(); assert.equal(g.arm({consent:true,scope:'OWNED_EDITOR',atMs:0}).status,'ARMED_LOCAL_SHADOW'); return g; }
function edit(g,t) {return g.note({kind:'LOCAL_EDIT',atMs:t});}
function ready(g) {edit(g,100);edit(g,200);return g.inspect({atMs:1000});}

test('unarmed by default and denied consent',()=>{const g=new InputGapShadow();assert.equal(g.inspect({atMs:0}).status,'HOLD_NOT_ARMED');assert.equal(g.arm({scope:'OWNED_EDITOR'}).status,'HOLD_NOT_ARMED');});
test('must be app-owned, not global keyboard',()=>{const g=new InputGapShadow();assert.equal(g.arm({consent:true,scope:'GLOBAL_KEYBOARD'}).status,'HOLD_NOT_ARMED');});
test('sensitive context refuses arm',()=>{const g=new InputGapShadow();assert.equal(g.arm({consent:true,scope:'OWNED_EDITOR',sensitive:true}).status,'HOLD_NOT_ARMED');});
test('reject raw keys content or clipboard',()=>{const g=fresh();for(const name of ['key','code','text','raw','clipboard','password','selectedText','windowTitle','screen','content','prompt','url','path']){assert.throws(()=>g.note({kind:'LOCAL_EDIT',atMs:100,[name]:'secret'}),/forbidden/);}});
test('no edit, no proposal even after quiet time',()=>{const g=fresh();assert.equal(g.inspect({atMs:50000}).status,'HOLD_INSUFFICIENT_LOCAL_ACTIVITY');});
test('one edit is insufficient',()=>{const g=fresh();edit(g,100);assert.equal(g.inspect({atMs:1200}).status,'HOLD_INSUFFICIENT_LOCAL_ACTIVITY');});
test('quiet interval must elapse',()=>{const g=fresh();edit(g,100);edit(g,200);assert.equal(g.inspect({atMs:999}).status,'HOLD_QUIET_WINDOW');});
test('quiet emits shadow only with zero effects',()=>{const g=fresh();const p=ready(g);assert.equal(p.schema,SCHEMA);assert.equal(p.status,'CANDIDATE_ONLY');assert.equal(p.proposed_action,'INSPECT_RELATIONS');assert.equal(p.authority,'NONE');assert.deepEqual(p.effects,{keys_captured:0,text_saved:0,workers_spawned:0,messages_sent:0});});
test('preview is once only until explicit decision',()=>{const g=fresh();ready(g);assert.equal(g.inspect({atMs:1100}).status,'HOLD_AWAITING_DECISION');});
test('accept never executes or sends anything',()=>{const g=fresh();ready(g);const p=g.decide({atMs:1200,decision:'ACCEPT_PREVIEW'});assert.equal(p.status,'PREVIEW_ACCEPTED_ONLY');assert.equal(p.effects.workers_spawned,0);});
test('reject still requires fresh edits and cooldown',()=>{const g=fresh();ready(g);g.decide({atMs:1200,decision:'REJECT_PREVIEW'});edit(g,1250);edit(g,1300);assert.equal(g.inspect({atMs:2200}).status,'HOLD_COOLDOWN');assert.equal(g.inspect({atMs:4100}).proposed_action,'CHALLENGE_PREMISE');});
test('sensitive transition disarms and clears pending',()=>{const g=fresh();edit(g,100);const p=g.inspect({atMs:1100,sensitive:true});assert.equal(p.status,'DISARMED_PRIVATE_OR_UNFOCUSED');assert.equal(g.status().edits_capped,0);});
test('focus loss disarms and clears pending',()=>{const g=fresh();edit(g,100);assert.equal(g.note({kind:'FOCUS_LOST',atMs:200}).status,'DISARMED_PRIVATE_OR_UNFOCUSED');assert.equal(g.status().armed,false);});
test('unknown event must not count as edit',()=>{const g=fresh();assert.equal(g.note({kind:'GLOBAL_KEYDOWN',atMs:100}).status,'HOLD_UNKNOWN_EVENT');assert.equal(g.status().edits_capped,0);});
test('local pointer alone cannot infer edit intent',()=>{const g=fresh();g.note({kind:'LOCAL_POINTER',atMs:100});assert.equal(g.inspect({atMs:4000}).status,'HOLD_INSUFFICIENT_LOCAL_ACTIVITY');});
test('time regressions fail closed',()=>{const g=fresh();edit(g,100);assert.throws(()=>edit(g,99),/backward/);});
test('configuration finite',()=>{for(const x of [{quietMs:0},{quietMs:Infinity},{minEdits:0},{cooldownMs:0},{quietMs:30000}])assert.throws(()=>new InputGapShadow(x),/bounded/);});
test('bad decision cannot cause effect',()=>{const g=fresh();ready(g);assert.equal(g.decide({atMs:1100,decision:'SEND'}).status,'HOLD_BAD_DECISION');});
test('cancel discards state',()=>{const g=fresh();ready(g);g.note({kind:'CANCEL',atMs:1100});assert.equal(g.status().awaiting_decision,false);assert.equal(g.status().armed,false);});
test('proposal cycle is bounded and reversible',()=>{const g=fresh();let p=ready(g);assert.equal(p.proposed_action,'INSPECT_RELATIONS');g.decide({atMs:1200,decision:'REJECT_PREVIEW'});edit(g,4500);edit(g,4600);p=g.inspect({atMs:5500});assert.equal(p.proposed_action,'CHALLENGE_PREMISE');g.decide({atMs:5600,decision:'REJECT_PREVIEW'});edit(g,8700);edit(g,8800);p=g.inspect({atMs:9900});assert.equal(p.proposed_action,'COMPARE_PRIOR_VERSION');});
