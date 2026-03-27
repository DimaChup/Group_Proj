# Streaming Analysis: Pi 5 Video + YOLOv8n Inference

> Evaluating streaming approaches for live SAR drone video from Raspberry Pi 5
> (IMX296 camera, TFLite YOLOv8n at ~4.8 FPS) to a ground station laptop over
> private WiFi at ~10m range.

---

## 1. Current Architecture

The project has three streaming implementations, all using MJPEG over HTTP:

| Component | Location | Pattern |
|-----------|----------|---------|
| `stream_server.py` | Shared module | Thread-safe frame buffer, MJPEG push, telemetry JSON, operator commands |
| `main.py` | Mission orchestrator | Single-thread: capture -> detect -> `set_stream_frame()` -> loop |
| `pi_flight.py` | Web ground station | Same single-thread pattern, inline MJPEG handler |
| `camera_stream_fast.py` | Test/diagnostic | **Threaded**: capture in main, detection in background thread |
| `camera_stream_h264.py` | Test/diagnostic | FFmpeg H.264/HLS pipeline, 2-4s latency |

**Current main.py flow (single-threaded):**
```
capture frame (picamera2)    ~5ms
  -> undistort (remap)       ~1.5ms
  -> TFLite inference        ~206ms
  -> draw overlay            ~0.5ms
  -> set_stream_frame()      ~0ms (lock + pointer swap)
  -> JPEG encode (320x240)   ~2ms (in HTTP handler thread)
  -> push to browser         ~1ms
                             --------
  Total loop: ~215ms = 4.6 FPS for both stream AND inference
```

The stream FPS is capped by inference time. The browser sees ~4.6 FPS video with
~215ms frame-to-display latency (plus network transit ~1-5ms on local WiFi).

**Current stream settings:**
- Resolution: 320x240 (downscaled from 1456x1088 capture)
- JPEG quality: 50%
- Frame size: ~15-50 KB per frame (depends on scene complexity)
- Bandwidth: ~0.5-1.5 Mbps at 5 FPS
- Latency: ~220ms (inference + encode + network)

---

## 2. Approach Evaluation

### 2.1 MJPEG over HTTP (Current)

**How it works:** Each frame is independently JPEG-encoded and pushed as a
`multipart/x-mixed-replace` HTTP response. The browser's `<img>` tag natively
renders the stream with zero JavaScript.

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Latency | Excellent (~200ms) | One-frame delay, no segmentation buffer |
| Reliability | Excellent | Works in every browser, degrades gracefully |
| CPU cost | Low | JPEG encode at 320x240 takes ~2ms on Pi 5 |
| Bandwidth | Moderate | ~30KB/frame x 5fps = 1.2 Mbps |
| Complexity | Minimal | 50 lines of Python, no dependencies beyond cv2 |

**Verdict: Keep as primary.** For a private WiFi link at 10m range, bandwidth is
not a constraint (typical 802.11n delivers 50+ Mbps). The simplicity and low latency
make MJPEG the right choice for SAR operator situational awareness.

**Optimization opportunity:** The current 320x240 at quality 50% is quite aggressive.
At 480x360 quality 60%, frames would be ~40KB each, giving ~1.6 Mbps at 5 FPS --
still well within WiFi capacity but noticeably sharper for the operator.

### 2.2 H.264 / HLS (Implemented in camera_stream_h264.py)

**How it works:** Raw frames are piped to an FFmpeg subprocess that encodes H.264
and outputs HLS segments (.ts files, ~1s each). A built-in HTTP server serves the
HLS playlist. The browser uses hls.js to play back.

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Latency | Poor (2-4s) | HLS segments impose minimum 2-3 segment delay |
| Reliability | Good | Standard protocol, but needs FFmpeg installed |
| CPU cost | Moderate | libx264 software encode uses ~15% of one Pi 5 core |
| Bandwidth | Excellent | 10x less than MJPEG (~0.1-0.2 Mbps) |
| Complexity | Moderate | FFmpeg subprocess, temp directory, hls.js CDN dependency |

**Verdict: Not recommended for primary use.** The 2-4 second latency is unacceptable
for operator decision-making during VERIFY state (Y/N/I confirmation). HLS is designed
for broadcast/VOD, not real-time control.

