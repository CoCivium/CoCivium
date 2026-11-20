"""CoLocalWorkID R1: portable interrupted synthetic WorkID, cold recovery.

One bounded *test* in the existing CoLocalWorkID review branch. It never
starts a scheduler, executes real model calls, or claims receiver-origin ACK.
SQLite state is exported using the SQLite backup API, not a raw live WAL copy.
An attacker controlling both archive and caller's SHA pin is out of scope.
"""
import hashlib
import json
import os
import pathlib
import sqlite3
import subprocess
import sys
import tempfile
import unittest
import zipfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1] / "cotalkitout"))
from due_work_catchup_r0 import Claim, DueWorkQueue

WORK = "CoLocalFirstUnfinished_SYNTHETIC_R1"
DUE = 1700000000
LEASE = 15
SOURCE = {"work_id": WORK, "synthetic": True, "payload": "NO_REAL_EFFECT", "external_receiver_ack": False}
RESULT = {"work_id": WORK, "state": "LOCAL_REPLAY_RESULT_ONLY",
          "model_calls": 0, "external_effects": 0, "receiver_ack": False}
MEMBERS = ("source.json", "checkpoint.json", "queue.sqlite3")
SCHEMA = "CoAll.WorkID.InterruptedSynthetic.R1"


def raw_json(obj):
    return (json.dumps(obj, sort_keys=True, separators=(",", ":")) + "\n").encode()


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def must(value, code):
    if not value:
        raise ValueError("HOLD_" + code)


def source_hash():
    return digest(raw_json(SOURCE))


def result_hash():
    return digest(raw_json(RESULT))


def manifest_for(entries):
    return {"schema": SCHEMA, "origin": "INVENTED_ONLY", "work_id": WORK,
            "members": [{"name": n, "sha256": digest(entries[n]), "size": len(entries[n])}
                        for n in MEMBERS],
            "nonclaims": ["NOT_X2_CAPSULE", "NOT_COSTEAD_RECEIVER_ACK",
                          "NOT_REAL_SCHEDULER", "NOT_EXTERNAL_EFFECT"]}


def prepare(root):
    """Simulate original worker dying *after lease*, before any result."""
    root.mkdir(parents=True, exist_ok=True)
    producer = root / "producer"
    producer.mkdir()
    source = raw_json(SOURCE)
    (producer / "source.json").write_bytes(source)
    live = producer / "live.sqlite3"
    queue = DueWorkQueue(str(live))
    try:
        must(queue.enqueue(WORK, "SYNTHETIC_R1", digest(source), DUE) == "ENQUEUED",
             "ORIGINAL_ENQUEUE")
        claims = queue.claim_due(now=DUE + 1, owner="ORIGINAL_INCARNATION",
                                 lease_seconds=LEASE, limit=1)
        must(len(claims) == 1 and claims[0].epoch == 1, "ORIGINAL_LEASE")
        claim = claims[0]
        snapshot = producer / "queue.sqlite3"
        with sqlite3.connect(snapshot) as backup:
            queue.db.backup(backup)
    finally:
        queue.close()
    checkpoint = {"schema": SCHEMA, "work_id": WORK, "state": "LEASED_UNFINISHED",
                  "source_sha256": digest(source), "epoch": claim.epoch,
                  "owner": claim.owner, "lease_until": claim.lease_until,
                  "result_sha256": None, "receiver_ack": False,
                  "external_effects": 0}
    (producer / "checkpoint.json").write_bytes(raw_json(checkpoint))
    entries = {name: (producer / name).read_bytes() for name in MEMBERS}
    manifest = manifest_for(entries)
    capsule = root / "unfinished.zip"
    with zipfile.ZipFile(capsule, "x", compression=zipfile.ZIP_DEFLATED) as z:
        z.writestr("manifest.json", raw_json(manifest))
        for name in MEMBERS:
            z.writestr(name, entries[name])
    return capsule, digest(capsule.read_bytes()), claim


