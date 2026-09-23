# CoFront+ GitHub App / Service-Principal Materialization R1

**State:** `DESIGN_READY__NO_GITHUB_APP_CREATED__NO_CREDENTIAL_MATERIALIZED`

## Lead

CoCivia already exists as a disclosed CoFront+ object. R1 defines the first safe path from that identity projection to an independently auditable GitHub **seat** without pretending the seat is the identity itself.

`CoCivia front -> scoped GitHub App/service principal -> one-repository canary -> exact effect receipt -> receiver verification`

R1 performs **no** GitHub App registration, installation, credential creation, token issuance, organization conversion, or permission grant.

## Why a service principal before another human-style account

The first machine seat should be:

- explicitly non-human;
- repository-scoped;
- revocable independently of a person's login;
- short-lived-token capable;
- auditable by installation/actor identity;
- replaceable without changing the CoCivia front contract;
- unable to inherit broad authority merely because the front represents CoAll.

`SEAT_NE_IDENTITY`  
`SERVICE_PRINCIPAL_NE_PERSONHOOD`

## Phase gates

### P0 — design only

Current state.

- front identity exists;
- desired seat class is GitHub App/service principal;
- no credential exists;
- no platform installation exists;
- no effect authority is granted.

### P1 — read-only installation canary

Requires an explicit platform/admin action outside this repository.

Initial installation scope:

- repository: `CoCivium/CoCivium` only;
- repository metadata: read;
- contents: read;
- all organization administration: none;
- secrets/actions/workflows/environments/members/billing: none.

Proof target:

`APP_IDENTITY_BOUND + INSTALLATION_SCOPE_BOUND + READ_ONLY_CURRENT_HEAD_READBACK`

P1 does not authorize mutation.

### P2 — one bounded draft-PR effect canary

Only after P1 proof and a separate authority gate.

Temporarily add only the minimum write permissions required to:

1. create a uniquely named canary branch;
2. add one public-safe proof object under a pre-elected canary path;
3. open one **draft** pull request;
4. perform no merge;
5. mutate no other repository.

The effect must be protected by:

- one bounded effect lease;
- expected-current-head precondition;
- no-clobber path;
- exact commit and blob readback;
- receipt identifying the actual GitHub App/service-principal actor;
- rollback/branch-delete eligibility recorded but not automatically executed.

`DRAFT_PR_NE_MERGE_AUTHORITY`

### P3 — receiver verification

A distinct receiver verifies:

- exact actor/installation identity;
- exact branch;
- exact commit SHA;
- exact blob SHA;
- exact draft PR identity;
- permission scope did not exceed the elected canary;
- no unrelated effects occurred.

Only that bounded canary may advance to `PICKED_UP`/accepted seat evidence.

## Credential contract

Credential material must never be committed to GitHub or embedded in public CoPulse objects.

Repository objects may contain only opaque references such as:

- app identifier;
- installation identifier;
- secret-manager handle;
- token expiry metadata;
- key/version fingerprint where safe.

Never contain:

- private keys;
- installation tokens;
- client secrets;
- recovery secrets.

`SECRET_HANDLE_NE_SECRET_VALUE`

## Horde rule

A large ecology of CoFront+ objects does **not** imply a large ecology of vendor accounts.

Many virtual/specialist fronts may share one properly disclosed service seat when their permission/audit boundary is the same.

Materialize another seat only when a distinct credential, permission, failure-domain, audit, or collaboration boundary justifies it.

`FRONT_COUNT_NE_ACCOUNT_COUNT`

## CoAll relation

A front may act `project_for -> CoAll`, but its seat authority remains the intersection of:

`delegated authority ∩ installation permissions ∩ effect lease ∩ confidentiality ∩ collision/currentness gates`

Representation never amplifies authority.

`REPRESENTATIVE_NE_PRINCIPAL`  
`AGENT_OF_NE_AUTHORIZED_FOR_ALL_EFFECTS`

## Human/admin gate

Creating or installing the GitHub App is a platform/credential/security mutation and therefore remains a human/admin gate.

Broad prior delegation to evolve CoAll does not silently create new credential principals.

`DELEGATION_NE_CREDENTIAL_CREATION_AUTHORITY`

## Current next action

Wait until an authorized human/admin elects to materialize the service principal. At that point execute P1 only: one-repository read-only identity/scope/readback proof.

No human action is required merely to keep evolving virtual fronts, schemas, subscriptions, or non-effectful CoAll work.

## Rails

`PRINCIPAL_NE_SHELL_NE_SEAT`  
`SEAT_NE_IDENTITY`  
`SERVICE_PRINCIPAL_NE_PERSONHOOD`  
`FRONT_COUNT_NE_ACCOUNT_COUNT`  
`SECRET_HANDLE_NE_SECRET_VALUE`  
`DRAFT_PR_NE_MERGE_AUTHORITY`  
`REPRESENTATIVE_NE_PRINCIPAL`  
`AGENT_OF_NE_AUTHORIZED_FOR_ALL_EFFECTS`  
`DELEGATION_NE_CREDENTIAL_CREATION_AUTHORITY`
