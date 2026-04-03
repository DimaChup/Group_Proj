# Design Decisions Log

Documenting technical choices, trade-offs, and rationale as they happen.
Useful for the final report — shows engineering reasoning, not just results.

---

## DD-01: MJPEG over H.264 for Video Streaming
**Date:** 2026-03-09 (updated 2026-03-18 with full comparison)
**Context:** Need to stream live camera feed from Pi to laptop ground station during flight.

**Options considered:**

| Method | Latency | Max FPS | Browser? | Dependencies | Complexity | Reliability |
|---|---|---|---|---|---|---|
| **MJPEG/HTTP (chosen)** | ~300ms | 3-5 | Yes | OpenCV only | Low | Very high |
| H.264/RTP + GStreamer | ~100ms | 30 | No (needs player) | gstreamer, pygobject | High | Medium |
| H.264/HLS via FFmpeg | 1-2s | 30 | Yes | ffmpeg | Medium | Medium |
| WebRTC | ~50ms | 30 | Yes | aiortc, STUN/TURN | High | Medium |
| GStreamer RTSP | ~100ms | 30 | No | gstreamer | Medium | Medium |
| VNC/screen sharing | ~500ms | 15 | VNC client | VNC server | Low | Medium |

**Decision:** MJPEG over HTTP

**Rationale:**
- **Most reliable** for field operations — pure HTTP, stateless, each frame independent
- Works in any browser (laptop, phone, tablet) — no special apps or codecs
- Zero extra dependencies — just OpenCV `imencode()`
- Our inference is only 3-5 FPS — low latency streaming doesn't help when AI processes 3 frames/sec
- Thread-safe with `ThreadingMixIn` — handles multiple browser clients
- Easy debugging — `/snapshot` endpoint, `/stream` in any browser
- Battle-tested: passive_watch.py, pi_flight.py, capture_training.py all use it

**Why not H.264/GStreamer (like our GCSScripts project on Desktop):**
- GCSScripts uses `udpsrc → rtph264depay → h264parse → avdec_h264 → videoconvert → appsink`
- Needs `pygobject` + `gstreamer` + plugins installed — extra failure points in field
- Doesn't work in a plain browser — needs Tkinter app or GStreamer player
- More complex to debug when it breaks during flight

**Why not WebRTC:**
- Most complex to set up (STUN/TURN servers, signaling)
- Overkill for passive monitoring at 3 FPS

**Trade-offs accepted:**
- Higher bandwidth (~2-5 Mbps vs ~0.5 Mbps for H.264)
- Higher latency (~300ms vs ~100ms) — acceptable since passive watch sends zero commands
- CPU cost of JPEG re-encoding per frame

**Revisit if:** Need real-time FPV for manual piloting, or inference speed exceeds 15 FPS (NCNN/Hailo).

**Implementation:**
- `passive_watch.py` — port 8090, JPEG quality 70%
- `pi_flight.py` — port 8090, JPEG quality 85%
- `capture_training.py` — port 8091
- `tests/diagnostics/camera_stream_h264.py` — H.264 alternative (needs FFmpeg, for future use)

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
**Date:** 2026-02-17 (updated 2026-03-30: NCNN added as third backend)
**Context:** Laptop has full PyTorch+Ultralytics, Pi only has lightweight TFLite. NCNN added later for ARM-optimised speed.
**Decision:** Single `vision.py` with auto-detection — priority: NCNN (if `--backend ncnn`) > Ultralytics (laptop, `.pt` models) > TFLite (Pi fallback, `.tflite` models). See DD-13 for NCNN details.
**Rationale:** Same code runs on both platforms. No `if platform == ...` scattered everywhere. `detect_in_image(frame) → (found, x, y, conf)` interface is identical regardless of backend. Adding a new backend means adding one `_try_load_*` and one `_detect_*` method — zero changes to callers.

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
**Date:** 2026-02-18 (updated 2026-03-09: numbered test scripts in tests/flight/)
**Context:** Need confidence that autonomous flight won't crash the drone.
**Decision:** Numbered test progression — each step builds trust before adding risk:
1. Mission Planner AUTO waypoints (no custom code)
2. Waypoint test script (no CV)
3. Manual flight + passive CV (zero commands)
4. Autonomous search + CV logging only (no action)
5. Full autonomous mission

