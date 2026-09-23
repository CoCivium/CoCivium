# CoEvoDelta intake

This directory is a **candidate append-only intake surface** for bounded `CoEvoDelta+` objects produced by sessions, workers, or reviewers participating in the shared CoAll GitHub Evolution Fabric.

It is not a command queue, canon, runtime state, or global authority surface.

Use the schema at `schemas/coevo-delta-v0.1.schema.json`.

## Rules

- one bounded delta per object;
- bind source refs and target surfaces;
- classify epistemic status, confidentiality, mutation class, and authority ceiling;
- preserve contradictions and wake conditions;
- prefer domain subscriptions over project-wide omniscience;
- branch/review uncertain or cross-cutting changes;
- do not infer CoEx, canon, runtime, adoption, or session-wide ACK from repository presence.

`ALL_SESSIONS_CAN_CONTRIBUTE_NE_ALL_SESSIONS_MUTATE_ALL_SURFACES`

`GITHUB_WRITE_ACCESS_NE_GLOBAL_AUTHORITY`

`DELTA_NE_COMMAND`

`MERGED_NE_CANON`
