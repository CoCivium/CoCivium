import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';
import { checkManifest } from './verify.mjs';

const root=path.dirname(fileURLToPath(import.meta.url));
const original=JSON.parse(fs.readFileSync(path.join(root,'manifest.json'),'utf8'));
const captions=fs.readFileSync(path.join(root,'CAPTIONS_DRAFT.vtt'),'utf8');
const copied=()=>structuredClone(original);
const rejects=(name,mutation,expected)=>{
  test(name,()=>{const m=copied();mutation(m);assert.ok(checkManifest(m,captions).includes(expected),expected);});
};

test('baseline candidate passes narrowly',()=>assert.deepEqual(checkManifest(original,captions),[]));
rejects('cannot declare filmed media on storyboard evidence',m=>m.media.kind='VIDEO_RENDERED','MEDIA_NOT_RENDERED');
rejects('cannot claim public release',m=>m.release_gates.public_release='PASS','NO_PREMATURE_PROMOTION');
rejects('no false user feedback pass',m=>m.release_gates.independent_viewer='PASS','NO_PREMATURE_PROMOTION');
rejects('new donation link fails closed',m=>m.offer.payment_url='https://not-verified.invalid','NO_UNVERIFIED_DONATIONS');
rejects('tax-receipt promise fails closed',m=>m.offer.tax_receipt_claim=true,'NO_UNVERIFIED_DONATIONS');
rejects('partner endorsement inference fails closed',m=>m.offer.named_partners=['unverified charity'],'NO_PARTNER_ENDORSEMENT');
rejects('public auto-publish fails closed',m=>m.evolution.automatic_publication=true,'NO_AUTO_PUBLIC_EFFECTS');
rejects('auto-email fails closed',m=>m.evolution.automatic_email=true,'NO_AUTO_PUBLIC_EFFECTS');
rejects('thousand unsolicited recipients fails closed',m=>m.academic_outreach.mass_1000_sending=true,'NO_BULK_MAIL');
rejects('missing proof reference fails closed',m=>m.media.scene_order[0].claim_refs=['unknown'],'SCENE_PROVENANCE');
rejects('unbounded timing changes fail',m=>m.media.scene_order[0].duration_s=5,'SUM_TIMES');
rejects('privacy guard cannot disappear',m=>m.community.prohibited=[],'PRIVACY_GUARD');
rejects('non-verified metaphysics not claimed',m=>m.nonclaims=[],'SYMBOLIC_BOUNDARY');
test('caption tampering fails closed',()=>assert.ok(checkManifest(copied(),captions.replace('Preview first. Nothing is typed automatically.','Never reject suggestions.')).includes('VTT_CAPTION_1')));
test('caption clock drift fails closed',()=>assert.ok(checkManifest(copied(),captions.replace('00:00:04.000 -->','00:00:03.000 -->')).includes('VTT_START_1')));
test('source URL cannot silently leave project',()=>{const m=copied();m.sources[0].url='https://random.invalid/tracker';assert.ok(checkManifest(m,captions).includes('SOURCE_BOUND'));});
test('captionless render is not declared safe',()=>{const m=copied();m.media.scene_order[2].caption='';assert.ok(checkManifest(m,captions).includes('SCENE_PROVENANCE'));});