def verify_archive(capsule, pinned_sha):
    must(isinstance(pinned_sha, str) and len(pinned_sha) == 64 and
         digest(capsule.read_bytes()) == pinned_sha, "CAPSULE_HASH")
    with zipfile.ZipFile(capsule, "r") as z:
        info = z.infolist()
        names = [item.filename for item in info]
        must(len(info) == 4 and len(set(names)) == 4 and
             set(names) == set(MEMBERS) | {"manifest.json"}, "ZIP_MEMBERS")
        must(all(not x.is_dir() and not (x.flag_bits & 1) and
                 0 < x.file_size < 2000000 and
                 ((x.external_attr >> 16) & 0o170000) != 0o120000
                 for x in info), "ZIP_SAFETY")
        must(sum(x.file_size for x in info) < 8000000, "ZIP_BOUNDS")
        manifest = json.loads(z.read("manifest.json"))
        must(manifest.get("schema") == SCHEMA and
             manifest.get("origin") == "INVENTED_ONLY" and
             manifest.get("work_id") == WORK, "MANIFEST")
        expected = manifest.get("members")
        must(isinstance(expected, list) and len(expected) == len(MEMBERS) and
             [x.get("name") for x in expected] == list(MEMBERS), "MANIFEST_INDEX")
        entries = {name: z.read(name) for name in MEMBERS}
        for item in expected:
            raw = entries[item["name"]]
            must(len(raw) == item.get("size") and digest(raw) == item.get("sha256"),
                 "MEMBER_SHA")
        must(entries["source.json"] == raw_json(SOURCE), "SOURCE_IDENTITY")
        checkpoint = json.loads(entries["checkpoint.json"])
        must(checkpoint == {
            "schema": SCHEMA, "work_id": WORK, "state": "LEASED_UNFINISHED",
            "source_sha256": source_hash(), "epoch": 1,
            "owner": "ORIGINAL_INCARNATION", "lease_until": DUE + 1 + LEASE,
            "result_sha256": None, "receiver_ack": False, "external_effects": 0
        }, "UNFINISHED_CHECKPOINT")
    return entries


def cold_restore(capsule, pin, target):
    must(not target.exists(), "DEST_EXISTS")
    entries = verify_archive(capsule, pin)
    target.mkdir()
    for name in MEMBERS:
        (target / name).write_bytes(entries[name])
        must((target / name).read_bytes() == entries[name], "RESTORE_READBACK")
    verify_queue(target, exact_initial=True)


def verify_queue(target, exact_initial=False):
    must((target / "source.json").read_bytes() == raw_json(SOURCE), "SOURCE_DRIFT")
    checkpoint = json.loads((target / "checkpoint.json").read_bytes())
    must(checkpoint.get("schema") == SCHEMA and
         checkpoint.get("source_sha256") == source_hash() and
         checkpoint.get("receiver_ack") is False and
         checkpoint.get("external_effects") == 0, "CHECKPOINT_INTEGRITY")
    p = target / "queue.sqlite3"
    must(p.is_file() and not p.is_symlink(), "DB_SOURCE")
    try:
        with sqlite3.connect(p.resolve().as_uri() + "?mode=ro", uri=True) as ro:
            must(ro.execute("PRAGMA integrity_check").fetchone() == ("ok",),
                 "DB_INTEGRITY")
            rows = ro.execute(
                "SELECT work_id,source_revision,payload_sha256,due_at,state,"
                "epoch,owner,lease_until,result_sha256,completed_at "
                "FROM work ORDER BY work_id").fetchall()
            objects = ro.execute(
                "SELECT type,name FROM sqlite_master WHERE type!='index' "
                "ORDER BY type,name").fetchall()
            must(objects == [("table", "work")], "DB_SCHEMA")
    except sqlite3.DatabaseError as exc:
        raise ValueError("HOLD_DB_UNREADABLE") from exc
    must(len(rows) == 1 and rows[0][:4] ==
         (WORK, "SYNTHETIC_R1", source_hash(), DUE), "WORKSET_IDENTITY")
    if exact_initial:
        must(rows[0] == (WORK, "SYNTHETIC_R1", source_hash(), DUE,
                         "LEASED", 1, "ORIGINAL_INCARNATION", DUE + 1 + LEASE,
                         None, None), "ORIGINAL_INFLIGHT_STATE")
    return rows[0]


