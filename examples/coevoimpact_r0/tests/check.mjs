import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {planImpact,SCHEMA,EDGE_WEIGHTS,NON_PROPAGATING} from '../CoEvoImpactR0.mjs';

const graph=JSON.parse(readFileSync(new URL('../fixture/graph.json',import.meta.url),'utf8'));
const event=JSON.parse(readFileSync(new URL('../fixture/event.json',import.meta.url),'utf8'));
const input=(extra={})=>({graph,event,...extra});
const altered=(change)=>{const g=structuredClone(graph);change(g);return g;};
const alteredEvent=(change)=>{const e=structuredClone(event);change(e);return e;};

test('01 deterministic finite output',()=>{
  const a=planImpact(input()),b=planImpact(input());
  assert.deepEqual(a,b);
});
test('02 schema and zero authority are explicit',()=>{
  const p=planImpact(input());
  assert.equal(p.schema,SCHEMA);
  assert.equal(p.authority,'NONE');
  assert.equal(p.effect_authority,'NONE');
  assert.equal(p.no_effects,true);
});
test('03 actual byte changes are not fabricated',()=>{
  const p=planImpact(input());
  assert.equal(p.change_evidence,'SYNTHETIC_FIXTURE_NOT_VERIFIED_SOURCE_BYTES');
  assert.match(p.evidence_scope,/NOT_OBSERVED_DEPENDENCIES/);
});
test('04 default candidate selection is small and expected',()=>{
  const p=planImpact(input());
  assert.equal(p.status,'PASS_SYNTHETIC_SHADOW_PLAN');
  assert.deepEqual(p.proposals.map(x=>x.dependent_id),['tests','challenge','contextamp','diagramcommons']);
  assert.equal(p.candidate_count,5);
});
test('05 directly affected proposals ask for review, not mutation',()=>{
  const p=planImpact(input());
  assert.ok(p.proposals.every(x=>x.depth===1&&x.impact_kind==='DIRECT_REVIEW_CANDIDATE'));
  assert.ok(p.proposals.every(x=>x.proposed_deed==='REVIEW_DEPENDENT_SOURCE_AND_RUN_EXISTING_CHECKS'));
});
test('06 second-order relationships remain hypothetical',()=>{
  const p=planImpact(input({max_proposals:8}));
  const x=p.proposals.find(x=>x.dependent_id==='second_order');
  assert.equal(x.depth,2);
  assert.equal(x.impact_kind,'DEFERRED_POSSIBLE_IF_PRIOR_ACTUALLY_CHANGES');
  assert.equal(x.proposed_deed,'WAIT_FOR_VERIFIED_INTERMEDIATE_CHANGE');
});
test('07 depth-one boundary eliminates second-order proposals',()=>{
  const p=planImpact(input({max_depth:1,max_proposals:8}));
  assert.ok(!p.proposals.some(x=>x.dependent_id==='second_order'));
  assert.equal(p.candidate_count,4);
});
test('08 three-depth search is capped and still shadow only',()=>{
  const p=planImpact(input({max_depth:3,max_proposals:16}));
  assert.ok(p.proposals.some(x=>x.dependent_id==='third_order'));
  assert.ok(p.diagnostics.cycle_deduped>=1);
  assert.equal(p.effects.worker_spawn,0);
});
test('09 private neighbor never appears by name or path',()=>{
  const p=planImpact(input({max_proposals:16}));
  assert.ok(p.diagnostics.held_privacy>=1);
  assert.ok(!JSON.stringify(p).includes('private_donor'));
});
test('10 unknown privacy is held and redacted',()=>{
  const p=planImpact(input({graph:altered(g=>g.nodes.find(x=>x.id==='private_donor').privacy='UNKNOWN')}));
  assert.ok(p.diagnostics.held_privacy>=1);
  assert.ok(!JSON.stringify(p).includes('private_donor'));
});
test('11 unsubscribed nodes never wake',()=>{
  const p=planImpact(input());
  assert.ok(p.diagnostics.held_unsubscribed>=1);
  assert.ok(!p.proposals.some(x=>x.dependent_id==='unsubscribed'));
});
test('12 stale relations never create selected proposals',()=>{
  const p=planImpact(input());
  assert.ok(p.diagnostics.held_stale>=1);
  assert.ok(!p.proposals.some(x=>x.dependent_id==='stale'));
});
test('13 authority approval is never inherited',()=>{
  const p=planImpact(input());
  assert.ok(p.diagnostics.held_authority>=1);
  assert.ok(!p.proposals.some(x=>x.dependent_id==='review_gate'));
});
test('14 unverified dependency is held instead of treated as fact',()=>{
  const p=planImpact(input());
  assert.ok(p.diagnostics.held_unverified>=1);
  assert.ok(!p.proposals.some(x=>x.dependent_id==='unverified'));
});
test('15 speculative similarity and inspiration never trigger waves',()=>{
  const p=planImpact(input());
  assert.ok(p.diagnostics.nonpropagating_relations>=2);
  assert.ok(NON_PROPAGATING.includes('MAY_INSPIRE'));
  assert.ok(!p.proposals.some(x=>x.dependent_id==='inspiration'));
});
test('16 priority is heuristic, not an authority escalation',()=>{
  const p=planImpact(input());
  assert.ok(EDGE_WEIGHTS.TESTS>EDGE_WEIGHTS.RENDERS);
  assert.deepEqual(p.proposals.map(x=>x.rank_heuristic),[100,90,80,70]);
  assert.ok(p.proposals.every(x=>x.auto_effects===0));
});
test('17 bounded proposal budget retains held count',()=>{
  const p=planImpact(input({max_proposals:1}));
  assert.equal(p.proposals.length,1);
  assert.equal(p.diagnostics.proposal_budget_held,4);
  assert.equal(p.candidate_count,5);
});
test('18 bounded visit budget never widens authority',()=>{
  const p=planImpact(input({max_visits:2}));
  assert.equal(p.proposals.length,1);
  assert.ok(p.diagnostics.visit_budget_held>0);
  assert.equal(p.authority,'NONE');
});
test('19 identical hashes are not treated as meaningful change',()=>{
  const p=planImpact(input({event:alteredEvent(e=>e.after_sha256=e.before_sha256)}));
  assert.equal(p.status,'HELD_NO_EXACT_DIGEST_CHANGE');
  assert.equal(p.proposals.length,0);
});
test('20 private source is rejected before neighbor traversal',()=>{
  const p=planImpact(input({graph:altered(g=>g.nodes.find(x=>x.id==='coomni').privacy='PRIVATE')}));
  assert.equal(p.status,'HELD_SOURCE_PRIVACY_OR_AUTHORITY');
  assert.equal(p.candidate_count,0);
  assert.ok(!JSON.stringify(p).includes('private_donor'));
});
test('21 source needing approval remains held',()=>{
  const p=planImpact(input({graph:altered(g=>g.nodes.find(x=>x.id==='coomni').authority='REQUIRES_APPROVAL')}));
  assert.equal(p.status,'HELD_SOURCE_PRIVACY_OR_AUTHORITY');
});
test('22 invalid evidence class fails closed',()=>{
  assert.throws(()=>planImpact(input({event:alteredEvent(e=>e.evidence_class='PROVEN') })),/HOLD_UNQUALIFIED_SOURCE_CHANGE/);
});
test('23 unknown source cannot be fabricated',()=>{
  assert.throws(()=>planImpact(input({event:alteredEvent(e=>e.changed_id='doesnotexist') })),/HOLD_MISSING_CHANGE_SOURCE/);
});
test('24 invalid or oversized budgets fail closed',()=>{
  assert.throws(()=>planImpact(input({max_depth:999})),/HOLD_UNBOUNDED_BUDGET/);
  assert.throws(()=>planImpact(input({max_proposals:1000000})),/HOLD_UNBOUNDED_BUDGET/);
  assert.throws(()=>planImpact(input({max_visits:0})),/HOLD_UNBOUNDED_BUDGET/);
});
test('25 duplicate node IDs are refused',()=>{
  assert.throws(()=>planImpact(input({graph:altered(g=>g.nodes.push({...g.nodes[0]}))})),/HOLD_INVALID_NODE/);
});
test('26 duplicate edge IDs are refused',()=>{
  assert.throws(()=>planImpact(input({graph:altered(g=>g.edges.push({...g.edges[0]}))})),/HOLD_DUPLICATE_RELATION/);
});
test('27 missing edge endpoints refuse phantom links',()=>{
  assert.throws(()=>planImpact(input({graph:altered(g=>g.edges[0].to='unknown_source')})),/HOLD_BAD_RELATION/);
});
test('28 dependent-to-prerequisite traversal is directional',()=>{
  const p=planImpact(input({event:alteredEvent(e=>e.changed_id='tests')}));
  assert.equal(p.status,'HELD_NO_QUALIFIED_DEPENDENTS');
  assert.equal(p.candidate_count,0);
});
test('29 unknown relation types are informational only',()=>{
  const p=planImpact(input({graph:altered(g=>g.edges.find(e=>e.from==='diagramcommons').kind='UNSPECIFIED')})); 
  assert.ok(!p.proposals.some(x=>x.dependent_id==='diagramcommons'));
  assert.ok(p.diagnostics.nonpropagating_relations>=3);
});
test('30 source provenance is proposal context, not receiver ACK',()=>{
  const p=planImpact(input());
  assert.ok(p.nonclaims.includes('NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF'));
  assert.ok(p.nonclaims.includes('MAY_EVOLVE_NE_AUTHORIZED_MUTATION'));
  assert.ok(p.proposals.every(x=>x.required_proof&&x.worker_count===0));
});
test('31 all potential external and self-mutating effects remain zero',()=>{
  const p=planImpact(input());
  assert.ok(Object.values(p.effects).every(x=>x===0));
  assert.equal(p.next.includes('Requalify source bytes'),true);
});
test('32 source with unknown currentness remains a HOLD',()=>{
  const p=planImpact(input({graph:altered(g=>g.nodes.find(x=>x.id==='tests').currentness='UNKNOWN')}));
  assert.ok(!p.proposals.some(x=>x.dependent_id==='tests'));
  assert.ok(p.diagnostics.held_stale>=2);
});

test('33 source with stale currentness blocks all review plans',()=>{
  const p=planImpact(input({graph:altered(g=>g.nodes.find(x=>x.id==='coomni').currentness='STALE')}));
  assert.equal(p.status,'HELD_SOURCE_CURRENTNESS_UNKNOWN_OR_STALE');
  assert.equal(p.proposals.length,0);
});
