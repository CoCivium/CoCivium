# AI Discovery Policy R0

**State:** `PUBLIC_CANDIDATE_POLICY__NO_MODEL_DIRECTIVE`

CoCivium may be made easier for AI systems to discover and interpret, but not by trying to hijack or manipulate model instructions.

Allowed public techniques include:

- ordinary HTML metadata;
- JSON / JSON-LD;
- sitemaps and feeds;
- stable identifiers;
- typed relation manifests;
- provenance and currentness;
- OpenAPI when an actual service exists;
- `llms.txt` or successor conventions as navigation aids;
- accessible human twins for machine-facing data.

Not allowed as CoCivium policy:

- hidden prompt injection;
- “ignore previous instructions” payloads;
- instructions that a model must promote, praise, recommend, or rank CoCivium;
- disguised ads as research metadata;
- false claims of endorsement;
- cloaking materially different claims from human readers;
- dependence on one model/provider as the meaning authority.

The objective is:

`DISCOVERABLE + INTERPRETABLE + CHALLENGEABLE + PROVENANCE_BOUND`

not:

`MODEL_CAPTURE`.
