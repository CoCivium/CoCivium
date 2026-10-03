#!/usr/bin/env python3
import hashlib
import json
import subprocess
from pathlib import Path

P = Path("fixtures/theory/co_virtual_command_surface_r0.json")

def fail(code):
    raise SystemExit(code)

def git_blob(path):
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], text=True).strip()

def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()

def decide(c):
    if c["irreversible_or_sensitive"] and not c["effect_authorized"]:
        return "HOLD_MISSING_AUTHORITY"

    if c.get("compiled_from_relational_deed"):
        return "COMPILE_COMMAND_AS_PROJECTION_THEN_EXECUTE_VIRTUALLY"

    if c.get("long_running"):
        if c["machine_route_available"]:
            return "BACKGROUND_WORKER_PLUS_VISIBLE_HEARTBEAT"

    if c.get("accessibility_text_projection"):
        if c["machine_route_available"]:
            return "VIRTUAL_COMMAND_WITH_ACCESSIBLE_TEXT_PROJECTION"

    if c["machine_route_available"]:
        if c["human_requested_terminal"] and c["debug_or_recovery"]:
            return "MATERIALIZE_TRANSIENT_OPERATOR_CLI"
        if c["human_requested_terminal"]:
            return "PROJECT_READABLE_TECHNICAL_TRACE_TERMINAL_OPTIONAL"
        return "VIRTUAL_COMMAND_RELATION_NO_TERMINAL"

    if c.get("alternate_receiver_available"):
        return "ROUTE_TO_ALTERNATE_RECEIVER_NO_TERMINAL"

    if c["debug_or_recovery"]:
        return "MATERIALIZE_TRANSIENT_BREAK_GLASS_CLI"

    return "HOLD_NO_RECEIVER"

def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    src = d["source_bindings"]
    checks = [
        ("cogenex_doc_path", "cogenex_doc_blob_sha"),
        ("coboogie_doc_path", "coboogie_doc_blob_sha"),
    ]
    for path_key, sha_key in checks:
        if git_blob(src[path_key]) != src[sha_key]:
            fail("FAIL_SOURCE_BIND:" + src[path_key])

    defaults = d["defaults"]
    if defaults["human_facing_cli"] is not False:
        fail("FAIL_HUMAN_CLI_DEFAULT")
    if defaults["machine_internal_command_surface"] != "VIRTUAL_RELATIONAL":
        fail("FAIL_INTERNAL_COMMAND_SURFACE")
    if defaults["break_glass_default"] is not False:
        fail("FAIL_BREAK_GLASS_DEFAULT")
    if defaults["user_relay_required"] is not False:
        fail("FAIL_USER_RELAY_DEFAULT")

    required_fields = {
        "intent","receiver","authority","input_bindings","effect_class",
        "reversibility","idempotence","preview","receipt_contract","retry_policy",
        "timeout","rollback","output_projection","visibility","retirement_condition"
    }
    if not required_fields.issubset(set(d["command_relation_fields"])):
        fail("FAIL_COMMAND_RELATION_FIELDS")

    observed = []
    for c in d["scenarios"]:
        got = decide(c)
        if got != c["expected"]:
            fail(f"FAIL:{c['id']}:got={got}:expected={c['expected']}")
        observed.append({"id": c["id"], "decision": got})

    rails = set(d["rails"])
    required_rails = {
        "CLI_NE_INTENT","CLI_NE_AUTHORITY","COMMAND_NE_EFFECT",
        "VIRTUAL_NE_NONPHYSICAL","HIDDEN_CLI_NE_HIDDEN_EFFECT",
        "CLI_NE_PRIMARY_UX","BREAK_GLASS_NE_DEFAULT","USER_NE_COMMAND_RELAY",
        "BACKGROUND_WORKER_NE_UNOBSERVABLE_WORKER","ROUTED_NE_EXECUTED"
    }
    if not required_rails.issubset(rails):
        fail("FAIL_REQUIRED_RAILS")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    receipt = {
        "STATE": "PASS_CO_VIRTUAL_COMMAND_SURFACE_R0",
        "checked_out_head_sha": head,
        "scenario_count": len(observed),
        "primary_human_surface": defaults["primary_human_surface"],
        "human_facing_cli_default": defaults["human_facing_cli"],
        "machine_internal_command_surface": defaults["machine_internal_command_surface"],
        "break_glass_cli_available": defaults["break_glass_cli_available"],
        "break_glass_default": defaults["break_glass_default"],
        "user_relay_required": defaults["user_relay_required"],
        "runtime_effect": false,
        "fixture_semantic_sha256": canonical_sha(d),
        "observed": observed
    }
    print(json.dumps(receipt, separators=(",", ":")))

if __name__ == "__main__":
    main()
