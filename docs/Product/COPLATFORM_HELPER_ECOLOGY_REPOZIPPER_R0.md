# CoPlatformHelper+ / RepoZipper+ / CoModule Ecology R0

**Date:** 2026-09-24  
**State:** `CANDIDATE__BRANCH_ONLY__NO_MERGE_CANON_RUNTIME_PUBLIC_OR_AUTHORITY_EFFECT`

## Lead

CoCivium should generalize the GitHub-helper idea into a **platform-helper ecology**.

The product strategy is not to clone every platform prematurely. It is to:

`use -> relate -> wrap -> improve -> make portable -> offer alternate substrate -> optionally replace dependency`

GitHub is an especially useful first host because it already supplies identity, repositories, branches, issues, pull requests, Actions, releases, social discovery and public distribution. CoAll can add missing relationality, provenance, portability, local-first execution, semantic currentness and receiver-relative UX while preserving the option to move to Forgejo/Gitea/GitLab or a future CoAll-native forge.

`PLATFORM_NE_ONTOLOGY`  
`HOST_NE_CUSTODY_TOTALITY`  
`API_NE_CAPABILITY_TOTALITY`  
`RELATION_PERSISTS__BINDING_EVOLVES`

## Existing CoCivium alignment

Current public architecture already supports this direction:

- `CoModule+` is a modular capability/experience with explicit inputs, outputs, dependencies, boundaries and provenance.
- GitHub is an elected public/currentness/evolution projection, not CoAll totality.
- the open-source donor ecology explicitly prefers qualifying and adapting useful upstreams rather than reimplementing every primitive.
- MCP-class adapters are replaceable capability routes, not ontology or authority.
- repository/path bindings may evolve while typed semantic relations persist.

This R0 composes those doctrines into a product family.

## Product family

### 1. RepoZipper+

Preserve **RepoZipper** as the user-facing lineage for repository portability and AI-ready repository handling.

Candidate capability vector:

- exact repository export/archive;
- branch/tag/history preservation;
- issues/PR/release metadata export where APIs permit;
- dependency/submodule/LFS awareness;
- provenance manifest and checksums;
- public/private boundary declaration;
- machine-readable repo map;
- AI-ready compact context bundle;
- restore verification;
- migration between compatible forge hosts;
- scheduled or event-driven bounded backups;
- repository lineage graph;
- stale-pointer / broken-link / orphan detection;
- optional local mirror;
- disaster-recovery rehearsal.

RepoZipper should become **more than a ZIP creator**, but the name remains a good product-shaped front door.

`ZIP_NE_BACKUP_PROOF`  
`EXPORT_NE_RESTORE_PROOF`  
`MIRROR_NE_PRIMARY_AUTHORITY`

Exact predecessor RepoZipper source/repository lineage is not yet recovered in the current CoCivium GitHub projection and must be rebound before source-level evolution is claimed.

### 2. Repo relational helpers

Candidate helpers may be separate CoModules or modes behind one calm surface:

- **RepoMap**: repository topology, roles, dependencies, currentness and semantic projections.
- **RepoDiff**: cross-branch/repo/host semantic and structural differences.
- **RepoPort**: migration/export/import and host rebinding.
- **RepoGuard**: secrets, dependency, license, SBOM, workflow and supply-chain checks through qualified donors.
- **RepoAlive**: health/currentness/receiver/provenance signals rather than vanity activity.
- **RepoBrief**: human and AI bootstrap packet with bounded context.
- **RepoConfluence**: duplicate/conflict/supersession reconciliation across repos and branches.
- **RepoRelease**: release packet, attestations, changelog/currentness and rollback relations.

Names are working projections, not commitments. Prefer a smaller composable capability registry over a merchandise aisle of nearly identical tools.

`MODULE_COUNT_NE_CAPABILITY_VALUE`

### 3. GitHub CoModule pack

A first productized GitHub pack can wrap existing GitHub functionality while adding CoAll relations:

- repository census and role classification;
- issue/PR relationship graph;
- branch collision/currentness checks;
- release/provenance packaging;
- Actions/workflow lint and permission inspection;
- backup/export/migration;
- AI-readable manifests;
- semantic repo search and bootstrap;
- receiver-specific digest/currentness;
- local working-copy and GitHub projection reconciliation;
- optional Forgejo/Gitea/GitLab migration targets.

