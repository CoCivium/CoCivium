# CoCopy+ / CoAckRewise+ Day Trail R0

**Review-only FOSS donor** for the existing [CoAllPulseField+ / CoTime+ event model](../../docs/Architecture/COALL_PULSEFIELD_COTIME_R0.md) and [CoRelationalUX+/CoAckRAW+/CoReWis+](../../docs/Architecture/CORELATIONAL_UX_PREDICTIVE_INPUT_R0.md). No second event bus, background daemon, global clipboard watcher, mind reader, provider connector or X2 install.

## What it actually does

- One **explicitly supplied** event becomes one private daily JSONL record: RAW, REWISE, ACK, CHALLENGE or OUTCOME.
- Each record carries sequence, event time, optional independently supplied source-time, source pointer, raw-content SHA-256, optional deliberately retained text, parent event identity and a local chained record digest.
- **Default: hash-only source content**, with no raw note retained. The --retain-raw flag is required to store selected note text.
- Separate **verify** readback and **render** of an offline HTML trail, with mobile-friendly green presentation, no JavaScript, no network, no CDN, readable source IDs, escaped private content, text fallbacks and keyboard-native disclosure.
- The daily source is isolated by ISO date. An ACK event means a participant locally labeled an ACK; it **does not** establish that any outside provider or human receiver acknowledged anything.
- Bad or unqualified data **HELD**. Single local writer uses an exclusive lock; interrupted writes require explicit recovery and verification, not silent auto-repair.

## One local-first example (public-safe synthetic fixture)

Python 3.9+ standard library. Work in a **private, explicitly chosen folder outside the public GitHub checkout**. These examples only read a deliberately selected file.

~~~sh
python3 examples/cocopy_ackday_r0/cocopy_ackday.py --root ./private-test-trail append --day 2026-10-26 --kind RAW --source-id test:synthetic-day
python3 examples/cocopy_ackday_r0/cocopy_ackday.py --root ./private-test-trail verify --day 2026-10-26
python3 examples/cocopy_ackday_r0/cocopy_ackday.py --root ./private-test-trail render --day 2026-10-26 --output ./private-test-trail/day.html
~~~

To hash a deliberately selected text file without storing its contents, append --input-file path. To deliberately retain the text locally, also pass --retain-raw. Do not use shell arguments for secret text; histories can retain them. No command captures clipboard text, keystrokes, unsent drafts, ChatGPT/WhatsApp conversations, private thoughts, microphone, camera, screen pixels or unrelated files.

All data remains where you explicitly chose to place it. A private local hash chain does **not** establish externally independent integrity, backup, CoStead landing or historical completeness. R0 has no built-in replication, authentication, encryption-at-rest or receiver session ingestion.

## CoOrb/RickBar projection

The local HTML page is a **standalone timeline demonstration**, not a desktop overlay or installed CoOrbWare. It shows explicit local RAW → REWISE → ACK → CHALLENGE → OUTCOME records and hashes. A real CoOrb/RickBar can later subscribe to a **consented, privacy-filtered, source-bound pointer**, never silently import this private journal.

The missing machine-owned future adapter is source-specific: supported provider APIs or locally authorized application exports must supply exact source/currentness and opt-in scope. Browser tab appearance, user intent and page contents are not authority or independent receiver ACK.

## Reproduce

~~~sh
python3 -m py_compile examples/cocopy_ackday_r0/cocopy_ackday.py
python3 -m unittest discover -s examples/cocopy_ackday_r0 -p 'test_cocopy_ackday.py' -v
~~~

Forty negative/synthetic tests cover data limits, intentional retention, time/scope, sequence, tampering, partial writes, single writer lock, symlink, XSS escaping, output no-clobber and no provider/OS ingestion.

**Hard boundaries:** RAW_NE_PUBLIC · REWISE_NE_ERASURE · ACK_LABEL_NE_RECEIVER_ACK · EVENT_HASH_NE_TRUTH · LOCAL_NE_DURABLE · NO_CONTENT_NE_NO_THOUGHT · LOCAL_VIEW_NE_X2_RUNTIME · CI_PASS_NE_USER_ADOPTION.

**FOSS Forever · Working Together Respectfully · Privacy by design · Explicit, reversible choice.**
