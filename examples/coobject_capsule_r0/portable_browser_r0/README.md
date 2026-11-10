# CoObject+ Portable Browser Prodlet R0 | Whole file, honest recovery

**State:** `PUBLIC_SAFE_ADDENDUM_TO_DRAFT_PR_446__NOT_DEPLOYED_NOT_CANON_NOT_END_USER_QUALIFIED`  
**Purpose:** Turn the CoObject/OVP recovery idea into a complete *offline browser* task accessible without a running CoAll daemon. A receiver selects one actual file, creates a source-hashed portable JSON capsule with two same-archive byte copies, re-imports it in a clean browser context, simulates copy loss, and downloads the restored exact bytes. No data leaves the browser except through explicit user downloads.

## One complete task

1. Open `index.html` in a browser supporting secure-context WebCrypto SHA-256. No server, login, model, service, install, live network or local storage is needed. A browser denying secure cryptography must fail closed rather than accept an unchecked package.
2. Select a local file up to **256 KiB**. Click **Package CoObject**. The browser computes SHA-256 from the actual selected bytes, includes source name, size, time *as reported by this local clock*, and a minimal purpose/rights/recovery manifest.
3. Export the JSON capsule. Reopen the same `index.html` in a fresh session or a different browser and explicitly import the JSON. Import must check exact object schema, field set, digest shape, size, byte copies, and authority/privacy constraints.
4. Simulate loss of copy A. The status visibly degrades and a surviving matching copy can be restored using an ordinary browser download. Corrupt both copies and restore becomes unavailable. No overwrite occurs through a privileged filesystem API.
5. Compare with **Simple copy baseline**, a direct download of the same selected source file. Export a local structural receipt if desired. No receipt is a remote ACK.

The HTML is a usable standalone file and includes its CSS, JS and text. The duplicated payload bytes are wholly inside one JSON package: **one package failure loses both**. A content digest detects inconsistency relative to its manifest, but does not identify/authenticate the original producer. Neither transferring a file between two browsers nor seeing a successful browser test is proof of independently hosted custody, a deployed service, external receiver acceptance, or X2.

### Contract crosswalk

- **CoObject:** one content-derived ID; explicit kind/purpose and bytes; source hash; scope; recovery limit; unknown origin; no effects.
- **CoGrace:** no bytes = `EMPTY`; both copies match = `READY_LOCAL_TWO_COPIES`; one surviving valid copy = `DEGRADED_ONE_COPY`; both lost or corrupted = `HELD_NO_VALID_BYTES`; forged manifest = `HELD_INVALID_CAPSULE`.
- **OVP:** a whole *file transport and recovery* task, not a complete native RickBar/Ollama user task. Task still needs independent user acceptance.
- **CoOrb/CoSpeedo:** the gauge shows byte-integrity states and **UNKNOWN** external ACK/user benefit; no simulated machine-health scores or fabricated live telemetry.
- **CoSeren/CoQuestionDrive:** new useful questions about transfer and failure modes may follow, but this app does not launch any workers or promote hypotheses.
- **CoMVP/CoLockStep:** preserved stable original objects and no automatic release/merge; this draft is additive.

## Honest baseline and efficiency

A raw 66-byte binary fixture produced a **876-byte** JSON capsule in the initial local test: an approximately 13.27x transfer-size cost, before the app HTML. The simple direct download retained exactly 66 bytes. A single file copy is cheaper and often preferable. Any claim that this design is 'better' needs a receiver-relative test of corruption detection, portability, actual recovery, time, accessibility, storage and human effort against that strong baseline. No such real-user comparison is claimed.

## Security/privacy ceilings

- `Content-Security-Policy: default-src 'none'; connect-src 'none'`. No `fetch`, analytics, workers, storage API, service worker, outbound messages, code execution of payload, or hidden release. The browser may require a suitable secure context for native WebCrypto; if not, packing and inspection remain disabled.
- The reader explicitly chooses input/import and download. Do **not** use private or sensitive information without understanding that downloaded capsules contain the original bytes twice in plain text base64, and will exist on the local device.
- Filename sanitization is for suggested download names only, not a filesystem sandbox. Import checks strict manifest schema and caps payload size to keep operation bounded. Source metadata from the user remains self-asserted. Browser security remains dependent on the host browser and filesystem.
- Reset drops in-memory references but does not guarantee secure memory erasure, browser download deletion, privacy on a shared machine, or removal of old copies.
- SHA-256 checks bytes, not publisher identity or legitimate rights; a motivated source actor can replace both payload and hash.

## Browser QA

`test_browser.py` is a **17-case real Chromium UI interaction test** using synthetic file data. It verifies the export from one context and import into a fresh isolated context, exact file restoration, fail-closed authorization/schema/corruption tests, reset, mobile layout at 390px, no external requests or JavaScript errors, and the direct-copy baseline. Test screenshots are evidence of **synthetic browser UI**, not real device state.

The local execution container blocks browser navigation (`file://` and all synthetic HTTPS URLs), so the local test loads the HTML in a blank Chromium page and supplies **test-only Python SHA-256** for `crypto.subtle`; it does not establish the native browser cryptography path. The GitHub CI job must run with `COOBJECT_BROWSER_MODE=native`, load the actual `file://` source, and use **Chromium's native WebCrypto without the shim**. Only a successful CI job can qualify that narrower claim. Never count local shim and CI native tests as independent human acceptance.

Local run in this sandbox (needs Python Playwright and `/usr/bin/chromium`):

```sh
python3 test_browser.py
```

GitHub CI run (Playwright and installed Google Chrome):

```sh
COOBJECT_BROWSER_MODE=native python3 test_browser.py
```

This test invokes real UI controls and samples DOM state; it is not a static parser. It writes `browser_qa.json`, `desktop_portable_qa.png` and `mobile_portable_qa.png` only under the test directory. The screenshots are not production releases.

## Existing proofs and next independent receiver gate

- [CoObject/OVP draft PR #446](https://github.com/CoCivium/CoCivium/pull/446), [source-level four-job cross-job receipt and independent witness](https://github.com/CoCivium/CoCivium/actions/runs/42770867550).
- [CoObject vitality](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COOBJECT_VITALITY_METABOLISM_R0_20261027.md), [CoGrace](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COGRACE_PHASE_RELATIVE_STEWARDSHIP_R0_20261101.md), [CoMVP/CoLockStep](https://github.com/CoCivium/CoCivium/blob/main/docs/Architecture/COMVP_COLOCKSTEP_SOURCE_RELEASE_R0_20261109.md).
- Existing [CoDemoWow Truth Gate R1](https://github.com/CoCivium/CoCivium/blob/main/examples/codemow/truth-gate-r1.html) owns the existing historical CI truth gauge and was not replaced or copied. This prodlet owns a distinct real-file transfer/reconstruction interaction.

**Next gate:** Have an independent, consenting receiver attempt this genuine task against a direct file copy; measure total time, mistakes, successful restoration, comprehension, and whether the added structure was worth its complexity. For X2 or CoStead, separately prove a real host/runtime and durable WorkID, restart, and actual source/receiver custody. No automatic cross-account relay or unapproved execution.

`WHOLE_TASK_NE_WHOLE_WORLD | CONTENT_DIGEST_NE_AUTHENTICITY | TWO_COPIES_ONE_JSON_NE_INDEPENDENT_REDUNDANCY | BROWSER_QA_NE_HUMAN_ACCEPTANCE | FILE_INPUT_NE_RELEASE_PERMISSION | SOURCE_CI_NE_X2_RUNTIME`