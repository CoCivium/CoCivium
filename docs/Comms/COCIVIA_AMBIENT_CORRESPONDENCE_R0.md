# CoCivia Ambient Correspondence R0

**State:** `CANDIDATE__DESIGN_AND_POLICY_ONLY__NO_EXTERNAL_AUTOREPLY_AUTHORITY`

## Purpose

CoCivia may eventually maintain a consent-aware ambient presence across adjacent communication surfaces, noticing relevant mentions and participating where the surface, relationship, receiver, and effect authority permit it.

The intended pattern is not "crawl the internet and inject CoCivia everywhere." It is:

`authorized surface -> mention/event -> relational qualification -> consent/effect check -> observe/draft/respond/hold -> receipt`

CoCivia remains a disclosed composite front.

`COCIVIA_FRONT_NE_HUMAN_PRINCIPAL`

## Trigger field

Candidate lexical triggers MAY include:

- `CoCivia`
- `CoCivium`
- `CoAll`
- registered CoFront names
- explicitly registered CoTerms
- relation-specific aliases or tags
- direct replies to a CoCivia-authored object
- explicit @mention or invocation
- opted-in thread subscriptions
- referral objects that create a candidate relationship edge

A trigger is only a routing hint.

`TRIGGER_WORD_NE_INVITATION`

`MENTION_NE_CONSENT`

`PUBLIC_POST_NE_REPLY_PERMISSION`

## Surfaces

Each monitored surface MUST have a machine-readable surface contract with:

- `surface_id`
- provider / transport
- read authority
- write authority
- installation / account / seat identity
- participant consent model
- thread visibility
- retention policy
- rate / anti-spam limits
- disclosure requirement
- effect ceiling
- revocation path
- provenance / receipt capability

Examples may eventually include GitHub discussions/issues/PRs, an opt-in forum, a project site, a community chat, a webhook-enabled partner surface, or future CoAll-native surfaces.

No surface is considered writable merely because it is publicly readable.

`READABLE_NE_WRITABLE`

`CONNECTED_NE_AUTHORIZED_TO_ENGAGE`

## Relationship and consent state

A mention event is qualified against relationship state.

Candidate relationship states:

- `NONE`
- `OBSERVABLE_PUBLIC`
- `REFERRED_CANDIDATE`
- `OPTED_IN_TO_LISTENING`
- `OPTED_IN_TO_CONTEXTUAL_REPLY`
- `DIRECTLY_INVITED`
- `ACTIVE_THREAD_PARTICIPANT`
- `MUTED`
- `REVOKED`

A referral by Alice about Bob does not confer Bob's consent.

`REFERRAL_NE_THIRD_PARTY_CONSENT`

A referral MAY create a bounded candidate edge that permits passive discovery or preparation of an introduction, subject to the destination surface's rules and a separate consent/authority decision.

## Action modes

For every qualified event, CoCivia elects one action mode:

1. `IGNORE` - irrelevant, duplicate, disallowed, muted, or below threshold.
2. `OBSERVE_ONLY` - retain bounded metadata/provenance, no reply.
3. `DRAFT_ONLY` - compose a candidate response but create no external effect.
4. `RESPOND_IF_EXPLICITLY_INVOKED` - direct mention/reply plus write authority and consent.
5. `RESPOND_IF_RELATIONALLY_OPTED_IN` - standing opt-in covers this surface/thread/category.
6. `ESCALATE_FOR_REVIEW` - ambiguity, sensitivity, contested identity, legal/financial/security/privacy consequence.
7. `BLOCK` - revoked, deceptive, harassing, prohibited, or outside authority.

Default is non-intervention.

`NO_MATCH_NE_NOISE_GENERATION`

`DRAFT_NE_SENT`

`RELATIONSHIP_NE_WRITE_AUTHORITY`

## Correspondence object

A candidate `CoCorrespondenceEvent+` SHOULD bind:

- event ID
- exact surface/thread/message ID
- timestamp/currentness
- trigger terms matched
- semantic relevance score
- source participant identity as represented by the surface
- relationship state
- consent basis
- visibility class
- read/write authority
- chosen action mode
- disclosure text/version
- response object if any
- rate-limit / quiet-mode state
- provenance and receipts
- deduplication key
- revocation / deletion hooks where supported

## Participation style

When authorized to reply, CoCivia should behave like a useful participant, not a brand-surveillance bot.

Prefer:

- answer the actual question;
- disclose CoCivia's nature when material;
- keep first contact brief;
- do not hijack unrelated threads;
- do not manufacture familiarity;
- do not pretend a referral is a personal introduction;
- do not repeat the same pitch across surfaces;
- do not pressure a receiver to continue;
- stop when muted, ignored, or asked to stop.

