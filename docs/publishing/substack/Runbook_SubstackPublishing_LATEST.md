# Substack Publishing Runbook (FAIL-CLOSED, SHA-pinned)
UTC: 20260216T143440Z

## Non-negotiables
- Every public pointer is pinned by immutable ID (commit SHA / digest). No /main RAW URLs.
- Publishing is allowed from STAGE only if the post footer explicitly states: "STAGE SHA=..." and includes pinned RAW links.
- After CANON merge, update the Substack post footer to point to CANON pins (do not silently swap sources).

## Minimum publishing workflow (no fancy tooling)
1) Open Substack editor → new post.
2) Paste **Issue_01.md** from the repo Substack pack.
3) Verify headings + bullet lists render correctly.
4) Add a footer block:

> Source-of-truth (pinned):
> - Repo commit SHA: <SHA>
> - RAW Issue: <RAW_URL>
> - RAW README: <RAW_URL>

5) Use SubjectLines.txt; pick one; keep the title stable.
6) Publish (or schedule). Record the post URL in a receipt file (outside the repo if needed).

## Update workflow (after CoPrime merges to canon)
- Edit the existing Substack post (do not republish a “new” copy).
- Replace STAGE SHA footer with CANON SHA footer.
- Keep a small change log line: "Updated pins on YYYY-MM-DD (old SHA → new SHA)."

## Evidence artifacts per publish
- A receipt text file with: UTC, post URL, SHA, RAW pointers, and (optional) screenshot.
- If attachments used: store them in repo and pin them too.
