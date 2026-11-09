# CoNav+ | Atlas of diagrams R0

**SOURCE-ONLY, PUBLIC-SAFE, PINNED PROJECTION. Not the X2 CoOrb, an all-session census, a live media index, or a receiver ACK.**

Based on [existing CoMap source graph](../../ai/comap-source-projection-r0.json) and [five-source retro-media overlay](prior-media-backfill-overlay-r0.json). An earlier bounded private inspiration sample and local screenshots are not copied here.

**View:** start with a small line-and-box overview, then choose a group below. Every group has paged sub-diagrams and text relations. Old and alternative versions remain in their original sources.

## Overview

```mermaid
flowchart LR
  Root["CoNav atlas | one source spine"]
  G0["CoMap and CoOrb (1)"]
  Root --> G0
  G1["Evolution domains (21)"]
  Root --> G1
  G2["Repositories (21)"]
  Root --> G2
  G3["Highlights (10)"]
  Root --> G3
  G4["Documents (3)"]
  Root --> G4
  G5["Prior media inspirations (5)"]
  Root --> G5
  G1 -->|REGISTERS_HIGHLIGHT x10| G3
  G1 -->|REGISTERED_REPOSITORY x46| G2
  G1 -->|RELATED_PUBLIC_DOCUMENT x3| G4
  G0 -->|PROPOSED_PROJECTION_FAMILY x1| G1
  G0 -->|PROPOSED_RELATIONAL_LENS x1| G1
  G5 -->|INSPIRATION_CANDIDATE_FOR x5| G0
```

## Diagram index

