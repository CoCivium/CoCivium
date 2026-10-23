# CoLogicalSession Million Preview R0

**State:** `LOGICAL_POPULATION_PREVIEW__NO_MATERIALIZATION`

## Question

Can CoCivium represent a population such as **1,000,000 logical sessions** without opening 1,000,000 provider chats, processes, accounts, sockets, or model contexts?

R0 answers the representation question only: **yes, as a generative recipe plus a bounded deterministic sample**.

It does not establish that one million tasks are useful, eligible, affordable, independent, or authorized to run.

## Existing architecture reused

This implementation extends existing CoSession doctrine rather than introducing another session ontology:

- `VIRTUAL_SESSION_COUNT_NE_ACTIVE_PROCESS_COUNT`
- `SPAWN_NE_NEW_CHAT`
- `SPAWN_NE_NEW_PROCESS`
- `LOGICAL_RESERVE_NE_LIVE_WORKER`
- `AVAILABLE_CAPACITY_NE_AUTHORITY_TO_SPAWN`

Sources are pinned into every preview by SHA-256:

- `ai/virtual-session-policy.json`
- `schemas/cospawn-contract-v0.1.schema.json`

The generated sample uses only declared roles, morphologies, and persistence modes from those registries.

## Representation

The command:

```sh
python scripts/CoLogicalSessionMillionPreviewR0.py \
  --logical-count 1000000 \
  --sample-limit 12 \
  --materialization-ceiling 64 \
  --seed andrew-r0
```

does **not** allocate one million session objects.

It stores one declared population count and computes at most the requested bounded sample. Each sampled descriptor is deterministically reconstructed from:

`recipe + seed + logical_index + source bindings`

The default sample ceiling is 100 records. The declared population bound is at most `10^12` for this canary.

## Materialization boundary

`materialization_ceiling` is a budget ceiling, not a selection.

R0 deliberately returns:

```text
eligible_materialization_count = null
selected_for_materialization = []
workers_started = 0
provider_sessions_created = 0
accounts_created = 0
```

A later materialization election requires task-specific evidence plus capability, authority, confidentiality, budget, lease, collision, receiver, and stop-condition gates.

A million logical identities can therefore remain dormant while a small justified frontier becomes HOT.

## Provider-neutral relation

A logical session is not rooted in Claude, ChatGPT, Ollama, a browser tab, or any other provider.

A later eligible work item may materialize through an authorized route such as:

- deterministic local code;
- the existing loopback-only local/Ollama worker;
- GitHub CI;
- an explicit provider adapter;
- another future node.

Changing embodiment does not grant authority and does not make providers independent evidence sources.

## Historical replay relation

Historical work can be represented as `ECHO`, `RITUAL`, `COUNTERFACTUAL`, `CHALLENGER`, or other logical sessions without immediately executing it.

A later replay planner should bind, where available:

- exact source artifact or prompt bytes;
- source date/version;
- old model/provider identity and version;
- old tool/runtime environment;
- known missing environment facts;
- current comparison target;
- fixed evaluation criteria;
- provenance of each replay result.

`SAME_PROMPT_NE_SAME_EXPERIMENT` and `NEWER_MODEL_NE_BETTER_RESULT`.

## Transparent adversarial fixtures

Model robustness work should use explicitly marked synthetic fixtures: ambiguous prompts, persuasion-resistance cases, provenance-loss cases, coordination simulations, and sycophancy tests.

R0 creates no identities, public interactions, provider accounts, or external communications. Its effects are zero.

## Why this helps Andrew

The visible product can show four active workspaces while retaining millions of dormant logical possibilities underneath. Andrew should interact with useful work, evidence, challenges, and receipts rather than babysitting provider tabs.

The system should optimize:

`verified_receiver_value / active_embodiment_cost`

not the raw number of sessions.

## Tests

The regression suite checks:

- one million declared sessions produce only the bounded sample;
- `10^12` declared sessions still decode only the requested sample;
- a zero sample calls no session decoder;
- session IDs and indices are deterministic and unique in the sample;
- provider/account/worker effects remain zero;
- a materialization ceiling selects nothing by itself;
- sampled facets come from existing registries;
- numeric bounds fail closed;
- external identity and interaction effects remain absent.

## Nonclaims

R0 does not prove:

- one million live workers;
- one million provider sessions;
- one million accounts;
- useful one-million-way parallelism;
- provider capacity;
- model independence;
- external adoption;
- receiver pickup;
- runtime scheduling;
- authority to materialize any sampled session.

The important result is less theatrical and more useful: **logical population size is decoupled from live embodiment count**.
