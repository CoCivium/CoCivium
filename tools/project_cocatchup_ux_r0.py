#!/usr/bin/env python3
import argparse
import hashlib
import html
import json
import os
import subprocess
from pathlib import Path


def fail(code):
    raise SystemExit(code)


def sha256(raw):
    return hashlib.sha256(raw).hexdigest().upper()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--output-json", required=True)
    ap.add_argument("--output-html", required=True)
    args = ap.parse_args()

    src = Path(args.input)
    raw = src.read_bytes()
    d = json.loads(raw.decode("utf-8"))

    if d.get("schema") != "CoCatchUp.DeltaSurfaceReceipt.v0.1":
        fail("FAIL_SOURCE_SCHEMA")
    if not str(d.get("STATE", "")).startswith("PASS_COCATCHUP_DELTA_SURFACE_R0"):
        fail("FAIL_SOURCE_STATE")
    if d.get("external_effects") != 0:
        fail("FAIL_SOURCE_EXTERNAL_EFFECTS")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    if d.get("checked_out_head_sha") != head:
        fail("FAIL_SOURCE_HEAD_NE_RECEIVER_HEAD")

    artifact_id = os.environ.get("SOURCE_ARTIFACT_ID")
    artifact_digest = os.environ.get("SOURCE_ARTIFACT_DIGEST")
    artifact_url = os.environ.get("SOURCE_ARTIFACT_URL")
    if not artifact_id or not artifact_digest:
        fail("FAIL_SOURCE_ARTIFACT_BINDING_MISSING")

    delta = int(d.get("material_delta_count", 0))
    hold = int(d.get("current_head_hold_count", 0))
    wait = int(d.get("current_head_wait_count", 0))

    if hold:
        headline = f"CoAll frontier: {hold} current-head hold signal(s)"
        status = "ATTENTION"
    elif delta:
        headline = f"CoAll frontier: {delta} material delta(s)"
        status = "DELTA"
    elif wait:
        headline = f"CoAll frontier: {wait} proof wait(s)"
        status = "WAIT"
    else:
        headline = "CoAll frontier: current and quiet"
        status = "QUIET"

    rows = []
    for r in d.get("rows", []):
        rows.append({
            "pr_number": r.get("pr_number"),
            "title": r.get("title"),
            "role": r.get("role"),
            "baseline_relation": r.get("baseline_relation"),
            "current_head_assessment": r.get("current_head_assessment"),
            "special_disposition": r.get("special_disposition"),
        })

    projection = {
        "schema": "CoCatchUp.UXProjection.v0.1-candidate",
        "STATE": "PASS_COCATCHUP_UX_RECEIVER_R0F",
        "checked_out_head_sha": head,
        "status": status,
        "CoHereNow": headline,
        "Meaning": d.get("ux_summary", {}).get(
            "Meaning",
            "Live GitHub currentness is projected without treating historical failures as current failures.",
        ),
        "NextSafeAction": d.get("next_safe_action"),
        "UXState": "UX_ACCEPTANCE_UNPROVEN",
        "source": {
            "receipt_sha256": sha256(raw),
            "receipt_state": d.get("STATE"),
            "artifact_id": artifact_id,
            "artifact_digest": artifact_digest,
            "artifact_url": artifact_url,
            "source_receiver_identity": d.get("receiver_identity"),
            "lifecycle_state_before_receiver": "LANDED",
            "receiver_identity": "github-actions:cocatchup-ux-projection-r0",
            "receiver_readproof": "PASS_EXACT_OBJECT_READBACK",
            "lifecycle_state_after_receiver": "PICKED_UP",
        },
        "evidence_summary": {
            "current_main_head_sha": d.get("current_main_head_sha"),
            "watched_pr_count": d.get("watched_pr_count"),
            "material_delta_count": delta,
            "current_head_hold_count": hold,
            "current_head_wait_count": wait,
            "rows": rows,
        },
        "nonclaims": [
            "UX_PROJECTION_ARTIFACT_NE_COBAR_INTEGRATION",
            "PICKED_UP_NE_INTEGRATED",
            "GREEN_WORKFLOW_NE_UX_ACCEPTANCE",
            "DELTA_PROJECTION_NE_CONTROL_PLANE",
            "GITHUB_ONLY_NE_FULL_COALL_CURRENTNESS",
            "VALIDATION_IS_NOT_ACCEPTANCE",
            "NO_INTEGRATION_COEX_CANON_RUNTIME_OR_PUBLIC_INFERENCE",
        ],
    }

    out_json = Path(args.output_json)
    out_html = Path(args.output_html)
    if out_json.exists() or out_html.exists():
        fail("FAIL_CLOSED_NO_CLOBBER")
    out_json.parent.mkdir(parents=True, exist_ok=True)
    out_html.parent.mkdir(parents=True, exist_ok=True)

    out_json.write_text(
        json.dumps(projection, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )

    evidence_rows = "\n".join(
        "<tr>"
        f"<td>#{html.escape(str(r['pr_number']))}</td>"
        f"<td>{html.escape(str(r['title']))}</td>"
        f"<td>{html.escape(str(r['current_head_assessment']))}</td>"
        f"<td>{html.escape(str(r['baseline_relation']))}</td>"
        "</tr>"
        for r in rows
    )

    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CoCatchUp R0F</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:980px;margin:3rem auto;padding:0 1rem;line-height:1.45}}
main{{border:1px solid #bbb;border-radius:14px;padding:1.4rem}}
h1{{font-size:1.35rem;margin-top:0}}
.status{{font-weight:700}}
small,code{{overflow-wrap:anywhere}}
table{{border-collapse:collapse;width:100%;font-size:.9rem}}
td,th{{border-top:1px solid #ccc;padding:.55rem;text-align:left;vertical-align:top}}
details{{margin-top:1rem}}
</style>
</head>
<body>
<main>
<h1>{html.escape(headline)}</h1>
<p class="status">Status: {html.escape(status)}</p>
<p>{html.escape(str(projection["Meaning"]))}</p>
<p><strong>Next safe action:</strong> <code>{html.escape(str(projection["NextSafeAction"]))}</code></p>
<p><small>UX state: UX_ACCEPTANCE_UNPROVEN. This is a read-only projection artifact, not CoBar integration or runtime authority.</small></p>
<details>
<summary>Evidence</summary>
<p>Current main: <code>{html.escape(str(d.get("current_main_head_sha")))}</code></p>
<p>Source receipt SHA-256: <code>{html.escape(sha256(raw))}</code></p>
<p>Source artifact ID: <code>{html.escape(str(artifact_id))}</code></p>
<p>Receiver readproof: <code>PASS_EXACT_OBJECT_READBACK</code></p>
<table>
<thead><tr><th>PR</th><th>Surface</th><th>Current-head assessment</th><th>Baseline relation</th></tr></thead>
<tbody>{evidence_rows}</tbody>
</table>
</details>
</main>
</body>
</html>
"""
    out_html.write_text(doc, encoding="utf-8")

    print(json.dumps({
        "STATE": projection["STATE"],
        "checked_out_head_sha": head,
        "status": status,
        "CoHereNow": headline,
        "NextSafeAction": projection["NextSafeAction"],
        "source_receipt_sha256": projection["source"]["receipt_sha256"],
        "source_artifact_id": artifact_id,
        "receiver_readproof": "PASS_EXACT_OBJECT_READBACK",
        "source_lifecycle_transition": "LANDED_TO_PICKED_UP",
        "UXState": "UX_ACCEPTANCE_UNPROVEN",
    }, separators=(",", ":")))


if __name__ == "__main__":
    main()
