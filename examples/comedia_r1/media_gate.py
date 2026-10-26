#!/usr/bin/env python3
"""CoMedia R1: offline source/storyboard/video release-readiness assessor.

Never uploads, edits, emails, posts, or publishes. A technically good video is
NOT automatically an accurate, ethical, effective or approved publication.
"""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "CoCivium.CoMediaQualityGate.R1"
STATUS = {"CONCEPT", "WIP_STORYBOARD", "WIP_RENDER", "REVIEW_CANDIDATE", "RELEASE_CANDIDATE"}
SHAPE = {"VERTICAL_9_16", "LANDSCAPE_16_9", "SQUARE_1_1"}
MAX_MEDIA_BYTES = 1024 * 1024 * 1024
MAX_PROBE_SECONDS = 20
MAX_ANALYZE_SECONDS = 35
SCAN_SECONDS = 60


def digest_file(path):
    sha = hashlib.sha256()
    with Path(path).open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            sha.update(chunk)
    return sha.hexdigest()


def _text(value, limit=600):
    return isinstance(value, str) and 0 < len(value.strip()) <= limit


def validate_spec(spec):
    errors = []
    if not isinstance(spec, dict):
        return ["manifest must be an object"]
    if spec.get("schema") != SCHEMA:
        errors.append("invalid schema")
    if not _text(spec.get("asset_id"), 96) or not re.fullmatch(r"[a-z0-9][a-z0-9_.-]*", str(spec.get("asset_id", ""))):
        errors.append("invalid asset_id")
    if spec.get("status") not in STATUS:
        errors.append("invalid editorial status")
    if spec.get("status") in {"WIP_STORYBOARD", "WIP_RENDER"} and not str(spec.get("public_note", "")).startswith("WORK IN PROGRESS"):
        errors.append("WIP needs visible work-in-progress label")
    if spec.get("publication_effect_authorized") is not False:
        errors.append("publication authority must be false in this assessor")
    if not _text(spec.get("source_identity")) or not _text(spec.get("source_revision"), 120):
        errors.append("source identity and revision required")
    if spec.get("shape") not in SHAPE:
        errors.append("unknown shape")
    if not isinstance(spec.get("storyboard"), list) or len(spec["storyboard"]) < 3:
        errors.append("at least three storyboard shots required")
    else:
        shots = spec["storyboard"]
        indexes = [x.get("shot") for x in shots if isinstance(x, dict)]
        if indexes != list(range(1, len(shots) + 1)):
            errors.append("storyboard shots must be sequential")
        for x in shots:
            if not isinstance(x, dict):
                errors.append("shot is not an object")
                continue
            if not (isinstance(x.get("seconds"), (int, float)) and 0.5 <= x["seconds"] <= 60):
                errors.append("invalid shot duration")
            for field in ("visual", "voiceover", "evidence_class"):
                if not _text(x.get(field), 500):
                    errors.append("missing shot " + field)
            if x.get("evidence_class") not in {"HYPOTHESIS", "METAPHOR", "DESIGN_PROPOSAL", "SOURCED_BACKGROUND"}:
                errors.append("unqualified shot evidence class")
    rights = spec.get("rights", {})
    if not isinstance(rights, dict) or any(rights.get(k) not in {"ORIGINAL", "LICENSE_VERIFIED", "UNKNOWN", "NOT_APPLICABLE"} for k in ("visuals", "music", "voice")):
        errors.append("invalid rights declaration")
    a11y = spec.get("accessibility", {})
    if not isinstance(a11y, dict) or not isinstance(a11y.get("captions_prepared"), bool) or not isinstance(a11y.get("text_twin_prepared"), bool):
        errors.append("invalid accessibility contract")
    if spec.get("realistic_ai_alteration") not in {True, False}:
        errors.append("AI alteration disclosure field required")
    if spec.get("ai_use_declared") not in {True, False}:
        errors.append("AI-use metadata field required")
    if spec.get("publication_url") is not None or spec.get("receiver_ack") is not None:
        errors.append("public delivery/ack cannot be preasserted by this tool")
    return sorted(set(errors))


def editorial_holds(spec):
    holds = []
    if spec.get("status") != "RELEASE_CANDIDATE":
        holds.append("WIP_NOT_RELEASE_CANDIDATE")
    rights = spec.get("rights", {})
    if any(rights.get(k) == "UNKNOWN" for k in ("visuals", "music", "voice")):
        holds.append("RIGHTS_NOT_QUALIFIED")
    a11y = spec.get("accessibility", {})
    if a11y.get("captions_prepared") is not True or a11y.get("text_twin_prepared") is not True:
        holds.append("ACCESSIBILITY_TWIN_INCOMPLETE")
    if spec.get("realistic_ai_alteration") is True and spec.get("ai_use_declared") is not True:
        holds.append("PLATFORM_AI_USE_DISCLOSURE_MISSING")
    approvals = spec.get("review", {})
    if not isinstance(approvals, dict) or not _text(approvals.get("editorial_approval_receipt")):
        holds.append("NO_EDITORIAL_REVIEW_RECEIPT")
    if not isinstance(approvals, dict) or not _text(approvals.get("reader_comprehension_receipt")):
        holds.append("NO_READER_COMPREHENSION_RECEIPT")
    return sorted(set(holds))


