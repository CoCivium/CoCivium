#!/usr/bin/env python3
"""CoSpeedo NeedleTrails R1 source acceptance (read-only, no network).
Guard exact archival counts, accessible fallback, truthful evidence labels.
"""
from html.parser import HTMLParser
from pathlib import Path
import json
import re

ROOT=Path(__file__).resolve().parents[1]
PAGE=ROOT/"examples/cospeedo/needle-trails-r1.html"
CENSUS=ROOT/"docs/Metrics/COSPEEDO_RECEIPT_CENSUS_R0_20261027.json"
RUNS=("42740435685","42738989013")

class View(HTMLParser):
    def __init__(self):
        super().__init__()
        self.rows=[]
        self.polylines=[]
        self.svgs=[]
        self.scripts=[]
        self.tables=0
        self.dialogs=0
        self.external_assets=[]
    def handle_starttag(self, tag, attrs):
        d=dict(attrs)
        if tag=="tr" and "data-date" in d: self.rows.append(d)
        if tag=="polyline": self.polylines.append(d)
        if tag=="svg": self.svgs.append(d)
        if tag=="script": self.scripts.append(d)
        if tag=="table": self.tables+=1
        if tag=="dialog": self.dialogs+=1
        if tag in {"iframe","audio","video","form"}: self.external_assets.append(tag)
        if tag in {"script","img","source"} and d.get("src"): self.external_assets.append(d["src"])

def main():
    html=PAGE.read_text(encoding="utf-8")
    archive=json.loads(CENSUS.read_text(encoding="utf-8"))
    p=View()
    p.feed(html)
    day_keys=[d for d in sorted(archive["days"]) if "2026-10-23"<=d<="2026-10-26"]
    assert len(day_keys)==4, "Archive four-day known interval changed"
    assert len(p.rows)==4 and len({x["data-date"] for x in p.rows})==4, "Duplicate / missing days"
    for row in p.rows:
        day=archive["days"][row["data-date"]]
        for key,label in (("PASS","data-pass"),("HELD","data-held"),("FAIL","data-fail")):
            assert int(row[label])==day["status_counts"][key], (row["data-date"],key)
        assert sum(int(row[x]) for x in ("data-pass","data-held","data-fail"))==day["ledger_rows"],row["data-date"]
    assert sum(archive["days"][d]["ledger_rows"] for d in day_keys)==145
    for day in ("2026-10-20","2026-10-21","2026-10-22"):
        assert archive["days"][day]["coverage_state"]=="NO_LEDGER_ROWS__UNKNOWN_NE_ZERO"
    assert "October 20–22 have no recorded rows" in html, "Missing unknown coverage"
    assert len(p.polylines)==3, "Missing real pass/hold/fail visual traces"
    for idx,key in enumerate(("PASS","HELD","FAIL")):
        expected=" ".join(f"{85+140*i},{190-(archive['days'][d]['status_counts'][key]/40)*130:.1f}" for i,d in enumerate(day_keys))
        supplied=p.polylines[idx]["points"]
        actual=[(float(pair.split(",")[0]),float(pair.split(",")[1])) for pair in supplied.split()]
        target=[(float(pair.split(",")[0]),float(pair.split(",")[1])) for pair in expected.split()]
        assert all(abs(a-b)<0.01 for (ax,ay),(bx,by) in zip(actual,target) for a,b in ((ax,bx),(ay,by))), (key,supplied,expected)
    assert len(p.svgs)==1 and p.svgs[0].get("role")=="img"
    assert p.tables==1
    assert p.dialogs==0 and p.external_assets==[], "No surprise popups or external embeds"
    assert "It does not auto-refresh" in html
    assert "not live telemetry" in html
    assert "Human improvement unknown" in html
    assert "24 hours" in html
    assert "recovery" in html.lower()
    assert "Unknown" in html
    assert all(run in html for run in RUNS), "Missing real CI links"
    assert "No background recording" in html
    assert "No comparable baseline" in html
    assert "verified useful closur" not in html.lower(), "No inferred closure claim"
    assert "setInterval" not in html and "window.open(" not in html
    print("PASS_COSPEEDO_NEEDLE_TRAILS_R1_COUNTS_ACCESSIBILITY_NONCLAIMS")

if __name__=="__main__":
    main()
