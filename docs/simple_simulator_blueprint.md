# simple_simulator.py — Interactive Flight Simulator MVP

Blueprint (map, not code copy). 2508 lines total.

## Sections

| Section | Lines | Purpose |
|---------|-------|---------|
| Docstring + imports | 1-42 | Module overview, keyboard controls |
| SimpleMission.__init__ | 46-302 | MAVLink, camera, clustering, telemetry, 7 flight modes |
| update_telemetry | 303-357 | MAVLink parse + GPS drift simulation |
| _new_cluster / _gps_distance | 358-384 | Cluster creation with permanent IDs |
| _route_to_cluster | 385-471 | Route observation to nearest cluster, update estimators |
| calculate_target_gps | 472-629 | Pixel-to-GPS: centre-snap, noise, weight, clustering, Kalman |
| _start_investigate / _start_investigate_gps | 630-659 | Begin investigation: set target, phase="approaching", switch active cluster |
| _gps_distance | 661-669 | Haversine distance in metres |
| send_velocity / send_arm / send_to_gps / send_land | 671-726 | MAVLink command helpers (velocity NED, arm/GUIDED, GPS goto, land) |
| get_frame_and_detect | 728-802 | Frame capture + CV + camera shake simulation |
| draw_hud | 803-1132 | Camera HUD: crosshair, detection markers, status panel |
| draw_dashboard | 1133-1271 | Status dashboard: position, clusters, lock, investigate |
| draw_scatter | 1272-1538 | GPS scatter plot: estimates, error ellipses, landing zone |
| _on_trackbar | 1550-1552 | No-op callback for error control sliders (values read in run loop) |
| run() | 1554-2305 | Main loop: telemetry, CV, flight modes, keyboard, 2x2 grid |
| _show_flight_chart | 2306-2445 | Post-flight matplotlib analysis |
| _mouse_cb | 2446-2479 | Scroll zoom + drag pan |
| __main__ | 2481-2508 | CLI args + instantiation |

## Flight Modes (keyboard)

- **WASD/QE/RF**: manual RC (velocity commands)
- **C**: GPS centering (fly to best_gps estimate)
- **V**: Visual servo (centre target in frame, EMA smoothing)
- **N**: Investigate cluster (approach -> descend 15m -> observe)
- **G**: GPS lock (30s averaging while V-centred)
- **L**: Offset landing (7.5m north of estimate)
- **H**: Altitude test (step 30/25/20/15/10m, compare estimators)

## Classification (during observe phase)

- **Y**: Confirm dummy
- **I**: Item of interest (log, resume search)
- **X**: False positive (discard, resume search)

## Three Estimators Per Cluster

1. **Rolling 50** weighted average (responsive, forgets old noise)
2. **Running total** average (stable, cumulative)
3. **Kalman filter** (2D Bayesian, measurement noise = f(weight))

## Cluster Structure

```
{
  id,
  observations [(lat, lon, weight)],
  best_gps,          # rolling 50
  total_gps,         # running total average
  total_wlat/wlon/w, # cumulative weighted sums
  kalman_gps,
  kalman_P,          # 2x2 covariance
  detection_count
}
```

## GPS Estimation Pipeline

```
pixel(u,v)
  -> GSD calculation (altitude / focal_length * sensor_width / image_width)
  -> body-frame offset (dx_m, dy_m from frame centre)
  -> yaw rotation (NED frame)
  -> lat/lon (metres to degrees)

Weight = centre_weight(1-5) * alt_factor((30/alt)^2)
Centre-snap: target within 30px of centre -> weight = 10 * alt_factor
```

## Display: 2x2 Grid

| Top-Left | Top-Right |
|----------|-----------|
| God View (map + clusters + drone) | Camera + HUD (crosshair, detection boxes, status) |

| Bottom-Left | Bottom-Right |
|-------------|--------------|
| Scatter Plot (GPS estimates, error ellipses, landing zone) | Dashboard (position, clusters, lock, investigate) |

## CLI Flags

| Flag | Default | Purpose |
|------|---------|---------|
| `--fps N` | unlimited | Limit CV inference rate (simulate Pi speed) |
| `--tflite` | off | Force TFLite backend instead of Ultralytics |
| `--gps-drift N` | 0 | Ornstein-Uhlenbeck GPS random walk (metres) |
| `--shake N` | 0 | Altitude-dependent camera angular jitter (pixels) |
| `--cluster-dist N` | 30 | Max metres between observations in same cluster |
| `--fov-error N` | 0 | Simulated FOV calibration error |

## `_on_trackbar()` (line 1550-1552)

No-op callback required by `cv2.createTrackbar`. Slider values are read directly
in the run loop (lines 1887-1898) via `cv2.getTrackbarPos()`, not through the callback.

## `run()` Detail (lines 1554-2305)

### Setup (1558-1576)
- Creates "Simple Simulator" window (1280x720) and "Error Controls" window
- 7 sliders: GPS Drift, Alt Noise, Yaw Noise, FOV Error, Shake, Landing Zone, Resolution
- Mouse callback for scroll zoom + drag pan (simulation only)

