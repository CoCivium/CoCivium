"""CoOrb boundary semantics: independent facts, candidate futures and version identity.

Synthetic view-model contract only. NOT an installed renderer or operating
observer. No subjective halo state is accepted as a proof of running code.
"""
from dataclasses import dataclass
import unittest


@dataclass(frozen=True)
class EvidenceRay:
    direction: str  # inward, outward, lateral, past, present, future
    status: str  # VERIFIED, OBSERVED, PREDICTED, UNKNOWN, CONTRADICTED
    source_id: str = ""
    source_hash: str = ""
    observed_at: int = 0
    ttl_seconds: int = 0
    confidence: float | None = None
    horizon_seconds: int = 0


@dataclass(frozen=True)
class OrbRevision:
    contract_version: str
    source_commit: str
    receiver_version: str
    rays: tuple


ALLOWED_DIRECTIONS = {"inward", "outward", "lateral", "past", "present", "future"}
ALLOWED_STATES = {"VERIFIED", "OBSERVED", "PREDICTED", "UNKNOWN", "CONTRADICTED"}


def project(revision, *, now):
    """Deterministic presentation from provenance and freshness, not animation."""
    if not revision.contract_version or not revision.source_commit:
        raise ValueError("unversioned orb contract")
    output = []
    for ray in revision.rays:
        if ray.direction not in ALLOWED_DIRECTIONS or ray.status not in ALLOWED_STATES:
            raise ValueError("unknown ray type")
        if ray.confidence is not None and not 0 <= ray.confidence <= 1:
            raise ValueError("confidence must be probability")
        has_evidence = bool(ray.source_id and ray.source_hash and ray.observed_at > 0)
        is_fresh = (has_evidence and ray.ttl_seconds > 0
                    and 0 <= now - ray.observed_at <= ray.ttl_seconds)
        if ray.status in ("VERIFIED", "OBSERVED"):
            visible = ray.status if is_fresh else "STALE_OR_UNVERIFIED"
        elif ray.status == "PREDICTED":
            visible = "PREDICTION" if has_evidence and ray.horizon_seconds > 0 else "UNQUALIFIED_PREDICTION"
        else:
            visible = ray.status
        output.append({
            "direction": ray.direction,
            "display_state": visible,
            "future_horizon_seconds": ray.horizon_seconds if visible == "PREDICTION" else 0,
            "source_hash": ray.source_hash if has_evidence else None,
            "confidence": ray.confidence if visible == "PREDICTION" else None,
        })
    return {
        "contract_version": revision.contract_version,
        "source_commit": revision.source_commit,
        "receiver_version": revision.receiver_version or "UNBOUND",
        "rays": output,
        "live_receiver_proven": False,
    }


class OrbMembraneTests(unittest.TestCase):
    def rev(self, *rays):
        return OrbRevision("CoOrb.Membrane.R0", "gitsha-demo", "", rays)

    def test_orb_version_is_explicit(self):
        p = project(self.rev(), now=100)
        self.assertEqual(p["contract_version"], "CoOrb.Membrane.R0")
        self.assertEqual(p["receiver_version"], "UNBOUND")
        self.assertFalse(p["live_receiver_proven"])

    def test_verified_ray_needs_source_and_freshness(self):
        ray = EvidenceRay("inward", "VERIFIED", "src", "hash", 90, 20)
        self.assertEqual(project(self.rev(ray), now=100)["rays"][0]["display_state"], "VERIFIED")

    def test_aged_verification_not_green(self):
        ray = EvidenceRay("outward", "VERIFIED", "src", "hash", 90, 5)
        self.assertEqual(project(self.rev(ray), now=100)["rays"][0]["display_state"],
                         "STALE_OR_UNVERIFIED")

    def test_no_source_no_verification(self):
        ray = EvidenceRay("present", "VERIFIED")
        self.assertEqual(project(self.rev(ray), now=100)["rays"][0]["display_state"],
                         "STALE_OR_UNVERIFIED")

    def test_future_prediction_not_observation(self):
        ray = EvidenceRay("future", "PREDICTED", "forecast", "h", 90, 20, 0.7, 3600)
        p = project(self.rev(ray), now=100)["rays"][0]
        self.assertEqual(p["display_state"], "PREDICTION")
        self.assertEqual(p["future_horizon_seconds"], 3600)

    def test_future_prediction_without_horizon_is_unqualified(self):
        ray = EvidenceRay("future", "PREDICTED", "forecast", "h", 90, 20, 0.7, 0)
        self.assertEqual(project(self.rev(ray), now=100)["rays"][0]["display_state"],
                         "UNQUALIFIED_PREDICTION")

    def test_contradiction_preserved(self):
        ray = EvidenceRay("lateral", "CONTRADICTED", "src", "h", 90, 20)
        self.assertEqual(project(self.rev(ray), now=100)["rays"][0]["display_state"],
                         "CONTRADICTED")

    def test_negative_confidence_fails_closed(self):
        with self.assertRaises(ValueError):
            project(self.rev(EvidenceRay("future", "PREDICTED", confidence=1.5)), now=100)

    def test_unsupported_direction_fails_closed(self):
        with self.assertRaises(ValueError):
            project(self.rev(EvidenceRay("fourth_wall", "OBSERVED")), now=100)

    def test_missing_commit_fails_closed(self):
        with self.assertRaises(ValueError):
            project(OrbRevision("r0", "", "", ()), now=100)

    def test_all_six_directions_project(self):
        rays = tuple(EvidenceRay(d, "UNKNOWN") for d in sorted(ALLOWED_DIRECTIONS))
        self.assertEqual(len(project(self.rev(*rays), now=100)["rays"]), 6)


if __name__ == "__main__":
    unittest.main()
