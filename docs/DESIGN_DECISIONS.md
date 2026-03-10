# Design Decisions Log

Documenting technical choices, trade-offs, and rationale as they happen.
Useful for the final report — shows engineering reasoning, not just results.

---

## DD-01: MJPEG over H.264 for Video Streaming
**Date:** 2026-03-09
**Context:** Need to stream live camera feed from Pi to laptop ground station.
**Options considered:**
1. **MJPEG over HTTP** — pure Python, any browser, ~100ms latency, ~0.5 Mbps
2. **H.264/HLS via FFmpeg** — needs ffmpeg install, 5-10x better compression, but 2-4s latency
3. **VNC/screen sharing** — heavy, laggy, wastes Pi CPU
4. **SSH X forwarding** — painfully slow for video

**Decision:** MJPEG
**Rationale:** For drone ops, low latency matters more than compression. 0.5 Mbps is trivial over WiFi. Zero dependencies — works in any browser via `<img>` tag. H.264 would only matter for cellular/4G or 720p+ resolution.

---

## DD-02: Headless Operation via SSH (PuTTY)
**Date:** 2026-03-10
**Context:** Pi mounted on drone has no screen. Need to start scripts and monitor remotely.
**Problem:** OpenCV (`cv2.imshow`) crashes when no display is available (Qt plugin error).
**Options considered:**
1. Attach monitor to Pi on the field — impractical
2. VNC — adds latency and complexity
3. **SSH + headless flags** — lightweight, reliable

**Decision:** SSH (PuTTY) for script control, browser for visual output
**Implementation:**
- `signal.signal(signal.SIGINT, signal.SIG_DFL)` — ensures Ctrl+C works in SSH
- `os.environ['QT_QPA_PLATFORM'] = 'minimal'` when no DISPLAY — prevents Qt crash
- Auto-detect IP with `hostname -I` — always prints correct URL
- All visual output via MJPEG web stream, never `cv2.imshow`

**Flight day workflow:**
- PuTTY Terminal 1: mavproxy
- PuTTY Terminal 2: `pi_flight.py`
- Laptop browser: dashboard at `http://<PI_IP>:8090`
- Laptop Mission Planner: TCP to `<PI_IP>:5762`

---

## DD-03: Dual-Backend Vision System (Ultralytics vs TFLite)
**Date:** 2026-02-17
**Context:** Laptop has full PyTorch+Ultralytics, Pi only has lightweight TFLite.
**Decision:** Single `vision.py` with auto-detection — tries Ultralytics first, falls back to TFLite.
**Rationale:** Same code runs on both platforms. No `if platform == ...` scattered everywhere. `detect_in_image(frame) → (found, x, y, conf)` interface is identical regardless of backend.

---

## DD-04: mavproxy UDP Bridge (not direct serial)
**Date:** 2026-02-17
**Context:** Python 3.13 + pyserial has broken serial reads — bytes dropped, BAD_DATA errors.
**Options considered:**
1. Downgrade to Python 3.11 — breaks other dependencies
2. Fix pyserial — upstream bug, not our fix to make
3. **mavproxy as UDP bridge** — reads serial correctly, forwards via UDP

**Decision:** mavproxy bridge
**Command:** `mavproxy.py --master=/dev/ttyAMA0 --baudrate=921600 --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762`
**Rationale:** mavproxy is battle-tested, also gives us free Mission Planner connectivity via TCP. Scripts connect to `udpin:0.0.0.0:14550` instead of serial. Extra process but zero data loss.

---

## DD-05: Camera Shares One Owner (no concurrent access)
**Date:** 2026-03-10
**Context:** Robin's mission script flies the drone, our script does vision. Can both run?
**Problem:** Only one process can open the Pi camera (picamera2) at a time.
**Decision:** Robin's script handles flight only (no camera). Our `pi_flight.py` handles camera + vision + stream. Both run in parallel, no conflict.
**Alternative rejected:** Shared camera via IPC/socket — adds complexity, fragile, not worth it for a demo.

---

## DD-06: IMX296 BGR Color Fix
**Date:** 2026-02-17
**Context:** Camera images had persistent blue tint despite trying AWB modes, manual gains, ISP tuning.
**Root cause:** IMX296 global shutter sensor outputs BGR data despite picamera2 labeling it RGB888. Code had `cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)` which double-swapped channels.
**Discovery method:** Tested all 6 permutations of R,G,B channels — "no conversion" looked correct.
**Fix:** Remove `cvtColor` entirely. Data is already BGR (OpenCV's native format).
**Lesson:** Don't trust format labels — test empirically.

---

## DD-07: Progressive Test Strategy
**Date:** 2026-02-18
**Context:** Need confidence that autonomous flight won't crash the drone.
**Decision:** Numbered test progression — each step builds trust before adding risk:
1. Mission Planner AUTO waypoints (no custom code)
2. Waypoint test script (no CV)
3. Manual flight + passive CV (zero commands)
4. Autonomous search + CV logging only (no action)
5. Full autonomous mission

**Rationale:** Never skip a step. Each step isolates one new variable. If step N fails, the problem is the thing you added at step N, not something from step N-2.

---

## DD-08: GPS Estimation — Inverse Variance Weighting
**Date:** 2026-02-20
**Context:** Estimating target GPS position from camera detections at varying altitudes.
**Problem:** Observations from 30m altitude have much larger error than from 10m (more metres per pixel).
**Decision:** Weight observations by 1/altitude² — a 10m observation is 9x more valuable than 30m.
**Additional:** Centre-snap observations (target at frame centre) get 10x bonus weight since projection error is minimal at the optical axis.
**Validated in simulation:** ~0.5m estimate error after 30s averaging while centred at 10-15m.

---

## DD-09: 7.5m Offset Landing
**Date:** 2026-02-19
**Context:** Drone must land near casualty but NOT directly on them (propwash, crash risk).
**Decision:** After GPS lock on target, fly to a point 7.5m north and land there.
**Rationale:** 7.5m gives safe separation. "North" is arbitrary but consistent — SAR team knows where to look relative to drone. Simulated successfully in simple_simulator.py.

---

*Add new decisions as they come up. Format: context → options → decision → rationale.*
