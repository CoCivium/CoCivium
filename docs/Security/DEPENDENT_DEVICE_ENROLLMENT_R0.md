# Dependent / Minor Device Enrollment R0

**State:** `POLICY_LANDED__NO_DEPENDENT_DEVICE_ENROLLMENT_AUTHORIZED_BY_THIS_DOCUMENT`

## Lead

A dependent/minor participant may have a device connected to CoCivium infrastructure, but the connection must not be implemented by sharing or reusing the participant's personal Windows/account credentials, nor by giving CoAll a standing unrestricted remote-control path.

Preferred pattern:

`participant-owned identity -> device enrollment identity -> scoped capability broker -> guardian/admin policy -> local consent gate where appropriate -> audited bounded effects`

## Current default

Do **not** create an unattended full-control AI endpoint merely because a connector supports it.

Before enrollment, prove the adult/primary X2 route first:

1. device identity and reconnect behavior;
2. scoped command/capability boundaries;
3. audit/receipt path;
4. emergency kill/disable path;
5. failure-to-Windows/local-control recovery;
6. credential isolation;
7. session/lease expiry;
8. local confirmation behavior for interactive/private actions.

`PRIMARY_ROUTE_FIRST__DEPENDENT_ENDPOINT_SECOND`

## Identity

The participant keeps their own OS/user identity.

CoCivium should use a distinct machine/service enrollment identity.

`DEVICE_SERVICE_ID_NE_PERSONAL_LOGIN`  
`NO_SHARED_PERSONAL_CREDENTIALS`

The service identity must be individually revocable and must not imply authority over every account, file, browser session, microphone, camera, message surface, or peripheral on the machine.

## Authority

Guardian/admin authority may permit configuration and safety maintenance, but:

`GUARDIAN_AUTHORITY_NE_UNATTENDED_AI_CONTROL`

CoAll/model/agent processes receive only explicitly delegated capabilities.

`MODEL_NE_AUTHORITY`  
`SERVICE_PRINCIPAL_NE_PERSONHOOD`  
`CAPABILITY_NE_AUTHORITY`

## Consent / presence

Interactive control while the participant is actively using the device should default to visible/local confirmation.

Privacy-sensitive actions should require a stronger local/guardian gate, such as:

- opening private files;
- reading personal messages/accounts;
- camera/microphone use;
- credential/security settings;
- browser account/session access;
- screen capture outside a bounded support session.

Routine non-sensitive maintenance may later be delegated under an explicit maintenance policy with finite lease and auditable receipts.

`VISIBLE_SUPPORT_NE_HIDDEN_SURVEILLANCE`

## Remote-control modes

Candidate modes, ordered from safer to more powerful:

- `OBSERVE_DEVICE_HEALTH`
- `RUN_BOUNDED_DIAGNOSTIC`
- `APPLY_PREAPPROVED_MAINTENANCE`
- `INTERACTIVE_SUPPORT_WITH_LOCAL_CONFIRMATION`
- `GUARDIAN_EMERGENCY_OVERRIDE`

Standing unrestricted remote desktop is not the default mode.

## Emergency / recovery

The participant/guardian must retain a simple local way to:

- disconnect the service;
- revoke the device token;
- stop the local broker;
- return to ordinary local control;
- inspect recent actions.

If the CoCivium layer fails, the device must remain normally usable.

`COCIVIUM_FAILURE_MUST_NOT_LOCK_OUT_LOCAL_USER`

## Enrollment gate

A dependent/minor endpoint is eligible for enrollment only after:

- the primary X2 path has a proven bounded pilot;
- the service identity is separate from personal credentials;
- command/effect scope is explicit;
- audit/receipts are durable;
- local stop/recovery is tested;
- consent/guardian policy is encoded;
- no hidden surveillance capability is enabled by default.

## Nonclaims

This policy does not prove:

- any dependent device is currently enrolled;
- any participant has consented to remote control;
- any connector supports the required consent gates;
- any unattended maintenance policy has been approved;
- any child/minor-specific legal requirement is fully satisfied.

## Rails

`PRIMARY_ROUTE_FIRST__DEPENDENT_ENDPOINT_SECOND`  
`DEVICE_SERVICE_ID_NE_PERSONAL_LOGIN`  
`NO_SHARED_PERSONAL_CREDENTIALS`  
`GUARDIAN_AUTHORITY_NE_UNATTENDED_AI_CONTROL`  
`MODEL_NE_AUTHORITY`  
`VISIBLE_SUPPORT_NE_HIDDEN_SURVEILLANCE`  
`COCIVIUM_FAILURE_MUST_NOT_LOCK_OUT_LOCAL_USER`
