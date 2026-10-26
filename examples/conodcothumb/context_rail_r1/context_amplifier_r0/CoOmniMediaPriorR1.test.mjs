/*
 * CoOrbWare OmniMedia R1 CONTRACT TEST ONLY.
 * This test reads one checked-in PUBLIC taxonomy JSON. It never inspects
 * private media or performs network/provider/device actions.
 */
import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const manifest=new URL('../../../../docs/Evolution/COORBWARE_OMNIMEDIA_PRIOR_CONTRACT_R1_20261025.json',import.meta.url);
const m=JSON.parse(readFileSync(manifest,'utf8'));
const families=m.media_families;
const relations=m.transfer_relations;
const fields=new Set(m.prior_record_fields);
const ids=arr=>arr.map(x=>x.id);
const requiredIds=['diagram','illustration','photograph','screenshot','video','animation',
  'audio','music','speech','interactive_ui','three_d_mesh','spatial_xr','simulation',
  'sensor_time_series','scientific_image','dataset','source_code_renderer',
  'text_typography','composite_media','physical_artifact'];

test('explicit candidate taxonomy state',()=>{
  assert.equal(m.format,'CoAll.CoOrbWare.OmniMediaPriorTaxonomy.R1');
  assert.match(m.status,/DESIGN_CANDIDATE_ONLY/);
});
test('never claims all session media scanned',()=>assert.match(m.status,/NO_ALL_SESSION_SCAN/));
test('never claims historical source bytes',()=>assert.match(m.status,/NO_HISTORICAL_BYTES_CLAIM/));
test('not a live device runtime',()=>assert.match(m.status,/NO_RUNTIME/));
test('20 explicit media families',()=>assert.equal(families.length,20));
test('exactly one record for every elected media family',()=>assert.deepEqual(new Set(ids(families)),new Set(requiredIds)));
test('all media families declare an inspiration affordance',()=>assert.ok(families.every(x=>typeof x.transferable_prior==='string'&&x.transferable_prior.length>0)));
test('all media families declare a human-accessible twin',()=>assert.ok(families.every(x=>typeof x.minimum_accessible_twin==='string'&&x.minimum_accessible_twin.length>0)));
test('18 typed relations rather than arbitrary synonymous edges',()=>assert.equal(relations.length,18));
test('relation identities unique',()=>assert.equal(new Set(ids(relations)).size,relations.length));
test('dissimilarity relation present',()=>assert.ok(ids(relations).includes('contrasts_with')));
test('inverse not conflated with negation',()=>assert.ok(ids(relations).includes('inverts_view_of')&&ids(relations).includes('negates_hypothesis_of')));
test('complement requires scoped meaning',()=>assert.ok(relations.find(x=>x.id==='complements_scope_of').semantics.includes('universe')));
test('source identity and provenance fields retained',()=>{
  for(const v of ['source_locator','source_repo_ref_or_custodian','source_sha256_if_computed','source_time','lineage']) assert.ok(fields.has(v),v);
});
test('timecode, coordinate and track fields retained',()=>{
  assert.ok(fields.has('track_or_segment_id'));
  assert.ok(fields.has('timecode_or_coordinate_frame'));
});
test('creator, rights and consent retained',()=>{
  for(const v of ['creator','license_or_rights','consent','purpose']) assert.ok(fields.has(v),v);
});
test('privacy and epistemic classifications explicit',()=>{
  assert.ok(fields.has('privacy')&&fields.has('evidence_class'));
  assert.ok(m.privacy_classes.includes('PRIVATE')&&m.epistemic_classes.includes('HYPOTHESIS'));
});
test('unlike and negative cases retained',()=>{
  assert.ok(fields.has('unlike_relations')&&fields.has('negative_findings')&&fields.has('inverse_kind'));
});
test('derivative information-loss report required',()=>assert.ok(fields.has('transform_loss')));
test('receiver acknowledgement never implied',()=>assert.ok(fields.has('receiver_ack')&&m.nonclaims.includes('POINTER_NE_ACK')));
test('not automatically ingesting or publishing',()=>{
  assert.equal(m.privacy_rules.automatic_ingestion,false);
  assert.equal(m.privacy_rules.automatic_publication,false);
  assert.equal(m.privacy_rules.implicit_authority_from_prior,false);
});
test('public projection suppresses restricted/private items',()=>assert.match(m.privacy_rules.public_projection,/suppress/i));
test('source does not equal transcript inferred from filename',()=>assert.match(m.privacy_rules.derived_content,/actually inspected/i));
test('derived works do not silently transfer rights',()=>assert.match(m.privacy_rules.author_identity,/consent/));
test('six cross-modal scenarios marked hypothetical',()=>{
  assert.equal(m.media_transfer_examples.length,6);
  assert.ok(m.media_transfer_examples.every(x=>x.state==='HYPOTHESIS_ONLY'));
});
test('real receiver test remains a requirement',()=>assert.ok(m.test_gates.some(s=>/receiver/i.test(s))));
test('unbounded possibility not unlimited compute',()=>assert.ok(m.nonclaims.includes('POTENTIAL_INFINITY_NE_PHYSICAL_INFINITY')));
