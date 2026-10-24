// CoDoodle+ / CoNex+ R0 reference generator.
// Dependency-free, deterministic, local-only. Generates candidates; does not execute effects.

import { performance } from 'node:perf_hooks';

export const OPERATORS = [
  "COMBINE","SPLIT","REVERSE","NEGATE","COMPLEMENT","SUBSTITUTE",
  "TRANSLATE","COMPRESS","EXPAND","REFRAME","TEMPORAL_SHIFT","RECEIVER_SHIFT",
  "OBSERVER_SHIFT","SUBSTRATE_SHIFT","SCALE_SHIFT","RENDER_SHIFT",
  "COUNTERFACTUAL","ANTI_HISTORY","NULL_BASELINE","OUTSIDE_VIEW"
];

function fnv1a(str) {
  let h = 0x811c9dc5;
  for (let i=0;i<str.length;i++) {
    h ^= str.charCodeAt(i);
    h = Math.imul(h, 0x01000193) >>> 0;
  }
  return h >>> 0;
}

function rng(seed) {
  let x = (seed >>> 0) || 1;
  return () => {
    x ^= x << 13; x >>>= 0;
    x ^= x >>> 17; x >>>= 0;
    x ^= x << 5; x >>>= 0;
    return (x >>> 0) / 4294967296;
  };
}

function idFor(sourceId, op, slot, seed) {
  return "cd_" + fnv1a(`${sourceId}|${op}|${slot}|${seed}`).toString(16).padStart(8,"0");
}

export function generate({sourceId="source", seed=1, count=128, operators=OPERATORS}={}) {
  if (!Number.isInteger(count) || count < 0 || count > 1_000_000) throw new Error("invalid count");
  if (!operators.length) throw new Error("operators required");
  const random = rng(seed);
  const out = [];
  const seen = new Set();

  for (let i=0;i<count;i++) {
    const op = operators[Math.floor(random()*operators.length)];
    const variant = Math.floor(random()*0x100000000) >>> 0;
    const id = idFor(sourceId, op, i, seed);
    const key = `${op}|${variant}`;
    if (seen.has(key)) continue;
    seen.add(key);
    out.push({
      id,
      source_id: sourceId,
      operator: op,
      variant,
      seed,
      status: "CANDIDATE",
      authority: "NONE",
      executable: false
    });
  }
  return out;
}

export function select(candidates, cap=32) {
  if (!Number.isInteger(cap) || cap < 0 || cap > 32) throw new Error("selector cap must be 0..32");
  const required = ["NULL_BASELINE","NEGATE","COUNTERFACTUAL","OUTSIDE_VIEW"];
  const chosen = [];
  const used = new Set();

  for (const op of required) {
    const c = candidates.find(x => x.operator === op);
    if (c && chosen.length < cap) { chosen.push(c); used.add(c.id); }
  }
  for (const c of candidates) {
    if (chosen.length >= cap) break;
    if (!used.has(c.id)) { chosen.push(c); used.add(c.id); }
  }
  return chosen;
}

export function benchmark(opts={}) {
  const t0 = performance.now();
  const candidates = generate(opts);
  const elapsedMs = performance.now() - t0;
  return {
    candidates,
    receipt: {
      schema: "CoDoodle.CoNex.GenerationReceipt.R0",
      source_id: opts.sourceId ?? "source",
      seed: opts.seed ?? 1,
      requested: opts.count ?? 128,
      generated: candidates.length,
      elapsed_ms: Number(elapsedMs.toFixed(6)),
      candidates_per_second: elapsedMs > 0 ? Math.round(candidates.length / (elapsedMs/1000)) : null,
      microseconds_per_candidate: candidates.length ? Number(((elapsedMs*1000)/candidates.length).toFixed(3)) : null,
      external_effects: 0,
      workers_spawned: 0,
      authority: "NONE"
    }
  };
}
