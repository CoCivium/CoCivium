# SessionSelfMining Protocol v0

## Purpose
Replace long handoff prose with compact pointer-first successor packs.

## Principle
A session should leave behind a small public self-mine pack containing:
- what was actually verified
- what public pointers matter
- what remains blocked
- what exact next mutation is highest leverage

## Required Fields
- SESSION
- UTC
- STATE
- VERIFIED
- BLOCKED
- NEXT
- PTRS

## Rules
- public/raw pointers over prose
- compact over exhaustive
- no hidden assumptions
- no local-only claims
- successor should be able to resume from pack alone

## Recommended Path
docs/COBUS_LITE/self_mining/packs/

## Truth Rule
If it is not publicly pointerable, it is not part of the self-mine authority surface.