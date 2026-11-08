# CoPullVector+ R0: deterministic synthetic smoke test

**Status:** candidate experiment, not validated theory or runtime. Related: #378 (G_dSide), #386 (CoZombieApocalypse), #367 (measurement).

Run: `python3 experiments/copullvector/copull_benchmark_r0.py > results.json`. Repeat with same seed and compare output byte-for-byte. Python standard library only; defaults seed=261108, trials=200.

## Purpose
Exercise deterministic candidate generation, five policy routes, one constrained admissibility gate, measurable outputs, and counterexample preservation. This test was constructed and executed in the assistant's isolated working container, not X2/CoFarm/CoStead. Results reported below are from a local implementation; CI on the GitHub branch and independent receiver acceptance remain unverified.

## Local test observation (200 artificial trials)
- Supply mean synthetic utility: -0.113303
- Demand: -0.090619
- Hybrid: -0.116618
- G_dSide proxy: 0.210796
- Random: -0.127320
- G_dSide proxy lost to hybrid on **13/200** trials; first counterexample at trial 3.
- 0 inadmissible choices across policies, by construction: scoring ranks only prefiltered eligible choices.
- A deterministic rerun of the original local script produced identical output.

**Critical bias warning:** the G_dSide selector sees noisy versions of the very outcome dimensions used by the constructed oracle utility function; supply and demand selectors see independent random variables. Thus the G_dSide lead is expected by design, is NOT a meaningful fair head-to-head model comparison, and must not be used to support metaphysical, economic, policy or real-world superiority claims. Even its loss cases are artificial. This is a smoke test for mechanics and counterexample capture.

## Next research upgrade
Use held-out worlds with causally generated supply/demand indicators and blinded outcome measurements; equal-information budgets; distinct models; preregistered utility and constraints; multiple seeds with intervals; prior-sensitive information costs; distribution shifts; adversarial labels; independent review; measured ecological and consent consequences. Never choose weights using test labels. Preserve all Pareto-incomparable alternatives.

## Nonclaims
No 24h continuous runner, actual provider federation, cross-session pickup, executable CoBar/CoOrb integration, physical disaster response, CoEx, canon or authorization is proved by this PR.
