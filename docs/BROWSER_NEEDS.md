# Browser Dashboard -- Master Reference

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
| **Camera Feed** -- live MJPEG `<img src="/stream">` | Two-column sub-grid `.det-pair` (25% + 25% of page): **Latest Detection** + **Best Detection** |
| Full width, aspect-ratio preserved | Below det-pair: **SMART Frames** grid (full width of right half) |

### Row 2: Map + GPS Analysis (25% / 75%)
```
.row2 { grid-template-columns: 1fr 3fr }
```
| Left (25%) | Right (75%) |
|------------|-------------|
| **Satellite Map** -- interactive Canvas (350px height) | **GPS Analysis** -- client-side Canvas scatter charts (500px main + 500px convergence + 2x250px side charts) |

### Row 3: Pipeline Visuals (50% / 50%)
```
.row3 { grid-template-columns: 1fr 1fr }
```
| Left (50%) | Right (50%) |
|------------|-------------|
| **CV Detection Pipeline** diagram | **GPS Estimation Pipeline** diagram |

### Responsive
At `max-width: 1000px`, all rows collapse to single column (`grid-template-columns: 1fr`).
Detection pair also collapses to single column.

---

## 2. Camera Feed

**Source**: Live MJPEG stream at `/stream` endpoint.
**Stream sleep**: 0.033s (30fps cap) -- DO NOT reduce further.

### HUD Overlay Elements (rendered server-side in Python `draw_overlay()`, baked into JPEG frames)

**Top bar** (black rectangle, full width, 30px):
- Left: `CAM:{fps} VIS:{fps} STR:{fps}` (cyan)
- Right: `Y:{yaw} P:{pitch} R:{roll}` (gray) + flight mode

**Compass rose** (top-right, 25px radius):
- Circle with N/S/E/W labels (black outline + white fill for readability)
- Heading arrow rotating by yaw (cyan)

**Centre crosshair**:
- Black outline (4px) + cyan inner line (2px), 25px arms
- Always visible against any background

**Detection box** (when detection age < 2s):
- Green bounding box (3px), fades with age via alpha
- Label `AI {conf:.2f} [{class}]` on black background rectangle above box

**Pink line** (when detection age < 2s):
- Magenta line from frame centre to detection centre
- **Pixel distance label**: magenta text on black background at midpoint, 0.65 scale
- **Meters distance label**: cyan text on black background below pixel label, 0.65 scale
  (computed from altitude + HFOV)

**Scale bar** -- white, bottom-right (from FOV info)

**GPS bar** (black rectangle, bottom 25px):
- `GPS: {lat}, {lon} | Alt: {alt}m | Sats: {sats}` (orange-blue)

**FOV/Estimate bars** (rendered in overlay, above GPS bar):
- FOV info, estimate GPS, drone-to-estimate offset, class+confidence

**Result banner** (temporary, 5 seconds after SMART lock or SURVEY complete):
- Large semi-transparent black rectangle, centered
- Title text: black outline (6px) + colored fill (3px)
- "TARGET FOUND" (green) or "SURVEY COMPLETE" (cyan in BGR = yellow display)

### Performance
- Runs at real-time speed (1 second per second)
- ~30fps from fake video, matches Pi camera rate
- This is the PRIMARY display -- must never slow down

---

## 3. Detection Panels

### Latest Detection (`/latest` endpoint)
- **Frozen snapshot** of the fully-overlayed display frame at the moment of detection
- Created by `_snapshot_overlay()`: resizes to `thumb_w=728`, adds label badge + info bar
- **Label badge**: "LATEST" in teal (200,160,0) on black rectangle, top-left
- **Info bar** (bottom, replaces camera feed bars with opaque black covering 75px):
  - Line 1: `DRONE: {lat}, {lon}` (cyan/yellow)
  - Line 2: `DUMMY EST: {lat}, {lon}` (magenta) + `OFFSET: {dist}m [{class} {conf}]` (yellow)
- Updates ONLY when a NEW detection happens (not every frame)
- 25% page width (inside right half of row 1)
- Updated via polling every 2s: `document.getElementById('latest').src = '/latest?' + Date.now()`

### Best Detection (`/best` endpoint)
- Same as Latest Detection but ONLY updates when a MORE CENTRAL detection is found
- Tracks the best (lowest center distance) across the entire session
- Persists until `Reset Best` or `Clear All` is clicked
- `_best_center_dist` global tracks the threshold -- new detection must beat it
- `_best_detection_gps` dict stores: `{est_lat, est_lon, drone_lat, drone_lon, center_dist}`
- **Label badge**: "BEST" in green (0,200,0) on black rectangle, top-left
- 25% page width (inside right half of row 1)

### SMART Frames Grid (`/smart-grid` endpoint)
- Server-rendered 5x2 grid of detection frames (240x180 each cell)
- **Status banner** (28px) at top:
  - Before any detections: "WAITING FOR DETECTIONS 0/N" (dark gray)
  - Collecting: "COLLECTING {have}/{need}" (dark orange/amber)
  - Locked: "LOCKED {N}/{N} spread {spread}m" (dark green)
- **Before lock**: shows ALL collected frames in chronological order
- **After lock**: shows ONLY the frames from the tightest cluster
- Each filled slot has `#{N}` number label (cyan text with white outline)
- Border: green (2px) if locked, yellow/amber (1px) if collecting
- Empty slots: dim gray rectangle with faint `#{N}` placeholder
- Each frame is the full HUD overlay (draw_overlay result), not raw camera
  - SmartEstimator.update_last_frame() replaces raw frame with overlayed display
