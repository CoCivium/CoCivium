import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.dirname(fileURLToPath(import.meta.url));
const TIME = /^([0-9]{2}):([0-9]{2}):([0-9]{2})\.([0-9]{3})$/;
const seconds = (s) => {
  const m = s.match(TIME);
  if (!m) return NaN;
  return Number(m[1])*3600+Number(m[2])*60+Number(m[3])+Number(m[4])/1000;
};

export function checkManifest(m, rawVtt) {
  const errors = [];
  const must = (ok,id) => {if (!ok) errors.push(id);};
  must(m?.schema === 'CoCivium.LivingPublication.Pilot.R0', 'SCHEMA');
  must(m?.status === 'SOURCE_AND_STORYBOARD_CANDIDATE_ONLY', 'RELEASE_STATUS');
  must(m?.media?.kind === 'STORYBOARD_ONLY_NO_VIDEO_RENDER', 'MEDIA_NOT_RENDERED');
  must(m?.media?.length_seconds === 40, 'DURATION');
  must(m?.media?.target_width === 1080 && m?.media?.target_height === 1920, 'ASPECT');
  const scenes = m?.media?.scene_order ?? [];
  must(scenes.length === 6, 'SCENE_COUNT');
  must(new Set(scenes.map(s=>s.id)).size === scenes.length, 'SCENE_IDS');
  must(scenes.every(s=>Number.isInteger(s.duration_s) && s.duration_s>0), 'SCENE_TIMES');
  must(scenes.reduce((t,s)=>t+(s.duration_s||0),0) === m?.media?.length_seconds,'SUM_TIMES');
  const sources = m?.sources??[];
  must(sources.length >= 3 && sources.every(s=>s?.url?.startsWith('https://github.com/CoCivium/')),'SOURCE_BOUND');
  must(scenes.every(s=>s.caption?.trim() && s.narration?.trim() && s.proof_label?.trim()
    && (s.claim_refs??[]).every(ref=>sources.some(q=>q.id===ref))), 'SCENE_PROVENANCE');
  must(m?.offer?.price === 'FREE_TO_READ_AND_TRY' && m?.offer?.paid_tier === false, 'FREE_TO_USE');
  must(m?.offer?.donations_enabled === false && m?.offer?.payment_url === null
    && m?.offer?.tax_receipt_claim === false, 'NO_UNVERIFIED_DONATIONS');
  must(m?.offer?.named_partners?.length === 0 && m?.offer?.partner_endorsements_proven === false,
    'NO_PARTNER_ENDORSEMENT');
  must(m?.evolution?.automatic_publication === false && m?.evolution?.automatic_email === false
    && m?.evolution?.automatic_partner_payments === false, 'NO_AUTO_PUBLIC_EFFECTS');
  must(m?.academic_outreach?.new_recipients_sent === 0 && m?.academic_outreach?.mass_1000_sending === false,
    'NO_BULK_MAIL');
  must(m?.release_gates?.public_release === 'HELD' && m?.release_gates?.actual_media_encode === 'NOT_RUN'
    && m?.release_gates?.independent_viewer === 'HELD', 'NO_PREMATURE_PROMOTION');
  must(m?.nonclaims?.includes('METAPHOR_G_D_NE_EVIDENCED_CAUSATION'), 'SYMBOLIC_BOUNDARY');
  must(m?.community?.prohibited?.includes('PRIVATE_KEYS'), 'PRIVACY_GUARD');
  const cues = [];
  if (!rawVtt.startsWith('WEBVTT')) errors.push('VTT_HEADER');
  const pattern = /(\d{2}:\d{2}:\d{2}\.\d{3}) --> (\d{2}:\d{2}:\d{2}\.\d{3})\r?\n([^\r\n]+)/g;
  let x;
  while ((x=pattern.exec(rawVtt))) cues.push({start:seconds(x[1]),end:seconds(x[2]),caption:x[3]});
  must(cues.length === scenes.length, 'VTT_CUES');
  let time = 0;
  for (let i=0;i<scenes.length;i++){
    const c=cues[i],s=scenes[i]; if(!c || !s) break;
    must(Math.abs(c.start-time)<0.0001,'VTT_START_'+i);
    time+=s.duration_s;
    must(Math.abs(c.end-time)<0.0001,'VTT_END_'+i);
    must(c.caption===s.caption,'VTT_CAPTION_'+i);
  }
  return errors;
}

if(process.argv[1] && path.resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  const manifest=JSON.parse(fs.readFileSync(path.join(ROOT,'manifest.json'),'utf8'));
  const captions=fs.readFileSync(path.join(ROOT,'CAPTIONS_DRAFT.vtt'),'utf8');
  const failures=checkManifest(manifest,captions);
  process.stdout.write(JSON.stringify({scope:'STORYBOARD_SOURCE_ONLY',checked_at:new Date().toISOString(),
    validation:failures.length?'FAIL':'PASS',failures,claims:'NO_FILM_NO_DONATIONS_NO_BULK_EMAIL'})+'\n');
  process.exitCode=failures.length?1:0;
}
