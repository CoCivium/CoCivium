// CoDiagramCommons / CoVisualAttractor R0 research selector.
// Read-only metadata scoring. Does not contact hosts, download images,
// infer licensing, publish derivatives, or communicate with recipients.
import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';

export const SCHEMA = 'CoDiagramCommons.CoVisualAttractorResearch.R0';
const MAX_INPUTS = 64;
const MAX_SELECTED = 3;
const nonclaims = Object.freeze([
  'SELECTED_NE_LICENSE_CLEARED',
  'DISCOVERED_NE_DOWNLOADED',
  'SEARCH_RANK_NE_REUSE_PERMISSION',
  'SCORE_NE_PROOF_OF_USEFULNESS',
  'FANOUT_NE_EXTERNAL_BROADCAST',
  'SCHEDULE_NE_RUNNING_DAEMON',
  'PRIVATE_PRIOR_NE_PUBLIC',
  'RESEARCH_ONLY_NE_PRODUCT'
]);
export function selectResearchFrontier(manifest, {cap=3}={}) {
  if(!manifest || manifest.schema !== SCHEMA || manifest.state !== 'PUBLIC_EXTERNAL_DISCOVERY_RESEARCH_CANDIDATES__NO_ASSET_INGESTION') throw Error('BAD_MANIFEST');
  if(manifest.privacy !== 'PUBLIC_METADATA_ONLY' || manifest.authority !== 'NONE') throw Error('PRIVACY_AUTHORITY_GATE');
  if(!Array.isArray(manifest.candidate_assets) || manifest.candidate_assets.length > MAX_INPUTS) throw Error('INPUT_LIMIT');
  if(!Number.isInteger(cap) || cap<1 || cap>MAX_SELECTED)throw Error('FRONTIER_CAP');
  const seen = new Set(), admitted = [], held = [];
  for (const c of manifest.candidate_assets) {
    if(!c || typeof c.id !== 'string' || !/^[a-z0-9-]{4,80}$/.test(c.id))throw Error('BAD_CANDIDATE_ID');
    if(typeof c.url !== 'string' || !c.url.startsWith('https://'))throw Error('NON_HTTPS_REFERENCE');
    const normalized = new URL(c.url).href;
    if(!['https:'].includes(new URL(normalized).protocol))throw Error('NON_HTTPS_REFERENCE');
    if(seen.has(normalized)){held.push({id:c.id,reason:'DUPLICATE_SOURCE_PAGE'});continue;}
    seen.add(normalized);
    if(!['PUBLIC_FILE_PAGE_READ','PUBLIC_PROJECT_PAGE_READ','PUBLIC_OBJECT_PAGE_READ','PUBLIC_API_DOC_READ','PUBLIC_GALLERY_READ','PUBLIC_ARTICLE_READ'].includes(c.source_retrieval_state)) {
      held.push({id:c.id,reason:'SOURCE_PAGE_UNQUALIFIED'});continue;
    }
    if(c.source_hash !== null){held.push({id:c.id,reason:'UNVERIFIED_IMAGE_DIGEST_SHOULD_BE_NULL'});continue;}
    const fields=['expected_value','novelty','cross_surface','verification_cost','license_friction'];
    if(fields.some(k => !Number.isInteger(c[k]) || c[k]<0 || c[k]>5))throw Error('BAD_RESEARCH_SCORING');
    if(typeof c.test!=='string' || c.test.length<12 || typeof c.hypothesis!=='string' || c.hypothesis.length<12) throw Error('MISSING_FALSIFIABLE_TEST');
    const rights=c.rights;
    if(typeof rights!=='string' || !rights) throw Error('MISSING_LICENSE_EVIDENCE');
    const notCleared = c.reuse_state === 'RESEARCH_REFERENCE_ONLY' || c.reuse_state === 'CATALOG_ONLY_NO_ASSET_COPY';
    const score = 4*c.expected_value + 2*c.novelty + 3*c.cross_surface - 2*c.verification_cost - 3*c.license_friction;
    admitted.push({
      id:c.id, source_url:normalized, media_type:c.media_type,
      score, hypothesis:c.hypothesis,test:c.test,
      rights_assertion: rights, reuse_state:c.reuse_state,
      rights_review_required:true, source_image_bytes_available:false,
      no_republication:true, source_sha256:null, status:notCleared?'RESEARCH_REFERENCE_ONLY':'RESEARCH_CANDIDATE_LICENSE_REVIEW'
    });
  }
  admitted.sort((a,b)=>b.score-a.score||a.id.localeCompare(b.id));
  const selected=admitted.slice(0,cap);
  const scoreBasis='ADVISORY_WEIGHTED_SUM_NO_EMPIRICAL_QUALITY_MEASUREMENT';
  return {
    schema:'CoVisualAttractor.ShadowResearchSelection.R0',state:'CANDIDATES_ONLY_NO_REUSE_AUTHORITY',
    input_count:manifest.candidate_assets.length,ranked_count:admitted.length,selected,
    deferred:admitted.slice(cap).map(x=>({id:x.id,score:x.score})),held,
    score_basis:scoreBasis,authority:'NONE',
    actual_rights_cleared_count:0,
    effects:{network_requests:0,downloads:0,outbound_messages:0,provider_model_calls:0,background_workers:0,public_media_published:0,receiver_ack:0},
    nonclaims:[...nonclaims]
  };
}
if(process.argv[1] && resolve(process.argv[1])===fileURLToPath(import.meta.url)) {
  try {
    const manifest=JSON.parse(readFileSync(new URL('./external_visual_research_r0.json',import.meta.url),'utf8'));
    process.stdout.write(JSON.stringify(selectResearchFrontier(manifest),null,2)+'\n');
  } catch(e) {
    process.stderr.write(JSON.stringify({state:'FAIL_CLOSED',reason:String(e.message||e)})+'\n');
    process.exitCode=1;
  }
}
