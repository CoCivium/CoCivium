# CoEvo Modes v0

- SESSION: CoEvo260322
- DATE: 2026-03-24
- STATE: COEX_VERIFIED
- ROLE: bounded control-layer definition

## Purpose
Define operating modes to control evolution (balance exploration, refinement, stability, recovery, and alignment).

## Modes

### 1) Exploration Mode
- Goal: discover novel options
- Bias: diversity ↑, mutation ↑, constraints ↓ (within safety rails)
- Use when: uncertainty high, early-stage design, stalled progress
- Risks: noise, low coherence

### 2) Refinement Mode
- Goal: improve quality of known good paths
- Bias: mutation ↓, evaluation rigor ↑, convergence ↑
- Use when: viable candidates exist
- Risks: local optima, overfitting

### 3) Preservation Mode
- Goal: maintain stability and trust
- Bias: mutation minimal, constraints strict, provenance strict
- Use when: high-trust surfaces, public canon, governance artifacts
- Risks: stagnation

### 4) Recovery Mode
- Goal: correct drift/failure
- Bias: rollback, audit, constraint tightening
- Use when: CoEvoDrift or CoEvoCollapse detected
- Risks: overcorrection

### 5) Harmonization Mode
- Goal: reconcile divergent branches
- Bias: recombination, conflict resolution, shared criteria
- Use when: parallel branches conflict or duplicate
- Risks: loss of diversity if overused

## Mode Transitions (triggers)
- Exploration → Refinement: candidate fitness exceeds threshold
- Refinement → Preservation: stability + trust thresholds met
- Any → Recovery: drift/collapse signals triggered
- Exploration/Refinement → Harmonization: duplication/conflict detected

## Minimal Control Rules
- Always declare active mode per wave
- Selection criteria must be explicit per mode
- Commit only with provenance
- Broadcast only bounded artifacts

## Stack Binding
- CoMapGraphs: encode mode transitions
- CoObjectPlans: annotate targets with active mode
- CoStacks: enforce mode-specific constraints

## Receipt
- SESSION=CoEvo260322
- STATE=COEX_VERIFIED
- NEXT=CoFitness_Model_v0