| Open a diagram | Source objects |
| --- | ---: |
| [CoMap and CoOrb](#map-views) | 1 |
| [Evolution domains](#domain-views) | 21 |
| [Repositories](#repository-views) | 21 |
| [Highlights](#highlight-views) | 10 |
| [Documents](#source-document-views) | 3 |
| [Prior media inspirations](#media-candidate-views) | 5 |

## Views and typed relations

### map views

**CoMap and CoOrb: 1 source objects.**

#### CoMap and CoOrb | page 1 of 1

```mermaid
flowchart LR
  P["CoMap and CoOrb / page 1"]
  N0["CoMap+ projection"]
  P --> N0
  X0["CoUX+/CoSurface+ | domain"]
  N0 -->|PROPOSED_PROJECTION_FAMILY| X0
  X1["CoAll+ | domain"]
  N0 -->|PROPOSED_RELATIONAL_LENS| X1
```

| Source object | Type | Outgoing relations |
| --- | --- | --- |
| `view:CoMap+` | map | PROPOSED_PROJECTION_FAMILY → domain:CoUX+/CoSurface+; PROPOSED_RELATIONAL_LENS → domain:CoAll+ |

### domain views

**Evolution domains: 21 source objects.**

#### Evolution domains | page 1 of 2

```mermaid
flowchart LR
  P["Evolution domains / page 1"]
  N0["CoAll+"]
  P --> N0
  N1["CoAutoEvo+/CoEvo+"]
  P --> N1
  N2["CoEducation+"]
  P --> N2
  N3["CoFuture+"]
  P --> N3
  N4["CoGibberTru+"]
  P --> N4
  N5["CoHighlight+"]
  P --> N5
  N6["CoHumour+"]
  P --> N6
  N7["CoIndex+"]
  P --> N7
  N8["CoInsight+"]
  P --> N8
  N9["CoLex+"]
  P --> N9
  N10["CoMythOps+"]
  P --> N10
  N11["CoNodeMesh+/GRAIL+"]
  P --> N11
  X0["CoInsights | repository"]
  N8 -->|REGISTERED_REPOSITORY| X0
  X1["CoCivium | repository"]
  N8 -->|REGISTERED_REPOSITORY| X1
  N5 -->|REGISTERED_REPOSITORY| X1
  X2["GIBindex | repository"]
  N7 -->|REGISTERED_REPOSITORY| X2
  N7 -->|REGISTERED_REPOSITORY| X1
  X3["CoShareHub | repository"]
  N7 -->|REGISTERED_REPOSITORY| X3
  N9 -->|REGISTERED_REPOSITORY| X2
  N9 -->|REGISTERED_REPOSITORY| X1
  N0 -->|REGISTERED_REPOSITORY| X1
  X4["CoSteward | repository"]
  N0 -->|REGISTERED_REPOSITORY| X4
  N10 -->|REGISTERED_REPOSITORY| X1
  N10 -->|REGISTERED_REPOSITORY| X0
  N4 -->|REGISTERED_REPOSITORY| X1
  N4 -->|REGISTERED_REPOSITORY| X2
  N6 -->|REGISTERED_REPOSITORY| X1
  N6 -->|REGISTERED_REPOSITORY| X0
  N1 -->|REGISTERED_REPOSITORY| X1
  X5["CoStacks | repository"]
  N1 -->|REGISTERED_REPOSITORY| X5
  N1 -->|REGISTERED_REPOSITORY| X4
  N11 -->|REGISTERED_REPOSITORY| X1
  N11 -->|REGISTERED_REPOSITORY| X3
  N11 -->|REGISTERED_REPOSITORY| X4
  X6["CoFutures | repository"]
  N3 -->|REGISTERED_REPOSITORY| X6
  N3 -->|REGISTERED_REPOSITORY| X1
  X7["CoAcademy | repository"]
  N2 -->|REGISTERED_REPOSITORY| X7
  N2 -->|REGISTERED_REPOSITORY| X1
  X8["Cognocarta Consenti / constitutional consent lineage | highlight"]
  N5 -->|REGISTERS_HIGHLIGHT| X8
  X9["CoTheoryAll+ | highlight"]
  N5 -->|REGISTERS_HIGHLIGHT| X9
  X10["CoCivia disclosed composite front | highlight"]
  N5 -->|REGISTERS_HIGHLIGHT| X10
  X11["RickBar / CoDesktop+ | highlight"]
  N5 -->|REGISTERS_HIGHLIGHT| X11
  X12["CoVirtualSession+ / session morphology | highlight"]
  N5 -->|REGISTERS_HIGHLIGHT| X12
  X13["CoNodeMesh+ / GRAIL+ federation | highlight"]
  N5 -->|REGISTERS_HIGHLIGHT| X13
  X14["CoPriMath+ | highlight"]
  N5 -->|REGISTERS_HIGHLIGHT| X14
  X15["CoGibberTru+ | highlight"]
  N5 -->|REGISTERS_HIGHLIGHT| X15
  X16["The CoCivium Salute | highlight"]
  N5 -->|REGISTERS_HIGHLIGHT| X16
  X17["CoAllPulseField+ / CoTime+ currentness | highlight"]
  N5 -->|REGISTERS_HIGHLIGHT| X17
  X18["Evolution Fabric | source_document"]
  N1 -->|RELATED_PUBLIC_DOCUMENT| X18
  X19["Civ2+ Cell Hosting | source_document"]
  N11 -->|RELATED_PUBLIC_DOCUMENT| X19
  X20["CoEvoDelta Schema | source_document"]
  N1 -->|RELATED_PUBLIC_DOCUMENT| X20
```

| Source object | Type | Outgoing relations |
| --- | --- | --- |
| `domain:CoAll+` | domain | REGISTERED_REPOSITORY → repo:CoCivium/CoCivium; REGISTERED_REPOSITORY → repo:CoCivium/CoSteward |
| `domain:CoAutoEvo+/CoEvo+` | domain | REGISTERED_REPOSITORY → repo:CoCivium/CoCivium; REGISTERED_REPOSITORY → repo:CoCivium/CoStacks; REGISTERED_REPOSITORY → repo:CoCivium/CoSteward; RELATED_PUBLIC_DOCUMENT → doc:docs/Evolution/COALL_GITHUB_EVOLUTIO; RELATED_PUBLIC_DOCUMENT → doc:schemas/coevo-delta-v0.1.schema.json |
| `domain:CoEducation+` | domain | REGISTERED_REPOSITORY → repo:CoCivium/CoAcademy; REGISTERED_REPOSITORY → repo:CoCivium/CoCivium |
| `domain:CoFuture+` | domain | REGISTERED_REPOSITORY → repo:CoCivium/CoFutures; REGISTERED_REPOSITORY → repo:CoCivium/CoCivium |
| `domain:CoGibberTru+` | domain | REGISTERED_REPOSITORY → repo:CoCivium/CoCivium; REGISTERED_REPOSITORY → repo:CoCivium/GIBindex |
| `domain:CoHighlight+` | domain | REGISTERED_REPOSITORY → repo:CoCivium/CoCivium; REGISTERS_HIGHLIGHT → highlight:CognocartaConsenti; REGISTERS_HIGHLIGHT → highlight:CoTheoryAll; REGISTERS_HIGHLIGHT → highlight:CoCivia; REGISTERS_HIGHLIGHT → highlight:RickBar; REGISTERS_HIGHLIGHT → highlight:CoVirtualSession; REGISTERS_HIGHLIGHT → highlight:CoNodeMesh; REGISTERS_HIGHLIGHT → highlight:CoPriMath; REGISTERS_HIGHLIGHT → highlight:CoGibberTru; REGISTERS_HIGHLIGHT → highlight:CoSalute; REGISTERS_HIGHLIGHT → highlight:CoAllPulseField |
| `domain:CoHumour+` | domain | REGISTERED_REPOSITORY → repo:CoCivium/CoCivium; REGISTERED_REPOSITORY → repo:CoCivium/CoInsights |
| `domain:CoIndex+` | domain | REGISTERED_REPOSITORY → repo:CoCivium/GIBindex; REGISTERED_REPOSITORY → repo:CoCivium/CoCivium; REGISTERED_REPOSITORY → repo:CoCivium/CoShareHub |
| `domain:CoInsight+` | domain | REGISTERED_REPOSITORY → repo:CoCivium/CoInsights; REGISTERED_REPOSITORY → repo:CoCivium/CoCivium |
| `domain:CoLex+` | domain | REGISTERED_REPOSITORY → repo:CoCivium/GIBindex; REGISTERED_REPOSITORY → repo:CoCivium/CoCivium |
| `domain:CoMythOps+` | domain | REGISTERED_REPOSITORY → repo:CoCivium/CoCivium; REGISTERED_REPOSITORY → repo:CoCivium/CoInsights |
| `domain:CoNodeMesh+/GRAIL+` | domain | REGISTERED_REPOSITORY → repo:CoCivium/CoCivium; REGISTERED_REPOSITORY → repo:CoCivium/CoShareHub; REGISTERED_REPOSITORY → repo:CoCivium/CoSteward; RELATED_PUBLIC_DOCUMENT → doc:docs/Architecture/CIV2_FEDERATED_CEL |

#### Evolution domains | page 2 of 2

```mermaid
flowchart LR
  P["Evolution domains / page 2"]
  N0["CoOps+"]
  P --> N0
  N1["CoPriMath+"]
  P --> N1
  N2["CoRails+"]
  P --> N2
  N3["CoSession+"]
  P --> N3
  N4["CoSource+/Provenance"]
  P --> N4
  N5["CoStrategy+"]
  P --> N5
  N6["CoTheoryAll+"]
  P --> N6
  N7["CoUX+/CoSurface+"]
  P --> N7
  N8["RickBar+/CoDesktop+"]
  P --> N8
  X0["MasterPlan | repository"]
  N5 -->|REGISTERED_REPOSITORY| X0
  X1["CoCivium | repository"]
  N5 -->|REGISTERED_REPOSITORY| X1
  N6 -->|REGISTERED_REPOSITORY| X1
  X2["CoInsights | repository"]
  N6 -->|REGISTERED_REPOSITORY| X2
  X3["CoSources | repository"]
  N6 -->|REGISTERED_REPOSITORY| X3
  X4["CoSteward | repository"]
  N0 -->|REGISTERED_REPOSITORY| X4
  X5["CoToolbelt | repository"]
  N0 -->|REGISTERED_REPOSITORY| X5
  X6["CoStacks | repository"]
  N0 -->|REGISTERED_REPOSITORY| X6
  N1 -->|REGISTERED_REPOSITORY| X1
  N1 -->|REGISTERED_REPOSITORY| X2
  N8 -->|REGISTERED_REPOSITORY| X1
  X7["CoAura | repository"]
  N8 -->|REGISTERED_REPOSITORY| X7
  N8 -->|REGISTERED_REPOSITORY| X5
  N7 -->|REGISTERED_REPOSITORY| X7
  N7 -->|REGISTERED_REPOSITORY| X1
  N3 -->|REGISTERED_REPOSITORY| X1
  N4 -->|REGISTERED_REPOSITORY| X3
  N4 -->|REGISTERED_REPOSITORY| X1
  X8["CoRails | repository"]
  N2 -->|REGISTERED_REPOSITORY| X8
  N2 -->|REGISTERED_REPOSITORY| X1
```

| Source object | Type | Outgoing relations |
| --- | --- | --- |
| `domain:CoOps+` | domain | REGISTERED_REPOSITORY → repo:CoCivium/CoSteward; REGISTERED_REPOSITORY → repo:CoCivium/CoToolbelt; REGISTERED_REPOSITORY → repo:CoCivium/CoStacks |
| `domain:CoPriMath+` | domain | REGISTERED_REPOSITORY → repo:CoCivium/CoCivium; REGISTERED_REPOSITORY → repo:CoCivium/CoInsights |
| `domain:CoRails+` | domain | REGISTERED_REPOSITORY → repo:CoCivium/CoRails; REGISTERED_REPOSITORY → repo:CoCivium/CoCivium |
| `domain:CoSession+` | domain | REGISTERED_REPOSITORY → repo:CoCivium/CoCivium |
| `domain:CoSource+/Provenance` | domain | REGISTERED_REPOSITORY → repo:CoCivium/CoSources; REGISTERED_REPOSITORY → repo:CoCivium/CoCivium |
| `domain:CoStrategy+` | domain | REGISTERED_REPOSITORY → repo:CoCivium/MasterPlan; REGISTERED_REPOSITORY → repo:CoCivium/CoCivium |
| `domain:CoTheoryAll+` | domain | REGISTERED_REPOSITORY → repo:CoCivium/CoCivium; REGISTERED_REPOSITORY → repo:CoCivium/CoInsights; REGISTERED_REPOSITORY → repo:CoCivium/CoSources |
| `domain:CoUX+/CoSurface+` | domain | REGISTERED_REPOSITORY → repo:CoCivium/CoAura; REGISTERED_REPOSITORY → repo:CoCivium/CoCivium |
| `domain:RickBar+/CoDesktop+` | domain | REGISTERED_REPOSITORY → repo:CoCivium/CoCivium; REGISTERED_REPOSITORY → repo:CoCivium/CoAura; REGISTERED_REPOSITORY → repo:CoCivium/CoToolbelt |

### repository views

**Repositories: 21 source objects.**

#### Repositories | page 1 of 2

```mermaid
flowchart LR
  P["Repositories / page 1"]
  N0[".github"]
  P --> N0
  N1["CoAcademy"]
  P --> N1
  N2["CoAura"]
  P --> N2
  N3["CoBusMirror"]
  P --> N3
  N4["CoCivium"]
  P --> N4
  N5["CoCrownJewelVault"]
  P --> N5
  N6["CoFutures"]
  P --> N6
  N7["CoInsights"]
  P --> N7
  N8["CoLegalVault"]
  P --> N8
  N9["CoPolitic-site"]
  P --> N9
  N10["CoRails"]
  P --> N10
  N11["CoShareHub"]
  P --> N11
```

| Source object | Type | Outgoing relations |
| --- | --- | --- |
| `repo:CoCivium/.github` | repository | None registered |
| `repo:CoCivium/CoAcademy` | repository | None registered |
| `repo:CoCivium/CoAura` | repository | None registered |
| `repo:CoCivium/CoBusMirror` | repository | None registered |
| `repo:CoCivium/CoCivium` | repository | None registered |
| `repo:CoCivium/CoCrownJewelVault` | repository | None registered |
| `repo:CoCivium/CoFutures` | repository | None registered |
| `repo:CoCivium/CoInsights` | repository | None registered |
| `repo:CoCivium/CoLegalVault` | repository | None registered |
| `repo:CoCivium/CoPolitic-site` | repository | None registered |
| `repo:CoCivium/CoRails` | repository | None registered |
| `repo:CoCivium/CoShareHub` | repository | None registered |

#### Repositories | page 2 of 2

```mermaid
flowchart LR
  P["Repositories / page 2"]
  N0["CoSources"]
  P --> N0
  N1["CoStacks"]
  P --> N1
  N2["CoSteward"]
  P --> N2
  N3["CoToolbelt"]
  P --> N3
  N4["CoTrustedWindow"]
  P --> N4
  N5["EntMent"]
  P --> N5
  N6["GIBindex"]
  P --> N6
  N7["MasterPlan"]
  P --> N7
  N8["TEMP"]
  P --> N8
```

| Source object | Type | Outgoing relations |
| --- | --- | --- |
| `repo:CoCivium/CoSources` | repository | None registered |
| `repo:CoCivium/CoStacks` | repository | None registered |
| `repo:CoCivium/CoSteward` | repository | None registered |
| `repo:CoCivium/CoToolbelt` | repository | None registered |
| `repo:CoCivium/CoTrustedWindow` | repository | None registered |
| `repo:CoCivium/EntMent` | repository | None registered |
| `repo:CoCivium/GIBindex` | repository | None registered |
| `repo:CoCivium/MasterPlan` | repository | None registered |
| `repo:CoCivium/TEMP` | repository | None registered |

### highlight views

**Highlights: 10 source objects.**

#### Highlights | page 1 of 1

```mermaid
flowchart LR
  P["Highlights / page 1"]
  N0["CoAllPulseField+ / CoTime+ currentness"]
  P --> N0
  N1["CoCivia disclosed composite front"]
  P --> N1
  N2["CoGibberTru+"]
  P --> N2
  N3["Cognocarta Consenti / constitutional consent lineage"]
  P --> N3
  N4["CoNodeMesh+ / GRAIL+ federation"]
  P --> N4
  N5["CoPriMath+"]
  P --> N5
  N6["The CoCivium Salute"]
  P --> N6
  N7["CoTheoryAll+"]
  P --> N7
  N8["CoVirtualSession+ / session morphology"]
  P --> N8
  N9["RickBar / CoDesktop+"]
  P --> N9
```

| Source object | Type | Outgoing relations |
| --- | --- | --- |
| `highlight:CoAllPulseField` | highlight | None registered |
| `highlight:CoCivia` | highlight | None registered |
| `highlight:CoGibberTru` | highlight | None registered |
| `highlight:CognocartaConsenti` | highlight | None registered |
| `highlight:CoNodeMesh` | highlight | None registered |
| `highlight:CoPriMath` | highlight | None registered |
| `highlight:CoSalute` | highlight | None registered |
| `highlight:CoTheoryAll` | highlight | None registered |
| `highlight:CoVirtualSession` | highlight | None registered |
| `highlight:RickBar` | highlight | None registered |

### source-document views

**Documents: 3 source objects.**

#### Documents | page 1 of 1

```mermaid
flowchart LR
  P["Documents / page 1"]
  N0["Civ2+ Cell Hosting"]
  P --> N0
  N1["Evolution Fabric"]
  P --> N1
  N2["CoEvoDelta Schema"]
  P --> N2
```

| Source object | Type | Outgoing relations |
| --- | --- | --- |
| `doc:docs/Architecture/CIV2_FEDERATED_CELL_HOSTING_R0.md` | source_document | None registered |
| `doc:docs/Evolution/COALL_GITHUB_EVOLUTION_FABRIC_R0.md` | source_document | None registered |
| `doc:schemas/coevo-delta-v0.1.schema.json` | source_document | None registered |

### media-candidate views

**Prior media inspirations: 5 source objects.**

#### Prior media inspirations | page 1 of 1

```mermaid
flowchart LR
  P["Prior media inspirations / page 1"]
  N0["CoMap offline source weave"]
  P --> N0
  N1["Context rail prototype"]
  P --> N1
  N2["Relational media diagram"]
  P --> N2
  N3["Public visual finder"]
  P --> N3
  N4["Visual prior bridge"]
  P --> N4
  X0["CoMap+ projection | map"]
  N0 -->|INSPIRATION_CANDIDATE_FOR| X0
  N2 -->|INSPIRATION_CANDIDATE_FOR| X0
  N4 -->|INSPIRATION_CANDIDATE_FOR| X0
  N3 -->|INSPIRATION_CANDIDATE_FOR| X0
  N1 -->|INSPIRATION_CANDIDATE_FOR| X0
```

| Source object | Type | Outgoing relations |
| --- | --- | --- |
| `media:comap-source-weave` | media_candidate | INSPIRATION_CANDIDATE_FOR → view:CoMap+ |
| `media:context-rail` | media_candidate | INSPIRATION_CANDIDATE_FOR → view:CoMap+ |
| `media:relational-media-diagram` | media_candidate | INSPIRATION_CANDIDATE_FOR → view:CoMap+ |
| `media:visual-finder` | media_candidate | INSPIRATION_CANDIDATE_FOR → view:CoMap+ |
| `media:visual-prior-bridge` | media_candidate | INSPIRATION_CANDIDATE_FOR → view:CoMap+ |

**Exact source pointers (not copied media):**
- [CoMap offline source weave](../../examples/comap/source-weave-r0.html) | Git blob `4887dbb294ae0c1eda3dffe475d9b1274bdf559c` | rights and receiver uptake **unverified**
- [Context rail prototype](../../examples/conodcothumb/context_rail_r1/index.html) | Git blob `e50b11a2825d9548248746c4f7937049ea97caa8` | rights and receiver uptake **unverified**
- [Relational media diagram](../../examples/colensmedia/relational_media_diagram_r0.md) | Git blob `476e5eeb6e24e1fae562552ac07dd234748ab8ce` | rights and receiver uptake **unverified**
- [Public visual finder](../../examples/covisual_finder_r1/index.html) | Git blob `2360b7ceea035599a7604e5c54d28b1765952e0d` | rights and receiver uptake **unverified**
- [Visual prior bridge](../../examples/colensmedia/visual_prior_bridge.html) | Git blob `aed071ba013e54320ce3e5b28c4c130a0317ba48` | rights and receiver uptake **unverified**

## Evidence and privacy ceiling

- Bounded graph: 56 earlier source nodes / 61 typed source edges.
- Retroactive sample: 5 public media **candidates** / same number of typed inspiration edges; prior private assets are not represented.
- The original source graph remains unmodified, as do previous CoMap/CoLens/CoMail versions.
- Links are source references. Motif selection is a hypothesis, not rights clearance, empirical proof, semantic acceptance, or user permission.
- Diagram boxes do not imply running agents, approved messages, live X2 CoOrb, or any provider/recipient ACK.
- To evolve, check source Git blobs, update the overlay with an explicit successor, re-render and compare. No overwrite without versioned review.

`RENDER_NE_TRUTH` · `DIAGRAM_NE_RECEIVER` · `INSPIRATION_NE_LICENSE` · `SOURCE_ONLY_NE_RUNTIME` · `PRIVATE_NE_PUBLIC` · `ADDRESSABLE_NE_ALL_LOADED`
