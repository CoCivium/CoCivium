#!/usr/bin/env python3
"""Fail-closed draft CoIndexRedir manifest validator; does not claim deployment."""
import json
from pathlib import Path
from urllib.parse import urlparse
import sys
ROOT=Path(__file__).resolve().parents[1]
p=ROOT/"ai"/"coindexredir-route-register-r0.json"
obj=json.loads(p.read_text(encoding="utf-8"))
errors=[]
if obj.get("schema")!="CoIndexRedir.RouteRegister.r0": errors.append("schema mismatch")
if obj.get("status")!="DRAFT_NOT_DEPLOYED": errors.append("must not claim deployment")
if obj.get("published_at") is not None: errors.append("published_at must be null before public readproof")
seen=set()
for route in obj.get("routes",[]):
    slug=route.get("slug","")
    if not slug.startswith("/") or slug in seen: errors.append("bad or duplicate slug: "+slug)
    seen.add(slug)
    target=route.get("target","")
    if target.startswith("https://"):
        if urlparse(target).hostname!="github.com": errors.append("target origin not allowed: "+target)
    elif target:
        fp=ROOT/target
        if target.startswith("/") or ".." in Path(target).parts or not fp.is_file(): errors.append("missing target: "+target)
    else: errors.append("missing target for "+slug)
    fb=route.get("fallback","")
    if not fb.startswith("https://github.com/CoCivium/CoCivium"):errors.append("unsafe fallback: "+slug)
    if route.get("state")=="DRAFT_BRANCH" and slug=="/start" and obj.get("status")!="DRAFT_NOT_DEPLOYED":errors.append("unreviewed live start")
if not all(k in obj.get("nonclaims",[]) for k in ["NO_LIVE_REDIRECT","NO_PUBLIC_DOMAIN_CONTROL"]):errors.append("missing release nonclaims")
html=(ROOT/"docs"/"Launch"/"coindexredir_r0"/"index.html").read_text(encoding="utf-8")
for invariant in ['<svg','<title id="artTitle">','aria-live="polite"','prefers-reduced-motion','<script>','No autoplay audio']:
    if invariant not in html: errors.append("missing accessible UI invariant: "+invariant)
print(json.dumps({"state":"FAIL" if errors else "PASS","errors":errors,"scope":"source and structural checks only; not live browser, HTTPS or redirect proof"},indent=2))
sys.exit(bool(errors))