**When it makes sense:** Long-range cellular backhaul, recording for later review, or
if streaming at 720p+ resolution over constrained bandwidth. None of these apply to
the current SAR mission (private WiFi, 10m range, 320-480px stream).

**Note on Pi hardware encoder:** The Pi 5's VideoCore VII can encode H.264 in hardware
via `h264_v4l2m2m`, which would reduce CPU cost to near zero. However, HLS latency
remains the fundamental problem. Hardware encoding would only help if combined with a
low-latency transport (see WebRTC below).

### 2.3 WebRTC

**How it works:** Peer-to-peer media channel with H.264 hardware encoding, DTLS
encryption, and adaptive bitrate. Requires a signaling server (WebSocket) for
connection setup.

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Latency | Excellent (~100-300ms) | Sub-frame latency with hardware encode |
| Reliability | Mixed | NAT traversal, ICE negotiation can fail; overkill for direct WiFi |
| CPU cost | Low (with HW encode) | Pi 5 H.264 hardware encoder handles 1080p30 |
| Bandwidth | Excellent | Adaptive bitrate, inter-frame compression |
| Complexity | High | aiortc (~15 deps), signaling server, STUN/TURN for NAT |

**Verdict: Overkill for this project.** WebRTC solves problems we do not have (NAT
traversal, adaptive bitrate for variable networks). On a direct WiFi link, the
complexity cost far outweighs the marginal latency improvement over MJPEG.

**The aiortc library** (Python WebRTC) adds ~15 dependencies including cffi, cryptography,
and pylibsrtp. It works, but debugging WebRTC issues on flight day is not how you want
to spend your time.

**When it makes sense:** Multi-hop networks, cellular, public internet, or if you need
two-way audio. Not applicable here.

### 2.4 RTSP / GStreamer

**How it works:** GStreamer pipeline captures from picamera2, encodes H.264 via
hardware encoder, and serves an RTSP stream. Clients use VLC, GStreamer, or
ffplay to view.

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Latency | Good (~200-500ms) | Depends on client buffer settings |
| Reliability | Good | Industry standard, mature |
| CPU cost | Low (with HW encode) | Same hardware encoder as WebRTC |
| Bandwidth | Excellent | H.264 inter-frame compression |
| Complexity | Moderate | GStreamer pipeline syntax, not browser-native |

**Verdict: Good alternative but wrong fit.** RTSP is not natively supported in
browsers -- the operator would need VLC or a separate player window alongside the
dashboard. This breaks the single-page ground station design (telemetry + video +
buttons in one browser tab).

**Hybrid possibility:** Use RTSP for high-quality recording/archival while MJPEG
serves the browser dashboard. This adds complexity for marginal benefit on a
university project timeline.

**When it makes sense:** Integration with existing ground station software (QGroundControl,
Mission Planner video), multi-client streaming, or professional recording pipelines.

### 2.5 Threaded Pipeline (Already Implemented in camera_stream_fast.py)

**How it works:** Camera capture runs in the main thread at full camera rate
(~25+ FPS). AI detection runs in a separate daemon thread at inference speed
(~4.8 FPS). The stream always shows the latest camera frame with the most recent
detection overlay.

| Criterion | Rating | Notes |
|-----------|--------|-------|
| Stream FPS | 15-25 FPS | Decoupled from inference speed |
| Detection FPS | ~4.8 FPS | Same as before -- inference is the bottleneck |
| Latency | Excellent | Latest frame always available, ~30-60ms capture-to-stream |
| CPU cost | Same | Inference still takes ~206ms, just runs in parallel |
| Complexity | Low | One `threading.Thread`, one shared lock |

**Verdict: Adopt this pattern in main.py.** This is the single highest-impact
improvement. The operator sees smooth video at 10-15 FPS instead of stuttery
4.6 FPS. Detection results update asynchronously -- the overlay "snaps" to a
new position every ~210ms, which is perfectly acceptable for SAR.

`camera_stream_fast.py` already proves this works. The pattern needs to be
integrated into main.py's mission loop.

---

