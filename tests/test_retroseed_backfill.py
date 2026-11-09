"""Synthetic CoRetroSeed backfill tests. No private files or chats are ingested."""
import hashlib
import unittest

def ingest(items, existing=None):
    index = dict(existing or {})
    events = []
    for item in items:
        if not item.get("authorized", False):
            events.append((item["id"], "SKIPPED_UNAUTHORIZED"))
            continue
        if not item.get("source_ref") or not item.get("content"):
            events.append((item["id"], "SKIPPED_NO_PROVENANCE"))
            continue
        digest = hashlib.sha256(item["content"].encode("utf-8")).hexdigest()
        key = (item["source_ref"], digest)
        if key in index:
            events.append((item["id"], "ALREADY_INGESTED"))
            continue
        index[key] = {
            "source_ref": item["source_ref"],
            "digest": digest,
            "custody": item["custody"],
            "candidate_state": "UNVERIFIED_INSPIRATION",
            "promotion_authorized": False,
        }
        events.append((item["id"], "CANDIDATE_RECORDED"))
    return index, events

class RetroSeedTests(unittest.TestCase):
    def setUp(self):
        self.item = {"id":"diagram-1","source_ref":"public:diagram-1",
                     "content":"Box A relates to Box B","authorized":True,"custody":"public"}

    def test_idempotent_backfill(self):
        index, events = ingest([self.item])
        index2, events2 = ingest([self.item], index)
        self.assertEqual(index, index2)
        self.assertEqual(events2[0][1], "ALREADY_INGESTED")

    def test_revision_is_new_version(self):
        index, _ = ingest([self.item])
        revised = dict(self.item, content="Box A contradicts Box B")
        new_index, events = ingest([revised], index)
        self.assertEqual(len(new_index), 2)
        self.assertEqual(events[0][1], "CANDIDATE_RECORDED")

    def test_private_unconsented_skipped(self):
        private = dict(self.item, authorized=False, custody="private")
        index, events = ingest([private])
        self.assertEqual(len(index), 0)
        self.assertEqual(events[0][1], "SKIPPED_UNAUTHORIZED")

    def test_missing_source_not_promoted(self):
        missing = dict(self.item, source_ref="")
        index, events = ingest([missing])
        self.assertFalse(index)
        self.assertEqual(events[0][1], "SKIPPED_NO_PROVENANCE")

    def test_candidate_never_self_promotes(self):
        index, _ = ingest([self.item])
        record = next(iter(index.values()))
        self.assertEqual(record["candidate_state"], "UNVERIFIED_INSPIRATION")
        self.assertFalse(record["promotion_authorized"])

if __name__ == "__main__":
    unittest.main(verbosity=2)
