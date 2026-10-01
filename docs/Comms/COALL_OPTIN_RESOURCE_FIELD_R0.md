# CoAll Opt-In Resource Field R0

**State:** `CANDIDATE__DESIGN_AND_POLICY_ONLY__NO_RESOURCE_CAPTURE_OR_RUNTIME_AUTHORITY`

## Purpose

As more participants explicitly opt in, CoAll may gain a broader pool of usable capabilities, attention, compute, storage, expertise, moderation, translation, local models, bandwidth, and other volunteered resources.

The important distinction is that a visible default menu is not itself consent.

`DEFAULT_VISIBLE_NE_DEFAULT_GRANTED`

A participant MAY choose a single "enable recommended defaults" action after seeing the grant set, but each underlying permission remains inspectable, revocable, bounded, and attributable.

## Candidate grant object

A `CoContributionGrant+` SHOULD bind:

- participant / principal reference;
- resource class;
- exact scope;
- allowed purposes;
- surface / device / account;
- read / write / execute ceiling;
- quantity or rate cap;
- locality requirements;
- privacy class;
- retention;
- expiry;
- quiet hours / battery / network constraints where relevant;
- revocation route;
- receipts;
- whether delegation or referral is allowed;
- currentness.

`OPT_IN_NE_PERPETUAL_CONSENT`

`CAPACITY_NE_PERMISSION`

`USER_DEVICE_NE_FREE_COMPUTE`

## Resource classes

Candidate resource classes include:

- `ATTENTION`: review, adjudication, moderation, mentoring;
- `EXPERTISE`: domain knowledge, critique, translation;
- `COMPUTE`: CPU/GPU/NPU or local-model inference;
- `STORAGE`: bounded replicated custody;
- `BANDWIDTH`: bounded transport/relay;
- `LOCAL_MODEL`: explicitly exposed model/runtime capability;
- `CONTENT`: contributed text, media, code, datasets with provenance;
- `OBSERVATION`: explicitly shared sensors or measurements;
- `DISCOVERY`: opted-in surface monitoring / mention events;
- `INTRODUCTION`: bounded referral or introduction permission;
- `SERVICE`: API/tool/app capability;
- `FUNDING`: separately authorized financial support.

Financial, credential, secret, private-message, sensitive-personal-data, actuator, and security capabilities MUST NOT be bundled into ordinary recommended defaults.

## Recommended defaults

A UI MAY present recommended default grants because making humans configure 43 toggles before they can say hello is how software loses wars against paper.

Recommended defaults SHOULD favor low-risk, reversible contribution modes, for example:

- receive public project updates;
- allow CoCivia to answer when directly invoked on an opted-in surface;
- permit bounded public feedback/review requests;
- contribute explicitly submitted public artifacts under their stated license;
- allow local, user-started canaries with visible resource caps.

Recommended defaults MUST NOT silently activate:

- private-message ingestion;
- broad contact harvesting;
- background device compute;
- continuous microphone/camera/sensor access;
- credential access;
- financial transfers;
- autonomous external posting;
- unrestricted data retention;
- cross-service identity correlation.

`RECOMMENDED_DEFAULT_NE_PREAUTHORIZED_EFFECT`

`ONE_CLICK_OPT_IN_NE_OPAQUE_BUNDLE`

## Resource field

Active grants form a candidate `CoResourceField+`.

The field is not merely a scalar pool. Each resource retains:

- owner / steward;
- authority boundary;
- capability vector;
- availability;
- locality;
- failure domain;
- privacy;
- cost / energy;
- current load;
- revocation state;
- evidence quality;
- provenance.

A scheduler may route eligible work only through resources whose grants cover the exact action.

`RESOURCE_AVAILABLE_NE_RESOURCE_ELIGIBLE`

`RESOURCE_ELIGIBLE_NE_SELECTED`

`SELECTED_NE_AUTHORITY_TRANSFER`

## Growth

More valid opt-ins can increase:

- parallel compute;
- geographic and network diversity;
- model/runtime diversity;
- review capacity;
- translation/localization;
- archival redundancy;
- failure-domain diversity;
- issue discovery;
- public correspondence coverage;
- community moderation;
- accessibility support;
- research breadth;
- cold-start/recovery options.

But additional resources also create coordination, privacy, currentness, trust, attack-surface, and compaction costs.

`MORE_RESOURCES_NE_MORE_PROGRESS`

`MORE_PARTICIPANTS_NE_MORE_TRUTH`

`RESOURCE_GROWTH_REQUIRES_COORDINATION_GROWTH`

## Authority and fairness

Contribution does not purchase truth, rank, governance power, or privileged access.

`RESOURCE_CONTRIBUTION_NE_GOVERNANCE_AUTHORITY`

`COMPUTE_CONTRIBUTION_NE_VOTING_POWER`

`FUNDING_NE_TRUTH_WEIGHT`

`POPULARITY_NE_CANON`

Scheduling SHOULD avoid creating a de facto oligarchy in which the largest compute/storage donors control what the system can see or decide.

Where practical, route for diversity of failure domain and ownership rather than raw capacity alone.

## Consent lifecycle

Candidate grant states:

`OFFERED -> REVIEWED -> ACTIVE -> PAUSED -> REVOKED -> EXPIRED`

A referral may create an `OFFERED` candidate grant but never an `ACTIVE` grant.

`REFERRAL_NE_RESOURCE_GRANT`

Revocation SHOULD stop future use for that scope as quickly as technically feasible and record what already occurred.

`REVOCATION_NE_HISTORY_ERASURE`

`REVOKED_NE_FUTURE_USE_ALLOWED`

## Resource receipts

Every material resource use SHOULD bind:

- grant ID;
- exact resource;
- action;
- start/end;
- quantity;
- output/artifact;
- privacy class;
- authority/effect ceiling;
- failure/partial-completion state;
- receiver/readback where relevant.

`RESOURCE_USE_NE_UNRECEIPTED_BACKGROUND_ACTIVITY`

## Relation to CoCivia ambient correspondence

CoCivia may draw on the Resource Field only when a correspondence event and a valid contribution grant both allow it.

Examples:

- opted-in translator helps answer a multilingual thread;
- opted-in local model generates a private draft locally;
- volunteered reviewer checks a response before release;
- opted-in storage retains a public artifact mirror;
- opted-in mention monitor forwards a relevant event.

A mention alone never activates a participant's devices or data.

`MENTION_NE_RESOURCE_WAKE`

`CORRESPONDENCE_AUTHORITY_NE_RESOURCE_AUTHORITY`

## First safe materialization

The first executable canary SHOULD remain synthetic or repository-local and prove:

1. a visible recommended grant is not active before explicit acceptance;
2. accepted low-risk grants become eligible;
3. private compute remains unavailable without explicit compute grant;
4. referrals remain offered/inactive;
5. revocation removes future eligibility;
6. contribution size does not change governance authority.

No device, financial, credential, private-message, or sensor resource is activated by R0.
