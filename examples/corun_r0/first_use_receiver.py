#!/usr/bin/env python3
"""CoPreCursor first-use artifact receiver with no repository checkout.

Checks the source bundle and producer receipt, extracts exact pinned HTML into
an isolated temporary directory, then runs a synthetic Chromium user journey.
This is same-provider cross-runner evidence, not off-provider custody, human
acceptance, long-term restore, installed runtime, or an actual CoStead receiver.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
from pathlib import Path
import tempfile
import zipfile

from playwright.sync_api import sync_playwright

PIN = "773e9de7aa7c6b03bf0bc75eddb7ca0a0c8dd101"
EXPECTED = "Test one CoMap relation, then "
SENTINEL = "ONLY_LOCAL_TEST_MARKER_NOT_FOR_RECEIPT"


def canonical(obj):
    return (json.dumps(obj, sort_keys=True, ensure_ascii=True,
                       separators=(",", ":")) + "\n").encode("utf-8")


def blobsha(raw):
    return hashlib.sha1(
        b"blob " + str(len(raw)).encode() + b"\x00" + raw
    ).hexdigest()


def check(value, label, cases):
    cases.append({"name": label, "passed": bool(value)})
    if not value:
        raise AssertionError("FAIL_CLOSED: " + label)


def verify_and_replay(bundle_path, producer_path):
    cases = []
    bundle = bundle_path.read_bytes()
    producer = json.loads(producer_path.read_text(encoding="utf-8"))
    check(0 < len(bundle) < 2_500_000, "CAPSULE_BOUNDED", cases)
    check(producer.get("schema") == "CoCivium.CoPreCursor.CapsuleProducerReceipt.R0",
          "PRODUCER_RECEIPT_SCHEMA", cases)
    check(hashlib.sha256(bundle).hexdigest() == producer.get("capsule_sha256"),
          "EXACT_CAPSULE_READBACK_SHA256", cases)
    check(producer.get("result") == "PACKAGE_CREATED_NOT_LANDED"
          and producer.get("receiver_ack") is False, "NO_IMPLIED_PREVIOUS_PICKUP", cases)
    with zipfile.ZipFile(io.BytesIO(bundle)) as zipped:
        check(sorted(zipped.namelist()) == ["index.html", "manifest.json"],
              "EXACT_ZIP_ALLOWLIST", cases)
        check(all(info.file_size < 2_000_000 and not info.is_dir()
                  for info in zipped.infolist()), "ZIP_UNCOMPRESSED_BOUNDED", cases)
        manifest = json.loads(zipped.read("manifest.json"))
        html = zipped.read("index.html")
    check(manifest.get("schema") == "CoCivium.CoPreCursor.SourceHandoffCapsule.R0",
          "MANIFEST_SCHEMA", cases)
    check(manifest.get("source_path") == "examples/coprecursor/index.html",
          "SOURCE_PATH_PROVENANCE", cases)
    check(blobsha(html) == PIN == manifest.get("blob_sha1")
          == producer.get("source_blob_sha1"), "PINNED_GIT_BLOB_READBACK", cases)
    check(hashlib.sha256(html).hexdigest() == manifest.get("source_sha256")
          == producer.get("source_sha256"), "PINNED_SOURCE_SHA256_READBACK", cases)
    check(len(html) == manifest.get("source_bytes"),
          "PINNED_SOURCE_BYTECOUNT", cases)
    check(manifest.get("user_data_included") is False
          and manifest.get("durable_custody") is False
          and manifest.get("product_promotion") is False,
          "NO_FALSE_LIFECYCLE_PROMOTION", cases)

    outbound, errors = [], []
    with tempfile.TemporaryDirectory(prefix="coprecursor-capsule-receiver-") as folder:
        source = Path(folder) / "index.html"
        source.write_bytes(html)
        check(source.read_bytes() == html, "EXTRACTED_SOURCE_IDENTITY", cases)
        with sync_playwright() as pw:
            browser = pw.chromium.launch(headless=True)
            version = browser.version
            page = browser.new_page(viewport={"width": 390, "height": 844})
            page.on("request", lambda r: outbound.append(r.url)
                    if r.url.startswith(("https://", "http://")) else None)
            page.on("pageerror", lambda e: errors.append(str(e)))
            page.goto(source.as_uri())
            field = page.locator("#draft")
            check(field.input_value() == EXPECTED
                  and page.locator("#accept").is_disabled(),
                  "CLEAN_RECEIVER_BASELINE", cases)
            page.locator("#preview").click()
            candidate = page.locator("#prediction").inner_text()
            check("typed relation" in candidate
                  and field.input_value() == EXPECTED,
                  "CLEAN_RECEIVER_PREVIEW_NO_EFFECT", cases)
            page.locator("#accept").click()
            check(field.input_value() == EXPECTED + candidate
                  and page.locator("#undo").is_enabled(),
                  "CLEAN_RECEIVER_EXPLICIT_ACCEPT", cases)
            page.locator("#undo").click()
            check(field.input_value() == EXPECTED
                  and page.locator("#undo").is_disabled(),
                  "CLEAN_RECEIVER_EXACT_UNDO", cases)
            page.locator("#preview").click()
            page.locator("#reject").click()
            check(field.input_value() == EXPECTED
                  and page.locator("#accept").is_disabled(),
                  "CLEAN_RECEIVER_REJECT_NO_CHANGE", cases)
            field.fill(SENTINEL)
            page.locator("#receipt").click()
            rendered = page.locator("#receipt-output").inner_text()
            receipt = json.loads(rendered)
            check(SENTINEL not in rendered
                  and receipt.get("raw_included") is False
                  and receipt.get("effects") == 0
                  and receipt.get("remote_receivers") == 0,
                  "CLEAN_RECEIVER_NO_PRIVATE_LEAK_IN_RECEIPT", cases)
            page.locator('[data-mode="ambient"]').click()
            check(not page.locator("#editor-panel").is_visible()
                  and not page.locator("#receipt-panel").is_visible(),
                  "CLEAN_RECEIVER_AMBIENT_PRIVATE", cases)
            page.locator('[data-mode="glance"]').click()
            page.locator("#reset").click()
            check(field.input_value() == EXPECTED
                  and page.locator("#undo").is_disabled(),
                  "CLEAN_RECEIVER_RESET", cases)
            field.fill(SENTINEL)
            page.reload()
            check(field.input_value() == EXPECTED
                  and page.locator("#accept").is_disabled(),
                  "CLEAN_RECEIVER_RELOAD_ERASES_DRAFT", cases)
            check(page.evaluate(
                "document.documentElement.scrollWidth <= innerWidth + 1"),
                "CLEAN_RECEIVER_MOBILE_WIDTH", cases)
            browser.close()
    check(not outbound, "NO_EXTERNAL_HTTP_REQUESTS", cases)
    check(not errors, "NO_PAGE_JAVASCRIPT_ERRORS", cases)
    return {
        "schema": "CoCivium.CoPreCursor.IsolatedRunnerReadbackR0",
        "producer_capsule_sha256": hashlib.sha256(bundle).hexdigest(),
        "source_blob_sha1": PIN,
        "source_sha256": hashlib.sha256(html).hexdigest(),
        "source_bytes": len(html),
        "receiver_type": "ISOLATED_GITHUB_ACTIONS_JOB_NO_REPOSITORY_CHECKOUT",
        "browser": {"engine": "chromium", "version": version,
                    "viewport": [390, 844]},
        "checks": cases,
        "total": len(cases),
        "passed": len(cases),
        "receiver_readback": "EXACT_BUNDLE_AND_SOURCE_BYTES",
        "behavioral_replay": "PASS_AUTOMATED_SYNTHETIC_TASK",
        "cross_provider": False,
        "durable_destination": False,
        "human_acceptance": "NOT_TESTED",
        "coprecursor_user_data_restored": False,
        "qualified_mvp": False,
        "operational_receiver": False,
        "no_external_effects": True,
        "nonclaims": [
            "ISOLATED_GITHUB_JOB_NE_INDEPENDENT_PROVIDER",
            "RUNNER_READBACK_NE_DURABLE_CUSTODY",
            "DEMO_RESTART_NE_USER_DATA_BACKUP",
            "AUTOMATED_SYNTHETIC_TASK_NE_HUMAN_ACCEPTANCE",
            "ZIP_TRANSPORT_NE_COSTEAD_PICKUP_OR_COEX",
            "NO_MVP_OR_PRODUCTION_SWITCH",
        ],
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capsule", required=True, type=Path)
    parser.add_argument("--producer-receipt", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    try:
        report = verify_and_replay(args.capsule, args.producer_receipt)
        args.out.mkdir(parents=True, exist_ok=False)
        raw = canonical(report)
        with (args.out / "receiver-readback.json").open("xb") as file:
            file.write(raw)
        receipt = {
            "schema": "CoCivium.CoPreCursor.ReceiverReadbackReceiptR0",
            "report_sha256": hashlib.sha256(raw).hexdigest(),
            "capsule_sha256": report["producer_capsule_sha256"],
            "source_sha256": report["source_sha256"],
            "source_blob_sha1": report["source_blob_sha1"],
            "result": "PASS_ISOLATED_SAME_PROVIDER_JOB_ONLY",
            "durable_custody": False,
            "independent_provider": False,
            "human_acceptance": False,
            "mvp_qualified": False,
        }
        with (args.out / "receipt.json").open("xb") as file:
            file.write(canonical(receipt))
    except (OSError, ValueError, AssertionError, json.JSONDecodeError,
            zipfile.BadZipFile) as exc:
        print("HOLD_OR_FAIL_CLOSED:", str(exc))
        return 2
    print(json.dumps({"result": receipt["result"], "checks": report["total"],
                      "mvp_qualified": False}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
