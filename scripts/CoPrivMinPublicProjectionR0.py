#!/usr/bin/env python3
"""CoPrivMin R0 public-safe *candidate* projector.

Reads a locally prepared review envelope. Writes ONLY caller-authored public
candidate fields. NEVER auto-declassifies, summarizes private content, commits,
publishes, emails, opens a browser, or asserts release authority. Automation
of this projector is not authorization to publish its outputs.

Not a replacement for human security/privacy/IP review. Generic scanners are
incomplete; trust only an authorized exact-payload review.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SCHEMA="CoCivium.CoPrivMin.CandidateProjection.R0"
OUTPUT_SCHEMA="CoCivium.CoPrivMin.PublicReviewCandidate.R0"
PUBLIC={"PUBLIC_EXACT","PUBLIC_SUMMARY","PUBLIC_SYNTHETIC"}
HELD={"WITHHELD_EXACT","EXISTENCE_HELD","UNRESOLVED"}
ALLOWED={"question","context","claim","status","limitation","next_test","source_public_url"}
REQUIRED={"question","status","limitation","next_test"}
MAX_BYTES=60000
MAX_FIELD=1600
SAFE_ID=re.compile(r"^[a-z][a-z0-9_]{2,47}$")
# These are only mechanical hints; absence never certifies public safety.
WARN=re.compile(
    r"(?i)(?:-----BEGIN [A-Z ]*PRIVATE KEY-----|"
    r"gh[pousr]_[A-Za-z0-9_]{20,}|"
    r"AKIA[0-9A-Z]{16}|"
    r"password\s*[:=]|bearer\s+[A-Za-z0-9._~+/-]{10,}|"
    r"https?://github\.com/CoCivium/CoSteward/(?:pull|issues|blob)/|"
    r"(?:[A-Za-z]:\\|\\\\)[^\s]{3,}|"
    r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,})"
)
def need(v,code):
    if not v:raise ValueError(code)
def canonical(v):
    return (json.dumps(v,sort_keys=True,ensure_ascii=False,
                       separators=(",",":"))+"\n").encode("utf-8")
def digest(v):return hashlib.sha256(v).hexdigest()
def validate(envelope):
    need(isinstance(envelope,dict) and envelope.get("schema")==SCHEMA,
         "INPUT_SCHEMA")
    need(set(envelope)=={"schema","object_alias","object_presence_sensitive",
                        "intent","fields"},"INPUT_KEYS")
    need(isinstance(envelope["object_alias"],str) and
         SAFE_ID.fullmatch(envelope["object_alias"]),"PUBLIC_ALIAS_INVALID")
    need(envelope["object_presence_sensitive"] is False,
         "OBJECT_EXISTENCE_PROTECTED")
    need(envelope["intent"]=="BUILD_REVIEWABLE_CANDIDATE_ONLY",
         "AUTO_RELEASE_NOT_AUTHORIZED")
    fields=envelope["fields"]
    need(isinstance(fields,list) and 1<=len(fields)<=40,
         "FIELD_BOUNDS")
    output={}
    used=set()
    for item in fields:
        need(isinstance(item,dict) and set(item)=={"field","decision","text"},
             "FIELD_SHAPE")
        field=item["field"]
        decision=item["decision"]
        need(isinstance(field,str) and SAFE_ID.fullmatch(field),
             "FIELD_ID")
        need(field not in used,"DUPLICATE_FIELD")
        used.add(field)
        need(decision in PUBLIC|HELD,"UNKNOWN_DECISION")
        # All protected field IDs/content remain completely absent from output.
        if decision in HELD:continue
        need(field in ALLOWED,"UNQUALIFIED_PUBLIC_FIELD")
        value=item["text"]
        need(isinstance(value,str) and 12<=len(value)<=MAX_FIELD,
             "PUBLIC_FIELD_TEXT_BOUNDS")
        need(not WARN.search(value),"POTENTIAL_SENSITIVE_TEXT")
        need("\x00" not in value and "\r" not in value and
             not any(ord(c)<32 and c not in "\t\n" for c in value),
             "CONTROL_CHARACTERS")
        if field=="source_public_url":
            need(value.startswith("https://") and
                 not any(c in value for c in ("@", " ", "\n", "\t")),
                 "PUBLIC_SOURCE_URL")
        output[field]=value
    need(REQUIRED<=set(output),"MISSING_PUBLIC_MINIMUM")
    result={
      "schema":OUTPUT_SCHEMA,"object_alias":envelope["object_alias"],
      "state":"PRIVATE_REVIEW_NEEDED_NO_RELEASE_AUTHORITY",
      "public_candidate_fields":output,
      "source_private_ids":"NOT_INCLUDED",
      "source_private_hashes":"NOT_INCLUDED",
      "protected_field_count":"NOT_DISCLOSED",
      "current_website_or_app_state":"NOT_ESTABLISHED",
      "public_commit_or_receiver_ack":"NOT_OBSERVED",
      "effects_executed":0,
      "nonclaims":["PUBLIC_CANDIDATE_NE_PUBLISHED",
                   "MECHANICAL_FILTER_NE_SECURITY_CLEARANCE",
                   "OMITTED_NE_NONEXISTENT",
                   "UNKNOWN_NE_ABSENT",
                   "SOURCE_HASH_NE_PRIVACY_PROOF"]
    }
    raw=canonical(result)
    # Receipt concerns only already sanitized public bytes, never input bytes.
    receipt={"schema":"CoCivium.CoPrivMin.CandidateReceipt.R0",
             "candidate_sha256":digest(raw),
             "effects":0,"release_authorized":False,
             "source_input_hash_disclosed":False,
             "reviewer_readback":"NOT_OBSERVED"}
    return result,receipt

def write(envelope,path):
    value,receipt=validate(envelope)
    target=Path(path)
    need(not target.exists(),"NO_OVERWRITE")
    need(target.parent.is_dir(),"PARENT_MISSING")
    raw=canonical(value)
    target.write_bytes(raw)
    need(digest(target.read_bytes())==receipt["candidate_sha256"],
         "LOCAL_READBACK_FAILED")
    return receipt

def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--review-envelope",type=Path,required=True)
    parser.add_argument("--candidate-out",type=Path,required=True)
    a=parser.parse_args()
    src=a.review_envelope
    need(src.is_file() and not src.is_symlink() and
         src.stat().st_size<=MAX_BYTES,"INPUT_FILE_INVALID")
    content=src.read_bytes()
    need(len(content)<=MAX_BYTES,"INPUT_TOO_LARGE")
    data=json.loads(content.decode("utf-8"))
    r=write(data,a.candidate_out)
    print(json.dumps(r,sort_keys=True))
if __name__=="__main__":
    try:main()
    except (ValueError,OSError,UnicodeError,json.JSONDecodeError) as e:
        # Do not echo input payloads or exception values with private paths.
        print("HELD_COPRIVMIN_REVIEW_INPUT_OR_RELEASE_GATE",file=sys.stderr)
        sys.exit(2)
