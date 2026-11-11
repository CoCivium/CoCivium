"""CoTalkItOut R0: deterministic decision gate, not an autonomous chat or authority."""
from dataclasses import dataclass

@dataclass(frozen=True)
class Case:
    evidence_conflict: bool = False
    interface_unknown: bool = False
    cheap_reversible_test: bool = False
    irreversible_effect: bool = False
    authority_proven: bool = False
    progress_delta: bool = False
    discussion_rounds: int = 0

def decide(c: Case):
    if c.irreversible_effect and not c.authority_proven:
        return "HOLD_FOR_AUTHORITY"
    if c.cheap_reversible_test:
        return "TEST_FIRST"
    if c.evidence_conflict or c.interface_unknown:
        if c.discussion_rounds >= 2 and not c.progress_delta:
            return "SUSPEND_UNTIL_NEW_EVIDENCE"
        return "BOUNDED_COTALKITOUT"
    return "PROCEED_WITH_VERIFICATION"

if __name__ == "__main__":
    import unittest
    class Tests(unittest.TestCase):
        def test_test_before_talk(self):
            self.assertEqual(decide(Case(interface_unknown=True, cheap_reversible_test=True)), "TEST_FIRST")
        def test_authority_gate(self):
            self.assertEqual(decide(Case(irreversible_effect=True)), "HOLD_FOR_AUTHORITY")
        def test_talk_on_unknown(self):
            self.assertEqual(decide(Case(interface_unknown=True)), "BOUNDED_COTALKITOUT")
        def test_no_progress_suspends(self):
            self.assertEqual(decide(Case(evidence_conflict=True, discussion_rounds=2)), "SUSPEND_UNTIL_NEW_EVIDENCE")
        def test_new_evidence_reopens(self):
            self.assertEqual(decide(Case(evidence_conflict=True, discussion_rounds=2, progress_delta=True)), "BOUNDED_COTALKITOUT")
    unittest.main(verbosity=2)
