#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EVOLUTION = ROOT / "docs" / "Evolution"

DOMAINS = EVOLUTION / "coall-evolution-domains-r1.json"
REPOS = EVOLUTION / "coall-repo-role-currentness-r1.json"
HIGHLIGHTS = EVOLUTION / "coall-highlight-registry-r0.json"
FABRIC = EVOLUTION / "COALL_GITHUB_EVOLUTION_FABRIC_R1.md"
README = EVOLUTION / "README.md"
DELTA_SCHEMA = ROOT / "schemas" / "coevo-delta-v0.1.schema.json"
DELTA_DIR = EVOLUTION / "deltas"

REQUIRED_DOMAIN_IDS = {
    "strategy","insights","theory","semantics","index","operations",
    "myth_metaphor_humour","formal_substrate","ux_surface",
    "highlight_ecology","session_lifecycle","pressure_capacity",
    "self_model_and_objective","time_prediction","protocol_ecology",
    "execution_surface","public_release","rails_governance"
}

REQUIRED_RAILS = {
    "ALL_SESSIONS_CAN_CONTRIBUTE_NE_ALL_SESSIONS_MUTATE_ALL_SURFACES",
    "CURRENTNESS_FOR_ALL_NE_CONTENT_FOR_ALL",
    "DOMAIN_NE_REPOSITORY",
    "REPOSITORY_NE_ONTOLOGY",
    "README_NE_CANON",
    "HIGHLIGHT_NE_CANON",
    "NO_NEWEST_WINS"
}

REQUIRED_REPOS = {
    "CoCivium/CoCivium","CoCivium/CoInsights","CoCivium/GIBindex",
    "CoCivium/MasterPlan","CoCivium/CoSteward","CoCivium/CoRails",
    "CoCivium/CoStacks","CoCivium/CoShareHub","CoCivium/CoAura",
    "CoCivium/CoFutures"
}

ALLOWED_MUTATIONS = {
    "OBSERVE","PROPOSE","BRANCH_MUTATE","REVIEW_CHALLENGE",
    "MERGE_LOW_EFFECT","EFFECT_GATED"
}
ALLOWED_EPISTEMIC = {
    "OBSERVED","INFERRED","HYPOTHESIS","PREDICTED","PLANNED","PREFERRED",
    "METAPHORICAL","MYTHIC","HUMOROUS","COUNTERFACTUAL","UNKNOWN"
}
ALLOWED_CONFIDENTIALITY = {"PUBLIC","PRIVATE","RESTRICTED","UNKNOWN"}

def load_json(path: Path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)

def require(cond: bool, msg: str, errors: list[str]):
    if not cond:
        errors.append(msg)

