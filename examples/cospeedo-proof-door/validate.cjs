"use strict";
const assert=require("node:assert/strict");
function qualify(b){
  assert.equal(b.schema,"CoCivium.CoSpeedo.PublicProofDoor.R0");
  assert.equal(b.observation_scope,"PUBLIC_GITHUB_DEFAULT_BRANCH_READBACK_SNAPSHOT");
  assert.match(b.identity,/^CoCivium\.EvoAll\./);
  assert.equal(typeof b.observed_date_utc,"string");
  assert.equal(b.source_refs.length,6);
  assert.equal(new Set(b.source_refs.map(s=>s.path)).size,b.source_refs.length);
  for(const s of b.source_refs){
    assert.match(s.path,/^(EVERGREEN\.md|ai\/[a-z0-9_.\/\-]+|docs\/[A-Za-z0-9_.\/\-]+|assets\/[A-Za-z0-9_.\/\-]+)$/);
    assert.match(s.blob_sha1_at_observation,/^[a-f0-9]{40}$/);
    assert.equal(s.readback,"GITHUB_DEFAULT_BRANCH");
    assert.equal(s.link,"https://github.com/CoCivium/CoCivium/blob/main/"+s.path);
  }
  assert.ok(b.frontier.length>=3);
  b.frontier.forEach(f=>assert.ok(Number.isInteger(f.source_index)&&f.source_index>=0&&f.source_index<b.source_refs.length));
  assert.ok(b.gates.some(x=>x.name.includes("Current X2")&&x.status==="HELD"));
  assert.ok(b.gates.some(x=>x.name.includes("Primary")&&x.status==="HELD"));
  assert.ok(b.gates.some(x=>x.name.includes("middle/thumb")&&x.status==="HELD"));
  for(const g of b.gates)assert.ok(["PASS","HELD","CANDIDATE","FAIL"].includes(g.status));
  assert.equal(b.scaling.actual_workers,0);
  assert.equal(b.scaling.background_processes,0);
  assert.equal(b.scaling.external_messages_sent,0);
  assert.equal(b.privacy.scope,"PUBLIC_ONLY");
  assert.equal(b.privacy.private_screenshot_content_included,false);
  assert.equal(b.privacy.credential_material_included,false);
  assert.equal(b.privacy.external_effect_authority,"NONE");
  assert.deepEqual(Object.values(b.receiver_state),[false,false,false,false,false]);
  const raw=JSON.stringify(b);
  assert.ok(!/[A-Z]:\\|@gmail\.com|ANTHROPIC_API_KEY\s*[:=]/i.test(raw));
  assert.ok(b.next_safe_action.includes("exact CoSpeedo source object"));
  return true;
}
module.exports={qualify};
