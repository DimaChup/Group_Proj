# Browser Dashboard — Master Reference

> Single source of truth for the passive_watch.py browser dashboard.
> Every feature documented here. Agents check this before making changes.
> Source files: `field_tools/passive_watch.py` (HTML_PAGE + HTTP handler),
> `field_tools/interactive_map.py`, `field_tools/gps_charts.py`,
> `field_tools/cv_pipeline_visual.py`, `field_tools/gps_pipeline_visual.py`

---

## 1. Layout

The page uses CSS grid with three rows, all inside a dark (#111) background.

### Row 1: Camera + Detections (50% / 50%)
```
.row1 { grid-template-columns: 1fr 1fr }
```
| Left (50%) | Right (50%) |
|------------|-------------|
| **Camera Feed** — live MJPEG `<img src="/stream">` | Two-column sub-grid `.det-pair` (25% + 25% of page): **Latest Detection** + **Best Detection** |
| Full width, aspect-ratio preserved | Below det-pair: **SMART Frames** grid (full width of right half) |

### Row 2: Map + GPS Analysis (25% / 75%)
```
.row2 { grid-template-columns: 1fr 3fr }
```
| Left (25%) | Right (75%) |
|------------|-------------|
| **Satellite Map** — interactive Canvas (350px height) | **GPS Analysis** — client-side Canvas scatter charts (500px main + 500px convergence + 2x250px side charts) |

### Row 3: Pipeline Visuals (50% / 50%)
```
.row3 { grid-template-columns: 1fr 1fr }
```
| Left (50%) | Right (50%) |
|------------|-------------|
| **CV Detection Pipeline** diagram | **GPS Estimation Pipeline** diagram |

### Responsive
At `max-width: 1000px`, all rows collapse to single column (`grid-template-columns: 1fr`).

---

## 2. Camera Feed

**Source**: Live MJPEG stream at `/stream` endpoint.
**Stream sleep**: 0.033s (30fps cap) — DO NOT reduce further.

### HUD Overlay Elements (rendered server-side in Python, baked into JPEG frames)
- **GPS bar** — drone lat, lon, alt, sats, mode
- **FPS bar** — camera FPS, vision FPS, stream FPS
- **Compass** — heading indicator
- **Crosshair** — cyan with black outline, visible on any background
- **Pink line** — from frame center to detection center, with:
  - Pixel distance label (magenta, black background)
  - Real meters label (cyan, black background)
  - Labels are BIGGER with black background for contrast
- **Detection box** — green bounding box with black outline text
- **Scale bar** — white, bottom-right
- **FOV bar** — field of view info
- **Estimate bar** — GPS estimate info
- All text uses outline technique: black stroke first, color fill on top

### Performance
- Runs at real-time speed (1 second per second)
- ~30fps from fake video, matches Pi camera rate
- This is the PRIMARY display — must never slow down

---

## 3. Latest Detection & Best Detection Panels

### Latest Detection (`/latest` endpoint)
- **Snapshot** (frozen frame) from the camera feed at moment of detection
- Same HUD as camera feed (it's a copy of the overlayed display frame)
- Updates ONLY when a NEW detection happens (not every frame)
- 25% page width (inside right half of row 1)
- Updated via polling: `document.getElementById('latest').src = '/latest?' + Date.now()` every 2s

### Best Detection (`/best` endpoint)
- Same as Latest Detection but ONLY updates when a MORE CENTRAL detection is found
- Tracks the best (lowest center distance) across the entire session
- Persists until `Reset Best` is clicked or `Clear All` is clicked
- `_best_center_dist` global tracks the threshold — new detection must beat it
- 25% page width (inside right half of row 1)

### SMART Frames Grid (`/smart-grid` endpoint)
- Server-rendered 5x2 grid of the smart cluster detection frames
- Shows below the Latest/Best pair in row 1
- Full width of the right 50% column
- Updated via polling every 2s

### Zoom/Pan on Detection Images
Both Latest and Best are wrapped in `.zoom-wrap` divs:
- **Scroll wheel** — zoom in/out (1x to 8x)
- **Click+drag** — pan when zoomed
- **Double-click** — reset to 1x zoom, 0 offset
- `transform: translate(ox, oy) scale(s)` with 0.1s ease-out transition

---

## 4. Control Bar

A `.ctrl-bar` div at the top of the page with flex layout:

### Model Selector
- `<select id="model-sel">` with 4 options:
  - `0` — Original (best.tflite)
  - `1` — SAR v2 TFLite
  - `2` — SAR v2 NCNN
  - `3` — COCO Person
- On change: calls `/api/switch-model?id=N`
- Shows loading status: `model-status` span with classes `.loading` (yellow), `.ok` (green), `.err` (red)
- Class filter auto-resets to "all" on model switch (server-side)
- Timeout: 10 seconds for large model loads
- Default at launch: whichever model was passed via `--model` arg (usually COCO Person with `--conf 0.2`)
- Server syncs active model ID back to dropdown via `/api/status` polling

### Confidence Slider
- `<input type="range" id="conf-slider" min="0.05" max="0.95" step="0.05">`
- Live display of value in `.conf-val` span
- On change (not input): calls `/api/set-conf?val=X`
- Server syncs current threshold back via `/api/status` polling

### Class Filter
- `<select id="class-sel">` with options: `all`, `dummy`, `person`, `bird`
- On change: calls `/api/set-class?name=X`
- `bird` included because COCO model classifies dummy as bird
- Server syncs current filter back via `/api/status` polling

### Clear All Button
- Red button (#600 background, #f44 border)
- Calls `/api/clear-all`
- Resets: all GPS estimates, smart estimator, best detection, dummy estimator, all JPEG snapshots/plots
- Button text flashes "Cleared!" for 1.5s

### Reset Best Button
- Dark button (#333 background, #0ff border)
- Calls `/api/reset-best`
- Resets ONLY best detection tracking (`_best_center_dist = 999.0`, clears `latest_best_jpeg`)
- Button text flashes "Reset!" for 1.5s

---

## 5. Satellite Map

**Source**: `field_tools/interactive_map.py` → `get_interactive_map_html()`
**Container**: `<div id="imap-host">` replaced at page serve with full HTML+JS component.

### Canvas Features
- **Map image** loaded once from `/map` endpoint (map.jpg, ~12MB, cached 24h)
- **High-DPI support** — canvas scaled by `devicePixelRatio`
- **Scroll-wheel zoom** centered on mouse (min 0.5x fit, max 20x native)
- **Click+drag pan**
- **Double-click** to reset to fit-to-view

### Overlays (drawn every frame via requestAnimationFrame, only when `needsRedraw`)
- **Zone polygons**:
  - Flight area (blue, thin, rgba(0,150,255,0.6))
  - SSSI no-fly zone (red, rgba(255,50,50,0.8))
  - Search area (yellow, rgba(255,255,0,0.8))
  - Takeoff marker (white dot with "H" label, blue ring)
- **Drone position dot** — blue filled circle with white ring, heading arrow with arrowhead
  - Updates via `/api/drone` poll every 500ms
- **Camera FOV footprint** — dashed rectangle rotated by yaw, cyan-green fill+stroke
  - Computed from altitude + sensor/focal config
- **GPS estimate dots** — heatmap colored by centrality (pdist):
  - Green (central, low pdist) through yellow to red (edge, high pdist)
  - Updated via `/api/estimates` poll every 2000ms
- **Smart cluster median star** — magenta 5-pointed star with "SMART" label
- **Coverage trace** — accumulated camera footprint history (blue fill, rgba(80,160,255,0.06))
  - Max 2000 entries, pushed on each drone position update
  - Toggle button "Coverage: ON/OFF" (top-right)
  - "Clear Coverage" button (top-right)
- **Scale bar** — bottom-left, auto-picks nice round distance (1/2/5/10/20/50/100/200/500m)
- **Info overlay** — top-left: lat/lon, alt, sats, mode, detection count, coverage count
- **Zoom info** — bottom-right: zoom percentage + "dblclick=reset" hint

### Coordinate System
- Map pixel (0,0) = top-left = (REF_LAT, REF_LON) from config.py
- GPS to map: `px = (lon - REF_LON) * 111320 * cos(REF_LAT) / MAP_WIDTH_METERS * mapW`

---

## 6. GPS Analysis Charts

**Source**: `field_tools/gps_charts.py` → `get_gps_charts_html()`
**Container**: `<div id="gps-charts-host">` replaced at page serve.
**Data**: polls `/api/estimates-full` every 1 second.

### Layout
```
Left column (500px):          Right column:
  [Main scatter 500x400]        [Smart cluster 250x300] [Central 4m 250x300]
  [Convergence 500x200]
```

### Main Scatter Plot (500x400 canvas)

**Toolbar buttons**:
- **Color mode**: Altitude (default, active green), Centrality, Confidence
  - Heatmap: green (good) to red (bad). For altitude: low=green, high=red. For centrality: central=green, edge=red. For confidence: high=green, low=red.
- **Map BG**: toggle satellite map background (ON by default). Loads `/map` image, draws with dark overlay for readability.
- **Reset View**: resets zoom and pan to auto-fit
- **Ground Truth**: text input `lat,lon` + Set button + Clear button
  - Sends `/api/set-ground-truth?lat=X&lon=Y` and `/api/clear-ground-truth`
  - When set: origin shifts to GT position, yellow star marker labeled "TRUE"
  - Error metrics computed relative to GT instead of mean

**Filter row** (below toolbar):
- **Pdist** (centrality): min/max range sliders (0 to dynamic max)
- **Alt** (altitude): min/max range sliders (0 to dynamic max, step 0.5)
- **Conf** (confidence): min/max range sliders (0 to 1, step 0.01)
- All update live. Slider max values auto-adjust based on actual data.
- Filtered-out points are excluded from all calculations and drawing.

**Chart elements**:
- Bullseye rings at 1, 2, 3, 5, 10, 20, 50m (dashed)
- Grid lines with auto-step (0.1/0.2/0.5/1/2/5/10/20/50/100m)
- Compass labels: N (top), E (right)
- Data dots colored by selected mode
- **Markers**:
  - Green cross — simple mean
  - Cyan square — weighted mean (weight = 1/centrality_dist^2)
  - Magenta diamond — median
  - Yellow star — ground truth (when set)
- **Stats bar** (below canvas): N (filtered/total), CEP50, max spread, GPS coords or GT coords, mean/weighted/median errors with distance from reference
- **Interactions**: scroll-wheel zoom (centered on mouse), click+drag pan, click on dot shows tooltip (lat, lon, alt, conf, center dist) for 3s

### Error Convergence Chart (500x200 canvas)
- X axis: detection count (1 to N)
- Y axis: error in meters (distance from reference — GT if set, else final mean)
- Three lines:
  - Green (+) — running simple mean error
  - Cyan (square) — running weighted mean error
  - Magenta (diamond) — running median error
- Grid lines at nice y-steps (0.1/0.2/0.5/1/2/5/10/20/50m)
- Shows convergence behavior: how estimate accuracy improves with more detections
- Needs 2+ detections to render

### Smart Cluster Mini-Chart (250x300 canvas)
- **Algorithm**: finds tightest-10 cluster from all estimates (smallest max pairwise spread)
  - For each seed point, sorts all by distance, takes nearest 10, computes max pairwise spread
  - Keeps best (smallest spread) across all seeds
- **Phases**:
  - Phase 1 (<10 detections): "Gathering N detections... Need 10 to start" with arriving dots
  - Phase 2 (10+, spread > 0.5m): "FINDING CLUSTER..." (orange) with spread value
  - Phase 3 (spread < 0.5m): "LOCKED" (green) — freezes the cluster, stops updating
- **Drawing**: fine rings (0.1, 0.2, 0.5, 1.0m), numbered cyan dots with radial lines from center, outlier dots dim gray, center cross (cyan), median diamond (magenta)
- **Stats**: total/cluster/rejected counts, spread, median error

### Central 4m Bullseye (250x300 canvas)
- Filters to detections with `pdist < 200px` (central in frame)
- Title: "CENTRAL (N/10, <200px)"
- Fixed 5m radius bullseye with rings at 1, 2, 3, 5m
- Dots colored by centrality (green=most central, red=least)
- After 10+ central detections: shows median (magenta diamond) and weighted mean (cyan square)
- Before 10: shows "N/10 searching..." message
- Stats: total, central count

### Live Progression Requirements
All charts must reflect the current state at each 1-second poll. No chart should wait for completion before rendering.

- **Smart Cluster chart**: Must show dots arriving live (1, 2, 3...). During searching, highlight the tightest N and show rejected dots as dim. Display "Finding... spread: X.Xm" until locked.
- **Central 4m chart**: Must show central detections arriving one by one. Display "3/10 searching..." until 10 collected.
- **SMART Frames grid**: Must show detection thumbnails as they arrive (partial grid is OK). Must not wait for lock before showing frames.
- **Error convergence**: Already shows live lines building up (correct).
- **Main scatter**: Already shows dots appearing live (correct).

---

## 7. CV Pipeline Visual

**Source**: `field_tools/cv_pipeline_visual.py` → `get_cv_pipeline_html()`
**Container**: `<div id="cv-pipeline-host">` replaced at page serve.

### 6-Stage Pipeline Diagram
Horizontal row of cards with arrow connectors:

1. **Camera** — IMX296 global shutter, 5.02x3.76mm sensor, f=5.46mm, 1456x1088 BGR, inverted mount
2. **Preprocess** — BGR pass-through, optional cv2.remap undistort (+1.5ms), no resize
3. **Model Input** — YOLOv8n TFLite, tensor [1,640,640,3] f32, letterbox 1456x1088 -> pad to 1456x1456 -> resize to 640x640
4. **Inference** — Pi TFLite ~206ms (4.8 FPS), Pi NCNN ~100ms (10 FPS), Laptop ~30ms. Output [1,5,8400]: 8400 candidates x 5 (cx,cy,w,h,conf) -> NMS
5. **Detection** — output (found, cx, cy, conf), pixel coords 1456x1088, threshold >= 0.4, class "dummy"
6. **GPS Estimation** — f_px = 1584px, pixel offset -> meters -> rotate by yaw -> GPS offset, weight = 1/alt^2 x centrality

### FOV Geometry Canvas (320x180)
- Side-view diagram: drone at altitude, FOV cone to ground, ground coverage bracket
- Detection marker on ground when active
- Dynamic: updates with altitude, shows GSD and dummy pixel height
- Sky-to-ground gradient background

### Summary Bar
- Bottom row: Latency, FPS, Model, Input size, Sensor size, f_px

### Live Update API
- `window.updatePipelineData({alt, yaw, lat, lon, fps, det_conf, det_cx, det_cy})`
- Called from status polling in main page JS

---

## 8. GPS Pipeline Visual

**Source**: `field_tools/gps_pipeline_visual.py` → `get_gps_pipeline_html()`
**Container**: `<div id="gps-pipeline-host">` replaced at page serve.

### Interactive Controls
- **Altitude slider** (5-60m)
- **Detection X slider** (0-1456px)
- **Detection Y slider** (0-1088px)
- **Yaw slider** (0-359 degrees)

### Left Column: Geometry Diagrams

**Camera Projection SVG (440x340)**:
- Drone body with propeller arms
- Altitude dashed line with label
- FOV cone (cyan, dashed)
- Ground coverage bar (green) with width/height label
- Detection point on ground (magenta) with projection ray from drone
- dx offset arrow (magenta)
- Camera view inset (120x90): crosshair, center dot, detection dot, offset lines
- Legend: drone nadir (cyan), detection (magenta), ground coverage (green)
- Focal length annotation

**Yaw Rotation Compass SVG (260x260)**:
- Compass ring with N/E/S/W labels and tick marks
- Body frame axes rotating with yaw: forward (cyan), right (magenta)
- World frame axes (fixed, dashed gray): north, east
- Yaw arc (yellow) showing rotation angle
- Detection vector in world frame (green dashed) with GPS offset dot
- Center dot (white)

### Calibration Reference Table
| Alt | Coverage | GSD | Dummy height |
|-----|----------|-----|-------------|
| 1m  | computed | computed | computed |
| 10m | computed | computed | computed |
| 30m | computed | computed | computed |
| **Current** | **bold cyan** | **bold cyan** | **bold magenta** |

Below: aspect ratio, sensor size, focal length, dummy height (1.8m), GSD formula.

### Right Column: Step-by-Step Equations
6 numbered steps, each in a card:

1. **Pixel Offset from Centre** — dx_px = cx - 728, dy_px = cy - 544
2. **Pixels to Ground Metres** — f_px = 5.46 x 1456 / 5.02 = 1584px, dx_m = dx_px x alt / f_px
3. **Body Frame Mapping** — forward_m = -dy_m, right_m = dx_m
4. **Rotate by Drone Yaw** — north = fwd*cos(yaw) - rgt*sin(yaw), east = fwd*sin(yaw) + rgt*cos(yaw)
5. **Metres to GPS Offset** — est_lat = drone_lat + north/111320, est_lon = drone_lon + east/(111320*cos(lat))
6. **Weighted Accumulation** — w = 1/alt^2 x centrality, shows weight comparison at two altitudes

### Summary Card
- Ground offset from drone: N meters, E meters
- Distance and bearing
- Weight at current altitude

### Live Update API
- `window.updateGPSData({alt, fov_deg, ground_w, ground_h, f_px})`
- Called from status polling in main page JS
- All values and diagrams recalculate interactively via sliders

---

## 9. API Endpoints

All served by the `Handler` class in `field_tools/passive_watch.py`.

### Page & Stream Endpoints
| Endpoint | Method | Content-Type | Description |
|----------|--------|-------------|-------------|
| `/` | GET | text/html | Main dashboard page (injects all component HTML) |
| `/stream` | GET | multipart/x-mixed-replace | Live MJPEG stream (30fps cap, 0.033s sleep) |
| `/snapshot` | GET | image/jpeg | Latest detection frame (or current frame if no detection) |
| `/latest` | GET | image/jpeg | Latest detection snapshot JPEG (frozen at detection time) |
| `/best` | GET | image/jpeg | Best (most central) detection snapshot JPEG |
| `/smart-grid` | GET | image/jpeg | Server-rendered 5x2 grid of smart cluster frames |
| `/bullseye` | GET | image/jpeg | Legacy server-rendered bullseye scatter plot |
| `/map` | GET | image/jpeg | Raw map.jpg file (cached 24h, loaded once by interactive map canvas) |
| `/map-rendered` | GET | image/jpeg | Legacy server-rendered map with dots overlay |

### Data API Endpoints
| Endpoint | Method | Content-Type | Description |
|----------|--------|-------------|-------------|
| `/api/drone` | GET | application/json | Drone telemetry: `{lat, lon, alt, yaw, sats, mode}` |
| `/api/estimates` | GET | application/json | GPS estimates for map: `{estimates: [[lat,lon],...], smart: [lat,lon] or null}` |
| `/api/estimates-full` | GET | application/json | Full estimates for charts: `{estimates: [[lat,lon,pdist,alt,conf],...], smart: {locked,cluster,spread,median}, drone: {lat,lon}, mean: [lat,lon], n, ground_truth}` |
| `/api/status` | GET | application/json | Full status: cam_fps, vis_fps, stream_fps, detections, det_pct, saved, gps_*, est_*, fov_deg, cal_*, active_model_id, conf_threshold, class_filter, bullseye_map_bg |

### Control API Endpoints
| Endpoint | Method | Content-Type | Description |
|----------|--------|-------------|-------------|
| `/api/switch-model?id=N` | GET | application/json | Switch model (0-3). Returns `{ok, model}` or `{ok:false, error}` |
| `/api/set-conf?val=X` | GET | application/json | Set confidence threshold (0.05-0.95) |
| `/api/set-class?name=X` | GET | application/json | Set class filter (all/dummy/person/bird) |
| `/api/clear-all` | GET | application/json | Reset everything: estimates, smart estimator, best detection, snapshots, plots |
| `/api/reset-best` | GET | application/json | Reset only best detection tracking |
| `/api/set-ground-truth?lat=X&lon=Y` | GET | application/json | Set ground truth for error analysis |
| `/api/clear-ground-truth` | GET | application/json | Clear ground truth |
| `/api/toggle-bullseye-bg` | GET | application/json | Toggle satellite map background on legacy bullseye |

### Polling Intervals (client-side)
| What | Interval | Source |
|------|----------|--------|
| `/api/status` + image refreshes | 2000ms | Main page `setInterval` |
| `/api/drone` | 500ms | interactive_map.py `setInterval` |
| `/api/estimates` | 2000ms | interactive_map.py `setInterval` |
| `/api/estimates-full` | 1000ms | gps_charts.py `setInterval` |

---

## 10. Performance Rules (DO NOT VIOLATE)

| Rule | Value | Reason |
|------|-------|--------|
| Stream sleep | 0.033s (30fps) | Never go below — matches Pi camera rate |
| Status/image polling | 2000ms | No faster — browser overhead |
| GPS charts polling | 1000ms | Needed for smooth convergence chart |
| Drone position polling | 500ms | Smooth map tracking, low payload |
| Detection snapshots | On detection event only | NOT every frame |
| JPEG quality: stream | Configured by args | Default 70-80% |
| JPEG quality: thumbnails | 80% | Snapshots |
| Dashboard CPU overhead | <5% of detection pipeline | Site is read-only display |
| Map image | Loaded once, cached 24h | 12MB, never re-fetch |
| Canvas redraw | Only on `needsRedraw` flag | requestAnimationFrame loop |

---

## 11. Feature Status

| # | Feature | Status | Component | Notes |
|---|---------|--------|-----------|-------|
| 1 | Live MJPEG camera stream at 30fps | DONE | passive_watch.py `/stream` | 0.033s sleep cap |
| 2 | Full HUD overlay (GPS, FPS, compass, crosshair, scale bar) | DONE | passive_watch.py (server-side render) | Black outline technique |
| 3 | Pink line center-to-detection with pixel+meter labels | DONE | passive_watch.py (server-side render) | Bigger labels, black bg |
| 4 | Detection bounding box (green, black outline text) | DONE | passive_watch.py (server-side render) | |
| 5 | Latest Detection snapshot (frozen on detection) | DONE | `/latest` endpoint | Updates on new detection only |
| 6 | Best Detection snapshot (most central) | DONE | `/best` endpoint | Reset via button |
| 7 | Zoom/pan on detection images (scroll+drag+dblclick) | DONE | HTML_PAGE JS (`.zoom-wrap`) | 1x-8x zoom |
| 8 | SMART Frames 5x2 grid | DONE | `/smart-grid` endpoint | Server-rendered |
| 9 | Model selector (4 models) | DONE | Control bar + `/api/switch-model` | With loading status |
| 10 | Confidence slider | DONE | Control bar + `/api/set-conf` | Synced from server |
| 11 | Class filter dropdown (all/dummy/person/bird) | DONE | Control bar + `/api/set-class` | Bird added for COCO |
| 12 | Clear All button | DONE | Control bar + `/api/clear-all` | Resets everything |
| 13 | Reset Best button | DONE | Control bar + `/api/reset-best` | Resets best only |
| 14 | Interactive satellite map (zoom/pan/dblclick-reset) | DONE | `field_tools/interactive_map.py` | Canvas, high-DPI |
| 15 | Drone position dot + heading arrow on map | DONE | interactive_map.py | 500ms poll |
| 16 | Camera FOV footprint rectangle (rotated by yaw) | DONE | interactive_map.py | Dashed cyan-green |
| 17 | GPS estimate dots on map (heatmap by centrality) | DONE | interactive_map.py | Green-yellow-red |
| 18 | Smart cluster median star on map (magenta) | DONE | interactive_map.py | "SMART" label |
| 19 | Zone overlays (search/flight/SSSI/takeoff) | DONE | interactive_map.py | Color-coded polygons |
| 20 | Scale bar on map | DONE | interactive_map.py | Auto-picks nice distance |
| 21 | Camera coverage trace on map | DONE | interactive_map.py | Blue fill, toggle+clear buttons, max 2000 |
| 22 | Main GPS scatter plot (500x400, bullseye rings) | DONE | `field_tools/gps_charts.py` | Canvas, high-DPI |
| 23 | Scatter color modes (altitude/centrality/confidence) | DONE | gps_charts.py toolbar | Toggle buttons |
| 24 | Scatter map background toggle | DONE | gps_charts.py toolbar | ON by default |
| 25 | Scatter zoom/pan (scroll+drag) | DONE | gps_charts.py | Mouse-centered zoom |
| 26 | Scatter click-to-inspect dot tooltip | DONE | gps_charts.py | 3s auto-hide |
| 27 | Ground truth input (lat,lon) with Set/Clear | DONE | gps_charts.py toolbar | Yellow star marker |
| 28 | Filter sliders (pdist/alt/conf min+max ranges) | DONE | gps_charts.py filter row | Auto-adjust max from data |
| 29 | Scatter stats bar (N, CEP50, max, mean/weighted/median errors) | DONE | gps_charts.py | Error ref: GT or mean |
| 30 | Error convergence line chart (mean/weighted/median) | DONE | gps_charts.py (500x200) | Needs 2+ detections |
| 31 | Smart cluster mini-chart (tightest-10, lock at <0.5m) | DONE | gps_charts.py (250x300) | 3 phases |
| 32 | Central 4m bullseye (<200px, 5m radius rings) | DONE | gps_charts.py (250x300) | 10+ triggers markers |
| 33 | CV Pipeline 6-stage diagram | DONE | `field_tools/cv_pipeline_visual.py` | Static + live data |
| 34 | CV Pipeline FOV geometry canvas | DONE | cv_pipeline_visual.py | Dynamic altitude |
| 35 | GPS Pipeline interactive SVG diagrams | DONE | `field_tools/gps_pipeline_visual.py` | Sliders for alt/cx/cy/yaw |
| 36 | GPS Pipeline calibration reference table | DONE | gps_pipeline_visual.py | 4 altitude rows |
| 37 | GPS Pipeline 6-step equations | DONE | gps_pipeline_visual.py | All compute live |
| 38 | GPS Pipeline yaw rotation compass | DONE | gps_pipeline_visual.py | Body+world frame axes |
| 39 | Live pipeline data updates from status poll | DONE | HTML_PAGE JS | updatePipelineData + updateGPSData |
| 40 | Server syncs model/conf/class back to UI controls | DONE | `/api/status` polling | Prevents UI desync |
| 41 | SRT pitch/roll extraction for camera feed | DONE | passive_watch.py (fake mode) | From DJI SRT telemetry |
| 42 | Map background ON by default (bullseye + GPS charts) | DONE | gps_charts.py, interactive_map.py | `mapBgOn = true`, `bullseye_map_bg = True` |
| 43 | Model switch with XNNPACK deadlock fix | DONE | passive_watch.py | Thread-safe model reload |
| 44 | Fake mode (replay DJI video + SRT telemetry) | DONE | passive_watch.py `--fake` | No camera/mavproxy needed |
| 45 | Map calibration tool | DONE | `tools/map_calibrate.py` | Standalone utility |
| 46 | Responsive layout (collapses at 1000px) | DONE | HTML_PAGE CSS `@media` | Single column fallback |