**Implementation:** `tests/flight/` directory with numbered scripts:
- `0a_cube_commands.py` — bench: individual MAVLink commands
- `0b_bench_mission.py` — bench: full command sequence (no props)
- `0c_feedback_test.py` — bench: vision-to-GPS pipeline (no commands)
- `0d_planning_test.py` — lawnmower pattern, bounds, NFZ avoidance (6 unit tests)
- `0e_geofence_test.py` — NFZ boundaries, waypoint filter, repulsion (7 unit tests)
- `0f_servo_test.py` — payload servo PWM on bench (interactive)
- `1_passive_flight.py` — manual RC, CV watches (ZERO commands)
- `2_waypoint_test.py` — fly GPS waypoints (no CV)
- `3_auto_detect.py` — AUTO + AI detection triggers GUIDED hover
- `4_detect_and_center.py` — autonomous pattern + centre on target

**Rationale:** Never skip a step. Each step isolates one new variable. If step N fails, the problem is the thing you added at step N, not something from step N-2. The `0x` bench tests are free (no props, no flying) and catch wiring/command bugs before risking hardware.

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

## DD-10: NFZ Geofence — Three Avoidance Strategies
**Date:** 2026-03-25
**Context:** SSSI no-fly zone near the search area. Drone must avoid entering but still search close to the boundary. Need safe, smooth behaviour in the buffer zone.

**Problem:** ArduCopter has no built-in soft boundary concept — it either respects a hard geofence (RTL/LAND) or ignores it entirely. We need graduated slowdown near the boundary so the drone doesn't overshoot into the NFZ.

**Options implemented (CLI flags):**

| Mode | Flag | Mechanism | Buffer | Smoothness | Notes |
|---|---|---|---|---|---|
| **Repulsive** | `--nfz-repel` | Velocity nudge away from NFZ | 8m (soft boundary) | Medium | Quadratic force, can fight waypoint navigation |
| **Velocity** | `--nfz-slow` | Velocity commands toward waypoint, speed capped | 20m | Medium | Jittery — velocity commands conflict with position targets |
| **Speed-cap** | `--nfz-carrot` | Normal waypoint nav, only `DO_CHANGE_SPEED` capped | 20m | **Best** | Smooth — same path, just slower |

**Decision:** `--nfz-carrot` (speed-cap) is the recommended mode.

**Speed profile (20m buffer zone):**
- Linear: `speed = 0.3 + (dist_to_boundary / 20) × (3.0 - 0.3)`
- At 20m from SSSI: 3.0 m/s (entering buffer)
- At 10m from SSSI: 1.65 m/s
- At 0m (boundary): 0.3 m/s (near-stop)
- Outside 20m: normal altitude-dependent speed (6-10 m/s)

**Why speed-cap wins:**
1. **No jitter** — doesn't override position targets or send velocity commands; ArduCopter's own path following handles direction
2. **Same flight path** — drone follows exact same waypoints as without geofence, just slower near SSSI
3. **`DO_CHANGE_SPEED` only affects GUIDED/AUTO** — has zero effect on manual RC flying (STABILIZE/LOITER/POSHOLD), so pilot can always override at full stick authority
4. **SEARCH-only** — speed cap only active during SEARCH state; transit, pre-waypoints, return, manual all fly at normal speed

**SSSI inside detection:** If drone enters NFZ (hard boundary), auto-switches to MANUAL mode regardless of which geofence mode is active.

**Visualization:** Orange buffer zone drawn on map at 20m from SSSI boundary (slow/carrot modes) or 8m (repel mode).

---

