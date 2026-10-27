# Improvement Club Kit R0

**State:** PUBLIC_SAFE_TEMPLATE__NO_PLATFORM_CLUB_CREATED  
**Purpose:** help a voluntary community improve a product, platform, protocol or shared system through transparent, reproducible experiments.

## 1. Name

Use a descriptive name such as:

`[Platform/Product] Improvement Club`

If the club is not operated by the platform/product owner, state that clearly.

Example:

> Independent, unofficial community for finding, testing and documenting ways to improve [Platform] for users, moderators, developers and accessibility.

## 2. Disclosure

Required front-door disclosure:

- who runs/moderates the club;
- whether it is official or unofficial;
- material affiliations;
- whether CoCivium methods/tools are being used;
- how evidence is stored;
- how participants can leave, fork or challenge the process.

Do not disguise a CoCivium adoption funnel as a neutral community.

`TRANSPARENT_AGENDA_NE_COVERT_PERSUASION`

## 3. Participation rule

Participation is voluntary.

Do:
- invite people who have relevant interest;
- make the purpose clear before they join;
- allow criticism and competing methods;
- allow people to leave without penalty;
- preserve attribution and privacy choices.

Do not:
- mass-invite uninterested users;
- imply platform endorsement;
- create fake grassroots support;
- hide sponsorship or control;
- pressure participants to adopt CoCivium or any other tool.

`IMPROVEMENT_CLUB_NE_ASTROTURF`

## 4. Improvement experiment template

### Problem

What user/system problem is being observed?

### Receiver

Who experiences it?

### Current evidence

What observable source supports the problem statement?

### Candidate improvement

What small change might help?

### Baseline

What happens without the change?

### Test

What bounded experiment can distinguish improvement from noise?

### Success criteria

What exact observable result would count as improvement?

### Failure / null

What result would show no improvement or harm?

### Privacy / authority

What data/actions are allowed? What is explicitly out of scope?

### Recovery / rollback

How is the experiment reversed or abandoned?

### Result

`PASS / FAIL / HELD / UNKNOWN`

### Evidence

Links, hashes, screenshots, receipts, measurements or participant feedback as appropriate.

### Return

What should change in the platform, club method, or shared protocol because of this result?

## 5. Evidence receipt template

```json
{
  "schema": "ImprovementClub.ExperimentReceipt.R0",
  "experiment_id": "...",
  "observed_at": "...",
  "problem": "...",
  "receiver": "...",
  "baseline": "...",
  "candidate": "...",
  "result": "PASS|FAIL|HELD|UNKNOWN",
  "evidence_refs": [],
  "privacy": "...",
  "authority": "...",
  "rollback": "...",
  "returned_delta": "...",
  "nonclaims": []
}
```

## 6. Challenge path

Every club should make it easy to say:

- this problem is misdiagnosed;
- this experiment is biased;
- this evidence is weak;
- a simpler solution exists;
- a competing tool works better;
- the club itself is creating harm or noise.

Challenges should be logged and either:
- accepted;
- rejected with reason;
- held pending evidence;
- converted into a competing experiment.

## 7. Exit / fork path

Participants should be able to:
- leave;
- export their own contributions where permitted;
- fork public methods/templates;
- run independent experiments;
- use competing communities or tools.

No contribution implies endorsement of CoCivium, the platform owner, or other participants.

## 8. Moderation minimum

Moderation should optimize:
- relevance;
- evidence;
- respectful disagreement;
- accessibility;
- anti-spam;
- privacy;
- correction visibility.

Do not optimize for:
- engagement volume;
- outrage;
- follower count;
- performative consensus.

## 9. Platform adapters

### X Communities

Use the host's Community roles and rules. Keep the club unofficial unless formally accepted. Do not use mass invitation waves. Community posts may be publicly visible outside the membership boundary.

### Bluesky

Use Starter Packs and custom feeds as optional discovery/onboarding primitives. Keep the evidence/method home portable outside any one feed.

### Reddit

Use a narrowly scoped community purpose, explicit rules and moderator practices. Check for an existing community before creating another.

### GitHub Discussions

Use Discussions for open-ended questions, proposals and feedback; move sufficiently scoped work into issues/PRs. Keep source/evidence close to the implementation.

## 10. Club health metrics

Track:
- qualified participants;
- first useful contribution;
- time to first independent experiment;
- evidence rate;
- failure retention rate;
- receiver-return rate;
- independent reproductions;
- human relay minutes;
- moderation burden;
- leave friction;
- cross-platform portability.

Do not use raw member count as the primary success metric.

`MEMBERS_NE_USEFULNESS`

## 11. First-use script

1. State the problem in plain language.
2. Show one small experiment.
3. Show the evidence.
4. Ask for a challenge, reproduction or alternative.
5. Record the return.
6. Update the shared method only if the evidence warrants it.

No CoCivium vocabulary is required for participation.

## 12. Rails

`TRANSPARENT_AGENDA_NE_COVERT_PERSUASION`  
`IMPROVEMENT_CLUB_NE_ASTROTURF`  
`OUTREACH_NE_SPAM`  
`MARKETING_NE_MANIPULATION`  
`RECEIVER_NE_TARGET`  
`MEMBERS_NE_USEFULNESS`  
`SENT_NE_DELIVERED`  
`DELIVERED_NE_UNDERSTOOD`  
`UNDERSTOOD_NE_USED`  
`USED_NE_RETURNED_DELTA`
