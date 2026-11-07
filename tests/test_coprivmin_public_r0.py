"""CoPrivMin R0 candidate projector tests: synthetic private values only."""
import copy
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path

HERE=Path(__file__).resolve().parents[1]
MODULE=HERE/"scripts"/"CoPrivMinPublicProjectionR0.py"
SPEC=importlib.util.spec_from_file_location("coprivmin_r0",MODULE)
proj=importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(proj)

def fixture():
    return {"schema":"CoCivium.CoPrivMin.CandidateProjection.R0",
            "object_alias":"coathene_public_purpose_r0",
            "object_presence_sensitive":False,
            "intent":"BUILD_REVIEWABLE_CANDIDATE_ONLY",
            "fields":[
              {"field":"question","decision":"PUBLIC_SUMMARY",
               "text":"Why do we have schools, and how might inquiry help?"},
              {"field":"status","decision":"PUBLIC_EXACT",
               "text":"Original private-research-derived candidate, no school status."},
              {"field":"limitation","decision":"PUBLIC_SUMMARY",
               "text":"No child-learning effect, accredited programme or partner is claimed."},
              {"field":"next_test","decision":"PUBLIC_SYNTHETIC",
               "text":"Ask a fictional educator to compare neutral and candidate lessons."},
              {"field":"private_case","decision":"WITHHELD_EXACT",
               "text":"unreleased synthetic secret 1234"},
              {"field":"private_topic","decision":"EXISTENCE_HELD",
               "text":"confidential fictional meeting"},
              {"field":"unknown_item","decision":"UNRESOLVED",
               "text":"unassessed fictional proposal"}
            ]}

class CoPrivMinR0Tests(unittest.TestCase):
    def test_synthetic_candidate_has_no_publication_authority(self):
        result,receipt=proj.validate(fixture())
        self.assertEqual(result["state"],"PRIVATE_REVIEW_NEEDED_NO_RELEASE_AUTHORITY")
        self.assertEqual(result["effects_executed"],0)
        self.assertFalse(receipt["release_authorized"])
        self.assertEqual(result["public_commit_or_receiver_ack"],"NOT_OBSERVED")

    def test_field_level_holds_not_existence_or_count_leaks(self):
        value,receipt=proj.validate(fixture())
        public=json.dumps(value,sort_keys=True)
        for secret in ("unreleased synthetic secret 1234","private_case",
                       "confidential fictional meeting","private_topic",
                       "unassessed fictional proposal","unknown_item"):
            self.assertNotIn(secret,public)
        self.assertEqual(value["protected_field_count"],"NOT_DISCLOSED")

    def test_source_digest_not_copied_into_public_output(self):
        d=fixture()
        d["fields"].append({"field":"private_hash","decision":"WITHHELD_EXACT",
                            "text":"00000000000000000000000000000000"})
        value,receipt=proj.validate(d)
        self.assertNotIn('"private_hash":',json.dumps(value))
        self.assertEqual(value["source_private_hashes"],"NOT_INCLUDED")
        self.assertFalse(receipt["source_input_hash_disclosed"])

    def test_same_sanitized_fields_are_deterministic(self):
        a=fixture();b=copy.deepcopy(a)
        # Private-only source changes cannot change sanitized public output.
        b["fields"][-2]["text"]="different undisclosed subject"
        result1,rec1=proj.validate(a)
        result2,rec2=proj.validate(b)
        self.assertEqual(result1,result2)
        self.assertEqual(rec1,rec2)

    def test_existence_sensitive_object_blocks_all_output(self):
        a=fixture();a["object_presence_sensitive"]=True
        with self.assertRaisesRegex(ValueError,"OBJECT_EXISTENCE_PROTECTED"):
            proj.validate(a)

    def test_release_intent_cannot_auto_publish(self):
        a=fixture();a["intent"]="PUBLISH_IMMEDIATELY"
        with self.assertRaisesRegex(ValueError,"AUTO_RELEASE_NOT_AUTHORIZED"):
            proj.validate(a)

    def test_invalid_public_field_rejected_even_if_short(self):
        a=fixture();a["fields"].append(
           {"field":"child_profile","decision":"PUBLIC_SUMMARY",
            "text":"A fictional child studied at a school."})
        with self.assertRaisesRegex(ValueError,"UNQUALIFIED_PUBLIC_FIELD"):
            proj.validate(a)

    def test_secret_pattern_in_public_text_holds(self):
        for value in ("password=examplePassword123",
                      "ghp_abcdefghijabcdefghijabcdef","Bearer abcdefghijklmnop",
                      "person@example.com",
                      "D:\\Demo\\Private\\source.json"):
            with self.subTest(value=value):
                a=fixture();a["fields"][0]["text"]=value+" is a claim"
                with self.assertRaisesRegex(ValueError,"POTENTIAL_SENSITIVE_TEXT"):
                    proj.validate(a)

    def test_private_git_url_not_in_public_candidate(self):
        a=fixture()
        a["fields"][0]["text"]="Private pointer: https://github.com/CoCivium/CoSteward/pull/123"
        with self.assertRaisesRegex(ValueError,"POTENTIAL_SENSITIVE_TEXT"):
            proj.validate(a)

    def test_unknown_is_not_absent_and_never_a_public_fact(self):
        a=fixture()
        a["fields"][0]["decision"]="UNRESOLVED"
        with self.assertRaisesRegex(ValueError,"MISSING_PUBLIC_MINIMUM"):
            proj.validate(a)
        value,_=proj.validate(fixture())
        self.assertIn("UNKNOWN_NE_ABSENT",value["nonclaims"])

    def test_public_source_requires_https_without_userinfo(self):
        a=fixture();a["fields"].append(
          {"field":"source_public_url","decision":"PUBLIC_EXACT",
           "text":"https://example.org/public-reference"})
        value,_=proj.validate(a)
        self.assertEqual(value["public_candidate_fields"]["source_public_url"],
                         "https://example.org/public-reference")
        a["fields"][-1]["text"]="http://example.org/something"
        with self.assertRaisesRegex(ValueError,"PUBLIC_SOURCE_URL"):
            proj.validate(a)

    def test_cannot_duplicate_public_and_held_label(self):
        a=fixture();a["fields"].append(copy.deepcopy(a["fields"][0]))
        with self.assertRaisesRegex(ValueError,"DUPLICATE_FIELD"):
            proj.validate(a)

    def test_no_clobber_and_exact_local_output_sha(self):
        with tempfile.TemporaryDirectory() as root:
            out=Path(root)/"candidate.json"
            receipt=proj.write(fixture(),out)
            self.assertEqual(receipt["candidate_sha256"],proj.digest(out.read_bytes()))
            with self.assertRaisesRegex(ValueError,"NO_OVERWRITE"):
                proj.write(fixture(),out)

    def test_output_contains_no_input_metadata_or_private_id(self):
        result,_=proj.validate(fixture())
        self.assertEqual(set(result["public_candidate_fields"]),
                         {"question","status","limitation","next_test"})
        self.assertNotIn("source_input_sha256",result)
        self.assertIn("MECHANICAL_FILTER_NE_SECURITY_CLEARANCE",result["nonclaims"])

if __name__=="__main__":
    unittest.main()