GitHub remains useful even if CoAll eventually supplies equivalent services.

`PIGGYBACK_NE_CAPTURE`

## General platform pattern

This applies beyond GitHub.

A reusable platform CoModule has six layers:

1. **Platform adapter**  
   API/MCP/CLI/local-client binding.

2. **Typed relation mapper**  
   Converts vendor-specific objects into CoAll relations without erasing vendor semantics.

3. **Evidence/currentness spine**  
   Source time, observation time, hashes/IDs, permissions, provenance, pickup and effect evidence.

4. **Portable local representation**  
   Export/cache/mirror sufficient for continuity and migration within policy.

5. **Receiver-relative surface**  
   RickBar/CoDesktop/public/AI projections appropriate to participant, purpose and privacy.

6. **Replacement/evolution seam**  
   A stable capability contract permitting another provider or CoAll-native implementation later.

This can apply to coding forges, chat/community systems, project trackers, knowledge bases, creative platforms, file/collaboration services, analytics systems and other tools as they become relevant.

`PLATFORM_OBJECT_NE_COALL_OBJECT`  
`ADAPTER_NE_IDENTITY`  
`IMPORT_NE_SEMANTIC_EQUIVALENCE`

## CoAll Optionality Ladder

For any useful external platform:

### L0 — Consume
Use the platform normally.

### L1 — Observe
Capture bounded currentness, provenance, permissions and important object relations.

### L2 — Assist
Add CoModules that improve navigation, analysis, safety, backup, context and automation.

### L3 — Port
Provide exact exports, local representations and migration paths.

### L4 — Dual-bind
Allow the same semantic object to project to multiple compatible surfaces.

### L5 — Substitute
Offer an alternate local/open-source/provider implementation for selected capabilities.

### L6 — CoAll-native
Implement a native service only where it materially improves agency, trust, resilience, economics or capability.

The ladder is non-monotonic. A platform can remain the best implementation indefinitely.

`NATIVE_NE_BETTER_BY_DEFAULT`  
`OPTIONALITY_NE_FORCED_MIGRATION`

## Desktop Commander / machine-capability direction

The present X2 route shows why the same pattern matters for machine control.

As observed on 2026-09-24, the current Remote Desktop Commander connection for X2 is offline from this receiver. That is a route fact, not proof the X2 machine or local tooling is unavailable.

The upstream open-source `wonderwhy-er/DesktopCommanderMCP` is MIT licensed and already contains useful local capabilities including:

- filesystem operations;
- search/edit;
- terminal/process control;
- long-running sessions;
- structured tool history/audit;
- document/data helpers;
- configuration controls.

A second MIT donor, `leonovee/winfs-mcp`, is specifically Windows-oriented and emphasizes:

- allowed-root enforcement;
- hard-bounded timeouts;
- atomic writes;
- audit logging;
- process control;
- MCP Roots;
- fail-closed default filesystem access.

These should be **qualified donors**, not blindly merged.

### Proposed split

Do not begin by rebuilding "Desktop Commander" as one monolith.

Build a CoAll-native **CoMachineCapability+ contract** with replaceable implementations:

`filesystem | search | git | process | shell | local-model | network-bounded | artifact | observer | receipt`

Then qualify donor implementations beneath it.

Candidate components:

- **CoMachineFS+**: bounded filesystem operations.
- **CoProcess+**: supervised process/session execution.
- **CoMachineGit+**: local Git operations and exact-head evidence.
- **CoMachineReceipt+**: append-only operation receipts/readproof.
- **CoMachinePolicy+**: allowed roots, authority ceiling, command policy, privacy.
- **CoMachineRoute+**: local stdio, LAN, authenticated remote MCP or future protocol.
- **CoMachineObserver+**: liveness/lease/currentness without claiming execution success.

Product/UI names can remain friendlier than the internal relation names.

`MCP_NE_MACHINE_CAPABILITY`  
`REMOTE_ROUTE_NE_LOCAL_CAPABILITY`  
`CONNECTED_NE_AUTHORIZED_FOR_ALL_EFFECTS`  
`COMMAND_ACCEPTED_NE_EFFECT_PROVEN`

## Rebuild versus fork decision

