#!/usr/bin/env python3
"""CoVisualFinder -> CoLens *rendered markup* R0.

Generate a standalone, script-free Text/Map/Orb preview from the already
qualified public source-METADATA bridge. This does not reproduce images,
fetch URLs, execute user actions, authenticate any receiver or install UI.
"""
import argparse
import hashlib
import html
import re
from pathlib import Path
from urllib.parse import urlsplit

import lens_bridge as bridge

HERE = Path(__file__).resolve().parent
VIEWS = ("Text", "Map", "Orb")
ALLOWED_PAGES = {
    "visual-external-commons-linkgraph-r1":
        "https://commons.wikimedia.org/wiki/File:Commons_Interwiki_links_with_wikidata_3.svg",
    "visual-external-nasa-orbit-r1":
        "https://science.nasa.gov/photojournal/gas-planet-orbits/",
    "visual-external-w3c-rdf-r1":
        "https://www.w3.org/TR/rdf12-primer/",
    "visual-external-creativecommons-linked-r1":
        "https://opensource.creativecommons.org/blog/entries/linked-commons-gsoc-wrap-up/",
}
DIGEST = re.compile(r"^[a-f0-9]{64}$")


def safe_text(value):
    if not isinstance(value, str) or len(value) > 1300 or "\x00" in value:
        raise ValueError("UNSAFE_TEXT")
    return html.escape(value, quote=True)


