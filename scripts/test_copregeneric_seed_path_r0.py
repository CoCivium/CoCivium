"""CoPreGeneric CoSeed/CoPath: public draft source-identity and no-false-pickup checks.

Verifies the four explicitly declared seedable blobs and four proposed routes
against the actual checked-out repository. It does not fetch the network,
make a receiver readproof, approve release, or validate historical coverage.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "ai/onramp/copregeneric-seed-path-discovery-r0.json"
GIT40 = re.compile(r"[0-9a-f]{40}\Z")
SAFE_PATH = re.compile(r"[A-Za-z0-9_./+-]{1,220}\Z")
PR_REVIEW_URL = "https://github.com/CoCivium/CoCivium/pull/426"
SYMBOLIC_TARGET = "AUTHORIZED_REVIEW"
REQUIRED_NONCLAIMS = {
    "PUBLIC_SOURCE_NE_RECEIVER_PICKUP", "PROPOSED_PATH_NE_EXECUTED_PATH",
    "DRAFT_NE_CANON", "SOURCE_RELATION_NE_SEMANTIC_INGESTION",
    "NO_GLOBAL_COMPLETE_HISTORICAL_SCAN", "GITHUB_NE_INDEPENDENT_MIRROR",
}
ALLOWED_EFFECTS = {
    "PUBLIC_DISCOVERY_ONLY", "NO_VENDOR_DELIVERY", "NO_SESSION_INSPECTION",
}


def require(condition: bool, reason: str) -> None:
    if not condition:
        raise ValueError("HOLD_COPRE_SEED_PATH: " + reason)


def local_source(path: str, *, allowed_review: bool = False) -> Path | None:
    if allowed_review and path in {PR_REVIEW_URL, SYMBOLIC_TARGET}:
        return None
    require(isinstance(path, str) and bool(SAFE_PATH.fullmatch(path)),
            "UNSAFE_OR_UNEXPECTED_SOURCE_PATH")
    require(not path.startswith("/") and all(
        component not in (".", "..", "") for component in path.split("/")),
        "SOURCE_PATH_TRAVERSAL")
    f = ROOT / path
    require(f.is_file(), "MISSING_SOURCE:" + path)
    return f


def blob_sha1(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode("ascii")
                        + b"\x00" + data).hexdigest()


def audit(manifest: dict) -> dict:
    require(isinstance(manifest, dict), "NOT_OBJECT")
    require(manifest.get("schema") == "CoAll.CoPreGeneric.SeedPathDiscovery.R0",
            "BAD_SCHEMA")
    require(manifest.get("state") ==
            "PUBLIC_SAFE_DRAFT__NOT_GLOBAL_INTEGRATION", "FALSE_PROMOTION")
    require(manifest.get("work_id") == "CoAll.CoPreGeneric.CrossAudience.20261109",
            "WORKID_DRIFT")

    source = manifest.get("public_source")
    require(isinstance(source, dict), "NO_SOURCE")
    require(source.get("repo") == "CoCivium/CoCivium" and
            source.get("branch") == "candidate/copregeneric-synth-bio-pull-20261109",
            "SOURCE_IDENTITY_DRIFT")
    require(source.get("hash_kind") == "GIT_BLOB_SHA1_NOT_MIRROR_SHA256",
            "WRONG_HASH_SEMANTICS")
    for key in ("human_index", "machine_delta", "retro_echo"):
        local_source(source.get(key))

    seeds = manifest.get("seedables")
    require(isinstance(seeds, list) and len(seeds) == 4,
            "SEED_COUNT_OR_TYPE")
    identities = set()
    for seed in seeds:
        require(isinstance(seed, dict) and
                isinstance(seed.get("id"), str) and
                seed["id"] not in identities, "DUPLICATE_OR_BAD_SEED_ID")
        identities.add(seed["id"])
        source_file = local_source(seed.get("source"))
        declared = seed.get("source_blob_sha1")
        require(isinstance(declared, str) and bool(GIT40.fullmatch(declared)),
                "MISSING_SEED_SOURCE_HASH")
        require(blob_sha1(source_file.read_bytes()) == declared,
                "SOURCE_HASH_MISMATCH:" + seed["id"])
        require(seed.get("discovery_state") ==
                "PUBLIC_DRAFT_SOURCE_NOT_PICKED_UP", "FALSE_SEED_PICKUP")
        require(seed.get("effect") in ALLOWED_EFFECTS, "BAD_SEED_EFFECT")
    routes = manifest.get("paths")
    require(isinstance(routes, list) and len(routes) == 4, "PATH_COUNT_OR_TYPE")
    route_ids = set()
    for route in routes:
        require(isinstance(route, dict) and
                isinstance(route.get("id"), str) and
                route["id"] not in route_ids, "DUPLICATE_OR_BAD_PATH_ID")
        route_ids.add(route["id"])
        require(route.get("execution_state") == "PROPOSED_NOT_EXECUTED" and
                route.get("receiver_readproof") is None,
                "FALSE_PATH_EXECUTION_OR_RECEIVER_ACK")
        require(isinstance(route.get("requires"), list) and
                bool(route["requires"]) and
                all(isinstance(x, str) and x for x in route["requires"]),
                "MISSING_PATH_GATES")
        local_source(route.get("from"))
        via = route.get("via")
        require(isinstance(via, list) and len(via) > 0,
                "NO_PATH_HOPS")
        for step in via:
            local_source(step, allowed_review=True)
        local_source(route.get("to"), allowed_review=True)
    require(route_ids == {"Path.Machine", "Path.Human", "Path.Retro",
                           "Path.Review"}, "MISSING_REQUIRED_PATH")

    relations = manifest.get("relations")
    require(isinstance(relations, list) and len(relations) >= 3,
            "NO_RELATIONAL_COVERAGE")
    for rel in relations:
        require(isinstance(rel, dict) and rel.get("from") in identities and
                rel.get("to") in identities and
                rel.get("verified_semantics") == "CANDIDATE",
                "BROKEN_OR_PROMOTED_RELATION")

    unresolved = manifest.get("unresolved")
    require(isinstance(unresolved, dict) and
            unresolved.get("unscanned_historical_fronts") == "UNKNOWN" and
            unresolved.get("third_party_receiver") == "UNPROVEN" and
            unresolved.get("coex") == "UNPROVEN" and
            unresolved.get("live_sync") == "UNPROVEN",
            "UNPROVEN_STATE_WAS_UPGRADED")
    for key in ("domain_cocivium_org_copre",
                "domain_inseed_com_stead", "distinct_copregeneric_repo"):
        require(unresolved.get(key) == "NOT_VERIFIED",
                "UNVERIFIED_MIRROR_WAS_PROMOTED")
    require(isinstance(manifest.get("nonclaims"), list) and
            REQUIRED_NONCLAIMS.issubset(set(manifest["nonclaims"])),
            "MISSING_NONCLAIMS")
    recovery = manifest.get("recovery")
    require(isinstance(recovery, dict) and recovery.get("read_only") is True,
            "UNSAFE_RECOVERY")
    local_source(recovery.get("last_good_source"))
    local_source(recovery.get("fallback"))
    return {
        "state": "PASS_SOURCE_IDENTITY_AND_PROPOSED_PATHS_ONLY",
        "seed_sources_matched": len(identities),
        "path_descriptions_valid": len(route_ids),
        "path_executions_observed": 0,
        "receiver_ack_observed": False,
        "global_integration_proven": False,
    }


class CoPreSeedPathTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.obj = json.loads(MANIFEST.read_text("utf-8"))

    def test_declared_sources_and_routes(self):
        result = audit(self.obj)
        self.assertEqual(result["seed_sources_matched"], 4)
        self.assertEqual(result["path_descriptions_valid"], 4)
        self.assertFalse(result["receiver_ack_observed"])

    def test_seed_blob_substitution_held(self):
        bad = copy.deepcopy(self.obj)
        bad["seedables"][0]["source_blob_sha1"] = "0" * 40
        with self.assertRaisesRegex(ValueError, "SOURCE_HASH_MISMATCH"):
            audit(bad)

    def test_seed_path_escape_held(self):
        bad = copy.deepcopy(self.obj)
        bad["seedables"][0]["source"] = "../private/data.txt"
        with self.assertRaisesRegex(ValueError, "UNSAFE|TRAVERSAL"):
            audit(bad)

    def test_seed_missing_source_held(self):
        bad = copy.deepcopy(self.obj)
        bad["seedables"][0]["source"] = "does_not_exist.md"
        with self.assertRaisesRegex(ValueError, "MISSING_SOURCE"):
            audit(bad)

    def test_duplicate_seed_held(self):
        bad = copy.deepcopy(self.obj)
        bad["seedables"][1]["id"] = bad["seedables"][0]["id"]
        with self.assertRaisesRegex(ValueError, "DUPLICATE"):
            audit(bad)

    def test_broken_relation_held(self):
        bad = copy.deepcopy(self.obj)
        bad["relations"][0]["to"] = "imaginary.receiver"
        with self.assertRaisesRegex(ValueError, "BROKEN_OR_PROMOTED_RELATION"):
            audit(bad)

    def test_untrusted_external_pointer_held(self):
        bad = copy.deepcopy(self.obj)
        bad["paths"][3]["via"][0] = "https://unverified.example/handoff"
        with self.assertRaisesRegex(ValueError, "UNSAFE_OR_UNEXPECTED_SOURCE_PATH"):
            audit(bad)

    def test_forged_receiver_ack_held(self):
        bad = copy.deepcopy(self.obj)
        bad["paths"][0]["receiver_readproof"] = {"ack": True}
        with self.assertRaisesRegex(ValueError, "FALSE_PATH_EXECUTION"):
            audit(bad)

    def test_forged_executed_path_held(self):
        bad = copy.deepcopy(self.obj)
        bad["paths"][0]["execution_state"] = "INTEGRATED"
        with self.assertRaisesRegex(ValueError, "FALSE_PATH_EXECUTION"):
            audit(bad)

    def test_unverified_mirror_cannot_be_promoted(self):
        bad = copy.deepcopy(self.obj)
        bad["unresolved"]["domain_inseed_com_stead"] = "VERIFIED"
        with self.assertRaisesRegex(ValueError, "UNVERIFIED_MIRROR"):
            audit(bad)

    def test_missing_historical_coverage_not_zero(self):
        bad = copy.deepcopy(self.obj)
        bad["unresolved"]["unscanned_historical_fronts"] = 0
        with self.assertRaisesRegex(ValueError, "UNPROVEN_STATE"):
            audit(bad)

    def test_hash_type_not_mirror_sha(self):
        bad = copy.deepcopy(self.obj)
        bad["public_source"]["hash_kind"] = "ALL_THREE_SHA256_VERIFIED"
        with self.assertRaisesRegex(ValueError, "WRONG_HASH_SEMANTICS"):
            audit(bad)


if __name__ == "__main__":
    unittest.main()
