#!/usr/bin/env python3
"""Compare a minimal WorkID pointer with a full CoUptake synthetic packet.

Pure, bounded, source-safe A/B fixture. No storage/mirror writes, network,
independent receiver trust, real provider session, or effect execution.
"""
import argparse
import copy
import json
from pathlib import Path

import CoPreUptakeBridgeR0 as bridge
import CoStatusOffloadR0 as offload

SCHEMA="CoCivium.CoPreRecoveryAB.R0.v0.1"

def pointer(checkpoint):
    return {
      "schema":"CoCivium.CoPreWorkPointer.R0",
      "work_id":checkpoint["work_id"],
      "source_revision":checkpoint["source_revision"],
      "expected_checkpoint_sha256":checkpoint["checkpoint_sha256"],
    }

def restore_pointer(p, available_bytes, known_revision):
    if not isinstance(p,dict) or set(p)!={"schema","work_id","source_revision","expected_checkpoint_sha256"} or p["schema"]!="CoCivium.CoPreWorkPointer.R0":
        return "HOLD_INVALID_POINTER"
    if available_bytes is None:
        return "HOLD_SOURCE_UNAVAILABLE"
    try:
        cp=json.loads(available_bytes)
    except (ValueError,TypeError):
        return "HOLD_UNREADABLE_SOURCE"
    if offload.check_checkpoint(cp)!="EXACT_STRUCTURAL_READBACK_ONLY":
        return "HOLD_SOURCE_INTEGRITY"
    if cp["work_id"]!=p["work_id"]:
        return "HOLD_WORK_ID_SUBSTITUTION"
    if cp["checkpoint_sha256"]!=p["expected_checkpoint_sha256"]:
        return "HOLD_UNRECOGNIZED_SOURCE"
    if cp["source_revision"]!=p["source_revision"] or known_revision != p["source_revision"]:
        return "HOLD_STALE_SOURCE_REVISION"
    return "LOCAL_POINTER_RESTORE_ONLY"

def full_packet_status(receiver_bytes, packet, pin, expected_work_id, expected_revision, min_generation=1):
    code,receipt=bridge.new_process_receiver(receiver_bytes,packet,pin,min_generation)
    semantic=bridge.semantic_check_after_pin(packet,receipt,expected_work_id,expected_revision)
    if receipt["effect_boundary"]=="LOCAL_PIN_MATCH_ONLY" and code==0:
        return semantic
    return "HELD_OUTER_SOURCE_PIN"

def main(repo):
    cp=offload.make_initial("CoPre.Offshore.20261109","fixture:public-safe","fixture:revision-1")
    cp["sections"]={"next":{"deed":"Verify recovery and preserve STOP"},
                    "recovery":{"pointer":"fixture:source"}}
    cp["checkpoint_sha256"]=offload.sha256({k:cp[k] for k in offload.FIELDS})
    assert offload.check_checkpoint(cp)=="EXACT_STRUCTURAL_READBACK_ONLY"
    raw=bridge.canonical(cp)
    p=pointer(cp)
    full=bridge.packet_from_source(raw)
    pin=bridge.synthetic_pin(full)
    receiver=bridge.obtain_receiver(repo)
    ptrbytes=len(bridge.canonical(p))
    pktbytes=len(bridge.canonical(full))
    cases=[]
    def case(name,a,b,expect_a,expect_b):
        assert a==expect_a,(name,"A",a,expect_a)
        assert b==expect_b,(name,"B",b,expect_b)
        cases.append({"case":name,"pointer":a,"full":b})

    expected=cp["work_id"]
    revision=cp["source_revision"]
    OK_A="LOCAL_POINTER_RESTORE_ONLY"
    OK_B="LOCAL_SOURCE_AND_WORK_CONTRACT_MATCH_ONLY"
    def B(packet=full,policy=pin,generation=1,expected_revision=revision):
        return full_packet_status(receiver,packet,policy,expected,expected_revision,generation)
    case("healthy",restore_pointer(p,raw,revision),B(),OK_A,OK_B)
    case("source_resolver_unavailable",restore_pointer(p,None,revision),B(),"HOLD_SOURCE_UNAVAILABLE",OK_B)
    case("source_unreadable",restore_pointer(p,"corrupt",revision),B(),"HOLD_UNREADABLE_SOURCE",OK_B)
    modified=copy.deepcopy(cp);modified["sections"]["next"]["deed"]="different"
    case("source_bytes_modified",restore_pointer(p,bridge.canonical(modified),revision),B(), "HOLD_SOURCE_INTEGRITY",OK_B)
    changed=copy.deepcopy(cp);changed["sections"]["next"]["deed"]="new content"
    changed["checkpoint_sha256"]=offload.sha256({k:changed[k] for k in offload.FIELDS})
    case("source_valid_but_wrong_hash",restore_pointer(p,bridge.canonical(changed),revision),B(),"HOLD_UNRECOGNIZED_SOURCE",OK_B)
    case("known_revision_advanced",restore_pointer(p,raw,"fixture:revision-2"),B(), "HOLD_STALE_SOURCE_REVISION",OK_B)
    wrongid=copy.deepcopy(p);wrongid["work_id"]="different"
    case("pointer_identity_substitution",restore_pointer(wrongid,raw,revision),B(),"HOLD_WORK_ID_SUBSTITUTION",OK_B)
    staler=copy.deepcopy(pin);staler["generation"]=0
    case("receiver_pin_generation_invalid",restore_pointer(p,raw,revision),B(policy=staler),OK_A,"HELD_OUTER_SOURCE_PIN")
    case("receiver_pin_minimum_raised",restore_pointer(p,raw,revision),B(generation=2),OK_A,"HELD_OUTER_SOURCE_PIN")
    altered=copy.deepcopy(full);altered["sources"][0]["content_base64"]="AAAA"
    case("full_packet_corrupted",restore_pointer(p,raw,revision),B(packet=altered),OK_A,"HELD_OUTER_SOURCE_PIN")
    wrongpin=copy.deepcopy(pin);wrongpin["source_pins"][bridge.SOURCE_ID]["sha256"]="0"*64
    case("full_pin_mismatch",restore_pointer(p,raw,revision),B(policy=wrongpin),OK_A,"HELD_OUTER_SOURCE_PIN")
    case("receiver_source_revision_mismatch",restore_pointer(p,raw,revision),B(expected_revision="fixture:revision-2"),OK_A,"HELD_STALE_WORK_SOURCE")
    assert len(cases)==12
    assert ptrbytes<pktbytes
    return {
      "schema":SCHEMA,
      "source_fixture_sha256":cp["checkpoint_sha256"],
      "pointer_bytes":ptrbytes,
      "full_packet_bytes":pktbytes,
      "relative_full_to_pointer":round(pktbytes/ptrbytes,2),
      "tests":len(cases),"passed":len(cases),
      "cases":cases,
      "scope":"SYNTHETIC_FIXTURE_ONLY",
      "receiver_pin":"SELF_GENERATED_NOT_INDEPENDENT",
      "remote_storage":"NOT_TESTED",
      "external_receiver_ack":"UNPROVEN",
      "effects_performed":0,
      "conclusion":"PACKET_PRESERVES_BYTES_WHEN_RESOLVER_UNAVAILABLE__POINTER_SMALLER_WHEN_SOURCE_AVAILABLE__NEITHER_PROVES_INDEPENDENT_TRUST"
    }

if __name__=="__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--selftest",action="store_true")
    cli.add_argument("--repo-root",default=".")
    args=cli.parse_args()
    if not args.selftest:cli.error("use --selftest")
    print(json.dumps(main(Path(args.repo_root).resolve()),sort_keys=True))
