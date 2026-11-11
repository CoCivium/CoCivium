"""Fail-closed R1 checks. No provider, network, real-world or outside-device access."""
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT))
from process_recovery import (
    RecoveryError, atomic_write, cp_body, digest_prefix, read_json,
    reclaim_dead_lock, run_worker, sealed_body, setup_workspace,
    validate_checkpoint, validate_grant,
)
from supervisor_canary import full_canary, PUBLIC_SOURCE


class RecoveryTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='coscalemorph-test-')
        self.addCleanup(self.tmp.cleanup)
        self.state=Path(self.tmp.name)/'state'
        self.source=Path(self.tmp.name)/'graph.json'
        self.source.write_bytes(PUBLIC_SOURCE.read_bytes())
        self.m=setup_workspace(self.state,self.source.read_bytes(),task_count=12)

    def rejects(self,code,action):
        with self.assertRaises(RecoveryError) as ex:
            action()
        self.assertIn(code,str(ex.exception))

    def test_initial_worker_all_tasks(self):
        r=run_worker(self.state,self.source)
        self.assertEqual(r['status'],'COMPLETE')
        self.assertEqual(r['completed'],12)
        self.assertEqual(r['digest'],digest_prefix(self.m['source_sha256'],12))
        self.assertFalse((self.state/'worker.lock').exists())

    def test_bounded_pause_then_resume(self):
        first=run_worker(self.state,self.source,max_steps=5)
        next=run_worker(self.state,self.source)
        self.assertEqual((first['completed'],first['status']),(5,'PAUSED'))
        self.assertEqual((next['completed'],next['status']),(12,'COMPLETE'))

    def test_corrupted_checkpoint_digest_rejected(self):
        run_worker(self.state,self.source,max_steps=3)
        cp=read_json(self.state/'checkpoint.json')
        cp['rolling_digest']='f'*64
        atomic_write(self.state/'checkpoint.json',cp)
        self.rejects('CHECKPOINT_HASH_MISMATCH',lambda:run_worker(self.state,self.source))

    def test_invented_progress_even_with_rehashed_checkpoint_rejected(self):
        run_worker(self.state,self.source,max_steps=4)
        cp=read_json(self.state/'checkpoint.json')
        cp['rolling_digest']='f'*64
        del cp['checkpoint_sha256']
        atomic_write(self.state/'checkpoint.json',sealed_body(cp))
        self.rejects('CHECKPOINT_TASK_PREFIX_MISMATCH',lambda:run_worker(self.state,self.source))

    def test_wrong_source_rejected(self):
        self.source.write_bytes(self.source.read_bytes()+b' ')
        self.rejects('SOURCE_IDENTITY_MISMATCH',lambda:run_worker(self.state,self.source))

    def test_missing_source_rejected(self):
        self.source.unlink()
        self.rejects('SOURCE_UNAVAILABLE',lambda:run_worker(self.state,self.source))

    def test_stale_mission_definition_rejected(self):
        run_worker(self.state,self.source,max_steps=3)
        m=read_json(self.state/'mission.json')
        m['task_count']=13
        atomic_write(self.state/'mission.json',m)
        self.rejects('CHECKPOINT_NAMESPACE_CHANGED',lambda:run_worker(self.state,self.source))

    def test_revoked_grant_rejected(self):
        run_worker(self.state,self.source,max_steps=3)
        g=read_json(self.state/'grant.json')
        g['state']='REVOKED'
        atomic_write(self.state/'grant.json',g)
        self.rejects('AUTHORIZATION_REVOKED_OR_OUT_OF_SCOPE',lambda:run_worker(self.state,self.source))

    def test_expired_grant_rejected(self):
        g=read_json(self.state/'grant.json')
        g['valid_until_utc']='2000-01-01T00:00:00Z'
        atomic_write(self.state/'grant.json',g)
        self.rejects('AUTHORIZATION_EXPIRED',lambda:run_worker(self.state,self.source))

    def test_forged_receiver_ack_rejected(self):
        run_worker(self.state,self.source,max_steps=3)
        cp=read_json(self.state/'checkpoint.json')
        cp['receiver_ack']='VERIFIED'
        del cp['checkpoint_sha256']
        atomic_write(self.state/'checkpoint.json',sealed_body(cp))
        self.rejects('FORGED_EXTERNAL_EFFECT',lambda:run_worker(self.state,self.source))

    def test_lock_fail_closed_with_live_owner(self):
        lock={'schema':'CoScaleMorph.LocalLock/R1','work_id':self.m['work_id'],'pid':__import__('os').getpid(),'nonce':'a'*32}
        atomic_write(self.state/'worker.lock',lock)
        self.rejects('LOCK_HELD_OR_STALE_REQUIRES_EXPLICIT_RECLAIM',lambda:run_worker(self.state,self.source))
        self.rejects('OWNER_STILL_LIVE',lambda:reclaim_dead_lock(self.state,__import__('os').getpid()))

    def test_workspace_refuses_reinitialize(self):
        self.rejects('WORKSPACE_NOT_EMPTY',lambda:setup_workspace(self.state,self.source.read_bytes()))

    def test_tasks_bounded(self):
        self.rejects('INVALID_WORK_BOUNDS',lambda:run_worker(self.state,self.source,max_steps=10**10))

    def test_duplicates_in_grant_rejected(self):
        (self.state/'grant.json').write_text('{"state":"AUTHORIZED","state":"REVOKED"}',encoding='utf-8')
        self.rejects('DUPLICATE_JSON_KEY',lambda:run_worker(self.state,self.source))

    def test_revoked_permission_not_overwritten(self):
        g=read_json(self.state/'grant.json')
        g['state']='REVOKED'
        atomic_write(self.state/'grant.json',g)
        self.rejects('AUTHORIZATION_REVOKED_OR_OUT_OF_SCOPE',lambda:run_worker(self.state,self.source))
        self.assertFalse((self.state/'checkpoint.json').exists())


    def test_two_live_processes_do_not_share_one_checkpoint(self):
        worker=subprocess.Popen([sys.executable,str(ROOT/'process_recovery.py'),'run',
                                 '--state',str(self.state),'--source',str(self.source),
                                 '--delay-ms','130'], stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
        try:
            import time
            expiry=time.monotonic()+4
            while time.monotonic()<expiry:
                if (self.state/'checkpoint.json').exists():
                    cp=read_json(self.state/'checkpoint.json')
                    if cp.get('completed',0)>=2 and worker.poll() is None:
                        break
                time.sleep(.02)
            else: self.fail('first worker failed to reach contention window')
            contender=subprocess.run([sys.executable,str(ROOT/'process_recovery.py'),'run',
                                      '--state',str(self.state),'--source',str(self.source)],
                                     capture_output=True,text=True,timeout=5)
            self.assertEqual(contender.returncode,2)
            self.assertIn('LOCK_HELD',contender.stderr)
        finally:
            if worker.poll() is None:worker.kill()
            worker.wait(timeout=5)
            if (self.state/'worker.lock').exists():
                reclaim_dead_lock(self.state,worker.pid)

    def test_revoke_grant_while_worker_is_running(self):
        worker=subprocess.Popen([sys.executable,str(ROOT/'process_recovery.py'),'run',
                                 '--state',str(self.state),'--source',str(self.source),
                                 '--delay-ms','130'],stdout=subprocess.DEVNULL,stderr=subprocess.PIPE,text=True)
        try:
            import time
            expiry=time.monotonic()+4
            while time.monotonic()<expiry:
                if (self.state/'checkpoint.json').exists():
                    cp=read_json(self.state/'checkpoint.json')
                    if cp.get('completed',0)>=2 and worker.poll() is None:
                        break
                time.sleep(.02)
            else:self.fail('worker did not reach revocation gate')
            g=read_json(self.state/'grant.json')
            g['state']='REVOKED'
            atomic_write(self.state/'grant.json',g)
            _,stderr=worker.communicate(timeout=5)
            self.assertEqual(worker.returncode,2)
            self.assertIn('AUTHORIZATION_REVOKED_OR_OUT_OF_SCOPE',stderr)
            cp2=read_json(self.state/'checkpoint.json')
            self.assertLess(cp2['completed'],12)
            self.assertEqual(cp2['receiver_ack'],'NOT_OBSERVED')
            self.assertFalse((self.state/'worker.lock').exists())
        finally:
            if worker.poll() is None:
                worker.kill()
                worker.communicate(timeout=5)

    def test_actual_os_process_death_and_independent_successor(self):
        # Runs a separate Python interpreter for the first worker and successor.
        receipt=full_canary(task_count=16,slow_ms=125)
        self.assertEqual(receipt['completed'],16)
        self.assertTrue(receipt['stale_lock_blocked_attempt'])
        self.assertTrue(receipt['successor_different_pid'])
        self.assertTrue(receipt['replay_exact_digest'])
        self.assertEqual(receipt['receiver_ack'],'NOT_OBSERVED')

if __name__=='__main__':unittest.main()
