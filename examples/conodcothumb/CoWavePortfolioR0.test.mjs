import test from 'node:test';
import assert from 'node:assert/strict';
import {electWave} from './CoWavePortfolioR0.mjs';

const candidate=(id,front,extra={})=>({id,front,state:'ELIGIBLE',benefit:6,cost:1,authorized:true,urgentRepair:false,...extra});
test('new eligible front beats repeated equal-value front',()=>{
 const x=electWave([candidate('repeat','orb'),candidate('new','media')],['orb'],{max:1});
 assert.equal(x.selected[0].id,'new');
 assert.equal(x.worker_count,0);
 assert.equal(x.effect,'ADVISORY_ONLY');
});
test('urgent verified repair can repeat a front',()=>{
 const x=electWave([candidate('repair','orb',{urgentRepair:true}),candidate('fresh','media')],['orb'],{max:1});
 assert.equal(x.selected[0].id,'repair');
 assert.equal(x.selected[0].reason,'URGENT_REPAIR');
});
test('blocked, dormant, and unauthorized proposals never win',()=>{
 const x=electWave([candidate('blocked','x2',{state:'BLOCKED',benefit:10}),
 candidate('sleep','theory',{state:'DORMANT',benefit:10}),
 candidate('forbidden','email',{authorized:false,benefit:10})],[],{max:2});
 assert.deepEqual(x.selected,[]);
 assert.equal(x.eligible_count,0);
});
test('higher value may intentionally repeat, no forced novelty',()=>{
 const x=electWave([candidate('critical','orb',{benefit:10,cost:0}),
 candidate('novel','media',{benefit:2,cost:2})],['orb'],{max:1});
 assert.equal(x.selected[0].id,'critical');
 assert.equal(x.selected[0].reason,'BENEFIT_OUTWEIGHS_NOVELTY');
});
test('exactly same wave inputs give stable selection with tie break',()=>{
 const a=[candidate('zeta','z'),candidate('alpha','a')];
 assert.deepEqual(electWave(a,[],{max:2}),electWave(a.slice().reverse(),[],{max:2}));
});
test('reject duplicate ID and unbounded or malformed proposals',()=>{
 for(const items of [[candidate('one','x'),candidate('one','y')],[candidate('unsafe','x',{benefit:Infinity})]]) {
   assert.throws(()=>electWave(items,[]),/INVALID_CANDIDATE/);
 }
 assert.throws(()=>electWave([],[],{max:999}),/INVALID_WAVE_INPUT/);
 assert.throws(()=>electWave([],['private secret with spaces']),/INVALID_HISTORY/);
});
test('repeating identical action produces no effect or fake receiver ack',()=>{
 const result=electWave([candidate('a','orb')],['orb']);
 assert.equal(result.receiver_ack,false);
 assert.equal(result.worker_count,0);
 assert.equal(result.nonclaims.includes('SELECTED_NE_EXECUTED'),true);
});
