# CoDependency Census / Triple-Loss Resilience R0

**State:** `CANDIDATE_DEPENDENCY_CENSUS__NO_LIVE_X2_OR_ACCOUNT_STATE_CLAIM`

## Purpose

The useful exit question is not merely "can one provider be removed?"

It is:

> Which capabilities disappear if several important embodiments fail at once?

R0 therefore models three simultaneous-loss scenarios:

- provider-chat loss;
- X2/local-site loss;
- GitHub loss.

The census is repository-evidence-based. It does **not** claim a live X2 inventory, a complete account census, current offsite custody, or current runtime adoption.

`DOCUMENTED_DEPENDENCY_NE_LIVE_DEPENDENCY_PROOF`

## Current documented roles

### Provider chat

Documented comparative advantages include interactive reasoning, interpretation, synthesis, challenge and provider-native conversation surfaces.

But current architecture already states:

`PROVIDER_SESSION_NE_CONTROL_PLANE`

and model/account memory is not source of truth.

Therefore loss of provider chat should degrade a reasoning/interaction route, not destroy project identity.

### X2 / local site

Main documents describe X2/local nodes as preferred sites for private execution, deterministic work, local-model materialization, receipts, and local UX.

However the local-model adapter is still documented as:

`ADAPTER_READY__OLLAMA_CANARY_NOT_YET_RUN_ON_X2`

Therefore current local/open-model substitution is not assumed proven.

A local-site loss may remove private execution capacity and private custody access unless independently replicated elsewhere.

### GitHub

GitHub is explicitly the elected shared **public/currentness/bootstrap surface**.

It is also explicitly **not** the sole custody root.

Therefore GitHub loss currently threatens public bootstrap, public source collaboration, CI, PR lineage and shared public currentness more strongly than project identity itself.

`GITHUB_NE_CUSTODY_ROOT`

## Triple-loss test

A critical capability is a continuity defect when all three of these losses leave no independently proven reconstruction route:

```text
provider chat unavailable
AND X2/local site unavailable
AND GitHub unavailable
-> capability unavailable with no independent receiver/custody path
```

This does not require every capability to survive unchanged. It requires the minimum continuity kernel to survive:

- project/work identity;
- authority boundaries;
- private essential state;
- public/current frontier or reconstruction recipe;
- provenance;
- successor/recovery instructions;
- human-readable recovery path.

`CAPABILITY_DEGRADATION_NE_CONTINUITY_FAILURE`

## R0 evidence-class census

| Capability | Provider loss | X2/site loss | GitHub loss | Independent route currently documented? | R0 disposition |
|---|---|---|---|---|---|
| Interactive provider reasoning | LOST/DEGRADED | AVAILABLE | AVAILABLE | Alternative models conceptually yes, live substitution unproven | GAP |
| Public bootstrap/currentness | AVAILABLE | AVAILABLE | LOST | No independent public mirror proven here | GAP |
| Public source/PR/CI lineage | AVAILABLE | AVAILABLE | LOST | No second host proven here | GAP |
| Private durable custody | AVAILABLE | LOST/UNKNOWN | AVAILABLE | Offsite private custody is architectural target, live proof absent here | GAP |
| Local deterministic execution | AVAILABLE | LOST | AVAILABLE | Other routes conceptually possible | DEGRADED |
| Local/open-model execution | AVAILABLE | LOST | AVAILABLE | X2 canary itself unproven | UNPROVEN |
| Human-readable recovery | AVAILABLE | DEGRADED | DEGRADED | Required by exit policy, concrete independent artifact not proven here | GAP |
| Authority model / semantic doctrine | AVAILABLE | AVAILABLE | LOST/DEGRADED | Recoverable if copies exist elsewhere, independent exact copy not proven here | GAP |
| CoBar/RickBar UX | AVAILABLE | LOST/DEGRADED | AVAILABLE | UX is nonessential by doctrine | NONCRITICAL |
| Provider-session history | LOST | AVAILABLE | AVAILABLE | Explicitly nonessential to continuity | NONCRITICAL |

The table is a bounded architecture census, not a live infrastructure audit.

## Highest-value gaps

R0 identifies five priority continuity gaps:

1. **Independent public/bootstrap mirror** outside GitHub.
2. **Independently proven private/offsite custody** outside the local site.
3. **Provider-independent reasoning/model route** with receiver readproof.
4. **Human-readable offline recovery packet** that does not require GitHub, ChatGPT or X2.
5. **Second source/provenance host or export bundle** sufficient to reconstruct public lineage after GitHub loss.

The aim is not to duplicate the entire project everywhere. It is to preserve a minimal continuity kernel plus reconstruction paths.

`REPLICA_NE_FULL_DUPLICATION_REQUIREMENT`

## Recovery kernel

Candidate minimum recovery kernel:

`identity + authority + provenance + current frontier + private-state pointers + public-state pointers + reconstruction recipes + exception register + human instructions`

A recovery kernel should be small enough to replicate across several genuinely independent domains.

`RECOVERY_KERNEL_NE_FULL_PROJECT_COPY`

## Rails

`DOCUMENTED_DEPENDENCY_NE_LIVE_DEPENDENCY_PROOF`  
`PROVIDER_SESSION_NE_CONTROL_PLANE`  
`GITHUB_NE_CUSTODY_ROOT`  
`LOCAL_DEVICE_NE_CUSTODY_ROOT`  
`CAPABILITY_DEGRADATION_NE_CONTINUITY_FAILURE`  
`REPLICA_NE_FULL_DUPLICATION_REQUIREMENT`  
`RECOVERY_KERNEL_NE_FULL_PROJECT_COPY`  
`COPY_COUNT_NE_FAILURE_DOMAIN_COUNT`  
`VALIDATION_IS_NOT_ACCEPTANCE`
