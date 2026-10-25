# CoThumb+ / CoOmniIO+ R1: local rich-payload rehearsal

**State:** Runnable isolated Python candidate. NO X2 device binding, NO hardware ACK, NO external provider, NO live CoOrb/CoMx/CoStead integration, NO background agent service.

The existing CoThumb R0 X2 self-test is separately recorded as `PASS_SELF_TEST__HELD_PHYSICAL_BUTTON`. The existing public draft PR #218 is a **preview-only** browser moustache. This R1 candidate adds a different, complementary proof: a user-selected real file can be copied and cryptographically indexed with chunk hashes, without an LLM context dump, intercepted keystrokes, or external transmission.

## Task-first operation

On a host with Python 3 (no third-party libraries):

```sh
python3 cothumb.py capture --file /path/to/user-selected-file --output-dir ./capsules --intent inspect
python3 cothumb.py verify --capsule ./capsules/cothumb-YOUR-GENERATED-ID --max-workers 3
```

Use `--verify-local` with the `capture` command to run all three local checks automatically after the selected-file capture. The optional keyboard/gesture adapter uses this option for one-gesture local completion.

The first command creates a private local directory with a redacted `manifest.json`, source bytes under `objects/`, self-contained `bundle.copack.zip`, and a local `receipt.json`. The second runs three deterministic local checks in at most three worker threads, preserving another uniquely named receipt. The result is **a local verified package**, not an AI analysis or receiver ACK.

### Windows keyboard/gesture adapter, disabled until run

`CoThumb-KeyboardFallback.ahk` uses AutoHotkey **v2** and listens for **Ctrl+Alt+Shift+F12** only after explicitly launching the script. It presents an ordinary file picker, calls Python 3 using Windows `py -3` (not yet verified on X2), and creates and locally verifies a capsule in a local `capsules` folder. No paste, upload or unattended provider task occurs. Closing the script exits the hook; removing the mapping restores ordinary input. No AHK listener is installed by this package.

If the Logitech device and Logi Options+ are confirmed, its thumb *gesture* can optionally emit the same chord. This avoids assuming that a dedicated Logitech gesture is `XButton1`, `XButton2` or `MButton`; these names refer to different input events on different configurations. Leave browser middle-click and OS navigation alone until observed and collision-tested. Verify Windows/Python/Options+/AutoHotkey versions and device ID with the user-present X2 session before treating any binding as active.

## Payload contract

- 1–8 regular non-symlink input files, **explicitly selected**, each <=128 MiB, total <=256 MiB.
- Streamed exact bytes and 4 MiB SHA-256 chunk hashes. No raw filenames or original absolute paths in shareable manifest.
- Archive retains exact original file bytes. **It is not encrypted. Do not upload/share it unless content/rights are reviewed.**
- `mime_hint_unverified` is a *hint*, not a verified media type.
- Authority for outbound send, execution, credential use and publication is NONE; receiver ACK is NONE.
- Three parallel deterministic checks: schema/path privacy; byte/chunk hashes; effect/receiver authority.
- Finite worker/thread limits; no recursion; no web, clipboard access, model API, account operation, or device capture.

## Why this is not unlimited context

Rich objects remain outside each model's finite context window. An authorized receiver can request selective chunks or transformations after capability, privacy and cost checks. This R1 does not create a remote attachment API or automatic model calls. One file/capsule may be indexed to many **logical** subscribers without copying content to all of them.

### Candidate eventual provider-neutral worker contract

`CoInputEvent -> consent/auth envelope -> selected object -> content-addressed capsule -> lease/budget/queue -> permitted agent/model/tool -> deterministic fan-in + independent challenge -> receipt -> user-visible result or separate authorized apply`

For material effects, a real receiver must enforce capability-scoped grants, expiry, revocation, destination identity, user-visible stop and independent error/side-effect recovery. The physical device event is an **invocation**, not blanket permission to send messages, initiate financial transactions, activate microphones/cameras, change accounts, or deploy websites.

## What was tested

See `tests/test_cothumb.py` and the generated `test_receipt.json`. Bounded local Python execution exercises actual 400+ KB binary bytes, content integrity, privacy redaction, finite budgets, tamper rejection, side-effect boundaries and concurrency controls. These do not test Windows, AutoHotkey, Logitech Options+, user experience, or X2 runtime.

## Source/evidence relations

- [CoResourceAttractor+ R0](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/CORESOURCE_ATTRACTOR_R0.md)
- [CoPredictiveInput+ shadow R0](https://github.com/CoCivium/CoCivium/blob/main/ai/co-predictive-input-r0.json)
- [CoGoAll receiver R3 with X2 CoThumb R0 self-test](https://github.com/CoCivium/CoCivium/blob/main/docs/publishing/cogoall-evergreen-receivers-r3.json)
- [CoThumb preview-only draft #218](https://github.com/CoCivium/CoCivium/pull/218)

**Next real gate:** Restore the authorized X2 remote connection, inspect the current CoThumbR0 PowerShell script and actual mouse/Options+ configuration **read-only**, then test one opt-in keyboard fallback before electing a physical binding. Do not install or bind hardware based solely on an off-device self-test.
