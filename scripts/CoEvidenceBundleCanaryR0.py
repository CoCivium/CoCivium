#!/usr/bin/env python3
"""Bounded, local public-evidence storage experiment; no live panel or receiver."""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import gzip
import hashlib
import io
import json
from pathlib import Path, PurePosixPath
import platform
import re
import statistics
import sys
import tarfile
import tempfile
import time


FORMAT = "CoEvidenceBundleCanarySpecR0"
TRANSFORM = "DECLARED_RELATION_VIEWS_R0_1"
MODES = ("per_role_copies", "shared_paths", "shared_cas", "indexed_cas")
DERIVATIONS = {"derived_from", "projection_of"}
IDENTIFIER = re.compile(r"[A-Za-z0-9_-]{1,80}\Z")
UTC_SECONDS = re.compile(r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z\Z")


class CanaryError(ValueError):
    """A required bound or verification failed; no successful report is emitted."""


def require(condition, message):
    if not condition:
        raise CanaryError(message)


def encode(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True,
                       separators=(",", ":"), allow_nan=False) + "\n").encode("utf-8")


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def git_blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode() + b"\0" + raw).hexdigest()


def decode(raw):
    def unique_pairs(pairs):
        out = {}
        for key, value in pairs:
            require(key not in out, "duplicate JSON key")
            out[key] = value
        return out

    def bad_constant(value):
        raise CanaryError("non-finite JSON constant: " + value)

    return json.loads(raw, object_pairs_hook=unique_pairs, parse_constant=bad_constant)


def timestamp(value):
    require(isinstance(value, str) and UTC_SECONDS.fullmatch(value),
            "timestamp must be canonical UTC seconds")
    try:
        return dt.datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
    except ValueError as exc:
        raise CanaryError("invalid UTC calendar timestamp") from exc


def relative_path(value):
    require(isinstance(value, str) and value and "\\" not in value,
            "invalid relative path")
    parsed = PurePosixPath(value)
    require(parsed.parts and not parsed.is_absolute() and parsed.as_posix() == value
            and all(part not in {".", ".."} for part in parsed.parts),
            "path must be a normalized relative path")
    return parsed


def records(value, limit, label):
    require(isinstance(value, list) and 0 < len(value) <= limit, label + " count out of bounds")
    result = {}
    for item in value:
        require(isinstance(item, dict), label + " record must be an object")
        key = item.get("id")
        require(isinstance(key, str) and IDENTIFIER.fullmatch(key), label + " invalid id")
        require(key not in result, label + " duplicate id")
        result[key] = item
    return result


def id_list(value, allowed, label, nonempty=True):
    require(isinstance(value, list) and len(value) <= 64, label + " must be a bounded list")
    require(all(isinstance(x, str) and x in allowed for x in value), label + " unknown id")
    require(len(value) == len(set(value)) and (value or not nonempty), label + " empty or duplicate")


