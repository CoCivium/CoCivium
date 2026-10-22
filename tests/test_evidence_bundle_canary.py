"""Small independent fixtures for the public evidence bundle canary.

These are storage and declared-query regressions, not scientific corroboration
or tests of an actual review panel. No live repository source is required.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "CoEvidenceBundleCanaryR0.py"
IMPORT_SPEC = importlib.util.spec_from_file_location("evidence_canary", SCRIPT)
canary = importlib.util.module_from_spec(IMPORT_SPEC)
IMPORT_SPEC.loader.exec_module(canary)

AS_OF = "2026-10-22T12:00:00Z"
RAW_SHARED = b"first\r\n\x00caf\xc3\xa9\n"
RAW_DISTINCT = b"\xffdifferent\x00\r\n"
ALL_SOURCE_IDS = ["s_alias", "s_distinct", "s_other", "s_primary"]
UNRESOLVED = [
    {"id": "conflict_forward", "type": "contradicts", "from": "c_base", "to": "c_alias",
     "resolution": "UNRESOLVED", "basis": "TEST_ONLY", "ambiguity": "Retain this exact qualification."},
    {"id": "conflict_reverse", "type": "contradicts", "from": "c_alias", "to": "c_base",
     "resolution": "UNRESOLVED", "basis": "TEST_ONLY", "ambiguity": "Separate declared reverse edge."},
]


def source_record(identifier, raw, custody="scope_alpha"):
    return {
        "id": identifier,
        "path": "data/" + identifier + ".bin",
        "sha256": hashlib.sha256(raw).hexdigest(),
        "git_blob_sha1": hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest(),
        "bytes": len(raw), "confidentiality": "PUBLIC", "custody_scope": custody,
        "version": "TEST_ONLY_V1", "locator": "canary-fixture://" + identifier,
        "observed_at": "2026-10-22T11:00:00Z",
    }


def claim_record(identifier, source_ids, **changes):
    row = {"id": identifier, "epistemic_class": "HYPOTHESIS", "status": "CANDIDATE",
           "source_ids": source_ids, "valid_from": "2026-10-21T00:00:00Z",
           "expires_at": None, "receivers": ["panel"]}
    row.update(changes)
    return row


def relation_record(identifier, kind, left, right):
    return {"id": identifier, "type": kind, "from": left, "to": right,
            "resolution": "NOT_APPLICABLE", "basis": "TEST_ONLY", "ambiguity": ""}


def fixture():
    payloads = {"s_primary": RAW_SHARED, "s_alias": RAW_SHARED,
                "s_other": RAW_SHARED, "s_distinct": RAW_DISTINCT}
    spec = {
        "format": "CoEvidenceBundleCanarySpecR0", "fixture_metadata_status": "TEST_ONLY",
        "sources": [source_record("s_primary", RAW_SHARED),
                    source_record("s_alias", RAW_SHARED),
                    source_record("s_other", RAW_SHARED, custody="scope_beta"),
                    source_record("s_distinct", RAW_DISTINCT)],
        "roles": [
            {"id": "worker", "operational_role": "WORKER", "source_ids": list(payloads)},
            {"id": "challenger", "operational_role": "CHALLENGER",
             "source_ids": ["s_primary", "s_distinct"]},
        ],
        "claims": [
            claim_record("c_base", ["s_primary"]),
            claim_record("c_alias", ["s_alias"], valid_from=AS_OF,
                         expires_at="2026-10-22T12:00:02Z"),
            claim_record("c_cycle", ["s_other", "s_distinct"]),
            claim_record("c_expired", ["s_primary"], expires_at=AS_OF),
            claim_record("c_future", ["s_distinct"], valid_from="2026-10-22T12:00:01Z"),
            claim_record("c_history", ["s_alias"], status="HISTORICAL", receivers=["archive"]),
            claim_record("c_empty", []),
        ],
        "relations": [
            relation_record("derive", "derived_from", "c_alias", "c_base"),
            relation_record("project", "projection_of", "c_cycle", "c_alias"),
            relation_record("return", "derived_from", "c_base", "c_cycle"),
            relation_record("empty_self_cycle", "derived_from", "c_empty", "c_empty"),
            *copy.deepcopy(UNRESOLVED),
            {"id": "resolved", "type": "contradicts", "from": "c_history", "to": "c_cycle",
             "resolution": "RESOLVED", "basis": "TEST_ONLY", "ambiguity": "Retained in source metadata."},
        ],
    }
    return spec, payloads


def expected_queries():
    """Manually specified oracle: the three-node cycle reaches four source IDs."""
    return {
        "claim_sources": {
            "c_alias": ALL_SOURCE_IDS, "c_base": ALL_SOURCE_IDS, "c_cycle": ALL_SOURCE_IDS,
            "c_empty": [], "c_expired": ["s_primary"], "c_future": ["s_distinct"],
            "c_history": ["s_alias"],
        },
        "unresolved_contradictions": copy.deepcopy(UNRESOLVED),
        "receiver_candidates": {"archive": [], "panel": ["c_alias", "c_base", "c_cycle", "c_empty"]},
    }


class EvidenceBundleCanaryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="coevidence-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.sources = self.root / "sources"
        self.sources.mkdir()
        self.spec, self.payloads = fixture()
        for source in self.spec["sources"]:
            path = self.sources / source["path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(self.payloads[source["id"]])

    def build(self, mode="indexed_cas"):
        root = self.root / mode
        inventory = canary.build_layout(self.spec, self.payloads, mode, AS_OF, root)
        return root, inventory

    def verify(self, root, inventory, mode="indexed_cas"):
        return canary.verify_layout(root, self.spec, self.payloads, mode, AS_OF, inventory)

    def test_both_query_methods_match_manual_cycle_and_contradiction_oracle(self):
        expected = expected_queries()
        self.assertEqual(canary.direct_queries(self.spec, AS_OF), expected)
        self.assertEqual(canary.materialize(self.spec, AS_OF)["results"], expected)
        # Queries retain claim sources even when a claim is expired or historical.
        self.assertEqual(expected["claim_sources"]["c_history"], ["s_alias"])

    def test_candidate_intervals_include_start_exclude_expiry_and_filter_status(self):
        cases = [
            ("2026-10-22T11:59:59Z", ["c_base", "c_cycle", "c_empty", "c_expired"]),
            (AS_OF, ["c_alias", "c_base", "c_cycle", "c_empty"]),
            ("2026-10-22T12:00:01Z", ["c_alias", "c_base", "c_cycle", "c_empty", "c_future"]),
            ("2026-10-22T12:00:02Z", ["c_base", "c_cycle", "c_empty", "c_future"]),
        ]
        for cutoff, expected in cases:
            with self.subTest(cutoff=cutoff):
                for answer in (canary.direct_queries(self.spec, cutoff),
                               canary.materialize(self.spec, cutoff)["results"]):
                    self.assertEqual(answer["receiver_candidates"], {"archive": [], "panel": expected})
                    self.assertEqual(answer["unresolved_contradictions"], UNRESOLVED)

    def test_binary_sources_load_without_normalizing_bytes_or_alias_identity(self):
        loaded = canary.load_sources(self.spec, self.sources)
        self.assertEqual(loaded, self.payloads)
        self.assertEqual(len(loaded), 4)
        self.assertEqual(loaded["s_primary"], b"first\r\n\x00caf\xc3\xa9\n")
        self.assertEqual(loaded["s_distinct"], b"\xffdifferent\x00\r\n")

    def test_all_layouts_reconstruct_six_bindings_and_count_all_file_bytes(self):
        payload_totals = {
            "per_role_copies": 4 * len(RAW_SHARED) + 2 * len(RAW_DISTINCT),
            "shared_paths": 3 * len(RAW_SHARED) + len(RAW_DISTINCT),
            "shared_cas": 2 * len(RAW_SHARED) + len(RAW_DISTINCT),
            "indexed_cas": 2 * len(RAW_SHARED) + len(RAW_DISTINCT),
        }
        for mode in canary.MODES:
            with self.subTest(mode=mode):
                root, inventory = self.build(mode)
                verified = self.verify(root, inventory, mode)
                self.assertEqual(verified["role_bindings_reconstructed"], 6)
                self.assertIs(verified["indexed_queries_equal_reference"],
                              True if mode == "indexed_cas" else None)
                self.assertEqual(json.loads((root / "spec.json").read_bytes()), self.spec)
                metrics = canary.storage_metrics(root)
                actual_total = sum(p.stat().st_size for p in root.rglob("*") if p.is_file())
                self.assertEqual(metrics["payload_bytes"], payload_totals[mode])
                self.assertEqual(metrics["total_file_bytes"], actual_total)
                self.assertEqual(actual_total, metrics["payload_bytes"] + metrics["metadata_bytes"]
                                 + metrics["view_bytes"])
                self.assertGreater(metrics["metadata_bytes"], 0)

    def test_cas_keeps_alias_provenance_and_separates_identical_cross_custody_bytes(self):
        root, inventory = self.build("shared_cas")
        binding = json.loads((root / "bindings.json").read_bytes())["worker"]
        self.assertEqual(binding["s_primary"], binding["s_alias"])
        self.assertNotEqual(binding["s_primary"], binding["s_other"])
        self.assertNotEqual(binding["s_other"], binding["s_distinct"])
        for identifier, relative in binding.items():
            self.assertEqual((root / relative).read_bytes(), self.payloads[identifier])
        stored_spec = json.loads((root / "spec.json").read_bytes())
        self.assertEqual([s["id"] for s in stored_spec["sources"]],
                         ["s_primary", "s_alias", "s_other", "s_distinct"])
        self.assertEqual(len({s["locator"] for s in stored_spec["sources"]}), 4)
        self.verify(root, inventory, "shared_cas")

    def test_shared_path_collision_holds_cross_custody_but_allows_compatible_alias(self):
        compatible = copy.deepcopy(self.spec)
        compatible["sources"][1]["path"] = compatible["sources"][0]["path"]
        root = self.root / "compatible-alias"
        inventory = canary.build_layout(compatible, self.payloads, "shared_paths", AS_OF, root)
        result = canary.verify_layout(root, compatible, self.payloads, "shared_paths", AS_OF, inventory)
        self.assertEqual(result["role_bindings_reconstructed"], 6)
        bindings = json.loads((root / "bindings.json").read_bytes())["worker"]
        self.assertEqual(bindings["s_primary"], bindings["s_alias"])

        incompatible = copy.deepcopy(self.spec)
        incompatible["sources"][2]["path"] = incompatible["sources"][0]["path"]
        held_root = self.root / "incompatible-alias"
        with self.assertRaisesRegex(canary.CanaryError, "incompatible custody"):
            canary.build_layout(incompatible, self.payloads, "shared_paths", AS_OF, held_root)
        self.assertFalse(held_root.exists())
        # The CAS layout can represent this case by keeping the custody scopes apart.
        cas_root = self.root / "scoped-alias"
        cas_inventory = canary.build_layout(incompatible, self.payloads, "shared_cas", AS_OF, cas_root)
        canary.verify_layout(cas_root, incompatible, self.payloads, "shared_cas", AS_OF, cas_inventory)
        scoped = json.loads((cas_root / "bindings.json").read_bytes())["worker"]
        self.assertNotEqual(scoped["s_primary"], scoped["s_other"])

    def test_tampered_missing_and_extra_layout_files_are_held(self):
        root, inventory = self.build()
        binding = json.loads((root / "bindings.json").read_bytes())["worker"]
        payload = root / binding["s_primary"]
        original = payload.read_bytes()
        payload.write_bytes(b"X" + original[1:])
        with self.assertRaises(canary.CanaryError):
            self.verify(root, inventory)
        payload.write_bytes(original)
        payload.unlink()
        with self.assertRaises(canary.CanaryError):
            self.verify(root, inventory)
        payload.write_bytes(original)
        extra = root / "unexpected.bin"
        extra.write_bytes(b"extra")
        with self.assertRaises(canary.CanaryError):
            self.verify(root, inventory)
        extra.unlink()
        self.verify(root, inventory)

    def test_rewritten_inventory_cannot_replace_the_external_expected_digest(self):
        root, inventory = self.build()
        (root / "unexpected.bin").write_bytes(b"added")
        (root / "inventory.json").write_bytes(canary.encode(canary.file_inventory(root)))
        with self.assertRaisesRegex(canary.CanaryError, "external expected digest"):
            self.verify(root, inventory)

    def test_tampered_view_and_stale_source_version_cutoff_transform_are_held(self):
        view = canary.materialize(self.spec, AS_OF)
        expected_hash = hashlib.sha256(canary.encode(view)).hexdigest()
        self.assertEqual(canary.guard_view(view, self.spec, AS_OF, expected_hash), expected_queries())
        damaged = copy.deepcopy(view)
        damaged["results"]["unresolved_contradictions"] = []
        with self.assertRaises(canary.CanaryError):
            canary.guard_view(damaged, self.spec, AS_OF, expected_hash)
        changed = copy.deepcopy(self.spec)
        changed["sources"][0]["version"] = "TEST_ONLY_V2"
        with self.assertRaises(canary.CanaryError):
            canary.guard_view(view, changed, AS_OF, expected_hash)
        with self.assertRaises(canary.CanaryError):
            canary.guard_view(view, self.spec, "2026-10-22T12:00:01Z", expected_hash)
        with mock.patch.object(canary, "TRANSFORM", "TEST_DIFFERENT_TRANSFORM"):
            with self.assertRaises(canary.CanaryError):
                canary.guard_view(view, self.spec, AS_OF, expected_hash)

    def test_duplicate_metadata_ids_are_rejected(self):
        for collection in ("sources", "roles", "claims", "relations"):
            with self.subTest(collection=collection):
                bad = copy.deepcopy(self.spec)
                bad[collection].append(copy.deepcopy(bad[collection][0]))
                with self.assertRaisesRegex(canary.CanaryError, "duplicate id"):
                    canary.validate_spec(bad)

    def test_empty_required_collections_and_unbound_sources_are_rejected(self):
        for collection in ("sources", "roles", "claims", "relations"):
            with self.subTest(collection=collection):
                bad = copy.deepcopy(self.spec)
                bad[collection] = []
                with self.assertRaises(canary.CanaryError):
                    canary.validate_spec(bad)
        bad = copy.deepcopy(self.spec)
        bad["roles"][0]["source_ids"].remove("s_other")
        with self.assertRaisesRegex(canary.CanaryError, "every corpus source"):
            canary.build_layout(bad, self.payloads, "shared_cas", AS_OF, self.root / "unbound")
        self.assertFalse((self.root / "unbound").exists())

    def test_dangling_duplicate_source_refs_and_invalid_public_labels_are_rejected(self):
        mutations = [
            lambda s: s["relations"][0].update({"to": "missing_claim"}),
            lambda s: s["roles"][0]["source_ids"].append("s_primary"),
            lambda s: s["claims"][0]["source_ids"].append("missing_source"),
            lambda s: s["sources"][0].update({"confidentiality": "PRIVATE"}),
            lambda s: s["sources"][0].update({"bytes": True}),
            lambda s: s["claims"][0].update({"epistemic_class": "OBSERVED"}),
        ]
        for mutation in mutations:
            with self.subTest(mutation=mutations.index(mutation)):
                bad = copy.deepcopy(self.spec)
                mutation(bad)
                with self.assertRaises(canary.CanaryError):
                    canary.validate_spec(bad)

    def test_wrong_source_bytes_and_missing_sources_are_held_before_layout_build(self):
        path = self.sources / self.spec["sources"][0]["path"]
        original = path.read_bytes()
        path.write_bytes(b"!" + original[1:])
        with self.assertRaisesRegex(canary.CanaryError, "source bytes mismatch"):
            canary.load_sources(self.spec, self.sources)
        path.unlink()
        with self.assertRaises(OSError):
            canary.load_sources(self.spec, self.sources)

    def test_source_paths_cannot_traverse_or_follow_a_symlink_outside_root(self):
        for relative in ("../escape.bin", "/tmp/escape.bin", "data/../escape.bin", "data\\escape.bin"):
            with self.subTest(path=relative):
                bad = copy.deepcopy(self.spec)
                bad["sources"][0]["path"] = relative
                with self.assertRaises(canary.CanaryError):
                    canary.validate_spec(bad)
        outside = self.root / "outside.bin"
        outside.write_bytes(RAW_SHARED)
        path = self.sources / self.spec["sources"][0]["path"]
        path.unlink()
        try:
            path.symlink_to(outside)
        except (NotImplementedError, OSError):
            self.skipTest("symlink creation unavailable on this platform")
        with self.assertRaisesRegex(canary.CanaryError, "leaves input root"):
            canary.load_sources(self.spec, self.sources)

    def test_existing_layout_is_not_overwritten(self):
        root, inventory = self.build()
        before = {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()}
        with self.assertRaisesRegex(canary.CanaryError, "fresh directory"):
            canary.build_layout(self.spec, self.payloads, "indexed_cas", AS_OF, root)
        self.assertEqual(before, {p.relative_to(root): p.read_bytes() for p in root.rglob("*") if p.is_file()})
        self.verify(root, inventory)

    def test_repetition_limits_reject_zero_out_of_range_bool_and_nonintegers(self):
        for value in (0, -1, 1002, True, 1.0, "1"):
            with self.subTest(query_repetitions=value):
                with self.assertRaisesRegex(canary.CanaryError, "query repetitions"):
                    canary.run_experiment(self.spec, self.sources, AS_OF, repetitions=value)
        for value in (0, -1, 10, False, 1.0, "1"):
            with self.subTest(build_repetitions=value):
                with self.assertRaisesRegex(canary.CanaryError, "build repetitions"):
                    canary.run_experiment(self.spec, self.sources, AS_OF, build_repetitions=value)

    def test_strict_decoder_rejects_duplicate_json_keys_and_nonfinite_values(self):
        for raw in (b'{"id":1,"id":2}', b'{"nested":{"id":1,"id":2}}',
                    b'{"number":NaN}', b'{"number":Infinity}'):
            with self.subTest(raw=raw):
                with self.assertRaises(canary.CanaryError):
                    canary.decode(raw)

    def test_end_to_end_report_keeps_inputs_and_qualifies_its_measurements(self):
        before_spec = copy.deepcopy(self.spec)
        before_files = {p.relative_to(self.sources): p.read_bytes()
                        for p in self.sources.rglob("*") if p.is_file()}
        report = canary.run_experiment(self.spec, self.sources, AS_OF, repetitions=1, build_repetitions=1)
        self.assertEqual(report["status"], "BOUNDED_CANARY_PASSED")
        self.assertEqual(report["source_count"], 4)
        self.assertEqual(report["role_binding_count"], 6)
        self.assertEqual(report["query_results"], expected_queries())
        self.assertEqual({r["probe"] for r in report["negative_probes"]},
                         {"tampered_payload", "missing_payload", "tampered_view",
                          "stale_source_version", "stale_cutoff"})
        self.assertTrue(all(row["held"] for row in report["negative_probes"]))
        self.assertFalse(report["measurement_scope"]["live_remote_staleness_measured"])
        self.assertFalse(report["refresh"]["incremental_refresh_implemented"])
        self.assertEqual(report["refresh"]["source_payload_delta_bytes"], 1)
        self.assertTrue(report["refresh"]["original_layouts_retained_and_reverified"])
        self.assertFalse(report["effect_boundary"]["source_files_changed"])
        self.assertEqual(report["effect_boundary"]["live_session_sync"], "NOT_TESTED")
        self.assertEqual(self.spec, before_spec)
        self.assertEqual(before_files, {p.relative_to(self.sources): p.read_bytes()
                                       for p in self.sources.rglob("*") if p.is_file()})


if __name__ == "__main__":
    unittest.main()
