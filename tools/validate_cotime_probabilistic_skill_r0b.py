#!/usr/bin/env python3
import hashlib
import json
import subprocess
from fractions import Fraction
from pathlib import Path

P = Path("fixtures/cotime/cotime_probabilistic_skill_r0b.json")
SCALE = 10000

def fail(code):
    raise SystemExit(code)

def git_blob(path):
    return subprocess.check_output(["git", "rev-parse", f"HEAD:{path}"], text=True).strip()

def canonical_sha(obj):
    return hashlib.sha256(
        json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest().upper()

def frac_obj(x):
    return {"numerator": x.numerator, "denominator": x.denominator}

def brier(rows, field):
    if not rows:
        fail("FAIL_EMPTY_SCORE_SET")
    total = Fraction(0, 1)
    for r in rows:
        p = r[field]
        y = r["outcome"] * SCALE
        total += Fraction((p - y) ** 2, SCALE ** 2)
    return total / len(rows)

def mean_bp(rows, field):
    return Fraction(sum(r[field] for r in rows), len(rows))

def main():
    d = json.loads(P.read_text(encoding="utf-8"))
    src = d["source_bindings"]

    if git_blob(src["calibration_fixture_path"]) != src["calibration_fixture_blob_sha"]:
        fail("FAIL_CALIBRATION_SOURCE_BIND")
    if git_blob(src["precommitment_fixture_path"]) != src["precommitment_fixture_blob_sha"]:
        fail("FAIL_PRECOMMITMENT_SOURCE_BIND")

    forecasts = d["forecasts"]
    if len({f["id"] for f in forecasts}) != len(forecasts):
        fail("FAIL_DUPLICATE_FORECAST_ID")

    for f in forecasts:
        for field in ("candidate_probability_bp", "baseline_probability_bp", "challenger_probability_bp"):
            p = f[field]
            if not isinstance(p, int) or not 0 <= p <= SCALE:
                fail("FAIL_PROBABILITY_RANGE:" + f["id"] + ":" + field)

    scored = []
    retained_unscored = []
    for f in forecasts:
        if f["status"] == "RESOLVED_VALID":
            if f["outcome"] not in (0, 1):
                fail("FAIL_RESOLVED_OUTCOME:" + f["id"])
            if f["outcome_observed_at"] is None or not (f["registered_at"] < f["outcome_observed_at"]):
                fail("FAIL_PRECOMMITMENT_ORDER:" + f["id"])
            scored.append(f)
        elif f["status"] in {"UNRESOLVED", "INVALIDATED_BY_ASSUMPTION_CHANGE"}:
            retained_unscored.append(f)
        else:
            fail("FAIL_UNKNOWN_STATUS:" + f["id"])

    exp = d["expected"]
    if len(forecasts) != exp["registered_count"]:
        fail("FAIL_REGISTERED_COUNT")
    if len(scored) != exp["scored_count"]:
        fail("FAIL_SCORED_COUNT")
    if len(retained_unscored) != exp["retained_unscored_count"]:
        fail("FAIL_RETAINED_UNSCORED_COUNT")

    candidate = brier(scored, "candidate_probability_bp")
    baseline = brier(scored, "baseline_probability_bp")
    challenger = brier(scored, "challenger_probability_bp")

    if frac_obj(candidate) != exp["candidate_brier"]:
        fail("FAIL_CANDIDATE_BRIER:" + str(candidate))
    if frac_obj(baseline) != exp["baseline_brier"]:
        fail("FAIL_BASELINE_BRIER:" + str(baseline))
    if frac_obj(challenger) != exp["challenger_brier"]:
        fail("FAIL_CHALLENGER_BRIER:" + str(challenger))

    if baseline == 0:
        fail("FAIL_ZERO_BASELINE_BRIER")
    skill = Fraction(1, 1) - candidate / baseline
    if frac_obj(skill) != exp["candidate_brier_skill_vs_baseline"]:
        fail("FAIL_SKILL_SCORE:" + str(skill))

    positives = [f for f in scored if f["outcome"] == 1]
    negatives = [f for f in scored if f["outcome"] == 0]
    pos_mean = mean_bp(positives, "candidate_probability_bp")
    neg_mean = mean_bp(negatives, "candidate_probability_bp")
    if pos_mean.denominator != 1 or pos_mean.numerator != exp["candidate_positive_mean_probability_bp"]:
        fail("FAIL_POSITIVE_MEAN")
    if neg_mean.denominator != 1 or neg_mean.numerator != exp["candidate_negative_mean_probability_bp"]:
        fail("FAIL_NEGATIVE_MEAN")

    discriminates = pos_mean > neg_mean
    beats_baseline = candidate < baseline
    challenger_worse = challenger > baseline
    if discriminates != exp["candidate_discriminates_in_fixture"]:
        fail("FAIL_DISCRIMINATION_EXPECTATION")
    if beats_baseline != exp["candidate_beats_baseline_in_fixture"]:
        fail("FAIL_BASELINE_EXPECTATION")
    if challenger_worse != exp["challenger_worse_than_baseline_in_fixture"]:
        fail("FAIL_CHALLENGER_EXPECTATION")

    if len(d["better_questions"]) != 8:
        fail("FAIL_BETTER_QUESTION_COUNT")

    head = subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    out = {
        "STATE": "PASS_COTIME_PROBABILISTIC_SKILL_R0B",
        "checked_out_head_sha": head,
        "fixture_semantic_sha256": canonical_sha(d),
        "registered_count": len(forecasts),
        "scored_count": len(scored),
        "retained_unscored_count": len(retained_unscored),
        "candidate_brier": frac_obj(candidate),
        "baseline_brier": frac_obj(baseline),
        "challenger_brier": frac_obj(challenger),
        "candidate_brier_skill_vs_baseline": frac_obj(skill),
        "candidate_positive_mean_probability_bp": int(pos_mean),
        "candidate_negative_mean_probability_bp": int(neg_mean),
        "candidate_discriminates_in_fixture": discriminates,
        "candidate_beats_baseline_in_fixture": beats_baseline,
        "challenger_worse_than_baseline_in_fixture": challenger_worse,
        "better_question_count": len(d["better_questions"]),
        "effect_authority_change": 0,
        "real_predictive_skill_claimed": False,
        "financial_effect_authority": False,
        "nonclaims": d["nonclaims"]
    }
    print(json.dumps(out, separators=(",", ":")))

if __name__ == "__main__":
    main()