def validate_spec(spec):
    require(isinstance(spec, dict) and spec.get("format") == FORMAT, "wrong spec format")
    require(spec.get("fixture_metadata_status") == "TEST_ONLY", "fixture status must be explicit")
    sources = records(spec.get("sources"), 32, "source")
    roles = records(spec.get("roles"), 16, "role")
    claims = records(spec.get("claims"), 64, "claim")
    relations = records(spec.get("relations"), 128, "relation")
    total = 0
    for source in sources.values():
        relative_path(source.get("path"))
        size = source.get("bytes")
        require(type(size) is int and 0 <= size <= 1024 * 1024, "source size out of bounds")
        total += size
        require(source.get("confidentiality") == "PUBLIC", "canary accepts only declared PUBLIC inputs")
        for key in ("custody_scope", "locator", "version"):
            require(isinstance(source.get(key), str) and 0 < len(source[key]) <= 2048,
                    "source lacks " + key)
        for key, length in (("sha256", 64), ("git_blob_sha1", 40)):
            require(isinstance(source.get(key), str) and re.fullmatch("[0-9a-f]{%d}" % length, source[key]),
                    "invalid source digest")
        timestamp(source.get("observed_at"))
    require(total <= 8 * 1024 * 1024, "corpus exceeds 8 MiB")
    for role in roles.values():
        require(isinstance(role.get("operational_role"), str) and role["operational_role"], "role missing label")
        id_list(role.get("source_ids"), sources, "role sources")
    for claim in claims.values():
        require(claim.get("epistemic_class") == "HYPOTHESIS", "query fixture is not observational evidence")
        require(claim.get("status") in {"CANDIDATE", "HISTORICAL"}, "unknown claim status")
        id_list(claim.get("source_ids"), sources, "claim sources", nonempty=False)
        receivers = claim.get("receivers")
        require(isinstance(receivers, list) and 0 < len(receivers) <= 16
                and all(isinstance(x, str) and IDENTIFIER.fullmatch(x) for x in receivers)
                and len(receivers) == len(set(receivers)), "invalid receivers")
        start = timestamp(claim.get("valid_from"))
        if claim.get("expires_at") is not None:
            require(timestamp(claim["expires_at"]) > start, "empty claim validity interval")
    for relation in relations.values():
        require(relation.get("type") in DERIVATIONS | {"contradicts"}, "unknown relation type")
        require(relation.get("from") in claims and relation.get("to") in claims, "dangling relation")
        require(relation.get("basis") == "TEST_ONLY", "relation basis must be explicit")
        require(relation.get("resolution") in {"UNRESOLVED", "RESOLVED", "NOT_APPLICABLE"},
                "invalid relation resolution")
        require(isinstance(relation.get("ambiguity"), str), "ambiguity field required")
    return spec


def check_payloads(spec, payloads):
    require(set(payloads) == {s["id"] for s in spec["sources"]}, "source set mismatch")
    for source in spec["sources"]:
        raw = payloads[source["id"]]
        require(isinstance(raw, bytes) and len(raw) == source["bytes"]
                and digest(raw) == source["sha256"] and git_blob(raw) == source["git_blob_sha1"],
                "source bytes mismatch: " + source["id"])


def load_sources(spec, source_root):
    validate_spec(spec)
    root = Path(source_root).resolve(strict=True)
    payloads = {}
    for source in spec["sources"]:
        path = root.joinpath(*relative_path(source["path"]).parts).resolve(strict=True)
        require(path.is_relative_to(root) and path.is_file(), "source path leaves input root")
        require(path.stat().st_size == source["bytes"], "source file size mismatch")
        payloads[source["id"]] = path.read_bytes()
    check_payloads(spec, payloads)
    return payloads


def direct_queries(spec, as_of):
    """Reference scan: DFS over explicit derivations; no semantic inference."""
    cutoff = timestamp(as_of)
    claims = {c["id"]: c for c in spec["claims"]}
    all_sources = {}
    for claim_id in sorted(claims):
        pending, seen, found = [claim_id], set(), set()
        while pending:
            current = pending.pop()
            if current in seen:
                continue
            seen.add(current)
            found.update(claims[current]["source_ids"])
            pending.extend(r["to"] for r in spec["relations"]
                           if r["from"] == current and r["type"] in DERIVATIONS)
        all_sources[claim_id] = sorted(found)
    contradictions = sorted((copy.deepcopy(r) for r in spec["relations"]
                             if r["type"] == "contradicts" and r["resolution"] == "UNRESOLVED"),
                            key=lambda item: item["id"])
    receivers = sorted({r for c in claims.values() for r in c["receivers"]})
    candidates = {}
    for receiver in receivers:
        candidates[receiver] = sorted(c["id"] for c in claims.values()
                                     if receiver in c["receivers"] and c["status"] == "CANDIDATE"
                                     and timestamp(c["valid_from"]) <= cutoff
                                     and (c["expires_at"] is None or cutoff < timestamp(c["expires_at"])))
    return {"claim_sources": all_sources, "unresolved_contradictions": contradictions,
            "receiver_candidates": candidates}