def resume(target, now, owner, simulate_crash=False):
    """Cold-process recovery, no external effect. Returns truthful local state."""
    before = verify_queue(target)
    must(before[4] in ("LEASED", "DONE"), "UNKNOWN_JOB_STATE")
    if before[4] == "DONE":
        return {"state": "ALREADY_DONE_NO_EFFECT", "model_calls": 0,
                "receiver_ack": False, "external_effects": 0}
    queue = DueWorkQueue(str(target / "queue.sqlite3"))
    try:
        claims = queue.claim_due(now=now, owner=owner,
                                 lease_seconds=LEASE, limit=1)
        if not claims:
            return {"state": "HOLD_ACTIVE_LEASE", "model_calls": 0,
                    "receiver_ack": False, "external_effects": 0}
        must(len(claims) == 1 and claims[0].work_id == WORK,
             "RECLAIM_SELECTION")
        claim = claims[0]
        if simulate_crash:
            print(json.dumps({"crash_after_claim": True, "epoch": claim.epoch,
                              "owner": claim.owner}), flush=True)
            os._exit(77)
        outcome = queue.complete(claim, result_sha256=result_hash(), now=now+1)
        must(outcome == "COMMITTED_LOCAL_ONLY", "RESULT_FENCE")
        return {"state": outcome, "epoch": claim.epoch,
                "model_calls": 0, "receiver_ack": False, "external_effects": 0}
    finally:
        queue.close()


def child(target, now, owner, crash=False):
    return subprocess.run(
        [sys.executable, "-B", str(pathlib.Path(__file__).resolve()),
         "--resume", str(target), str(now), owner] +
        (["--crash-after-claim"] if crash else []),
        capture_output=True, text=True, timeout=15)