For every donor component, use this election:

1. **use upstream unchanged** when fit and risk are acceptable;
2. **adapter-wrap** when behavior is useful but ontology/control should stay ours;
3. **fork** when sustained source changes are materially required;
4. **reimplement a narrow primitive** when the dependency cost or policy mismatch exceeds the code value;
5. **retire/rebind** when a better implementation appears.

Forking is not the default trophy.

`FORK_NE_PROGRESS`

## Open-source Bring-In pipeline

Every candidate donor should enter through one reusable pipeline:

`discover -> exact upstream bind -> license capture -> threat/permission review -> capability map -> test evidence -> narrow canary -> compare -> adapter/fork/reference election -> provenance-preserving integration -> update watch`

Required donor record:

`donor_id | repo | commit/tag | license | capability | data touched | authority required | network behavior | telemetry | update model | test state | adapter/fork/reference | provenance | known gaps | replacement seam`

This extends the existing Open-Source Donor Ecology into a machine-actionable registry.

## Productization model

A CoModule should be usable in at least three modes where practical:

- **CoAll-native**: integrated into RickBar/CoDesktop/CoHome.
- **Sidecar**: augments an existing platform without replacing it.
- **Standalone**: focused helper/product for people who do not use CoAll.

This permits external products to become onramps instead of requiring a full CoCivium adoption decision.

RepoZipper is a strong candidate for such a standalone/sidecar-first product.

`PRODUCT_ONRAMP_NE_PLATFORM_CAPTURE`

## NB readiness gate

A new note/email to NB should wait for a small credible participant journey, not another giant architecture dump.

Candidate readiness means we can point him to:

1. one stable start URL or local entry point;
2. one working CoModule he can actually use;
3. one visible way his action changes something and produces a receipt;
4. one recovery path when a session/provider disappears;
5. one fun/creative layer rather than only operator machinery;
6. no need for him to act as transport between tabs/tools;
7. a clear boundary between experiment and public/effectful action.

When those are true, prepare a short email that says, in substance:

- we rebuilt enough of the substrate that it is worth trying again;
- here is the single entry point;
- here is one interesting thing to do;
- break it, disagree with it, invent around it;
- his prior contributions remain attributed where provenance supports them.

Do not send automatically. Draft for Rick's manual use when the gate is satisfied.

`EMAIL_READY_NE_PRODUCT_READY`  
`PRODUCT_READY_FOR_NB_NE_BROAD_PUBLIC_RELEASE_READY`

## Immediate bounded frontier

1. recover exact prior RepoZipper lineage from X2/local history when the machine route is available;
2. classify current Desktop Commander/local-machine route failure without assuming root cause;
3. create a machine-readable donor registry extension for machine-control and forge/platform helpers;
4. qualify DesktopCommanderMCP and winfs-mcp at exact commits;
5. select one tiny CoMachineCapability canary, preferably read-only orientation plus exact hash/readproof;
6. only then elect adapter vs fork vs narrow reimplementation;
7. build RepoZipper/CoModule helper proof on top of the provider-neutral relation model;
8. hold NB outreach until the participant journey gate is real.

## Nonclaims

This document does not prove:

- prior RepoZipper source recovery;
- X2 local runtime state;
- current PS7/local Desktop Commander health;
- a CoAll-native forge implementation;
- donor security;
- donor integration;
- NB outreach readiness;
- runtime deployment;
- canon.

## Rails

`RELATION_PERSISTS__BINDING_EVOLVES`  
`REPOSITORY_NE_ONTOLOGY`  
`GITHUB_NE_COALL_TOTALITY`  
`PLATFORM_NE_ONTOLOGY`  
`ADAPTER_NE_AUTHORITY`  
`DONOR_CODE_NE_ARCHITECTURE`  
`FORK_NE_IDENTITY`  
`UPSTREAM_UPDATE_NE_AUTOMATIC_ADOPTION`  
`MCP_NE_COALL`  
`MCP_NE_MACHINE_CAPABILITY`  
`PS7_NE_DEFAULT_IF_MACHINE_ROUTE_HEALTHY`  
`LOCAL_IS_NOT_LANDED`  
`DELIVERY_NE_PICKUP`  
`POINTER_NE_ACK`  
`NO_NEWEST_WINS`
