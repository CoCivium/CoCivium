import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import costretch_r1 as c


class CoStretchTests(unittest.TestCase):
    def test_trillion_address_bounds(self):
        for i in (0, 1, 10, 10**8, 10**12 - 1):
            self.assertEqual(c.encode_index(c.decode_index(i)), i)
        with self.assertRaises(ValueError):
            c.decode_index(c.CARDINALITY)

    def test_queue_is_deterministic(self):
        a = c.run_batch(1, task_count=16)
        b = c.run_batch(4, task_count=16)
        self.assertEqual(a['digest_root'], b['digest_root'])
        self.assertEqual(b['failed'], [])

    def test_retry(self):
        a = c.run_batch(1, task_count=16)
        b = c.run_batch(2, task_count=16, fault_task=7)
        self.assertEqual(a['digest_root'], b['digest_root'])
        self.assertEqual(b['retries'], 1)

    def test_fail_closed(self):
        result = c.run_batch(2, task_count=16, fault_task=7, max_attempts=1)
        self.assertEqual(result['failed'], [7])
        self.assertEqual(result['completed'], 15)

    def test_checkpoint_replay(self):
        root, checkpoint = c.turtle_root(1000, checkpoint_at=500)
        self.assertEqual(root, c.resume_turtle(checkpoint, 500, 1000))

    def test_bad_width_does_not_run(self):
        with self.assertRaises(ValueError):
            c.run_batch(10, task_count=16)


if __name__ == '__main__':
    unittest.main()
