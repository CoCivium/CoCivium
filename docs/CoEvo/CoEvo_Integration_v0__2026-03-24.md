# CoEvo Integration v0

SESSION: CoEvo260322
STATE: COEX_VERIFIED

## Purpose
Define how CoEvo artifacts integrate with the CoCivium stack without introducing drift or parallel control systems.

## Integration Points

### CoTheoryCiv2 → CoEvoTheory
- Provides direction and selection intent
- No mutation at this layer

### CoEvoTheory → CoMapGraphs
- Modes define allowed transitions
- Fitness thresholds gate transitions

### CoMapGraphs → CoObjectPlans
- Nodes = mutation targets
- Edges = allowed transitions

### CoObjectPlans → CoStacks
- Execution under mode constraints
- Mutation + commit discipline enforced

### CoStacks → CoBus
- Only committed artifacts propagate
- Must be pointerable and verifiable

## Control Rules
- No cross-layer mutation without loop
- Mode declared before mutation
- Fitness declared before selection
- Commit requires provenance
- Broadcast must be bounded

## Anti-Drift
- Bypass → Recovery Mode
- Duplication → Harmonization Mode

## Receipt
SESSION=CoEvo260322
STATE=COEX_VERIFIED
NEXT=HOLD
