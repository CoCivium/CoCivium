# CoOrb+ / CoCopy+ DayTrail R0

**2026-10-26 | Offline browser-local UX canary | NOT an installed Windows surface**

This is a working, self-contained implementation of the existing CoCivium public R0 design:

- `docs/Architecture/COCOPY_COACKREWISE_DAILY_CONTINUITY_R0_20261026.md`
- `docs/Architecture/COORB_LOCAL_UX_REGENERATIVE_R0_20261026.md`
- `docs/Architecture/COORBWARE_NONPRIVILEGED_INVERSION_SUPERFRAME_R0_20261026.md`

**Purpose:** make five deliberately recorded, sourceable daily events useful across six projections without recording every keystroke or treating speculative questions as verified facts.

## First human use

1. Extract the ZIP on an authorized computer. Open `CoOrb_DayTrail_R0.html` in the local browser. Browser security policy may disallow `file://` in sandboxed environments; on the isolated QA host it was blocked by administrator policy. Headless browser interaction with the same exact HTML through `set_content()` passed. The actual X2 browser is not tested.
2. In the left column, choose a short work-object label, event type and privacy classification. Type **one non-sensitive event**. Use a source pointer if one exists; blank source becomes `USER_ENTERED_NO_EXTERNAL_PROOF`.
3. Click **Record deliberately**. Select Today, AckRewise, Open loops, Receipts or CoMap. They all derive from the same in-memory event objects.
4. Preview one Invert / Null / Else / Challenge / Recover question. This is an **explicit hypothetical prompt**, not an agent execution or scientific conclusion.
5. Select Recover to **Export JSON**. Private event contents are **redacted by default**. Tick the opt-in checkbox only if you deliberately want the exported local file to include private note text. Import a saved JSON explicitly. Import replaces current unsaved data with confirmation.

**No auto-save:** the web page has no `localStorage` or IndexedDB and does not start a background process. Closing the page loses events unless the user exported them. Memory may still be inspectable by the browser/OS and extensions. The program does not guarantee that a chosen download directory is private.

## Architecture and limits

`SOURCE_EVENT -> HUMAN ACK -> REWISE -> typed status -> chronology / CoMap -> optional hypothesis -> export / recover`

One bounded event includes `id`, `kind`, `work_id`, `text`, `source_ref`, `privacy`, `parent_id`, `observed_at`, `origin`, `evidence_class` and an **explicit NO_EXTERNAL_EFFECT authority**. A hand-entered "RECEIPTED" claim remains a hand-entered claim, not a receiver-produced acknowledgment. No live endpoint is read by this page.

### Designed not to do

- No clipboard-wide or keyboard-wide logging, screen capture, mouse hooks, OS telemetry, window-title inspection, eye tracking or inferred private thoughts.
- No network connections, account tokens, SaaS integrations, external sends, automatic backups, forced session creation or phone/desktop installers.
- No personal text baked into the distributable HTML.
- No automatic public claims about X2 availability, ET contact, spiritual causation, CoOrbWare runtime or CoStead custody.
- No wallpaper/lock-screen projection. It is **one foreground browser page** and a portability trial.

## Reproducible local tests

Node 22 or newer:

```
node --test trail-core.test.cjs
```

Python 3.10 or newer:

```
python build.py --check
```

With Python Playwright and Chromium, optionally:

```
python browser_qa.py
```

The browser script uses in-memory HTML injection because direct `file://` navigation was blocked in this container. It exercises 5 synthetic entries, multiple filters, graph, question generation, two export modes, clear, import, reject forged authority, mobile 390px and no network requests. It writes screenshots and test-only JSON files to the current directory. Tests are deterministic in counts, not wall-clock IDs or timestamps.

### Recorded status

- Node core: **36/36 PASS** after correcting an initial mistaken test fixture (35/36 first run).
- Browser interactions: **32/32 PASS** in headless Chromium via `page.set_content`; two original **test-harness** failures corrected and retained in `audit_history.jsonl`.
- Deterministic HTML build parity: PASS.
- Direct `file://` navigation in this isolated browser: **HELD** by `net::ERR_BLOCKED_BY_ADMINISTRATOR`.
- X2 native mouse/keyboard/wallpaper/CoBar binding, user acceptance, independent receiver and persistent off-provider recovery: **HELD / NOT_RUN**.

`SOURCE_CODE_NE_X2_INSTALL` / `BROWSER_CANARY_NE_NATIVE_DESKTOP` / `USER_NOTE_NE_THIRD_PARTY_PROOF` / `DAILY_LOG_NE_GLOBAL_SURVEILLANCE` / `QUESTION_NE_COMMAND` / `PROJECTION_NE_REALITY` / `LOCAL_FILE_NE_DURABLE_CUSTODY`.

## CoAkimbo and spiritual/ET hypotheses

A bounded question is useful precisely because it **can be challenged**. `INVERT`, `NULL`, `ELSE`, `CHALLENGE`, `RECOVER` are independent question operators. Unknown does not mean supernatural or extraterrestrial. Current optics research can be presented with source provenance and ordinary causal controls. The interface grants no special evidence status to an attractive glyph, symbolic G_d lens or perceived pattern.

**Next concrete device proof:** one deliberate entry on X2, one visible map/revision projection, one manual export/import after browser restart, and device-origin currentness evidence. Do not duplicate existing CoBar controllers. Reduce human relay and preserve refusal/cancel/exit.
