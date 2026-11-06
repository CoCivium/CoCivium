# CoAI / IA / CoOrbWare evergreen read-only onramp gate R0

**Mode:** shadow-only on-change source validation for existing machine onramps, not a new registry, always-on process, AI provider adapter, account enrolment, CoOrbWare installation or source of truth.

The current public project already has `llms.txt`, `ai/index.json`, `ai/session-bootstrap.json`, `ai/onramp/cocivia-first-use-r0.json`, `ai/onramp/specialist-entrypoints-r0.json` and CoAcademy's `docs/coorb/discovery.json` / CoRelay `docs/relay/beacon.json`. This canary checks the *five same-repo local source bodies* for exact-byte identity, known schema and cross-pointer consistency, and distinguishes a dated declaration from current independent readproof.

```
python3 scripts/coai_onramp_evergreen_r0.py --repo-root .
python3 -m unittest -v scripts/test_coai_onramp_evergreen_r0.py
```

**Evergreen** here means source-addressable and re-checked when a material dependency changes or a qualified receiver needs it. It does not mean every old provider session has read the update, every model has converted to a functioning agent, a subscribed receiver is awake, or every conceptual capability is currently operational.

**Three distinct levels**:

1. **AI discovery:** a source-bound AI/model/client may read, compare, summarize, challenge or propose. None of this yields effect authority.
2. **IA candidate:** a model/tool would need an authenticated adapter, named identity, measurable capability, explicit scoped authority, privacy and budget controls, and real receiver handling. Read-only discovery does not grant these.
3. **CoOrbWare receiver:** a user-selected projection of work across interfaces. Public `docs/coorb/discovery.json` is an external source pointer; this gate does not fetch it, prove GitHub Pages host currentness, verify independent human/model adoption or install anything on X2.

The offline canary only reads five public checkout files and emits one compact JSON report. GitHub Actions on a draft branch may run this on relevant source changes; this is not an independent failure domain or real receiver, and contains no background schedule. `declared_observation` older than 14 days is a **recheck warning**, not evidence a link failed or a source was superseded. The `--max-age-days` value is a tunable candidate. No auto-promote on recency.

Because `CoAcademy` is outside this checkout, its URL is cross-checked against pinned **public navigation pointers** but never marked as remotely read. Actual CoAcademy readback, independent HTTP, first-use comprehension and an authenticated IA task require separate receipts. The live apex front door currently has independent reachability/security questions, outside this offline evaluator's scope.

**Non-equivalences:** `SOURCE_READ_NE_AI_OR_IA_ADOPTION | POINTER_NE_REMOTE_READPROOF | LATCHED_NE_ALWAYS_RUNNING | MACHINE_READABLE_NE_EFFECT_AUTHORITY | LISTED_ROLE_NE_ACTIVE_WORKER | COORB_VIEW_NE_INSTALLED_OS | GITHUB_PROVIDER_NE_INDEPENDENT_CUSTODY | STALENESS_WARNING_NE_SOURCE_INVALIDITY`.

**Next useful proof:** one independently operated model (not just another provider chat copying a prompt) follows the public CoAcademy manifest, correctly identifies one supported claim and one missing proof, and produces a timestamped receiver-origin readback. Actual tool-use elevation then needs a separate permissioned adapter trial. If X2 remains unreachable through Desktop Commander, that is a route observation, not proof that X2 itself is powered off.