def safe_url(source_id, url):
    if ALLOWED_PAGES.get(source_id) != url:
        raise ValueError("UNQUALIFIED_SOURCE_LINK")
    parsed = urlsplit(url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("UNSAFE_SOURCE_URL")
    return safe_text(url)


def check_projection(data):
    bridge.assert_safe(data)
    if data.get("sample_size") != 4 or data.get("actual_receivers") != 0:
        raise ValueError("NOT_FOUR_UNACCEPTED_PUBLIC_SOURCES")
    if data.get("actual_effects") != 0 or data.get("source_image_bytes_copied") != 0:
        raise ValueError("NO_EXTERNAL_EFFECT_OR_MEDIA_COPIES")
    if set(data.get("views", ())) != set(VIEWS):
        raise ValueError("VIEW_CONTRACT_CHANGED")
    for key in ("source_registry_digest", "colens_contract_digest"):
        if not DIGEST.fullmatch(data.get(key, "")):
            raise ValueError("UNQUALIFIED_CONTRACT_DIGEST")
    seen = set()
    for record in data["objects"]:
        sid = record["id"]
        if sid in seen or sid not in ALLOWED_PAGES:
            raise ValueError("UNKNOWN_OR_DUPLICATE_SOURCE")
        seen.add(sid)
        safe_url(sid, record["source_page"])
        if not DIGEST.fullmatch(record["source_digest"]):
            raise ValueError("UNQUALIFIED_SOURCE_DIGEST")
        if record["receiver_state"] != "HELD_NOT_RENDERED_OR_READ_BY_INDEPENDENT_RECEIVER":
            raise ValueError("RECEIVER_STATE_MUST_REMAIN_HELD")
        if set(record["views"]) != set(VIEWS) or len(record["semantic_loss"]) != 3:
            raise ValueError("MISSING_VIEW_OR_LOSS_RECORD")
        for name, view in record["views"].items():
            if view["status"] != "ADVISORY_SOURCE_TO_VIEW_SPEC_NOT_RENDERED":
                raise ValueError("UPSTREAM_SPEC_STATUS_CHANGED")
            if (view["source_id"] != sid or view["work_id"] != record["work_id"]
                or view["source_digest"] != record["source_digest"]
                or view["authority"] != "NONE" or view["receiver_ack"] is not None):
                raise ValueError("RENDER_INPUT_CROSS_VIEW_DRIFT")
            if name == "Map":
                if len(view["nodes"]) != 3 or len(view["edges"]) != 2:
                    raise ValueError("MAP_SCOPE_CHANGED")
            if name == "Orb" and len(view["satellites"]) > 3:
                raise ValueError("UNBOUNDED_ORB_ROLES")
    if seen != set(ALLOWED_PAGES):
        raise ValueError("MISSING_PUBLIC_SOURCE")
    return True


def provenance(record, view):
    sid = safe_text(record["id"])
    work = safe_text(record["work_id"])
    digest = safe_text(record["source_digest"])
    rights = safe_text(record["rights_state"])
    epistemic = safe_text(record["epistemic_class"])
    name = safe_text(view)
    return (
        f'<div class="provenance" data-view="{name}" data-source="{sid}" '
        f'data-work="{work}" data-digest="{digest}" data-rights="{rights}" '
        f'data-epistemic="{epistemic}">'
        f'<span>Work: <code>{work}</code></span>'
        f'<span>Source SHA-256: <code>{digest}</code></span>'
        f'<span>Rights: {rights}</span><span>Epistemic class: {epistemic}</span>'
        '</div>'
    )


def map_svg(view, sid):
    label = safe_text(sid + " conceptual Map preview")
    inverse = safe_text(view["nodes"][2]["label"])
    return f"""<figure class="mapfigure"><svg viewBox="0 0 690 175" role="img"
      aria-label="{label}; proposed, noncausal arrows from source to motif to a challenge">
      <title>Map: source pointer, design motif and inverse challenge</title>
      <desc>Two dashed links mean a proposal to consider an idea and test it, not a causal claim.</desc>
      <line x1="144" y1="75" x2="312" y2="75" class="link"/>
      <line x1="380" y1="75" x2="547" y2="75" class="link"/>
      <circle cx="115" cy="75" r="35" class="dot"/>
      <circle cx="346" cy="75" r="35" class="focus"/>
      <circle cx="580" cy="75" r="35" class="dot"/>
      <text x="115" y="80" class="node-label">Source</text>
      <text x="346" y="80" class="node-label">Motif</text>
      <text x="580" y="80" class="node-label">Question</text>
      <text x="229" y="55" class="edge-label">may inspire</text>
      <text x="465" y="55" class="edge-label">is challenged</text>
      <text x="346" y="143" class="label-small">PROPOSED EDGES ONLY</text>
    </svg><figcaption>Question: {inverse}. No reciprocal, causal or evidence edge is inferred.</figcaption></figure>"""


def orb_svg(view, sid):
    label = safe_text(sid + " Orb preview")
    satellites = view["satellites"]
    positions = ((145, 72), (545, 72), (345, 211))
    lines, circles = [], []
    for item, (x, y) in zip(satellites, positions):
        role = safe_text(item["role"])
        if item["status"] != "PROPOSED_INTERNAL_VIEW_ONLY":
            raise ValueError("ROLE_STATUS_NOT_PROPOSED")
        lines.append(f'<line x1="345" y1="125" x2="{x}" y2="{y}" class="link"/>')
        circles.append(f'<circle cx="{x}" cy="{y}" r="47" class="dot"/>'
                       f'<text x="{x}" y="{y+5}" class="node-label">{role}</text>')
    return f"""<figure class="orbfigure"><svg viewBox="0 0 690 280" role="img"
       aria-label="{label}; one proposed central design motif and {len(satellites)} illustrative roles">
       <title>Orb: one design motif and proposed internal role satellites</title>
       <desc>The circles are purely organizational; they do not depict physical orbits, live agents or astronomy.</desc>
       {''.join(lines)}
       <circle cx="345" cy="125" r="73" class="focus"/>
       <text x="345" y="121" class="node-label">DESIGN</text>
       <text x="345" y="142" class="node-label">MOTIF</text>
       {''.join(circles)}
       </svg><figcaption>Focus: {safe_text(view["focus"]["label"])}. '
       Roles are proposed labels, not executing workers.</figcaption></figure>"""


def render_document(data):
    check_projection(data)
    parts = []
    for i, record in enumerate(data["objects"], 1):
        sid, views = record["id"], record["views"]
        source = safe_url(sid, record["source_page"])
        tid = safe_text(sid)
        text_view, map_view, orb_view = (views[key] for key in VIEWS)
        parts.append(f'''<article class="source" id="{tid}">
            <h2>Source {i}: {safe_text(map_view["nodes"][0]["label"])}</h2>
            <p class="description">Motif: {safe_text(text_view["motif"])}</p>
            <p><a href="{source}" rel="noopener noreferrer">Inspect the original source page</a>
            (a deliberate link, not an embedded image).</p>
            <details {"open" if i == 1 else ""}><summary>Inspect three views of this one source</summary>
                <div class="views">
                  <section class="pane" aria-label="Accessible text interpretation">
                    <h3>Text | meaning and uncertainty</h3>
                    <p>{safe_text(text_view["accessible_explanation"])}</p>
                    <p><strong>Inverse question:</strong> {safe_text(text_view["inverse_question"])}</p>
                    {provenance(record, "Text")}
                  </section>
                  <section class="pane" aria-label="Conceptual Map projection">
                    <h3>Map | proposed relations</h3>
                    {map_svg(map_view, sid)}
                    <p><strong>Motif label:</strong> {safe_text(map_view["nodes"][1]["label"])}</p>
                    {provenance(record, "Map")}
                  </section>
                  <section class="pane" aria-label="Conceptual Orb projection">
                    <h3>Orb | proposed focus and roles</h3>
                    {orb_svg(orb_view, sid)}
                    <p><strong>Text alternative:</strong> {safe_text(orb_view["plain_text_fallback"])}</p>
                    {provenance(record, "Orb")}
                  </section>
                </div>
                <p class="loss"><strong>Known projection loss:</strong>
                    {safe_text("; ".join(record["semantic_loss"]))}.</p>
                <p class="next"><strong>Next independent test:</strong>
                    {safe_text(record["next_test"])}</p>
            </details>
        </article>''')
    body = "\n".join(parts)
    reg = safe_text(data["source_registry_digest"])
    lens = safe_text(data["colens_contract_digest"])
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="referrer" content="no-referrer">
<title>CoLens | Four source-linked visual inspirations</title>
<style>
:root {{color-scheme:dark; background:#071a17; color:#e9f8f2; font-family:system-ui,-apple-system,sans-serif;}}
* {{box-sizing:border-box;}} body {{margin:0 auto; padding:1rem; max-width:1050px; line-height:1.53;}}
h1,h2,h3 {{line-height:1.25;}} h1 {{font-size:clamp(1.5rem,4vw,2.35rem);}}
header,.source {{padding:1.1rem; margin:1.1rem 0; border:1px solid #548777; border-radius:14px; background:#102d27;}}
.eyebrow,.loss,.next,.description {{color:#c4e7d9;}} .eyebrow {{font-weight:700;}}
a {{color:#a7e9f5;}} a:focus-visible,summary:focus-visible {{outline:3px solid #edce73; outline-offset:4px;}}
details {{border-top:1px solid #528071; padding-top:1rem;}}
summary {{cursor:pointer; font-weight:700; min-height:44px; padding:8px 2px;}}
.views {{display:grid; gap:1rem; grid-template-columns:repeat(auto-fit,minmax(min(100%,300px),1fr));}}
.pane {{background:#193e36; border:1px solid #6e9f8b; border-radius:12px; padding:.85rem; min-width:0;}}
.provenance {{display:grid; gap:.32rem; font-size:.77rem; color:#c9eadf; border-top:1px solid #567c73; padding-top:.6rem; overflow-wrap:anywhere;}}
svg {{width:100%; height:auto; display:block; background:#102f2a; border-radius:8px;}}
.link {{stroke:#b4dfc6;stroke-width:2;stroke-dasharray:7 5;fill:none;}}
.dot {{stroke:#b6e8d1;stroke-width:2;fill:#24574a;}}
.focus {{stroke:#f3cd7a;stroke-width:3;fill:#446446;}}
.node-label {{fill:#fffdf3;font-size:17px;text-anchor:middle;font-weight:700;}}
.edge-label,.label-small {{fill:#d0f1e2;font-size:13px;text-anchor:middle;}}
figcaption {{font-size:.9rem; color:#d6eadd;}}
figure {{margin:.5rem 0;}}
code {{font-size:.9em;word-break:break-all;}}
.notice {{border-left:4px solid #f3cd7a;padding:.7rem;background:#32402e;}}
@media (prefers-reduced-motion:reduce) {{* {{animation:none!important;transition:none!important;}}}}
</style>
</head>
<body>
<header>
<p class="eyebrow">◎ CoVisualFinder → CoLens / CoMap / CoOrb</p>
<h1>Four inspirations, one source each, three honest views</h1>
<p class="notice">Rendered from public source-page <strong>metadata only</strong>. No original images, videos,
private artwork, accounts, network reads, controllers, permissions or active agents are embedded.
Relations are proposed design analogies, never scientific measurements or confirmed causes.</p>
<p>Open a source, compare Text, Map and Orb, and inspect the same work ID and source digest.
No automatic refresh; this is a pinned static snapshot. All views have visible text alternatives.</p>
</header>
<main>{body}</main>
<footer><p><strong>Provenance:</strong> Source registry SHA-256 <code>{reg}</code><br>
CoLens view-contract SHA-256 <code>{lens}</code>.</p>
<p>State: <strong>STATIC_MARKUP_GENERATED__INDEPENDENT_BROWSER_AND_READER_ACCEPTANCE_HELD</strong>.
This document establishes HTML/SVG source construction only, not end-user comprehension,
source artwork rights, live native CoOrbWare, receiver ACK or deployment.</p>
<p>CoCivium public-safe research draft. Accessibility is designed but not independently certified.</p></footer>
</body></html>
"""


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="Generate/validate offline, do not write")
    parser.add_argument("--output", type=Path, help="Explicit destination for static HTML")
    args = parser.parse_args()
    if args.check and args.output:
        parser.error("Choose --check or --output, not both")
    content = render_document(bridge.build())
    fingerprint = hashlib.sha256(content.encode("utf-8")).hexdigest()
    if args.output:
        args.output.write_text(content, encoding="utf-8")
    print(f"PASS: 4 public source records, 12 static Text/Map/Orb panels, "
          f"no original images or network calls; HTML bytes={len(content.encode('utf-8'))}; "
          f"SHA-256={fingerprint}; independent reader=HELD")


if __name__ == "__main__":
    main()
