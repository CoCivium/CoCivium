# CoReach Pre-Send Identity Gate R0 | Proof boundary

- Reuses existing CoOrg/CoThread/CoReach/CoRelationshipBraid semantics.
- Pure Python 3.11 stdin-to-stdout pre-send shadow checker; **no Gmail or WhatsApp access in this code**.
- Accepts a declared review envelope, refuses missing/mismatched sender/recipient/thread/speaker/CC/BCC/approval claims.
- Every recipient field, speaker class and transport address requires an authorized upstream verifier. A self-declared TRUE flag is not independent authentication.
- 78 fictional test cases with no actual account addresses or mail copies.
- `HELD` and `READY_FOR_HUMAN_REVIEW_ONLY` are the only output states; never `SEND_ALLOWED`.
- Private Gmail draft audit was conducted in a separate restricted artifact and **must not** be added to public GitHub, issues, commit messages or publications.
- No public publishing, send operation, recipient ACK, send-as alias verification, runtime interception, verified real contact mapping, X2 installation or CoStead recovery is claimed.

Next acceptance target: one *authorized* real unsent Gmail draft in a connected account with exact from/To/Cc/Bcc and reply-to evidence. Reinspect against any material change before human signoff; integration with actual send endpoint is separate.
