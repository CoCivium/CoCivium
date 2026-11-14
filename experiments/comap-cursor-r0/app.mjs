import {seed,validate,projection,ghost,acceptSuggestion,checkpoint} from "./core.mjs";
const $=id=>document.getElementById(id);
if(validate(seed).length) throw Error("Synthetic fixture failed validation");
const ns="http://www.w3.org/2000/svg";
let view="map",cursor=6,draft="",caret=0,history=[],selected="work";
const viewNames=["map","orb","trails","ambient"];
const svg=(tag,attrs={})=>{
 const e=document.createElementNS(ns,tag);
 for(const [k,v] of Object.entries(attrs)) e.setAttribute(k,String(v));
 return e;
};
function point(node,mode){
 if(mode==="orb"){
  const i=seed.nodes.findIndex(n=>n.id===node.id);
  const a=(i/seed.nodes.length)*Math.PI*2-Math.PI/2;
  const r=node.id==="work"?0:210;
  return {x:500+Math.cos(a)*r,y:275+Math.sin(a)*r};
 }
 if(mode==="trails"){
  const i=seed.nodes.findIndex(n=>n.id===node.id);
  return {x:90+i*135,y:i%2===0?200:340};
 }
 return {x:node.x*10,y:node.y*5.5};
}
function textEl(parent,label,x,y,cssClass){
 const t=svg("text",{x,y,"text-anchor":"middle",class:cssClass});
 t.textContent=label; parent.append(t);return t;
}
function render(){
 const data=projection(seed,view,cursor);
 const stage=$("scene");stage.replaceChildren();
 const coords=new Map(data.nodes.map(n=>[n.id,point(n,view)]));
 for(const e of data.edges){
  const a=coords.get(e.from),b=coords.get(e.to);
  const line=svg("line",{x1:a.x,y1:a.y,x2:b.x,y2:b.y,
   class:"relation "+(e.epistemic==="PREDICTED"?"forecast":e.epistemic==="CANDIDATE"?"candidate":"")});
  const tooltip=svg("title");tooltip.textContent=e.from+" "+e.type+" "+e.to+" | "+e.epistemic;line.append(tooltip);stage.append(line);
 }
 for(const n of data.nodes){
  const p=coords.get(n.id),g=svg("g",{class:"node "+(n.epistemic==="PREDICTED"?"predicted":n.epistemic==="CANDIDATE"?"candidate":"")+(n.id===selected?" active":""),tabindex:"0",role:"button","aria-label":n.label+" "+n.kind+" "+n.epistemic});
  const c=svg("circle",{cx:p.x,cy:p.y,r:39});
  g.append(c);textEl(g,n.label,p.x,p.y+4,"node-label");
  const title=svg("title");title.textContent=n.kind+" | "+n.epistemic+" | Synthetic";g.append(title);
  const choose=()=>{selected=n.id;render();};
  g.addEventListener("click",choose);g.addEventListener("keydown",ev=>{if(ev.key==="Enter"||ev.key===" "){ev.preventDefault();choose();}});
  stage.append(g);
 }
 const item=data.nodes.find(n=>n.id===selected);
 const touching=seed.edges.filter(e=>e.from===selected||e.to===selected);
 $("inspect").textContent=item.label+" / "+item.kind+" / "+item.epistemic+" | "+touching.length+" incident relations. Source: synthetic fixture, not live telemetry.";
 $("current").textContent=data.edges.length+" typed links shown; "+data.censored_edges+" outside selected time cursor. No model connected. No receiver ACK.";
 $("timetext").textContent="Synthetic event horizon "+cursor+"/6. Past and forecast are not present-state proof.";
 $("status").textContent=view==="ambient"?"Ambient preview only. Does not change OS wallpaper or screensaver.":"Static/offline demonstration. Nothing was transmitted.";
 $("scene").setAttribute("aria-label","Synthetic "+view+" relational projection with "+data.edges.length+" visible links");
 document.querySelectorAll("[data-view]").forEach(button=>button.setAttribute("aria-pressed",String(button.dataset.view===view)));
}
function preview(){
 const input=$("draft"),pred=ghost(input.value,input.selectionStart);
 $("hint").textContent=pred?"Suggested beyond cursor: "+pred:"Type Compare, Map, Show or Review to preview a local suggestion.";
 $("accept").disabled=!pred;
}
document.querySelectorAll("[data-view]").forEach(b=>b.addEventListener("click",()=>{view=b.dataset.view;render();}));
$("time").addEventListener("input",()=>{cursor=Number($("time").value);render();});
$("draft").addEventListener("input",()=>{draft=$("draft").value;preview();});
$("draft").addEventListener("click",preview);
$("draft").addEventListener("keyup",preview);
$("accept").addEventListener("click",()=>{
 const input=$("draft"),offset=input.selectionStart;
 const suggestion=ghost(input.value,offset);
 if(!suggestion) return;
 const accepted=acceptSuggestion(input.value,offset,suggestion,true);
 input.value=accepted.text;input.focus();input.setSelectionRange(accepted.cursor,accepted.cursor);
 draft=accepted.text;caret=accepted.cursor;
 history.push({type:"EXPLICIT_GHOST_ACCEPT",epistemic:"LOCAL_EDIT",source:seed.identity,ack:"NONE"});
 $("ack").textContent="CoAckRAW: LOCAL_EDIT_OBSERVED. Receiver ACK: UNPROVEN.";
 preview();
});
$("export").addEventListener("click",()=>{
 const data=checkpoint($("draft").value,view,cursor,history);
 const blob=new Blob([JSON.stringify(data,null,2)+"\n"],{type:"application/json"});
 const url=URL.createObjectURL(blob);
 const anchor=document.createElement("a");anchor.href=url;anchor.download="comap-cursor-r0-local-checkpoint.json";anchor.click();
 URL.revokeObjectURL(url);
 $("ack").textContent="Local JSON export requested. File download is not delivery or receiver ACK.";
});
$("reset").addEventListener("click",()=>{
 $("draft").value="";draft="";caret=0;history=[];selected="work";view="map";cursor=6;$("time").value="6";
 $("ack").textContent="CoAckRAW: NONE. Receiver ACK: UNPROVEN.";render();preview();
});
render();preview();
