# CoModel substrate-light Ollama inventory preflight R0

**State:** `READ_ONLY_PREFLIGHT_READY__REAL_X2_INVENTORY_UNPROVEN`

## Purpose

Before selecting or executing any real local model, bind what is **actually installed**.

The preflight queries only:

`GET /api/tags`

on an HTTP loopback endpoint.

It records exact installed-model names, manifest digests, sizes and available details.

It does not:

- run inference;
- pull or install a model;
- create, copy or delete a model;
- select a model merely because its name sounds useful;
- use external network access;
- grant runtime or integration authority.

## Why exact digest matters

A model tag or name is not sufficient identity for this canary.

Selection for the later real-model run requires at least:

`model name + exact locally reported digest`

The inventory receipt therefore ends in:

`UNBOUND_REQUIRES_EXACT_NAME_AND_DIGEST_SELECTION`

rather than silently choosing the first model in a list. Computers are very fast at making bad defaults look official.

## Current CI proof

The repository workflow exercises the **same preflight script** against a deterministic loopback `/api/tags` receiver on Linux, Windows and macOS, then fans in the receipts.

That proves the inventory protocol path and normalization behavior only.

It does not prove the contents of X2's actual Ollama inventory.

## Real machine wake condition

When an authorized machine route is available:

1. run this preflight against `http://127.0.0.1:11434`;
2. produce a read-only inventory receipt;
3. bind one already-installed candidate by exact name + digest;
4. do **not** pull/install anything;
5. then run one PUBLIC / LOGICAL_ONLY low-effect contract through `CoLocalModelWorkerR3`;
6. exact-hash its candidate output and require receiver review before any integration.

## Rails

`MODEL_NAME_NE_EXACT_MODEL_IDENTITY_WITHOUT_DIGEST`  
`INSTALLED_NE_VALIDATED_FOR_COCIVIUM`  
`INVENTORY_READBACK_NE_MODEL_MATERIALIZATION`  
`INVENTORY_PROTOCOL_PASS_NE_REAL_OLLAMA_RUNTIME`  
`NO_MODEL_PULL_OR_INSTALL`  
`LOCAL_NE_TRUSTED`  
`VALIDATION_IS_NOT_ACCEPTANCE`
