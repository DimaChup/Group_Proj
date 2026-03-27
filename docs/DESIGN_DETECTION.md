# Detection Pipeline Design Decisions

This document records the design rationale behind the detection pipeline in the SAR drone mission system. Each decision is numbered and explains the alternatives considered, the choice made, and the quantitative reasoning behind it.

---

## DD-1: Single-Frame vs Multi-Frame Detection Trigger

**Decision:** Single-frame detection is the default. Each frame that produces a detection above `CONFIDENCE_THRESHOLD` immediately queues the target for investigation. Multi-frame confirmation is available as an opt-in flag (`--smart-detect`) but is not the default.

**Alternatives considered:**

- *Single-frame trigger (chosen):* Any single detection is queued. Fast, aggressive, catches everything.
- *Multi-frame confirmation (`--smart-detect`):* Requires `DETECT_CONFIRM_FRAMES` (3) consecutive frames with a detection before queuing. Reduces false positives but risks missing real targets.

**Rationale:** At a search speed of 6--10 m/s (`SPEED_AT_LOW` to `SPEED_AT_HIGH` in `config.py`) and a camera field of view of approximately 40 m across at 35 m altitude, the dummy is within the frame for roughly 4--7 seconds during a direct flyover. At 4.8 FPS (Pi 5 TFLite inference benchmark), this yields approximately 19--34 frames of visibility. However, at the edge of a scan line the dummy may appear in only 1--2 frames before exiting the field of view. The `--smart-detect` requirement of 3 consecutive detections would miss these edge-of-swath cases entirely.

The asymmetry of costs is decisive: investigating a false positive costs approximately 10 seconds (fly to target, operator presses N, resume search). Missing a real target costs a full rescan pass at lower altitude, adding minutes to the mission and consuming battery. The expected cost of a false positive investigation is far lower than the expected cost of a missed detection.

**Implementation:** In `_handle_search()` within `state_machine.py`, a detection on any single frame calls `_detect_queue.append((lat, lon, conf))`. When `--smart-detect` is active, the counter `_consecutive_detect_count` must reach `DETECT_CONFIRM_FRAMES` before queuing, and resets to zero whenever a frame produces no detection.

---

## DD-2: Detection Queue vs Immediate Divert

**Decision:** Detections are appended to a FIFO queue (`_detect_queue`) and investigated in order. The drone does not immediately divert to a new detection; it finishes its current investigation first.

**Alternatives considered:**

- *Immediate divert:* On each new detection, abandon the current target and fly to the new one.
- *Priority queue (highest confidence first):* Sort detections by confidence and investigate the strongest signal first.
- *FIFO queue (chosen):* Investigate in the order detected.

**Rationale:** Immediate divert causes oscillation. If two targets are visible in alternating frames, the drone bounces between them indefinitely, never reaching either. This failure mode was observed in early simulation testing.

A priority queue sorted by confidence was rejected because confidence is not a reliable indicator of target validity. The same physical object produces different confidence scores depending on viewing angle, lighting, and distance. A target detected at 0.3 from the edge of the field of view may score 0.9 once the drone is directly overhead. Prioritising by confidence would deprioritise detections that are perfectly valid but happened to be seen obliquely.

FIFO ordering is simple and fair: the first target detected is investigated first. The operator handles false positives quickly by pressing N, and the drone moves to the next queued target. Queue management is handled by `_pop_valid_target()`, which re-validates each entry against current rejection lists, NFZ boundaries, and the active search polygon before dispatching.

---

## DD-3: Target Lock During CENTERING (5 m Radius)

**Decision:** When the drone enters the CENTERING state to investigate a target, a lock radius of 5 m (`DETECT_LOCK_RADIUS_M` in `config.py`) is enforced. Only detections within 5 m of the locked target position refine the estimate. Detections outside 5 m are treated as separate targets and queued.

**Alternatives considered:**

- *No lock:* Always track the highest-confidence detection in the current frame.
- *Hard lock (ignore all other detections):* Only track the locked target, discard everything else.
- *Soft lock with radius (chosen):* Refine within radius, queue outside it.

**Rationale:** Without a lock, a second target (B) visible from the hover position above target A will capture the drone's attention if it has higher confidence, causing the drone to drift between A and B. This was observed in simulation when two objects were within 20 m of each other.

A hard lock (ignore everything) risks missing a nearby target that the drone will not see again once it moves on. The soft lock with a 5 m radius solves both problems: detections within 5 m are treated as the same physical object and refine the GPS estimate, while detections outside 5 m are queued for later investigation.

The 5 m value was chosen based on GPS noise characteristics. Real GPS has a CEP (Circular Error Probable) of 2--3 m, meaning the estimated position of the same stationary object varies by up to 3 m between readings. A 5 m radius comfortably encompasses this noise while remaining tight enough to distinguish objects that are physically separate.

