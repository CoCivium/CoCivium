#!/usr/bin/env python3
"""Deterministic, offline CoMail fixture compiler. No sockets, sends or payment calls."""
from __future__ import annotations

import argparse
import html
import json
import hashlib
from pathlib import Path
from xml.etree import ElementTree as ET

from core import json_bytes, read_fixture, sha, validate

ROOT = Path(__file__).resolve().parent


def embed(obj: dict) -> str:
    # Defend the inline application/json element from a malicious closing tag.
    return json.dumps(obj, sort_keys=True, ensure_ascii=False, separators=(",", ":")).replace("<", "\\u003c").replace(">", "\\u003e").replace("&", "\\u0026")


def make_html(obj: dict) -> str:
    template = (ROOT / "template.html").read_text("utf-8")
    assert template.count("__COMAIL_JSON__") == 1
    return template.replace("__COMAIL_JSON__", embed(obj))


def make_atom(obj: dict) -> str:
    """Static *example* Atom feed; relative URLs intentionally not public endpoints."""
    ET.register_namespace("", "http://www.w3.org/2005/Atom")
    ns = "{http://www.w3.org/2005/Atom}"
    r = obj["resource"]
    versions = r["versions"]
    root = ET.Element(ns + "feed")
    ET.SubElement(root, ns + "id").text = r["resource_id"]
    ET.SubElement(root, ns + "title").text = "CoMail R0 synthetic living resource · no live subscription"
    ET.SubElement(root, ns + "updated").text = versions[-1]["observed_at"]
    ET.SubElement(root, ns + "author").append(ET.Element(ns + "name"))
    root.find(ns + "author").find(ns + "name").text = "Synthetic CoCivium design example"
    ET.SubElement(root, ns + "link", {"href": "feed.atom", "rel": "self", "type": "application/atom+xml"})
    ET.SubElement(root, ns + "link", {"href": "index.html", "rel": "alternate", "type": "text/html"})
    for v in versions:
        entry = ET.SubElement(root, ns + "entry")
        ET.SubElement(entry, ns + "id").text = r["resource_id"] + ":" + v["id"]
        ET.SubElement(entry, ns + "title").text = v["headline"]
        ET.SubElement(entry, ns + "updated").text = v["observed_at"]
        ET.SubElement(entry, ns + "published").text = v["observed_at"]
        ET.SubElement(entry, ns + "content", {"type": "text"}).text = v["body"]
        ET.SubElement(entry, ns + "link", {"href": "index.html#" + v["id"], "rel": "alternate", "type": "text/html"})
        ET.SubElement(entry, ns + "summary").text = "Synthetic demonstration version: " + v["why_changed"]
    return '<?xml version="1.0" encoding="utf-8"?>\n' + ET.tostring(root, encoding="unicode", short_empty_elements=True) + "\n"


def outputs() -> dict[str, str]:
    obj = read_fixture(ROOT / "fixture.json")
    h = make_html(obj)
    feed = make_atom(obj)
    rec = validate(obj) | {
        "html_sha256": sha(h.encode()),
        "feed_sha256": sha(feed.encode()),
        "fixture_sha256": sha((ROOT / "fixture.json").read_bytes()),
        "source_contracts": obj["source_contracts"],
        "nonclaims": obj["nonclaims"],
        "source_not_receiver": True,
    }
    return {"index.html": h, "feed.atom": feed, "receipt.json": json.dumps(rec, indent=2, ensure_ascii=False) + "\n"}


def check_donors(obj: dict) -> None:
    # Source-contract pin check uses the git blob identity on the local clean checkout.
    # The check is network-free and makes changed donor documents an explicit hold.
    checkout_root=ROOT.parents[1]
    for item in obj["source_contracts"]:
        file=checkout_root / item["path"]
        if not file.is_file():
            raise SystemExit("HOLD_MISSING_SOURCE_DONOR " + item["path"])
        data=file.read_bytes()
        blob=hashlib.sha1(b"blob "+str(len(data)).encode("ascii")+b"\0"+data).hexdigest()
        if blob != item["blob_sha"]:
            raise SystemExit("FAIL_SOURCE_DONOR_MISMATCH " + item["path"])
    print("PASS_COMAIL_R0_PINNED_SOURCE_DONORS",len(obj["source_contracts"]))


def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true")
    p.add_argument("--check-donors", action="store_true")
    args = p.parse_args()
    if args.check_donors:
        check_donors(read_fixture(ROOT / "fixture.json"))
    for name, content in outputs().items():
        path = ROOT / name
        if args.check:
            if not path.exists() or path.read_text("utf-8") != content:
                raise SystemExit("FAIL_DETERMINISM " + name)
        else:
            path.write_text(content, encoding="utf-8")
    print("PASS_COMAIL_R0_DETERMINISM_AND_BOUNDARIES" if args.check else "GENERATED_COMAIL_R0")


if __name__ == "__main__":
    main()
