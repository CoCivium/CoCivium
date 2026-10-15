#!/usr/bin/env python3
import json
from pathlib import Path
P=Path("fixtures/relations/coall_bounded_discovery_projection_r0.json")
def main():
 d=json.loads(P.read_text())
 checks=[
  d["metaphysics"]["established_fact"] is False,
  d["virtual_cli"]["default_user_visible"] is False,
  d["virtual_cli"]["auditable"] is True,
  d["compressed_projection"]["critical_meaning_symbol_only"] is False,
  d["compressed_projection"]["expandable_meaning_required"] is True,
  d["inventory"]["scope_required"] is True,
  d["convergence"]["endless_compute_allowed"] is False,
  d["cocheap"]["generation_cost_implies_verification_cost"] is False,
  d["cocheap"]["summonable_implies_useful"] is False,
  d["compute"]["x2_required_root"] is False,
  d["compute"]["single_new_remote_root_allowed"] is False,
  d["outreach"]["candidate_receiver_implies_contact_authority"] is False,
  d["budget"]["crypto_balance_inferred_without_wallet_evidence"] is False,
  d["launch"]["countdown_implies_release_authority"] is False,
  d["runtime_effect"] is False and d["public_effect"] is False
 ]
 if not all(checks): raise SystemExit("FAIL:bounded discovery/projection contract")
 print("PASS: CoAll bounded discovery/projection ecology R0")
if __name__=="__main__": main()
