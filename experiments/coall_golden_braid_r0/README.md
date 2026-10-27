# CoAll+ Golden Braid R0 | two-destination local canary

**Tracking source:** [CoCivium issue #317](https://github.com/CoCivium/CoCivium/issues/317).  Reuse the existing CoEvoDelta, session fan-in, receiver-relative fanout and CoSourceGraph contracts.  This is an **offline demonstration of the transport/receipt state machine**, not a new runtime, semantic control plane, deployed adapter or cross-session bus.

## Exactly what was tested

One immutable public-safe, wholly synthetic canonical task packet carries identity, source/version, intent, authority ceiling, owner, next deed, acceptance, timestamp, status, evidence class, alternative substrates, and two fixed recipients `test-alpha` and `test-beta`.

1. A dispatcher writes **only** local test destination files, using creation-exclusive (no-overwrite) writes and fsync on each file.
2. First attempt deliberately fails beta; the failed attempt remains recorded.
3. A separate foreground Python invocation reads alpha's actual bytes and writes its own local readproof, hash-bound to the original source packet and destination payload.
4. A fresh dispatcher invocation leaves alpha untouched, recovers beta, and preserves beta's failed attempt.
5. A distinct fresh receiver invocation checks beta's payload and creates its own readproof.
6. A fresh status invocation reconstructs both states solely from the original packet path and output directory. Each destination has its own attempt and ACK record, not one global success boolean pretending to be two acknowledgments.

The receiver is an independently invoked **local process on the same machine**, not an independent NAS host, authorized provider session, CoStead consumer, GitHub receiver, third-party identity, or human acceptance. The static `reader` label describes the test CLI, not verified physical host identity. `STOP` (a local sentinel in the selected output root) prevents subsequent dispatch or ACK; it is a fixture-level revocation test, not a deployed global kill switch. Source modification, mismatched readproof and unexpected destinations fail closed. No external network calls, emails, messages, model invocations, device access, or provider changes.

## Reproduce

From the repository root:

```sh
python3 -B -m unittest discover -s experiments/coall_golden_braid_r0 -p 'test_golden_braid.py' -v
# Or run the explicit first-failure/then-repair scenario, using a new empty directory:
PACKET=experiments/coall_golden_braid_r0/packet.json
RUN_DIR="$(mktemp -d)"
python3 experiments/coall_golden_braid_r0/golden_braid.py dispatch --packet "$PACKET" --root "$RUN_DIR" --fail test-beta
python3 experiments/coall_golden_braid_r0/golden_braid.py receive --packet "$PACKET" --root "$RUN_DIR" --dest test-alpha
python3 experiments/coall_golden_braid_r0/golden_braid.py dispatch --packet "$PACKET" --root "$RUN_DIR"
python3 experiments/coall_golden_braid_r0/golden_braid.py receive --packet "$PACKET" --root "$RUN_DIR" --dest test-beta
python3 experiments/coall_golden_braid_r0/golden_braid.py status --packet "$PACKET" --root "$RUN_DIR"
```

Do not point this fixture at personal directories or sensitive source material. The fixture only demonstrates a local contract. The ephemeral test directory is its own collision domain, **not** independent failure-domain persistence.

## Reconciliation / issue #317

| Acceptance item | State for this scope | Exact meaning |
|---|---|---|
| Surface inventory | PARTIAL | Two local test directories; GitHub and CoStead known as candidates, real receiver access not proven by this test |
| Canonical packet | PASS_SYNTHETIC | `packet.json`, source identity and normalized schema validated |
| One input, two destinations | PASS_LOCAL | Two local file payloads and delivery attempts, not two external transports |
| Per-destination receipts | PASS_LOCAL | Distinct recipient readback files, bytes+SHA-256 bound; no independent machine ACK |
| Failure/recovery and dedupe | PASS_LOCAL | One deliberate beta failure, preserved attempt and alpha no-overwrite recovery |
| Unified status | PASS_LOCAL | `status` reconstructs each state with nonclaims and source hash |
| Fresh-session recovery | PASS_FRESH_PROCESS_ONLY | Separate process uses packet+output directory; ChatGPT tab recovery not tested |
| Provider/device integrations | HELD | No credentials, other sessions, NAS consumer, external outreach or actual global broadcast |
| UX / benefit | NOT_TESTED | No real first-time user, dashboard or independently measured benefit |

## Next proof gate

Bind **one actual authorized receiver** with current source head, receiver-specific authority, independent execution identity and exact-object readproof. Then bind a second independent destination, induce a real but safe failure and verify recovery without losing prior receipts. Keep issue #317 open until its real cross-surface acceptance criteria are evidenced. Do not promote this synthetic canary into `PICKED_UP`, `INTEGRATED` or `COEX` for any external system.

`LOCAL_RECEIVER_NE_INDEPENDENT_HOST | LOCAL_ACK_NE_GLOBAL_SYNC | HASH_NE_SEMANTIC_TRUTH | RECEIPT_NE_BENEFIT | NO_CREDENTIALS | NO_OUTREACH | NO_CONSEQUENTIAL_EFFECTS`
