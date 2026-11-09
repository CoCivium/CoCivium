# rickBar Continuity R1 | Source, recovery and acceptance

**Status:** PUBLIC_CANDIDATE_SOURCE. Synthetic CI results must be checked. Not a native dock, X2 deployment, independent CoStead receiver, ChatGPT-session takeover, or actual >24-hour uptime.

## The decision

The visible rickBar conversation owns a durable conversation ID, not any provider window. WorkID and TurnID bind each proposed model response. Workers may be replaced only under fenced successor epochs, exact readback and permissions. The interface can appear continuously usable without falsely calling a worker continually alive or aware.

## Existing reusable components

- [R1 continuity store](../../examples/comodelfabric/rickbar_continuity_r1.py): standard-library SQLite/WAL for stable conversation identity, bounded-turn history, idempotent turns, conflict detection, stale-epoch fencing and explicit indeterminate responses.
- [R1 loopback UI](../../examples/comodelfabric/rickbar_local_web_r1.py): localhost browser shell, persistent conversation pointer, exact local readback and one-request-at-a-time interaction.
- [Continuity tests](../../examples/comodelfabric/test_rickbar_continuity_r1.py) and [real local HTTP tests with fake model](../../examples/comodelfabric/test_rickbar_local_http_r1.py). [Existing CoModelFabric CI](../../.github/workflows/comodelfabric-ollama.yml) is extended, not duplicated.
- [R0 model/receipt bridge](../../examples/comodelfabric/rickbar_ollama_bridge_r0.py): local Ollama response and unverified model-output receipt. Output is not independent physical effect confirmation.

## Day-one host trial (not performed on X2)

From an authorized machine with Python, an explicitly qualified local Ollama instance and the repository files, execute:

    python examples/comodelfabric/rickbar_local_web_r1.py --port 8766 --model qwen3:4b

Then browse to http://127.0.0.1:8766. This is a local browser prototype, not installation of the existing native rickBar or a ChatGPT API integration. The default local state is current-user CoBarState/continuity-r1.sqlite; receipts remain in current-user CoBarReceipts. Do not submit secrets or confidential data. Backups and disk encryption remain operator responsibilities.

## Minimum acceptance matrix

| Gate | Observable proof | Current boundary |
| --- | --- | --- |
| Conversational persistence | Two real turns with same ConversationID, restart browser and local process, verify transcript | Source + synthetic tests, no X2 proof |
| Handoff safety | Two contenders, one elected epoch; stale writer fails; accepted turn read back | SQLite same-host fixture, not distributed lease |
| Interrupted turn | INDETERMINATE after interrupted model call; no duplicate automatic request | Source + synthetic test |
| Hosted provider swap | Authorized official API adapters with identical WorkID schema, revocable permissions, cost/retention limits | Not implemented |
| Original ChatGPT session swap | Supported provider/session API, no browser limit evasion | Not demonstrated; do not claim possible by rotating UI tabs |
| Retirement/deletion | Verified successor checkpoint before retirement; separately authorized provider deletion and proof | Not supported; no auto-deletion |
| True communal mindshare | Participant consent + visibility scopes + independent receiver ACK and retraction | Research architecture only |
| RickBar native dock | Visible native bar, input/output and fallback, local Ollama on authorized host | X2 host not accessible from current bridge |
| Unattended >24 h | Durable wake/WorkID, independent host witness, real crash/reboot recovery, human-touch count | Not observed |
| User value | Task completion, clarity, time, trust, recoverability vs prior UX | Not measured |

## Trigger attribution (the missing answer to overnight progress)

Record for each attempt: WorkID, ConversationID, TurnID, event time, observer, trigger_kind = USER_TURN / SCHEDULED / EVENT / MANUAL_OPERATOR / UNKNOWN, source revision, model/provider, authorization, output hash, receiver readproof, checkpoint, next wake and limitations. Never infer a cause from an unsourced next-morning status. GitHub commits indicate repository work, not whether a schedule, mobile session or independent agent caused it. For an unavailable source, use UNKNOWN.

