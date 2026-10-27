# CoResourceFrontier+ R0 | CoEnerget+ resource mesh shadow canary

**Status:** REVIEW_ONLY / SYNTHETIC ALLOCATION / NO X2 INSTALL / NOT A LIVE SCHEDULER.

This is a small acceptance proof for the [existing CoResourceFrontier](../../docs/Architecture/CORESOURCE_FRONTIER_ALLOCATOR_R0.md), [CoRenewal](../../docs/Architecture/CORENEWAL_SELECTIVE_AMPLIFICATION_R0_20261026.md) and [CoAkimbo](../../docs/Architecture/COAKIMBO_PRODUCTIVE_DISEQUILIBRIUM_R0_20261026.md). It does **not** create a competing CoBus, CoRunner, CoOrb or power-source system.

## What can grow?

A CoObject, a relation, an observation, a negative result, a symbol or an untested hypothesis may all be represented and related. This is an **opportunity space**, not evidence that every object physically harvests energy, has agency, or is authorized to act. To allocate a real device, first establish a calibrated energy/CPU/memory budget, health/currentness, authority, receiver and consent. Physical net energy must be measured in appropriate units; this demo models **estimated consumption in mWh**, not generation.

## Main rule

`DISCOVER -> QUALIFY CAPABILITY -> VERIFY CURRENTNESS/CONSENT -> RESERVE HEADROOM -> ELECT FINITE SHADOW PROPOSAL -> INDEPENDENT EXECUTION GATE -> RECEIPT -> RELEASE -> SLEEP`

An overloaded, offline, stale, degraded, unverified or operator-protected device is **not** a place to elect new work. The planner has no execution path. One user working in the foreground outweighs an unproven synthetic task score.

## How to run (Python 3.11+, no dependencies)

```sh
cd examples/coresource_frontier_shadow_r0
python -m unittest -v test_resource_mesh_r0
python resource_mesh_r0.py < fixture.json > proposed_only.json
```

The example contains **synthetic workstation/CPU/cloud candidates** and six test tasks. It deliberately denies speculative power harvesting, real device mutation, unknown energy costs, high-pressure research and an offline/protected workstation. It selects at most two inexpensive **SHADOW_PROPOSAL_ONLY** candidates from separate simulated failure domains. A mock `ONLINE_DECLARED` resource is not an actual connected resource.

### What is bounded

- <=32 resource descriptors, <=64 work descriptors, <=256 KiB input, <=8 proposed active jobs.
- Strict metadata validation and IDs, full upfront policy costs, unknown cost/observability held.
- Configurable CPU milliseconds, energy **mWh**, human attention seconds, and money cents; memory peak MiB reserved separately, conservative sum across co-resident jobs.
- Headroom reserve from 0 to 95%, domain and resource concurrency ceilings, protected foreground resource list, stale observation threshold, locality/privacy gates.
- Only metadata, no secret content, source download, clipboard/window text, credentials or background execution.
- Recover/maintain/serve a person before speculative experiment as an **illustrative** priority rule, not a universal economic optimum or verified social benefit. No claim of mathematical global optimization or real observed energy gain.
- All effect classes other than `NONE` are held, even when there is a reversible route. The caller's resource/status/cost statements are not independently authenticated.

### Windows, when a real machine is available

`read_only_windows_census_r0.ps1` is a **single shot**, local PowerShell 7 script. By default it returns JSON **only to stdout**, without writing a file, changing a process, touching startup tasks, scheduling or networking. It observes Windows process count, top working-set sizes, browser process counts, logical processors, free physical RAM if CIM is available, and per-drive free disk space. **CPU figures are process lifetime, not instantaneous CPU load.** One snapshot cannot establish the cause of a lag.

```powershell
pwsh -NoProfile -File .\read_only_windows_census_r0.ps1
```

Optional **private** append-only file, when explicitly requested:

```powershell
pwsh -NoProfile -File .\read_only_windows_census_r0.ps1 -SavePrivate -OutputDirectory 'D:\CoCivium\CoFarm\PrivateDiagnostics'
```

Do not post the private snapshot to GitHub or a public chat; process names and local drive data may be sensitive. No automatic X2 control is provided. On Windows, this script should be qualified by CI before considering production use. The Desktop Commander bridge being offline is not proof that the computer itself is off.

## What the tests do and do not prove

`test_resource_mesh_r0.py` tests deterministic selection, per-resource/domain caps, memory and energy headroom, classification, freshness, output privacy, fail-closed errors and zero effects. The Windows CI job validates the PowerShell script on a GitHub-hosted Windows runner without printing process data. It is **not** an X2 acceptance test.

**Explicit nonclaims:**

- No continuously running process, actual AI calls, local model inference, power harvesting or universal availability.
- No measured workload time, battery Wh, CPU watts, system efficiency or actual benefit.
- No actual provider/tool/device authorization or receiver ACK.
- No access to X1 or X2, no RicKBar/CoBar installation and no task termination.
- No CoStead/offsite independent pickup.
- No source-currentness proof merely from a caller timestamp.

Next real proof when X2 authenticated connectivity exists: observe **one** read-only, bounded machine resource snapshot; compare with a second snapshot taken when lag occurs; attribute resource pressure before any service intervention; preserve an exact local receipt; propose only one reversible fix with a manual stop path. Existing [desktop owner issue #181](https://github.com/CoCivium/CoCivium/issues/181) retains responsibility for any launcher change.

`CONTINUOUS_OPTIONALITY_NE_PERMANENT_ACTIVE_COMPUTE | POWER_GRADIENT_NE_FREE_ENERGY | HYPOTHESIS_NE_HARVESTED_POWER | AVAILABLE_NE_AUTHORIZED | OPTIMIZATION_NE_CPU_100_PERCENT | PROCESS_PRESENT_NE_HEALTHY | SHADOW_NE_EFFECT | FIRST_DATA_NE_CAUSE | X2_BRIDGE_OFFLINE_NE_X2_POWER_OFF`
