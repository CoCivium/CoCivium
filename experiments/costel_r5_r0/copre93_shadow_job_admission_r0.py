"""CoPre9.3 work-first SHADOW admission, leasing and receipt replay fixture.

Pure synthetic transitions. NEVER a production scheduler, worker recruiter,
autonomous executor, authority service, receiver, or network bridge.
All authority labels below are test inputs, not independently verified rights.
"""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import re
from typing import Any, Mapping

QUEUE_SCHEMA = "CoSessionMesh.WorkQueue.R0"
SCHEMA = "CoStel.CoPre93.ShadowJobAdmission.R0"
SHA256 = re.compile(r"^[a-f0-9]{64}$")
MAX_JOBS = 64
MAX_WORKERS = 32


class Held(ValueError):
    pass


def audit_candidate_queue(queue: Mapping[str, Any]) -> dict[str, Any]:
    """Survey source shape without turning worker labels into job authority."""
    if not isinstance(queue, dict) or queue.get("schema") != QUEUE_SCHEMA:
        raise Held("HOLD_SOURCE_SCHEMA")
    workers = queue.get("workers")
    if not isinstance(workers, list) or len(workers) > MAX_WORKERS:
        raise Held("HOLD_CANDIDATE_WORKER_COUNT")
    seen = set()
    for worker in workers:
        if not isinstance(worker, dict):
            raise Held("HOLD_WORKER_RECORD")
        wid = worker.get("worker_id")
        if not isinstance(wid, str) or not wid or wid in seen:
            raise Held("HOLD_DUPLICATE_OR_MISSING_DISPLAY_LABEL")
        seen.add(wid)
    return {
        "schema": SCHEMA,
        "state": "HOLD_QUEUE_NOT_A_REAL_DISPATCHER",
        "source_status": queue.get("status", "UNKNOWN"),
        "observed_candidate_labels": len(seen),
        "independently_authorized_workers": 0,
        "source_job_ids_proved_ready": 0,
        "dispatches": 0,
        "actual_worker_acks": 0,
        "note": "Queue labels and outcome names alone confer no capabilities, leases or authority.",
        "nonclaims": ["NOT_WORKER_ACK", "NOT_X2_RUNTIME", "NOT_SCHEDULER",
                      "NO_COEX", "NO_PHANTOM_ACK"],
    }


def _int0to10(v: Any) -> bool:
    return type(v) is int and 0 <= v <= 10


def shadow_rank(jobs: list[dict[str, Any]], completed: set[str],
                allowed_simulated_scopes: set[str]) -> dict[str, Any]:
    """Rank synthetic eligible jobs; hard gates before ranking; no assignment."""
    if not isinstance(jobs, list) or len(jobs) > MAX_JOBS:
        raise Held("HOLD_JOB_COUNT")
    if not isinstance(completed, set) or not isinstance(allowed_simulated_scopes, set):
        raise Held("HOLD_TRUSTED_SCOPE_INPUT")
    seen = set()
    eligible = []
    held = []
    for job in jobs:
        if not isinstance(job, dict):
            raise Held("HOLD_BAD_JOB")
        jid = job.get("job_id")
        if not isinstance(jid, str) or not jid or jid in seen:
            raise Held("HOLD_DUPLICATE_OR_MISSING_JOB_ID")
        seen.add(jid)
        dep = job.get("dependencies")
        scope = job.get("collision_scope")
        digest = job.get("source_sha256")
        scores = [job.get(k) for k in ("value", "urgency", "unlock", "age", "risk")]
        conditions = [
            job.get("synthetic_scope") is True,
            isinstance(scope, str) and scope.startswith("SYNTHETIC:"),
            scope in allowed_simulated_scopes,
            isinstance(digest, str) and SHA256.fullmatch(digest) is not None,
            type(job.get("ready")) is bool and job.get("ready") is True,
            isinstance(dep, list) and all(isinstance(x, str) for x in dep),
            isinstance(dep, list) and all(x in completed for x in dep),
            all(_int0to10(x) for x in scores),
        ]
        if not all(conditions):
            held.append({"job_id": jid, "state": "HOLD_ADMISSION_GATES"})
            continue
        value, urgency, unlock, age, risk = scores
        score = 4 * value + 3 * urgency + 2 * unlock + age - 2 * risk
        eligible.append((score, jid, scope))
    eligible.sort(key=lambda x: (-x[0], x[1]))
    return {
        "schema": SCHEMA, "state": "SHADOW_RANK_ONLY_NOT_AUTHORIZED_EXECUTION",
        "eligible": [{"job_id": jid, "advisory_score": s, "scope": sc}
                     for s, jid, sc in eligible],
        "held": held,
        "assignments": 0, "actuations": 0, "worker_acks": 0,
        "nonclaims": ["SHADOW_ADVISORY_NOT_AUTHORITY", "NO_REAL_DISPATCH", "NO_COEX"]
    }


