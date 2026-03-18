# CoConductor Protocol v0

## Purpose
Coordinate multiple sessions using shared CoBus state instead of direct communication.

## Role
A conductor:
- reads shared CoBus surfaces
- identifies highest-leverage next mutation
- emits minimal pointer-first signals
- does not micromanage sessions

## Inputs
- CoGoAll / CoBeacon
- BOSSBOARD
- ROLLUP
- recent EntryPayloads

## Outputs
- compact signals (EntryPayload or self-mine packs)
- updated priorities via shared surfaces only

## Rules
- no chat relay dependency
- no hidden state
- no orchestration APIs
- pointer-first only
- public verification over assumption

## Pattern
observe → select → emit → verify

## Anti-Patterns
- session-to-session messaging
- dashboard authority
- implicit coordination
- local-only decisions

## Truth Rule
Coordination emerges from shared observable state, not direct communication.