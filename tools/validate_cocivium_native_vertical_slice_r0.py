#!/usr/bin/env python3
import argparse
import hashlib
import json
import re
import subprocess
from html.parser import HTMLParser
from pathlib import Path

FIXTURE = Path("fixtures/ux/cocivium_native_vertical_slice_r0.json")


def fail(code):
    raise SystemExit("FAIL:" + code)


def git_blob(path):
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], text=True).strip()


class SliceParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = []
        self.surfaces = []
        self.roles = []
        self.lang_buttons = []
        self.body_head_sha = None

    def handle_starttag(self, tag, attrs):
        d = dict(attrs)
        if "id" in d:
            self.ids.append(d["id"])
        if "data-surface" in d:
            self.surfaces.append(d["data-surface"])
        if "data-role" in d:
            self.roles.append(d["data-role"])
        if "data-lang" in d:
            self.lang_buttons.append(d["data-lang"])
        if tag == "body":
            self.body_head_sha = d.get("data-head-sha")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    args = ap.parse_args()

    doc = json.loads(FIXTURE.read_text(encoding="utf-8"))
    src = doc["source_bindings"]
    checks = [
        ("public_onboarding_doc_path", "public_onboarding_doc_blob_sha"),
        ("cobar_delivery_doc_path", "cobar_delivery_doc_blob_sha"),
        ("cotime_doc_path", "cotime_doc_blob_sha"),
        ("cocivia_identity_path", "cocivia_identity_blob_sha"),
    ]
    for path_key, sha_key in checks:
        if git_blob(src[path_key]) != src[sha_key]:
            fail("SOURCE_BIND:" + src[path_key])

    raw = Path(args.input).read_bytes()
    text = raw.decode("utf-8")
    parser = SliceParser()
    parser.feed(text)

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    if parser.body_head_sha != head:
        fail("HEAD_BIND")

    required_surfaces = {"CoBar", "CoReply", "CoVIA", "CoTime", "LearningPath"}
    if not required_surfaces.issubset(set(parser.surfaces)):
        fail("SURFACE_SET")

    if parser.roles.count("CoCivia") != 1:
        fail("COCIVIA_ROLE_COUNT")
    if parser.ids.count("cocivia-avatar") != 1:
        fail("AVATAR_COUNT")
    if parser.ids.count("cobar-input") != 1:
        fail("COBAR_INPUT_COUNT")
    if parser.ids.count("coreply") != 1:
        fail("COREPLY_COUNT")

    if sorted(set(parser.lang_buttons)) != ["en-CA", "fr-CA"]:
        fail("LANGUAGE_BUTTON_SET")

    if "CoHereNow" not in text or "Meaning" not in text or "NextSafeAction" not in text:
        fail("UX_SUMMARY_CONTRACT")

    journey = doc["journey"]
    for section in ["synthetic_user_input", "reply", "cohere_now", "meaning", "next_safe_action"]:
        for lang in ["en-CA", "fr-CA"]:
            if journey[section][lang] not in text:
                fail("MISSING_TRANSLATION:" + section + ":" + lang)

    for item in doc["evidence"]:
        if item["id"] not in text or item["state"] not in text:
            fail("EVIDENCE_CARD:" + item["id"])

    for step in doc["learning_path"]:
        for lang in ["en-CA", "fr-CA"]:
            if step["title"][lang] not in text or step["detail"][lang] not in text:
                fail("LEARNING_PATH:" + str(step["step"]) + ":" + lang)

    lowered = text.lower()
    forbidden_external = [
        "src=\"http://",
        "src=\"https://",
        "href=\"http://",
        "href=\"https://",
        "fetch(",
        "xmlhttprequest",
        "websocket("
    ]
    if any(token in lowered for token in forbidden_external):
        fail("EXTERNAL_NETWORK_DEPENDENCY")

    if re.search(r"\b(powershell|cmd\.exe|terminal required|cli required)\b", lowered):
        fail("VISIBLE_CLI_DEPENDENCY")

    ux = doc["ux_contract"]
    if ux["visible_cli_required"] is not False:
        fail("FIXTURE_CLI_CONTRACT")
    if ux["account_required_for_preview"] is not False:
        fail("FIXTURE_ACCOUNT_CONTRACT")
    if ux["resource_contribution_required"] is not False:
        fail("FIXTURE_RESOURCE_CONTRACT")
    if ux["external_network_required_by_rendered_artifact"] is not False:
        fail("FIXTURE_NETWORK_CONTRACT")

    digest = hashlib.sha256(raw).hexdigest().upper()
    receipt = {
        "STATE": "PASS_COCIVIUM_NATIVE_VERTICAL_SLICE_R0",
        "checked_out_head_sha": head,
        "html_sha256": digest,
        "surface_roles_present": sorted(required_surfaces | {"CoCivia"}),
        "avatar_count": 1,
        "primary_input_count": 1,
        "primary_reply_count": 1,
        "language_projections": ["en-CA", "fr-CA"],
        "external_network_dependency": False,
        "visible_cli_dependency": False,
        "account_required_for_preview": False,
        "resource_contribution_required": False,
        "public_deployment": False,
        "runtime_effect": False,
        "ux_state": "UX_ACCEPTANCE_UNPROVEN",
        "nonclaims": doc["nonclaims"]
    }
    print(json.dumps(receipt, separators=(",", ":")))


if __name__ == "__main__":
    main()
