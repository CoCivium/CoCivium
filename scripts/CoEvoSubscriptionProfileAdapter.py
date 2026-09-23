from __future__ import annotations

import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def canonical_bytes(obj: Any) -> bytes:
    return (json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest().upper()


def load_json(path: Path) -> dict[str, Any]:
    obj = json.loads(path.read_text(encoding="utf-8-sig"))
    if not isinstance(obj, dict):
        raise ValueError(f"JSON_OBJECT_REQUIRED={path}")
    return obj


def profile_to_subscription(
    catalog: dict[str, Any],
    profile_id: str,
    subscriber_id: str,
    source_ref: str,
) -> dict[str, Any]:
    profiles = catalog.get("profiles")
    if not isinstance(profiles, list):
        raise ValueError("PROFILE_CATALOG_PROFILES_REQUIRED")

    matches = [x for x in profiles if isinstance(x, dict) and x.get("profile_id") == profile_id]
    if len(matches) != 1:
        raise ValueError(f"PROFILE_MATCHES={len(matches)} profile_id={profile_id}")
    profile = matches[0]

    rows: list[dict[str, Any]] = []
    seen: set[str] = set()
    for key, temperature in (("hot", "HOT"), ("warm", "WARM"), ("digest", "DIGEST")):
        values = profile.get(key, [])
        if not isinstance(values, list):
            raise ValueError(f"PROFILE_FIELD_NOT_ARRAY={key}")
        for domain in values:
            if not isinstance(domain, str) or not domain:
                raise ValueError(f"PROFILE_DOMAIN_INVALID={key}")
            if domain in seen:
                raise ValueError(f"PROFILE_DOMAIN_DUPLICATE={domain}")
            seen.add(domain)
            rows.append(
                {
                    "domain": domain,
                    "temperature": temperature,
                    "purpose": f"Derived from CoSession profile {profile_id}",
                    "receiver_need": "Material subscribed deltas only",
                    "target_surfaces": list(profile.get("preferred_repos", [])),
                    "max_context_budget": None,
                }
            )

    if not rows:
        raise ValueError("PROFILE_HAS_NO_SUBSCRIBED_DOMAINS")

    return {
        "subscriber_id": subscriber_id,
        "observed_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "authority_ceiling": "INHERIT_CALLER_AUTHORITY_CEILING__NO_ELEVATION",
        "confidentiality": "PUBLIC",
        "profile_id": profile_id,
        "profile_catalog_ref": source_ref,
        "subscriptions": rows,
        "cursors": [],
        "material_delta_policy": {
            "emit_on_material_change_only": True,
            "dedupe_before_emit": True,
            "quiet_when_no_material_delta": True,
        },
        "pressure_policy": {
            "prefer_digest_over_full_ingest": True,
            "externalize_before_context_overflow": True,
            "human_attention_is_exception_path": True,
        },
        "wake_conditions": [
            "MATERIAL_DOMAIN_DELTA",
            "CURRENTNESS_CURSOR_STALE",
            "SUCCESSOR_RESUME_FAILURE",
            "AUTHORITY_OR_EFFECT_GATE_CHANGE",
            "MATERIAL_CROSS_DOMAIN_COLLISION",
        ],
        "nonclaims": [
            "PROFILE_NE_AUTHORITY",
            "SUBSCRIPTION_NE_PICKUP",
            "SUBSCRIPTION_NE_INTEGRATION",
            "UNLISTED_DOMAIN_NE_IRRELEVANT_FOREVER",
            "CURRENTNESS_FOR_ALL_NE_CONTENT_FOR_ALL",
        ],
    }


def write_new(path: Path, obj: dict[str, Any]) -> str:
    if path.exists():
        raise FileExistsError(f"NO_CLOBBER={path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    raw = canonical_bytes(obj)
    path.write_bytes(raw)
    return sha256_bytes(raw)


def selftest() -> None:
    catalog = {
        "profiles": [
            {
                "profile_id": "CoTheory",
                "hot": ["CoTheoryAll+", "CoInsight+"],
                "warm": ["CoPriMath+"],
                "digest": ["CoHighlight+"],
                "preferred_repos": ["CoCivium", "CoInsights"],
            }
        ]
    }
    out = profile_to_subscription(
        catalog,
        "CoTheory",
        "SELFTEST",
        "CoCivium/CoCivium:ai/session-subscription-profiles.json@test",
    )
    assert len(out["subscriptions"]) == 4
    assert [x["temperature"] for x in out["subscriptions"]] == ["HOT", "HOT", "WARM", "DIGEST"]
    assert len({x["domain"] for x in out["subscriptions"]}) == 4
    assert out["material_delta_policy"]["quiet_when_no_material_delta"] is True

    bad = {
        "profiles": [
            {
                "profile_id": "Bad",
                "hot": ["CoIndex+"],
                "warm": ["CoIndex+"],
                "digest": [],
            }
        ]
    }
    try:
        profile_to_subscription(bad, "Bad", "SELFTEST", "bad")
    except ValueError as exc:
        assert str(exc).startswith("PROFILE_DOMAIN_DUPLICATE=")
    else:
        raise AssertionError("duplicate profile domain not held")

    print("SELFTEST=PASS")
    print("PROFILE_ADAPTATION=PASS")
    print("DUPLICATE_DOMAIN=HOLD")
    print("AUTHORITY_ELEVATION=NONE")


def main() -> int:
    p = argparse.ArgumentParser(
        description="Adapt CoSession subscription profiles into a bounded CoSubscriptionCurrentness object."
    )
    p.add_argument("--catalog", type=Path)
    p.add_argument("--profile-id")
    p.add_argument("--subscriber-id")
    p.add_argument("--source-ref")
    p.add_argument("--out", type=Path)
    p.add_argument("--selftest", action="store_true")
    args = p.parse_args()

    if args.selftest:
        selftest()
        return 0

    if not all([args.catalog, args.profile_id, args.subscriber_id, args.source_ref, args.out]):
        p.error("--catalog --profile-id --subscriber-id --source-ref --out are required unless --selftest")

    catalog = load_json(args.catalog)
    subscription = profile_to_subscription(
        catalog,
        args.profile_id,
        args.subscriber_id,
        args.source_ref,
    )

    # RUNGUARD: source parsed and exact profile resolved before the first write.
    if args.out.exists():
        raise FileExistsError(f"NO_CLOBBER={args.out}")

    sha = write_new(args.out, subscription)
    print("STATE=PASS_COEVO_SUBSCRIPTION_PROFILE_ADAPTER")
    print(f"PROFILE_ID={args.profile_id}")
    print(f"SUBSCRIBER_ID={args.subscriber_id}")
    print(f"SUBSCRIPTIONS={len(subscription['subscriptions'])}")
    print(f"OUTPUT={args.out}")
    print(f"OUTPUT_SHA256={sha}")
    print("AUTHORITY_TRANSFER=NONE")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
