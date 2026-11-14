// CoMapCursor+ R0. No network, no model, no external effects.
export const seed = Object.freeze({
 schema:"CoMapCursor.Seed.R0", identity:"synthetic-comap-r0", version:"r0.1",
 coverage:"SEVEN_SYNTHETIC_NODES_ONLY", confidentiality:"PUBLIC_SYNTHETIC",
 nodes:[
  {id:"work",label:"Work",kind:"WORK",epistemic:"SIMULATED",x:50,y:48},
  {id:"source",label:"Source",kind:"EVIDENCE",epistemic:"SIMULATED",x:21,y:20},
  {id:"receiver",label:"Receiver",kind:"RECEIVER",epistemic:"SIMULATED",x:80,y:20},
  {id:"model",label:"Model",kind:"RESOURCE",epistemic:"CANDIDATE",x:21,y:76},
  {id:"recovery",label:"Recovery",kind:"RECOVERY",epistemic:"SIMULATED",x:80,y:76},
  {id:"future",label:"Future",kind:"FORECAST",epistemic:"PREDICTED",x:50,y:8},
  {id:"dissent",label:"Challenge",kind:"CHALLENGE",epistemic:"CANDIDATE",x:50,y:92}
 ],
 edges:[
  {id:"e1",from:"source",to:"work",type:"FEEDS",epistemic:"SIMULATED",at:1},
  {id:"e2",from:"work",to:"receiver",type:"ROUTES",epistemic:"SIMULATED",at:2},
  {id:"e3",from:"model",to:"work",type:"OPTION_FOR",epistemic:"CANDIDATE",at:3},
  {id:"e4",from:"recovery",to:"work",type:"RECOVERS",epistemic:"SIMULATED",at:4},
  {id:"e5",from:"dissent",to:"work",type:"CHALLENGES",epistemic:"CANDIDATE",at:5},
  {id:"e6",from:"work",to:"future",type:"FORECASTS",epistemic:"PREDICTED",at:6}
 ],
 metadata:{source_origin:"SYNTHETIC_FIXTURE",valid_at:"NOT_REAL_TIME",receiver_ack:"UNPROVEN",model_execution:"NONE"}
});
export const epistemic = Object.freeze(["OBSERVED","DERIVED","SIMULATED","INFERRED","CANDIDATE","PREDICTED","UNAVAILABLE"]);
export function validate(g=seed){
 const errors=[];
 if(g.schema!=="CoMapCursor.Seed.R0") errors.push("SCHEMA");
 if(g.confidentiality!=="PUBLIC_SYNTHETIC") errors.push("CONFIDENTIALITY");
 if(!Array.isArray(g.nodes)||!Array.isArray(g.edges)) return ["INVALID_ARRAYS"];
 const ids=new Set();
 for(const n of g.nodes){
  if(ids.has(n.id)) errors.push("DUPLICATE_NODE");
  ids.add(n.id);
  if(!epistemic.includes(n.epistemic)) errors.push("NODE_EPISTEMIC");
  if(!(Number.isFinite(n.x)&&n.x>=0&&n.x<=100&&Number.isFinite(n.y)&&n.y>=0&&n.y<=100)) errors.push("POSITION");
 }
 const edgeIds=new Set();
 for(const e of g.edges){
  if(edgeIds.has(e.id)) errors.push("DUPLICATE_EDGE");
  edgeIds.add(e.id);
  if(!ids.has(e.from)||!ids.has(e.to)) errors.push("ORPHAN_EDGE");
  if(!epistemic.includes(e.epistemic)) errors.push("EDGE_EPISTEMIC");
  if(!Number.isInteger(e.at)||e.at<0) errors.push("EDGE_TIME");
 }
 if(g.metadata?.receiver_ack!=="UNPROVEN") errors.push("FALSE_ACK");
 if(g.metadata?.model_execution!=="NONE") errors.push("FALSE_MODEL");
 return errors;
}
export function projection(g=seed,mode="map",cursor=6){
 if(validate(g).length) throw Error("INVALID_SOURCE");
 if(!["map","orb","trails","ambient"].includes(mode)) throw Error("BAD_MODE");
 if(!Number.isInteger(cursor)||cursor<0||cursor>6) throw Error("BAD_CURSOR");
 const links=g.edges.filter(e=>e.at<=cursor);
 return {mode,identity:g.identity,version:g.version,nodes:g.nodes,edges:links,
   censored_edges:g.edges.length-links.length,
   source_state:"SYNTHETIC_ONLY",receiver_ack:"UNPROVEN",model_execution:"NONE"};
}
const completions=[
 ["compare"," the source and receiver readproof before acknowledging pickup."],
 ["map"," the typed relations, provenance, uncertainty and recovery trails."],
 ["show"," the current evidence first, then offer forecasts separately."],
 ["review"," the counterevidence and preserve disagreement."]
];
export function ghost(text,cursor){
 if(typeof text!=="string"||!Number.isInteger(cursor)||cursor<0||cursor>text.length) throw Error("BAD_INPUT_CURSOR");
 const left=text.slice(0,cursor).toLowerCase().trimEnd();
 const match=completions.find(([prefix])=>left.endsWith(prefix));
 return match?match[1]:"";
}
export function acceptSuggestion(text,cursor,proposed,explicit){
 if(!explicit) throw Error("NO_EXPLICIT_ACCEPTANCE");
 if(proposed!==ghost(text,cursor)||!proposed) throw Error("STALE_OR_INVALID_PREDICTION");
 return {text:text.slice(0,cursor)+proposed+text.slice(cursor),cursor:cursor+proposed.length,
  effect:"LOCAL_TEXT_EDIT_ONLY",receiver_ack:"UNPROVEN"};
}
export function checkpoint(draft,view,cursor,history=[]){
 if(typeof draft!=="string"||draft.length>4000) throw Error("DRAFT_LIMIT");
 const p=projection(seed,view,cursor);
 return {schema:"CoMapCursor.Checkpoint.R0",source_id:p.identity,source_version:p.version,
  view,graph_cursor:cursor,draft,local_event_log:history.slice(-32),
  epistemic:"SYNTHETIC",receiver_ack:"UNPROVEN",provider_session:"NONE",submission:"NONE"};
}
export function restore(c){
 if(!c||c.schema!=="CoMapCursor.Checkpoint.R0"||c.source_id!==seed.identity||c.source_version!==seed.version ||
 c.receiver_ack!=="UNPROVEN"||c.provider_session!=="NONE"||c.submission!=="NONE"||
 !Array.isArray(c.local_event_log)||c.local_event_log.length>32) throw Error("INCOMPATIBLE_CHECKPOINT");
 return checkpoint(c.draft,c.view,c.graph_cursor,c.local_event_log);
}
