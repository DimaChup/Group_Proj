# Threaded Vision Pipeline Design

> Design document for overlapping capture, inference, and streaming in the SAR drone
> vision system. Written for `vision.py`, consumed by `main.py`, `pi_flight.py`, and
> `passive_watch.py`.

---

## 1. Problem

The current vision loop is strictly sequential:

```
capture frame  -->  YOLO inference  -->  draw overlay  -->  encode JPEG  -->  stream
   ~10ms              ~200ms              ~1ms              ~3ms             ~2ms
                                                                    TOTAL: ~216ms = 4.6 FPS
```

Every step blocks the next. The operator's MJPEG stream refreshes at the same 4.6 FPS
as inference, making the video feed choppy and harder to visually track the target.
Meanwhile the camera sits idle for 200ms out of every 216ms cycle.

### What we lose

| Metric | Current | Problem |
|--------|---------|---------|
| Stream FPS | 4.6 | Choppy video, hard to judge target |
| Frame freshness | 0-216ms stale | Inference runs on a frame that may be 200ms old |
| Capture duty cycle | 5% | Camera idle 95% of the time |
| Telemetry loop rate | Blocked | main.py can't read MAVLink while inference runs |

---

## 2. Design

Three threads plus the existing main thread:

```
┌──────────────────────────────────────────────────────────────────────┐
│                                                                      │
│  Thread 1: CAPTURE              Thread 2: INFERENCE                  │
│  ┌────────────────────┐         ┌──────────────────────────┐        │
│  │ loop:              │         │ loop:                    │        │
│  │   frame = camera() │         │   wait for new_frame     │        │
│  │   lock:            │         │   lock:                  │        │
│  │     latest = frame │         │     frame = latest.copy()│        │
│  │   signal new_frame │         │   result = YOLO(frame)   │        │
│  │   sleep(30ms)      │         │   lock:                  │        │
│  └────────────────────┘         │     detection = result   │        │
│          │                      │     annotated = frame    │        │
│          │                      │   signal new_result      │        │
│          ▼                      └──────────────────────────┘        │
│   shared_frame buffer                    │                          │
│          │                               ▼                          │
│          │                      shared_detection buffer              │
│          │                               │                          │
│  Thread 3: STREAM               Main thread: STATE MACHINE          │
│  ┌────────────────────┐         ┌──────────────────────────┐        │
│  │ loop:              │         │ loop:                    │        │
│  │   lock:            │         │   update_telemetry()     │        │
│  │     if annotated:  │         │   lock:                  │        │
│  │       jpeg=encode()│         │     det = detection      │        │
│  │     else:          │         │   state_dispatch(det)    │        │
│  │       jpeg=raw     │         │   geofence()             │        │
│  │   serve jpeg       │         │   sleep(20ms)            │        │
│  │   sleep(33ms)      │         └──────────────────────────┘        │
│  └────────────────────┘                                              │
│                                                                      │
└──────────────────────────────────────────────────────────────────────┘
```

### Thread responsibilities

| Thread | Rate | Reads | Writes | Blocks on |
|--------|------|-------|--------|-----------|
| Capture | ~33 FPS (30ms) | camera hardware | `_latest_frame` | camera I/O only |
| Inference | ~5 FPS (200ms) | `_latest_frame` | `_detection_result`, `_annotated_frame` | YOLO compute |
| Stream | ~30 FPS (33ms) | `_annotated_frame` or `_latest_frame` | MJPEG socket | JPEG encode (~3ms) |
| Main | ~50 Hz (20ms) | `_detection_result` | state machine, MAVLink commands | nothing |

### Shared buffers

```python
# Capture → Inference, Capture → Stream
_latest_frame: np.ndarray | None      # most recent raw frame
_frame_lock: threading.Lock()
_frame_event: threading.Event()        # signals new frame available

# Inference → Stream, Inference → Main
_detection_result: DetectionResult     # (found, cx, cy, conf, timestamp)
_annotated_frame: np.ndarray | None    # frame with bbox drawn
_result_lock: threading.Lock()
```

---

## 3. Implementation Sketch

### 3.1 Data structure

