# CoAthene Review Intake / Defect Compiler R0C

**State:** `PUBLIC_CANDIDATE__REVIEW_INTAKE_AND_DERIVATION_CONTRACT__NO_HUMAN_REVIEW_YET`

## Purpose

A public review is evidence about the module. It is not automatically truth, endorsement, authority, or a patch instruction.

R0C defines a bounded path:

```text
raw human review
-> immutable source reference
-> section extraction
-> candidate defect(s)
-> dedupe / relation to other reviews
-> project disposition
-> patch candidate where warranted
-> machine tests
-> human re-review where material
-> pilot gate
```

## Two-object rule

Never collapse the review and our interpretation of the review.

### Object A — Raw review

Preserve:

- source URL / issue ID;
- author handle as publicly supplied;
- timestamp;
- exact public body;
- edits/currentness where observable;
- reviewer-declared role/context;
- reviewer-declared conflicts;
- reviewer disposition;
- reviewer confidence.

### Object B — Derived defect candidate

May contain:

- defect ID;
- source review relation;
- affected file/section;
- concise normalized claim;
- severity;
- confidence;
- evidence/example;
- suggested fix;
- duplicate/related defect links;
- project disposition;
- disposition rationale;
- patch/test links.

A derived defect can be wrong even when the raw review is perfectly preserved.

`RAW_REVIEW_NE_DERIVED_DEFECT`

## Reviewer authority

Reviewer expertise is useful context but does not make a claim true.

Likewise, anonymous or non-credentialed feedback is not automatically invalid.

`CREDENTIAL_NE_TRUTH`  
`NO_CREDENTIAL_NE_NO_EVIDENCE`  
`REVIEWER_CLAIM_NE_PROJECT_FACT`

## Severity and priority

Reviewers may state severity.

Project triage may independently state priority.

These are different relations:

`SEVERITY_NE_PRIORITY`

Example:

- a high-severity defect might be low priority only because the module is already held from pilot;
- a low-severity typo may be high priority if it causes systematic misunderstanding across every lesson.

## Disposition

Project disposition values:

- ACCEPT
- ACCEPT_WITH_MODIFICATION
- DEFER_WITH_REASON
- DISAGREE_WITH_EVIDENCE
- NEEDS_TEST
- DUPLICATE
- OUT_OF_SCOPE_FOR_THIS_MODULE

Disposition must not overwrite the reviewer conclusion.

`DISPOSITION_NE_REVIEWER_AGREEMENT`

## Multiple reviews

Two comments do not necessarily equal two independent observations.

Potential relations include:

- INDEPENDENTLY_CORROBORATES
- REPEATS
- DERIVES_FROM
- CONTRADICTS
- PARTIALLY_OVERLAPS
- ADDRESSES_DIFFERENT_SCOPE

`MULTIPLE_REVIEWS_NE_INDEPENDENT_CORROBORATION_BY_DEFAULT`

## Public correction rule

When a material critique is accepted:

1. preserve the raw critique;
2. create/relate defect;
3. patch on a branch;
4. run existing canaries;
5. add a regression test where technically meaningful;
6. record disposition;
7. request human re-review for material pedagogical/safety changes.

Do not rewrite history to make the original module appear never to have had the defect.

## Advancement gate

`EDUCATOR_REVIEWED` requires at least:

- one real human review source;
- raw review preserved/referenced;
- material defect extraction;
- disposition record.

`PILOT_READY` requires more than `EDUCATOR_REVIEWED`.

R0C does not define the full pilot gate.

## Current state

As of creation of R0C, public issue #133 had **zero comments**.

That is a dated observation, not a permanent claim.

`ZERO_COMMENTS_AT_T_NE_NO_FUTURE_REVIEW`

## Rails

`RAW_REVIEW_NE_DERIVED_DEFECT`  
`REVIEWER_CLAIM_NE_PROJECT_FACT`  
`CREDENTIAL_NE_TRUTH`  
`NO_CREDENTIAL_NE_NO_EVIDENCE`  
`SEVERITY_NE_PRIORITY`  
`DISPOSITION_NE_REVIEWER_AGREEMENT`  
`MULTIPLE_REVIEWS_NE_INDEPENDENT_CORROBORATION_BY_DEFAULT`  
`STRUCTURED_REVIEW_NE_TRUTH`  
`REVIEW_FORM_NE_REVIEW`  
`NO_SILENT_DELETION_OF_MATERIAL_CRITIQUE`
