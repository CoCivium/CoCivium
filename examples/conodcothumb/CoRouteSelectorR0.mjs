// CoPayload route and budget election: deterministic advisory only.
// Selection is not consent to capture, install, send, or execute anything.
export const SCHEMA='CoPayload.RouteSelector.ShadowR0';
export const INLINE_LIMIT=8192;
export const R0_LIMIT=512*1024**2;
export const R1_DEFAULT_LIMIT=16*1024**3;
export const R1_HARD_LIMIT=64*1024**3;
export function chooseRoute({byte_count,explicit_extended=false,sensitive=false,consent_scope=null}={}) {
 const base={schema:SCHEMA,mode:'ADVISORY_ONLY',external_actions:0,authorized_external_receivers:[],
   opt_in_required_for_stage:true,consent_scope:consent_scope??'NONE',
   nonclaims:['SUGGESTION_NE_PERMISSION','LARGE_PAYLOAD_NE_UNLIMITED_CONTEXT','POINTER_NE_BYTES']};
 if(sensitive) return {...base,status:'HOLD_PRIVACY',lane:null,reason:'Sensitive context is blocked by default'};
 if(!Number.isSafeInteger(byte_count)||byte_count<0) return {...base,status:'HOLD_INVALID_SIZE',lane:null};
 if(byte_count<=INLINE_LIMIT) return {...base,status:'PROPOSED',lane:'SMALL_INLINE',max_bytes:INLINE_LIMIT};
 if(byte_count<=R0_LIMIT) return {...base,status:'PROPOSED',lane:'EXPLICIT_FILE_BACKED_R0',max_bytes:R0_LIMIT};
 if(byte_count<=R1_DEFAULT_LIMIT) return {...base,status:'PROPOSED',lane:'EXPLICIT_CHUNKED_R1',max_bytes:R1_DEFAULT_LIMIT};
 if(explicit_extended && byte_count<=R1_HARD_LIMIT) return {...base,status:'PROPOSED',lane:'EXTENDED_CHUNKED_R1',max_bytes:R1_HARD_LIMIT,
   requires_extra_disk_time_budget:true};
 return {...base,status:'HOLD_RESOURCE_BUDGET',lane:null,reason:'No bounded local transfer can be assumed safe'};
}
