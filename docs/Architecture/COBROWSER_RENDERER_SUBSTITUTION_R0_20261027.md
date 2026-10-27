# CoBrowser+ Renderer Substitution + CoRendererLattice R0

**State:** CANDIDATE_ARCHITECTURE__NO_BROWSER_REMOVAL__NO_X2_RUNTIME_CHANGE  
**Observed:** 2026-10-27

## Thesis

CoBrowser continuity should not depend on one vendor browser, one rendering engine, one account, or one visible tab.

The renderer is a replaceable projection substrate.

```
CoWorkObject
-> CoOrb projection
-> CoBrowser continuity shell
-> renderer adapter
-> selected renderer
```

The renderer may change while work identity, provenance, currentness, authority, checkpoint lineage, and recovery remain stable.

`RENDERER_NE_WORK_IDENTITY`
`ENGINE_NE_CONTINUITY_ROOT`

## Initial Windows substrate policy

### Preferred embedded Windows renderer

`WEBVIEW2_EVERGREEN`

Reason:
- mature Windows-native embedding path;
- maintained separately as the WebView2 Runtime;
- automatic Evergreen servicing;
- available across Windows 11;
- can render local or remote web content while CoBrowser retains its own work identity.

This is a renderer substrate, not the CoBrowser identity root.

### Independent-engine continuity canary

`FIREFOX_MANAGED`

Reason:
- independent browser engine family;
- enterprise policy surface;
- useful diversity canary against Chromium-family rendering or compatibility failure.

Current or ESR release may be selected by deployment policy; CoBrowser must not make work identity depend on either release train.

### Compatibility embodiments

Existing Edge/Chrome/other Chromium-family browsers may remain useful for:
- provider compatibility;
- login/session continuity during migration;
- comparison;
- receiver fit;
- site-specific behavior.

They are not automatically removed and are not canonical state stores.

### Headless typed projection

Every important work object should retain a renderer-independent representation such as JSON/HTML/text plus evidence pointers.

This is the recovery floor.

## CoRendererLattice

Do not enumerate every possible browser/device/provider combination.

Generate candidate embodiments from typed dimensions:

```
engine
x host
x work_object
x provider_adapter
x device
x operating_system
x auth_boundary
x privacy_class
x authority
x currentness
x recovery_mode
x network_state
x interaction_mode
x accessibility_profile
x cost_band
x latency_band
x energy_band
x provenance_quality
x exitability
x portability
```

The raw Cartesian space may be enormous.

Only a bounded qualified frontier should materialize.

`LOGICAL_OPTION_SPACE_NE_LIVE_PROCESSES`
`ADDRESSABLE_NE_MATERIALIZED`

## Selection

Hard gates first:

- authority;
- privacy;
- credential boundary;
- required capability;
- minimum currentness;
- minimum evidence;
- platform compatibility;
- accessibility;
- recovery path.

Then rank the surviving frontier by a vector such as:

`receiver_fit + portability + recovery + proof + diversity + locality + accessibility + exitability - friction - cost - hidden_state - maintenance_debt`

Do not collapse the hard gates into a learned scalar.

## Dual-engine resilience

R0 recommends keeping at least two independently useful renderer families available during transition:

1. WebView2/Chromium-family embedded renderer;
2. Firefox-family independent renderer.

A site-specific compatibility embodiment may exist in parallel.

This is not a claim that two engines guarantee availability. It reduces a single-engine failure domain and creates a practical substitution test.

## Migration ladder

```
LEGACY_BROWSER_AS_ROOT
-> LEGACY_BROWSER_AS_EMBODIMENT
-> COBROWSER_OWNS_WORK_IDENTITY
-> DUAL_RENDERER_PROJECTION
-> RECONSTRUCTION_PROVED
-> PROVIDER_BROWSER_OPTIONAL
-> LEGACY_BROWSER_RETIREMENT_ELIGIBLE
```