- Shows below the Latest/Best pair in row 1
- Full width of the right 50% column
- Updated via polling every 2s

### Zoom/Pan on Detection Images
Both Latest and Best are wrapped in `.zoom-wrap` divs:
- **Scroll wheel** -- zoom in/out (1x to 8x)
- **Click+drag** -- pan when zoomed
- **Double-click** -- reset to 1x zoom, 0 offset
- `transform: translate(ox, oy) scale(s)` with 0.1s ease-out transition

---

## 4. Control Bar

A `.ctrl-bar` div at the top of the page with flex layout:

### Model Selector
- `<select id="model-sel">` with 4 options:
  - `0` -- Original (best.tflite)
  - `1` -- SAR v2 TFLite
  - `2` -- SAR v2 NCNN
  - `3` -- COCO Person
- On change: calls `/api/switch-model?id=N`
- Shows loading status: `model-status` span with classes `.loading` (yellow), `.ok` (green), `.err` (red)
- Class filter auto-resets to "all" on model switch (server-side)
- Timeout: 10 seconds for large model loads
- Default at launch: whichever model was passed via `--model` arg (usually COCO Person with `--conf 0.2`)
- Server syncs active model ID back to dropdown via `/api/status` polling

### Confidence Slider
- `<input type="range" id="conf-slider" min="0.05" max="0.95" step="0.05">`
- Live display of value in `.conf-val` span
- `input` event: updates display only
- `change` event: calls `/api/set-conf?val=X`
- Server syncs current threshold back via `/api/status` polling

### Class Filter
- `<select id="class-sel">` with options: `all`, `dummy`, `person`, `bird`
- On change: calls `/api/set-class?name=X`
- `bird` included because COCO model classifies dummy as bird
- Server syncs current filter back via `/api/status` polling

### Smart Cluster Controls
- **Spread**: `<input type="number" id="smart-spread">` (default 0.75, range 0.1-5.0, step 0.05)
  - Label "m" suffix
- **Count**: `<input type="number" id="smart-count">` (default 10, range 3-50, step 1)
  - Label "pts" suffix
- Both call `/api/set-smart?spread=X&count=Y` on `change`
- Server resets the SmartEstimator lock state when params change (fresh cluster search)
- Server syncs values back via `/api/status` polling (prevents desync when not focused)