## Model receipt namespace and replay barrier (2026-11-09)

The R1 HTTP adapter now derives its model-output receipt WorkID from **both** ConversationID and TurnID. A bare turn number is only unique *within* a conversation, so using it as a global receipt filename could make two unrelated conversations collide. The derived bounded ID is deterministic and SHA-256-based; it protects the receipt namespace, not privacy or authorization.

A newly reserved turn accepts only a **fresh** `RECORDED_UNVERIFIED` model result that returns the matching WorkID and syntactically valid digest. `REPLAY`, `CONFLICT`, absent identity, or foreign receipt identity cannot be silently promoted to a new committed reply. Ambiguity remains `INDETERMINATE`; no automatic model retry or data deletion. This is local consistency, **not** an authenticated receipt from an independent receiver or proof the model's answer is true.

Existing raw receipt files are not rewritten or deleted. No local data or credentials are published.

## Trigger provenance R1 extension (source candidate)

The persisted `trigger_kind` now distinguishes `UNKNOWN`, `LOCAL_HTTP_REQUEST`, `SCHEDULED`, `EVENT` and `MANUAL_OPERATOR` on every *new* turn. The additional `trigger_evidence` records `NONE`, `LOOPBACK_REQUEST_OBSERVED_USER_UNAUTHENTICATED`, or `PRODUCER_CLAIM_UNVERIFIED`. Model-output receipt hashes and local readback include both fields. Previous R1 SQLite rows migrate to `UNKNOWN/NONE` without reclassifying historical activity.

Local HTTP requests are always marked `LOCAL_HTTP_REQUEST`, even if client JSON pretends to be a scheduler; loopback origin does **not** prove which human, process or external trigger originated the request. A separate authenticated scheduler or event adapter is still necessary to attribute off-browser activity. No automatic overnight agent has been created.

**Required next proof:** authenticated scheduler/host event identity `->` durable WorkID trigger `->` model execution `->` independent receiver acknowledgment `->` source revision and timing readback. A self-declared `SCHEDULED` label is not sufficient. Unknown preexisting turns and unattributed GitHub commits remain UNKNOWN.

## Human, virtual and non-sentient participants

A participant can be a consenting human, a permissioned model/tool process, a device, a static source, or a simulation, but participant_type and authority_scope cannot be inferred from conversational persona. Voices, avatars and CoAvNims are revocable projections. Keep independent observer identities, uncertainty, time and evidence classes, no implicit equality between source publication and uptake. A reusable relational field is not automatic cross-session consciousness.

## Security and no-clobber

The R1 server binds only loopback and checks Host/Origin, but is not multi-user authenticated; never expose to LAN, WAN, proxies or untrusted local processes. Conversations are stored as plaintext local SQLite and not in the public repository. Browser localStorage stores a pointer only. No private transcripts, secrets, credentials, device telemetry, or provider account contents should be published.

Switching to a new conversation is NOT deletion of the old transcript. No session/browser cleanup, official provider data deletion, or cross-provider token replay is implemented. External hosted APIs must follow actual consent, usage, rate limits and retention rules. Do not claim an implicit permanent autonomous process or unbounded provider usage.

## Next causal promotion

First observe the amended GitHub Actions job for this PR. Fix any failures. Then, after actual X2 or another authorized host becomes reachable, run a real Ollama message in the local interface, stop and restart it, confirm same durable transcript and receipt, capture elapsed time and independent receiver observation. Preserve native fallback and Break Glass. If host remains unreachable, stay at CI_TESTED_SOURCE, not WORKING_X2.

**Rail:** SESSION_NE_WORK_ID | SOURCE_PASS_NE_DEPLOYMENT | LOCAL_READBACK_NE_INDEPENDENT_ACK | CONTINUITY_NE_SENTIENCE | PROVIDER_DELETION_NE_LOCAL_UI_REMOVAL | NO_HUMAN_MAILMAN.
