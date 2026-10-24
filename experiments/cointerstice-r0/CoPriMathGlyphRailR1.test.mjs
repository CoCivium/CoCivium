import test from 'node:test';
import assert from 'node:assert/strict';
import {SCHEMA,GLYPHS,CONTEXTS,OPERATORS,ADDRESSABLE_COUNT,rail,addressAt,inverseCandidate}
  from './CoPriMathGlyphRailR1.mjs';

const base={surface:'COMAP_NODE',privacy:'LOCAL',gesture:'SYNTHETIC_TEST',
  explicit_preview:true,source_id:'source:synthetic:001',relation_type:'OBSERVED'};
const evalRail = (over={})=>rail({...base,...over});

test('01 schema pinned',()=>assert.equal(SCHEMA,'CoCivium.CoPriMathGlyphRail.R1'));
test('02 twenty accessible glyphs',()=>assert.equal(GLYPHS.length,20));
test('03 unique glyph semantic IDs',()=>assert.equal(new Set(GLYPHS.map(x=>x.id)).size,20));
test('04 unique glyph Unicode marks',()=>assert.equal(new Set(GLYPHS.map(x=>x.mark)).size,20));
test('05 all glyphs include readable and ASCII fallbacks',()=>{
  for(const x of GLYPHS)for(const k of ['id','mark','ascii','label'])
    assert.ok(typeof x[k]==='string'&&x[k].trim(),x.id+':'+k);
});
test('06 eleven explicit contexts',()=>assert.equal(Object.keys(CONTEXTS).length,11));
test('07 eight finite query operators',()=>assert.equal(OPERATORS.length,8));
test('08 1760 addressable descriptions, no worker claim',()=>assert.equal(ADDRESSABLE_COUNT,1760));
test('09 address zero deterministic',()=>assert.deepEqual(addressAt(0),addressAt(0)));
test('10 address last is bounded',()=>assert.equal(addressAt(1759).address,1759));
test('11 address negative rejected',()=>assert.throws(()=>addressAt(-1),RangeError));
test('12 address beyond capacity rejected',()=>assert.throws(()=>addressAt(1760),RangeError));
test('13 fractional and unsafe addresses rejected',()=>{
  assert.throws(()=>addressAt(1.5),RangeError);
  assert.throws(()=>addressAt(Number.MAX_SAFE_INTEGER+1),RangeError);
});
test('14 address sampling never launches workers',()=>{
  for(const idx of [0,1,19,39,127,511,900,1759]){
    const x=addressAt(idx);assert.equal(x.materialized_workers,0);
    assert.equal(x.authority,'NONE');assert.ok(GLYPHS.some(g=>g.id===x.semantic_id));
  }
});
test('15 null metadata held',()=>assert.equal(rail(null).state,'HOLD_INVALID_CONTEXT'));
test('16 unknown metadata keys fail closed, no accidental keylogging',()=>{
  for(const k of ['raw_key','text','clipboard','key','password','screen_capture','coords']){
    const v=evalRail({[k]:'synthetic_not_a_secret'});
    assert.equal(v.state,'HOLD_UNDECLARED_OR_SENSITIVE_FIELDS');
    assert.equal(JSON.stringify(v).includes('synthetic_not_a_secret'),false);
  }
});
test('17 no implicit unknown privacy classification',()=>assert.equal(evalRail({privacy:undefined}).state,'HOLD_UNKNOWN_OR_PRIVATE_CONTEXT'));
test('18 private metadata held',()=>assert.equal(evalRail({privacy:'PRIVATE'}).state,'HOLD_UNKNOWN_OR_PRIVATE_CONTEXT'));
test('19 unknown surface held',()=>assert.equal(evalRail({surface:'SECRET_PAGE'}).state,'HOLD_UNKNOWN_SURFACE'));
test('20 native mouse gesture is not silently bound',()=>assert.equal(evalRail({gesture:'MIDDLE'}).state,'HOLD_NATIVE_GESTURE_NOT_VERIFIED'));
test('21 native thumb gesture is not silently bound',()=>assert.equal(evalRail({gesture:'THUMB'}).state,'HOLD_NATIVE_GESTURE_NOT_VERIFIED'));
test('22 no preview absent explicit user request',()=>assert.equal(evalRail({explicit_preview:false}).state,'HOLD_NO_PREVIEW_REQUEST'));
test('23 external effects held even with explicit preview',()=>assert.equal(evalRail({external_effect_requested:true}).state,'HOLD_EXTERNAL_EFFECT'));
test('24 source pointer must be restricted and nonsecret',()=>{
  assert.equal(evalRail({source_id:'../private path with spaces'}).state,'HOLD_INVALID_SOURCE_POINTER');
  assert.equal(evalRail({source_id:'https://example.net/?token=NO'}).state,'HOLD_INVALID_SOURCE_POINTER');
});
test('25 declared preview never authenticates a source',()=>{
  const r=evalRail();
  assert.equal(r.state,'PASS_DECLARED_SHADOW_PREVIEW_ONLY');
  assert.equal(r.source_authenticity,'NOT_CHECKED');assert.equal(r.receiver_ack,null);
});
test('26 visible menu always Preview More Cancel and Escape',()=>{
  const r=evalRail();
  assert.deepEqual(r.choices,['Preview','More','Cancel']);assert.equal(r.dismiss,'ESC');
});
test('27 no effect authority or workers from preview',()=>{
  const r=evalRail();assert.equal(r.authority,'NONE');assert.equal(r.materialized_workers,0);
  assert.ok(Object.values(r.effects).every(n=>n===0));
});
test('28 relation reversal is not reverse causation',()=>{
  const x=inverseCandidate('CAUSES');assert.equal(x.status,'HYPOTHESIS_ONLY');assert.equal(x.proven,false);
});
test('29 dependency inversion only substitute hypothesis',()=>{
  assert.equal(inverseCandidate('DEPENDS_ON').proven,false);
});
test('30 support challenge is not evidence of falsehood',()=>{
  assert.equal(inverseCandidate('SUPPORTED_BY').status,'CHALLENGE_CANDIDATE');
});
test('31 open-world observed missing cannot prove absence',()=>{
  assert.equal(inverseCandidate('OBSERVED').status,'OPEN_WORLD_UNKNOWN');
});
test('32 absence missing finite negative witness is held',()=>{
  assert.equal(inverseCandidate('OBSERVED_ABSENT',false,'evidence:123456').status,'HOLD_NEGATIVE_EVIDENCE');
});
test('33 scoped absence still not universal proof',()=>{
  const x=inverseCandidate('OBSERVED_ABSENT',true,'evidence:123456');
  assert.equal(x.status,'SCOPED_NEGATIVE_CANDIDATE');assert.equal(x.proven,false);
});
test('34 metaphysical source remains a metaphor or testable hypothesis',()=>{
  for(const q of ['SYMBOLIC_GD','ET_STORY'])
    assert.equal(inverseCandidate(q).status,'METAPHOR_OR_HYPOTHESIS');
});
test('35 no scientific conclusion from a naked glyph',()=>{
  assert.ok(evalRail({relation_type:'SYMBOLIC_GD'}).nonclaims.includes('SYMBOL_NE_MEASURED_PHYSICS'));
});
test('36 comparable contexts select distinct relation rails',()=>{
  const a=evalRail({surface:'CODE'}).rail.map(x=>x.semantic_id);
  const b=evalRail({surface:'IMAGE'}).rail.map(x=>x.semantic_id);
  assert.notDeepEqual(a,b);
});
test('37 no hidden private state in blocked response',()=>{
  const r=evalRail({privacy:'RESTRICTED',source_id:'private:identifier'});
  assert.equal(r.rail.length,0);assert.equal(JSON.stringify(r).includes('private:identifier'),false);
});
for(const [name,ids] of Object.entries(CONTEXTS)){
  test('context '+name+' exactly 8 accessible options and zero effects',()=>{
    assert.equal(ids.length,8);
    assert.equal(new Set(ids).size,8);
    const r=evalRail({surface:name});
    assert.equal(r.rail_size,8);
    assert.equal(r.rail.length,8);
    assert.deepEqual(r.rail.map(x=>x.semantic_id),ids);
    assert.ok(r.rail.every(x=>x.label&&x.spoken_fallback&&x.text_fallback));
    assert.ok(Object.values(r.effects).every(v=>v===0));
    assert.equal(r.materialized_workers,0);
    assert.equal(r.receiver_ack,null);
  });
}
