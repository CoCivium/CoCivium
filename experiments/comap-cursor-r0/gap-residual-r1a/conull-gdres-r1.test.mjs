import test from 'node:test';
import assert from 'node:assert/strict';
import {NULL_STATES,qualifyNull,publicNullProjection,numericResidual,edgeResidual,electNullSeat} from './conull-gdres-r1.mjs';
const base=()=>({id:'n1',null_state:'UNKNOWN',privacy:'PUBLIC',authority:'NONE',coverage:'UNKNOWN',evidence_refs:[],source_ref:'PUBLIC_DOC'});
const measured=()=>({privacy:'PUBLIC',expectation_ref:'forecast:1',observation_ref:'sensor:2',independence_evidence:true,
 expected:10,observed:12,unit:'ms',observed_unit:'ms',tolerance:1,valid_at:'2026-10-23T18:00:00Z',observation_valid_at:'2026-10-23T18:00:00Z',observed_at:'2026-10-23T18:05:00Z'});
const edges=()=>({privacy:'PUBLIC',coverage:'PARTIAL',expectation_ref:'forecast:1',observation_ref:'measurement:2',
 expected_at:'2026-10-22T18:00:00Z',target_valid_at:'2026-10-23T18:00:00Z',observed_at:'2026-10-23T18:05:00Z',observation_valid_at:'2026-10-23T18:00:00Z',coverage_evidence_ref:'scope:full-scan',independence_evidence:true,
 expected:[{id:'A',epistemic:'PREDICTED'},{id:'B',epistemic:'PREDICTED'}],observed:[{id:'A',epistemic:'OBSERVED'},{id:'C',epistemic:'OBSERVED'}]});