## 3. Recommendation: Threaded MJPEG (Best of Both Worlds)

### Architecture

```
Thread 1: CAPTURE (main)              Thread 2: INFERENCE (daemon)
  picamera2.capture_array()             grab latest_frame (lock)
  -> latest_frame (lock)                -> undistort
  -> draw overlay from last result      -> TFLite inference (~206ms)
  -> set_stream_frame()                 -> update det_result (lock)
  -> loop at ~15-25 FPS                 -> loop at ~4.8 FPS

Thread 3: HTTP SERVER (daemon)
  /stream  -> MJPEG from latest_frame
  /status  -> JSON telemetry
  /cmd     -> operator commands
  /        -> dashboard HTML
```

### Why This Wins

1. **Stream FPS jumps from 4.6 to 15+ FPS.** The operator gets smooth video instead
   of a slideshow. Detection overlay updates every ~210ms regardless.

2. **Detection rate is unchanged.** TFLite still runs at 4.8 FPS on the same frames.
   The only difference is that the stream is not blocked waiting for inference.

3. **Latency improves.** Current: 215ms (capture + inference + stream). Threaded:
   ~40ms (capture + JPEG encode + network). Detection results lag by one inference
   cycle (~210ms), but the camera view is live.

4. **Zero new dependencies.** Uses `threading.Thread` and `threading.Lock` from
   stdlib. Already proven in `camera_stream_fast.py`.

5. **No protocol change.** MJPEG stays as the transport. Browser compatibility,
   dashboard integration, and operator buttons all work unchanged.

### Resolution Strategy

| Purpose | Resolution | Why |
|---------|-----------|-----|
| Camera capture | 1456x1088 | IMX296 native, maximum detail for inference |
| AI inference input | 640x640 | YOLOv8n model input (resized internally by vision.py) |
| Stream to browser | 480x360 | Good visual quality at ~40KB/frame, 2.4 Mbps at 8 FPS |
| Stream to browser (alt) | 320x240 | Current default, ~20KB/frame, use if WiFi is weak |

The capture resolution should stay at 1456x1088 for maximum detection accuracy.
The stream resolution is independent -- downscaling happens in the HTTP handler
after the frame buffer is updated.

### Bandwidth Budget

On private 802.11n WiFi at 10m range (practical throughput ~30-50 Mbps):

| Stream Config | Frame Size | FPS | Bandwidth | % of WiFi |
|---------------|-----------|-----|-----------|-----------|
| 320x240 Q50 | ~20 KB | 5 | 0.8 Mbps | 1.6% |
| 320x240 Q50 | ~20 KB | 10 | 1.6 Mbps | 3.2% |
| 480x360 Q60 | ~40 KB | 8 | 2.6 Mbps | 5.1% |
| 480x360 Q70 | ~55 KB | 10 | 4.4 Mbps | 8.8% |
| 640x480 Q70 | ~80 KB | 10 | 6.4 Mbps | 12.8% |

All configurations are well within WiFi capacity. The mavlink telemetry stream
uses ~50 Kbps, negligible by comparison.

**Recommendation:** 480x360 at quality 60%, 8 FPS. Sharp enough for the operator
to assess the scene, low enough bandwidth to be rock-solid.

---

## 4. Implementation Plan

### Phase 1: Integrate Threaded Pattern into main.py (Priority: HIGH)

The existing `camera_stream_fast.py` proves the pattern. Integration into main.py
requires these changes:

1. **Separate capture from inference.** Move `detect_in_image()` into a daemon thread
   that grabs the latest frame from a shared buffer, runs inference, and stores the
   result in a thread-safe dict.

2. **Main loop captures and streams.** The main mission loop calls `get_frame()`,
   reads the latest detection result (lock), makes state machine decisions, and
   pushes the frame to `stream_server.py`.

3. **State machine reads detection results.** Instead of calling `detect_in_image()`
   synchronously, the state machine reads `det_result` which updates at ~4.8 FPS.
   This is functionally identical -- the state machine already only acts on the
   "latest" detection.

4. **Frame synchronization.** The detection result includes the frame timestamp or
   sequence number so the state machine knows how fresh the detection is. If the
   last detection is >500ms old, treat it as stale.

