# CoAlienMath / CoPriMath R0: Public falsifier laboratory

**Status:** Public research candidate for criticism. Not CoAll canon, a new theorem, a physics discovery, a claim of sentient AI, a certified measurement standard, or an installed X2 service.

## Why this is public

A private notebook is not an independent review. This public-safe companion makes a few unusual mathematical intuitions reproducible and challengeable, without publishing private machine evidence, recipient information, credentials, unpublished internal archives, or unverified receiver claims. This is a proposal and falsification surface, not an official release.

Existing adjacent public review: [CoMeasure R0 PR #365](https://github.com/CoCivium/CoCivium/pull/365) is the measurement-registry candidate, and [PR #366](https://github.com/CoCivium/CoCivium/pull/366) is a supplemental challenger. This laboratory addresses **identifiability, decision preservation, typed nulls, independent observation and experimental discrimination**. It must not create a competing unit registry.

## Working question

Can an evidence-aware relational calculus combine established mathematics, including type theory, causal inference, compositionality, inverse problems and experimental design, to help observers distinguish what is *represented*, what is *observed*, what is *identifiable*, what is *still possible*, and what is *permitted*? The useful claim is a possible engineering synthesis. Novelty, formal completeness and real-world benefit are **unproven**.

## Four elementary propositions and disproof obligations

1. **Observation cannot identify what it cannot separate.** If admissible observations `f(w1) == f(w2)` but the worlds require different conclusions, then any decoder using only `f` must give the same response to both. A stronger test requires an observation or intervention whose outputs differ. This is elementary non-identifiability, not newly invented mathematics.
2. **Decision-preserving projection.** A finite encoding `q:S -> T` retains all decisions in a specified family `D` if and only if every decision is constant on each fiber `q^-1(t)`. Example: compressing `UNKNOWN` and `NOT_AUTHORIZED` into generic `NULL` is unsafe when they require different actions. This is an elementary factorization criterion.
3. **Restricted authority composes.** If every admissible step satisfies `A(next) subseteq A(prior)`, then any finite chain cannot increase authority. This is a formal condition, not evidence that an actual process faithfully enforces it.
4. **Multiple witnesses can be one failure domain.** Three displays reading the same untrusted producer do not create three independent confirmations. Evidence combination requires conditional dependence modeling; a copied signature or screenshot proves no fresh effect.

An additional counterexample uses three binary variables with pairwise constraints `a != b`, `b != c`, `c != a`. Each individual constraint is satisfiable, but all three cannot hold together. Locally plausible evidence is not necessarily a globally consistent world.

## Speculative exploration: unusual priors, strict gates

Explore process-first identities, coinductive and non-well-founded structures, sheaf-style contextuality, typed negative space, inverse ontologies, causal topology, probabilistic model ambiguity, information geometry, multi-scale emergence, predictions of future relation types, and quality-diversity searches across candidate axiom systems. These have mature predecessors and may add nothing. Distinguish the *metaphor*, a *formal definition*, a *proved proposition*, a *software test*, and an *empirically evaluated explanation*. An unfamiliar mathematical glyph is not evidence of alien life or a new physical law.

## Reproduce the synthetic lab

At the public repository root:

```sh
python3 -m unittest discover -s ai/coalienmath -p 'test_*.py' -v
python3 -O -m unittest discover -s ai/coalienmath -p 'test_*.py' -v
```

This is standard-library-only deterministic code, with no network, file mutation, secrets, GUI, automated messages, or independent receiver. Tests cover observations that cannot distinguish a live UI from a recording, typed zero/unknown, unit mismatches, permission non-escalation, correlated observers, a toy gauge freedom, and a finite constraint contradiction. Passing means only that these local fixtures behaved as specified. This limited residual operator does not implement time-window, uncertainty, reference-frame, provenance, or independent-receiver qualification; passing must never be used as a production measurement gate.

## Honest next proof

Compare this representation against plain typed JSON and simple scripts using identical held-out adversarial cases. Track false-green status promotions, correct decisions, counterexample discovery, human comprehension, runtime cost, proof obligation count, and recovery. If the richer approach does not add value, keep the simpler baseline. No new recurring scheduler or automatic promotion is authorized by this public draft.

## Prior art and criticism welcome

- [Fong & Spivak, *Seven Sketches in Compositionality*](https://arxiv.org/abs/1803.05316)
- [W3C PROV-O](https://www.w3.org/TR/prov-o/)
- [Homotopy Type Theory book](https://homotopytypetheory.org/book/)
- [Abramsky & Brandenburger, sheaf-theoretic contextuality](https://arxiv.org/abs/1102.0264)
- [Stanford Encyclopedia, non-well-founded set theory](https://plato.stanford.edu/entries/nonwellfounded-set-theory/)

**Boundaries:** PUBLIC_DRAFT_NE_CANON; SYNTHETIC_PASS_NE_REALITY_PROOF; SOURCE_HASH_NE_SOURCE_TRUTH; MULTI_FEED_NE_INDEPENDENT_WITNESS; PREDICTION_NE_OUTCOME; NULL_NE_ZERO; NEW_NOTATION_NE_NEW_MATHEMATICS; PRIVATE_PRECURSOR_NE_PUBLIC_DISCLOSURE.