test('1 distinct typed CoNull states',()=>assert.equal(new Set(NULL_STATES).size,12));
test('2 unknown is not observed absent',()=>assert.equal(qualifyNull(base()).null_state,'UNKNOWN'));
test('3 absence requires closed world',()=>assert.throws(()=>qualifyNull({...base(),null_state:'OBSERVED_ABSENT',evidence_refs:['scope:1']}),/CLOSED_WORLD/));
test('4 absence requires valid dated evidence',()=>assert.throws(()=>qualifyNull({...base(),null_state:'OBSERVED_ABSENT',coverage:'COMPLETE',evidence_refs:['scope:1']}),/CLOSED_WORLD/));
test('5 closed world absence passes with evidence',()=>assert.equal(qualifyNull({...base(),null_state:'OBSERVED_ABSENT',coverage:'COMPLETE',evidence_refs:['scope:1'],closed_world_scope_ref:'scope:all-edges',observed_at:'2026-10-23T18:00:00Z'}).epistemic,'NON_RELATION'));
test('6 explicit disconnection must be sourced',()=>assert.throws(()=>qualifyNull({...base(),null_state:'EXPLICIT_DISCONNECTED'}),/UNSOURCED/));
test('7 intentionally private cannot be public',()=>assert.throws(()=>qualifyNull({...base(),null_state:'INTENTIONALLY_PRIVATE'}),/PRIVATE_CLASS/));
test('8 predicted non-edge needs horizon',()=>assert.throws(()=>qualifyNull({...base(),null_state:'PREDICTED_ONLY',forecast_ref:'x'}),/FORECAST/));
test('9 prediction stays typed predicted',()=>assert.equal(qualifyNull({...base(),null_state:'PREDICTED_ONLY',forecast_ref:'x',horizon_end:'2026-10-24T18:00:00Z'}).epistemic,'PREDICTED'));
test('10 CoNull cannot grant authority',()=>assert.throws(()=>qualifyNull({...base(),authority:'GLOBAL'}),/AUTHORITY/));
test('11 privacy qualification required',()=>assert.throws(()=>qualifyNull({...base(),privacy:'unspecified'}),/PRIVACY/));
test('12 public views suppress every private record',()=>{
 const r=publicNullProjection([base(),{...base(),id:'secret-path-SHOULD-NOT-LEAK',privacy:'PRIVATE',null_state:'INTENTIONALLY_PRIVATE'}]);
 assert.equal(r.non_edges.length,1); assert.equal(JSON.stringify(r).includes('secret-path'),false);
});
test('13 ambient view contains no private or public identifiers',()=>{
 const r=publicNullProjection([base()], 'AMBIENT'); assert.deepEqual(r.non_edges,[]); assert.equal(r.rendered_live_edges,0); assert.equal(r.receiver_ack,'UNPROVEN');
});
test('14 public projection modes preserve CoNull id sets',()=>{
 const rec=[base(),{...base(),id:'n2',null_state:'NOT_MATERIALIZED'}];
 const a=['MAP','ORB','TEXT'].map(mode=>publicNullProjection(rec,mode).non_edges.map(x=>x.id).join(','));assert.equal(new Set(a).size,1);
});
test('15 residual calculates observed minus expected',()=>{
 const r=numericResidual(measured());assert.equal(r.delta,2);assert.equal(r.normalized_to_tolerance,2);assert.equal(r.state,'MISMATCH');assert.equal(r.discovery_eligible,true);
});
test('16 equal values are not missing data',()=>assert.equal(numericResidual({...measured(),observed:10}).state,'WITHIN_TOLERANCE'));
test('17 missing observation is not a zero',()=>assert.equal(numericResidual({...measured(),observed:null}).state,'NOT_OBSERVED'));
test('18 numeric zero is a valid observation',()=>assert.equal(numericResidual({...measured(),observed:0}).delta,-10));
test('19 mismatched units block residual',()=>assert.equal(numericResidual({...measured(),observed_unit:'bytes'}).state,'INCOMPATIBLE_UNITS'));
test('20 wrong observation time cannot compare as same epoch',()=>assert.equal(numericResidual({...measured(),observation_valid_at:'2026-10-23T17:00:00Z'}).state,'TIME_OR_SOURCE_UNQUALIFIED'));
test('21 shared-source forecast is not independent evidence',()=>assert.equal(numericResidual({...measured(),observation_ref:'forecast:1'}).discovery_eligible,false));
test('22 private numeric data produce no delta output',()=>{const r=numericResidual({...measured(),privacy:'PRIVATE'});assert.equal(r.state,'WITHHELD');assert.equal('delta' in r,false)});
test('23 partial graph coverage retains unobserved forecasts as unresolved',()=>{const r=edgeResidual(edges());assert.deepEqual(r.confirmed,['A']);assert.deepEqual(r.unexpected,['C']);assert.deepEqual(r.unresolved_predictions,['B']);assert.deepEqual(r.disconfirmed,[]);});
test('24 complete graph coverage makes expected-but-missing disconfirmed',()=>{const r=edgeResidual({...edges(),coverage:'COMPLETE'});assert.deepEqual(r.disconfirmed,['B']);assert.deepEqual(r.unresolved_predictions,[])});
test('25 simulated edges are not admitted as observations',()=>assert.throws(()=>edgeResidual({...edges(),observed:[{id:'A',epistemic:'SIMULATED'}]}),/SIMULATED/));
test('26 predicted edges are required on expected side',()=>assert.throws(()=>edgeResidual({...edges(),expected:[{id:'A',epistemic:'OBSERVED'}]}),/EXPECTED/));
test('27 duplicate edge identity rejected',()=>assert.throws(()=>edgeResidual({...edges(),observed:[{id:'A',epistemic:'OBSERVED'},{id:'A',epistemic:'OBSERVED'}]}),/DUPLICATE/));
test('28 unknown source blocked',()=>assert.throws(()=>edgeResidual({...edges(),observation_ref:''}),/REFS/));
test('29 private edge sets are not exported',()=>assert.equal(edgeResidual({...edges(),privacy:'PRIVATE'}).state,'WITHHELD_OR_INVALID'));
test('30 zero budget materializes zero workers',()=>assert.equal(electNullSeat([{id:'A',privacy:'PUBLIC',authority:'READ_ONLY',testable:true,recovery:true,expected_info_gain:.9,estimated_cost:.2}],0).selected.length,0));
test('31 pick only marginally useful and admissible null seats',()=>{
 const r=electNullSeat([
 {id:'A',privacy:'PUBLIC',authority:'READ_ONLY',testable:true,recovery:true,expected_info_gain:.8,estimated_cost:.2},
 {id:'B',privacy:'PUBLIC',authority:'READ_ONLY',testable:true,recovery:true,expected_info_gain:.2,estimated_cost:.8},
 {id:'C',privacy:'PRIVATE',authority:'READ_ONLY',testable:true,recovery:true,expected_info_gain:1,estimated_cost:0},
 {id:'D',privacy:'PUBLIC',authority:'EXECUTE',testable:true,recovery:true,expected_info_gain:1,estimated_cost:0}],4);
 assert.deepEqual(r.selected.map(x=>x.id),['A']);assert.equal(r.materialized_workers,0);
});
test('32 deterministic tie breaks preserve same order',()=>{
 const a=['b','a'].map(id=>({id,privacy:'PUBLIC',authority:'READ_ONLY',testable:true,recovery:true,expected_info_gain:.7,estimated_cost:.2}));assert.deepEqual(electNullSeat(a,2).selected.map(x=>x.id),['a','b']);
});
test('33 rejection of unsafe/null or malformed candidate',()=>assert.throws(()=>electNullSeat([null]),/INVALID_CANDIDATE/));
test('34 no ever-growing work budget',()=>assert.throws(()=>electNullSeat([],1000000),/INVALID_BUDGET/));

