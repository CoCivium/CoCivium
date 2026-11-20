# CoInputGap+ R0 | App-local time between edits, without key capture

**State:** bounded candidate in the existing CoOmniIO PR. No X2 installation, Perixx hardware observation, mouse interception, session wake, CoBar adoption, network access, AI invocation, surveillance, claim about sentience or autonomously shared context.

A quiet interval after at least two local edit notifications may offer a **single shadow candidate**: `INSPECT_RELATIONS`, `CHALLENGE_PREMISE` (CoInversion+), or `COMPARE_PRIOR_VERSION`. It never interprets the pause as consent, proof of intent, or execution permission. A preview requires an explicit decision; no candidate sends, saves content, types, executes, opens a model or modifies a work object.

The `InputGapShadow` module is a deterministic, dependency-free library. It **does not attach listeners, own a timer, read the keyboard or mouse, collect raw text/keys, search windows, or discover focus itself**. An authorized app-local editor may explicitly arm it after consent and supply only a monotonic timestamp, event class `LOCAL_EDIT` / `LOCAL_POINTER`, focus and sensitivity booleans. Events containing raw `key`, `code`, `text`, `clipboard`, `password`, window title, URL or path are rejected. On sensitive context or focus loss it disarms and clears pending state. `LOCAL_POINTER` alone never infers writing intent. No use with password, payment, authentication, unknown, bystander or cross-application contexts.

## Local reproduction

```sh
node --test examples/coomniio/CoInputGapR0.test.mjs
```

A source-only demonstration can be reproduced with a synthetic event stream. It does not observe the OS or user:

```js
import {InputGapShadow} from './CoInputGapR0.mjs';
const g = new InputGapShadow({quietMs:800});
g.arm({consent:true,scope:'OWNED_EDITOR',atMs:0});
g.note({kind:'LOCAL_EDIT',atMs:100});
g.note({kind:'LOCAL_EDIT',atMs:200});
const shadow = g.inspect({atMs:1000}); // CANDIDATE_ONLY
```

**Unclaimed next gates:** explicit accessible UI with a visible armed indicator, Escape/off switch, no background/wallpaper input; independent first-use test on an owned Perixx keyboard and current mouse; latency/false-positive/attention budget; hard data privacy checks; exact version/receipt capture; only then optional downstream mapping to CoMap/CoOrb/CoCopy. Pair with CoPreCursor+ preview and CoThumb+ file-backed capsules. CoLens+ can render evidence and G_d as labeled interpretations, never as physical verification.

**Symbol key for accessible surfaces:** `>` follows evidence to a next reversible preview; `<` shows prior/source; `?` unknown; `!` actionable concern; `↔` comparison; `⊘` intentionally held; `✓` verified within stated scope. Always show words with symbols, never color alone. No permanent gesture assignment is assumed.

`QUIET_NE_CONSENT | EVENT_CLASS_NE_KEYLOGGER | CANDIDATE_NE_ACTION | INVERSION_NE_TRUTH | SYMBOL_NE_SEMANTIC_PROOF | LOCAL_CI_NE_X2_ADOPTION`.