def main() -> int:
    errors: list[str] = []
    files = [DOMAINS, REPOS, HIGHLIGHTS, FABRIC, README, DELTA_SCHEMA]
    for p in files:
        require(p.is_file(), f"MISSING_FILE:{p.relative_to(ROOT)}", errors)
    require(DELTA_DIR.is_dir(), "MISSING_DELTA_DIR", errors)
    if errors:
        print("\n".join(errors))
        return 2

    domains = load_json(DOMAINS)
    repos = load_json(REPOS)
    highlights = load_json(HIGHLIGHTS)
    delta_schema = load_json(DELTA_SCHEMA)
    fabric = FABRIC.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")

    domain_rows = domains.get("domains", [])
    ids = [r.get("id") for r in domain_rows]
    require(len(ids) == len(set(ids)), "DUPLICATE_DOMAIN_ID", errors)
    require(REQUIRED_DOMAIN_IDS.issubset(set(ids)), "MISSING_REQUIRED_DOMAIN_ID", errors)
    require(len(domain_rows) >= 18, "DOMAIN_REGISTRY_TOO_SMALL", errors)
    require(REQUIRED_RAILS.issubset(set(domains.get("principles", []))), "MISSING_CORE_DOMAIN_RAIL", errors)

    tiers = domains.get("subscription_model", {}).get("tiers", {})
    require(set(tiers) == {"HOT","WARM","DIGEST","SLEEP"}, "BAD_SUBSCRIPTION_TIERS", errors)

    for row in domain_rows:
        require(bool(row.get("labels")), f"DOMAIN_NO_LABELS:{row.get('id')}", errors)
        require(bool(row.get("relations")), f"DOMAIN_NO_RELATIONS:{row.get('id')}", errors)
        require(bool(row.get("candidate_homes")), f"DOMAIN_NO_HOME:{row.get('id')}", errors)
        require(row.get("default_mutation") in ALLOWED_MUTATIONS, f"BAD_MUTATION:{row.get('id')}", errors)

    repo_rows = repos.get("repositories", [])
    repo_names = [r.get("repo") for r in repo_rows]
    require(len(repo_names) == len(set(repo_names)), "DUPLICATE_REPO", errors)
    require(repos.get("repo_count") == len(repo_rows), "REPO_COUNT_MISMATCH", errors)
    require(REQUIRED_REPOS.issubset(set(repo_names)), "MISSING_REQUIRED_REPO", errors)
    for row in repo_rows:
        require(row.get("visibility") in {"public","private"}, f"BAD_VISIBILITY:{row.get('repo')}", errors)
        require(bool(row.get("default_branch")), f"MISSING_DEFAULT_BRANCH:{row.get('repo')}", errors)
        require(bool(row.get("role")), f"MISSING_REPO_ROLE:{row.get('repo')}", errors)

    dims = highlights.get("scoring_dimensions", [])
    require(len(dims) >= 8, "HIGHLIGHT_DIMENSIONS_TOO_SMALL", errors)
    hitems = highlights.get("items", [])
    hids = [x.get("id") for x in hitems]
    require(len(hids) == len(set(hids)), "DUPLICATE_HIGHLIGHT_ID", errors)
    require(len(hitems) >= 6, "HIGHLIGHT_SEED_TOO_SMALL", errors)
    for item in hitems:
        require(bool(item.get("source_refs")), f"HIGHLIGHT_NO_SOURCE:{item.get('id')}", errors)
        require(bool(item.get("relations")), f"HIGHLIGHT_NO_RELATIONS:{item.get('id')}", errors)

    required_delta = set(delta_schema.get("required", []))
    expected_required = {
        "delta_id","session_id","observed_at","domain","subject","relation",
        "epistemic_class","source_refs","target_surfaces","mutation_class",
        "authority_ceiling","confidentiality","next_receiver"
    }
    require(expected_required.issubset(required_delta), "DELTA_SCHEMA_REQUIRED_FIELDS_REGRESSED", errors)

    delta_files = sorted(p for p in DELTA_DIR.glob("*.json") if p.is_file())
    require(bool(delta_files), "NO_COEVO_DELTA_EXEMPLAR", errors)
    seen_delta_ids: set[str] = set()
    known_domains = set(ids)
    for path in delta_files:
        d = load_json(path)
        missing = [k for k in expected_required if k not in d]
        require(not missing, f"DELTA_MISSING_FIELDS:{path.name}:{','.join(sorted(missing))}", errors)
        did = d.get("delta_id")
        require(bool(did), f"DELTA_EMPTY_ID:{path.name}", errors)
        require(did not in seen_delta_ids, f"DUPLICATE_DELTA_ID:{did}", errors)
        seen_delta_ids.add(did)
        require(d.get("epistemic_class") in ALLOWED_EPISTEMIC, f"DELTA_BAD_EPISTEMIC:{path.name}", errors)
        require(d.get("mutation_class") in ALLOWED_MUTATIONS, f"DELTA_BAD_MUTATION:{path.name}", errors)
        require(d.get("confidentiality") in ALLOWED_CONFIDENTIALITY, f"DELTA_BAD_CONFIDENTIALITY:{path.name}", errors)
        require(bool(d.get("source_refs")), f"DELTA_NO_SOURCE_REFS:{path.name}", errors)
        require(bool(d.get("target_surfaces")), f"DELTA_NO_TARGETS:{path.name}", errors)
        require(bool(d.get("authority_ceiling")), f"DELTA_NO_AUTHORITY_CEILING:{path.name}", errors)
        for domain in d.get("domain", []):
            require(domain in known_domains, f"DELTA_UNKNOWN_DOMAIN:{path.name}:{domain}", errors)

    for phrase in [
        "GLOBAL_RELATIONAL_RICHNESS_CAN_GROW__PER_SESSION_FOREGROUND_SHOULD_STAY_BOUNDED",
        "RELATION_CAN_RELATE_TO_RELATION__RECURSION_REQUIRES_STOP_RULES",
        "PARALLELIZE_UNCERTAINTY__SERIALIZE_AUTHORITY",
        "GITHUB_WRITE_ACCESS_NE_GLOBAL_AUTHORITY",
        "MERGE_NE_CANON",
        "PUBLIC_NE_VALIDATED"
    ]:
        require(phrase in fabric, f"FABRIC_MISSING_RAIL:{phrase}", errors)

    for path_name in [
        "COALL_GITHUB_EVOLUTION_FABRIC_R0.md",
        "COALL_GITHUB_EVOLUTION_FABRIC_R1.md",
        "coall-evolution-domains-r1.json",
        "coall-repo-role-currentness-r1.json",
        "coall-highlight-registry-r0.json",
        "deltas/"
    ]:
        require(path_name in readme, f"README_MISSING_LINK:{path_name}", errors)

    if errors:
        print(f"HOLD: {len(errors)} validation error(s)")
        for e in errors:
            print(" -", e)
        return 1

    print("PASS_COALL_GITHUB_EVOLUTION_R1")
    print(f"domains={len(domain_rows)}")
    print(f"repos={len(repo_rows)}")
    print(f"highlights={len(hitems)}")
    print(f"coevo_deltas={len(delta_files)}")
    print("subscription_tiers=HOT,WARM,DIGEST,SLEEP")
    print("authority=UNCHANGED")
    print("canon=UNPROVEN")
    print("runtime=UNPROVEN")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
