"""CoOrb R0B projection semantics. Pure in-memory fixtures; not deployed UX."""
from dataclasses import dataclass, replace
import hashlib
import json
import unittest

@dataclass(frozen=True)
class Strand:
    id: str
    kind: str
    epistemic: str
    payload: str
    visible_to: tuple = ("public",)
    source_ref: str = ""
    forecast_horizon: int = 0
    observed_receipt: str = ""
    authorized_to_send: bool = False

@dataclass(frozen=True)
class Orb:
    work_id: str
    revision: int
    strands: tuple
    predecessor: str = ""

    def digest(self):
        canonical = {"work_id":self.work_id, "revision":self.revision,
                     "strands":[vars(s) for s in self.strands], "predecessor":self.predecessor}
        return hashlib.sha256(json.dumps(canonical,sort_keys=True).encode()).hexdigest()

    def successor(self, strands):
        if tuple(strands) == self.strands:
            return self  # cosmetic redraw is never a semantic revision
        return Orb(self.work_id, self.revision+1, tuple(strands), self.digest())

def project(orb, receiver, renderer, now, verifier_receipts=()):
    """Only two renderers are supported; output data is intentionally isomorphic."""
    if renderer not in ("map", "orb"):
        raise ValueError("unknown renderer")
    # Restricted strands do not contribute counts, IDs, glow or any visible metadata.
    visible=[]
    verified=set(verifier_receipts)  # trusted verifier input, never model-generated
    for strand in orb.strands:
        if receiver not in strand.visible_to:
            continue
        if strand.epistemic not in ("OBSERVED","PREDICTED","SCENARIO","UNKNOWN"):
            raise ValueError("invalid epistemic class")
        if strand.kind == "OUTWARD" and not strand.authorized_to_send:
            # Showing a proposed effect must never imply a send occurred.
            delivery="PROPOSAL_ONLY"
        else:
            delivery="NO_SEND_PERFORMED"
        if strand.epistemic == "PREDICTED":
            state="PREDICTED"  # time passing cannot turn it into an observation
        elif strand.forecast_horizon and now > strand.forecast_horizon:
            state="STALE"
        else:
            state=strand.epistemic
        visible.append({"id":strand.id,"kind":strand.kind,"state":state,
                        "source_ref":strand.source_ref,"delivery":delivery,
                        "receiver_ack":bool(strand.observed_receipt and strand.observed_receipt in verified)})
    # A receiver-visible projection has its own version. Do not disclose the
    # full source digest, global revision or predecessor: each can reveal
    # the existence or timing of changes to receiver-ineligible strands.
    scoped={"work_id":orb.work_id,"strands":visible}
    projection_hash=hashlib.sha256(
        json.dumps(scoped,sort_keys=True).encode()).hexdigest()
    return {"renderer":renderer,"work_id":orb.work_id,
            "projection_hash":projection_hash,"strands":visible,
            "visible_count":len(visible)}

class CoOrbTwoView(unittest.TestCase):
    def setUp(self):
        self.a=Strand("a","INWARD","OBSERVED","measurement",
                      source_ref="receipt:a")
        self.p=Strand("p","TEMPORAL","PREDICTED","future",
                      source_ref="scenario:p",forecast_horizon=20)
        self.out=Strand("out","OUTWARD","UNKNOWN","proposal")
        self.secret=Strand("secret","INWARD","OBSERVED","restricted",
                           visible_to=("private",),source_ref="secret:1")
        self.orb=Orb("work-1",1,(self.a,self.p,self.out,self.secret))

    def test_two_views_share_identity_and_epistemic_classes(self):
        x=project(self.orb,"public","orb",10)
        y=project(self.orb,"public","map",10)
        self.assertEqual(x["projection_hash"],y["projection_hash"])
        self.assertEqual(x["strands"],y["strands"])
        self.assertEqual(x["visible_count"],3)

    def test_cosmetic_redraw_no_semantic_version(self):
        self.assertIs(self.orb.successor(self.orb.strands),self.orb)

    def test_changed_evidence_advances_version_and_predecessor(self):
        changed=replace(self.a,payload="new independently observed value",
                        observed_receipt="receiver:verified-new")
        nxt=self.orb.successor((changed,self.p,self.out,self.secret))
        self.assertEqual(nxt.revision,2)
        self.assertEqual(nxt.predecessor,self.orb.digest())
        self.assertNotEqual(nxt.digest(),self.orb.digest())

    def test_forecast_never_auto_promotes(self):
        states=[s["state"] for s in project(self.orb,"public","orb",100)["strands"]]
        self.assertEqual(states[1],"PREDICTED")

    def test_outbound_proposal_has_no_delivery_claim(self):
        o=project(self.orb,"public","orb",10)["strands"][2]
        self.assertEqual(o["delivery"],"PROPOSAL_ONLY")
        self.assertFalse(o["receiver_ack"])

    def test_stale_observation_labeled_not_erased(self):
        aged=replace(self.a,forecast_horizon=5)
        nxt=self.orb.successor((aged,self.p,self.out,self.secret))
        s=project(nxt,"public","map",10)["strands"][0]
        self.assertEqual(s["state"],"STALE")

    def test_private_strand_not_counted_or_rendered(self):
        public=project(self.orb,"public","orb",10)
        private=project(self.orb,"private","orb",10)
        self.assertEqual(public["visible_count"],3)
        self.assertEqual(private["visible_count"],1)
        self.assertNotIn("secret",str(public["strands"]))

    def test_private_only_change_has_no_public_delta(self):
        changed=replace(self.secret,payload="private new fact",source_ref="secret:2")
        nxt=self.orb.successor((self.a,self.p,self.out,changed))
        before=project(self.orb,"public","orb",10)
        after=project(nxt,"public","orb",10)
        self.assertEqual(before,after)
        self.assertNotIn("source_hash",before)
        self.assertNotIn("revision",before)
        self.assertNotIn("predecessor",before)

    def test_receipt_string_cannot_claim_receiver_ack(self):
        changed=replace(self.a,observed_receipt="self:claimed")
        nxt=self.orb.successor((changed,self.p,self.out,self.secret))
        evidence=project(nxt,"public","orb",10)["strands"][0]
        self.assertFalse(evidence["receiver_ack"])

    def test_separately_supplied_verifier_ref_required(self):
        changed=replace(self.a,observed_receipt="receiver:attested")
        nxt=self.orb.successor((changed,self.p,self.out,self.secret))
        without=project(nxt,"public","orb",10)["strands"][0]
        with_proof=project(nxt,"public","orb",10,
                           verifier_receipts=("receiver:attested",))["strands"][0]
        self.assertFalse(without["receiver_ack"])
        self.assertTrue(with_proof["receiver_ack"])

    def test_bad_renderer_fails_closed(self):
        with self.assertRaises(ValueError):
            project(self.orb,"public","unrecognized",10)

    def test_bad_epistemic_class_fails_closed(self):
        bad=replace(self.a,epistemic="VERIFIED_BY_MODEL")
        with self.assertRaises(ValueError):
            project(self.orb.successor((bad,)),"public","orb",10)

if __name__=="__main__":
    unittest.main(verbosity=2)
