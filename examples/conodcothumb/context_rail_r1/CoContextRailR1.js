/* CoContextRail+ R1. Pure candidate selector, NO device/clipboard/network interaction. */
(function(root,factory){
  const api=factory();
  if(typeof module==='object'&&module.exports) module.exports=api;
  else root.CoContextRailR1=api;
})(typeof globalThis!=='undefined'?globalThis:this,function(){
  'use strict';
  const SCHEMA='CoAll.CoContextRail.R1';
  const NO_EFFECTS=Object.freeze({device:0,network:0,send:0,clipboard:0,model:0,workers:0});
  // Only declared synthetic/UI fields are eligible for a source-labelled preview.
  const PACKET_FIELDS=new Set(['context','question','relation','lens','time','surface','privacy',
    'gesture','mode','object_kind','user_selected','source_ref','external_effect_requested']);
  const contextual={
    FILE:['INSPECT_IDENTITY','COPY_REFERENCE','CHECK_PRIORS','TRACE_RECOVERY','EXPLORE_RELATIONS'],
    MEDIA:['INSPECT_IDENTITY','PROPOSE_MEDIA_CAPSULE','CHECK_RIGHTS','FIND_PRIORS','CHECK_ALTERNATIVE'],
    WRITING:['CHECK_PRIORS','DRAFT_ALTERNATIVE','ASK_FALSIFIER','COMPARE_RENDER','REVIEW_RECOVERY'],
    CODE:['CHECK_PRIORS','PROPOSE_STATIC_TEST','ASK_FALSIFIER','TRACE_RECOVERY','CHECK_ALTERNATIVE'],
    MAP:['EXAMINE_INVERSE','INSPECT_EVIDENCE','MAP_UNKNOWN','COMPARE_RENDER','SHOW_LINEAGE'],
    ORB:['INSPECT_EVIDENCE','COMPARE_RENDER','MAP_UNKNOWN','TRACE_RECOVERY','SHOW_LINEAGE'],
    RESEARCH:['ASK_FALSIFIER','CHECK_PRIORS','SEPARATE_HYPOTHESIS','CHECK_ALTERNATIVE','COMPARE_TIMES'],
    QUESTION:['REPHRASE_QUESTION','CHECK_PRIORS','ASK_FALSIFIER','LOCATE_SOURCE','CHECK_ALTERNATIVE'],
    DEVICE:['READ_ONLY_HEALTH','TRACE_RECOVERY','INSPECT_CURRENTNESS','CHECK_ALTERNATIVE'],
    FLEET:['READ_ONLY_HEALTH','TRACE_RECOVERY','INSPECT_CURRENTNESS','CHECK_COST','ASK_FALSIFIER'],
    OUTREACH:['PREPARE_UNSENT_DRAFT','CHECK_AUTHORITY','CHECK_PRIORS','REVIEW_PRIVACY'],
    DESIGN:['COMPARE_RENDER','CHECK_PRIORS','ASK_FALSIFIER','CHECK_ACCESSIBILITY'],
    CULTURE:['SEPARATE_HYPOTHESIS','CHECK_PRIORS','ASK_FALSIFIER','COMPARE_RENDER','LOCATE_SOURCE']
  };
  const details={
    INSPECT_IDENTITY:['◎','Inspect exact selected-object identity','Source hash, currentness and scope. No file access in this simulator.'],
    COPY_REFERENCE:['◇','Propose a CoCopy reference','A pointer is not payload, paste, send or receiver acknowledgment.'],
    PROPOSE_MEDIA_CAPSULE:['◇','Preview a rich-media capsule','Metadata/rights/format lane only; no actual media copied or decoded.'],
    CHECK_PRIORS:['↔','Find competing priors','Compare existing work and alternatives; no automatic search or trust promotion.'],
    TRACE_RECOVERY:['⟳','Inspect recovery path','Keep source and rollback; no restore or installation executed.'],
    EXPLORE_RELATIONS:['⊂','Explore typed source relations','Inclusion and adjacency do not grant authority.'],
    CHECK_RIGHTS:['?','Check permissions and rights','No rights claim without a specific verified source.'],
    FIND_PRIORS:['↔','Compare similar media/examples','Content similarity is not endorsement or independent evidence.'],
    CHECK_ALTERNATIVE:['◇','Propose an alternative','A counterproposal is not a better result until tested.'],
    DRAFT_ALTERNATIVE:['◇','Propose another phrasing','No reading other apps and no automatic typing.'],
    ASK_FALSIFIER:['¬','Ask what could falsify it','An inverse or negation is a test proposal, not proof of falsity.'],
    COMPARE_RENDER:['↔','Compare accessible projections','Same source identity across text, CoMap, CoOrb and media.'],
    REVIEW_RECOVERY:['⟳','Review prior state and undo','No history rewriting; no automatic restore.'],
    PROPOSE_STATIC_TEST:['✓','Propose a reproducible test','Test design only; no arbitrary code is run.'],
    EXAMINE_INVERSE:['↔','Explore inverse/reverse relation','Reverse relation need not imply reverse causation.'],
    INSPECT_EVIDENCE:['?','Open provenance and unknowns','A beautiful visualization cannot replace source truth.'],
    MAP_UNKNOWN:['?','Distinguish UNKNOWN and ABSENT','Absence requires bounded, dated complete observation.'],
    SHOW_LINEAGE:['Δ','Inspect change and predecessor','Track what changed without silently overwriting earlier evidence.'],
    SEPARATE_HYPOTHESIS:['◇','Separate story from empirical claim','Civ2+/ET/G_d are scenarios or hypotheses unless independently evidenced.'],
    COMPARE_TIMES:['Δ','Compare prior, observed and future time','A future story is not a forecast or schedule.'],
    REPHRASE_QUESTION:['?','Form a precise reusable question','The question is a source-bound object; no answer is presumed.'],
    LOCATE_SOURCE:['◎','Locate an attributable source','No network lookup in this canary.'],
    READ_ONLY_HEALTH:['⟳','Propose a local health check','No machine or device inspected by this source.'],
    INSPECT_CURRENTNESS:['Δ','Review freshness and lease','A running process is not proof of correct or visible service.'],
    CHECK_COST:['>','Compare work against cost and time','Define units; optimize verified utility rather than worker counts.'],
    PREPARE_UNSENT_DRAFT:['@','Prepare recipient-specific draft','No recipient selected, no send authority, no automated outreach.'],
    CHECK_AUTHORITY:['⊗','Check sender and receiver authority','The gesture is not permission to deliver.'],
    REVIEW_PRIVACY:['⊗','Check private/bystander exposure','Consent and privacy are higher priority than convenience.'],
    CHECK_ACCESSIBILITY:['⊂','Check text/keyboard/contrast alternatives','Color and glyph alone are not sufficient.'],
    WHAT_IF:['◇','Create a falsifiable what-if','Counterfactual is not observation.'],
    WHEREFORE:['?','Ask purpose and human consequences','Meaning or ethics frame; not a physics fact.'],
    WHO_ROLE:['@','Check role and consent','A role is not an identified human or permission grant.'],
    WHEN_TIME:['Δ','Inspect time and expiry','Past, observed, future and valid-time remain distinct.'],
    WHERE_SCOPE:['⊂','Inspect scope and location claims','No precise-location collection or inference.'],
    WHAT_NOT:['¬','Inspect missing and opposite cases','UNKNOWN is not FALSE; NOT_ALL is not NONE.'],
    NOT_ELSE:['∅','Test the NotElse/null baseline','An empty scoped domain does not prove universal absence.'],
    WHAT_ELSE:['⊕','Generate alternative branches','A branch is not executed; CoTurtle review still applies.'],
    WHICH_COMPARE:['≠','Compare multiple qualified options','No automatic winner or endorsement.'],
    HOW_MUCH:['>','Ask measurement and budget','State unit, reference and observation window.'],
    HOW_KNOW:['?','Ask evidence and falsifiers','Independent data before certainty.'],
    WHAT_NEXT:['→','Preview one next safe step','No effect without separate authority.'],
    WHAT_GENERAL:['◎','Clarify the selected object','Unknown scope remains HELD.']
  };
  const questionActions={WHAT:'WHAT_GENERAL',WHY:'CHECK_PRIORS',HOW:'PROPOSE_STATIC_TEST',WHEN:'WHEN_TIME',WHERE:'WHERE_SCOPE',WHO:'WHO_ROLE',WHEREFORE:'WHEREFORE',WHICH:'WHICH_COMPARE',WHAT_IF:'WHAT_IF',WHY_NOT:'ASK_FALSIFIER',WHAT_NOT:'WHAT_NOT',WHAT_ELSE:'WHAT_ELSE',NOT_ELSE:'NOT_ELSE',HOW_MUCH:'HOW_MUCH',HOW_KNOW:'HOW_KNOW',WHAT_NEXT:'WHAT_NEXT',AT_RECEIVER:'CHECK_AUTHORITY'};
  function cleanEnum(value,values,fallback){return typeof value==='string'&&values.includes(value)?value:fallback;}
  function lexicalScore(action,p){
    let v=10;
    if(action===questionActions[p.question])v+=20;
    if(p.relation==='INVERSE'&&action==='EXAMINE_INVERSE')v+=18;
    if(p.relation==='FALSIFIER'&&action==='ASK_FALSIFIER')v+=18;
    if(p.relation==='NULL_BASELINE'&&action==='NOT_ELSE')v+=18;
    if(p.relation==='RECOVERY'&&action==='TRACE_RECOVERY')v+=18;
    if(p.surface==='ACCESSIBLE'&&action==='CHECK_ACCESSIBILITY')v+=8;
    if(p.lens==='G_D_HYPOTHESIS'||p.lens==='ET_HYPOTHESIS') if(action==='SEPARATE_HYPOTHESIS'||action==='ASK_FALSIFIER')v+=30;
    return v;
  }
  function decide(packet,manifest){
    if(!manifest||manifest.schema!==SCHEMA||!packet||typeof packet!=='object'||Array.isArray(packet))throw Error('INVALID_CONTRACT');
    const base={schema:SCHEMA,work_id:manifest.work_id,authority:'NONE',receiver_ack:false,effects:{...NO_EFFECTS},
      context: 'REDACTED',question:'REDACTED',privacy:'REDACTED',state:'HELD',source_ref:null,suggestions:[],
      nonclaims:['PREVIEW_NE_EXECUTION','GESTURE_NE_AUTHORITY','PROJECTION_NE_RECEIVER_PICKUP']};
    // Fail closed before scope or identity hints are projected. Unknown metadata may
    // include raw input or future effect-intent fields from an unqualified adapter.
    // Reject inherited state, hidden/symbol keys and getter/setter descriptors.
    // Inspect descriptors before reading any field: no accessor is invoked.
    const proto=Object.getPrototypeOf(packet);
    const keys=Reflect.ownKeys(packet);
    if((proto!==Object.prototype && proto!==null) ||
       keys.some(k=>typeof k!=='string' || !PACKET_FIELDS.has(k) ||
         !Object.hasOwn(Object.getOwnPropertyDescriptor(packet,k),'value')))
      return {...base,state:'HELD_UNDECLARED_INPUT',explanation:'Unqualified context fields withheld. No input captured.'};
    if(Object.hasOwn(packet,'external_effect_requested') && packet.external_effect_requested!==false)
      return {...base,state:'HELD_EFFECT_REQUEST',explanation:'Preview does not authorize device, network, send or paste effects.'};
    const privacy=cleanEnum(packet.privacy,['PUBLIC','PRIVATE_LOCAL','SENSITIVE','UNKNOWN'],'UNKNOWN');
    const g=cleanEnum(packet.gesture,['NATIVE_MIDDLE','EXPLICIT_RING','KEYBOARD_FALLBACK','UNBOUND'],'UNBOUND');
    if(privacy==='SENSITIVE'||privacy==='UNKNOWN')return {...base,state:'HELD_PRIVACY',explanation:'Sensitive or unclassified context. No capture or metadata disclosed.'};
    if(g==='NATIVE_MIDDLE')return {...base,state:'PASS_THROUGH_NATIVE',explanation:'Native middle-click is unchanged. No preview or device action.'};
    if(g!=='EXPLICIT_RING'&&g!=='KEYBOARD_FALLBACK')return {...base,state:'HELD_UNBOUND_GESTURE',explanation:'No eligible preview gesture elected.'};
    const context=cleanEnum(packet.context,manifest.contexts,'UNKNOWN');
    if(context==='SENSITIVE'||context==='UNKNOWN')return {...base,state:'HELD_UNKNOWN_CONTEXT',explanation:'Select a nonsensitive context explicitly; no OS inspection performed.'};
    const question=cleanEnum(packet.question,manifest.questions,'WHAT');
    const relation=cleanEnum(packet.relation,manifest.relations,'SOURCE');
    const lens=cleanEnum(packet.lens,manifest.lenses,'PRACTICAL');
    const surface=cleanEnum(packet.surface,manifest.surfaces,'TEXT');
    const time=cleanEnum(packet.time,manifest.times,'PRESENT');
    const p={context,question,relation,lens,surface,time};
    // A source hash in synthetic tests is a declared pointer, not a verified observation.
    const source=typeof packet.source_ref==='string'&&/^sha256:[0-9a-f]{64}$/.test(packet.source_ref)?packet.source_ref:null;
    const objectKinds=['FILE','MEDIA','RELATION','CLAIM','QUESTION','DEVICE'];
    const kind=cleanEnum(packet.object_kind,objectKinds,'QUESTION');
    const selected=packet.user_selected===true;
    let actions=[...contextual[context]];
    if(questionActions[question]&&question!=='WHAT')actions.unshift(questionActions[question]);
    if(lens==='G_D_HYPOTHESIS'||lens==='ET_HYPOTHESIS') actions.unshift('SEPARATE_HYPOTHESIS','ASK_FALSIFIER');
    if(relation==='INVERSE')actions.unshift('EXAMINE_INVERSE');
    if(relation==='NULL_BASELINE')actions.unshift('NOT_ELSE');
    if(surface==='ACCESSIBLE')actions.unshift('CHECK_ACCESSIBILITY');
    actions=[...new Set(actions)];
    const lackingSelection=['FILE','MEDIA'].includes(context)&&(!selected||!source);
    if(lackingSelection)actions=['WHAT_GENERAL','CHECK_PRIORS'];
    if(kind==='DEVICE'&&context!=='DEVICE'&&context!=='FLEET')actions=['READ_ONLY_HEALTH','CHECK_AUTHORITY'];
    if(context==='OUTREACH')actions=actions.filter(x=>x!=='PROPOSE_MEDIA_CAPSULE');
    const max=Math.min(Math.max(manifest.max_visible_suggestions|0,0),7);
    const mode=packet.mode==='MORE'?'MORE':'GLANCE';
    const ranked=actions.map((id,index)=>({id,score:lexicalScore(id,p),index})).sort((a,b)=>b.score-a.score||a.index-b.index);
    const head=ranked.slice(0,mode==='MORE'?max:Math.min(1,max)).map(x=>({id:x.id,glyph:details[x.id][0],title:details[x.id][1],explanation:details[x.id][2],status:'PROPOSED_ONLY',allowed_to_execute:false,effects:{...NO_EFFECTS}}));
    return {...base,context,question,privacy,lens,time,relation,surface,object_kind:kind,source_ref:privacy==='PUBLIC'?source:null,
      selected_object_proof:source?'USER_DECLARED_HASH_NOT_VERIFIED':'NONE',
      state:'PROPOSED_ONLY',explanation:lackingSelection?'Explicit file/media selection and exact source hash needed before meaningful preview.':'Shadow-only. Select one safe action; no effect adapter installed.',
      suggestions:head,remaining_hidden_count:Math.max(0,ranked.length-head.length),
      observed_device_event:false,physical_binding:'NOT_INSTALLED'};
  }
  // Mixed-radix addresses are descriptive possibilities, NOT eligible/active work.
  function logicalSize(manifest){
    return ['contexts','questions','relations','lenses','times','surfaces'].reduce((p,k)=>p*BigInt(manifest[k].length),1n).toString();
  }
  function sampleAddresses(manifest,seed,limit){
    if(!Number.isInteger(limit)||limit<0||limit>64)throw Error('BOUND_LIMIT_0_64');
    if(typeof seed!=='string'||seed.length>256)throw Error('INVALID_SEED');
    const total=BigInt(logicalSize(manifest));
    let state=2166136261>>>0;
    for(let i=0;i<seed.length;i++){state^=seed.charCodeAt(i);state=Math.imul(state,16777619)>>>0;}
    let stride=BigInt((state|1)>>>0); while(gcd(stride,total)!==1n)stride+=2n;
    const start=BigInt(state)%total;const out=[];
    for(let i=0;i<limit;i++)out.push(((start+BigInt(i)*stride)%total).toString());
    return out;
  }
  function gcd(a,b){while(b!==0n){const r=a%b;a=b;b=r;}return a;}
  function decode(manifest,index){
    const axes=['contexts','questions','relations','lenses','times','surfaces'];const names=['context','question','relation','lens','time','surface'];
    let n=BigInt(index);const max=BigInt(logicalSize(manifest));if(n<0n||n>=max)throw Error('OUT_OF_LOGICAL_RANGE');
    const row={};for(let i=axes.length-1;i>=0;i--){const items=manifest[axes[i]];row[names[i]]=items[Number(n%BigInt(items.length))];n/=BigInt(items.length);}
    return row;
  }
  return Object.freeze({SCHEMA,NO_EFFECTS,decide,logicalSize,sampleAddresses,decode});
});