def view_binding(spec, as_of):
    timestamp(as_of)
    return {"transform": TRANSFORM, "spec_sha256": digest(encode(spec)), "as_of": as_of,
            "source_bindings": [{key: s[key] for key in ("id", "sha256", "bytes", "custody_scope", "confidentiality")}
                                for s in spec["sources"]]}


def materialize(spec, as_of):
    """Independent fixed-point closure and UTC-string eligibility implementation."""
    validate_spec(spec)
    binding = view_binding(spec, as_of)
    closure = {c["id"]: set(c["source_ids"]) for c in spec["claims"]}
    changed = True
    while changed:
        changed = False
        for relation in spec["relations"]:
            if relation["type"] in DERIVATIONS:
                target = closure[relation["from"]]
                before = len(target)
                target.update(closure[relation["to"]])
                changed |= len(target) != before
    candidates = {r: [] for c in spec["claims"] for r in c["receivers"]}
    for claim in spec["claims"]:
        if (claim["status"] == "CANDIDATE" and claim["valid_from"] <= as_of
                and (claim["expires_at"] is None or as_of < claim["expires_at"])):
            for receiver in claim["receivers"]:
                candidates[receiver].append(claim["id"])
    unresolved = [copy.deepcopy(r) for r in spec["relations"]
                  if (r["type"], r["resolution"]) == ("contradicts", "UNRESOLVED")]
    return {"binding": binding,
            "results": {"claim_sources": {key: sorted(closure[key]) for key in sorted(closure)},
                        "unresolved_contradictions": sorted(unresolved, key=lambda r: r["id"]),
                        "receiver_candidates": {key: sorted(value) for key, value in sorted(candidates.items())}}}


def guard_view(view, spec, as_of, expected_sha256):
    require(digest(encode(view)) == expected_sha256, "view bytes do not match trusted digest")
    require(view.get("binding") == view_binding(spec, as_of), "view is stale or bound to different inputs")
    return view["results"]


def payload_path(source, role_id, mode):
    if mode == "per_role_copies":
        return "payload/roles/" + role_id + "/" + source["id"] + ".bin"
    if mode == "shared_paths":
        return "payload/sources/" + source["path"]
    scope = digest(encode([source["custody_scope"], source["confidentiality"]]))
    return "payload/objects/" + scope + "/" + source["sha256"]


def layout_files(spec, payloads, mode, as_of):
    validate_spec(spec)
    check_payloads(spec, payloads)
    require(mode in MODES, "unknown layout")
    sources = {s["id"]: s for s in spec["sources"]}
    # Refuse a role projection that would silently omit a corpus source.
    referenced = {sid for role in spec["roles"] for sid in role["source_ids"]}
    require(referenced == set(sources), "every corpus source must have a declared role binding")
    files = {"spec.json": encode(spec)}
    bindings = {}
    path_scopes = {}
    for role in spec["roles"]:
        bindings[role["id"]] = {}
        for source_id in role["source_ids"]:
            path = payload_path(sources[source_id], role["id"], mode)
            raw = payloads[source_id]
            scope = (sources[source_id]["custody_scope"], sources[source_id]["confidentiality"])
            require(path not in path_scopes or path_scopes[path] == scope,
                    "payload path would share incompatible custody scopes")
            path_scopes[path] = scope
            require(path not in files or files[path] == raw, "conflicting payload path")
            files[path] = raw
            bindings[role["id"]][source_id] = path
    files["bindings.json"] = encode(bindings)
    if mode == "indexed_cas":
        files["views.json"] = encode(materialize(spec, as_of))
    return files


def file_inventory(root):
    inventory = []
    for path in sorted(Path(root).rglob("*")):
        require(not path.is_symlink(), "layout symlink is not supported")
        if path.is_file() and path.relative_to(root).as_posix() != "inventory.json":
            raw = path.read_bytes()
            inventory.append({"path": path.relative_to(root).as_posix(),
                              "bytes": len(raw), "sha256": digest(raw)})
    return {"format": "CoEvidenceBundleFileInventoryR0", "files": inventory}


