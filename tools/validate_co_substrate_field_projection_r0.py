#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path

FIELD=Path("docs/Architecture/COSUBSTRATE_FIELD_R0.md")
PROJECTION=Path("fixtures/substrate/co_substrate_field_projection_r0.json")
MIGRATION=Path("fixtures/substrate/co_substrate_migration_r0.json")

def fail(msg):
    raise SystemExit(f"FAIL: {msg}")

def blob(path):
    return subprocess.check_output(["git","hash-object",str(path)], text=True).strip()

def main():
    if not FIELD.exists() or not PROJECTION.exists() or not MIGRATION.exists():
        fail("required input missing")

    p=json.loads(PROJECTION.read_text(encoding="utf-8"))
    m=json.loads(MIGRATION.read_text(encoding="utf-8"))
    src=p["source_field"]

    if blob(FIELD) != src["git_blob_sha"]:
        fail("CoSubstrateField donor blob drift")

    field_text=FIELD.read_text(encoding="utf-8")
    required=set(src["relation_names"])
    for name in required:
        if name not in field_text:
            fail(f"bound field relation missing from donor: {name}")

    migration_ids={c["id"] for c in m["cases"]}
    cases=p.get("profile_cases",[])
    if len(cases)!=4:
        fail("expected four profile projection cases")

    used=set()
    for c in cases:
        if c["migration_fixture_case"] not in migration_ids:
            fail(f"{c['id']}: missing migration fixture binding")
        rels=c.get("field_relations",[])
        if not rels:
            fail(f"{c['id']}: field relations required")
        for r in rels:
            name=r.get("relation")
            if name not in required:
                fail(f"{c['id']}: relation {name!r} is not bound to CoSubstrateField donor")
            if not r.get("subject") or not r.get("object"):
                fail(f"{c['id']}: relation endpoints required")
            used.add(name)

    must_use={"reconstructs_from","preserves_invariant_across","loses_information_to","incompatible_with","requires_adapter","bounded_by"}
    if not must_use.issubset(used):
        fail("projection does not exercise required existing field vocabulary")

    if "FIELD_PROJECTION_NE_NEW_SUBSTRATE_ONTOLOGY" not in p.get("nonclaims",[]):
        fail("missing anti-duplication rail")

    print("PASS: CoSubstrate Independence consumes exact CoSubstrateField R0 vocabulary (4 cases)")

if __name__=="__main__":
    main()
