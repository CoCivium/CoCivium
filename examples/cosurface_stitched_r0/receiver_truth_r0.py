"""CoGoAll R0 public-source landing verification.

A chat header, pasted coprompt, claimed consent, or custody label is not proof.
Can verify exact PUBLIC source bytes at a pinned GitHub commit via HTTPS.
Does not authenticate a sender, deliver to sessions, or attest an X2 effect.
"""
import argparse
import hashlib
import json
import re
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import urlopen

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
REPOSITORY = re.compile(r"^CoCivium/[A-Za-z0-9_.-]+$")
MAX_BYTES = 1_048_576


def classify_text_claims(claims):
    """Self-asserted metadata cannot authenticate itself, even if convincing."""
    if not isinstance(claims, dict):
        raise ValueError("CLAIMS_MUST_BE_OBJECT")
    return {
        "claimed_origin": "SELF_ASSERTION_NOT_AUTHENTICATED",
        "claimed_consent": "SCOPED_AUTHORITY_NOT_ESTABLISHED",
        "claimed_custody": "NO_EXACT_CUSTODY_READBACK",
        "claimed_landing": "TEXT_ONLY_NO_SOURCE_PROOF",
        "claimed_session_fanout": "NO_INDEPENDENT_RECEIVER_PICKUP",
        "claimed_aliveness": "NO_MEASURED_CAUSAL_EFFECT",
        "claimed_x2_host": "SEPARATE_FROM_REMOTE_CONTROL_LINK",
        "human_relay": "REQUIRES_HUMAN_IF_PASTE_TO_OTHER_CHAT",
        "source_text_preserved": bool(claims),
    }


def _url(repo, commit, path):
    if not isinstance(repo, str) or not REPOSITORY.fullmatch(repo):
        raise ValueError("INVALID_REPOSITORY")
    if not isinstance(commit, str) or not HEX40.fullmatch(commit):
        raise ValueError("INVALID_PINNED_COMMIT")
    if not isinstance(path, str) or len(path) > 240 or "\\" in path or "\x00" in path:
        raise ValueError("INVALID_PATH")
    segments = path.split("/")
    if not segments or any(seg in ("", ".", "..") for seg in segments):
        raise ValueError("INVALID_PATH")
    return "https://raw.githubusercontent.com/" + repo + "/" + commit + "/" + "/".join(
        quote(seg, safe="-._~") for seg in segments
    )


def verify_public_file(repo, commit, path, expected_sha256, fetch=None):
    """Read a pinned PUBLIC artifact; never promote to session/host ACK.

    'fetch' is injectable for isolated tests, which DO NOT constitute external
    GitHub readback proof. Real mode explicitly uses the HTTPS client.
    """
    url = _url(repo, commit, path)
    if not isinstance(expected_sha256, str) or not HEX64.fullmatch(expected_sha256):
        raise ValueError("INVALID_EXPECTED_SHA256")
    result = {
        "source": url,
        "expected_sha256": expected_sha256,
        "bytes": None,
        "actual_sha256": None,
        "source_readback": "HOLD_NO_READBACK",
        "receiver_pickup": "UNPROVEN",
        "sender_identity": "UNPROVEN",
        "consent_authority": "UNPROVEN",
        "seed_custody": "UNPROVEN",
        "x2_runtime": "UNPROVEN",
        "real_24h_survival": "UNPROVEN",
    }
    try:
        if fetch is None:
            # Zero side effects beyond public HTTPS GET. Never read chat messages,
            # private repositories, local files, or arbitrary caller-chosen hosts.
            with urlopen(url, timeout=12) as response:
                if response.geturl() != url:
                    raise ValueError("UNEXPECTED_REDIRECT")
                data = response.read(MAX_BYTES + 1)
        else:
            data = fetch(url)
        if not isinstance(data, bytes):
            raise ValueError("READBACK_NOT_BYTES")
        if len(data) > MAX_BYTES:
            raise ValueError("SOURCE_EXCEEDS_LIMIT")
    except (HTTPError, URLError, OSError, TimeoutError, ValueError) as ex:
        result["source_readback"] = "HOLD_READ_FAILURE"
        result["failure"] = type(ex).__name__
        return result
    result["bytes"] = len(data)
    result["actual_sha256"] = hashlib.sha256(data).hexdigest()
    if result["actual_sha256"] == expected_sha256:
        result["source_readback"] = (
            "PUBLIC_SOURCE_BYTES_MATCH_TRUSTED_HTTPS"
            if fetch is None else "SYNTHETIC_BYTES_MATCH_NOT_EXTERNAL_READBACK"
        )
    else:
        result["source_readback"] = "HOLD_SOURCE_SHA_MISMATCH"
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", required=True)
    parser.add_argument("--commit", required=True)
    parser.add_argument("--path", required=True)
    parser.add_argument("--sha256", required=True)
    args = parser.parse_args()
    result = verify_public_file(args.repo, args.commit, args.path, args.sha256)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["source_readback"] == "PUBLIC_SOURCE_BYTES_MATCH_TRUSTED_HTTPS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