def build_layout(spec, payloads, mode, as_of, root):
    root = Path(root)
    require(not root.exists(), "layout output must be a fresh directory")
    files = layout_files(spec, payloads, mode, as_of)
    root.mkdir(parents=True)
    for relative, raw in sorted(files.items()):
        path = root.joinpath(*relative_path(relative).parts)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(raw)
    inventory_raw = encode(file_inventory(root))
    (root / "inventory.json").write_bytes(inventory_raw)
    require((root / "inventory.json").read_bytes() == inventory_raw, "inventory readback mismatch")
    return digest(inventory_raw)


def verify_layout(root, spec, payloads, mode, as_of, inventory_sha256):
    validate_spec(spec)
    check_payloads(spec, payloads)
    require(mode in MODES, "unknown layout")
    root = Path(root)
    inventory_raw = (root / "inventory.json").read_bytes()
    require(digest(inventory_raw) == inventory_sha256, "inventory differs from external expected digest")
    require(decode(inventory_raw) == file_inventory(root), "layout bytes or file set changed")
    require((root / "spec.json").read_bytes() == encode(spec), "stored spec changed")
    bindings = decode((root / "bindings.json").read_bytes())
    require(set(bindings) == {r["id"] for r in spec["roles"]}, "stored role set changed")
    count = 0
    for role in spec["roles"]:
        require(set(bindings[role["id"]]) == set(role["source_ids"]), "stored role source set changed")
        for source_id in role["source_ids"]:
            path = root.joinpath(*relative_path(bindings[role["id"]][source_id]).parts).resolve(strict=True)
            require(path.is_relative_to(root.resolve()), "binding leaves layout")
            require(path.read_bytes() == payloads[source_id], "reconstruction differs from source bytes")
            count += 1
    reference = direct_queries(spec, as_of)
    if mode == "indexed_cas":
        view_raw = (root / "views.json").read_bytes()
        entries = decode(inventory_raw)["files"]
        expected_view_hash = next(item["sha256"] for item in entries if item["path"] == "views.json")
        answer = guard_view(decode(view_raw), spec, as_of, expected_view_hash)
        require(answer == reference, "direct and indexed queries disagree")
    return {"role_bindings_reconstructed": count,
            "indexed_queries_equal_reference": True if mode == "indexed_cas" else None,
            "query_result_sha256": digest(encode(reference))}


def archive_size(root):
    stream = io.BytesIO()
    with tarfile.open(fileobj=stream, mode="w", format=tarfile.USTAR_FORMAT) as archive:
        for path in sorted(Path(root).rglob("*")):
            if path.is_file():
                raw = path.read_bytes()
                info = tarfile.TarInfo(path.relative_to(root).as_posix())
                info.size, info.mtime, info.mode = len(raw), 0, 0o644
                archive.addfile(info, io.BytesIO(raw))
    return len(gzip.compress(stream.getvalue(), compresslevel=9, mtime=0))


def storage_metrics(root):
    sizes = {p.relative_to(root).as_posix(): p.stat().st_size
             for p in Path(root).rglob("*") if p.is_file()}
    payload = sum(size for name, size in sizes.items() if name.startswith("payload/"))
    views = sizes.get("views.json", 0)
    total = sum(sizes.values())
    return {"payload_bytes": payload, "metadata_bytes": total - payload - views,
            "view_bytes": views, "total_file_bytes": total,
            "file_count": len(sizes), "deterministic_tar_gz_bytes": archive_size(root)}


def sample_times(operation, repetitions):
    samples = []
    for _ in range(repetitions):
        start = time.perf_counter_ns()
        operation()
        samples.append(time.perf_counter_ns() - start)
    return {"repetitions": repetitions, "median_ns": statistics.median(samples),
            "min_ns": min(samples), "max_ns": max(samples)}


def expect_hold(operation, label):
    try:
        operation()
    except (CanaryError, OSError, ValueError):
        return {"probe": label, "held": True}
    raise CanaryError("negative probe unexpectedly succeeded: " + label)


