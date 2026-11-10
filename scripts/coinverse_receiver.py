#!/usr/bin/env python3
"""Independent read-only CoInverse receiver. Python standard library only."""
import argparse
import datetime as dt
import hashlib
import json
import pathlib
import sys
import urllib.request

BASE = "https://raw.githubusercontent.com/CoCivium/CoCivium/main/"
SEEDS = {
    "docs/Evolution/COPRE_DRAFT_READY_CYCLE_R0.json": "522a45140d1c19b8f58987fa8044c6fdceffcb11",
    "docs/Evolution/COINVERSE_BENCHMARK_GENERATIONAL_STEWARDSHIP_R0.json": "863d1396d1b320bf5bd51e8d05894c65f39f8636",
}
def blob_sha(data):
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()

def read_source(path, root=None):
    if root is not None:
        return (pathlib.Path(root) / path).read_bytes()
    req = urllib.request.Request(BASE + path, headers={"User-Agent": "CoInverseReceiver/0.1"})
    with urllib.request.urlopen(req, timeout=20) as response:
        return response.read()

def receive(root=None, prior=None, now=None):
    now = now or dt.datetime.now(dt.timezone.utc)
    checks = []
    for path, expected in SEEDS.items():
        item = {"path": path, "expected_git_blob_sha1": expected, "source": "local_fixture" if root else BASE + path}
        try:
            raw = read_source(path, root)
            actual = blob_sha(raw)
            parsed = json.loads(raw)
            item.update(actual_git_blob_sha1=actual, sha256=hashlib.sha256(raw).hexdigest(),
                        bytes=len(raw), valid_json=isinstance(parsed, dict), matched=actual == expected)
        except (OSError, ValueError, TimeoutError) as exc:
            item.update(matched=False, error=type(exc).__name__ + ": " + str(exc))
        checks.append(item)
    passed = all(x.get("matched") and x.get("valid_json") for x in checks)
    receipt = {"schema": "cocivium.coinverse.receiver.receipt.r0",
               "observed_utc": now.isoformat(), "receiver": "python_stdlib_independent_process",
               "status": "SOURCE_VERIFIED" if passed else "HOLD",
               "checks": checks, "source_verified": passed,
               "independent_handoff_verified": False,
               "cross_session_sync_verified": False, "survived_24h_verified": False,
               "mirror_verified": False}
    if prior is not None:
        try:
            old = json.loads(pathlib.Path(prior).read_text(encoding="utf-8"))
            old_time = dt.datetime.fromisoformat(old["observed_utc"].replace("Z", "+00:00"))
            elapsed = (now - old_time).total_seconds() / 3600
            previous = {x["path"]: x.get("sha256") for x in old["checks"] if x.get("matched")}
            same = all(x.get("matched") and previous.get(x["path"]) == x.get("sha256") for x in checks)
            receipt["prior_comparison"] = {"elapsed_hours": round(elapsed, 3),
                                            "same_source_digests": same,
                                            "prior_source_verified": old.get("source_verified") is True}
            # 24h continuity means a later independent fetch matches an earlier receipt.
            receipt["survived_24h_verified"] = bool(passed and same and old.get("source_verified") is True and elapsed >= 24)
        except (OSError, ValueError, KeyError, TypeError) as exc:
            receipt["prior_comparison"] = {"error": type(exc).__name__ + ": " + str(exc)}
    return receipt

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", help="offline fixture root; defaults to public GitHub")
    parser.add_argument("--prior", help="previous receipt for 24h comparison")
    parser.add_argument("--output", help="write receipt to JSON file")
    args = parser.parse_args()
    receipt = receive(args.root, args.prior)
    rendered = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        pathlib.Path(args.output).write_text(rendered, encoding="utf-8")
    print(rendered, end="")
    return 0 if receipt["source_verified"] else 2

if __name__ == "__main__":
    sys.exit(main())
