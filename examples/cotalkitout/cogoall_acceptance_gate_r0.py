"""CoGoAll one-seed acceptance gate: no self-certified operational PASS."""
from dataclasses import dataclass
import json
import unittest

REQUIRED = (
    "one_seed", "one_orb", "one_gauge", "one_thumb", "one_time",
    "zero_placeholders", "unattended_wake", "seed_survived_24h",
    "single_fenced_handoff", "independent_receiver_ack",
    "restart_recovery", "cross_session_exchange",
)
@dataclass(frozen=True)
class Evidence:
    claim: str
    status: str
    receipt: str = ""
    observer: str = ""

def evaluate(items):
    by_name = {e.claim: e for e in items}
    checks = {}
    for claim in REQUIRED:
        e = by_name.get(claim)
        if e is None:
            checks[claim] = "MISSING"
        elif e.status != "VERIFIED":
            checks[claim] = "HELD"
        elif not e.receipt or not e.observer:
            checks[claim] = "HELD_NO_EVIDENCE"
        elif claim in ("independent_receiver_ack", "single_fenced_handoff", "cross_session_exchange") and e.observer == "executor":
            checks[claim] = "HELD_SELF_ACK"
        else:
            checks[claim] = "EVIDENCED"
    return {"overall": "PASS" if all(v == "EVIDENCED" for v in checks.values()) else "HELD",
            "checks": checks}

class Tests(unittest.TestCase):
    def test_empty_is_held(self):
        self.assertEqual(evaluate([])["overall"], "HELD")
    def test_claim_without_receipt_held(self):
        self.assertEqual(evaluate([Evidence("one_seed", "VERIFIED")])["checks"]["one_seed"], "HELD_NO_EVIDENCE")
    def test_all_independent_evidence_passes(self):
        es = [Evidence(c, "VERIFIED", "sha256:"+c, "receiver") for c in REQUIRED]
        self.assertEqual(evaluate(es)["overall"], "PASS")
    def test_self_ack_held(self):
        es = [Evidence(c, "VERIFIED", "sha256:"+c, "receiver") for c in REQUIRED]
        es[REQUIRED.index("independent_receiver_ack")] = Evidence("independent_receiver_ack", "VERIFIED", "sha256:a", "executor")
        self.assertEqual(evaluate(es)["checks"]["independent_receiver_ack"], "HELD_SELF_ACK")
    def test_missing_one_holds_all(self):
        es = [Evidence(c, "VERIFIED", "sha256:"+c, "receiver") for c in REQUIRED[:-1]]
        self.assertEqual(evaluate(es)["overall"], "HELD")

if __name__ == "__main__":
    unittest.main(verbosity=2)