test('35 received later still comparable if valid-time matches',()=>{const r=numericResidual(measured()); assert.equal(r.state,'MISMATCH');});
test('36 missing valid-time agreement on edges blocks negative assertions',()=>{const r=edgeResidual({...edges(),observation_valid_at:'2026-10-24T18:00:00Z'});assert.equal(r.state,'TIME_OR_SOURCE_UNQUALIFIED');});
test('37 closed-world graph cannot be asserted without scope receipt',()=>assert.throws(()=>edgeResidual({...edges(),coverage:'COMPLETE',coverage_evidence_ref:''}),/COVERAGE_EVIDENCE/));

test('38 graph discrepancy from same source does not earn discovery credit',()=>{
 const r=edgeResidual({...edges(),observation_ref:'forecast:1'});
 assert.equal(r.independently_sourced,false); assert.equal(r.discovery_eligible,false);
});
test('39 accidentally public-tagged source pointers are not projected',()=>{
 const r=publicNullProjection([{...base(),id:'C:\\Users\\Owner\\Secret',source_ref:'private@example.test',evidence_refs:['D:\\CoCivium\\Private'] }]);
 const raw=JSON.stringify(r);
 for(const secret of ['Secret','Owner','private@example','CoCivium','D:']) assert.equal(raw.includes(secret),false);
 assert.equal(r.non_edges[0].id,'null-1');assert.equal(r.non_edges[0].evidence_declared,true);
});
test('40 stable opaque public identities across three views',()=>{
 const arr=[base(),{...base(),id:'secret2'}];
 const proj=['MAP','ORB','TEXT'].map(x=>publicNullProjection(arr,x).non_edges.map(n=>n.id));
 assert.deepEqual(proj[0],['null-1','null-2']);assert.deepEqual(proj[0],proj[1]);assert.deepEqual(proj[1],proj[2]);
});
test('41 nonindependent numeric discrepancy is not promoted to discovery',()=>{
 const r=numericResidual({...measured(),independence_evidence:false});assert.equal(r.state,'MISMATCH');assert.equal(r.discovery_eligible,false);
});