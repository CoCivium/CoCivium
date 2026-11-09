"""CoPreGeneric release readiness gate R0.

Pure evaluation of supplied independent receipts, no network and no invented ACK.
It cannot itself install X2, provision a repository, publish a website or sync.
"""
REQUIRED_TARGETS = (
    "github.com/CoCivium/CoPreGeneric",
    "CoCivium.org/CoPre",
    "InSeed.com/Stead",
)

def evaluate(evidence):
    """Fail closed when receipts are absent, mismatched, or self-declared."""
    holds = []
    source = evidence.get("candidate_source", {})
    if not (source.get("readback") is True
            and source.get("commit_sha")
            and source.get("visibility") == "PUBLIC"):
        holds.append("PUBLIC_CANDIDATE_SOURCE_NOT_VERIFIED")
    targets = evidence.get("targets", {})
    digests = set()
    for target in REQUIRED_TARGETS:
        proof = targets.get(target, {})
        if not (proof.get("owner_authorized") is True
                and proof.get("independent_fetch") is True
                and proof.get("privacy_review") is True
                and proof.get("http_success") is True
                and proof.get("sha256")
                and len(proof.get("sha256", "")) == 64
                and all(c in "0123456789abcdef" for c in proof["sha256"].lower())):
            holds.append("TARGET_NOT_QUALIFIED:" + target)
        else:
            digests.add(proof["sha256"].lower())
    if len(digests) != 1 or len(targets) < len(REQUIRED_TARGETS):
        holds.append("THREE_MIRROR_IDENTICAL_PAYLOAD_UNPROVEN")
    receiver = evidence.get("receiver", {})
    if not (receiver.get("independent_actor") is True
            and receiver.get("exact_digest_match") is True
            and receiver.get("durable_ack") is True
            and receiver.get("recovery_after_restart") is True):
        holds.append("INDEPENDENT_RECEIVER_HANDOFF_UNPROVEN")
    if not (evidence.get("seed_survival", {}).get("verified_hours", 0) > 24):
        holds.append("SEED_SURVIVAL_GT_24H_UNPROVEN")
    if not (evidence.get("system_automation", {}).get("system_owned") is True
            and evidence.get("system_automation", {}).get("human_interventions") == 0
            and evidence.get("system_automation", {}).get("observed_run") is True):
        holds.append("SYSTEM_1_YOU_0_UNPROVEN")
    return {"schema":"CoPreGeneric.ReadinessGate.R0",
            "status":"READY_FOR_INDEPENDENT_DEPLOYMENT_TEST" if not holds else "DRAFT_HELD",
            "holds":holds,
            "ready":not holds,
            "checked_destinations":list(REQUIRED_TARGETS),
            "effective_runtime_proven":False,
            "coex_proven":False,
            "governing_canon_proven":False}

if __name__ == "__main__":
    import json
    from pathlib import Path
    fixture = json.loads(Path(__file__).with_name("copre_ready_cycle_observed_r0.json").read_text())
    print(json.dumps(evaluate(fixture), indent=2))