## DD-11: Threaded Inference — Stream at 30fps, Detect in Background
**Date:** 2026-03-31 (refined 2026-04-01)
**Context:** Pi 5 TFLite inference runs at ~4.8 FPS. If inference blocks the main loop, the video stream stutters at 4.8 FPS — unacceptable for an operator monitoring a flight.

**Problem:** Single-threaded approach forces the camera capture, AI inference, overlay drawing, and MJPEG streaming to run sequentially. The slowest stage (inference at ~208ms) bottlenecks everything.

**Decision:** Decouple capture/display from inference using a background thread.

**Architecture:**
- **Main thread** (display loop): grabs camera frames at native rate (~30fps on Pi), draws overlays (GPS, crosshair, detection boxes from last result), encodes JPEG, serves MJPEG stream.
- **Inference thread** (`inference_worker`): grabs the latest frame from a shared variable, runs `detect_in_image()`, updates shared detection state (`_inference_frame`, detection coords, confidence).
- **Shared state** protected by `_inference_lock` and `_inference_eyes_lock` (for model hot-swap).

**Why this approach:**
1. Stream never stalls — operator always sees live video, even if AI is mid-inference
2. AI results appear as soon as ready (no frame queue delay)
3. Frame-dropping is intentional: inference always processes the *latest* frame, skipping stale ones
4. Model hot-swap is safe: lock `_inference_eyes_lock`, join the inference thread, swap `VisionSystem`, restart

**Trade-offs accepted:**
- Detection overlay lags by one inference cycle (~200ms) — imperceptible at flight altitude
- Slightly higher CPU usage from concurrent threads — Pi 5 has 4 cores, plenty of headroom
- Frame copy on each inference pass (`det_frame = frame.copy()`) — ~1ms cost, prevents race conditions

**Implemented in:** `field_tools/passive_watch.py` (lines ~2488-2550), `tests/diagnostics/diagnostics.py`

---

## DD-12: SmartEstimator — Greedy Tightest Cluster for GPS Lock
**Date:** 2026-04-01
**Context:** GPS estimation from camera detections produces a scatter of points. Outliers from GPS lag, false positives, or edge-of-frame detections can pull the weighted mean off-target. Need a robust lock mechanism that ignores outliers.

**Problem:** The DummyEstimator (inverse-variance weighted mean) is susceptible to outliers. A single false positive at 30m altitude can shift the mean by several metres. Need a method that finds the *consistent core* of estimates.

**Decision:** Greedy tightest-cluster algorithm — find the N points (default 5) with the smallest pairwise spread.

**Algorithm:**
1. Collect all GPS estimates as `(lat, lon, pixel_dist, frame)` tuples
2. For each point, compute the sum of distances to all other points
3. Pick the point with smallest total distance as the seed (geometric medoid)
4. Greedily add the nearest remaining point, recomputing cluster spread
5. Stop at N points. If spread < `max_spread` (default 1.0m), lock

**Why greedy over k-means/DBSCAN:**
- No hyperparameters to tune (k-means needs k, DBSCAN needs eps + min_samples)
- Deterministic — same input always gives same result
- O(N^2) is fine for N < 100 estimates (typical mission has 10-50 detections per target)
- Greedy from medoid naturally finds the densest region, which is the true target

**Lock behaviour:**
- Once locked, `SmartEstimator.locked = True` — no more estimates accepted
- `lock_id` counter increments (survives resets) — used for unique result filenames
- Locked cluster saved with frames for the result image grid
- Most central frame (smallest `pixel_dist`) becomes the hero image

**Configurable via CLI:**
- `--smart-min N` — minimum cluster size before lock (default 5)
- `--smart-radius M` — maximum spread in metres for lock (default 1.0)

**Implemented in:** `field_tools/passive_watch.py` (SmartEstimator class, lines ~1103-1200)

---

