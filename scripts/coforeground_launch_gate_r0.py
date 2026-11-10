#!/usr/bin/env python3
"""CoForeground R0 source/launch admission gate. Read-only. Never launches anything.

Scopes: declared runners and their source files, not installed X2 processes.
A PASS_FOR_SOURCE_POLICY is *not* an OS enforcement or UX acceptance claim.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

SCHEMA="CoAll.CoRunner.ForegroundAdmission.R0"
AUTO={"SCHEDULED","EVENT","RECOVERY","AUTOSTART"}
MANUAL={"USER_GESTURE","MANUAL_OPERATOR"}
VISIBILITY={"HEADLESS","TRAY","SURFACE","OPERATOR_TERMINAL","DEBUG_TEMPORARY"}
RUNTIMES={"pwsh","powershell","python","pythonw","native"}
GUI_TOKENS=(
    r"(?i)\bOut-GridView\b",
    r"(?i)\bShowDialog\s*\(",
    r"(?i)\bMessageBox(?:\]|\s*::)",
    r"(?i)\bWindows\.Forms\.Form\b",
    r"(?i)\bSystem\.Windows\.Window\b",
    r"(?i)\bStart-Process\b[^\r\n]*\bWindowStyle\s+(?:Normal|Maximized)\b",
)
EXPECTED_FIELDS={"module_id","source","runtime","visibility","allowed_triggers",
                 "qualification","launch_args","max_live_instances","restart_policy",
                 "foreground_ownership","user_exit"}

def source_file(repo_root, relative):
    if not isinstance(relative,str) or not relative.startswith("scripts/"):
        raise ValueError("HELD_SOURCE_OUTSIDE_SCRIPTS")
    if "\\" in relative or "//" in relative or ".." in Path(relative).parts:
        raise ValueError("HELD_SOURCE_PATH_UNSAFE")
    root=Path(repo_root).resolve()
    path=root/relative
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root):
        raise ValueError("HELD_SOURCE_ABSENT_OR_LINKED")
    return path

def audit(entry, source):
    holds=[]
    if not isinstance(entry,dict):
        return ["HELD_INVALID_ENTRY"]
    if EXPECTED_FIELDS.difference(entry):
        holds.append("HELD_MISSING_CONTRACT_FIELDS")
        return holds
    if not isinstance(entry["module_id"],str) or not re.fullmatch(r"[A-Za-z][A-Za-z0-9_.-]{2,80}",entry["module_id"]):
        holds.append("HELD_INVALID_MODULE_ID")
    visibility=entry["visibility"]
    runtime=entry["runtime"]
    triggers=entry["allowed_triggers"]
    argv=entry["launch_args"]
    if visibility not in VISIBILITY or runtime not in RUNTIMES:
        holds.append("HELD_UNKNOWN_VISIBILITY_OR_RUNTIME")
    if not isinstance(triggers,list) or not triggers or any(t not in AUTO|MANUAL for t in triggers) or len(set(triggers))!=len(triggers):
        holds.append("HELD_INVALID_TRIGGER_SCOPE")
        triggers=[]
    if not isinstance(argv,list) or not all(isinstance(v,str) and v for v in argv):
        holds.append("HELD_INVALID_LAUNCH_ARGUMENTS")
        argv=[]
    if entry["qualification"] not in {"CANDIDATE_SOURCE_ONLY","QUALIFIED_FOR_HOST_TRIAL"}:
        holds.append("HELD_INVALID_QUALIFICATION")
    if entry["max_live_instances"] != 1:
        holds.append("HELD_NOT_SINGLE_ELECTED_RUNNER")
    if entry["restart_policy"] not in {"NONE","SUPERVISED_BACKOFF"}:
        holds.append("HELD_RESTART_POLICY")
    if entry["foreground_ownership"] not in {"USER_INVOCATION_ONLY","NONE_NEVER_STEAL_FOCUS"}:
        holds.append("HELD_FOREGROUND_OWNER_UNVERIFIED")
    if not isinstance(entry["user_exit"],str) or not entry["user_exit"].strip():
        holds.append("HELD_NO_USER_EXIT")
    if any(t in AUTO for t in triggers):
        if visibility not in {"HEADLESS","TRAY"}:
            holds.append("HELD_AUTOMATED_FOREGROUND_SURFACE")
        if entry["qualification"]!="QUALIFIED_FOR_HOST_TRIAL":
            holds.append("HELD_AUTOSTART_OF_CANDIDATE")
        if entry["foreground_ownership"]!="NONE_NEVER_STEAL_FOCUS":
            holds.append("HELD_AUTORUN_FOCUS_POLICY")
        if runtime in {"pwsh","powershell"}:
            lower=[v.lower() for v in argv]
            if not {"-noprofile","-noninteractive","-windowstyle","hidden"}.issubset(lower):
                holds.append("HELD_POWERSHELL_BACKGROUND_CONSOLE_RISK")
            if "-noexit" in lower or "-command" in lower or "-encodedcommand" in lower:
                holds.append("HELD_DYNAMIC_OR_PERSISTENT_CONSOLE")
            if any(re.search(p,source) for p in GUI_TOKENS):
                holds.append("HELD_HEADLESS_GUI_ESCAPE_CANDIDATE")
        if runtime=="python" and visibility=="HEADLESS":
            holds.append("HELD_PYTHON_CONSOLE_BACKGROUND_RISK")
    if visibility in {"SURFACE","OPERATOR_TERMINAL","DEBUG_TEMPORARY"}:
        if any(t in AUTO for t in triggers) or not set(triggers).issubset(MANUAL):
            holds.append("HELD_VISIBLE_NOT_EXPLICITLY_USER_INITIATED")
    if visibility=="SURFACE" and "USER_GESTURE" not in triggers:
        holds.append("HELD_SURFACE_WITHOUT_USER_INTENT")
    if runtime in {"pwsh","powershell"} and visibility=="SURFACE":
        if "-Mode" not in argv or "UI" not in argv:
            holds.append("HELD_UI_MODE_NOT_EXPLICIT")
        # This guard is intentionally specific to CoThumb-style Mode entrypoints.
        if "ValidateSet('HOLD','UI','Worker','SelfTest')" not in source:
            holds.append("HELD_UI_SCRIPT_NO_HOLD_DEFAULT")
        if not re.search(r"\[string\]\$Mode\s*=\s*'HOLD'",source):
            holds.append("HELD_UI_SCRIPT_DEFAULTS_VISIBLE")
        pos_guard=source.find("HELD_EXPLICIT_MODE_REQUIRED")
        pos_side_effect=source.find("[IO.Directory]::CreateDirectory")
        if pos_guard<0 or (pos_side_effect>=0 and pos_guard>pos_side_effect):
            holds.append("HELD_MODE_GUARD_AFTER_EFFECT")
    return sorted(set(holds))

def inspect_manifest(repo_root, manifest):
    if not isinstance(manifest,dict) or manifest.get("schema")!=SCHEMA:
        return {"state":"HOLD","holds":["HELD_SCHEMA"],"entries":[]}
    entries=manifest.get("entries")
    if not isinstance(entries,list) or not entries:
        return {"state":"HOLD","holds":["HELD_EMPTY_REGISTRY"],"entries":[]}
    records=[]
    seen=set()
    for e in entries:
        ident=e.get("module_id","UNKNOWN") if isinstance(e,dict) else "INVALID"
        holds=[]
        if ident in seen: holds.append("HELD_DUPLICATE_MODULE_ID")
        seen.add(ident)
        try:
            source=source_file(repo_root,e.get("source")).read_text(encoding="utf-8")
            sha256=hashlib.sha256(source.encode("utf-8")).hexdigest()
            holds+=audit(e,source)
        except (OSError,UnicodeError,ValueError,TypeError,AttributeError) as error:
            sha256=None
            holds.append(str(error) if str(error).startswith("HELD_") else "HELD_SOURCE_UNAVAILABLE")
        records.append({"module_id":ident,"sha256":sha256,
                        "source_policy":"HOLD" if holds else "PASS_FOR_SOURCE_POLICY",
                        "holds":sorted(set(holds)),
                        "host_runtime_proof":"UNKNOWN","foreground_focus_proof":"UNKNOWN"})
    return {"state":"HOLD" if any(v["holds"] for v in records) else "PASS_FOR_SOURCE_POLICY",
            "schema":SCHEMA,"entries":records,
            "runtime_effect":"NONE","window_or_process_launches":0,
            "nonclaims":["STATIC_POLICY_NE_OS_ENFORCEMENT","NO_X2_WINDOW_FOCUS_OBSERVATION",
                         "NO_HOST_RUNTIME_PROOF","CI_PASS_NE_PRODUCT_ADOPTION"]}

def main():
    ap=argparse.ArgumentParser(description="Read-only CoForeground admission audit; never starts processes")
    ap.add_argument("--repo-root",type=Path,default=Path(__file__).resolve().parents[1])
    ap.add_argument("--manifest",type=Path,required=True)
    args=ap.parse_args()
    try:
        data=json.loads(args.manifest.read_text(encoding="utf-8"))
        result=inspect_manifest(args.repo_root,data)
    except (OSError,ValueError):
        result={"state":"HOLD","holds":["HELD_INVALID_MANIFEST"]}
    print(json.dumps(result,sort_keys=True))
    if result["state"]!="PASS_FOR_SOURCE_POLICY":
        raise SystemExit(2)

if __name__=="__main__":
    main()
