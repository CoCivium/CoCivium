#!/usr/bin/env python3
"""CoForeground R0: classify a *supplied* read-only X2 launcher snapshot.

No device access, task manipulation, new console, scheduled timer, process kill,
task enable/disable or network. Input requires an existing authorized observer;
a synthetic fixture never becomes host evidence.
"""
from __future__ import annotations
import argparse
import datetime as dt
import json
import re
from pathlib import Path

SCHEMA="CoAll.CoForeground.LauncherObservation.R0"
BOOL_KEYS=("automated","windowstyle_hidden","noninteractive","ui_mode")
ALLOWED_KINDS={"POWERSHELL","NATIVE","CMD","UNKNOWN"}
ALLOWED_STATES={"Ready","Running","Disabled","Unknown"}
KNOWN_FUNCTIONS={
  "CoCiviumExeDevMuleResidentTick1Min":"LOCAL_DEV_MULE_HEALTH",
  "CoPing_CopyBlock_InboxProcessor_1min_V05":"LOCAL_COPYBLOCK_INBOX",
  "CoCiviumExeProductShellWatchdog5Min":"LEGACY_PRODUCT_SHELL_WATCH",
  "CoEyesStructuralReview10Min":"LEGACY_COEYES_REVIEW",
}
NONCLAIMS=[
  "SOURCE_INVENTORY_NE_LIVE_FOREGROUND_ATTRIBUTION",
  "WINDOWSTYLE_HIDDEN_NE_GUI_IMPOSSIBLE",
  "ENABLED_TASK_NE_ACTUAL_TASK_FIRED",
  "DISABLED_TASK_NE_PERMANENTLY_DISABLED",
  "X2_OFFLINE_NE_X2_POWERED_OFF",
  "SYNTHETIC_INPUT_NE_RECEIVER_READPROOF",
  "NO_MUTATION_OR_AUTOMATIC_TERMINATION",
  "CLOUD_CI_NE_LOCAL_BOOTDEPENDENCY",
]

class Held(Exception):
    pass

def strict_snapshot(snapshot):
    if not isinstance(snapshot,dict) or snapshot.get("schema")!=SCHEMA:
        raise Held("HELD_INVALID_SCHEMA")
    if snapshot.get("scope") not in {"SYNTHETIC_CI_ONLY","AUTHORIZED_HOST_OBSERVER"}:
        raise Held("HELD_UNKNOWN_OBSERVATION_SCOPE")
    if snapshot.get("coverage") != "BOUNDED_MATCHING_LAUNCHERS_ONLY":
        raise Held("HELD_FALSE_COMPLETE_COVERAGE")
    if not isinstance(snapshot.get("observed_at_utc"),str) or not re.fullmatch(
            r"\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z",snapshot["observed_at_utc"]):
        raise Held("HELD_UNKNOWN_OBSERVATION_TIME")
    if not isinstance(snapshot.get("tasks"),list) or len(snapshot["tasks"])>250:
        raise Held("HELD_INVALID_TASK_COLLECTION")
    seen=set()
    for t in snapshot["tasks"]:
        if not isinstance(t,dict) or set(t)!={
            "task_name","state","kind","automated","windowstyle_hidden","noninteractive",
            "ui_mode","action_sha256"
        }:
            raise Held("HELD_UNDECLARED_TASK_FIELDS")
        if not isinstance(t["task_name"],str) or not (1<=len(t["task_name"])<=180):
            raise Held("HELD_INVALID_TASK_ID")
        if t["task_name"].casefold() in seen:
            raise Held("HELD_DUPLICATE_TASK_ID")
        seen.add(t["task_name"].casefold())
        if t["state"] not in ALLOWED_STATES or t["kind"] not in ALLOWED_KINDS:
            raise Held("HELD_UNKNOWN_STATE_OR_KIND")
        if any(type(t[x]) is not bool for x in BOOL_KEYS):
            raise Held("HELD_INVALID_BOOLEAN_FLAGS")
        if not isinstance(t["action_sha256"],str) or not re.fullmatch(r"[0-9a-f]{64}",t["action_sha256"]):
            raise Held("HELD_UNVERIFIABLE_ACTION_FINGERPRINT")
    return snapshot

