"""R1 gallery proof-pin tests. Source-only, reversible, not hosted approval.

Checks that user-facing immutable GitHub links reproduce the historical
observed Git blob IDs in the machine manifest. Optional remote readback
uses only nine hardcoded public GitHub snapshot endpoints, no tokens.
"""
from __future__ import annotations

import copy
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import sys
import unittest
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT / "proof-gallery.json"
HTML = ROOT / "proof-gallery.html"
BLOB = re.compile(r"^[a-f0-9]{40}$")
HISTORIC = {
    "CoPreCursor": ("f2a7d70a48f461424c904fb4721e3ccd2d3940d2",
                    "14520a4992b2d723fe33c6cbfffa1815c87df670", True),
    "CoOrbWare": ("5ca76d0808003eda51bb90a003aa785d1333bae4",
                  "634adc3ae92e5aba9671427ca56a78a1a72d05f9", True),
    "CoLensMedia": ("a7a4fa22619183d21549ebd62db51e532e196666",
                    "b5a87427f2a6bf3c5e4928b7aa2c64e3a46deb01", True),
    "CoTheoryAll": ("090c532627cd014e6c41355ddd70b90a56cc03ff",
                    "21da563a35106896c3029ea8f2cc4fd30cfa31c3", False),
    "CognocartaConsenti": ("090c532627cd014e6c41355ddd70b90a56cc03ff",
                           "997a0b6951c52b58dc479a6075a743336a6449c5", False),
    "CoSubstrateField": ("090c532627cd014e6c41355ddd70b90a56cc03ff",
                         "5fec3249945ad3d14511621bc52da5587c3526b8", False),
    "CoPlan": ("090c532627cd014e6c41355ddd70b90a56cc03ff",
               "261f120b648835c50e9a1e1ecb728e8cdc2825f6", False),
    "CoPhoenix": ("615b0e99ad4fb9ad2f126d71be0d57da82f98937",
                  "b891405f587bc296297a932a9bb3f519eb16e741", False),
    "CoSpiff": ("090c532627cd014e6c41355ddd70b90a56cc03ff",
                "40d1a5706ce7cead09d9c6a9a155bb57e4162d46", False),
}
URL = re.compile(
    r"^https://github[.]com/(CoCivium/(?:CoCivium|CoAcademy))/"
    r"blob/([a-f0-9]{40})/([A-Za-z0-9_./-]+)$"
)
DEFAULT = re.compile(
    r"^https://github[.]com/(CoCivium/(?:CoCivium|CoAcademy))/"
    r"blob/(?:main|master)/([A-Za-z0-9_./-]+)$"
)


