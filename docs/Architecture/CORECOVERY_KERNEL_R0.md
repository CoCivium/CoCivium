# CoRecoveryKernel+ Minimal Continuity Packet R0

**State:** `CANDIDATE_MINIMAL_RECOVERY_KERNEL__NO_LIVE_REPLICA_OR_OFFSITE_CUSTODY_CLAIM`

## Purpose

A resilient CoAll should not require the full project, a provider transcript, a particular workstation, or a repository host merely to know what it is and how to continue safely.

R0 therefore defines a **minimal recovery kernel**: the smallest bounded set of information needed to reconstruct orientation, authority, provenance and the current continuation frontier after major route loss.

This is not a full backup.

`RECOVERY_KERNEL_NE_FULL_PROJECT_COPY`

`BOOTSTRAP_SUFFICIENCY_NE_FULL_STATE_REPLICATION`

## Required kernel sections

A candidate kernel contains:

1. **Identity**
   - project/system identity;
   - kernel version;
   - creation time;
   - source lineage.

2. **Authority**
   - default authority ceiling;
   - destructive/public/financial/security boundaries;
   - revocation and escalation rules.

3. **Current frontier**
   - bounded current work heads;
   - unresolved blockers;
   - wake conditions;
   - explicit stale/unknown markers.

4. **Provenance**
   - source object identifiers;
   - content hashes where available;
   - previous-kernel pointer;
   - reconstruction evidence.

5. **Custody pointers**
   - public-safe source pointers;
   - private-state pointers that reveal no private payload;
   - offsite or alternate-route pointers when actually proven.

6. **Reconstruction recipe**
   - how to recover public/bootstrap state;
   - how to recover private state;
   - how to rebind an authorized execution route;
   - how to verify exactness;
   - how to stop if evidence is incomplete.

7. **Exception register**
   - provider-only dependencies;
   - local-only dependencies;
   - host-only dependencies;
   - unavailable credentials/capabilities;
   - unproven assumptions.

8. **Human-readable fallback**
   - plain-language description of what CoAll is;
   - what must not be inferred;
   - first safe recovery actions;
   - explicit "do not guess" conditions.

`UNKNOWN_NE_FILL_WITH_GUESS`

## Three-domain survivability

The kernel SHOULD be representable in at least three materially distinct continuity domains, for example:

- local/private durable custody;
- independent offsite/private custody;
- public-safe or human-readable offline copy.

The domains must not silently collapse onto one shared failure root.

`THREE_COPIES_NE_THREE_FAILURE_DOMAINS`

`SAME_SITE_NE_INDEPENDENT_DOMAIN`

`SAME_CREDENTIAL_ROOT_NE_INDEPENDENT_DOMAIN`

R0 validates the representation and failure-domain declaration only. It does not claim that three live replicas exist today.

## No-secret public projection

A public or printed recovery projection MUST NOT contain:

- passwords;
- API keys;
- bearer tokens;
- private keys;
- recovery codes;
- private payloads;
- unnecessary personal data.

It may contain opaque private-custody pointers, hashes and instructions that require separately held credentials.

`RECOVERY_PACKET_NE_SECRET_DUMP`

## Reconstruction proof ladder

Candidate proof ladder:

`STRUCTURAL_VALID`
-> `SELF_CONTAINED_ORIENTATION`
-> `SOURCE_HASH_VERIFIED`
-> `INDEPENDENT_READER_RECONSTRUCTED_FRONTIER`
-> `PRIVATE_POINTER_RESOLVED_ON_AUTHORIZED_ROUTE`
-> `SECOND_FAILURE_DOMAIN_READPROOF`
-> `THIRD_FAILURE_DOMAIN_READPROOF`
-> `PROVIDER_ACCOUNT_NOT_REQUIRED`
-> `PRIMARY_LOCAL_SITE_NOT_REQUIRED`
-> `PRIMARY_GIT_HOST_NOT_REQUIRED`

No higher rung is inferred from a lower one.

`STRUCTURAL_PASS_NE_RECOVERY_PROOF`

## Human fallback

The human-readable section must be sufficient for a technically competent person who has no chat history to answer:

- what system this is;
- what the current bounded frontier is;
- which source is authoritative for which kind of state;
- what actions are forbidden without separate authority;
- where private and public state should be sought;
- what failures are known;
- what the first safe verification step is.

It should not require memorizing CoTerms to avoid catastrophe. Civilization has enough escape rooms already.

`HUMAN_RECOVERY_NE_ONTOLOGY_EXAM`

## First canary

The synthetic fixture proves:

1. all required sections exist;
2. destructive authority remains false;
3. public projection contains no secret-bearing fields;
4. three declared copies are rejected when they share one failure domain;
5. a valid three-domain declaration can be represented;
6. unknown pointers remain explicit rather than guessed;
7. human fallback includes first-safe-step and stop conditions;
8. structural validity does not claim live offsite custody or independent reconstruction.

## Rails

`RECOVERY_KERNEL_NE_FULL_PROJECT_COPY`  
`BOOTSTRAP_SUFFICIENCY_NE_FULL_STATE_REPLICATION`  
`UNKNOWN_NE_FILL_WITH_GUESS`  
`THREE_COPIES_NE_THREE_FAILURE_DOMAINS`  
`SAME_SITE_NE_INDEPENDENT_DOMAIN`  
`RECOVERY_PACKET_NE_SECRET_DUMP`  
`STRUCTURAL_PASS_NE_RECOVERY_PROOF`  
`HUMAN_RECOVERY_NE_ONTOLOGY_EXAM`  
`ACCOUNT_RETIREMENT_REQUIRES_EXPLICIT_AUTHORITY`  
`VALIDATION_IS_NOT_ACCEPTANCE`
