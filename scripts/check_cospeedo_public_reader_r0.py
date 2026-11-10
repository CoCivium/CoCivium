#!/usr/bin/env python3
"""Check CoSpeedo's GitHub-readable entry against exact archived evidence.

No network, no site-health inference and no human comprehension claim.
"""
from pathlib import Path
import json
import re

ROOT = Path(__file__).resolve().parents[1]
PAGE = ROOT / "examples/cospeedo/README.md"
COPRE = ROOT / "CoPre.md"
ARCHIVE = ROOT / "docs/Metrics/COSPEEDO_RECEIPT_CENSUS_R0_20261027.json"
HTML = ROOT / "examples/cospeedo/needle-trails-r1.html"

def main():
    body = PAGE.read_text(encoding="utf-8")
    copre = COPRE.read_text(encoding="utf-8")
    chart = HTML.read_text(encoding="utf-8")
    data = json.loads(ARCHIVE.read_text(encoding="utf-8"))

    assert "# What actually got better?" in body
    assert "examples/cospeedo/README.md" in copre, "No discovery from CoPre"
    assert "needle-trails-r1.html" in body
    assert "not a live dashboard" in body.lower()
    assert "not yet proven" in body.lower()
    assert "unknown coverage" in body.lower()
    assert "human outcome baseline" in body.lower() and "receiver" in body.lower()
    assert "No automatic refresh" in body
    assert "October 20–22 have no captured ledger rows" in body
    assert "42744256246" in body and "42750710011" in body
    assert "<iframe" not in body and "<script" not in body
    assert "Needle trails through time" in chart

    # Plain-language bullets work on narrow GitHub mobile views without a table.
    assert not re.search(r"^\|", body, flags=re.M), "Mobile reader reverted to a table"
    rows = re.findall(
        r"^- \*\*(2026-10-\d{2}):\*\* (\d+) passed, (\d+) held, (\d+) failed\.$",
        body,
        flags=re.M,
    )
    expected_dates = ["2026-10-23", "2026-10-24", "2026-10-25", "2026-10-26"]
    assert [r[0] for r in rows] == expected_dates, rows
    total = 0
    for date, passed, held, failed in rows:
        day = data["days"][date]
        assert (int(passed), int(held), int(failed)) == tuple(
            day["status_counts"][key] for key in ("PASS", "HELD", "FAIL")
        ), date
        total += day["ledger_rows"]
    assert total == data["selected_row_count"] == 145
    for date in ["2026-10-20", "2026-10-21", "2026-10-22"]:
        assert data["days"][date]["coverage_state"] == "NO_LEDGER_ROWS__UNKNOWN_NE_ZERO"

    # Validate local reference destinations, without assuming GitHub HTTPS works.
    for target in re.findall(r"\]\(([^)]+)\)", body):
        if target.startswith(("https://", "http://", "#")):
            continue
        candidate = (PAGE.parent / target.split("#", 1)[0]).resolve()
        assert candidate.is_relative_to(ROOT) and candidate.is_file(), target
    print("PASS_COSPEEDO_PUBLIC_READER_EXACT_ARCHIVE_LINKS_AND_NONCLAIMS")

if __name__ == "__main__":
    main()
