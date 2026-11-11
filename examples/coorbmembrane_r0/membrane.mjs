// CoOrbMembrane+ R0: projection-only, no IO, no actions, no implied receiver acceptance.
export const permittedStates = new Set(["VERIFIED", "STALE", "FORECAST", "CONTRADICTED", "HELD", "UNKNOWN"]);
const esc = s => String(s).replaceAll("&","&amp;").replaceAll("<","&lt;").replaceAll(">","&gt;").replaceAll('"',"&quot;").replaceAll("'","&#39;");
function validISO(v){return typeof v==="string" && !Number.isNaN(Date.parse(v)) && /Z$/.test(v);}
export function validate(record) {
  if(!record || typeof record!=="object" || Array.isArray(record)) throw Error("record required");
  // R0 can only display public synthetic fixtures. No live receiver trust boundary.
  if(record.proof_scope!=="SYNTHETIC_FIXTURE_ONLY") throw Error("synthetic proof scope required");
  for(const k of ["work_id","work_version","seed_sha","observed_at","policy_version"]) if(!record[k]) throw Error("missing "+k);
  if(!validISO(record.observed_at)) throw Error("observed_at must be UTC ISO");
  if(!/^[a-f0-9]{64}$/.test(record.seed_sha)) throw Error("seed_sha must be SHA256 hex");
  if(!Array.isArray(record.edges) || !record.edges.length || record.edges.length>24) throw Error("edges required and capped at 24");
  const ids=new Set();
  for(const e of record.edges){
    if(!e || typeof e!=="object" || Array.isArray(e)) throw Error("edge object required");
    for(const k of ["edge_id","target","status","source_sha","observed_at"]) if(!e[k]) throw Error("missing edge."+k);
    if(e.privacy_class!=="PUBLIC") throw Error("private or unqualified edge must not be projected");
    if(!/^[a-f0-9]{64}$/.test(e.source_sha)) throw Error("edge source SHA256 invalid");
    if(ids.has(e.edge_id)) throw Error("duplicate edge id");
    ids.add(e.edge_id);
    if(!permittedStates.has(e.status)) throw Error("invalid status");
    if(!validISO(e.observed_at)) throw Error("edge observed_at invalid");
    if(e.status==="VERIFIED" && (!e.receiver_readproof || !e.authorized)) throw Error("false verified edge");
    if(e.status==="FORECAST" && (!e.horizon || !e.falsifier || !e.baseline_ref || typeof e.confidence!=="number" || !Number.isFinite(e.confidence) || e.confidence<0 || e.confidence>1)) throw Error("forecast missing horizon/confidence/falsifier/baseline");
  }
  return record;
}
export function project(record, asOf=record.observed_at) {
  validate(record);
  if(!validISO(asOf)) throw Error("asOf must be UTC ISO");
  const edges=record.edges.map(e=>{
    const expired=!!e.valid_to && Date.parse(asOf)>Date.parse(e.valid_to);
    const status=e.status==="VERIFIED" && expired?"STALE":e.status;
    return {id:e.edge_id,target:e.target,status,source_sha:e.source_sha,observed_at:e.observed_at,
      receiver_readproof:status==="VERIFIED"?e.receiver_readproof:null,
      horizon:status==="FORECAST"?e.horizon:null,confidence:status==="FORECAST"?e.confidence:null};
  });
  return {work_id:record.work_id,work_version:record.work_version,seed_sha:record.seed_sha,
    policy_version:record.policy_version,as_of:asOf,proof_scope:"SYNTHETIC_FIXTURE_ONLY",
    receiver_ack:"NOT_OBSERVED",edges};
}
export function toText(p){
  return ["PUBLIC SYNTHETIC PROJECTION ONLY | NO LIVE RECEIVER ACK",
    p.work_id+" | version "+p.work_version+" | as of "+p.as_of,
    "Seed SHA256 "+p.seed_sha,"Policy "+p.policy_version,
    ...p.edges.map(e=>e.id+": "+e.target+" | "+e.status+
      (e.status==="FORECAST"?" | horizon "+e.horizon+" | p="+e.confidence:""))].join("\n");
}
export function toSVG(p) {
  const palette={VERIFIED:"#2cba91",STALE:"#c88c52",FORECAST:"#8d82f7",CONTRADICTED:"#ef6a78",HELD:"#e1ad57",UNKNOWN:"#8992a4"};
  const text=toText(p);
  const n=p.edges.length;
  const rays=p.edges.map((e,i)=>{
    const a=(i/n)*2*Math.PI-Math.PI/2, x1=300+95*Math.cos(a),y1=225+95*Math.sin(a),
      x2=300+165*Math.cos(a),y2=225+165*Math.sin(a),c=palette[e.status];
    const dash=e.status==="FORECAST"?'stroke-dasharray="4 7"':e.status==="UNKNOWN"?'stroke-dasharray="2 8"':"";
    return '<line x1="'+x1.toFixed(2)+'" y1="'+y1.toFixed(2)+'" x2="'+x2.toFixed(2)+'" y2="'+y2.toFixed(2)+'" stroke="'+c+'" stroke-width="3" '+dash+'/>'+
    '<circle cx="'+x2.toFixed(2)+'" cy="'+y2.toFixed(2)+'" r="7" fill="'+c+'"/>'+
    '<text x="'+(300+194*Math.cos(a)).toFixed(2)+'" y="'+(230+194*Math.sin(a)).toFixed(2)+'" fill="#e3e8f7" text-anchor="middle" font-size="12">'+esc(e.id)+': '+esc(e.status)+'</text>';
  }).join("\n");
  return '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 600 475" role="img" aria-labelledby="orbtitle orbdesc">'+
  '<title id="orbtitle">CoOrb membrane '+esc(p.work_id)+' version '+esc(p.work_version)+'</title>'+
  '<desc id="orbdesc">'+esc(text)+'</desc>'+
  '<rect width="600" height="475" fill="#091426"/>'+
  '<circle cx="300" cy="225" r="99" fill="#181c3b" stroke="#7c66d8" stroke-width="2"/>'+
  '<circle cx="300" cy="225" r="78" fill="#192849" opacity=".8"/>'+
  rays+
  '<text x="300" y="212" text-anchor="middle" fill="#fafaff" font-size="17">'+esc(p.work_id)+'</text>'+
  '<text x="300" y="240" text-anchor="middle" fill="#bcb5fa" font-size="13">v'+esc(p.work_version)+'</text>'+
  '<text x="300" y="265" text-anchor="middle" fill="#d3daf0" font-size="10">'+esc(p.as_of)+'</text>'+
  '<text x="300" y="293" text-anchor="middle" fill="#e2b77b" font-size="11">SYNTHETIC ONLY - NO LIVE ACK</text>'+
  '</svg>';
}