@dataclass(frozen=True)
class Lease:
    job_id: str
    collision_scope: str
    worker_id: str
    fencing_epoch: int
    expires_at: int


class SyntheticLedger:
    """In-memory negative-control fixture. No disk, networking, OS or user task."""
    def __init__(self, allowed_simulated_scopes: set[str],
                 verified_synthetic_capabilities: dict[str, set[str]]):
        if any(not str(scope).startswith("SYNTHETIC:") for scope in allowed_simulated_scopes):
            raise Held("HOLD_SCOPE_NOT_SYNTHETIC")
        self.allowed = allowed_simulated_scopes.copy()
        self.verified = {k: v.copy() for k, v in verified_synthetic_capabilities.items()}
        self.fencing_epochs: dict[str, int] = {}
        self.lease_by_scope: dict[str, Lease] = {}
        self.finished: dict[str, str] = {}
        self.stopped: set[str] = set()
        self.events: list[tuple[str, str]] = []

    def claim(self, *, job_id: str, scope: str, worker_id: str,
              required_capabilities: set[str], now: int, ttl: int) -> Lease:
        if not isinstance(job_id, str) or not job_id or not isinstance(scope, str):
            raise Held("HOLD_IDENTITY")
        if scope not in self.allowed or not scope.startswith("SYNTHETIC:"):
            raise Held("HOLD_SCOPE_AUTHORITY")
        if worker_id not in self.verified or not required_capabilities.issubset(self.verified[worker_id]):
            raise Held("HOLD_WORKER_CAPABILITY_UNVERIFIED")
        if job_id in self.stopped:
            raise Held("HOLD_EXPLICIT_STOP")
        if job_id in self.finished:
            raise Held("HOLD_COMPLETED_JOB_REPLAY")
        if type(now) is not int or type(ttl) is not int or ttl < 1 or ttl > 3600:
            raise Held("HOLD_CLOCK_OR_TTL")
        current = self.lease_by_scope.get(scope)
        if current is not None and now < current.expires_at:
            raise Held("HOLD_LIVE_COLLISION_LEASE")
        next_epoch = self.fencing_epochs.get(scope, 0) + 1
        self.fencing_epochs[scope] = next_epoch
        lease = Lease(job_id, scope, worker_id, next_epoch, now + ttl)
        self.lease_by_scope[scope] = lease
        self.events.append(("LEASE_ISSUED_SHADOW", job_id))
        return lease

    def commit(self, lease: Lease, *, now: int, result_sha256: str) -> str:
        if not isinstance(result_sha256, str) or SHA256.fullmatch(result_sha256) is None:
            raise Held("HOLD_RECEIPT_HASH")
        if lease.job_id in self.finished:
            if self.finished[lease.job_id] == result_sha256:
                return "REPLAY_SAME_SYNTHETIC_RECEIPT_NO_EFFECT"
            raise Held("HOLD_CONFLICTING_RECEIPT")
        if lease.job_id in self.stopped:
            raise Held("HOLD_EXPLICIT_STOP")
        current = self.lease_by_scope.get(lease.collision_scope)
        if current != lease or type(now) is not int or now >= lease.expires_at:
            raise Held("HOLD_STALE_FENCING_TOKEN_OR_LEASE")
        self.finished[lease.job_id] = result_sha256
        self.lease_by_scope.pop(lease.collision_scope)
        self.events.append(("SYNTHETIC_RECEIPT_COMMITTED", lease.job_id))
        return "SYNTHETIC_RECEIPT_COMMITTED"

    def stop(self, job_id: str) -> None:
        self.stopped.add(job_id)
        for scope, lease in list(self.lease_by_scope.items()):
            if lease.job_id == job_id:
                self.lease_by_scope.pop(scope)
                self.fencing_epochs[scope] = max(self.fencing_epochs.get(scope, 0), lease.fencing_epoch) + 1
        self.events.append(("STOP_WINS", job_id))
