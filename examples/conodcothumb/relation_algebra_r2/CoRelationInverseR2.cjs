'use strict';
// CoMiddle / CoPriMath R2: pure relation preview. No device or network I/O.
const crypto = require('node:crypto');
const SCHEMA = 'CoCivium.CoMiddle.RelationInverse.R2';
const PAIRS = [
  ['DEPENDS_ON','IS_DEPENDENCY_OF','DEPENDENCY'],
  ['DERIVES_FROM','IS_SOURCE_FOR','PROVENANCE'],
  ['HAS_EVIDENCE','EVIDENCE_FOR','EVIDENCE'],
  ['HAS_MEMBER','MEMBER_OF','MEMBERSHIP'],
  ['CONTAINS','CONTAINED_BY','SCOPE'],
  ['PRECEDES','FOLLOWS','TEMPORAL'],
  ['SUPERSEDES','SUPERSEDED_BY','TEMPORAL'],
  ['ROUTES_TO','IS_ROUTE_TARGET_OF','RECEIVER'],
  ['HAS_TEST','TESTS','EVIDENCE'],
  ['CHALLENGES','CHALLENGED_BY','CHALLENGE'],
  ['GREATER_THAN','LESS_THAN','MEASUREMENT'],
  ['CAUSED_BY','CAUSES','CAUSAL'],
  ['CITES','CITED_BY','PROVENANCE'],
  ['PROPOSES_TO','IS_PROPOSED_RECIPIENT_OF','RECEIVER'],
  ['REPLACES','REPLACED_BY','TEMPORAL'],
  ['NEEDS_APPROVAL_FROM','IS_APPROVAL_REQUIRED_FOR','AUTHORITY']
];
const SYMMETRIC = [
  ['RELATED_TO','RELATIONAL'],
  ['CONNECTED_WITH','RELATIONAL'],
  ['DIFFERENT_FROM','COMPARISON'],
  ['CONTRADICTS','CHALLENGE']
];
const EVIDENCE_GATES = Object.freeze({
  CAUSAL:'Causal claim requires intervention/control or adequate external evidence',
  MEASUREMENT:'Numeric comparison requires shared units, scale, observation and uncertainty',
  RECEIVER:'Route or recipient candidate is not delivery, consent or ACK',
  AUTHORITY:'Relationship labels never establish executable permission',
  EVIDENCE:'Evidence links do not make the conclusion true',
  CHALLENGE:'Disagreement or contradiction requires same proposition, scope and time',
  TEMPORAL:'Observe valid-time and historical version; later never erases prior',
  PROVENANCE:'Source or citation identity must be independently checked',
  DEPENDENCY:'Dependency direction is not substitutability',
  MEMBERSHIP:'Membership requires qualified collection and object scope',
  SCOPE:'Scope is not ownership or permission',
  RELATIONAL:'Related does not imply causation or endorsement',
  COMPARISON:'Difference is not contradiction'
});
const relationMap = new Map();
for (const [a,b,family] of PAIRS) {
  if (relationMap.has(a) || relationMap.has(b) || a === b) throw Error('DUPLICATE_RELATION');
  relationMap.set(a, Object.freeze({id:a,converse:b,family,kind:'DIRECTIONAL'}));
  relationMap.set(b, Object.freeze({id:b,converse:a,family,kind:'DIRECTIONAL'}));
}
for (const [id,family] of SYMMETRIC) {
  if (relationMap.has(id)) throw Error('DUPLICATE_RELATION');
  relationMap.set(id,Object.freeze({id,converse:id,family,kind:'SYMMETRIC'}));
}
const TRANSFORMS = Object.freeze(['CONVERSE','NEGATE','ELSE','NULL','OUTSIDE','COUNTERFACTUAL','UNKNOWN']);
const CONTEXTS = Object.freeze(['MAP','ORB','FILE','MEDIA','CODE','WRITING','RESEARCH','QUESTION','DEVICE','FLEET','OUTREACH','DESIGN','CULTURE']);
const QUESTIONS = Object.freeze(['WHO','WHAT','WHY','HOW','WHEN','WHERE','WHEREFORE','WHICH','WHAT_IF','WHY_NOT','NOT_ELSE','HOW_MUCH','HOW_KNOW','WHAT_NEXT','AT_RECEIVER','WHAT_ELSE','WHAT_NOT']);
const SURFACES = Object.freeze(['TEXT','GLYPH','COMAP','COORB','RICH_MEDIA','SPEC','CODE','ACCESSIBLE']);
const GLYPHS = Object.freeze({CONVERSE:'↔',NEGATE:'¬',ELSE:'±',NULL:'∅',OUTSIDE:'⊃',COUNTERFACTUAL:'◇',UNKNOWN:'?'});
const ZERO_EFFECTS = Object.freeze({device:0,network:0,send:0,clipboard:0,worker:0});
function eligible(req) {
  if (!req || typeof req !== 'object' || Array.isArray(req)) return 'HELD_INVALID_REQUEST';
  if (req.gesture === 'NATIVE_MIDDLE') return 'PASS_THROUGH_NATIVE';
  if (!['PUBLIC','PRIVATE_LOCAL'].includes(req.privacy)) return 'HELD_PRIVACY_UNCLASSIFIED';
  if (!['EXPLICIT_RING','KEYBOARD_FALLBACK'].includes(req.gesture)) return 'HELD_UNBOUND_GESTURE';
  if (!CONTEXTS.includes(req.context)) return 'HELD_CONTEXT_UNKNOWN';
  if (!/^sha256:[0-9a-f]{64}$/.test(req.source_ref || '')) return 'HELD_UNVERIFIED_SOURCE_POINTER';
  if (req.authority !== 'NONE') return 'HELD_UNAUTHORIZED_EFFECT';
  return 'ELIGIBLE';
}
function preview(req) {
  const state=eligible(req);
  const base={schema:SCHEMA,status:state,authority:'NONE',effects:{...ZERO_EFFECTS},receiver_ack:false,
    glyph:null,relation_id:null,proposed_relation_id:null,transformation:null,review_gate:null,context:'REDACTED',source_ref:null,
    message:'No effect or claim of proof',nonclaims:['PREVIEW_NE_EXECUTION','CONVERSE_NE_CAUSALITY','NEGATION_NE_FALSEHOOD','SUMMON_NE_AUTHORITY']};
  if (state !== 'ELIGIBLE') return base;
  const record=relationMap.get(req.relation_id);
  if (!record) return {...base,status:'HELD_UNTYPED_RELATION'};
  if (!TRANSFORMS.includes(req.transform)) return {...base,status:'HELD_UNSUPPORTED_TRANSFORM'};
  const transform=req.transform;
  const id=(transform==='CONVERSE')?record.converse:null;
  const gate=EVIDENCE_GATES[record.family];
  const summary={CONVERSE:'formal relational converse (direction swap), not logical negation',NEGATE:'candidate NOT relation; truth not evaluated',
    ELSE:'candidate alternative; not equivalent',NULL:'no-change baseline; no proof of absence',OUTSIDE:'candidate outside view; scope not automatically complete',
    COUNTERFACTUAL:'hypothetical changed premise, not an observation',UNKNOWN:'unknown state; not false'}[transform];
  return {...base,status:'SHADOW_PROPOSAL',context:req.context,source_ref:req.privacy==='PUBLIC'?req.source_ref:null,relation_id:record.id,
    proposed_relation_id:id,transformation:transform,glyph:GLYPHS[transform],relation_kind:record.kind,
    relation_family:record.family,review_gate:gate,
    message:summary,version:'R2',source_ref_state:req.privacy==='PUBLIC'?'DECLARED_POINTER_ONLY_NOT_BYTE_VERIFIED':'PRIVATE_POINTER_REDACTED',user_action_required:true};
}
function decodeAddress(index) {
  const total=BigInt(relationMap.size)*BigInt(TRANSFORMS.length)*BigInt(CONTEXTS.length)*BigInt(QUESTIONS.length)*BigInt(SURFACES.length);
  if(typeof index!=='bigint' || index<0n || index>=total) throw Error('ADDRESS_OUT_OF_RANGE');
  const axes=[[...relationMap.keys()],TRANSFORMS,CONTEXTS,QUESTIONS,SURFACES];let remainder=index;
  const decoded=[];
  for(const axis of axes){const base=BigInt(axis.length);decoded.push(axis[Number(remainder%base)]);remainder/=base;}
  return Object.freeze({relation_id:decoded[0],transform:decoded[1],context:decoded[2],question:decoded[3],surface:decoded[4],logical_address:index.toString()});
}
function addressCount() {return (BigInt(relationMap.size)*BigInt(TRANSFORMS.length)*BigInt(CONTEXTS.length)*BigInt(QUESTIONS.length)*BigInt(SURFACES.length)).toString();}
function sampleAddresses(seed,limit=7) {
  if(typeof seed!=='string'||seed.length>512||!Number.isInteger(limit)||limit<1||limit>32) throw Error('BAD_SAMPLE_REQUEST');
  const total=BigInt(addressCount());const picked=new Set();const out=[];
  for(let i=0;out.length<limit&&i<limit*5;i++){
    const hash=crypto.createHash('sha256').update(seed+'|'+i).digest('hex');
    const id=BigInt('0x'+hash)%total;
    if(!picked.has(id.toString())){picked.add(id.toString());out.push(decodeAddress(id));}
  }
  if(out.length!==limit)throw Error('UNEXPECTED_SAMPLE_COLLISION');return out;
}
function schemaSummary(){return {schema:SCHEMA,relation_count:relationMap.size,directional_pairs:PAIRS.length,symmetric:SYMMETRIC.length,
  contexts:CONTEXTS.length,questions:QUESTIONS.length,surfaces:SURFACES.length,transforms:TRANSFORMS.length,
  logical_addresses:addressCount(),zero_effects:{...ZERO_EFFECTS},authority:'NONE',source:'typed simulation not OS binding'};}
module.exports={SCHEMA,PAIRS,SYMMETRIC,TRANSFORMS,CONTEXTS,QUESTIONS,SURFACES,GLYPHS,EVIDENCE_GATES,ZERO_EFFECTS,relationMap,eligible,preview,decodeAddress,addressCount,sampleAddresses,schemaSummary};
if(require.main===module){console.log(JSON.stringify({summary:schemaSummary(),example:preview({privacy:'PUBLIC',gesture:'EXPLICIT_RING',context:'MAP',source_ref:'sha256:'+'0'.repeat(64),authority:'NONE',relation_id:'DEPENDS_ON',transform:'CONVERSE'}),sample:sampleAddresses('CoAll-r2',4)},null,2));}