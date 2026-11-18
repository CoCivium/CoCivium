#!/usr/bin/env python3
"""Public read-only CoPre source/mirror probe. No writes, login, or effects.

A 200 response or matching bytes is evidence of publication only. This
is not proof of site ownership, independence, receiver uptake, or CoEx.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import urllib.error
import urllib.request
from pathlib import Path

PINNED_COMMIT = "63b41ead8797e5a781699f32bcbc77b78bdbd7af"
SOURCE_URL = f"https://raw.githubusercontent.com/CoCivium/CoCivium/{PINNED_COMMIT}/CoPre.md"
TARGETS = (
    ("github_dedicated_repo", "https://github.com/CoCivium/CoPreGeneric"),
    ("human_site", "https://CoCivium.org/CoPre"),
    ("stead_site", "https://InSeed.com/Stead"),
)
MAX_BYTES = 1_000_000

def read_public(url: str, *, timeout: float = 8.0) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "CoCivium-Public-Readback-R0/1.0", "Accept": "text/plain, text/html, application/json"})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            data = response.read(MAX_BYTES + 1)
            if len(data) > MAX_BYTES:
                return {"state": "HELD_TOO_LARGE", "http_status": response.status, "sha256": None}
            return {"state": "FETCHED_UNQUALIFIED", "http_status": response.status,
                    "sha256": hashlib.sha256(data).hexdigest(), "byte_count": len(data),
                    "final_url": response.geturl()}
    except urllib.error.HTTPError as ex:
        return {"state":"HELD_HTTP_ERROR","http_status":ex.code,"sha256":None}
    except (urllib.error.URLError, TimeoutError, OSError) as ex:
        return {"state":"HELD_TRANSPORT","reason_class":type(ex).__name__,"sha256":None}

def classify(source: dict, targets: list[dict]) -> dict:
    if source.get("state") != "FETCHED_UNQUALIFIED" or source.get("http_status") != 200:
        qualified_source = False
    else:
        qualified_source = True
    out=[]
    for target in targets:
        x=dict(target)
        # NEVER call a live HTML route identical to the Markdown source only because
        # it returned 200. Such a byte comparison would be meaningless.
        x["exact_source_equivalence"] = (
            "MATCHED_BYTES" if qualified_source and x.get("http_status") == 200
            and x.get("sha256") == source.get("sha256")
            else "UNPROVEN"
        )
        x["owner_control"] = "UNPROVEN"
        x["independent_receiver_ack"] = False
        x["independent_cold_restore"] = False
        out.append(x)
    return {
        "schema":"CoAll.CoPreGeneric.PublicReadback.R0",
        "source":{"url":SOURCE_URL, **source, "source_revision":PINNED_COMMIT},
        "targets":out,
        "all_three_identical_verified":False if not qualified_source else all(t["exact_source_equivalence"]=="MATCHED_BYTES" for t in out),
        "source_is_read_not_executed":True,
        "cross_provider_sync":False,
        "receiver_pickup":False,
        "nonclaims":["PUBLIC_FETCH_NE_PUBLICATION_AUTHORITY","HTML_200_NE_SOURCE_PARITY",
                     "MATCHED_SHA_NE_INDEPENDENT_HOST","READBACK_NE_DELIVERY_ACK",
                     "RUNNER_NE_OFF_PROVIDER_RECOVERY","THREE_ROUTES_NE_THREE_MIRRORS"]
    }

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=None)
    args=parser.parse_args()
    source=read_public(SOURCE_URL)
    targets=[{"id":name,"requested_url":url,**read_public(url)} for name,url in TARGETS]
    result=classify(source,targets)
    rendered=json.dumps(result, indent=2, sort_keys=True)+"\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered,end="")
    # A probe that cannot fetch a target records HELD, never claims PASS or
    # treats public-domain availability as a required deployment assertion.

if __name__=="__main__":
    main()