## DD-13: NCNN Backend — Third Inference Option for Pi 5
**Date:** 2026-03-30
**Context:** TFLite on Pi 5 gives ~4.8 FPS. NCNN (Tencent's neural network framework) is optimised for ARM and promises ~15 FPS on the same hardware. Need to add it without breaking existing backends.

**Decision:** Add NCNN as a third backend in `vision.py`, selectable via `--backend ncnn` CLI flag or `backend="ncnn"` parameter. Priority order: NCNN (if requested) > Ultralytics (laptop) > TFLite (Pi fallback).

**Why not replace TFLite:**
- NCNN requires separate model files (`.param` + `.bin`) alongside `.tflite`
- Not all models have NCNN exports yet — TFLite is the universal fallback
- NCNN Python bindings (`pip install ncnn`) can be finicky on some platforms
- TFLite is battle-tested (months of flights) — NCNN is newer, less proven

**Implementation:**
- `VisionSystem.__init__` accepts `backend="ncnn"` parameter (no sys.argv hack needed)
- NCNN model directory resolved from `.tflite` path: `<dir>/ncnn/best_ncnn_model/`
- Same `detect_in_image()` interface — callers don't know which backend is running
- NCNN uses `ncnn.Mat.from_pixels()` for zero-copy input, 4 threads
- Warmup inference on init to trigger JIT compilation

**Trade-offs:**
- Extra dependency (`pip install ncnn`) on Pi
- Two model files to keep in sync with `.tflite`
- Less tested than TFLite path

**Implemented in:** `vision.py` (`_try_load_ncnn`, `_detect_ncnn` methods)

---

## DD-14: Zero-Command Passive Mode — Safety-First Observer
**Date:** 2026-02-17
**Context:** Before trusting autonomous flight, need to validate that CV detects the target in real outdoor conditions. Running detection during manual RC flight is the safest approach.

**Problem:** Any script that sends MAVLink commands is a safety risk during early testing. A bug could arm the drone, change mode, or send velocity commands while the pilot is flying manually.

**Decision:** `passive_watch.py` sends exactly ZERO MAVLink commands. It only *reads* telemetry (GPS, altitude, heading) for geotagging. The pilot has full RC authority at all times.

**What it does:**
- Opens camera, runs AI inference, streams MJPEG to browser
- Saves detection snapshots (raw + annotated) with estimated GPS coordinates
- Reads drone GPS/altitude/heading from mavproxy (read-only `recv_match`)
- SmartEstimator clustering for target GPS lock
- CSV logging of all detections with timestamps, confidence, GPS

**What it explicitly does NOT do:**
- No `mav.mav.command_long_send()` — no arming, mode changes, or waypoints
- No `mav.mav.set_position_target*()` — no velocity or position commands
- No `mav.mav.rc_channels_override*()` — no RC override
- No servo commands, no buzzer triggers, no payload release

**Why this matters:**
- Can be run during ANY flight (manual, auto, or another script's mission)
- Safe to leave running — worst case is it fills the SD card with photos
- Validates detection altitude, false positive rate, GPS estimation accuracy
- Training data collection: `--simple-names` saves raw frames for labelling

**Implemented in:** `field_tools/passive_watch.py`, `capture_training.py`

---

## DD-15: SMART Result Image — Visual Confirmation with Map Composite
**Date:** 2026-04-01
**Context:** When SmartEstimator locks onto a target, the operator needs visual confirmation: *where* is the target, and *what* does it look like? A GPS coordinate alone is not enough.

**Decision:** Generate a composite result image (`RESULT_SMART_{lat}_{lon}.jpg`) that combines:
1. **Hero image** — the most central detection frame (smallest pixel distance from frame centre), with bounding box and GPS overlay already drawn
2. **Smart grid** — thumbnail strip of all cluster frames, showing the N detections that formed the lock
3. **Map composite** — satellite map with search area polygon, flight area boundary, SSSI no-fly zone, all detection scatter points, and a star marker at the locked GPS coordinate
4. **Stats banner** — lock spread, sample count, GPS coordinate, altitude, confidence range

**Why composite over just saving the frame:**
- A single frame doesn't show *where* on the map the target is
- The grid shows the operator all N cluster frames — if any look like false positives, they can reject
- The star on the map gives immediate spatial context relative to boundaries and NFZ
- `lock_id` counter in the filename prevents overwrites when multiple targets are found

**Implementation details:**
- `generate_result_image()` in passive_watch.py
- Map drawn with `cv2.fillPoly` for search/flight/SSSI polygons, GPS-to-pixel transform
- Star coordinate drawn as 5-pointed star (magenta) at the cluster median position
- Bullseye/grid lock sync: `update_last_frame()` ensures thumbnails show the overlayed display frame, not the raw camera frame
- Saved synchronously after lock to guarantee the file exists before the next detection cycle

---

## DD-16: Inverse-Variance Weighting — Altitude-Dependent Observation Quality
**Date:** 2026-02-20 (expanded from DD-08)
**Context:** DD-08 documented the basic 1/alt^2 weighting. This entry documents the full weighting model used in DummyEstimator, including the centrality bonus.

**Weighting model:** `weight = (1 / altitude^2) * centrality_bonus`

**Rationale for 1/alt^2:**
- Ground sample distance (GSD) scales linearly with altitude — each pixel covers more metres
- GPS estimation error propagates through two dimensions (x and y), so variance scales as alt^2
- A detection at 10m has 9x more weight than at 30m (GSD ratio squared)
- This naturally down-weights flyover detections (high altitude, low precision) and up-weights centering detections (low altitude, high precision)

**Centrality bonus (10x):**
- Detections where the target is near the frame centre get a 10x weight multiplier
- At the optical axis, lens distortion is minimal and the projection from pixel to GPS is most accurate
- "Centre-snap" threshold: target within central 20% of the frame
- This incentivises the centering behaviour: hovering directly above the target produces the tightest GPS estimates

**Why not equal weighting:**
- Equal weighting treats a glancing detection at 35m the same as a hover at 10m
- In testing (simple_simulator.py), equal weighting gave ~2m error vs ~0.5m with inverse-variance
- The altitude-squared model matches the physics of perspective projection

**Implemented in:** `DummyEstimator` class in `field_tools/passive_watch.py`, `simple_simulator.py`

---

## DD-17: CLI Flags Reflected in Browser UI
**Date:** 2026-04-01
**Context:** passive_watch.py accepts ~15 CLI flags (`--conf`, `--smart-min`, `--smart-radius`, `--class-filter`, `--model`, etc.). The operator launches the script via SSH but monitors via browser. If the browser doesn't show which flags are active, the operator has to remember or re-check the terminal.

**Problem:** Disconnect between launch parameters and what the dashboard shows. The operator might think confidence is 0.4 when it was launched with `--conf 0.2`.

**Decision:** All runtime-affecting CLI flags are reflected in the browser dashboard via two mechanisms:

1. **HTML template injection** — at page load, `__CONF_VAL__`, `__SMART_SPREAD__`, `__SMART_COUNT__` placeholders in the HTML are replaced with actual `args.*` values.
2. **JSON stats endpoint** (`/stats`) — polled every second by the browser. Returns `conf_threshold`, `class_filter`, `active_model_id`, `smart_spread`, `smart_count`, and other runtime state. JavaScript updates the UI elements in real-time.

**Live-adjustable parameters:**
- Confidence threshold — adjustable via browser slider, updates `runtime_state["conf_threshold"]`
- Class filter — dropdown in browser, updates `runtime_state["class_filter"]`
- Model switch — button in browser, triggers `runtime_state["model_switch_request"]`
- These changes propagate to the inference thread within one cycle (~200ms)

**Read-only display:**
- Smart spread/count — shown in the SMART panel header
- Active model name — shown in the stats bar
- FPS counters — camera FPS and inference FPS displayed separately

**Why not a config file:**
- Config file requires restart to take effect
- Browser slider gives instant feedback — operator can tune confidence mid-flight
- `runtime_state` dict is thread-safe (protected by `runtime_lock`)

**Implemented in:** `field_tools/passive_watch.py` (HTML template, `/stats` endpoint, `runtime_state` dict)

---

*Add new decisions as they come up. Format: context → options → decision → rationale.*