def inspect(snapshot, now=None):
    strict_snapshot(snapshot)
    when=dt.datetime.strptime(snapshot["observed_at_utc"],"%Y-%m-%dT%H:%M:%SZ").replace(tzinfo=dt.timezone.utc)
    now=now or dt.datetime.now(dt.timezone.utc)
    if now.tzinfo is None:
        raise Held("HELD_NAIVE_NOW")
    age=(now-when).total_seconds()
    if age < -120:
        raise Held("HELD_FUTURE_OBSERVATION")
    fresh=age<=600
    findings=[]
    for t in snapshot["tasks"]:
        name=t["task_name"]
        if t["state"]=="Disabled":
            risk="DISABLED_AS_OBSERVED_NOT_CURRENTNESS"
        elif t["state"]=="Unknown" or t["kind"]=="UNKNOWN":
            risk="HOLD_UNRESOLVED_LAUNCHER"
        elif t["automated"] and t["ui_mode"]:
            risk="P0_AUTOMATED_VISIBLE_UI_RISK"
        elif t["automated"] and t["kind"]=="POWERSHELL" and (
            not t["windowstyle_hidden"] or not t["noninteractive"]):
            risk="P1_AUTOMATED_PS7_CONSOLE_RISK"
        elif t["automated"] and t["kind"]=="POWERSHELL":
            risk="HEADLESS_FLAGS_PRESENT_FOCUS_UNVERIFIED"
        else:
            risk="NO_RISK_IN_DECLARED_FLAGS_NOT_REAL_HOST_PASS"
        findings.append({
            "task_name":name,
            "risk":risk,
            "function_to_preserve":KNOWN_FUNCTIONS.get(name,"UNKNOWN_PRESERVE_UNTIL_REVIEWED"),
            "action_fingerprint":t["action_sha256"],
            "next_effect":"NONE_READ_ONLY_CLASSIFICATION",
            "requires_host_actor_identity":True,
        })
    return {
        "schema":"CoAll.CoForeground.LauncherTriageReceipt.R0",
        "state":"SYNTHETIC_POLICY_CHECK_ONLY" if snapshot["scope"]=="SYNTHETIC_CI_ONLY"
                 else "BOUNDED_HOST_OBSERVATION_NE_CAUSAL_PROOF",
        "host_snapshot_fresh":fresh,
        "observation_age_seconds":round(age),
        "count":len(findings),
        "findings":findings,
        "local_execution_effects":0,
        "task_settings_changed":False,
        "processes_terminated":0,
        "restart_triggered":False,
        "popup_cause":"UNIDENTIFIED",
        "complete_inventory":False,
        "elected_next_proof":"AUTHORIZED_X2_FRESH_READ_ONLY_LAUNCHER_AND_FOCUS_CORRELATION",
        "nonclaims":NONCLAIMS,
    }

def main():
    p=argparse.ArgumentParser(description="Classify preexisting launcher snapshot, never mutates host")
    p.add_argument("--snapshot",type=Path,required=True)
    args=p.parse_args()
    try:
        if args.snapshot.is_symlink() or not args.snapshot.is_file() or args.snapshot.stat().st_size>128*1024:
            raise Held("HELD_INPUT_MISSING_LINKED_OR_OVERSIZED")
        data=json.loads(args.snapshot.read_text(encoding="utf-8"))
        result=inspect(data)
        # Printing task identifiers to the console is deliberately avoided.
        print(json.dumps({k:v for k,v in result.items() if k not in {"findings"}}))
    except (Held,OSError,UnicodeError,ValueError,TypeError) as e:
        msg=str(e) if isinstance(e,Held) else "HELD_INPUT_UNREADABLE"
        print(json.dumps({"state":msg,"task_settings_changed":False,"processes_terminated":0}))
        raise SystemExit(2)

if __name__=="__main__":
    main()
