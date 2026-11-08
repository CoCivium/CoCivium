import unittest
from collections import deque

"""Isolated GS-Loop guard proof; not integrated with X2 or CoBar."""

class LoopGuard:
    def __init__(self, max_repeats=2, max_steps=12, window=5):
        self.max_repeats=max_repeats
        self.max_steps=max_steps
        self.history=deque(maxlen=window)
        self.steps=0
        self.state='ACTIVE'
    def observe(self, fingerprint, verified_progress=False):
        if self.state!='ACTIVE': return self.state
        self.steps+=1
        if verified_progress:
            self.history.clear()
            self.steps=0
            return 'PROGRESS'
        self.history.append(fingerprint)
        if self.history.count(fingerprint)>self.max_repeats:
            self.state='SUSPENDED_REPETITION'
        elif self.steps>=self.max_steps:
            self.state='SUSPENDED_BUDGET'
        return self.state
    def resume(self, changed_trigger):
        if not changed_trigger: return False
        self.history.clear(); self.steps=0; self.state='ACTIVE'
        return True

class TestLoopGuard(unittest.TestCase):
    def test_repeated_ack_suspends(self):
        g=LoopGuard()
        self.assertEqual([g.observe('ack') for _ in range(3)][-1], 'SUSPENDED_REPETITION')
    def test_progress_resets_repetition(self):
        g=LoopGuard()
        g.observe('same'); g.observe('same')
        self.assertEqual(g.observe('receipt:verified',True),'PROGRESS')
        self.assertEqual(g.observe('same'),'ACTIVE')
    def test_budget_stops_unique_spinning(self):
        g=LoopGuard(max_steps=4)
        self.assertEqual([g.observe(str(i)) for i in range(4)][-1], 'SUSPENDED_BUDGET')
    def test_resume_requires_changed_trigger(self):
        g=LoopGuard(); [g.observe('ack') for _ in range(3)]
        self.assertFalse(g.resume(False))
        self.assertTrue(g.resume(True))
        self.assertEqual(g.observe('new'),'ACTIVE')
    def test_suspended_cannot_self_resume(self):
        g=LoopGuard(); [g.observe('ack') for _ in range(3)]
        self.assertEqual(g.observe('new',True),'SUSPENDED_REPETITION')

if __name__=='__main__': unittest.main(verbosity=2)
