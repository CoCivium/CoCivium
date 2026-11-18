import copy
import importlib.util
import unittest
from pathlib import Path

path=Path(__file__).with_name("copre_public_readback_r0.py")
spec=importlib.util.spec_from_file_location("copre_public_readback_r0",path)
mod=importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def fetched(x):
    return {"state":"FETCHED_UNQUALIFIED","http_status":200,"sha256":x,"byte_count":50,"final_url":"https://example.org/"}

class MirrorReadbackTest(unittest.TestCase):
    def test_no_targets_do_not_pass(self):
        r=mod.classify(fetched("a"),[{"id":"site",**fetched("b")}])
        self.assertFalse(r["all_three_identical_verified"])
        self.assertEqual(r["targets"][0]["exact_source_equivalence"],"UNPROVEN")

    def test_identical_bytes_are_only_byte_equivalence(self):
        r=mod.classify(fetched("a"),[{"id":"site",**fetched("a")}])
        self.assertTrue(r["all_three_identical_verified"])
        self.assertFalse(r["targets"][0]["independent_receiver_ack"])
        self.assertEqual(r["targets"][0]["owner_control"],"UNPROVEN")
        self.assertFalse(r["receiver_pickup"])

    def test_unavailable_source_never_matches(self):
        r=mod.classify({"state":"HELD_TRANSPORT","sha256":None},[{"id":"a","state":"HELD_TRANSPORT","sha256":None}])
        self.assertFalse(r["all_three_identical_verified"])

    def test_http_404_no_mirror(self):
        r=mod.classify(fetched("a"),[{"id":"a","state":"HELD_HTTP_ERROR","http_status":404,"sha256":None}])
        self.assertEqual(r["targets"][0]["exact_source_equivalence"],"UNPROVEN")

    def test_no_mutation(self):
        xs=[{"id":"a",**fetched("a")}]
        old=copy.deepcopy(xs)
        mod.classify(fetched("a"),xs)
        self.assertEqual(xs,old)

    def test_three_distinct_targets(self):
        self.assertEqual(len(mod.TARGETS),3)
        self.assertEqual(len(set(url for _,url in mod.TARGETS)),3)

    def test_pinned_sha_is_full_git_commit(self):
        self.assertRegex(mod.PINNED_COMMIT,r"^[0-9a-f]{40}$")

    def test_no_network_in_unit_tests(self):
        self.assertTrue(mod.classify(fetched("a"),[])["source_is_read_not_executed"])

if __name__=="__main__":
    unittest.main()
