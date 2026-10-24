# CoMutualAidGame+ Offline Participation / Human Relay R0

**State:** `SYNTHETIC_OFFLINE_PARTICIPATION_CANARY__NO_REAL_EMERGENCY_NO_PUBLIC_DEPLOYMENT`

## Purpose

Make device-less humans first-class participants in CoMutualAidGame+ rather than treating connectivity as citizenship.

The candidate relation is:

```text
person
-> consented role
-> observation / need / offer
-> human or physical relay
-> typed message
-> dedupe / privacy / authority checks
-> simulation coordination
```

A phone, laptop, account, model, or central server may help, but none is the definition of participation.

`DEVICE_NE_PARTICIPATION_REQUIREMENT`

## Offline relay forms

R0 allows synthetic routing through:

- human verbal relay;
- printed card;
- community noticeboard;
- simulated telephone tree;
- simulated radio relay;
- ordinary digital message when available.

The route may cross digital and non-digital segments.

A participant with no device can originate a valid message if consent, purpose, privacy class and authority ceiling remain bound through the relay.

## Typed message

Every relayed object carries:

```text
message_id
scenario_id
origin_participant_id
purpose
privacy_class
consent_snapshot
payload
authority_ceiling
```

This turns "somebody told somebody" into a reconstructible relation without pretending every oral interaction can be perfectly captured.

## Eight bounded cases

R0 proves synthetically:

1. a device-less participant can report through a human relay;
2. a printed-card route still works when the digital path is unavailable;
3. two relay paths for the same message dedupe to one simulated delivery;
4. referring another person creates only an invitation offer, not enrolment;
5. a revoked participant is no longer routed;
6. repeated cooperation can create a social/friendship candidate relation but no friendship obligation or access right;
7. a simulated dispatcher cannot acquire real emergency-service authority;
8. a private simulated payload is held when the available relay is public.

## Friendship and community

Repeated useful cooperation can generate:

```text
FAMILIAR_WITH
TRUST_CANDIDATE
WOULD_WORK_WITH_AGAIN
LOCAL_GROUP_CANDIDATE
MENTORSHIP_CANDIDATE
FRIENDSHIP_CANDIDATE
```

These relations remain optional and independently consented.

They do not grant private contact details, social access, ranking power, emergency authority, or automatic matching.

`COOPERATION_NE_FRIENDSHIP_OBLIGATION`

`HELP_HISTORY_NE_PERSONAL_ACCESS_RIGHT`

## Referral

A participant may say:

> D might enjoy the next exercise.

That creates an invitation candidate only.

It does not enrol D, wake D's devices, expose D's information, or authorize CoAll to contact D through some unrelated surface.

`REFERRAL_NE_ENROLMENT`

## Failure tolerance

An offline route is useful partly because failures differ.

The target ecology may eventually mix:

- local humans;
- printed packets;
- community hubs;
- low-bandwidth radio/text;
- open-source local models;
- public internet services;
- delayed store-and-forward synchronization.

Copies are useful, but genuinely different failure domains matter more than copy count.

## Emergency boundary

This remains a game/simulation fabric.

It does not dispatch people, replace emergency services, issue evacuation orders, impersonate credentialed responders, or authorize entry into danger.

Future real-event modes would require their own jurisdiction, credential, safety, privacy and authoritative-source gates.

## What else this unlocks

If this pattern survives larger canaries, a global mutual-aid ecology can include people who are:

- offline;
- temporarily without power;
- unable to use conventional apps;
- working through a trusted local facilitator;
- communicating asynchronously;
- contributing local knowledge rather than compute;
- contributing translation, verification, physical observation or neighbour awareness.

That matters for resilience and fairness. A global coordination fabric that disappears when somebody loses a smartphone is not especially global.

## Current boundary

No real participant is enrolled.

No real emergency is acted upon.

No public message is sent.

No device or account is connected.

No friendship/contact relationship is created.

No external effect is performed.

## Rails

`DEVICE_NE_PARTICIPATION_REQUIREMENT`  
`CENTRAL_SERVER_NE_GAME_CONTINUITY_ROOT`  
`OFFLINE_NE_NONPARTICIPANT`  
`REFERRAL_NE_ENROLMENT`  
`COOPERATION_NE_FRIENDSHIP_OBLIGATION`  
`HELP_HISTORY_NE_PERSONAL_ACCESS_RIGHT`  
`SIMULATED_ROLE_NE_REAL_CREDENTIAL`  
`HELP_OFFER_NE_COMMAND_AUTHORITY`  
`DUPLICATE_ROUTE_NE_DUPLICATE_DISPATCH`  
`CONSENT_REVOKED_NE_FUTURE_ROUTING_ALLOWED`  
`SIMULATION_NE_REAL_EMERGENCY`  
`VALIDATION_IS_NOT_ACCEPTANCE`
