// Bounded wave portfolio election. Deterministic advisory, never starts workers.
export function electWave(candidates, recent, {max=2}={}) {
  if (!Array.isArray(candidates) || !Array.isArray(recent) ||
      !Number.isInteger(max) || max<1 || max>8) throw Error('INVALID_WAVE_INPUT');
  const seen=new Set(), ranked=[];
  for (const c of candidates) {
    if (!c || typeof c.id!=='string' || !/^[A-Za-z0-9_.:-]{1,100}$/.test(c.id) ||
        typeof c.front!=='string' || !/^[A-Za-z0-9_.:-]{1,100}$/.test(c.front) ||
        !['ELIGIBLE','BLOCKED','DORMANT'].includes(c.state) ||
        typeof c.benefit!=='number' || !Number.isFinite(c.benefit) || c.benefit<0 || c.benefit>10 ||
        typeof c.cost!=='number' || !Number.isFinite(c.cost) || c.cost<0 || c.cost>10 ||
        typeof c.urgentRepair!=='boolean' || typeof c.authorized!=='boolean' || seen.has(c.id))
      throw Error('INVALID_CANDIDATE');
    seen.add(c.id);
    if(c.state!=='ELIGIBLE' || !c.authorized) continue;
    const sameFront=recent.filter(x=>x===c.front).length;
    const novelty= sameFront===0 ? 3 : -Math.min(3,sameFront*2);
    ranked.push({...c,score:c.benefit-c.cost+novelty+(c.urgentRepair?20:0),
      novelty_class:sameFront?'REPEATED_FRONT':'NEW_FRONT', repeat_reason:c.urgentRepair?'URGENT_REPAIR':sameFront?'BENEFIT_OUTWEIGHS_NOVELTY':'DIVERSIFY'});
  }
  if(recent.some(x=>typeof x!=='string' || !/^[A-Za-z0-9_.:-]{1,100}$/.test(x)))
    throw Error('INVALID_HISTORY');
  ranked.sort((a,b)=>b.score-a.score || a.id.localeCompare(b.id));
  return {schema:'CoAll.CoEvoCycle.WaveElection.R0',selected:ranked.slice(0,max).map(x=>({
    id:x.id,front:x.front,score:x.score,novelty_class:x.novelty_class,reason:x.repeat_reason
  })), eligible_count:ranked.length, unelected_count:ranked.length-Math.min(max,ranked.length),
    effect:'ADVISORY_ONLY', worker_count:0, receiver_ack:false,
    nonclaims:['DIVERSITY_NE_USEFULNESS','SELECTED_NE_EXECUTED','NO_CROSS_SESSION_SYNC']};
}