def synthetic_refresh(spec, payloads):
    updated, new_payloads = copy.deepcopy(spec), dict(payloads)
    source = updated["sources"][0]
    original = copy.deepcopy(source)
    new_raw = new_payloads[source["id"]] + b"\n"
    source.update({"locator": "canary-fixture://append-newline/" + source["id"],
                   "version": "TEST_ONLY_APPEND_NEWLINE_R0", "bytes": len(new_raw),
                   "sha256": digest(new_raw), "git_blob_sha1": git_blob(new_raw),
                   "derived_from": original, "classification": "TEST_ONLY_DERIVATIVE",
                   "byte_verification": "SYNTHETIC_BYTES_VERIFIED_LOCALLY_NOT_A_REMOTE_GIT_OBSERVATION"})
    updated["refresh_status"] = "TEST_ONLY_SYNTHETIC_DERIVATIVE_NOT_REMOTE_GIT_CONTENT"
    new_payloads[source["id"]] = new_raw
    validate_spec(updated)
    return updated, new_payloads


def run_experiment(spec, source_root, as_of, repetitions=31, build_repetitions=3):
    require(type(repetitions) is int and 1 <= repetitions <= 1001, "query repetitions must be 1..1001")
    require(type(build_repetitions) is int and 1 <= build_repetitions <= 9, "build repetitions must be 1..9")
    timestamp(as_of)
    payloads = load_sources(spec, source_root)
    reference = direct_queries(spec, as_of)
    view = materialize(spec, as_of)
    require(view["results"] == reference, "preflight query disagreement")
    measures, probes = {}, []
    with tempfile.TemporaryDirectory(prefix="coevidence-canary-") as temporary:
        work = Path(temporary)
        roots, inventories = {}, {}
        for mode in MODES:
            build_samples = []
            for index in range(build_repetitions):
                root = work / (mode + "-" + str(index))
                start = time.perf_counter_ns()
                inventory = build_layout(spec, payloads, mode, as_of, root)
                build_samples.append(time.perf_counter_ns() - start)
            roots[mode], inventories[mode] = root, inventory
            verified = verify_layout(root, spec, payloads, mode, as_of, inventory)
            measures[mode] = {**storage_metrics(root), **verified, "inventory_sha256": inventory,
                              "build": {"repetitions": build_repetitions,
                                        "median_ns": statistics.median(build_samples),
                                        "min_ns": min(build_samples), "max_ns": max(build_samples)},
                              "full_validation": sample_times(
                                  lambda: verify_layout(root, spec, payloads, mode, as_of, inventory),
                                  build_repetitions)}
        query_timing = {"direct_scan_and_result_encoding": sample_times(
                            lambda: encode(direct_queries(spec, as_of)), repetitions),
                        "validated_view_result_encoding": sample_times(
                            lambda: encode(view["results"]), repetitions)}
        indexed = roots["indexed_cas"]
        inventory = inventories["indexed_cas"]
        # Select an actual payload file, not an intermediate scope directory.
        first = next(p for p in (indexed / "payload").rglob("*") if p.is_file())
        original_raw = first.read_bytes()
        first.write_bytes(original_raw + b"x")
        probes.append(expect_hold(lambda: verify_layout(indexed, spec, payloads, "indexed_cas", as_of, inventory),
                                  "tampered_payload"))
        first.write_bytes(original_raw)
        first.unlink()
        probes.append(expect_hold(lambda: verify_layout(indexed, spec, payloads, "indexed_cas", as_of, inventory),
                                  "missing_payload"))
        first.write_bytes(original_raw)
        expected_view_hash = digest(encode(view))
        damaged = copy.deepcopy(view)
        damaged["results"]["claim_sources"] = {}
        probes.append(expect_hold(lambda: guard_view(damaged, spec, as_of, expected_view_hash), "tampered_view"))
        refreshed_spec, refreshed_payloads = synthetic_refresh(spec, payloads)
        probes.append(expect_hold(lambda: guard_view(view, refreshed_spec, as_of, expected_view_hash), "stale_source_version"))
        later = (timestamp(as_of) + dt.timedelta(seconds=1)).strftime("%Y-%m-%dT%H:%M:%SZ")
        probes.append(expect_hold(lambda: guard_view(view, spec, later, expected_view_hash), "stale_cutoff"))
        refresh = {}
        for mode in MODES:
            destination = work / (mode + "-refresh")
            start = time.perf_counter_ns()
            new_inventory = build_layout(refreshed_spec, refreshed_payloads, mode, as_of, destination)
            verify_layout(destination, refreshed_spec, refreshed_payloads, mode, as_of, new_inventory)
            elapsed = time.perf_counter_ns() - start
            refresh[mode] = {"build_and_verify_ns": elapsed, **storage_metrics(destination),
                             "inventory_sha256": new_inventory}
        # All negative probes were restored. Re-read original layouts before success.
        for mode in MODES:
            verify_layout(roots[mode], spec, payloads, mode, as_of, inventories[mode])
        require(load_sources(spec, source_root) == payloads, "original inputs changed during run")
    return {"format": "CoEvidenceBundleCanaryReportR0", "status": "BOUNDED_CANARY_PASSED",
            "observed_at": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
            "spec_sha256": digest(encode(spec)), "implementation_sha256": digest(Path(__file__).read_bytes()),
            "source_commit": spec.get("commit"), "source_count": len(payloads),
            "unique_payload_bytes": sum(len(raw) for raw in {digest(v): v for v in payloads.values()}.values()),
            "role_binding_count": sum(len(r["source_ids"]) for r in spec["roles"]),
            "fixture_metadata_status": "TEST_ONLY", "query_as_of": as_of,
            "source_observation_at": spec.get("observed_at"),
            "query_results": reference, "layouts": measures, "query_timing": query_timing,
            "negative_probes": probes, "refresh": {"method": "FULL_REBUILD_OF_SYNTHETIC_ONE_BYTE_DERIVATIVE",
                "original_layouts_retained_and_reverified": True, "incremental_refresh_implemented": False,
                "source_payload_delta_bytes": 1, "layouts": refresh},
            "environment": {"python": platform.python_version(), "platform": platform.system(),
                            "machine": platform.machine(), "timing_clock": "perf_counter_ns"},
            "measurement_scope": {"storage": "logical contents of every file, including inventory and views; not allocated disk",
                "archive": "sorted USTAR members, zero mtimes, gzip level 9 mtime 0, whole-stream compression",
                "build": "serialization, view construction where applicable, writes, inventory reads; inputs already loaded",
                "query": "warm validated in-memory data plus result JSON encoding; excludes load, hashing and validation",
                "validation": "full disk read/hash, metadata checks, reconstruction and reference query comparison",
                "refresh": "one full build and verification per mode; no deletion of original layout",
                "live_remote_staleness_measured": False},
            "effect_boundary": {"source_files_changed": False, "live_workers_started": 0,
                "receiver_adoption": "UNOBSERVED", "external_replication": "NOT_PERFORMED",
                "live_session_sync": "NOT_TESTED"}}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", type=Path, required=True)
    parser.add_argument("--source-root", type=Path, required=True)
    parser.add_argument("--as-of", default="2026-10-22T00:00:00Z", help="synthetic query cutoff, not remote freshness")
    parser.add_argument("--repetitions", type=int, default=31)
    parser.add_argument("--build-repetitions", type=int, default=3)
    args = parser.parse_args(argv)
    try:
        require(args.spec.stat().st_size <= 1024 * 1024, "spec exceeds 1 MiB")
        spec = decode(args.spec.read_bytes())
        report = run_experiment(spec, args.source_root, args.as_of, args.repetitions, args.build_repetitions)
    except (CanaryError, OSError, ValueError, KeyError, TypeError) as exc:
        print(json.dumps({"status": "HELD", "error": str(exc)}, sort_keys=True))
        return 1
    print(json.dumps(report, ensure_ascii=False, sort_keys=True, indent=2, allow_nan=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