Retirement eligibility requires all of:

- exact or qualified work export;
- durable CoWorkObject/checkpoint;
- reconstruction in at least one alternate renderer;
- evidence/currentness preserved;
- required provider flows still reachable where needed;
- rollback path;
- human gate for uninstall/default-browser/account changes.

`PREFERENCE_NE_RETIREMENT_AUTHORITY`
`INSTALLED_NE_CONTINUITY_ROOT`

## No destructive migration while X2 observer is offline

The authorized X2 Remote Desktop Commander observer is currently offline.

Therefore R0 permits:
- architecture;
- public policy;
- synthetic substitution tests;
- future inventory plan.

R0 does not permit:
- uninstalling browsers;
- changing default browser;
- deleting browser profiles;
- deleting provider sessions;
- changing credentials;
- moving private browser state;
- claiming current X2 browser inventory.

`OFFLINE_OBSERVER_NE_RUNTIME_AUTHORITY`
`SCREENSHOT_NE_MACHINE_INVENTORY`

## First bounded substitution canary

Use one local work object and render the same deterministic local projection through:
- renderer A label: `WEBVIEW2_EVERGREEN`;
- renderer B label: `FIREFOX_MANAGED`;
- renderer-independent typed representation.

For R0 the canary is logical/synthetic only. It verifies:
- same work-object digest;
- same authority envelope;
- same evidence pointers;
- same currentness cursor;
- renderer-specific fields do not mutate work identity;
- zero external effects.

A later X2 canary must use actually installed renderers and exact version readback.

## G_d relation

For a renderer candidate `r` and work object `w`, retain a vector distance:

```
G_d(w,r) =
(
 capability_gap,
 authority_gap,
 privacy_gap,
 currentness_gap,
 integration_gap,
 recovery_gap,
 cost_gap,
 accessibility_gap,
 maintenance_gap,
 exit_gap
)
```

A renderer with short `G_d` may be preferable even when another has more nominal features.

`GD_VECTOR_NE_MYSTICAL_FORCE`

## EVO ALL BETTERS+ relation

The renderer lattice is one instance of the general cycle:

```
Discover
-> Qualify
-> Relate
-> Resource
-> Experiment
-> Produce
-> Verify
-> Preserve
-> Extend
-> Recombine
```

Every result may become another resource, relation, anti-resource, null resource, recovery path, test, or substitution candidate.

The cycle is open-ended, but execution remains bounded by evidence, authority, cost, attention, and recoverability.

## Rails

`RENDERER_NE_WORK_IDENTITY`  
`ENGINE_NE_CONTINUITY_ROOT`  
`LEGACY_BROWSER_NE_CANONICAL_STATE`  
`LOGICAL_OPTION_SPACE_NE_LIVE_PROCESSES`  
`ADDRESSABLE_NE_MATERIALIZED`  
`DUAL_ENGINE_NE_AVAILABILITY_GUARANTEE`  
`PREFERENCE_NE_RETIREMENT_AUTHORITY`  
`INSTALLED_NE_CONTINUITY_ROOT`  
`OFFLINE_OBSERVER_NE_RUNTIME_AUTHORITY`  
`SCREENSHOT_NE_MACHINE_INVENTORY`  
`GD_VECTOR_NE_MYSTICAL_FORCE`  
`LOCAL_IS_NOT_LANDED`  
`VALIDATION_IS_NOT_ACCEPTANCE`  
`NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`  
`NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE`  
`HASHING_IS_NOT_SEMANTIC_INGESTION`  
`DISCOVERED_SET_IS_NOT_COMPLETE_HISTORY`

## Sources

- Microsoft WebView2 distribution and Evergreen runtime documentation.
- Microsoft WebView2 WinUI 3 documentation.
- Mozilla Firefox Enterprise policy reference.

These sources establish renderer/deployment capabilities only; they do not prove X2 installation, configuration, or suitability.
