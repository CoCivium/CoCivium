#!/usr/bin/env python3
"""CoLens legacy-highlight bridge R0: one pinned JSON registry, three passive views.

No device, network, provider, clipboard, browser-tab, scheduler or external
effect. The original legacy JSON remains the only authority for its own fields.
"""
import argparse
import hashlib
import html
import json
import math
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SOURCE = ROOT / "ai" / "highlight-assets.json"
OUT = HERE / "preview.html"
EXPECTED_GIT_BLOB = "a6cf0422a2fbf82852de3619a47ea8b8ec3c45de"
EXPECTED_SCHEMA = "CoAll.HighlightRegistry.v0.1-candidate"
EXPECTED_STATE = "PUBLIC_CANDIDATE_HIGHLIGHTS__NOT_CANON_NOT_RELEASE_READINESS"
STATUS = {"CANDIDATE_HIGHLIGHT", "PUBLIC_HIGHLIGHT"}
MAX_SOURCE = 65536
MAX_ASSETS = 32
ALLOWED_ROOT = {"schema", "state", "updated_utc", "assets", "rails"}
ALLOWED_ASSET = {"id", "name", "status", "readiness"}
ID = re.compile(r"^[A-Za-z][A-Za-z0-9_]{1,63}$")
LABEL = re.compile(r"^[A-Z][A-Z0-9_]{2,119}$")
UTC = re.compile(r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")
LOSSES = (
    "The flat registry has no verified per-asset evidence or source-time receipt.",
    "The flat registry has no measured health, runtime or device liveness.",
    "Listed-with is not a scientific, causal, organizational or permission relation.",
    "No imported media bytes, third-party rights, reader acceptance or recipient ACK.",
)


def _object_no_duplicate_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def decode_registry(raw, expected_blob=EXPECTED_GIT_BLOB):
    if not isinstance(raw, bytes) or len(raw) > MAX_SOURCE or not raw:
        raise ValueError("SOURCE_BYTES_OUT_OF_BOUNDS")
    blob = hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()
    if expected_blob is not None and blob != expected_blob:
        raise ValueError("SOURCE_GIT_BLOB_CHANGED__REVIEW_REQUIRED")
    try:
        obj = json.loads(raw.decode("utf-8"), object_pairs_hook=_object_no_duplicate_keys,
                         parse_constant=lambda _: (_ for _ in ()).throw(ValueError("NONFINITE_NUMBER")))
    except UnicodeDecodeError as e:
        raise ValueError("NOT_UTF8") from e
    if not isinstance(obj, dict) or set(obj) != ALLOWED_ROOT:
        raise ValueError("UNKNOWN_REGISTRY_ENVELOPE")
    if obj["schema"] != EXPECTED_SCHEMA or obj["state"] != EXPECTED_STATE:
        raise ValueError("REGISTRY_TYPE_OR_RELEASE_STATE_CHANGED")
    if not isinstance(obj["updated_utc"], str) or not UTC.fullmatch(obj["updated_utc"]):
        raise ValueError("INVALID_DECLARED_SOURCE_TIME")
    rows = obj["assets"]
    if not isinstance(rows, list) or not 1 <= len(rows) <= MAX_ASSETS:
        raise ValueError("ASSET_COUNT_INVALID")
    if not isinstance(obj["rails"], list) or obj["rails"] != [
        "HIGHLIGHT_NE_CANON", "PUBLIC_NE_VALIDATED", "VISIBLE_NE_RELEASE_READY"
    ]:
        raise ValueError("NONCLAIM_RAIL_DRIFT")
    seen = set()
    for asset in rows:
        if not isinstance(asset, dict) or set(asset) != ALLOWED_ASSET:
            raise ValueError("UNKNOWN_ASSET_FIELDS")
        key = asset["id"]
        if not isinstance(key, str) or not ID.fullmatch(key) or key in seen:
            raise ValueError("INVALID_OR_DUPLICATE_ASSET_ID")
        seen.add(key)
        if not isinstance(asset["name"], str) or not 1 <= len(asset["name"]) <= 160:
            raise ValueError("INVALID_ASSET_NAME")
        if any(ord(c) < 32 for c in asset["name"]):
            raise ValueError("CONTROL_CHAR_IN_ASSET_NAME")
        if asset["status"] not in STATUS:
            raise ValueError("UNSUPPORTED_HIGHLIGHT_STATUS")
        if not isinstance(asset["readiness"], str) or not LABEL.fullmatch(asset["readiness"]):
            raise ValueError("INVALID_READINESS_TOKEN")
    return obj, hashlib.sha256(raw).hexdigest(), blob


def model_from_registry(doc, source_sha, source_blob):
    rows = [
        {"id": x["id"], "name": x["name"], "status": x["status"],
         "readiness": x["readiness"], "epistemic": "DECLARED_REGISTRY_METADATA_ONLY"}
        for x in doc["assets"]
    ]
    return {
        "source_id": EXPECTED_SCHEMA,
        "source_path": "ai/highlight-assets.json",
        "source_sha256": source_sha,
        "source_git_blob": source_blob,
        "declared_source_time": doc["updated_utc"],
        "rendered_freshness": "NOT_VERIFIED_CURRENT",
        "source_state": doc["state"],
        "asset_count": len(rows),
        "status_counts": {s: sum(x["status"] == s for x in rows) for s in sorted(STATUS)},
        "assets": rows,
        "edges": [{"from": "REGISTRY", "to": x["id"], "type": "LISTS_ENTRY",
                   "evidence_class": "DECLARED_REGISTRY_ONLY"} for x in rows],
        "translation_losses": list(LOSSES),
        "authority": "READ_ONLY_NONE",
        "effects": {"network": 0, "input_capture": 0, "send": 0,
                    "device_change": 0, "provider_calls": 0, "source_mutation": 0},
        "receiver_ack": None,
        "native_fallback": "OPEN_ORIGINAL_LEGACY_JSON",
    }


def render_html(m):
    esc = html.escape
    def h(s):
        return esc(str(s), quote=True)

    sha = h(m["source_sha256"])
    rows = m["assets"]
    count = len(rows)
    graph = ['<svg viewBox="0 0 760 560" role="img" aria-labelledby="map-title map-desc">',
             '<title id="map-title">Registry-to-highlight map</title>',
             '<desc id="map-desc">The registry lists exactly ' + str(count) +
             ' entries. Every line is only a lists-entry relationship; no causal links are inferred.</desc>',
             '<circle cx="380" cy="280" r="52" fill="#236577" stroke="#b2f7e2" stroke-width="3"/>',
             '<text x="380" y="284" text-anchor="middle" fill="white" font-size="16">Registry</text>']
    for i, row in enumerate(rows):
        angle = (2 * math.pi * i / count) - math.pi / 2
        x = round(380 + 275 * math.cos(angle))
        y = round(280 + 208 * math.sin(angle))
        graph.append('<line x1="380" y1="280" x2="' + str(x) + '" y2="' + str(y) +
                     '" stroke="#7caac0" stroke-width="1.5"/>')
        graph.append('<g><title>' + h(row["name"]) + ": " + h(row["readiness"]) + '</title>'
                     '<circle cx="' + str(x) + '" cy="' + str(y) +
                     '" r="21" fill="#385786" stroke="#acd9fb" stroke-width="2"/>'
                     '<text x="' + str(x) + '" y="' + str(y + 4) +
                     '" fill="white" font-size="10" text-anchor="middle">' + str(i+1) + '</text></g>')
    graph.append("</svg>")
    readable_items = "".join(
        '<li><strong>' + h(x["id"]) + '</strong>: ' + h(x["name"]) +
        ' <small>(' + h(x["status"]) + ' / ' + h(x["readiness"]) + ')</small></li>'
        for x in rows
    )
    table_rows = "".join(
        '<tr><th scope="row">' + h(x["id"]) + '</th><td>' + h(x["name"]) +
        '</td><td>' + h(x["status"]) + '</td><td>' + h(x["readiness"]) + '</td></tr>'
        for x in rows
    )
    counts = " · ".join(h(key) + ": " + str(m["status_counts"][key])
                        for key in sorted(STATUS))
    losses = "".join("<li>" + h(value) + "</li>" for value in m["translation_losses"])
    # Source identity and loss accounting are repeated verbatim in all three projections.
    views = []
    views.append('<section id="map" data-source-sha256="' + sha + '"><h2>CoMap · Registry membership</h2>'
                 + "".join(graph) + '<p>Only source-declared registry membership is drawn.</p>'
                 '<ol aria-label="Map node text alternatives">' + readable_items + '</ol></section>')
    views.append('<section id="orb" data-source-sha256="' + sha + '"><h2>CoOrb · Attention summary, not live health</h2>'
                 '<div class="orb" role="img" aria-label="' + str(count) +
                 ' declared highlights; no live health or receiver currentness verified"><strong>' + str(count) +
                 '</strong><span>declared entries</span></div><p>' + counts + '</p>'
                 '<p>All status and readiness labels are inherited verbatim; none are independently validated.</p>'
                 '<ol aria-label="Orb membership text alternative">' + readable_items + '</ol></section>')
    views.append('<section id="text" data-source-sha256="' + sha + '"><h2>Text · Exact legacy fields</h2>'
                 '<div class="tablewrap"><table><caption>Registry metadata, not product certification</caption>'
                 '<thead><tr><th scope="col">ID</th><th scope="col">Name</th><th scope="col">Status</th>'
                 '<th scope="col">Readiness (declared)</th></tr></thead><tbody>' + table_rows +
                 '</tbody></table></div></section>')
    return ('<!doctype html>\n<html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; '
            'style-src \'unsafe-inline\'; img-src data:; connect-src \'none\'; form-action \'none\'; '
            'object-src \'none\'; base-uri \'none\'">'
            '<title>CoLens · Legacy highlight registry compatibility R0</title><style>'
            ':root{color-scheme:dark;font:16px/1.55 system-ui,Segoe UI,sans-serif;'
            'background:#0d1825;color:#eef7fa}body{max-width:940px;margin:auto;padding:24px}'
            'section{border:1px solid #5c7a8b;border-radius:12px;padding:18px;margin:22px 0}'
            'h1,h2{line-height:1.2}h2{color:#b6e7e3}small,.muted{color:#c4d3de}'
            'svg{max-width:100%;height:auto;display:block}ol{columns:2;gap:32px}'
            'li{break-inside:avoid;margin:0 0 7px}.orb{width:190px;height:190px;'
            'border:9px solid #80c0d2;border-radius:50%;display:grid;place-content:center;'
            'text-align:center;background:#183b52}.orb strong{font-size:3.5rem;line-height:1.1}'
            '.orb span{font-size:.84rem}code,li,td,th,small{overflow-wrap:anywhere;word-break:break-word}'
            '.tablewrap{max-width:100%;overflow-x:auto}'
            'table{border-collapse:collapse;width:100%}td,th{border:1px solid #668295;'
            'padding:8px;text-align:left}a{color:#b4f2e2}'
            '@media(max-width:630px){body{padding:12px}ol{columns:1}section{padding:12px}}'
            '@media(prefers-reduced-motion:reduce){*{animation:none!important;transition:none!important}}'
            '</style></head><body><header><h1>One legacy JSON source → three honest views</h1>'
            '<p>No installation, permission change, network request, model worker or clipboard access.</p>'
            '<p class="muted">Exact source: <code>' + h(m["source_path"]) +
            '</code> · SHA-256 <code>' + sha + '</code></p>'
            '<p class="muted">Source-declared update: ' + h(m["declared_source_time"]) +
            ' · Currentness: ' + h(m["rendered_freshness"]) + '</p></header>'
            + "".join(views)
            + '<section><h2>Information lost or not present in the legacy format</h2><ul>' + losses +
            '</ul><p><strong>Fallback:</strong> Open the original unmodified '
            '<code>ai/highlight-assets.json</code>. Delete this generated page to remove the overlay.</p>'
            '<p class="muted">No projection modifies the source. No visual, status label or registry '
            'entry establishes an external effect or independent receiver acknowledgment.</p></section>'
            '</body></html>\n')


def main():
    parser = argparse.ArgumentParser(description="Read-only CoLens legacy highlight adapter")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--build", action="store_true", help="Write only the local preview.html")
    mode.add_argument("--check", action="store_true", help="Require exact preview parity, no writes")
    args = parser.parse_args()
    before = SOURCE.read_bytes()
    doc, digest, blob = decode_registry(before)
    projection = model_from_registry(doc, digest, blob)
    output = render_html(projection).encode("utf-8")
    if SOURCE.read_bytes() != before:
        raise SystemExit("HELD_SOURCE_MUTATED_DURING_READ")
    if args.build:
        OUT.write_bytes(output)
        state = "PASS_LOCAL_PREVIEW_BUILT__NOT_DEPLOYED"
    else:
        if not OUT.is_file() or OUT.read_bytes() != output:
            raise SystemExit("FAIL_PREVIEW_DRIFT__REBUILD_REQUIRED")
        state = "PASS_PREVIEW_EXACT_SOURCE_PARITY"
    print(json.dumps({"status": state, "assets": projection["asset_count"],
                      "source_sha256": digest, "output_sha256": hashlib.sha256(output).hexdigest(),
                      "effects": projection["effects"], "receiver_ack": None},
                     sort_keys=True))


if __name__ == "__main__":
    main()