### Clear All Button
- Red button (#600 background, #f44 border)
- Calls `/api/clear-all`
- Resets: all GPS estimates, smart estimator (reinit), best detection, dummy estimator,
  all JPEG snapshots/plots, result mode flags (`_smart_result_saved`, `_survey_result_saved`),
  result banner
- Button text flashes "Cleared!" for 1.5s

### Reset Best Button
- Dark button (#333 background, #0ff border)
- Calls `/api/reset-best`
- Resets ONLY best detection tracking (`_best_center_dist = 999.0`, clears `latest_best_jpeg`
  and `_best_detection_gps`)
- Button text flashes "Reset!" for 1.5s

---

## 5. Satellite Map

**Source**: `field_tools/interactive_map.py` -> `get_interactive_map_html()`
**Container**: `<div id="imap-host">` replaced at page serve with full HTML+JS component.

### Canvas Features
- **Map image** loaded once from `/map` endpoint (map.jpg, ~12MB, cached 24h)
- **High-DPI support** -- canvas scaled by `devicePixelRatio`
- **Scroll-wheel zoom** centered on mouse (min 0.5x fit, max 20x native)
- **Click+drag pan**
- **Double-click** to reset to fit-to-view

### Overlays (drawn every frame via requestAnimationFrame, only when `needsRedraw`)
- **Zone polygons**:
  - Flight area (blue, thin, rgba(0,150,255,0.6), rgba(0,150,255,0.05) fill)
  - SSSI no-fly zone (red, rgba(255,50,50,0.8), rgba(255,0,0,0.08) fill)
  - Search area (yellow, rgba(255,255,0,0.8), rgba(255,255,0,0.06) fill, 2px)
  - Takeoff marker: white dot (4px) with blue ring, "H" label
- **Drone position dot** -- blue filled circle with white ring, heading arrow with arrowhead
  - Circle radius: `max(5, 8 * viewScale)` (scales with zoom)
  - Arrow: white, length 2.5x radius, with arrowhead
  - Updates via `/api/drone` poll every 500ms
- **Camera FOV footprint** -- dashed rectangle rotated by yaw
  - Fill: rgba(0,255,200,0.1), stroke: rgba(0,255,200,0.6), 1.5px dashed [4,3]
  - Computed from altitude + sensor/focal config (4 GPS corners)
  - Only drawn when alt >= 0.5m
- **GPS estimate dots** -- heatmap colored by pdist (pixel centrality):
  - Green (central, low pdist) through yellow to red (edge, high pdist)
  - Dot radius: `max(2, 3 * viewScale)`
  - Updated via `/api/estimates-full` poll every 2000ms
- **Smart cluster median star** -- magenta 5-pointed star (10px outer, 5px inner)
  - "SMART" label in magenta, bold 10px monospace
  - Only drawn when SmartEstimator is locked
- **Ground truth star** -- yellow (when set via `/api/set-ground-truth`)
  - Black outline star (18/8px) + yellow star (16/7px) on top
  - "TRUE" label: black outline + yellow fill, bold 11-12px
  - Always drawn LAST (on top of everything)
- **Coverage trace** -- accumulated camera footprint history
  - Blue fill rgba(80,160,255,0.06) for each recorded footprint (4 GPS corners)
  - Max 2000 entries, pushed on each drone position update
  - Toggle button "Coverage: ON/OFF" (top-right, green/gray)
  - "Clear Coverage" button (top-right, gray)
- **Scale bar** -- bottom-left, auto-picks nice round distance (1/2/5/10/20/50/100/200/500m)
  - White line with end ticks, label on dark background
- **Info overlay** -- top-left (rgba(0,0,0,0.7) background):
  - `{lat}, {lon} | Alt:{alt}m Sats:{sats} {mode} | {N} detections | Cov:{N}`
- **Zoom info** -- bottom-right: zoom percentage + "dblclick=reset" hint

### Coordinate System
- Map pixel (0,0) = top-left = (REF_LAT, REF_LON) from config.py
- GPS to map: `px = (lon - REF_LON) * 111320 * cos(REF_LAT) / MAP_WIDTH_METERS * mapW`
- Square pixels: `py = (REF_LAT - lat) * 111320 / MAP_WIDTH_METERS * mapW`

---

## 6. GPS Analysis Charts

**Source**: `field_tools/gps_charts.py` -> `get_gps_charts_html()`
**Container**: `<div id="gps-charts-host">` replaced at page serve.
**Data**: polls `/api/estimates-full` every 1 second.

### Layout
```
Left column (500px):          Right column:
  [Main scatter 500x400]        [Smart cluster 250x300] [Central 4m 250x300]
  [Convergence 500x200]           (side by side in a flex row)
```

All canvases use high-DPI scaling via `devicePixelRatio`.

### Main Scatter Plot (500x400 canvas)

**Toolbar buttons**:
- **Color mode** (4 options, mutually exclusive, active=green border):
  - `Pixel Centrality` (default, active on load) -- heatmap by pdist in pixels
  - `Distance Centrality` -- heatmap by `pdist * alt / F_PX` (ground meters from frame center)
  - `Altitude` -- heatmap by altitude (low=green, high=red)
  - `Confidence` -- heatmap by confidence (high=green, low=red)
  - Heatmap function: `val 0 = green (rgb(0,255,0)), val 1 = red (rgb(255,0,0))`
  - Color scale uses GLOBAL range (full dataset), not filtered subset -- colors are absolute
- **Map BG**: toggle satellite map background (default: **ON**)
  - Loads `/map` image (once), draws with dark overlay (rgba(0,0,0,0.4)) for readability
  - Button text: "Map BG: ON" / "Map BG: off"
- **Dots: ON/OFF**: toggle individual dot rendering (default: ON)
  - When OFF, marker shapes (mean/weighted/median/smart/best/central) still draw
- **Reset View**: resets zoom/pan to auto-fit
- **Ground Truth**: text input `lat,lon` + Set button + Clear button
  - Sends `/api/set-ground-truth?lat=X&lon=Y` and `/api/clear-ground-truth`
  - When set: origin shifts to GT position, all distances measured from GT
  - Input border turns green on success, red on parse error
  - Clear button hidden until GT is set
  - Server pre-loads GT from `_ground_truth` global on first poll (auto-populates input)

**Filter row** (below toolbar, only the active color mode's filter is visible):
- **Pdist** (pixel centrality): min/max range sliders (0 to dynamic max, step 1)
  - Shown when colorMode = "pixel_centrality"
- **Distance** (ground meters): min/max range sliders (0 to dynamic max, step 0.1)
  - Shown when colorMode = "distance_centrality"
- **Alt** (altitude): min/max range sliders (0 to dynamic max, step 0.5)
  - Shown when colorMode = "altitude"
- **Conf** (confidence): min/max range sliders (0 to 1, step 0.01)
  - Shown when colorMode = "confidence"
- All update live on `input` event. Slider max values auto-adjust based on actual data.
- Max slider auto-snaps to new maximum when data arrives.
- Filtered-out points are excluded from all calculations and drawing.

**Chart elements**:
- Bullseye rings at 1, 2, 3, 5, 10, 20, 50m (dashed [4,4], #444, 1px)
  - Centered on origin (GT or mean), with meter labels
- Grid lines with auto-step (0.1/0.2/0.5/1/2/5/10/20/50/100m), #333, 0.5px
  - X-axis labels at bottom, Y-axis labels at left
- Compass labels: **N** (top), **E** (right), bold 12px, #888
- Data dots: 3.5px radius, colored by selected mode (when dots enabled)
  - Off-screen dots clipped (skip if >10px outside canvas)

**Marker shapes on scatter plot** (drawn on top of dots):
| Marker | Shape | Color | Label | Meaning |
|--------|-------|-------|-------|---------|
| Simple mean | Cross (+) | Yellow (#ffdc00) | -- | Arithmetic average of all filtered estimates |
| Weighted mean | Square outline | Cyan (#00ffff) | -- | Weighted by 1/pdist^2 (more central = more weight) |
| Median | Filled triangle (down) | Pink/magenta (#ff66ff, 0.4 alpha fill) | -- | Component-wise median of filtered estimates |
| Ground truth | 5-pointed star | Bright yellow (#ffff00) | "TRUE" | User-set known position, origin when active |
| Best detection | Filled circle (6px) | Red (#ff2020) | "BEST" | Most central single detection's estimated GPS |
| Best drone pos | X mark (8px) | Red (#ff2020) | -- | Drone position at time of best detection |
| Best line | Dashed line | Red (#ff2020, [5,4]) | -- | Connects best drone pos to best estimate |
| SMART median | 5-pointed star (9/4px) | Magenta (#ff00ff) | "SMART" | Median of locked tightest cluster |
| Central-10 median | Filled diamond | Orange (#ff8c00) | "4m" | Median of first 10 detections with pdist < 200px |

**Stats bar** (below canvas, #222 background, 11px monospace):
- Line 1: `N: {filtered}/{total}  CEP50: {val}m  Max: {val}m  [GPS: lat,lon OR GT: lat,lon]`
- Line 2: `Mean (simple avg): {err}m  Weighted (centrality): {err}m  Median: {err}m
  Best: {err}m  Smart: {err}m (or "searching...")  4m: {err}m`
- Error reference label: "(from GT)" or "(from mean)"
- All errors are distance from origin (GT when set, else mean of filtered)

**Interactions**: scroll-wheel zoom (centered on mouse, 0.1x-200x), click+drag pan,
click on dot shows tooltip for 3s:
```
#N
Lat: X.XXXXXXX
Lon: X.XXXXXXX
Alt: X.Xm
Conf: X.XXX
CenterDist: Xpx (X.XXm)
```

### Error Convergence Chart (500x200 canvas)
- X axis: detection count (1 to N), labeled "detection count" at bottom center
- Y axis: error in meters (distance from reference -- GT if set, else final mean)
- Three lines:
  - Yellow (#ffdc00) -- running simple mean error, legend "+mean"
  - Cyan (#00ffff) -- running weighted mean error, legend square+"weighted"
  - Magenta (#ff00ff) -- running median error, legend diamond+"median"
- Title: "ERROR CONVERGENCE" (top-left, 11px monospace)
- Grid lines at nice y-steps (0.1/0.2/0.5/1/2/5/10/20/50m), #333
- Axes: #555, 1px
- X-axis label: "N={count}" at bottom-right
- Needs 2+ detections to render (shows message otherwise)

### Smart Cluster Mini-Chart (250x300 canvas)

The smart cluster algorithm: for each seed point, find `SMART_LOCK_COUNT` nearest neighbors,
compute max pairwise spread. Keep the cluster with smallest spread. Parameters synced from
server via `/api/estimates-full` response (`smart_spread`, `smart_count`).

**Phase 1** (< SMART_LOCK_COUNT detections):
- Title: "SMART CLUSTER" (orange, bold 12px)
- Subtitle: "Gathering N/10... spread: X.Xm" (or no spread if < 2)
- Shows ALL arriving dots numbered chronologically
  - Faint rings at 0.2, 0.5, 1.0m (dashed [3,3])
  - Cyan dots (5px) with white ring, radial lines from center, number labels
- Scale auto-fits to data extent
- Center cross (#444, 1px)
- Bottom: "N={total}/{count}" (9px monospace)

**Phase 2** (>= count, spread > SMART_LOCK_SPREAD):
- Title: "FINDING CLUSTER..." (orange, bold 12px)
- Subtitle: "spread: X.XXm (need <X.Xm)" + "{N} det, best {count} highlighted"
- Fine rings: 0.1, 0.2, 0.5, 1.0m (dashed [3,3], #444, 0.8px)
- **Cluster dots**: cyan (5px) with white ring, numbered, radial lines from center
- **Outlier X marks**: dim gray (rgba(100,100,100,0.5)), 1.5px crossed lines
- Center cross: cyan (#00ffff, 2px)
- Cluster median: magenta 5-pointed star (8/3px)
- Scale auto-fits to cluster extent * 1.5

**Phase 3** (spread < SMART_LOCK_SPREAD, client-side lock):
- Title: "LOCKED" (green, bold 12px) + "spread: X.XXm" (green, 10px)
- Same drawing as Phase 2 but frozen (uses locked indices/spread)
- Stats (bottom): "Total:N  Cluster:10  Rejected:N" + "Spread:X.XXm  Med err:X.XXm"

Note: client-side lock (in gps_charts.js) mirrors server-side SmartEstimator lock. Server lock
triggers when `add()` finds tight cluster. Client lock triggers from `findTightestCluster()` in JS.
Both sync via `/api/estimates-full` response: `smartData.locked` resets client lock when server
resets (e.g. via `/api/set-smart`).

### Central 4m Bullseye (250x300 canvas)

Filters all estimates to those with `pdist < 200px` (pixel distance from frame center).

- Title: "CENTRAL ({N}/{target}, <{threshold}px)" (magenta, bold 12px)
  - target = 10, threshold = 200px
- **Before 10 central**: "{N}/10 searching..." message (magenta, 11px)
- **After 10+**: shows markers:
  - Magenta 5-pointed star (7/3px) -- component-wise median of central detections
  - Cyan square outline (10px) -- weighted mean (1/pdist^2)
  - Stats: "Median err: X.XXm" (magenta), "Weighted err: X.XXm" (cyan)
- Origin: mean of all central detections
- Fixed 5m radius bullseye with rings at 1, 2, 3, 5m (dashed [3,3], #444)
- Center cross (#444, 1px)
- Dots colored by centrality within the central set (green=most central/lowest pdist, red=least)
  - Dot radius: 3.5px
- Stats (bottom): "Total:{N} | Central:{N}" (9px, #888)

When no central detections: "No central detections..." + "(need pdist < 200px)" centered.

### Live Progression Requirements
All charts reflect the current state at each 1-second poll. No chart waits for completion
before rendering.

- **Smart Cluster chart**: Shows dots arriving live (1, 2, 3...). During searching, highlights
  the tightest N and shows rejected dots as dim X marks. Displays "Finding... spread: X.Xm"
  until locked.
- **Central 4m chart**: Shows central detections arriving one by one. Displays "3/10 searching..."
  until 10 collected.
- **SMART Frames grid**: Shows detection thumbnails as they arrive (partial grid OK). Does not
  wait for lock before showing frames.
- **Error convergence**: Shows live lines building up (correct).
- **Main scatter**: Shows dots appearing live (correct).

---

## 7. Mission Result Modes

Two independent result modes run concurrently during a session. Both produce saved result images
and temporary on-screen banners.

### Mode 1: Quick Lock (SMART)
- **Trigger**: SmartEstimator locks (tightest cluster spread < threshold)
- **Output**: `generate_result_image()` saved as `RESULT_SMART_{lat}_{lon}.jpg`
  - Banner title: "TARGET FOUND" (green)
  - GPS coordinate: `DUMMY EST: {lat}, {lon}` (magenta)
  - Stats: `Spread: {X}m  CEP50: {X}m  Conf: {X}  N={count}`
  - DRONE GPS + OFFSET lines (when available)
- **Stream banner**: "TARGET FOUND" (green) for 5 seconds
- **Flag**: `_smart_result_saved` prevents duplicate saves
- Requires `--smart-estimate` CLI flag to enable SmartEstimator

### Mode 2: Full Survey
- **Trigger**: `len(_all_gps_estimates) >= SURVEY_TARGET` (default 100)
- **Output**: `generate_result_image()` saved as `RESULT_SURVEY_{lat}_{lon}.jpg`
  - Banner title: "SURVEY COMPLETE" (yellow/cyan)
  - GPS from `compute_survey_analysis()` which evaluates 5 methods:
    1. Simple mean
    2. Weighted mean (1/pdist^2)
    3. Component-wise median
    4. Tightest-10 cluster median (reuses SmartEstimator logic)
    5. Central-only median (pdist < 200)
  - Picks tightest-10 as the best method (most robust against outliers)
  - Stats: `N={count}  CEP50={X}m  method={name}  tight10_spread={X}m  central={count}`
- **Stream banner**: "SURVEY COMPLETE" (yellow) for 5 seconds
- **Flag**: `_survey_result_saved` prevents duplicate saves

Both modes reset via `/api/clear-all`.

---

## 8. CV Pipeline Visual

**Source**: `field_tools/cv_pipeline_visual.py` -> `get_cv_pipeline_html()`
**Container**: `<div id="cv-pipeline-host">` replaced at page serve.

### 6-Stage Pipeline Diagram
Horizontal row of cards with arrow connectors (gradient #333 -> #0a0):

1. **Camera** -- IMX296 global shutter, 5.02x3.76mm sensor, f=5.46mm, 1456x1088 BGR, inverted mount
2. **Preprocess** -- BGR pass-through, optional cv2.remap undistort (+1.5ms), no resize
3. **Model Input** -- YOLOv8n TFLite, tensor [1,640,640,3] f32, letterbox 1456x1088 -> pad to 1456x1456 -> resize to 640x640
4. **Inference** -- Pi TFLite ~206ms (4.8 FPS), Pi NCNN ~100ms (10 FPS), Laptop ~30ms. Output [1,5,8400]: 8400 candidates x 5 (cx,cy,w,h,conf) -> NMS. Dynamic values: `cvp-inf-ms`, `cvp-inf-fps`
5. **Detection** -- output (found, cx, cy, conf), pixel coords 1456x1088, threshold >= 0.4, class "dummy". Dynamic values: `cvp-det-conf`, `cvp-det-pos`
6. **GPS Estimation** -- f_px = 1584px, pixel offset -> meters -> rotate by yaw -> GPS offset, weight = 1/alt^2 x centrality. Dynamic value: `cvp-gps-alt`

Each card: #1a1a1a background, #333 border (hover: #0a0), green badge number, icon + uppercase name.

### FOV Geometry Canvas (320x180)
- Side-view diagram: sky-to-ground gradient background
- Drone at altitude with `[ DRONE ]` label
- FOV cone (green gradient fill + green edges)
- Altitude dashed line with label
- Ground line (dashed #2a4a2a)
- Ground coverage bracket (green, 2px) with width label (bold) + height label (smaller)
- HFOV arc at drone position
- Detection marker on ground when active
- Dynamic: updates with altitude, recalculates ground coverage and GSD

### Geometry Info Panel (beside canvas)
- Ground coverage at altitude: alt, width, height, HFOV, GSD (mm/px)
- Detection range: dummy pixel heights at 10m, 30m, 50m
- GPS accuracy: CEP50 ~2.3m, GPS lag 100-200ms, at 5m/s ~1m error

### Summary Bar
- Bottom row: Latency (`cvp-sum-lat`), FPS (`cvp-sum-fps`), Model: YOLOv8n, Input: 640x640, Sensor: 1456x1088, f_px: 1584

### Live Update API
- `window.updatePipelineData({alt, yaw, lat, lon, fps, det_conf, det_cx, det_cy})`
- Called from status polling in main page JS
- Updates inference FPS/ms, detection conf/position, GPS altitude, FOV canvas geometry,
  summary bar values

---

## 9. GPS Pipeline Visual

**Source**: `field_tools/gps_pipeline_visual.py` -> `get_gps_pipeline_html()`
**Container**: `<div id="gps-pipeline-host">` replaced at page serve.

### Interactive Controls
4 sliders at top, centered flex layout:
- **Altitude slider** (5-60m, step 1, cyan accent)
- **Detection X slider** (0-1456px, step 1, magenta accent)
- **Detection Y slider** (0-1088px, step 1, magenta accent)
- **Yaw slider** (0-359 degrees, step 1, yellow accent)

### Left Column: Geometry Diagrams

**Camera Projection SVG (440x340)**:
- Sky gradient (#0a0a2e) top half, ground gradient (#1a2a1a) bottom half
- Drone body (gray rectangle with cyan circle, propeller arms)
- Altitude dashed line with label
- FOV cone (cyan, dashed)
- Ground coverage bar (green) with width/height label
- Detection point on ground (magenta) with projection ray from drone
- dx offset arrow (magenta) with marker arrowheads
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

1. **Pixel Offset from Centre** -- dx_px = cx - 728, dy_px = cy - 544
2. **Pixels to Ground Metres** -- f_px = 5.46 x 1456 / 5.02 = 1584px, dx_m = dx_px x alt / f_px
3. **Body Frame Mapping** -- forward_m = -dy_m, right_m = dx_m
4. **Rotate by Drone Yaw** -- north = fwd*cos(yaw) - rgt*sin(yaw), east = fwd*sin(yaw) + rgt*cos(yaw)
5. **Metres to GPS Offset** -- est_lat = drone_lat + north/111320, est_lon = drone_lon + east/(111320*cos(lat))
6. **Weighted Accumulation** -- w = 1/alt^2 x centrality, shows weight comparison at two altitudes

### Summary Card
- Ground offset from drone: N meters, E meters
- Distance and bearing
- Weight at current altitude

### Live Update API
- `window.updateGPSData({alt, fov_deg, ground_w, ground_h, f_px})`
- Called from status polling in main page JS
- All values and diagrams recalculate interactively via sliders

---

## 10. API Endpoints

All served by the `Handler` class in `field_tools/passive_watch.py`.

### Page & Stream Endpoints
| Endpoint | Method | Content-Type | Description |
|----------|--------|-------------|-------------|
| `/` | GET | text/html | Main dashboard page (injects all 4 component HTML blocks) |
| `/stream` | GET | multipart/x-mixed-replace | Live MJPEG stream (30fps cap, 0.033s sleep) |
| `/snapshot` | GET | image/jpeg | Latest detection frame (or current frame if no detection) |
| `/latest` | GET | image/jpeg | Latest detection snapshot JPEG (frozen at detection time, with HUD) |
| `/best` | GET | image/jpeg | Best (most central) detection snapshot JPEG (with HUD) |
| `/smart-grid` | GET | image/jpeg | Server-rendered 5x2 grid of smart cluster frames |
| `/bullseye` | GET | image/jpeg | Legacy server-rendered bullseye scatter plot (5 panels) |
| `/map` | GET | image/jpeg | Raw map.jpg file (cached 24h via Cache-Control, loaded once by canvas) |
| `/map-rendered` | GET | image/jpeg | Legacy server-rendered map with dots overlay |

### Data API Endpoints
| Endpoint | Method | Content-Type | Description |
|----------|--------|-------------|-------------|
| `/api/drone` | GET | application/json | Drone telemetry: `{lat, lon, alt, yaw, sats, mode}` |
| `/api/estimates` | GET | application/json | GPS estimates for map: `{estimates: [[lat,lon],...], smart: [lat,lon] or null}` |
| `/api/estimates-full` | GET | application/json | Full estimates for charts (see schema below) |
| `/api/status` | GET | application/json | Full status (see schema below) |

**`/api/estimates-full` response schema:**
```json
{
  "estimates": [[lat, lon, pdist, alt, conf], ...],
  "smart": {
    "locked": bool,
    "cluster": [[lat, lon, pdist], ...],
    "spread": float,
    "median": [lat, lon] or null
  } or null,
  "drone": {"lat": float, "lon": float},
  "mean": [lat, lon] or null,
  "n": int,
  "ground_truth": {"lat": float, "lon": float} or null,
  "best": {
    "est_lat": float, "est_lon": float,
    "drone_lat": float, "drone_lon": float,
    "center_dist": float
  } or null,
  "smart_spread": float,
  "smart_count": int
}
```

**`/api/status` response schema:**
```json
{
  "frames": int, "detections": int, "det_pct": str, "saved": int,
  "cam_fps": str, "vis_fps": str, "stream_fps": str,
  "gps_lat": str, "gps_lon": str, "alt": str, "sats": int, "flight_mode": str,
  "est_lat": str, "est_lon": str, "est_obs": int,
  "fov_deg": str, "cal_1m_w": str, "cal_1m_h": str,
  "active_model_id": int, "conf_threshold": float, "class_filter": str,
  "bullseye_map_bg": bool,
  "smart_spread": float, "smart_count": int
}
```

### Control API Endpoints
| Endpoint | Method | Response | Description |
|----------|--------|----------|-------------|
| `/api/switch-model?id=N` | GET | `{ok, model, id, path}` or `{ok:false, error}` | Switch model (0-3). Waits up to 10s for main loop to complete reload. |
| `/api/set-conf?val=X` | GET | `{ok, conf}` | Set confidence threshold (0.01-0.99) |
| `/api/set-class?name=X` | GET | `{ok, class_filter}` | Set class filter (all/dummy/person/bird) |
| `/api/set-smart?spread=X&count=Y` | GET | `{ok, spread, count}` | Update SMART cluster params (spread 0.1-5.0, count 3-50). Resets lock, clears all estimates in SmartEstimator, resets `_smart_result_saved`. |
| `/api/set-ground-truth?lat=X&lon=Y` | GET | `{ok, ground_truth}` | Set ground truth position for error analysis |
| `/api/clear-ground-truth` | GET | `{ok}` | Clear ground truth |
| `/api/clear-all` | GET | `{ok}` | Reset everything: all GPS estimates, smart estimator (reinit), best detection, dummy estimator, all JPEG snapshots/plots, result flags, result banner |
| `/api/reset-best` | GET | `{ok}` | Reset only best detection tracking (center dist, JPEG, GPS) |
| `/api/toggle-bullseye-bg` | GET | `{ok, map_bg}` | Toggle satellite map background on legacy bullseye |

### Polling Intervals (client-side)
| What | Interval | Source |
|------|----------|--------|
| `/api/status` + image refreshes (latest, best, smart-grid) | 2000ms | Main page `setInterval` in HTML_PAGE |
| `/api/drone` | 500ms | interactive_map.py `setInterval` |
| `/api/estimates-full` (map component) | 2000ms | interactive_map.py `setInterval` |
| `/api/estimates-full` (GPS charts) | 1000ms | gps_charts.py `setInterval` |

---

## 11. Performance Rules (DO NOT VIOLATE)

| Rule | Value | Reason |
|------|-------|--------|
| Stream sleep | 0.033s (30fps) | Never go below -- matches Pi camera rate |
| Status/image polling | 2000ms | No faster -- browser overhead |
| GPS charts polling | 1000ms | Needed for smooth convergence chart |
| Drone position polling | 500ms | Smooth map tracking, low payload |
| Detection snapshots | On detection event only | NOT every frame |
| JPEG quality: stream | Configured by args | Default 70-80% |
| JPEG quality: thumbnails | 85% (latest/best), 80% (smart-grid, bullseye, map) | Balance size/quality |
| Dashboard CPU overhead | <5% of detection pipeline | Site is read-only display |
| Map image | Loaded once, cached 24h | 12MB, never re-fetch |
| Canvas redraw | Only on `needsRedraw` flag | requestAnimationFrame loop |
| Smart grid | Rendered server-side (OpenCV numpy) | Keeps browser light |

---

## 12. Feature Status

| # | Feature | Status | Component | Notes |
|---|---------|--------|-----------|-------|
| 1 | Live MJPEG camera stream at 30fps | DONE | passive_watch.py `/stream` | 0.033s sleep cap |
| 2 | Full HUD overlay (GPS, FPS, compass, crosshair, scale bar) | DONE | passive_watch.py `draw_overlay()` | Black outline technique |
| 3 | Pink line center-to-detection with pixel+meter labels | DONE | passive_watch.py `draw_overlay()` | Bigger labels, black bg |
| 4 | Detection bounding box (green, fading with age, black bg text) | DONE | passive_watch.py `draw_overlay()` | Age < 2s |
| 5 | Latest Detection snapshot with HUD (DRONE/DUMMY EST/OFFSET/class/conf) | DONE | `/latest` + `_snapshot_overlay()` | Updates on new detection |
| 6 | Best Detection snapshot with HUD (most central, same info bar) | DONE | `/best` + `_snapshot_overlay()` | Reset via button |
| 7 | Zoom/pan on detection images (scroll+drag+dblclick) | DONE | HTML_PAGE JS (`.zoom-wrap`) | 1x-8x zoom |
| 8 | SMART Frames grid with status banner + live progress | DONE | `/smart-grid` + `render_smart_grid()` | 5x2, server-rendered, full HUD on each frame |
| 9 | Model selector (4 models) with loading status | DONE | Control bar + `/api/switch-model` | Thread-safe, 10s timeout |
| 10 | Confidence slider (synced from server) | DONE | Control bar + `/api/set-conf` | 0.05-0.95 range |
| 11 | Class filter dropdown (all/dummy/person/bird) | DONE | Control bar + `/api/set-class` | Bird for COCO compat |
| 12 | Smart cluster controls (spread + count, adjustable in browser) | DONE | Control bar + `/api/set-smart` | Resets lock on change |
| 13 | Clear All button (resets everything) | DONE | Control bar + `/api/clear-all` | Includes result flags |
| 14 | Reset Best button | DONE | Control bar + `/api/reset-best` | Resets best only |
| 15 | Interactive satellite map (zoom/pan/dblclick-reset, high-DPI) | DONE | `field_tools/interactive_map.py` | Canvas + requestAnimationFrame |
| 16 | Drone position dot + heading arrow on map | DONE | interactive_map.py | Blue circle, white ring, arrow, 500ms poll |
| 17 | Camera FOV footprint rectangle (rotated by yaw, dashed) | DONE | interactive_map.py | Cyan-green, alt >= 0.5m |
| 18 | GPS estimate dots on map (heatmap by pdist centrality) | DONE | interactive_map.py | Green-yellow-red |
| 19 | Smart cluster median star on map (magenta) | DONE | interactive_map.py | "SMART" label, locked only |
| 20 | Ground truth star on map (yellow, always on top) | DONE | interactive_map.py | Black outline + yellow fill |
| 21 | Zone overlays (search/flight/SSSI/takeoff) | DONE | interactive_map.py | Color-coded polygons |
| 22 | Scale bar on map (auto nice distance) | DONE | interactive_map.py | White, bottom-left |
| 23 | Camera coverage trace on map (toggle+clear) | DONE | interactive_map.py | Blue fill, max 2000 |
| 24 | Main GPS scatter plot (500x400, bullseye rings, zoom/pan) | DONE | `field_tools/gps_charts.py` | Canvas, high-DPI |
| 25 | 4 scatter color modes (pixel centrality, distance centrality, altitude, confidence) | DONE | gps_charts.py toolbar | Global color range |
| 26 | Dots toggle (ON/OFF) | DONE | gps_charts.py toolbar | Markers still draw when dots off |
| 27 | Scatter map background toggle (default ON) | DONE | gps_charts.py toolbar | Dark overlay for readability |
| 28 | Scatter zoom/pan (scroll+drag, mouse-centered) | DONE | gps_charts.py | 0.1x-200x range |
| 29 | Scatter click-to-inspect dot tooltip (3s auto-hide) | DONE | gps_charts.py | Shows lat/lon/alt/conf/cdist |
| 30 | Ground truth input (lat,lon) with Set/Clear | DONE | gps_charts.py toolbar + `/api/set-ground-truth` | Yellow star, auto-loads from server |
| 31 | Filter sliders (pdist/distance/alt/conf min+max, mode-specific) | DONE | gps_charts.py filter row | Auto-adjust max, one visible per mode |
| 32 | 7 marker shapes on scatter (mean/weighted/median/GT/best/smart/central) | DONE | gps_charts.py | See marker table above |
| 33 | Scatter stats bar (N, CEP50, max, all 6 error distances) | DONE | gps_charts.py | GT-relative or mean-relative |
| 34 | Error convergence line chart (mean/weighted/median) | DONE | gps_charts.py (500x200) | Needs 2+ detections |
| 35 | Smart cluster mini-chart (tightest cluster, 3 phases) | DONE | gps_charts.py (250x300) | Live dots, numbered, outlier X marks |
| 36 | Central 4m bullseye (<200px, 5m radius, 10+ triggers markers) | DONE | gps_charts.py (250x300) | Magenta star + cyan square after 10 |
| 37 | CV Pipeline 6-stage diagram | DONE | `field_tools/cv_pipeline_visual.py` | Static cards + live dynamic values |
| 38 | CV Pipeline FOV geometry canvas (320x180) | DONE | cv_pipeline_visual.py | Dynamic altitude, GSD, detection range |
| 39 | GPS Pipeline interactive SVG diagrams | DONE | `field_tools/gps_pipeline_visual.py` | 4 sliders for alt/cx/cy/yaw |
| 40 | GPS Pipeline calibration reference table | DONE | gps_pipeline_visual.py | 4 altitude rows + current |
| 41 | GPS Pipeline 6-step equations | DONE | gps_pipeline_visual.py | All compute live from sliders |
| 42 | GPS Pipeline yaw rotation compass | DONE | gps_pipeline_visual.py | Body+world frame axes |
| 43 | Live pipeline data updates from status poll | DONE | HTML_PAGE JS | updatePipelineData + updateGPSData |
| 44 | Server syncs model/conf/class/smart back to UI controls | DONE | `/api/status` polling | Prevents UI desync |
| 45 | SRT pitch/roll extraction for camera feed | DONE | passive_watch.py (fake mode) | From DJI SRT telemetry |
| 46 | Map background ON by default (GPS charts + bullseye) | DONE | gps_charts.py, passive_watch.py | `mapBgOn = true`, `bullseye_map_bg = True` |
| 47 | Model switch with XNNPACK deadlock fix | DONE | passive_watch.py | Thread-safe model reload |
| 48 | Fake mode (replay DJI video + SRT telemetry) | DONE | passive_watch.py `--fake` | No camera/mavproxy needed |
| 49 | Map calibration tool | DONE | `tools/map_calibrate.py` | Standalone utility |
| 50 | Responsive layout (collapses at 1000px) | DONE | HTML_PAGE CSS `@media` | Single column fallback |
| 51 | Quick Lock result mode (SMART) | DONE | passive_watch.py | Saves RESULT_SMART image + 5s banner |
| 52 | Full Survey result mode (100 estimates) | DONE | passive_watch.py | Saves RESULT_SURVEY image + 5s banner |
| 53 | Best detection GPS on scatter (red circle + X + dashed line) | DONE | gps_charts.py | Estimate + drone + offset line |
| 54 | Central-10 median on scatter (orange diamond) | DONE | gps_charts.py | Labeled "4m" |
| 55 | Legacy bullseye (server-rendered, 5 panels) | DONE | passive_watch.py `render_bullseye()` | `/bullseye` endpoint |
| 56 | Legacy map-rendered | DONE | passive_watch.py `render_map()` | `/map-rendered` endpoint |
