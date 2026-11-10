#!/usr/bin/env python3
"""CoSpeedo Morning Glance R2 public-source acceptance: no network or OS effects.

Checks visual/semantic anchors against one dated typed evidence record.
It does NOT claim a rendered browser, independent receiver, or live dashboard.
"""
import json
import re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "examples/cospeedo/morning-glance-r2.html"
DATA = ROOT / "docs/Metrics/COSPEEDO_MORNING_GLANCE_R2_20261110.json"
STAGES = [
    "UNVERIFIED_SOURCE", "VERIFIED_PUBLIC_SOURCE",
    "SAME_PROVIDER_COLD_HANDOFF", "INDEPENDENT_RECEIVER",
    "PROVEN_RECOVERY_WITH_MEASURED_BENEFIT",
]
EXPECTED_RUNS = (42864184377, 42851899467)

class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
        self.bad = []
        self.svgs = []
        self.svg_titles = []
        self.heading_tags = []
        self.inline_style = 0
        self.details = 0
        self.summaries = 0
        self.articles = 0
        self.ids = set()
        self.duplicate_ids = []
    def handle_starttag(self, tag, attributes):
        a = dict(attributes)
        if tag in {"script", "iframe", "form", "audio", "video", "object", "embed", "canvas"}:
            self.bad.append(tag)
        if tag in {"img", "link", "source", "script"} and a.get("src"):
            self.bad.append((tag, a["src"]))
        if tag == "link" and a.get("href"):
            self.bad.append((tag, a["href"]))
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        if tag == "style":
            self.inline_style += 1
        if tag == "svg":
            self.svgs.append(a)
        if tag == "h1":
            self.heading_tags.append(tag)
        if tag == "details":
            self.details += 1
        if tag == "summary":
            self.summaries += 1
        if tag == "article":
            self.articles += 1
        if "id" in a:
            if a["id"] in self.ids:
                self.duplicate_ids.append(a["id"])
            self.ids.add(a["id"])
        if any(k.startswith("on") for k in a):
            self.bad.append("inline_event_handler")
    def handle_startendtag(self, tag, attributes):
        self.handle_starttag(tag, attributes)

def main():
    html = PAGE.read_text(encoding="utf-8")
    data = json.loads(DATA.read_text(encoding="utf-8"))
    assert data["schema"] == "CoSpeedo.MorningGlance.R2"
    assert data["state"] == "PUBLIC_SOURCE_CANDIDATE_NOT_LIVE_PRODUCT"
    assert data["observed_at"].startswith("2026-11-10T17:22:")
    gauge = data["gauge"]
    assert gauge["measurement_type"] == "CATEGORICAL_EVIDENCE_MATURITY_NOT_VELOCITY_OR_PERCENTAGE"
    assert gauge["ordered_stages"] == STAGES
    assert gauge["observed_stage"] == STAGES[2]
    assert all(gauge[k] is False for k in ("independent_receiver_ack", "survived_24h", "runtime_deployment"))
    assert gauge["measured_human_time_saved_minutes"] is None
    assert len(data["evidence"]) == 2
    assert tuple(e["run_id"] for e in data["evidence"]) == EXPECTED_RUNS
    assert data["evidence"][0]["work_id"].startswith("copre:cold:")
    assert data["evidence"][0]["external_receiver_ack"] is False
    assert data["evidence"][1]["x2_runtime_proof"] is False
    assert len(data["public_routes"]["proposed_mirrors"]) == 3
    assert all(e["last_verified_http_status"] == 404 for e in data["public_routes"]["proposed_mirrors"])
    assert data["next_elected_gate"] == "EXACT_OBJECT_COLD_READBACK_BY_AUTHORIZED_RECEIVER_OUTSIDE_GITHUB_FAILURE_DOMAIN"
    assert data["no_user_action_required_for_this_source_review"] is True

    p = Page()
    p.feed(html)
    assert not p.bad, p.bad
    assert not p.duplicate_ids, p.duplicate_ids
    assert len(p.heading_tags) == 1
    assert len(p.svgs) == 1 and p.svgs[0].get("role") == "img"
    assert p.svgs[0].get("aria-labelledby") == "dial-title dial-desc"
    assert {"dial-title", "dial-desc"}.issubset(p.ids)
    assert p.inline_style == 1
    assert p.articles == 3
    assert p.details == p.summaries == 1
    assert "@media(max-width:760px)" in html and "prefers-reduced-motion" in html
    assert "Good morning." in html and "Here's what carried itself." in html
    assert "The next useful step is not another prompt" in html
    assert "categorical evidence snapshot, not live telemetry" in html
    assert "Your time back" in html and "Unknown" in html
    assert "24-hour" in html and "outside GitHub" in html
    assert "source proof is not product acceptance" in html.lower()
    assert "No background recording" in html
    assert all(str(event["run_id"]) in html for event in data["evidence"])
    assert data["evidence"][0]["work_id"] in html
    assert "31 packet safety tests" in html and "28 source-policy tests" in html
    assert "returned 404" in html
    assert not re.search(r"(?:fetch\(|setInterval\(|navigator\.clipboard|window\.open\()", html)
    assert not re.search(r"<(?:audio|video|form|iframe|script)\b", html, re.I)

    assert p.links, "No evidence routes"
    for link in p.links:
        if link.startswith("#"):
            assert link[1:] in p.ids
            continue
        if link.startswith("https://"):
            u = urlsplit(link)
            assert u.hostname == "github.com" and u.path.startswith("/CoCivium/CoCivium/"), link
            continue
        assert not link.startswith(("http://", "//", "javascript:", "data:")), link
        path = (PAGE.parent / link.split("#", 1)[0]).resolve()
        assert path.is_relative_to(ROOT) and path.is_file(), link
    required = {"../../CoPre.md", "needle-trails-r1.html",
                "../../docs/Metrics/COSPEEDO_MORNING_GLANCE_R2_20261110.json", "README.md"}
    assert required.issubset(set(p.links)), required.difference(p.links)
    assert "no live telemetry" in html.lower() and "not yet measurable" in html.lower()
    print("PASS_COSPEEDO_MORNING_GLANCE_R2_SOURCE_LEDGER_NEEDLE_ACCESSIBILITY_NONCLAIMS")

if __name__ == "__main__":
    main()