**Implementation:** In `_handle_centering()`, when a detection is found, the distance to `_locked_target` is computed. If within `DETECT_LOCK_RADIUS_M`, the locked target position is updated. Otherwise, the detection is appended to `_detect_queue` and the locked target position is restored for continued navigation.

---

## DD-4: Rejection Radius (5 m)

**Decision:** After the operator presses N (false positive) or I (item of interest), the target's GPS position is recorded. All future detections within 5 m (`REJECTED_TARGET_RADIUS_M` in `config.py`) of any rejected or identified position are silently ignored.

**Alternatives considered:**

- *3 m radius:* Matches GPS CEP. Tight, minimal suppression.
- *5 m radius (chosen):* Accounts for viewing angle variation.
- *10 m radius:* Aggressive suppression, risks masking nearby real targets.

**Rationale:** The rejection radius must be large enough to prevent re-investigation of the same physical object when seen from different angles. When the drone flies over the same object on adjacent scan lines, the GPS estimate shifts by 3--4 m due to the change in viewing geometry (the pixel-to-GPS projection changes with the drone's position relative to the object). A 3 m radius was tested in simulation and caused re-investigation of already-rejected targets. A 5 m radius eliminated this problem without suppressing detections of distinct objects more than approximately 7 m apart.

**Implementation:** The `_is_near_known()` helper iterates over `rejected_targets`, `items_of_interest`, and the current `_detect_queue`, returning `True` if the candidate position is within `REJECTED_TARGET_RADIUS_M` of any known point. This check is applied at three stages: when a detection is first produced in SEARCH, when a detection occurs during CENTERING (outside the lock radius), and when `_pop_valid_target()` dequeues entries for investigation.

---

## DD-5: NFZ Auto-Ignore

**Decision:** Detections whose estimated GPS position falls inside the No-Fly Zone (SSSI boundary defined in KML) are silently discarded. No operator notification is generated.

**Rationale:** The drone must never fly into the NFZ to investigate a detection. The geofence system (`geofence.py`) enforces hard boundaries with speed ramps and repulsive forces near the NFZ, but queuing a target inside the NFZ would create a conflict between the state machine (which wants to fly to the target) and the geofence (which prevents it). Dropping the detection at source eliminates this conflict entirely.

Silent discarding is appropriate because the operator does not need to make a decision about an unreachable target. The detection is simply a false positive from the mission's perspective, regardless of whether a real object exists there.

**Implementation:** In `_handle_search()`, after computing the target GPS position, `_is_inside_nfz()` calls `geofence.distance_to_boundary()` and checks the `inside` flag. If inside, `target_found` is set to `False` and the consecutive detection counter is reset.

---

## DD-6: Search Area Boundary Enforcement

**Decision:** Detections whose estimated GPS position falls outside the active search polygon are ignored. Additionally, all queue pops via `_pop_valid_target()` re-validate each entry against the current search polygon before dispatching.

**Rationale:** The search polygon may change during the mission. When a PLB (Personal Locator Beacon) signal is received (simulated via the B key or `--beacon-delay`), the active search area switches from the full survey polygon to a smaller focus area (`FOCUS_AREA_GPS` in `config.py`). Targets queued before the beacon signal may now lie outside the new polygon. Without re-validation, the drone would leave the focus area to investigate stale detections, wasting time and battery.

The `_pop_valid_target()` helper applies three checks to each dequeued entry: `_is_inside_nfz()`, `_is_outside_search_area()`, and `_is_near_known()`. Invalid entries are silently skipped with a log message. This ensures the queue is self-cleaning without requiring explicit purge logic when the search area changes.

**Implementation:** `_is_outside_search_area()` uses `cv2.pointPolygonTest()` against the planner's current search polygon (pixel coordinates). A negative result indicates the point is outside. This is checked both at detection time in `_handle_search()` and at dispatch time in `_pop_valid_target()`.

---

## DD-7: Confidence Threshold (0.1)

**Decision:** The minimum detection confidence is set to 0.1 (`CONFIDENCE_THRESHOLD` in `config.py`). This is deliberately low.

**Alternatives considered:**

- *0.4--0.5 (typical YOLOv8 default):* Filters most noise, but risks missing the real target at altitude or in poor lighting.
- *0.2--0.3 (moderate):* Catches weak signals, some false positives.
- *0.1 (chosen):* Catches almost everything. The operator sorts it out.

**Rationale:** The mission objective is to find one specific target (a casualty/dummy) in a large search area. A missed detection has severe consequences (failed mission), while a false positive has minor consequences (a few seconds of operator time pressing N). This asymmetry demands a low threshold.

The YOLOv8n model trained on the project's custom dataset (`cv_models/sar_v2_1088/`) is well-calibrated: real dummy detections consistently score above 0.8, while false positives from terrain features, shadows, and vegetation typically fall in the 0.1--0.4 range. A threshold of 0.1 captures all real detections with high margin while also catching weak signals from partially occluded or distant targets.

The deduplication system (rejection radius, NFZ filtering, search boundary checks) prevents false positives from flooding the queue. In practice, only a handful of false positives are queued per scan pass, each taking approximately 10 seconds to dismiss.

**Configuration:** The threshold is read by `vision.py` at startup via `config.CONFIDENCE_THRESHOLD` and applied in both the TFLite and Ultralytics inference paths. It can be adjusted in `config.py` without code changes.

---

## DD-8: Manual Mode Detection Queuing

**Decision:** When the operator engages manual flight mode (M key), the detection pipeline continues running. Detections are queued with all standard filters (NFZ, search boundary, deduplication) but no autonomous action is taken. When the operator exits manual mode, the queue is checked before returning to the automated search pattern.

**Alternatives considered:**

- *Disable detection in manual mode:* Simplest, but risks missing targets during manual exploration.
- *Queue detections (chosen):* Detection continues passively, targets accumulate for later.
- *Immediate alert to operator:* Show detection on screen but don't queue.

**Rationale:** Manual mode is used when the operator wants direct control, typically to visually inspect an area or manoeuvre around an obstacle. The camera is still active and pointed at the ground. Disabling detection during this time wastes frames that could contain the target.

By queuing detections, the system ensures that any target glimpsed during manual flight is not lost. On resume from manual mode, `_pop_valid_target()` is called first. If the queue contains valid entries, the drone proceeds to investigate them immediately rather than flying back to its departure point on the scan line. This is more efficient than returning to the pattern and potentially re-scanning the same area.

**Implementation:** In `_handle_keys()`, the block guarded by `self.state == State.MANUAL and target_found` computes the detection GPS position, applies all three filters (`_is_inside_nfz`, `_is_outside_search_area`, `_is_near_known`), and appends to `_detect_queue` if valid. On exiting manual mode (M key pressed again), the resume logic calls `_pop_valid_target()` before deciding whether to return to the scan line or investigate a queued detection.

---

## DD-9: Single Detection Per Frame

**Decision:** `vision.py` returns only the single highest-confidence detection per frame. The `detect_in_image()` function signature is `(found, x, y, confidence)`, not a list of detections.

**Alternatives considered:**

- *Return all detections above threshold:* More information per frame, but increases complexity.
- *Return top-N detections:* Compromise, but still adds complexity.
- *Return single best detection (chosen):* Simplest interface, sufficient for the mission.

**Rationale:** The mission scenario involves a single casualty target in the search area. Multiple dummy objects in the same frame are not expected during the real mission. YOLOv8 may produce multiple bounding boxes for the same object (overlapping detections at different scales), and returning all of them would flood the queue with duplicate entries for the same physical target.

The single-detection interface keeps the `vision.py` API clean. The state machine receives one detection per frame cycle and applies GPS estimation, deduplication, and queuing to that single point. Over multiple frames, different objects naturally emerge as separate queue entries because the drone's movement changes which object has the highest confidence in each frame.

For the YOLOv8 Ultralytics backend, the implementation selects `max(results[0].boxes, key=lambda x: x.conf[0])`. For the TFLite and NCNN backends, it iterates over all detections and retains the one with the highest confidence above threshold.

---

## DD-10: Future Improvements

The following improvements have been identified but not implemented, as the current pipeline is sufficient for the project's testing and demonstration requirements.

**Confidence-tiered detection.** Rather than a single threshold, use two tiers: detections in the 0.1--0.5 range would require 2 or more hits from nearby frames before queuing (a soft version of `--smart-detect`), while detections above 0.5 would queue immediately. This would reduce false positive investigations without the strict consecutive-frame requirement of `--smart-detect`.

**End-of-line investigation.** Currently, the drone diverts to investigate a queued target as soon as the queue is non-empty, even mid-scan-line. An alternative would be to defer investigation until the current scan line is complete, reducing unnecessary backtracking. The trade-off is increased latency between detection and investigation.

**Multi-detection per frame.** Returning all detections above threshold from `detect_in_image()` would allow the queue to accumulate targets faster during a single flyover, particularly useful at lower altitudes where the field of view is smaller and multiple objects may be present. This would require changes to the `vision.py` interface and the queuing logic in `_handle_search()`.

**Temporal GPS smoothing.** Currently, each detection produces a single GPS estimate based on the drone's position and the pixel offset at that instant. Averaging GPS estimates across multiple frames for the same physical object (using spatial clustering) would improve target localisation accuracy, particularly at higher speeds where GPS timing lag introduces 1--2 m of along-track error.