```python
from dataclasses import dataclass, field
import time

@dataclass
class DetectionResult:
    found: bool = False
    cx: int = 0
    cy: int = 0
    conf: float = 0.0
    bbox_w: int = 0
    bbox_h: int = 0
    class_name: str = ""
    timestamp: float = field(default_factory=time.time)  # when frame was captured
```

### 3.2 ThreadedVisionSystem (extends VisionSystem)

```python
import threading
import time
import numpy as np
from vision import VisionSystem

class ThreadedVisionSystem(VisionSystem):
    """Drop-in replacement for VisionSystem with threaded capture/inference.

    Usage:
        vs = ThreadedVisionSystem(camera_index=0, model_path="best.tflite")
        vs.start()          # launches capture + inference threads
        ...
        det = vs.get_detection()   # non-blocking, returns latest DetectionResult
        frame = vs.get_display_frame()  # latest annotated or raw frame for stream
        ...
        vs.stop()
    """

    def __init__(self, camera_index=0, model_path="best.tflite"):
        super().__init__(camera_index=camera_index, model_path=model_path)

        # --- Shared state ---
        self._latest_frame = None
        self._frame_lock = threading.Lock()
        self._frame_event = threading.Event()

        self._detection = DetectionResult()
        self._annotated_frame = None
        self._result_lock = threading.Lock()

        self._running = False
        self._capture_thread = None
        self._inference_thread = None

    # ── Lifecycle ──────────────────────────────────────────────

    def start(self):
        """Launch capture and inference threads."""
        self._running = True

        self._capture_thread = threading.Thread(
            target=self._capture_loop, name="capture", daemon=True)
        self._inference_thread = threading.Thread(
            target=self._inference_loop, name="inference", daemon=True)

        self._capture_thread.start()
        self._inference_thread.start()
        print("[VISION] Threaded pipeline started (capture + inference)")

    def stop(self):
        """Signal threads to stop and wait for them."""
        self._running = False
        self._frame_event.set()  # unblock inference if waiting
        if self._capture_thread:
            self._capture_thread.join(timeout=2.0)
        if self._inference_thread:
            self._inference_thread.join(timeout=2.0)
        self.release()
        print("[VISION] Threaded pipeline stopped")

    # ── Capture thread ─────────────────────────────────────────

    def _capture_loop(self):
        """Grab frames as fast as the camera allows, store latest."""
        while self._running:
            frame = self.get_frame()  # inherited from VisionSystem
            if frame is not None:
                with self._frame_lock:
                    self._latest_frame = frame   # overwrite — always newest
                self._frame_event.set()          # wake inference thread
            time.sleep(0.005)  # yield CPU, ~200 Hz max poll rate

    # ── Inference thread ───────────────────────────────────────

    def _inference_loop(self):
        """Wait for new frame, run YOLO, store result."""
        while self._running:
            # Block until capture signals a new frame (or timeout for shutdown check)
            self._frame_event.wait(timeout=0.5)
            self._frame_event.clear()

            if not self._running:
                break

            # Grab latest frame (copy to avoid mutation during inference)
            with self._frame_lock:
                if self._latest_frame is None:
                    continue
                frame = self._latest_frame.copy()
                capture_time = time.time()

            # Run detection (inherited — handles undistort + backend selection)
            found, cx, cy, conf = self.detect_in_image(frame)

            # Store results atomically
            result = DetectionResult(
                found=found, cx=cx, cy=cy, conf=conf,
                bbox_w=self.last_bbox_w, bbox_h=self.last_bbox_h,
                class_name=self.last_class_name,
                timestamp=capture_time,
            )
            with self._result_lock:
                self._detection = result
                self._annotated_frame = frame  # detect_in_image drew bbox on it

    # ── Public interface (called from main thread) ─────────────

    def get_detection(self) -> DetectionResult:
        """Return the latest detection result (non-blocking)."""
        with self._result_lock:
            return self._detection

    def get_display_frame(self) -> 'np.ndarray | None':
        """Return the latest frame for streaming.

        Prefers the annotated frame (with detection bbox). Falls back to
        the raw capture frame if inference hasn't run yet.
        """
        with self._result_lock:
            if self._annotated_frame is not None:
                return self._annotated_frame
        with self._frame_lock:
            return self._latest_frame

    def get_raw_frame(self) -> 'np.ndarray | None':
        """Return the latest raw capture frame (no annotations)."""
        with self._frame_lock:
            if self._latest_frame is not None:
                return self._latest_frame.copy()
            return None
```

