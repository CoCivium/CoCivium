# CoAndrewFirst+ R0

A dependency-free static browser prototype for the merged CoEvidence Bundle Canary R0.

## Run

From the repository root:

```sh
python -m http.server 8000
```

Open:

```text
http://localhost:8000/examples/coandrewfirst/
```

The page reads these existing repository artifacts:

- `examples/co-evidence-bundle-r0.spec.json`
- `docs/Operations/fixtures/coevidence-bundle-r0-20261022.json`

No backend, account, model API, telemetry, cookies, or external write action is implemented.

## Five-minute path

1. See one measured result.
2. Inspect exact evidence identities, hashes, versions, custody labels, and pinned locators.
3. Challenge three bounded claims using deterministic answers grounded in the merged canary.
4. Inspect simulated-versus-observed boundaries and select a future provider lane.
5. Generate a local browser receipt describing what this browser instance read and which boundaries remain unproved.

## Model and substrate boundary

R0 executes deterministic browser logic only.

The UI exposes future adapter targets for Claude, open-source/local models, OpenAI-compatible endpoints, and historical model replay. Selecting one changes only the local receipt. It does not call a model or assert that a provider is configured.

Historical replay is intentionally not implemented in R0. A later experiment should bind the exact old prompt/input, model identifier/version when known, tool environment, expected comparison criteria, and current replay output. Different model generations must not be treated as equivalent merely because they received similar text.

## Evidence boundary

The prototype consumes the merged canary's pinned public source manifest and measured report. It does not establish:

- live session synchronization;
- receiver adoption or pickup;
- independent scientific replication;
- semantic truth of source claims;
- model-provider execution;
- deployment on Andrew's device or any other receiver.

The generated browser receipt is a local read/interaction record, not a custody transition or receiver pickup proof.

## Acceptance target

A first-time user should be able to complete the five steps without project-specific vocabulary, identify at least one source artifact, state whether the demo is live or simulated, and leave with a receipt whose nonclaims are explicit.
