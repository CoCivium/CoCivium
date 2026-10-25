import { test } from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, lstatSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';
import { resolve, relative, isAbsolute, sep } from 'node:path';

const repo = fileURLToPath(new URL('../../../', import.meta.url));
const here = fileURLToPath(new URL('../', import.meta.url));
const manifest = JSON.parse(readFileSync(resolve(here, 'registry.json'), 'utf8'));
const flow = readFileSync(resolve(here, 'FLOW.mmd'), 'utf8');
const readme = readFileSync(resolve(here, 'README.md'), 'utf8');
const ids = new Set(manifest.donors.map(d => d.id));
const classes = ['VISUAL_CODE','SVG_BRAND','SEMANTIC_MANIFEST','ARCHITECTURE_NOTE','GENERATOR_GUIDE'];
function gitBlobSha(data) {
  return createHash('sha1').update(Buffer.from('blob ' + data.length + '\0')).update(data).digest('hex');
}

test('schema and candidate maturity never assert canon or runtime', () => {
  assert.equal(manifest.schema, 'CoDiagramCommons.PublicDonorRegistry.R0');
  assert.equal(manifest.version, 'R0');
  assert.equal(manifest.authority, 'NONE');
  assert.match(manifest.state, /NOT_ALL_PRIORS_RECONCILED/);
});
test('bounded source coverage has seven visual and three nonvisual donors', () => {
  assert.equal(manifest.donors.length, 10);
  assert.equal(manifest.donors.filter(d => ['VISUAL_CODE','SVG_BRAND'].includes(d.asset_class)).length, 7);
  assert.equal(ids.size, manifest.donors.length);
  assert.match(manifest.scope, /Neither all prior sessions nor private images/);
});
for (const d of manifest.donors) {
  test('exact public source identity: ' + d.id, () => {
    assert.match(d.git_blob_sha1, /^[0-9a-f]{40}$/);
    assert.ok(classes.includes(d.asset_class), d.asset_class);
    assert.equal(d.origin, 'CoCivium/CoCivium@main');
    assert.equal(d.verified_scope, 'PUBLIC_GITHUB_SOURCE_BLOB_READBACK');
    assert.equal(d.render_quality, 'NOT_VERIFIED_BY_THIS_REGISTRY');
    assert.equal(d.adopted_runtime, false);
    assert.equal(d.inspiration_permission, 'SOURCE_ONLY_REUSE_CONDITIONAL_ON_LICENSE_AND_ATTRIBUTION');
    assert.ok(Array.isArray(d.axes) && d.axes.length > 0);
    assert.ok(!d.path.startsWith('/') && !d.path.includes('\\') && !d.path.split('/').includes('..'));
    const target = resolve(repo,d.path);
    const rel = relative(repo,target);
    assert.ok(rel && !rel.startsWith('..'+sep) && !isAbsolute(rel));
    assert.ok(lstatSync(target).isFile());
    const bytes = readFileSync(target);
    assert.equal(gitBlobSha(bytes), d.git_blob_sha1);
  });
}
test('candidate links are typed, resolvable, and not alleged causal proof', () => {
  assert.equal(manifest.candidate_edges.length,9);
  const edgeIds = new Set();
  for (const e of manifest.candidate_edges) {
    assert.ok(ids.has(e.from) && ids.has(e.to));
    assert.notEqual(e.from,e.to);
    assert.equal(e.causal_claim,false);
    assert.equal(e.authority,'NONE');
    assert.equal(e.converse_not_causal_reversal,true);
    assert.match(e.relation_type,/^[A-Z_]+$/);
    const key=e.from+'|'+e.relation_type+'|'+e.to;
    assert.ok(!edgeIds.has(key));
    edgeIds.add(key);
  }
});
test('difference and falsifier lanes not lost to positive inspiration only', () => {
  const a=new Set(manifest.variation_operators);
  for(const k of ['NULL_BASELINE','INVERT_EDGE_DIRECTION_AS_HYPOTHESIS','COUNTERFACTUAL','OUTSIDE_VIEW','ACCESSIBILITY_TWIN','CHALLENGE_WITH_FALSIFIER','REPLAY_HISTORICAL_FAILURE'])
    assert.ok(a.has(k),k);
  assert.ok(manifest.candidate_edges.some(e=>e.relation_type.includes('NEGATIVE')));
  assert.ok(manifest.candidate_edges.some(e=>e.relation_type.includes('FALSIFIER')));
});
test('future mediums remain discoverable but are not asserted present', () => {
  for(const k of ['SVG','PNG','Mermaid','PDF_PAGE','VIDEO_FRAME','SKETCH','TEXT_DIAGRAM'])
    assert.ok(manifest.future_intake.accepted_mediums.includes(k),k);
  assert.equal(manifest.future_intake.unlocated_history_policy,'DISCOVERABLE_CANDIDATE__NOT_RECOVERED');
});
test('rights/privacy guardrails prevent universal public derivatives', () => {
  assert.match(manifest.future_intake.private_policy,/PRIVATE_HOLD/);
  assert.match(manifest.future_intake.rights_policy,/RIGHTS_AND_ATTRIBUTION_REVIEW/);
  assert.ok(manifest.future_intake.required_fields.includes('privacy'));
  assert.ok(manifest.future_intake.required_fields.includes('loss_ledger'));
});
test('zero external effects, no inferred always-on operation', () => {
  assert.equal(manifest.outputs.external_effects,0);
  assert.equal(manifest.outputs.live_workers_spawned,0);
  assert.equal(manifest.outputs.expected_proposal_mode,'SHADOW');
  assert.ok(manifest.outputs.process.includes('sleep'));
});
test('projection and semantic stability acceptance requirements are explicit',()=>{
  for(const k of ['source_retrieval_sha_match','semantic_id_stability','same_source_multiple_projections','projection_loss_visible','tested_renderer_quality','independent_receiver_task_usefulness','cold_recovery_source_readproof'])
    assert.ok(manifest.acceptance_gates.includes(k),k);
});
test('epistemic boundaries include inference and private-history caveats',()=>{
  for(const k of ['DIAGRAM_NE_EVIDENCE','SOURCE_GIT_BLOB_NE_VISUAL_QA','CONVERSE_NE_CAUSAL_REVERSE','VIVID_NE_TRUE','PRIVATE_PRIOR_NE_PUBLIC','INFINITY_NE_UNBOUNDED_COMPUTE','DAILY_CAPABLE_NE_DAILY_CHURN'])
    assert.ok(manifest.epistemic_rails.includes(k),k);
});
test('editable diagram represents challenge, held path and recurrence',()=>{
  assert.ok(flow.startsWith('flowchart TD'));
  for(const k of ['Tests, contradiction and visual review','FAIL / HELD','PASS scope only','Wake only for significant delta'])
    assert.ok(flow.includes(k),k);
});
test('human README links source and disclaims exhaustive prior inventory',()=>{
  assert.match(readme,/Only ten public GitHub source objects are actually indexed/);
  assert.match(readme,/not a full inventory/i);
  assert.ok(readme.includes('G_D_HYPOTHESIS_NE_MEASURED_FIELD'));
});
test('CoLens semantic source is not conflated with visual render',()=>{
  const visual=manifest.donors.find(x=>x.id==='colens_map_orb_text');
  const source=manifest.donors.find(x=>x.id==='colens_typed_manifest');
  assert.equal(visual.asset_class,'VISUAL_CODE');
  assert.equal(source.asset_class,'SEMANTIC_MANIFEST');
  assert.ok(manifest.candidate_edges.some(x=>x.from===source.id&&x.to===visual.id));
});