### 3.3 Integration with main.py

The change in `update_dashboard()` is minimal. Replace the sequential
capture-then-detect block with a single non-blocking read:

```python
# BEFORE (sequential, blocks 200ms):
frame = self.eyes.get_frame()
found, u, v, conf = self.eyes.detect_in_image(frame)

# AFTER (non-blocking, <0.01ms):
det = self.eyes.get_detection()
found, u, v, conf = det.found, det.cx, det.cy, det.conf
frame = self.eyes.get_display_frame()
```

The main loop goes from ~216ms/iteration to ~20ms/iteration. Telemetry is read
50x/second instead of 5x/second. State machine reacts to detections within 20ms
of them being produced.

### 3.4 Integration with pi_flight.py

Same pattern. The existing `_frame_lock` and `_stream_jpeg` in pi_flight.py
already follow this model for the stream thread. Replace:

```python
# BEFORE:
frame = self.get_frame()
found, u, v, conf = self.eyes.detect_in_image(frame)
_, jpeg = cv2.imencode('.jpg', frame, ...)

# AFTER:
det = self.eyes.get_detection()
found, u, v, conf = det.found, det.cx, det.cy, det.conf
frame = self.eyes.get_display_frame()
if frame is not None:
    _, jpeg = cv2.imencode('.jpg', frame, ...)
```

### 3.5 Stream thread (optional, for dedicated MJPEG server)

The existing HTTP stream handlers in `stream_server.py` and `pi_flight.py` already
run in their own threads. They just need to call `get_display_frame()` instead of
reading from a manually-set buffer. No new stream thread is needed unless we want
to decouple JPEG encoding from the HTTP handler:

```python
# Optional: dedicated encode thread for consistent 30 FPS JPEG output
def _stream_encode_loop(self):
    """Encode latest frame to JPEG at fixed rate for MJPEG clients."""
    while self._running:
        frame = self.eyes.get_display_frame()
        if frame is not None:
            _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 80])
            with self._stream_lock:
                self._stream_jpeg = jpeg.tobytes()
        time.sleep(0.033)  # ~30 FPS
```

---

## 4. Expected Performance

| Metric | Before | After | Improvement |
|--------|--------|-------|-------------|
| **Stream FPS** | 4.6 | ~30 | 6.5x smoother video |
| **Detection FPS** | 4.6 | ~4.8 | Same (still 200ms inference) |
| **Frame staleness** | 0-216ms | 0-30ms | 7x fresher frames for inference |
| **Main loop rate** | 4.6 Hz | ~50 Hz | 10x faster telemetry + state machine |
| **Operator experience** | Choppy slideshow | Smooth video with bbox overlay | Major UX improvement |

Detection throughput stays at ~5 FPS because YOLO inference still takes 200ms.
But the operator sees smooth 30 FPS video, and the state machine runs at 50 Hz
instead of being blocked by inference.

---

## 5. Risks and Mitigations

### 5.1 Thread safety on detection results

**Risk**: Main thread reads `(found, cx, cy, conf)` while inference thread writes it,
getting a torn read (e.g., `found=True` from detection N but `cx, cy` from detection N-1).

**Mitigation**: The `DetectionResult` dataclass is written atomically under
`_result_lock`. The main thread copies the whole object in one lock acquisition.
No partial reads are possible.

### 5.2 Frame-detection mismatch

**Risk**: The annotated frame shown in the stream may not match the detection result
the state machine acts on, if inference completes between the two reads.

**Mitigation**: Both `_detection` and `_annotated_frame` are written together inside
the same lock in `_inference_loop`. Reading them together in `get_detection()` +
`get_display_frame()` is two separate lock acquisitions, so there is a small window.
In practice this is harmless: the worst case is the stream shows a bbox from the
detection one frame before the state machine acts on it (30ms difference). For SAR
operations this is imperceptible.

If strict consistency is ever needed, add a `get_detection_and_frame()` method that
returns both under a single lock.

### 5.3 CPU contention

**Risk**: Pi 5 has 4 cores. Three threads + main all competing for CPU could slow
inference.