def probe_media(media_file, run_cmd=subprocess.run):
    f = Path(media_file)
    if not f.is_file():
        return {"state": "FAIL_MEDIA_MISSING", "reason": "file not found"}
    size = f.stat().st_size
    if not 0 < size <= MAX_MEDIA_BYTES:
        return {"state": "FAIL_MEDIA_SIZE_BOUND", "size_bytes": size}
    if shutil.which("ffprobe") is None or shutil.which("ffmpeg") is None:
        return {"state": "HELD_FFMPEG_TOOLS_UNAVAILABLE", "size_bytes": size}
    try:
        probe = run_cmd(["ffprobe", "-v", "error", "-show_entries", "stream=codec_type,width,height,r_frame_rate:format=duration", "-of", "json", str(f)], capture_output=True, text=True, timeout=MAX_PROBE_SECONDS, check=False)
        if probe.returncode != 0:
            return {"state": "FAIL_FFPROBE_DECODING", "size_bytes": size}
        meta = json.loads(probe.stdout)
        streams = meta.get("streams", [])
        video = next((s for s in streams if s.get("codec_type") == "video"), None)
        audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
        if not video:
            return {"state": "FAIL_NO_VIDEO_STREAM", "size_bytes": size}
        w, h = int(video.get("width", 0)), int(video.get("height", 0))
        duration = float(meta.get("format", {}).get("duration", 0) or 0)
        ff = run_cmd(["ffmpeg", "-nostdin", "-hide_banner", "-loglevel", "info", "-i", str(f), "-t", str(SCAN_SECONDS), "-vf", "blackdetect=d=0.50:pix_th=0.10", "-an", "-f", "null", "-"], capture_output=True, text=True, timeout=MAX_ANALYZE_SECONDS, check=False)
        black = re.findall(r"black_start:([0-9.]+)\s+black_end:([0-9.]+)", ff.stderr[-25000:])
        return {"state": "PASS_SCOPED_MEDIA_DECODE" if ff.returncode == 0 else "FAIL_FFMPEG_DECODING", "sha256": digest_file(f), "size_bytes": size, "width": w, "height": h, "duration_seconds": round(duration, 3), "has_audio": audio is not None, "black_intervals_first_60s": len(black), "black_segments": [[float(a), float(b)] for a,b in black[:12]], "scan_seconds_max": SCAN_SECONDS, "tool_ceiling": "TECHNICAL_DECODE_NOT_EDITORIAL_QUALITY"}
    except (json.JSONDecodeError, ValueError, OSError, subprocess.TimeoutExpired) as exc:
        return {"state": "HELD_TOOL_EXECUTION", "reason": type(exc).__name__, "size_bytes": size}


def inspect(spec, media_file=None, run_probe=probe_media):
    errors = validate_spec(spec)
    report = {"schema": "CoCivium.CoMediaReceipt.R1", "observed_at_utc": datetime.now(timezone.utc).isoformat(), "asset_id": spec.get("asset_id") if isinstance(spec, dict) else None, "status_declared": spec.get("status") if isinstance(spec, dict) else None, "manifest_errors": errors, "publication_effects": 0, "network_calls": 0, "provider_sessions": 0, "published_url": None, "receiver_ack": None}
    if errors:
        return {**report, "state": "FAIL_MANIFEST", "release_eligible": False, "holds": ["INVALID_SOURCE_SPEC"]}
    holds = editorial_holds(spec)
    media = None
    if media_file is None:
        holds.append("NO_RENDERED_MEDIA_CHECKED")
    else:
        media = run_probe(media_file)
        if media.get("state") != "PASS_SCOPED_MEDIA_DECODE":
            holds.append("MEDIA_DECODE_OR_TOOL_HELD")
        else:
            if media["size_bytes"] <= 300_000:
                holds.append("UNDER_300KB_USER_LITMUS")
            if media["width"] < 720 or media["height"] < 720:
                holds.append("INSUFFICIENT_SPATIAL_RESOLUTION")
            ratio = media["width"] / media["height"]
            ideal = {"VERTICAL_9_16": 9/16, "LANDSCAPE_16_9": 16/9, "SQUARE_1_1": 1.0}[spec["shape"]]
            if abs(ratio - ideal) > 0.08:
                holds.append("WRONG_ASPECT_FOR_TARGET")
            if media["black_intervals_first_60s"]:
                holds.append("BLACK_SEGMENTS_REQUIRE_EDITORIAL_REVIEW")
            if not media["has_audio"]:
                holds.append("AUDIO_OR_MUTE_INTENT_NOT_VERIFIED")
    holds = sorted(set(holds))
    # Even with no holds, source technical checks cannot issue publication authority.
    return {**report, "state": "HELD_PREPUBLICATION" if holds else "PASS_PREPUBLICATION_GATES_ONLY", "release_eligible": False, "holds": holds, "media": media, "next_action": "Human/editor reviews rights, claims, captions, pacing and receiver fit; a separate authorized publisher must prove delivery."}


def main():
    parser = argparse.ArgumentParser(description="Offline media release-readiness assessor; NEVER publishes")
    parser.add_argument("manifest", type=Path)
    parser.add_argument("--media", type=Path, default=None, help="explicit path to one local media file")
    args = parser.parse_args()
    if not args.manifest.is_file() or args.manifest.stat().st_size > 262144:
        parser.error("manifest missing or exceeds 256 KiB")
    spec = json.loads(args.manifest.read_text(encoding="utf-8"))
    print(json.dumps(inspect(spec, args.media), indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