`RELEVANCE_NE_LICENSE_TO_INTERRUPT`

`REPLY_NE_RECRUITMENT`

`REPETITION_NE_PRESENCE`

## Mention ecology

A richer trigger model should extend beyond exact strings.

Candidate signals:

- direct lexical mention;
- reply-to ancestry;
- semantic reference to a registered CoObject;
- quote / link / citation of a CoCivium artifact;
- registered hashtag or machine-readable relation;
- opted-in referral token;
- thread membership;
- prior explicit invitation;
- follow-up on an unresolved CoCorrespondence object;
- inbound webhook from an authorized adjacent system.

The routing engine should combine signals rather than make exact-keyword surveillance the architecture.

`KEYWORD_MATCH_NE_SEMANTIC_RELEVANCE`

`SEMANTIC_RELEVANCE_NE_REPLY_AUTHORITY`

## Referral objects

A `CoReferral+` SHOULD separate:

- referrer
- referred party
- referred object/topic
- reason/context
- surface
- referrer's authority
- referred party's consent state
- expiry
- allowed next action

Candidate next actions include:

- `DISCOVER_ONLY`
- `WAIT_FOR_INBOUND`
- `INTRODUCTION_DRAFT`
- `INTRODUCTION_ALLOWED`
- `NO_CONTACT`

Default third-party referral action:

`WAIT_FOR_INBOUND` or `DISCOVER_ONLY`.

## Anti-spam and attention rails

The system SHOULD maintain:

- per-person frequency caps;
- per-thread caps;
- cross-surface deduplication;
- quiet periods;
- global anomaly detection;
- receiver-side mute;
- surface-specific policy compliance;
- opt-out memory;
- relevance threshold;
- bounded retry count;
- conversation abandonment after non-response.

`SILENCE_NE_PENDING_OBLIGATION`

`NONRESPONSE_NE_RETRY_PERMISSION`

`MULTI_SURFACE_NE_MULTI_PINGS`

`OPT_OUT_NE_TEMPORARY_HINT`

## Privacy

Passive monitoring itself can create privacy and profiling risk.

Therefore:

- collect the minimum event data required for routing;
- do not build hidden personal dossiers from unrelated public activity;
- do not infer sensitive traits to decide whom to engage;
- separate public-content observation from private/sensitive data;
- respect platform and participant deletion/revocation signals where available;
- make relationship/consent provenance inspectable.

`PUBLICLY_VISIBLE_NE_UNBOUNDED_PROFILE_INPUT`

`OBSERVATION_NE_PERMISSION_TO_PROFILE`

## Authority

R0 creates no new external communication authority.

A future adapter must prove:

`FRONT -> SEAT -> SURFACE -> THREAD -> ACTION -> RECEIPT`

before any autonomous external reply.

Existing CoCivia authority remains advisory and bounded content contribution unless separately delegated.

`AGENT_OF_NE_AUTHORIZED_FOR_ALL_EFFECTS`

`AUTOMATION_NE_CONSENT`

`TRIGGER_NE_AUTHORITY`

## Candidate architecture

```text
surface adapters
      |
      v
CoMentionField+
      |
      v
CoCorrespondenceEvent+
      |
      +--> dedupe/currentness
      +--> relationship lookup
      +--> consent qualification
      +--> authority/effect ceiling
      +--> relevance/context
      +--> quiet/rate policy
      |
      v
CoCorrespondenceRouter+
   |    |      |       |
ignore observe draft respond
                    |
                    v
             effect receipt
                    |
                    v
          CoRelationshipField+
```

Related candidate objects:

- `CoMentionField+`
- `CoCorrespondenceEvent+`
- `CoCorrespondenceRouter+`
- `CoReferral+`
- `CoRelationshipField+`
- `CoInboxField+`
- `CoOutboxField+`
- `CoCommsCurrentness+`
- `CoCrossChannelDedup+`
- `CoQuietMode+`
- `CoCommsQuarantine+`

## First safe materialization

The first executable canary SHOULD use a surface already controlled by CoCivium, such as a repository event stream or dedicated opt-in test thread.

It should prove:

1. exact trigger detection;
2. relationship and consent lookup;
3. duplicate suppression;
4. draft creation;
5. explicit no-send state;
6. one deliberately authorized reply in a synthetic/test context;
7. exact actor/surface/thread/effect receipt;
8. revocation/mute behavior.

No public auto-engagement is authorized by this R0.

`CANARY_REPLY_NE_GENERAL_REPLY_AUTHORITY`

`TEST_THREAD_NE_PUBLIC_SOCIAL_LICENSE`
