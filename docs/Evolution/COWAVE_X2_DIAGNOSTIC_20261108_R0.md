# CoWave diagnostic interpretation R0

Source: X2 PowerShell transcript supplied 2026-11-08, waves 13:50:08 and 13:50:46 local.

## Observed
- Windows PowerShell 7.6.9.
- Current directory C:\\Users\\Owner; not a Git repository.
- Relative contract file absent from that directory.
- Python 3.14 reports no module named pytest.
- First hash command failed due to invalid Get-FileHash pipeline binding.
- Second wave used a .NET SHA-256 helper and explicitly skipped tests.
- Both receipts are FAILED_WITH_EVIDENCE; neither is test success.
- A GitHub page open in a browser does not prove a local clone.
- X2 is visibly running; remote desktop bridge connection is a separate issue.

## Corrected procedure
1. Discover an actual local repository path rather than assuming the current directory.
2. If a local repository is absent, report ABSENT, do not silently clone or install.
3. For the existing stdlib test files, run Python -m unittest discover, not pytest.
4. Capture the process exit code explicitly; zero tests collected is a failure.
5. Hash the actual captured output with .NET SHA-256 and preserve the raw evidence securely.
6. Set receipt status only from verified preconditions, exit code, and nonzero test count.
7. Do not self-declare independent verification or invent lease epochs.

## Open
- Local clone discovery
- Actual CI run verification
- Live receiver acknowledgment
- >24h durable Seed survival
- Independent verifier and automatic cross-session handoff

Status: PUBLIC DIAGNOSTIC RECORD, not proof of runtime repair.
