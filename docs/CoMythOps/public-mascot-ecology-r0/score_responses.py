#!/usr/bin/env python3
"""Score CoMythOps public mascot ecology blind-comprehension responses.

Input: one JSON object per line, each conforming to response-schema.json.
Output: aggregate JSON only. No participant identity is required or expected.
"""

import json
import sys
from collections import Counter

EXPECTED = {
    "dragon": "SCALE_INFRASTRUCTURE_DISRUPTION",
    "kitten": "CARE_REPAIR_RELATIONAL_NUANCE",
    "turtle": "CONTINUITY_BRANCHING_PERSISTENCE",
    "cloud": "POSSIBILITY_AMBIGUITY_HYPOTHESIS",
}

MASCOTS = tuple(EXPECTED)


def score(rows):
    total = len(rows)
    exact = Counter()
    memorable = Counter()
    confusing = Counter()
    misreads = Counter()
    aggregate_eligible = 0

    for row in rows:
        if row.get("consent_to_aggregate") is True:
            aggregate_eligible += 1

        mappings = row.get("mappings", {})
        for mascot, expected_role in EXPECTED.items():
            roles = mappings.get(mascot, [])
            if expected_role in roles:
                exact[mascot] += 1

        memorable[row.get("most_memorable", "none")] += 1
        confusing[row.get("most_confusing", "none")] += 1

        for flag in row.get("misread_flags", []):
            if flag != "NONE":
                misreads[flag] += 1

    rates = {
        mascot: (exact[mascot] / total if total else None)
        for mascot in MASCOTS
    }

    majority_correct = sum(
        1 for mascot in MASCOTS
        if total and exact[mascot] > total / 2
    )

    pass_candidate = bool(
        total
        and majority_correct >= 3
        and misreads["KITTEN_MERELY_DECORATIVE"] <= total / 2
        and misreads["NATIONALITY_STEREOTYPE"] <= total / 2
        and misreads["MASCOT_AS_AUTHORITY"] <= total / 2
    )

    return {
        "schema": "CoMythOps.PublicMascotComprehensionAggregate.v0.1",
        "state": "OBSERVED_RESPONSES" if total else "NO_RESPONSES",
        "response_count": total,
        "aggregate_consent_count": aggregate_eligible,
        "intended_mapping_rates": rates,
        "majority_correct_mascot_count": majority_correct,
        "most_memorable": dict(memorable),
        "most_confusing": dict(confusing),
        "misread_counts": dict(misreads),
        "candidate_pass": pass_candidate,
        "nonclaims": [
            "PASS_NE_PUBLIC_ADOPTION",
            "MEMORABILITY_NE_CORRECTNESS",
            "SMALL_SAMPLE_NE_GENERAL_POPULATION",
            "SELF_SELECTED_SAMPLE_NE_REPRESENTATIVE_SAMPLE"
        ],
    }


def main():
    rows = []
    for line in sys.stdin:
        line = line.strip()
        if line:
            rows.append(json.loads(line))

    json.dump(score(rows), sys.stdout, indent=2, sort_keys=True)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main()