### Detection + GPS Estimation (1584-1619)
- On each frame: `get_frame_and_detect()` -> if found, `calculate_target_gps(u, v)`
- Terminal log per detection: count, pixel coords, confidence, centre-snap flag, estimate error
- **Detection saving** (1601-1619): when `self.save_detections` is True, saves each detection
  frame as JPEG with green bbox, confidence overlay, altitude + GPS text. Filename encodes
  timestamp, lat, lon, confidence. Saved to `self.det_dir` (detections/ folder).

### Auto-centering — C mode (1621-1626)
- When `self.centering` is True: sends `send_to_gps(best_gps)` every frame
- Sends the same GPS target whether or not current frame has a detection
  (position updates come from `calculate_target_gps` accumulating observations)

### Visual Servo — V mode (1628-1664)
- **EMA smoothing** (1632-1638): first detection initialises `smooth_u/v`, subsequent
  detections blended with `servo_alpha` (0.3). Reduces jitter from camera shake.
  `smooth_u = alpha * u + (1 - alpha) * smooth_u`
- **Proportional control** (1645-1654): pixel error from frame centre ->
  `vel_right = servo_kp * err_x`, `vel_fwd = -servo_kp * err_y` (image y inverted).
  Speed clamped to `servo_max_speed`. Sent via `send_velocity()`.
- **Centre log** (1656-1657): prints "CENTRED!" when pixel error < 15px in both axes
- **Servo fallback** (1658-1664): when target lost (`found=False`), sets
  `servo_fallback=True` and falls back to `send_to_gps(best_gps)`. If no estimate
  exists, sends zero velocity (hover in place).

### Offset Landing Sequence (1666-1711)
- **flying_to** (1667-1676): sends `send_to_gps(landing_target)` each frame.
  When within 1.5m and groundspeed < 0.5 m/s, transitions to "descending" and
  sends `send_land()`.
- **descending** (1677-1711): keeps commanding landing target GPS to hold position
  during descent. When alt < 0.5m, transitions to "landed".
- **Landing report** (1698-1711): prints estimate source, dummy actual/estimated GPS,
  landing target, actual landed position, estimate error, landing GPS error,
  distance to dummy vs intended offset.

### Investigate Mode — N key (1713-1821)
- Three phases: approaching -> descending -> observing
- **approaching** (1715-1722): fly to `investigate_target`, transition at < 3m + < 1 m/s
- **descending** (1732-1747): hold position at `investigate_alt`, transition when within 1.5m
- **observing** (1748-1759): hold position, print periodic updates every 10 observations
  showing estimate error and improvement since investigation started
- **Altitude test** (1761-1821): when `alt_test_active`, steps through altitudes
  (30/25/20/15/10m), hovers `alt_test_duration` seconds each, resets cluster per altitude,
  records rolling/total/Kalman errors, prints comparison table at end

### G Lock (1822-1859)
- Runs during V mode only. Collects `(lat, lon)` samples for `lock_duration` (30s)
- Only collects when `centre_snap` is active (target confirmed at frame centre)
- On completion: averages all snap samples, stores as `locked_gps` with error.
  Also snapshots current `best_gps` as `locked_est` for comparison.
- Fails if 0 snap samples collected. Cancels if V mode turned off mid-lock.

### Recording — B key (1861-1871)
- When active, samples at `record_interval` rate into three buckets:
  - V mode: `v_est_data` (best_gps estimates), `v_drone_data` (raw drone GPS)
  - C mode: `c_mode_data` (best_gps estimates)
- Data used by `_show_flight_chart()` for end-of-flight scatter plots

### Slider Read-back (1886-1898)
- Each iteration reads all 7 trackbar values and updates error simulation params:
  `gps_drift_max`, `alt_noise`, `yaw_noise`, `fov_error_pct`/`fov_scale`,
  `shake_px`, `show_landing_zone`, `resolution_idx`
- Wrapped in try/except for window-not-ready race condition

### 2x2 Grid Assembly (1900-1956)
- God view (top-left), camera+HUD (top-right), scatter (bottom-left), dashboard (bottom-right)
- All panels resized to PANEL_H=480, widths padded to match per row

### Key Handling (1992-2278)
- ESC: quit. SPACE: arm/disarm. T: toggle CV model view. Tab: cycle scatter ref dummy.
- L: offset landing (G LOCK > TOTAL AVG > ROLLING 50 estimate priority).
- B: toggle recording. G: start/cancel GPS lock. H: altitude test.
- N: investigate active cluster (cancel if already investigating).
- 1-9: investigate specific cluster by number.
- Y/I/X: classify during observe phase (confirm/interest/false positive).
- C/V: toggle GPS centering / visual servo (mutually exclusive).
- WASD/QE/RF: manual flight (cancels all auto modes). R at ground = takeoff to 2m.

### Session Summary (2280-2304)
- Prints frame count, detection count, saved images count, GPS observations,
  best estimate + error, last single estimate, actual target GPS.
- Calls `_show_flight_chart()` for matplotlib scatter analysis.

## Known Issues

- 2508 lines (needs splitting: UI, estimation, flight modes)
- Duplicate Kalman/rolling-avg code in `calculate_target_gps` and `_route_to_cluster`
- No timeout on "approaching" investigate phase
- Centre-snap weight can explode at very low altitude (no clamp)
- Recording data only in-memory (should auto-dump CSV on exit)
