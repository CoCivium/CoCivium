import assert from 'node:assert/strict';
import { generate, select, benchmark, OPERATORS } from './generator.mjs';

const a = generate({sourceId:'packet-A',seed:42,count:500});
const b = generate({sourceId:'packet-A',seed:42,count:500});
const c = generate({sourceId:'packet-A',seed:43,count:500});

assert.deepEqual(a,b,'same seed must replay exactly');
assert.notDeepEqual(a,c,'different seed should vary');
assert.ok(OPERATORS.length >= 12);
assert.ok(a.every(x => x.status === 'CANDIDATE' && x.authority === 'NONE' && x.executable === false));
assert.ok(new Set(a.map(x=>x.id)).size === a.length);

const selected = select(a,32);
assert.ok(selected.length <= 32);
assert.ok(selected.every(x => a.some(y => y.id === x.id)));

for (const op of ['NULL_BASELINE','NEGATE','COUNTERFACTUAL','OUTSIDE_VIEW']) {
  if (a.some(x=>x.operator===op)) assert.ok(selected.some(x=>x.operator===op));
}

assert.throws(()=>select(a,33));
assert.throws(()=>generate({count:1_000_001}));

const bench = benchmark({sourceId:'packet-A',seed:42,count:10000});
assert.equal(bench.receipt.external_effects,0);
assert.equal(bench.receipt.workers_spawned,0);
assert.equal(bench.receipt.authority,'NONE');
assert.ok(bench.receipt.generated > 0);
assert.ok(bench.receipt.elapsed_ms >= 0);

console.log(JSON.stringify({
  status:'PASS',
  tests:12,
  operators:OPERATORS.length,
  selected:selected.length,
  benchmark:bench.receipt,
  nonclaims:[
    'CANDIDATE_NE_EXECUTED',
    'MICROSECOND_TARGET_NE_MEASURED_UNTIL_RUN',
    'RANDOM_NE_AUTHORITY',
    'ADDRESSABLE_NE_ACTIVE'
  ]
},null,2));
