"""CoCarry R0: a browser tab is a projection, not a work custody root.

Pure synthetic state-transition tests. No browser profile modification, tab
closing, cross-provider session access, clipboard reads or remote execution.
"""
from dataclasses import dataclass, replace
import unittest


@dataclass(frozen=True)
class WorkCheckpoint:
    work_id: str
    source_revision: str
    source_hash: str
    custody_ref: str
    pending_work: bool
    receiver_readback: str = ""
    acknowledged_by: str = ""
    stop_requested: bool = False


@dataclass(frozen=True)
class Surface:
    surface_id: str
    browser: str
    work_id: str
    state: str = "OPEN"


def classify(checkpoint, surfaces):
    if not checkpoint.work_id or not checkpoint.source_revision or not checkpoint.source_hash:
        return "INVALID_WORK_POINTER"
    if checkpoint.stop_requested:
        return "STOP_HOLD"
    if not checkpoint.custody_ref:
        return "UNRECOVERABLE_POINTER"
    active = tuple(s for s in surfaces
                   if s.work_id == checkpoint.work_id and s.state == "OPEN")
    if (checkpoint.receiver_readback and checkpoint.acknowledged_by
            and checkpoint.acknowledged_by != checkpoint.work_id):
        effect = "RECEIVER_CLAIM_RECORDED_UNVERIFIED"
    else:
        effect = "NO_RECEIVER_PROOF"
    if checkpoint.pending_work:
        return ("SURFACE_ATTACHED" if active else "HEADLESS_PENDING", effect)
    return ("SURFACE_ATTACHED" if active else "HEADLESS_GRACE", effect)


def close_surface(surface):
    if surface.state != "OPEN":
        return surface
    return replace(surface, state="CLOSED")


def open_surface(browser, checkpoint, *, surface_id):
    if browser not in ("Firefox", "Edge", "OTHER"):
        raise ValueError("unqualified browser label")
    if not checkpoint.custody_ref or not checkpoint.work_id or not checkpoint.source_hash:
        raise ValueError("work custody pointer missing")
    return Surface(surface_id, browser, checkpoint.work_id)


def safe_public_projection(checkpoint, surfaces):
    status = classify(checkpoint, surfaces)
    return {
        "work_id": checkpoint.work_id,
        "source_revision": checkpoint.source_revision,
        "surface_count": sum(s.state == "OPEN" and s.work_id == checkpoint.work_id
                             for s in surfaces),
        "classification": status,
        "private_custody_ref_exposed": False,
        "external_session_accepted": False,
        "runtime_continuity_proven": False,
    }


class BrowserCarryTests(unittest.TestCase):
    def checkpoint(self, **overrides):
        v = dict(work_id="work-r0", source_revision="rev1", source_hash="sha-demo",
                 custody_ref="private:pointer", pending_work=True)
        return WorkCheckpoint(**{**v, **overrides})

    def test_tab_close_preserves_durable_work_object(self):
        c = self.checkpoint()
        edge = Surface("edge1", "Edge", c.work_id)
        self.assertEqual(classify(c, (close_surface(edge),))[0], "HEADLESS_PENDING")
        self.assertTrue(c.pending_work)

    def test_firefox_rebind_does_not_change_work_revision(self):
        c = self.checkpoint()
        edge = Surface("edge1", "Edge", c.work_id)
        ff = open_surface("Firefox", c, surface_id="ff1")
        p = safe_public_projection(c, (close_surface(edge), ff))
        self.assertEqual(p["classification"][0], "SURFACE_ATTACHED")
        self.assertEqual(p["source_revision"], "rev1")
        self.assertEqual(p["surface_count"], 1)

    def test_many_tabs_do_not_create_many_workers(self):
        c = self.checkpoint()
        tabs = tuple(Surface(str(i), "Edge", c.work_id) for i in range(1000))
        p = safe_public_projection(c, tabs)
        self.assertEqual(p["surface_count"], 1000)
        self.assertFalse(p["runtime_continuity_proven"])

    def test_unseen_sessions_are_not_inventoried(self):
        c = self.checkpoint()
        self.assertEqual(safe_public_projection(c, ())["surface_count"], 0)

    def test_missing_custody_blocks_new_browser_binding(self):
        c = self.checkpoint(custody_ref="")
        with self.assertRaises(ValueError):
            open_surface("Firefox", c, surface_id="f1")
        self.assertEqual(classify(c, ()), "UNRECOVERABLE_POINTER")

    def test_private_pointer_is_not_published(self):
        c = self.checkpoint()
        p = safe_public_projection(c, ())
        self.assertNotIn("custody_ref", p)
        self.assertNotIn("private:pointer", str(p))

    def test_closed_all_tabs_does_not_prove_service_dead(self):
        c = self.checkpoint(pending_work=False)
        self.assertEqual(classify(c, ()), ("HEADLESS_GRACE", "NO_RECEIVER_PROOF"))

    def test_stop_survives_surface_changes(self):
        c = self.checkpoint(stop_requested=True)
        self.assertEqual(classify(c, (Surface("f", "Firefox", c.work_id),)), "STOP_HOLD")

    def test_receiver_self_claim_never_proves_effect(self):
        c = self.checkpoint(receiver_readback="claimed", acknowledged_by="work-r0")
        self.assertEqual(classify(c, ())[1], "NO_RECEIVER_PROOF")

    def test_receiver_label_alone_is_not_authentication(self):
        c = self.checkpoint(receiver_readback="claimed", acknowledged_by="peer")
        self.assertEqual(classify(c, ())[1], "RECEIVER_CLAIM_RECORDED_UNVERIFIED")

    def test_other_work_tab_does_not_keep_this_work_attached(self):
        c = self.checkpoint()
        self.assertEqual(classify(c, (Surface("another", "Firefox", "different-work"),))[0],
                         "HEADLESS_PENDING")


if __name__ == "__main__":
    unittest.main()