**Estimated effort:** 2-3 hours. Most of the code already exists in `camera_stream_fast.py`.

### Phase 2: Tune Stream Parameters (Priority: MEDIUM)

Update `stream_server.py` defaults and main.py constants:

```python
# main.py
STREAM_W, STREAM_H = 480, 360    # was 320, 240
STREAM_FPS = 8                    # was 5
STREAM_QUALITY = 60               # was 50
```

Test on Pi over WiFi to confirm smooth playback without frame drops.

### Phase 3: Optional Enhancements (Priority: LOW)

These are future improvements, not needed for the current mission:

- **Adaptive quality:** If the HTTP handler detects slow writes (> 100ms per frame
  push), reduce quality or resolution automatically.
- **JPEG turbo:** Replace cv2.imencode with `turbojpeg` library for ~30% faster
  JPEG encoding. Only matters if encoding becomes a bottleneck at higher resolutions.
- **Dual stream:** Serve both a low-res fast stream (operator) and a high-res slow
  stream (recording/review) on different endpoints. `camera_stream_fast.py` already
  has `/stream-ai` for this.

---

## 5. Thread Safety Considerations

The threaded pattern introduces shared mutable state. Here is how to keep it safe:

| Shared Resource | Protection | Notes |
|----------------|-----------|-------|
| `latest_frame` | `threading.Lock` | Written by capture thread, read by inference + HTTP |
| `det_result` | `threading.Lock` | Written by inference thread, read by main + HTTP |
| `stream_server._stream_frame` | Already has `_stream_lock` | No change needed |
| `VisionSystem` instance | Single-writer | Only inference thread calls `detect_in_image()` |
| State machine state | Main thread only | Inference thread never modifies mission state |

**Critical rule:** The inference thread must NEVER call any mavlink function or modify
mission state. It only reads frames and writes detection results. All flight decisions
remain in the main thread.

**Frame copying:** The inference thread should `frame.copy()` the shared frame before
running detection, because `detect_in_image()` mutates the frame (draws bounding boxes).
This is already done in `camera_stream_fast.py` line 245.

---

## 6. Comparison Summary

| Approach | Latency | Stream FPS | Bandwidth | Complexity | Browser | Verdict |
|----------|---------|-----------|-----------|------------|---------|---------|
| MJPEG (current) | ~220ms | 4.6 | 1.2 Mbps | Minimal | Native | Keep, but thread it |
| MJPEG + threads | ~40ms* | 15+ | 2.6 Mbps | Low | Native | **RECOMMENDED** |
| H.264/HLS | 2-4s | 5-30 | 0.2 Mbps | Moderate | hls.js | Not for real-time |
| WebRTC | ~150ms | 30 | 0.5 Mbps | High | JS SDK | Overkill |
| RTSP | ~300ms | 30 | 0.3 Mbps | Moderate | No | Wrong UI model |

*Detection overlay lags by ~210ms (one inference cycle), but the camera image is live.

**Bottom line:** Adopt the threaded MJPEG pattern from `camera_stream_fast.py` into
main.py. This gives the biggest improvement (4.6 -> 15+ FPS stream) with the least
risk (proven code, zero new dependencies, same protocol). Everything else is either
overkill (WebRTC), too laggy (HLS), or breaks the browser dashboard (RTSP).

---

## 7. Quick Reference: What Exists vs What To Build

| Already exists | Location | Status |
|---------------|----------|--------|
| MJPEG stream server | `stream_server.py` | Production-ready, used by main.py |
| Threaded capture + inference | `camera_stream_fast.py` | Proven in testing |
| H.264/HLS pipeline | `camera_stream_h264.py` | Works but 2-4s latency |
| Dashboard with telemetry | `stream_server.py` HTML | Production-ready |

| To build | Effort | Impact |
|----------|--------|--------|
| Merge threaded pattern into main.py | 2-3 hours | Stream FPS: 4.6 -> 15+ |
| Bump stream defaults (480x360 Q60) | 5 minutes | Sharper operator view |
| Stale detection timeout | 30 minutes | Safety: ignore old detections |
