#!/usr/bin/env python3
"""CoVisualFinder -> CoLens three-view source identity adapter.

No network, private images, pixel copying, providers, accounts, effects or renderer
installation. Constructs metadata-only Text / Map / Orb *view specifications*,
not already displayed/accepted independent renders.
"""
import argparse
import hashlib
import json
from pathlib import Path

import finder

HERE = Path(__file__).resolve().parent
COLENS = HERE.parent / "colensmedia" / "manifest.json"
VIEW_NAMES = ("Text", "Map", "Orb")
DONOR_KEYS = frozenset({
    "id", "title", "source_page", "origin", "source_type",
    "rights_state", "stated_license", "rights_evidence_page", "credit",
    "motif", "accessible_twin", "inverse_challenge", "next_test",
    "epistemic_class", "consumers", "selected_reuse", "noendorsement"
})
BANNED = {"CAUSES", "PROVES", "MEASURES", "SEND", "EXECUTES", "GRANTS_AUTHORITY"}


def load_colens(path=COLENS):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def qualify_colens(lens):
    if not isinstance(lens, dict):
        raise ValueError("COLENS_NOT_OBJECT")
    if lens.get("schema") != "CoAll.CoLens.LivingMediaTwin.R0":
        raise ValueError("COLENS_UNKNOWN_SCHEMA")
    if set(lens.get("views", ())) != set(VIEW_NAMES) or len(lens.get("views", ())) != 3:
        raise ValueError("COLENS_THREE_VIEWS_REQUIRED")
    if lens.get("authority") != "NONE":
        raise ValueError("COLENS_EFFECT_AUTHORITY")
    if lens.get("privacy", {}).get("external_network") is not False:
        raise ValueError("COLENS_NETWORK_NOT_BOUNDED")
    if lens.get("privacy", {}).get("raw_private_source") != "NOT_EMBEDDED":
        raise ValueError("COLENS_RAW_PRIVATE")
    return True


def qualify_sources(registry):
    if not isinstance(registry, dict):
        raise ValueError("REGISTRY_NOT_OBJECT")
    rows = finder.validate(registry)
    if len(rows) != 4:
        raise ValueError("FOUR_SOURCE_FIXED_SAMPLE_REQUIRED")
    for row in rows:
        if set(row) != DONOR_KEYS:
            raise ValueError("UNDECLARED_DONOR_METADATA")
        if row["selected_reuse"] != "MOTIF_ONLY_LINK_BACK_TO_SOURCE":
            raise ValueError("MEDIA_REUSE_UNQUALIFIED")
        if len(row["accessible_twin"].strip()) < 20:
            raise ValueError("ACCESSIBLE_DESCRIPTION_REQUIRED")
        if "?" not in row["inverse_challenge"]:
            raise ValueError("INVERSE_QUESTION_REQUIRED")
    return rows


def digest(obj):
    return hashlib.sha256(finder.canon(obj).encode("utf-8")).hexdigest()


