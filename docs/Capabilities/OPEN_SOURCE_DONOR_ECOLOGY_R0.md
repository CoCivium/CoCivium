# Open-Source Donor Ecology R0

**State:** `REFERENCE_ONLY__LICENSE_CAPTURED__NO_SOURCE_CODE_INGESTED`

Yes: CoCivium should deliberately maintain a donor ecology rather than reimplementing every useful primitive from scratch.

The rule is not “copy everything useful.” It is:

`discover -> qualify -> bind exact upstream -> record license/provenance -> extract pattern or adapter -> canary -> compare -> integrate or reject`

## First qualified donor set

| Donor | License observed | Candidate value | Initial posture |
|---|---|---|---|
| Microsoft PowerToys | MIT | FancyZones, multi-monitor/window utility patterns | Pattern/component donor |
| Flow Launcher | MIT | command palette, plugins, search/launcher UX | Pattern/adapter donor |
| GlazeWM | GPL-3.0 | tiling/workspace/focus architecture | Architecture reference first |
| OpenSSF Scorecard | Apache-2.0 | repository/supply-chain posture | CI candidate |
| Gitleaks | MIT | secret leak scanning | read-only scan candidate |
| Trivy | Apache-2.0 | dependency/config/container scanning | read-only scan candidate |
| OSV-Scanner | Apache-2.0 | vulnerability matching | read-only scan candidate |
| actionlint | MIT | GitHub Actions validation | read-only CI lint candidate |

Exact observed license blob SHAs are stored in `open_source_donors_r0.json`.

## Why this matters

The donor ecology can give CoAll faster access to:

- desktop/workspace management;
- command palettes and plugin systems;
- CI validation;
- security and vulnerability scanning;
- provenance and supply-chain evidence;
- SBOM and dependency visibility;
- reusable interaction patterns;
- future adapter surfaces.

But the donor remains replaceable.

`DONOR_CODE_NE_ARCHITECTURE`

`FORK_NE_IDENTITY`

`UPSTREAM_UPDATE_NE_AUTOMATIC_ADOPTION`

## Three adoption modes

### 1. Pattern reference

Study behavior/architecture and implement a CoAll-native relation.

No source copy required.

### 2. Replaceable adapter

Use the donor as an external tool behind a typed capability contract.

Preferred when it prevents a fork from becoming a permanent dependency empire.

### 3. Provenance-bound source ingestion

Only when source reuse is materially better than an adapter.

Before copying code:

1. bind exact upstream repository and commit;
2. capture license and notices;
3. record source paths/lineage;
4. define transformation;
5. preserve attribution;
6. test independently;
7. keep the donor relation visible after modification.

## GitHub-native capability pack

The CoCivium root repository should also grow a calm, reusable project shell:

- CODEOWNERS;
- contribution policy;
- security-reporting policy;
- pull-request template;
- issue forms;
- dependency update automation;
- read-only validation;
- release provenance;
- artifact attestations;
- machine-readable capability registry.

R0 stages only the non-executing governance/doc pieces. Automated scanners/workflows should enter through separate bounded PRs so their permissions and noise can be reviewed.

## Future donor families

Candidate discovery lanes, not yet qualified:

- docs/sites: MkDocs Material, Docusaurus, Astro/Starlight;
- diagrams: Mermaid and compatible graph renderers;
- provenance/knowledge: W3C PROV, RO-Crate, LinkML, SHACL;
- observability: OpenTelemetry, Prometheus-compatible exporters;
- messaging/event fabric: NATS or lighter append-log adapters;
- local data: SQLite/DuckDB;
- cross-platform UI: Avalonia or web/native hybrids;
- SBOM: Syft and interoperable CycloneDX/SPDX tooling;
- release automation and changelog generation;
- accessibility testing;
- property/fuzz testing;
- reproducible-build and attestation tooling.

Each donor must be independently qualified before source ingestion.

## Rails

`OPEN_SOURCE_NE_FREE_OF_OBLIGATIONS`  
`LICENSE_CAPTURE_NE_LICENSE_COMPLIANCE_PROVEN`  
`REFERENCE_NE_INGESTION`  
`ADAPTER_NE_AUTHORITY`  
`TOOL_OUTPUT_NE_TRUTH`  
`SECURITY_SCANNER_NE_SECURITY_PROOF`  
`OPTIONALITY_NE_DEPENDENCY_SPRAWL`
