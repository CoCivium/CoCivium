# CiVars+ and CoKarma+ | CiAll-wide R0 experimental relation layer

**Status:** Offline, synthetic, opt-in architecture candidate. **NOT** a scoring system for people, a financial token, a deployed runtime, a continuously running scheduler, or an assessment of independent visitor outcomes.

## First-use question

Can a change in need, evidence, capability or currentness affect the *next safe task* while a genuine contribution or correction is recognized without converting a person into a number?

- **CiVars (provisional label):** typed, scoped descriptors of a work object's context, needs, constraints, evidence, uncertainty, currentness and *observation/proposal* authority. The exact term had no established definition in the searched public CoCivium sources. This candidate does **not** claim to settle the name.
- **CoKarma (provisional label):** opt-in, object-specific **contribution/benefit relations** such as origin, challenge, repair, verification, translation, and gratitude. **Not** a moral ledger, a score, social credit, global ranking, trading balance, pay-to-win mechanism, or grant of authority.

Reuses the CoCivium `CoParticipationEcology+` contribution-lineage and benefit-observation distinction. Review outcomes can be `UNACKNOWLEDGED`, `BENEFIT_OBSERVED_CAUSE_UNPROVEN`, `HELD_NO_CONSENT`, `HELD_PRIVACY`, or `RETRACTED_CLAIM`. Even a recorded comparator does not prove causality.

## Quickstart

```sh
cd CiVars_CoKarma_R0
python3 -m unittest discover -s tests -v
python3 build_evidence.py
python3 verify_release.py
```

Python standard library only. No network, GPU, accounts, models, timers, mouse hooks or background processes.

## Cross-lane evolution: one small shared envelope

| Existing lane | CiVars candidate role | CoKarma candidate role | What still needs evidence |
|---|---|---|---|
| CoParticipation / CoSteward | privacy, authority, accessibility | fair contribution lineage, right to opt out, correction/appeal | independent consent and dispute handling |
| CoEvo / CoTurtle / CoReview | uncertainty, test budget, challenge triggers | record and preserve a counterexample even when unpopular | real challenger outcomes |
| CoResource / CoOmni / CoStretch | resource need, currentness, capability | mark objectively useful reusable changes | actual measured cost and benefits |
| CoFactory / CoProduct / CoSpiff | audience, first-task requirement, feedback | recognize repair, translation, nontechnical help | independent first-use completion |
| CoOrbWare / CoMap / CoBar | explain why a next task appears | optionally show attribution and uncertainty | comprehension/accessibility tests |
| CoEvergreen / CoStead / CoAckRAW | source ID, checkpoint, scope expiry | verified ACK versus publisher claim | receiver readproof and deletion tests |

### No hidden power gain

`KARMA_RECORD_NE_PERSON_SCORE` · `APPRECIATION_NE_PAYMENT` · `CONTRIBUTION_NE_CAUSAL_BENEFIT` · `THANKS_NE_AUTHORITY` · `WORKING_SCOPE_NE_GLOBAL_TRACKING` · `CURRENTNESS_NE_CONSENT` · `MODEL_AGREEMENT_NE_INDEPENDENT_REVIEW`

A reputation algorithm, contribution-based priority rank, forced identity, financial award, cross-context profiling, or automatic external outreach is outside scope. Human reviewers retain their own accountabilities; CoKarma can't arbitrate someone's moral worth or create governance authority.

## Synthetic negative case (keep the failure)

Two safe, low-cost tasks are represented: (A) independently challenge a privacy issue and (B) publish publicity. Under the authored **predicted** benefit values, the task selector chooses A. Under an authored **distribution shift**, its true benefit can be A=0 and B=6. This is a **FAIL** for the predictor, even though the unit tests pass. This is an illustrative counterexample, not a real-world effect or a claim that publicity beats privacy review.

## Governance and rollout gates

1. **Source review:** no second participant ontology, no duplicate credit or donor capture, no de facto social scoring.
2. **Privacy/legal review:** scoped opt-in, minimization, independent source permission, optional attribution, correction/retraction/deletion lifecycle. A public append-only hash chain is *not* appropriate for personal information.
3. **Adversarial review:** collusive ACKs, sybil amplification, proxy ratings, popularity/celebrity bias, inaccessible participation, claims of downstream causality and soft coercion.
4. **Product review:** one voluntary task on one surface; explain meaning, uncertainty and opt-out without ontology.
5. **Operational review:** explicit owner, versioned schema, rollback, budget, safety gates, edge cases, renderer-neutral semantics.
6. **Independent acceptance:** consented visitors and maintainers verify real utility and real corrections. Report null/negative outcomes; do not claim global uptake.

## Sources and relationship

- [CoParticipationEcology+](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COPARTICIPATION_ECOLOGY_R0.md) supplies the contribution/benefit relation rail.
- [CoOmni+ resource fabric](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COOMNI_CONTEXT_RESOURCE_FABRIC_R0_20261024.md) supplies descriptor, availability, authority and bounded active-frontier mechanisms.
- [CoEvoAll middle latch](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COEVOALL_MIDDLE_LATCH_R0_20261024.md) supplies the durable intention, not unrestricted execution or financial transfers.

Source exists and tests pass only **locally** until independent replication. Publication to a review branch is not merge, adoption, or acknowledgement by a recipient.