def build(registry=None, colens=None):
    registry = finder.load() if registry is None else registry
    colens = load_colens() if colens is None else colens
    rows = qualify_sources(registry)
    qualify_colens(colens)
    objects = []
    for row in rows:
        sid = row["id"]
        work = "coal.visualprior." + sid
        identity = digest(row)
        common = {
            "work_id": work,
            "source_id": sid,
            "source_digest": identity,
            "source_page": row["source_page"],
            "rights_state": row["rights_state"],
            "epistemic_class": row["epistemic_class"],
            "authority": "NONE",
            "source_media_bytes": "NOT_INCLUDED",
            "receiver_ack": None,
            "status": "ADVISORY_SOURCE_TO_VIEW_SPEC_NOT_RENDERED"
        }
        text = {
            **common, "view": "Text",
            "accessible_explanation": row["accessible_twin"],
            "motif": row["motif"],
            "credit": row["credit"],
            "inverse_question": row["inverse_challenge"]
        }
        map_view = {
            **common, "view": "Map",
            "nodes": [
                {"id": sid + ":source", "kind": "SOURCE_PAGE_POINTER", "label": row["title"]},
                {"id": sid + ":motif", "kind": "DESIGN_MOTIF", "label": row["motif"]},
                {"id": sid + ":challenge", "kind": "INVERSE_QUESTION_NOT_FACT",
                 "label": row["inverse_challenge"]}
            ],
            "edges": [
                {"from": sid + ":source", "to": sid + ":motif",
                 "type": "INSPIRES_CANDIDATE", "status": "PROPOSED"},
                {"from": sid + ":motif", "to": sid + ":challenge",
                 "type": "CHALLENGED_BY_QUESTION", "status": "PROPOSED"}
            ],
            "presentation_note": "Spec only. Do not infer cause, scientific measurement, or rights to reproduce source imagery."
        }
        orb = {
            **common, "view": "Orb",
            "focus": {"id": sid + ":motif", "label": row["motif"]},
            "satellites": [
                {"role": role, "status": "PROPOSED_INTERNAL_VIEW_ONLY"}
                for role in row["consumers"]
            ],
            "plain_text_fallback": row["accessible_twin"],
            "inverse_question": row["inverse_challenge"],
            "presentation_note": "Orb is a candidate projection, not a running worker or scientific orbit."
        }
        objects.append({
            "id": sid,
            "work_id": work,
            "source_digest": identity,
            "source_page": row["source_page"],
            "rights_state": row["rights_state"],
            "epistemic_class": row["epistemic_class"],
            "views": {"Text": text, "Map": map_view, "Orb": orb},
            "semantic_loss": [
                "Original pixels and full source context intentionally absent",
                "No source image copyright or derivative approval inferred",
                "No visual encoding or perceptual comprehension test performed"
            ],
            "next_test": row["next_test"],
            "receiver_state": "HELD_NOT_RENDERED_OR_READ_BY_INDEPENDENT_RECEIVER"
        })
    return {
        "schema": "CoCivium.CoVisual.CoLensSourceToViewBridge.R0",
        "status": "PASS_STRUCTURAL_METADATA_PROJECTION_ONLY",
        "source_registry_digest": digest(registry),
        "colens_contract_digest": digest(colens),
        "upstream_colens_schema": colens["schema"],
        "views": list(VIEW_NAMES),
        "objects": objects,
        "sample_size": len(objects),
        "independent_renderers_qualified": 0,
        "actual_receivers": 0,
        "actual_effects": 0,
        "source_image_bytes_copied": 0,
        "nonclaims": [
            "SOURCE_REFERENCE_NE_MEDIA_COPY",
            "THREE_VIEW_SPECS_NE_THREE_INDEPENDENT_RENDERERS",
            "RICH_VISUAL_METAPHOR_NE_SCIENTIFIC_PROOF",
            "CROSS_VIEW_IDENTITY_NE_HUMAN_COMPREHENSION",
            "SOURCE_FOOTPRINT_NE_UNLIMITED_TOKENS",
            "PASS_STRUCTURAL_NE_DEVICE_OR_RECEIVER_ACCEPTANCE",
            "PROPOSED_ROLES_NE_ACTIVATED_WORKERS"
        ]
    }


def assert_safe(projection):
    if projection["sample_size"] != 4 or projection["actual_effects"] != 0:
        raise ValueError("OUT_OF_SCOPE_PROJECTION")
    for obj in projection["objects"]:
        if set(obj["views"]) != set(VIEW_NAMES):
            raise ValueError("MISSING_VIEW")
        for view_name, view in obj["views"].items():
            if (view["work_id"] != obj["work_id"]
                or view["source_id"] != obj["id"]
                or view["source_digest"] != obj["source_digest"]
                or view["source_page"] != obj["source_page"]
                or view["epistemic_class"] != obj["epistemic_class"]
                or view["rights_state"] != obj["rights_state"]
                or view["authority"] != "NONE"
                or view["source_media_bytes"] != "NOT_INCLUDED"
                or view["receiver_ack"] is not None):
                raise ValueError("CROSS_VIEW_SOURCE_OR_RIGHTS_DRIFT")
            if view_name == "Map":
                ids = {node["id"] for node in view["nodes"]}
                for edge in view["edges"]:
                    if (edge["from"] not in ids or edge["to"] not in ids
                            or edge["status"] != "PROPOSED"
                            or edge["type"] in BANNED):
                        raise ValueError("UNQUALIFIED_GRAPH_EDGE")
            if view_name == "Orb" and len(view["satellites"]) > 3:
                raise ValueError("UNBOUNDED_ORB_SATELLITES")
    return True


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--check", action="store_true",
                   help="Run no-effect structural qualification without emitting source text")
    args = p.parse_args()
    result = build()
    assert_safe(result)
    if args.check:
        print("PASS: 4 public-source motifs x Text/Map/Orb view specs; 0 images; 0 effects; 0 receivers")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