**Mitigation**: Thread activity profile is heavily asymmetric:
- Capture thread: ~1ms active per 30ms cycle (3% CPU)
- Stream encode: ~3ms active per 33ms cycle (9% CPU)
- Inference thread: ~200ms continuous (100% of one core)
- Main thread: ~1ms active per 20ms cycle (5% CPU)

Total: ~1.17 cores. Pi 5 has 4 cores. Inference is the bottleneck and it gets a
full core to itself. The other threads combined use ~17% of one core. GIL is not a
concern because the heavy work (YOLO C++ inference, numpy operations, JPEG encoding)
all release the GIL.

### 5.4 picamera2 thread safety

**Risk**: picamera2's `capture_array()` may not be safe to call from a non-main thread.

**Mitigation**: picamera2 is thread-safe for `capture_array()` calls. The library
internally uses its own threading for the camera pipeline. The only requirement is
that `start()` and `stop()` are called from the same thread (which they are -- both
happen in `__init__` and `release()` on the main thread). Confirmed by picamera2 docs
and community usage.

### 5.5 Memory: double-buffering cost

**Risk**: `frame.copy()` in the inference thread allocates a new 1456x1088x3 array
(~4.7 MB) every 200ms.

**Mitigation**: 4.7 MB every 200ms = 23.5 MB/s allocation rate. Python's memory
allocator handles this easily. The old frame is freed immediately. If profiling
shows GC pressure, pre-allocate two buffers and swap pointers (true double-buffer),
but this is unlikely to matter.

---

## 6. Recommendation

**Yes, implement this.** The effort-to-benefit ratio is excellent.

### Why it's worth it

1. **Operator UX**: The operator confirming Y/N on a target needs smooth video to
   judge whether the detection is a real casualty or a false positive. 4.6 FPS is a
   slideshow. 30 FPS is usable video. This directly impacts mission success.

2. **Telemetry responsiveness**: The main loop currently reads MAVLink at 4.6 Hz.
   At 50 Hz, GPS degradation, RC failsafe, and link-lost detection all trigger
   faster. This is a safety improvement.

3. **Low risk**: The threaded system is a wrapper around the existing `VisionSystem`.
   If anything goes wrong, revert to `VisionSystem` by changing one line in
   `__init__`. The fallback is zero-risk.

4. **Low effort**: ~2-3 hours for implementation + testing. The code sketch above
   is nearly complete. The integration points in main.py and pi_flight.py are
   2-3 line changes each.

### What it does NOT improve

- Detection FPS stays at ~5 (inference is the bottleneck, and that requires
  a faster model or hardware accelerator like Hailo-8L).
- Detection accuracy is unchanged.
- Power consumption slightly increases (camera polled continuously instead of
  on-demand), but the difference is negligible.

### Implementation order

1. Create `threaded_vision.py` with `ThreadedVisionSystem` class
2. Test standalone: instantiate, start, print detections for 10 seconds, stop
3. Integrate into `pi_flight.py` first (simpler loop, web stream benefits most)
4. Integrate into `main.py`
5. Benchmark on Pi: confirm inference FPS unchanged, stream FPS at 30

### Fallback

If threaded mode causes any issues on flight day, the switch is one line:

```python
# Threaded (normal):
self.eyes = ThreadedVisionSystem(camera_index=0, model_path=MODEL_PATH)
self.eyes.start()

# Fallback (sequential, proven):
self.eyes = VisionSystem(camera_index=0, model_path=MODEL_PATH)
```

No other code changes needed. `get_detection()` and `get_display_frame()` can be
added to the base `VisionSystem` as synchronous wrappers so the calling code doesn't
need to change at all.

---

## 7. Compatibility Notes

- **picamera2**: Thread-safe for `capture_array()`. No issues expected.
- **TFLite interpreter**: Thread-safe for single-interpreter single-thread inference
  (which is what we do -- one interpreter, one inference thread). Do NOT call
  `invoke()` from multiple threads simultaneously.
- **OpenCV VideoCapture**: Thread-safe for `read()` on a single capture object.
- **GIL**: Not a concern. YOLO inference (C++), numpy ops, and JPEG encoding all
  release the GIL. Only the Python lock acquisition (~microseconds) is serialized.
- **Python 3.13 on Pi**: No known threading regressions. The free-threaded build
  (3.13t) is not needed; standard 3.13 works fine.
