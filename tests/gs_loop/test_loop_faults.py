import unittest
from dataclasses import dataclass

"""Isolated fault tests: in-memory only; not X2 integration or durable receipts."""

@dataclass
class Receipt:
    work_id: str
    event_id: str
    epoch: int
    effect: str

class EffectLedger:
    def __init__(self):
        self.epochs = {}
        self.receipts = {}
        self.effects = []
    def elect(self, work_id):
        self.epochs[work_id] = self.epochs.get(work_id, 0) + 1
        return self.epochs[work_id]
    def commit(self, receipt):
        if self.epochs.get(receipt.work_id) != receipt.epoch:
            return 'FENCED'
        old = self.receipts.get(receipt.event_id)
        if old is not None:
            return 'REPLAY' if old == receipt else 'CONFLICT'
        self.receipts[receipt.event_id] = receipt
        self.effects.append(receipt.effect)
        return 'COMMITTED'

class FaultTests(unittest.TestCase):
    def test_duplicate_delivery_no_duplicate_effect(self):
        l=EffectLedger(); e=l.elect('w'); r=Receipt('w','event',e,'notify')
        self.assertEqual(l.commit(r),'COMMITTED')
        self.assertEqual(l.commit(r),'REPLAY')
        self.assertEqual(l.effects,['notify'])
    def test_stale_worker_after_handoff(self):
        l=EffectLedger(); old=l.elect('w'); new=l.elect('w')
        self.assertEqual(l.commit(Receipt('w','late',old,'unsafe')),'FENCED')
        self.assertEqual(l.commit(Receipt('w','fresh',new,'safe')),'COMMITTED')
        self.assertEqual(l.effects,['safe'])
    def test_conflicting_receipt_rejected(self):
        l=EffectLedger(); e=l.elect('w')
        self.assertEqual(l.commit(Receipt('w','id',e,'A')),'COMMITTED')
        self.assertEqual(l.commit(Receipt('w','id',e,'B')),'CONFLICT')
        self.assertEqual(l.effects,['A'])
    def test_no_election_no_effect(self):
        l=EffectLedger()
        self.assertEqual(l.commit(Receipt('w','id',1,'unsafe')),'FENCED')
        self.assertEqual(l.effects,[])

if __name__ == '__main__': unittest.main(verbosity=2)
