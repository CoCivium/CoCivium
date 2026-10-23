/* CoMapPulse R0 browser projection. All state is ephemeral, no network requests. GPL-3.0 */
'use strict';
(function(){
  const $=id=>document.getElementById(id), NS='http://www.w3.org/2000/svg';
  const data=JSON.parse($('graph-data').textContent);
  const core=window.CoMapCore;
  const stats=core.validateGraph(data);
  const map=new Map(data.nodes.map(n=>[n.id,n]));
  let mode='map', selected='comap', inspected=0, prediction=null, foundIds=null;
  const statusClass=state=>state==='HELD'?'held':state==='PROPOSED'||state==='CANDIDATE'||state==='DESIGN_ONLY'?'proposed':'documented';
  function sEl(tag,attrs){const el=document.createElementNS(NS,tag);for(const [key,val] of Object.entries(attrs||{}))el.setAttribute(key,String(val));return el;}
  function label(node){const t=node.title;const parts=t.split(' ');const max=parts.length>=2&&t.length>17?Math.ceil(parts.length/2):parts.length;
    const lines=parts.length>max?[parts.slice(0,max).join(' '),parts.slice(max).join(' ')]:[t];return lines.map(x=>x.length>19?x.slice(0,18)+'…':x);}
  function midPath(from,to){const a=map.get(from),b=map.get(to);let offset=0;
    const dx=b.x-a.x,dy=b.y-a.y,len=Math.hypot(dx,dy)||1;
    if(mode==='trails')offset=Math.min(85,len*.17);return {d:`M ${a.x} ${a.y} Q ${(a.x+b.x)/2-dy/len*offset} ${(a.y+b.y)/2+dx/len*offset} ${b.x} ${b.y}`,mx:(a.x+b.x)/2-dy/len*offset*.5,my:(a.y+b.y)/2+dx/len*offset*.5};}
  function renderGraph(){const svg=$('graph-svg');svg.replaceChildren();
    const defs=sEl('defs');const marker=sEl('marker',{id:'arrow',viewBox:'0 0 10 10',refX:'8',refY:'5',markerWidth:'4',markerHeight:'4',orient:'auto-start-reverse'});marker.append(sEl('path',{d:'M 0 0 L 10 5 L 0 10 z',fill:'#9fbcc6'}));defs.append(marker);svg.append(defs);
    for(const edge of data.edges){const p=midPath(edge.from,edge.to);const active=edge.from===selected||edge.to===selected;
      const classes=['relation',edge.epistemic==='PROPOSED'?'proposed':edge.epistemic==='HELD'?'held':'documented',active?'emphasis':'dimmed'].filter(Boolean).join(' ');
      const path=sEl('path',{d:p.d,class:classes,'data-id':edge.id,'marker-end':'url(#arrow)'});svg.append(path);
      if(mode==='trails'&&active){const t=sEl('text',{x:p.mx,y:p.my-9,class:'relation-label'});t.textContent=edge.relation;svg.append(t);}
    }
    for(const n of data.nodes){const g=sEl('g',{class:`node ${n.id===selected?'selected ':''}${n.status==='HELD'?'held ':''}${n.id==='goal'?'goal ':''}${(foundIds&&!foundIds.has(n.id))?'dimmed':''}`,'data-node-id':n.id,tabindex:'0',role:'button','aria-label':`Inspect ${n.title}; status ${n.status}`});
      const rect=sEl('rect',{x:n.x-78,y:n.y-27,width:156,height:61,rx:13});g.append(rect);
      label(n).forEach((line,i,all)=>{const t=sEl('text',{x:n.x,y:n.y+(all.length===1?0:-7)+i*15});t.textContent=line;g.append(t);});
      const st=sEl('text',{x:n.x,y:n.y+23,class:'sub'});st.textContent=n.status;g.append(st);
      g.addEventListener('click',()=>select(n.id));g.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();select(n.id);}});svg.append(g);
    }
    $('graph-viewport').dataset.mode=mode;
  }
  function renderNodeList(){const list=$('node-list');list.replaceChildren();for(const n of data.nodes){const b=document.createElement('button');b.type='button';b.textContent=n.title+' · '+n.status;b.setAttribute('aria-pressed',String(n.id===selected));b.addEventListener('click',()=>select(n.id));list.append(b);}}
  function select(id){if(!map.has(id))return;selected=id;const n=map.get(id);$('detail-title').textContent=n.title;$('detail-text').textContent=n.detail;
    $('detail-type').textContent=n.type;$('detail-status').textContent=n.status;$('detail-status').className='tag '+statusClass(n.status);
    const src=$('detail-source');src.replaceChildren();if(n.source&&core.safePublicUrl(n.source)){const a=document.createElement('a');a.href=n.source;a.target='_blank';a.rel='noopener noreferrer';a.textContent='Public source (opens separately)';src.append(a);}else{src.textContent='No independently verified source supplied for this proposal.';}
    $('detail-next').textContent=n.status==='HELD'?'Qualify a real receiver, obtain its own readproof, then review authority.':n.status==='DESIGN_ONLY'||n.status==='PROPOSED'||n.status==='CANDIDATE'?'Run a distinct, bounded first-use test; preserve failures.':'Follow the evidence link and challenge the claim.';
    $('detail-relations').replaceChildren();core.related(data,id).forEach(edge=>{const li=document.createElement('li');li.textContent=`${edge.relation} → ${map.get(edge.other).title} · ${edge.epistemic} · ${edge.ack}`;$('detail-relations').append(li);});renderGraph();renderNodeList();
  }
  function renderRoutes(){const body=$('routes');body.replaceChildren();core.routePlan(data).forEach(route=>{const tr=document.createElement('tr'),name=document.createElement('td'),state=document.createElement('td');name.textContent=route.label;state.textContent=route.state;state.className='state '+(route.state.startsWith('HOLD')?'held':'pointer');tr.append(name,state);body.append(tr);});}
  function setMode(next){mode=next;for(const item of ['map','trails','quiet'])$('view-'+item).setAttribute('aria-pressed',String(item===next));
    $('mode-note').textContent=next==='quiet'?'Quiet CoOrb is a browser projection, not an OS background service.':next==='trails'?'Trails annotate relations by evidence status and time; no predictive future is asserted.':'Schematic CoMap projection, not live machine status.';renderGraph();}
  for(const m of ['map','trails','quiet'])$('view-'+m).addEventListener('click',()=>setMode(m));
  $('inspect-local').addEventListener('click',()=>{$('inspection').textContent=`LOCAL_INSPECTION = ${++inspected}. Actual receiver ACK = NOT_OBSERVED. No receipt sent.`;});
  $('export-snapshot').addEventListener('click',()=>{const text=JSON.stringify(data,null,2)+'\n',blob=new Blob([text],{type:'application/json'}),url=URL.createObjectURL(blob);const a=document.createElement('a');a.href=url;a.download='CoMapPulse_PUBLIC_SNAPSHOT_R0.json';a.click();URL.revokeObjectURL(url);});
  const cmd=$('command'),toggle=$('enable-prediction'),ghost=$('ghost'),hint=$('prediction-hint');
  function positionGhost(){ghost.textContent='';prediction=null;
    if(!toggle.checked||document.activeElement!==cmd||cmd.selectionStart!==cmd.selectionEnd){$('accept-prediction').disabled=true;return;}
    const cursor=cmd.selectionStart;prediction=core.predict(cmd.value,cursor,true);
    if(!prediction){hint.textContent='No local static completion at this cursor; nothing is inferred.';$('accept-prediction').disabled=true;return;}
    const style=getComputedStyle(cmd),canvas=document.createElement('canvas'),ctx=canvas.getContext('2d');ctx.font=style.font;
    const inputPrefix=cmd.value.slice(0,cursor),pixel=ctx.measureText(inputPrefix).width;
    ghost.style.left=`${Math.max(13,Math.min(cmd.clientWidth-16,13+pixel-cmd.scrollLeft))}px`;
    ghost.textContent=prediction.suffix;
    $('accept-prediction').disabled=false;
    hint.textContent=`Local static suggestion ${prediction.term}. Accept with button or F2. No automatic submission.`;
  }
  function updateHint(){if(!toggle.checked){prediction=null;ghost.textContent='';$('accept-prediction').disabled=true;hint.textContent='Suggestions OFF; input stays on this device and in this page.';return;}positionGhost();}
  function acceptHint(){if(!toggle.checked||!prediction)return;const cursor=cmd.selectionStart;const updated=core.accept(cmd.value,cursor,prediction);cmd.value=updated;const p=cursor+prediction.suffix.length;cmd.focus();cmd.setSelectionRange(p,p);positionGhost();}
  $('accept-prediction').addEventListener('click',acceptHint);toggle.addEventListener('change',updateHint);
  for(const event of ['input','click','keyup','focus','select'])cmd.addEventListener(event,updateHint);
  cmd.addEventListener('blur',()=>{ghost.textContent='';});
  cmd.addEventListener('keydown',event=>{if(event.key==='F2'&&toggle.checked&&prediction){event.preventDefault();acceptHint();}if(event.key==='Escape'){ghost.textContent='';prediction=null;$('accept-prediction').disabled=true;}});
  $('reset-input').addEventListener('click',()=>{cmd.value='';cmd.focus();foundIds=null;renderGraph();updateHint();});
  $('inspect-input').addEventListener('click',()=>{const words=cmd.value.toLowerCase().match(/[a-z0-9]+/g)||[];foundIds=new Set(data.nodes.filter(n=>words.some(w=>(n.title+' '+n.type+' '+n.id+' '+n.detail).toLowerCase().includes(w))).map(n=>n.id));
    $('mode-note').textContent=`Local query highlighted ${foundIds.size} of ${data.nodes.length} bounded entries; no remote discovery.`;renderGraph();});
  $('json-info').textContent=`${stats.nodes} nodes | ${stats.edges} edges | ${stats.receivers} proposed or held receiver paths | snapshot ${data.snapshot} | no live source polling. All URLs are explicit public-source pointers.`;
  renderRoutes();select('comap');setMode('map');updateHint();
})();
