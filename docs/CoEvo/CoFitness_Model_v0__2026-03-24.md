# CoFitness Model v0

- SESSION: CoEvo260322
- DATE: 2026-03-24
- STATE: COEX_VERIFIED
- ROLE: bounded selection-layer definition

## Purpose
Define how CoEvo selects what survives, spreads, or is deprecated.

## Core Principle
Fitness is multi-dimensional, not singular. Selection must be explicit and declared per wave.

## Fitness Dimensions

### 1) Truth / Provenance
- Evidence-backed
- Traceable origin
- Reproducibility

### 2) Utility / Adoption
- Solves real problem
- Used by others
- Low friction

### 3) Alignment / Equity
- Benefits multiple participants
- Avoids exploitative dynamics
- Respects consent

### 4) Reversibility
- Can be undone
- Low lock-in
- Safe rollback path

### 5) Anti-Capture Resilience
- Resistant to central control
- Works across vendors
- Avoids hidden dependencies

## Scoring (simple v0)
Each dimension scored:
- LOW / MED / HIGH

Selection heuristic:
- Reject if any critical dimension = LOW (context dependent)
- Prefer balanced HIGH/MED across all

## Selection Rules
- Must declare fitness criteria before selection
- Must record rationale (selection_receipt)
- Must preserve rejected candidates when useful

## Stack Binding
- CoEvoLoop: CoEval + CoSelect phases
- CoMapGraphs: encode thresholds
- CoStacks: enforce constraints

## Receipt
- SESSION=CoEvo260322
- STATE=COEX_VERIFIED
- NEXT=CoEvo_Megascroller_v0
