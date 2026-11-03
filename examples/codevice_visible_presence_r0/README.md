# CoDeviceVisiblePresence+ R0 | Reolink 8-camera synthetic canary

**State:** `SYNTHETIC_READ_ONLY_PROJECTION__NOT_LIVE_HA__NOT_X2__NO_CAMERA_COMMANDS`.

## Purpose

Treat quiet, reachable, stale, private, unknown, and real observed events differently. A physical camera should not simulate animation merely to appear sentient. The eight fictional camera labels represent neither historical nor current inventory. The fixture's `SYNTHETIC` evidence (including assumed PTZ/low-glare capability for *one invented test*) is fictional, not a device map.

## Reuse, not duplicate

Attach to CoDeviceQuadPlane+ → HA/Reolink existing local integration → CoQuanta/CoPulse → CoOrb/CoBar. Never add a second surveillance control plane. Reolink official and Home Assistant documentation describe model-dependent LED, floodlight, presence, PTZ capabilities. They do not guarantee which entities are on X2/HA or that all cameras have a programmable status LED.

- Home Assistant integration: https://www.home-assistant.io/integrations/reolink
- Reolink light classes: https://support.reolink.com/articles/12822588308121-How-to-Set-up-Different-Lights-of-Reolink-Cameras/
- Reolink spotlight-supported models: https://support.reolink.com/articles/10446659667097-Which-Cameras-Support-the-Spotlight/

## Run

`python3 -m unittest -v test_visible_presence.py` from this directory; then `python3 CoDeviceVisiblePresenceR0.py --fixture fixture.json --output /tmp/coalive-shadow.json` (create-only). No camera API, live feed, credentials, or Home Assistant connection.

## Product contract

1. **Observer**: Exact device identity, actual model/firmware, source entity and timestamp/cursor verified per device; expose quiet/reachable separately from events; stale and unknown never automatically become success/failure.
2. **Private projections**: CoBar receives a short event/badge; ambient light should not reveal who is home; no face, identity, or audio profiling. Users/bystanders can opt out of visible gestures where appropriate.
3. **Two output classes**: `local_ui_ack` is a nonflashing illustration; `physical_proposal` is human/installer-reviewed only and is **never a hardware write**. Default outputs are `NONE`. No PTZ movements, sirens, chimes, floodlight flash, alarm disable, public RTSP, WAN port forward, or credential access.
4. **Physical capability**: Verify device/firmware actually exposes a suitable indicator. If only floodlights exist, prefer their documented normal person-event/night mode, restrained intensity and short duration. Never improvise a flashing code or change floodlight policies without neighbor/glare/safety checks.
5. **Multiplied evaluation**: The eight camera observers can be evaluated independently and delta-fanned-in to one CoOrb view. Shared hardware commands must have one elected actuator, rate cap, kill switch, provenance and rollback.
6. **Recovery**: Disconnect HA observer, expire timestamps, verify UNKNOWN/STALE not fake-green; reconnect, read actual observation, ensure cursor reconciliation and no double event actuation; preserve native camera/security function if overlay fails.

## Next genuine proof

Authorized, **read-only** Home Assistant camera entity census (user-owned local HA Yellow, PoE camera network; verify actual names/models/versions and consent policies), then one time-limited UI-only local event representation. Collect p50/p95 signal latency, duplicate count, false-green rate, attention/glare complaints, manual steps, recovery and 24-hour uptime. Only after proof is an approved model-specific physical acknowledgment candidate eligible for separate controlled deployment.

**No device was connected, powered, restarted, moved, lit, flashed, or recorded.** Test receipts are computer-local synthetic fixtures only. `VALIDATION_NE_RECEIVER_ACCEPTANCE`, `VISUAL_PULSE_NE_LIVE_HEALTH`, `NO_RECEIVER_PICKUP_WITHOUT_EXACT_READPROOF`.

## Visual prototype

Open `demo.html` locally for a no-network, accessible, explicitly SYNTHETIC visual with three simulation controls. It does not represent live HA or camera health, and never sends a command.