class Tests(unittest.TestCase):
    def setUp(self):
        t = tempfile.TemporaryDirectory()
        self.addCleanup(t.cleanup)
        self.root = pathlib.Path(t.name)
        self.zip, self.pin, self.original_claim = prepare(self.root)
        self.restored = self.root / "restored"

    def test_cold_interrupted_job_recovers_after_incarnation_crash(self):
        cold_restore(self.zip, self.pin, self.restored)
        self.assertEqual(verify_queue(self.restored)[4], "LEASED")
        # A second process dies after reclaiming epoch 2, without committing.
        crash = child(self.restored, DUE+LEASE+2, "RESTORE_INCARNATION_1", True)
        self.assertEqual(crash.returncode, 77, crash.stderr)
        self.assertEqual(json.loads(crash.stdout)["epoch"], 2)
        # A third process cannot steal an unexpired elected lease.
        hold = child(self.restored, DUE+LEASE+3, "RESTORE_INCARNATION_2")
        self.assertEqual(hold.returncode, 0, hold.stderr)
        self.assertEqual(json.loads(hold.stdout)["state"], "HOLD_ACTIVE_LEASE")
        # After expiry, a fresh process finishes the one local result.
        done = child(self.restored, DUE+2*LEASE+3, "RESTORE_INCARNATION_3")
        self.assertEqual(done.returncode, 0, done.stderr)
        self.assertEqual(json.loads(done.stdout)["state"], "COMMITTED_LOCAL_ONLY")
        self.assertEqual(verify_queue(self.restored)[5], 3)
        again = child(self.restored, DUE+2*LEASE+50, "OTHER_ACTOR")
        self.assertEqual(json.loads(again.stdout)["state"], "ALREADY_DONE_NO_EFFECT")
        self.assertEqual(verify_queue(self.restored)[5], 3)

    def test_original_lease_holder_is_fenced_after_expiry(self):
        cold_restore(self.zip, self.pin, self.restored)
        q = DueWorkQueue(str(self.restored / "queue.sqlite3"))
        try:
            claims = q.claim_due(now=DUE+LEASE+2, owner="RECOVERED", lease_seconds=LEASE)
            self.assertEqual(len(claims), 1)
            self.assertEqual(q.complete(self.original_claim,
                         result_sha256=result_hash(), now=DUE+LEASE+3), "FENCED")
            self.assertEqual(q.complete(claims[0],
                         result_sha256=result_hash(), now=DUE+LEASE+3),
                             "COMMITTED_LOCAL_ONLY")
            self.assertEqual(q.complete(claims[0],
                         result_sha256=result_hash(), now=DUE+LEASE+3), "REPLAY")
            self.assertEqual(q.enqueue(WORK, "SYNTHETIC_R1", source_hash(), DUE),
                             "REPLAY")
            self.assertEqual(q.claim_due(now=DUE+500,owner="FOURTH"), [])
        finally:
            q.close()

    def test_unexpired_original_lease_not_stolen(self):
        cold_restore(self.zip, self.pin, self.restored)
        p = child(self.restored,DUE+LEASE-1,"UNINVITED")
        self.assertEqual(json.loads(p.stdout)["state"], "HOLD_ACTIVE_LEASE")
        self.assertEqual(verify_queue(self.restored)[5], 1)

    def test_forged_archive_sha_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "HOLD_CAPSULE_HASH"):
            cold_restore(self.zip, "0"*64, self.restored)

    def test_destination_never_clobbered(self):
        self.restored.mkdir()
        with self.assertRaisesRegex(ValueError, "HOLD_DEST_EXISTS"):
            cold_restore(self.zip, self.pin, self.restored)

    def test_manifest_tamper_detected_even_with_updated_outer_sha(self):
        corrupt = self.root / "corrupt.zip"
        with zipfile.ZipFile(self.zip) as src, zipfile.ZipFile(corrupt,"x") as dst:
            for name in src.namelist():
                payload=src.read(name)
                if name=="source.json":
                    payload=payload.replace(b"NO_REAL_EFFECT", b"A_REAL_EFFECT!")
                dst.writestr(name,payload)
        with self.assertRaisesRegex(ValueError, "HOLD_MEMBER_SHA"):
            cold_restore(corrupt,digest(corrupt.read_bytes()),self.restored)

    def test_extra_archive_member_rejected(self):
        extra = self.root / "extra.zip"
        with zipfile.ZipFile(self.zip) as src, zipfile.ZipFile(extra,"x") as dst:
            for name in src.namelist():
                dst.writestr(name,src.read(name))
            dst.writestr("../outside.txt","not executable")
        with self.assertRaisesRegex(ValueError, "HOLD_ZIP_MEMBERS"):
            cold_restore(extra,digest(extra.read_bytes()),self.restored)

    def test_hidden_workid_fails_readonly_preflight(self):
        cold_restore(self.zip,self.pin,self.restored)
        q=DueWorkQueue(str(self.restored/"queue.sqlite3"))
        try:
            self.assertEqual(q.enqueue("hidden-work", "SYNTHETIC_R1",
                                       "0"*64,DUE),"ENQUEUED")
        finally:q.close()
        with self.assertRaisesRegex(ValueError,"HOLD_WORKSET_IDENTITY"):
            resume(self.restored,DUE+LEASE+2,"OTHER")

    def test_forged_checkpoint_ack_holds(self):
        cold_restore(self.zip,self.pin,self.restored)
        f=self.restored/"checkpoint.json"
        o=json.loads(f.read_bytes());o["receiver_ack"]=True
        f.write_bytes(raw_json(o))
        with self.assertRaisesRegex(ValueError, "HOLD_CHECKPOINT_INTEGRITY"):
            resume(self.restored,DUE+LEASE+2,"OTHER")

    def test_untrusted_source_tamper_holds_without_leasing(self):
        cold_restore(self.zip,self.pin,self.restored)
        f=self.restored/"source.json"
        f.write_bytes(f.read_bytes()+b"\n")
        with self.assertRaisesRegex(ValueError,"HOLD_SOURCE_DRIFT"):
            resume(self.restored,DUE+LEASE+2,"OTHER")


if __name__ == "__main__":
    if len(sys.argv)>1 and sys.argv[1]=="--resume":
        result=resume(pathlib.Path(sys.argv[2]),int(sys.argv[3]),sys.argv[4],
                      "--crash-after-claim" in sys.argv[5:])
        print(json.dumps(result,sort_keys=True))
    else:
        unittest.main()
