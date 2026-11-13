"""CoOmni R0: source-bound cross-render ACK qualification.

This module is a synthetic protocol fixture, NOT a WhatsApp/ChatGPT/Ollama
bridge. A prose claim of broadcast or identical seed labels does not prove
a receiver independently reconstructed the exact work object.
"""
from dataclasses import dataclass
import unittest


@dataclass(frozen=True)
class Seed:
    work_id: str
    source_sha256: str
    revision: str
    permissions: str = "READ_ONLY"


@dataclass(frozen=True)
class Render:
    render_id: str
    medium: str
    expected_work_id: str
    advertised_revision: str
    observed_sha256: str = ""
    receiver_readback_ref: str = ""
    receiver_identity: str = ""
    receiver_distinct: bool = False
    source_access_verified: bool = False
    boundary: str = "VIEW_ONLY"
    status: str = "PROPOSED"


def qualify(seed, render):
    """Never let version strings, broadcast counts or claimed ACKs green-sync."""
    if not seed.work_id or not seed.source_sha256 or not seed.revision:
        return "SEED_INVALID"
    if render.expected_work_id != seed.work_id:
        return "WORK_ID_SPLIT"
    if render.advertised_revision != seed.revision:
        return "VERSION_SPLIT"
    if not render.observed_sha256:
        return "UNOBSERVED"
    if render.observed_sha256 != seed.source_sha256:
        return "SOURCE_SPLIT"
    if not render.source_access_verified:
        return "SOURCE_ACCESS_UNVERIFIED"
    if not render.receiver_readback_ref or not render.receiver_identity or not render.receiver_distinct:
        return "RECEIVER_UNVERIFIED"
    if render.status != "RECEIVER_READBACK":
        return "ACK_NOT_PROVEN"
    return "SYNTHETIC_ACK_QUALIFIED"


def federation(seed, renders):
    """Explicit scoped membership; unseen sessions can never count as synced."""
    if not renders:
        return {"status": "NO_VERIFIED_RENDER_MEMBERSHIP", "qualified": 0, "total": 0}
    states = {r.render_id: qualify(seed, r) for r in renders}
    qualified = sum(s == "SYNTHETIC_ACK_QUALIFIED" for s in states.values())
    # Even all candidate test renders passing is not real cross-provider sync.
    return {"status": "SYNTHETIC_CONVERGED" if qualified == len(renders) else "SPLIT_OR_UNVERIFIED",
            "qualified": qualified, "total": len(renders), "states": states,
            "actual_provider_sync_proven": False}


class CoOmniFederationTests(unittest.TestCase):
    seed = Seed("work-r0", "sha-test", "rev-r0")

    def render(self, **changes):
        values = dict(render_id="firefox", medium="browser",
                      expected_work_id="work-r0", advertised_revision="rev-r0",
                      observed_sha256="sha-test", receiver_readback_ref="test-ref",
                      receiver_identity="independent-test-receiver", receiver_distinct=True,
                      source_access_verified=True, status="RECEIVER_READBACK")
        return Render(**{**values, **changes})

    def test_exact_synthetic_receiver_qualifies_only_test_scope(self):
        self.assertEqual(qualify(self.seed, self.render()), "SYNTHETIC_ACK_QUALIFIED")
        self.assertFalse(federation(self.seed, (self.render(),))["actual_provider_sync_proven"])

    def test_repeated_version_label_not_sync(self):
        self.assertEqual(qualify(self.seed, self.render(observed_sha256="")), "UNOBSERVED")

    def test_split_version_detected(self):
        self.assertEqual(qualify(self.seed, self.render(advertised_revision="v8.44")),
                         "VERSION_SPLIT")

    def test_split_source_detected(self):
        self.assertEqual(qualify(self.seed, self.render(observed_sha256="other")),
                         "SOURCE_SPLIT")

    def test_other_work_cannot_ack(self):
        self.assertEqual(qualify(self.seed, self.render(expected_work_id="another")),
                         "WORK_ID_SPLIT")

    def test_claimed_meta_ai_ack_has_no_verified_receiver(self):
        r = self.render(medium="WhatsApp", receiver_distinct=False,
                        status="CLAIMED_ACK")
        self.assertEqual(qualify(self.seed, r), "RECEIVER_UNVERIFIED")

    def test_unverified_source_access_blocks(self):
        self.assertEqual(qualify(self.seed, self.render(source_access_verified=False)),
                         "SOURCE_ACCESS_UNVERIFIED")

    def test_held_candidate_cannot_count_as_ack(self):
        self.assertEqual(qualify(self.seed, self.render(status="PROPOSED")),
                         "ACK_NOT_PROVEN")

    def test_no_render_census_is_not_omni(self):
        self.assertEqual(federation(self.seed, ())["status"],
                         "NO_VERIFIED_RENDER_MEMBERSHIP")

    def test_partial_fanout_remains_split(self):
        a = self.render(render_id="firefox")
        b = self.render(render_id="whatsapp", receiver_readback_ref="")
        result = federation(self.seed, (a, b))
        self.assertEqual(result["qualified"], 1)
        self.assertEqual(result["status"], "SPLIT_OR_UNVERIFIED")

    def test_all_test_renderers_remain_synthetic(self):
        a = self.render(render_id="browser")
        b = self.render(render_id="headless", medium="test-process")
        f = federation(self.seed, (a, b))
        self.assertEqual(f["status"], "SYNTHETIC_CONVERGED")
        self.assertFalse(f["actual_provider_sync_proven"])

    def test_draft_email_not_broadcast_receipt(self):
        self.assertEqual(qualify(self.seed, self.render(
            render_id="outreach-draft", medium="email_draft",
            status="DRAFT", receiver_readback_ref="")), "RECEIVER_UNVERIFIED")


if __name__ == "__main__":
    unittest.main()
