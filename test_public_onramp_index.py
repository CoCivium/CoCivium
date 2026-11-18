"""Offline negative/positive controls for the 1,000-page manifest builder."""
import unittest
from scripts.build_public_onramp_index import eligible, gather, render, topic_for

def fake_fetch(url):
    if url.endswith("/repos/CoCivium/CoCivium"):
        return {"private": False, "default_branch": "main"}
    if url.endswith("/branches/main"):
        return {"commit": {"sha": "a" * 40}}
    if "/git/commits/" in url:
        return {"tree": {"sha": "0" * 40}}
    if "/git/trees/" in url:
        return {"truncated": False, "tree": [
            {"type": "blob", "path": "docs/Onramp/hello.md", "sha": "b" * 40, "size": 100},
            {"type": "blob", "path": "private/notes.md", "sha": "c" * 40, "size": 100},
            {"type": "blob", "path": "docs/Architecture/intro.html", "sha": "d" * 40, "size": 300},
            {"type": "blob", "path": "docs/credentials/login.json", "sha": "e" * 40, "size": 100},
            {"type": "blob", "path": "bin/model.bin", "sha": "f" * 40, "size": 400},
        ]}
    raise AssertionError("unexpected request "+url)

class IndexContractTest(unittest.TestCase):
    def test_exact_pinned_urls_and_exclusions(self):
        rows = gather(fetch=fake_fetch, repos=("CoCivium/CoCivium",))
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["topic"], "Architecture")
        self.assertIn("/blob/" + "a"*40 + "/",rows[0]["url"])
        self.assertTrue(all("/private/" not in r["url"] for r in rows))
        self.assertEqual(rows[0]["blob_sha"], "d"*40)

    def test_never_claim_1000_when_2(self):
        rows=gather(fetch=fake_fetch, repos=("CoCivium/CoCivium",))
        with self.assertRaisesRegex(RuntimeError, "INSUFFICIENT_VERIFIED"):
            render(rows,1000)

    def test_exclude_risky_paths(self):
        for path in ("private/s.md", "docs/secrets/x.json", "docs/.cache/info.md",
                     "docs/contacts/people.md", "bin/model.bin"):
            self.assertFalse(eligible(path, 100),path)
        self.assertFalse(eligible("docs/valid.md", 3_000_000))
        self.assertTrue(eligible("docs/valid.md", 20))

    def test_truncated_tree_holds(self):
        def truncated(url):
            x=fake_fetch(url)
            if "/git/trees/" in url:
                x["truncated"]=True
            return x
        with self.assertRaisesRegex(RuntimeError,"TRUNCATED"):
            gather(fetch=truncated,repos=("CoCivium/CoCivium",))

    def test_nonpublic_repository_holds(self):
        def private(url):
            x=fake_fetch(url)
            if url.endswith("/repos/CoCivium/CoCivium"):
                x["private"]=True
            return x
        with self.assertRaisesRegex(RuntimeError,"PUBLIC_REPOSITORY"):
            gather(fetch=private,repos=("CoCivium/CoCivium",))

if __name__ == "__main__":
    unittest.main()
