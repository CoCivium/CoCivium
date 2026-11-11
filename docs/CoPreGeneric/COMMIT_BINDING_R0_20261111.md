# CoPre generic producer: local Git source binding

Review candidate, 2026-11-11. Extends the existing ReadyCycle WorkID producer; no new Seed, receiver, scheduler, device action or authority root.

The complete unchanged `scripts/CoNarrativeWorkIDR0.py` at base commit `ff2acf209d37038dd7404a70366922f21972dbae`, Git blob `f810759ea326013c5dd43a58f51f1fac72c7da31`, accepted a local `CoPre.md` outside a Git repository with a well-formed nonexistent commit ID (`f` repeated 40 times). Its packet then passed schema validation. This confirms a producer source-binding gap, not a failure of the separate historical-source browser/SQLite bridge.

The producer now checks that the named local object is a commit and that its root `CoPre.md` blob exactly matches the supplied bytes before constructing a packet. Git replace objects are disabled. Missing Git/history stays HELD; no automatic fetch, checkout, rewrite or network request is introduced. The same check applies to CLI verification because it reconstructs the expected packet through `source_packet`.

The existing 11 replay/recovery tests now create real isolated Git fixtures. Six added checks cover nonexistent commits, wrong bytes, a blob presented as a commit, a source outside Git, a valid older commit and forged CLI verification. Existing workflow `.github/workflows/coobject-vitality-r0.yml` already runs this suite and separate producer/reader jobs; no additional workflow or schedule.

Boundary: local Git content binding does not authenticate the repository owner, establish scientific truth, authorize the packet, acknowledge a remote receiver, prove exactly-once external effects or establish 24-hour runtime survival. `validate` and direct `commit_once` remain schema/integrity functions; direct callers must qualify provenance separately. Direct `readback` with a source file retains its hash-only integrity contract; use the CLI or an independently qualified expected packet for local Git binding. Historical objects must be available in the consuming checkout.

The three proposed short routes are independent deployment concerns. This change does not create or certify `CoCivium/CoPreGeneric`, `CoCivium.org/CoPre` or `InSeed.com/Stead`. Existing public bootstrap remains `CoPre.md` in `CoCivium/CoCivium`.
