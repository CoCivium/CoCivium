"""CoSource R0: verify supplied CoPre bytes against browser fixture pin.

No network, issuer authentication, consent grant, or receiver ACK.
"""
import hashlib
from pathlib import Path

EXPECTED_SHA256 = "58f8c722bfbfc34cac41189c072d2effe4b19dbbe8a37be4f8687344d6b00b9a"
EXPECTED_COMMIT = "63b41ead8797e5a781699f32bcbc77b78bdbd7af"
EXPECTED_REF = f"CoCivium/CoCivium:CoPre.md@{EXPECTED_COMMIT}"


def verify_source(path, source_ref, expected_sha256=EXPECTED_SHA256):
    if source_ref != EXPECTED_REF or expected_sha256 != EXPECTED_SHA256:
        return {"state": "HELD_PIN_MISMATCH", "source_verified": False}
    p = Path(path)
    if p.name != "CoPre.md" or p.is_symlink() or not p.is_file():
        return {"state": "HELD_SOURCE_UNAVAILABLE", "source_verified": False}
    try:
        with p.open("rb") as stream:
            raw = stream.read(131073)
    except OSError:
        return {"state": "HELD_SOURCE_UNAVAILABLE", "source_verified": False}
    if not raw or len(raw) > 131072:
        return {"state": "HELD_SOURCE_SIZE", "source_verified": False}
    actual = hashlib.sha256(raw).hexdigest()
    if actual != EXPECTED_SHA256:
        return {"state": "HELD_SOURCE_BYTES_MISMATCH", "source_verified": False, "actual_sha256": actual}
    return {"state": "SOURCE_BYTES_MATCH_FIXTURE_PIN", "source_verified": True, "source_ref": EXPECTED_REF, "sha256": actual, "authenticated_origin": False, "receiver_ack": False}