class Anchors(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.source_links: list[str] = []
        self.forms = 0

    def handle_starttag(self, tag, attrs):
        info = dict(attrs)
        if tag == "form":
            self.forms += 1
        if tag == "a" and "source" in (info.get("class") or "").split():
            self.source_links.append(info.get("href", ""))


def audit(data, document):
    """No I/O; exact nine-record source and human-link consistency gate."""
    issues = []
    try:
        items = data["items"]
        source_policy = data["source_pin_policy"]
    except (KeyError, TypeError):
        return ["HOLD_MALFORMED_MANIFEST"]
    if not isinstance(items, list) or len(items) != 9:
        issues.append("HOLD_EXHIBIT_COUNT")
        return sorted(set(issues))
    labels, urls = set(), set()
    for row in items:
        if not isinstance(row, dict):
            issues.append("HOLD_ITEM_SHAPE")
            continue
        id_ = row.get("id")
        if id_ in labels:
            issues.append("HOLD_DUPLICATE_EXHIBIT")
        labels.add(id_)
        expected = HISTORIC.get(id_)
        if expected is None:
            issues.append("HOLD_UNKNOWN_EXHIBIT")
            continue
        commit, blob, changed = expected
        if row.get("source_snapshot_commit") != commit or row.get("blob") != blob:
            issues.append("HOLD_SOURCE_PIN_DRIFT")
        if row.get("source_snapshot_blob_verified") is not True:
            issues.append("HOLD_UNVERIFIED_SOURCE_ASSERTION")
        if row.get("default_branch_changed_from_snapshot_on_20261120") is not changed:
            issues.append("HOLD_MUTABILITY_STATUS_DRIFT")
        source = row.get("source")
        previous = row.get("default_branch_source")
        a = URL.fullmatch(source) if isinstance(source, str) else None
        b = DEFAULT.fullmatch(previous) if isinstance(previous, str) else None
        if a is None or b is None or a.group(1) != b.group(1) or a.group(3) != b.group(2) or a.group(2) != commit:
            issues.append("HOLD_MALFORMED_SNAPSHOT_URL")
        if isinstance(source, str):
            if source in urls:
                issues.append("HOLD_DUPLICATE_SOURCE_URL")
            urls.add(source)
    if set(HISTORIC) != labels:
        issues.append("HOLD_EXHIBIT_SET")
    if not isinstance(source_policy, dict) or source_policy.get("verified_gallery_items") != 9 or set(source_policy.get("default_branch_drift_at_review", [])) != {k for k, v in HISTORIC.items() if v[2]}:
        issues.append("HOLD_SOURCE_POLICY_DRIFT")
    a = Anchors()
    try:
        a.feed(document)
    except Exception:
        issues.append("HOLD_HTML_PARSE")
    if a.forms:
        issues.append("HOLD_UNEXPECTED_GALLERY_FORM")
    if len(a.source_links) != 9 or set(a.source_links) != urls:
        issues.append("HOLD_HUMAN_MACHINE_SOURCE_DIVERGENCE")
    if any(DEFAULT.fullmatch(x or "") for x in a.source_links):
        issues.append("HOLD_MUTABLE_VISITOR_SOURCE")
    if "newer GitHub branch versions may differ" not in document:
        issues.append("HOLD_NO_DRIFT_DISCLOSURE")
    for key, (_, sha, _) in HISTORIC.items():
        if "Observed Git blob: " + sha[:12] not in document:
            issues.append("HOLD_HISTORIC_FINGERPRINT_MISSING")
    return sorted(set(issues))


class GalleryProofTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(SOURCE.read_text(encoding="utf-8"))
        cls.html = HTML.read_text(encoding="utf-8")

    def test_exact_nine_pins_and_site_links(self):
        self.assertEqual(audit(self.data, self.html), [])

    def test_no_forms_or_automatic_data_submission(self):
        self.assertNotIn("<form", self.html.casefold())
        self.assertNotIn("fetch(", self.html.casefold())

    def test_archive_original_revision_is_not_overwritten(self):
        self.assertEqual(self.data.get("observed_on"), "2026-10-24")
        self.assertEqual(self.data.get("global_gates", {}).get("www_human_front_door"),
                         "REVIEW_REQUIRED_LEGACY_METADATA_INDEX")

    def test_one_mutable_source_cannot_masquerade_as_witness(self):
        old = copy.deepcopy(self.data)
        old["items"][0]["source"] = old["items"][0]["default_branch_source"]
        self.assertIn("HOLD_MALFORMED_SNAPSHOT_URL", audit(old,self.html))

    def test_forged_snapshot_blob_rejected(self):
        m = copy.deepcopy(self.data)
        m["items"][0]["blob"] = "f" * 40
        self.assertIn("HOLD_SOURCE_PIN_DRIFT", audit(m, self.html))

    def test_source_epoch_mismatch_held(self):
        m = copy.deepcopy(self.data)
        m["items"][1]["source_snapshot_commit"] = "a"*40
        self.assertIn("HOLD_SOURCE_PIN_DRIFT", audit(m, self.html))

    def test_wrong_snapshotted_path_rejected(self):
        m = copy.deepcopy(self.data)
        m["items"][2]["source"] += "/stale.md"
        self.assertIn("HOLD_MALFORMED_SNAPSHOT_URL", audit(m,self.html))

    def test_duplicate_exhibit_rejected(self):
        m = copy.deepcopy(self.data)
        m["items"][1]["id"] = m["items"][0]["id"]
        self.assertIn("HOLD_DUPLICATE_EXHIBIT",audit(m,self.html))

    def test_missing_exhibit_rejected(self):
        m = copy.deepcopy(self.data)
        m["items"].pop()
        self.assertIn("HOLD_EXHIBIT_COUNT",audit(m,self.html))

    def test_one_human_anchor_mismatch_rejected(self):
        m = self.html.replace(
            self.data["items"][0]["source"],
            self.data["items"][0]["default_branch_source"]
        )
        self.assertIn("HOLD_HUMAN_MACHINE_SOURCE_DIVERGENCE",audit(self.data,m))
        self.assertIn("HOLD_MUTABLE_VISITOR_SOURCE",audit(self.data,m))

    def test_drift_status_not_silently_promoted(self):
        m = copy.deepcopy(self.data)
        m["items"][0]["default_branch_changed_from_snapshot_on_20261120"]=False
        self.assertIn("HOLD_MUTABILITY_STATUS_DRIFT",audit(m,self.html))

    def test_spoofed_verified_label_rejected(self):
        m = copy.deepcopy(self.data)
        m["items"][0]["source_snapshot_blob_verified"]="true"
        self.assertIn("HOLD_UNVERIFIED_SOURCE_ASSERTION",audit(m,self.html))

    def test_wrong_host_rejected(self):
        m = copy.deepcopy(self.data)
        m["items"][0]["source"]="https://evil.example/exfiltrate"
        self.assertIn("HOLD_MALFORMED_SNAPSHOT_URL",audit(m,self.html))

    def test_removed_fingerprint_rejected(self):
        m = self.html.replace("Observed Git blob: "+HISTORIC["CoPlan"][1][:12],
                              "Observed Git blob: unknown")
        self.assertIn("HOLD_HISTORIC_FINGERPRINT_MISSING",audit(self.data,m))

    def test_drift_disclosure_required(self):
        m = self.html.replace("newer GitHub branch versions may differ","always latest")
        self.assertIn("HOLD_NO_DRIFT_DISCLOSURE",audit(self.data,m))

    def test_excess_inline_form_rejected(self):
        self.assertIn("HOLD_UNEXPECTED_GALLERY_FORM",audit(self.data,self.html+"<form></form>"))


def remote_pin_readback():
    """CI-only network verification, fixed public source snapshots, no tokens."""
    j = json.loads(SOURCE.read_text(encoding="utf-8"))
    issues = audit(j, HTML.read_text(encoding="utf-8"))
    if issues:
        raise RuntimeError("HOLD_STATIC_GALLERY_CONTRACT")
    observations = []
    for row in j["items"]:
        match = URL.fullmatch(row["source"])
        if not match:
            raise RuntimeError("HOLD_UNLISTED_SOURCE_HOST")
        repo, commit, path = match.groups()
        url = f"https://raw.githubusercontent.com/{repo}/{commit}/{path}"
        req = Request(url,headers={"User-Agent":"CoCivium-Gallery-PinnedSourceCanary-R0"})
        with urlopen(req,timeout=15) as response:
            if response.status != 200 or response.geturl().split("/")[2] != "raw.githubusercontent.com":
                raise RuntimeError("HOLD_SOURCE_REDIRECT_OR_NON200")
            data = response.read(2_000_001)
        if not 0 < len(data) <= 2_000_000:
            raise RuntimeError("HOLD_SOURCE_SIZE")
        actual = hashlib.sha1(b"blob " + str(len(data)).encode("ascii") + b"\0" + data).hexdigest()
        if actual != row["blob"]:
            raise RuntimeError("HOLD_SOURCE_GIT_BLOB_MISMATCH:"+row["id"])
        observations.append({"id":row["id"],"sha1":actual,"bytes":len(data),
                             "commit":commit})
    # Exact-source metadata only; never print or retain source bytes.
    print(json.dumps({"state":"PASS_NINE_PINNED_PUBLIC_SOURCE_BLOB_READBACKS",
                      "count":len(observations),"observations":observations,
                      "effect":"READ_ONLY_EXTERNAL_GITHUB_SOURCE", 
                      "nonclaims":["NOT_INDEPENDENT_PROVIDER","NOT_HOSTED_GALLERY",
                                   "NO_VISITOR_ACCEPTANCE","NO_PUBLIC_RELEASE"]}))
    return 0


if __name__ == "__main__":
    if len(sys.argv) == 2 and sys.argv[1] == "--remote-verify":
        sys.exit(remote_pin_readback())
    unittest.main()
