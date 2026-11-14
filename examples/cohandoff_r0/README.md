# CoOmni local two-view handoff R0 - public-safe demonstration

State: `BOUNDED_BROWSER_LOCAL_DEMO__NOT_PROVIDER_SYNC__NOT_X2_RUNTIME__NOT_COLD_RESTORE`

This is an **additive implementation candidate** for the existing source contract
[`ai/onramp/coomni-cross-window-handoff-r0.json`](../../ai/onramp/coomni-cross-window-handoff-r0.json).
It does not create a second shared CoWorkObject authority or machine-intake root.

## Try

In a local checkout, run `python3 -m http.server 8765` at repository root.
Open `http://127.0.0.1:8765/examples/cohandoff_r0/index.html` in a modern browser.
Click **Open receiver views**, or use the explicit receiver links if popups are blocked.
Send the built-in fictional work item once to both role views. Each receiver must
show a role-local ACK with its own cursor. Click **Replay last** and verify
`STALE_OR_REPLAY` on the appropriate receiver. Click **Stop session** and verify
no further send is available. The sender's acknowledgement panel must never
claim an ACK merely because a packet was posted.

To run the exact inline source in a synthetic channel/DOM harness without external packages, run:
`node examples/cohandoff_r0/smoke.cjs`. It verifies two SHA-256 ACKs, stale
replay HELD, role-targeted delivery and STOP.

To attempt actual browser dual-window acceptance, run:
`python3 examples/cohandoff_r0/test_browser.py`. This optional test needs the
Playwright Python package and Chromium. In the originating container, Chrome
returned `net::ERR_BLOCKED_BY_ADMINISTRATOR` for loopback and file URLs; the
real-browser test was therefore **HELD**, not passed.

## Trust boundaries and limits

- `BroadcastChannel` reaches only same-origin browser contexts sharing this
  random channel identifier. Not ChatGPT tab contexts, OS apps, devices, LAN,
  cloud providers, or public users.
- No network `fetch`, storage, clipboard, microphone, screen capture, model call,
  background daemon, authentication, or public send is performed.
- The session ID is not a secret/authentication mechanism. Pages sharing origin
  and identifier can read role messages. **Only fictional/public-safe content.**
- User initiates every send. UX and Theory each receive role-scoped packets,
  with independent per-role sequence and exact JSON SHA-256 acknowledgement.
- Sender checks the ack digest against its pending packet before indicating
  receiver acceptance. Receiver rejects replays/gaps; it does not persist cursors.
- A failed send, lost window, restart, or offline receiver can lose volatile
  state. No recovery or durable custody is claimed.
- A browser fixture PASS is not an X2 hardware run, provider-session sync,
  independent human acceptance, cross-origin privacy audit or CoEx.

**Next evidence gate:** a qualified X2 run and one separate authorized receiver
with exact-object readproof, followed by restart/recovery and privacy negative
checks. Never promote this source to a public installer by inference.