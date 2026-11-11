"""Offline tests for CoFront public verifier."""
import hashlib
import unittest
from cofront_public_consumer import git_blob_sha, verify

class ConsumerTests(unittest.TestCase):
    def test_git_blob_hash(self):
        self.assertEqual(git_blob_sha(b"hello\n"), hashlib.sha1(b"blob 6\0hello\n").hexdigest())

    def test_matching(self):
        payload = b"public evidence"
        sha = git_blob_sha(payload)
        m = {"source_refs":[{"id":"a","path":"docs/Evolution/a.json","blob_sha":sha}]}
        r = verify(m, lambda path: payload)
        self.assertTrue(r["passed"])
        self.assertEqual(len(r["sources"]),1)

    def test_mismatch_fails_closed(self):
        m = {"source_refs":[{"id":"a","path":"docs/Evolution/a.json","blob_sha":"0"*40}]}
        self.assertFalse(verify(m, lambda path: b"changed")["passed"])

    def test_unsafe_path_rejected(self):
        m = {"source_refs":[{"id":"a","path":"docs/Evolution/../../private","blob_sha":"0"*40}]}
        with self.assertRaises(ValueError):
            verify(m, lambda path: b"data")

    def test_empty_manifest_fails(self):
        self.assertFalse(verify({"source_refs":[]},lambda path: b"")["passed"])

if __name__ == "__main__":
    unittest.main()
