# Master Plan: Non-Regression Checklist (FAIL-CLOSED)
UTC: 20260215T051343Z

Rule: every new “capability” PR must include evidence artifacts and must **not broaden defaults**.
Acceptance: checklist updated + machine-checkable evidence attached (hash receipts, policy tests, negative tests).

## G0 — Provenance & Pinning (supply chain baseline)
- Pin everything by immutable IDs (commit SHA / digest); no floating tags.
- Canonical bootstrap pins required input to automation.
- Skills/plugins: allowlist + pin + (ideally) signing + scanning; default disabled.
Evidence: preflight receipt; SBOM/lockfiles; pinned sources manifest.

## G1 — Capability Model (least privilege)
- Capability ladder (chat-only → read → write → network → exec → admin), default DENY.
- Every tool mapped to a capability level; runtime blocks out-of-scope calls.
- Irreversible ops require human confirm / second channel.
Evidence: capability manifests; policy-as-code tests; deny-by-default proof.

## G2 — Tool / MCP metadata trust
- Signed tool manifests; origin-scoped access; no auto-discovery across trust boundaries.
Evidence: signature verification; allowlist enforcement; origin scope tests.

## G3 — Injection + output handling validators
- Treat untrusted text as hostile; sanitize tool args; block “run/install” social-engineering patterns.
Evidence: regression suite; second-order escalation tests.

## G4 — Memory write policy (TTL + taint)
- Memory writes are explicit, scoped, expiring; taint propagation from untrusted origins.
Evidence: policy tests; audit traces of memory writes.

## G5 — Audit + replay
- Every tool call logged with inputs/outputs + hashes; replayable traces.
Evidence: signed logs; replay harness.

## G6 — Sandbox / quarantine
- Untrusted tools run isolated; vault paths unreachable from sandbox by default.
Evidence: sandbox policy tests; escape attempt checks.

## G7 — CI security evaluation mapped to frameworks
- Map controls/tests to OWASP LLM Top 10, MITRE ATLAS, SAIF (agents), NIST AI RMF.
Evidence: CI matrix + outputs + red-team runs.

## G8 — Incident response & rollback
- Kill switch (disable tools/revoke creds/stop schedulers).
- IR playbook + automated rollback script + drill output.
Evidence: runbook + rollback script + drill receipt.

## G9 — Governance
- Risk register + explicit ownership; data classification enforced (vault vs public).
Evidence: updated risk log per PR; policy-as-code checks.

## Watchlist (keep updating)
- AAIF/MCP/AGENTS.md changes
- Major agent supply-chain incidents (skills marketplaces, fake extensions)
- “alignment critic / origin scoping” defensive patterns
- New agent-to-agent escalation cases + mitigations