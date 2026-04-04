# Passive Watch Dashboard — Complete Visualization Inventory

**File**: `field_tools/passive_watch.py` (~3435 lines)
**Supporting modules**: `field_tools/interactive_map.py`, `field_tools/cv_pipeline_visual.py`, `field_tools/gps_pipeline_visual.py`, `field_tools/gps_charts.py`
**Date**: 2026-04-04

---

## 1. Dashboard Layout (Browser HTML)

The browser page at `http://PI_IP:8090/` is a dark monospace-themed dashboard with three rows.

### Row 1: Camera Feed + Detections (50/50 grid)
| Panel | Element | What it shows |
|-------|---------|---------------|
| **Camera Feed** | `<img src="/stream">` MJPEG stream | Live camera with all CV2 overlays (see Section 2) |
| **Latest Detection** | `<img id="latest" src="/latest">` | Frozen snapshot of last accepted detection with overlay. Zoom+pan via mouse wheel and drag. |
| **Best Detection** | `<img id="best-det" src="/best">` | Frozen snapshot of the most-central detection seen so far. Zoom+pan enabled. |
| **SMART Frames** | `<img id="smart-grid" src="/smart-grid">` | 5x2 thumbnail grid showing the tightest cluster frames (see Section 4) |

### Row 2: Satellite Map + GPS Analysis (25/75 grid)
| Panel | Element | What it shows |
|-------|---------|---------------|
| **Satellite Map** | Interactive canvas (from `interactive_map.py`) | Zoomable/pannable satellite map with drone, estimates, zones, coverage (see Section 5) |
| **GPS Analysis** | Canvas charts (from `gps_charts.py`) | Main scatter plot + error convergence + smart cluster + central chart (see Section 6) |

### Row 3: CV Pipeline + GPS Pipeline (50/50 grid)
| Panel | Element | What it shows |
|-------|---------|---------------|
| **CV Detection Pipeline** | Diagram (from `cv_pipeline_visual.py`) | 6-stage pipeline diagram: Camera -> Preprocess -> Model Input -> Inference -> Detection -> GPS (see Section 7) |
| **GPS Estimation Pipeline** | SVG + compass (from `gps_pipeline_visual.py`) | Interactive camera projection geometry SVG + yaw rotation compass (see Section 8) |

### Control Bar (top of page, line 270-305)
| Element | Type | What it does |
|---------|------|-------------|
| **Model** dropdown | `<select>` | Switch between Original, SAR v2 TFL, SAR v2 NCNN, COCO Person models |
| **Inference FPS** badge | `<span>` | Shows current inference FPS with color: green (>=4), amber (>=2), red (<2) |
| **Conf** slider | `<input type="range">` | Confidence threshold 0.05-0.95 |
| **Class** checkboxes | 4 checkboxes | person, bird, dummy, other — filter which classes are saved |
| **Clear All** button | `<button>` | Reset all GPS estimates, SMART estimator, best detection, plots |
| **Reset Best** button | `<button>` | Reset only the best detection tracker |
| **Smart spread** input | `<input type="number">` | Max cluster spread in meters |
| **Smart count** input | `<input type="number">` | Min number of cluster points for lock |

### Status Text Lines (below control bar, line 307-310)
| Line | ID | Data | Example |
|------|----|------|---------|
| Stats | `#stats` | CAM fps, VIS fps, STR fps, Det count (%), Saved count | `CAM:14.2 VIS:4.8 STR:29.1 Det:37(12%) Saved:37` |
| GPS | `#gps` | Drone lat/lon, Alt, Sats, Mode | `DRONE:51.4234067,-2.6715321 Alt:30.2m Sats:12 Mode:GUIDED` |
| Estimate | `#est` | Estimated dummy GPS + observation count | `EST:51.4233990,-2.6715320(37obs)` |
| FOV | `#fov` | FOV degrees, calibration at 1m | `FOV: 49deg | @1m: 92x69cm` |

---

## 2. Camera Stream Overlays (cv2 drawing on every frame)

All drawn in `draw_overlay()` at line 2404. The function runs on **every display frame** (~30fps), independent of inference.

### 2.1 Top Bar (line 2526-2541)
- **Location**: Full width, top 30px, black background
- **Content**: `CAM:X.X  VIS:X.X  STR:X.X` (FPS counters in cyan)
- **Right side**: Attitude text `Y:XXX P:X.X R:X.X` (gray) + flight mode (gray)
- **Data**: `cam_fps_tracker`, `vis_fps_tracker`, `stream_fps_tracker`, `gps_data["yaw/pitch/roll/mode"]`

### 2.2 Compass Rose (line 2544-2560)
- **Location**: Top-right corner, center at (w-45, 65), radius 25px
- **Elements**: Gray circle outline, "N" label above, green arrow showing drone heading
- **Arrow**: Rotated by `yaw_deg` (0=North, clockwise), arrowedLine with tipLength=0.4
- **Data**: `gps_data["yaw"]`

### 2.3 "FRONT" Label (line 2563-2566)
- **Location**: Top center of frame, y=48
- **Content**: "FRONT" in gray with black outline
- **Purpose**: Indicates which edge of the camera frame faces forward on the drone

### 2.4 Centre Crosshair (line 2468-2476)
- **Location**: Exact frame center (w//2, h//2)
- **Elements**: Black outline (4px) + cyan inner lines (2px), length 25px each arm
- **Purpose**: Helps pilot align directly over target

### 2.5 Accepted Detection Box (line 2448-2466)
- **Condition**: `last_det is not None` and `age < 2.0 seconds`
- **Elements**:
  - Green bounding box (3px) that fades with age (`alpha = 1.0 - age/2.0`, min 0.3)
  - Label above box: `AI 0.XX [class_name]` with black background rectangle
  - Box size from `draw_overlay._last_bw`, `._last_bh`
- **Data**: `last_det = (cx, cy, conf, age)`, class from `draw_overlay._last_class`

### 2.6 Rejected Detection Box (Yellow) (line 2420-2444)
- **Condition**: `raw_det` exists, age < 0.5s, and is not the same as the filtered `last_det`
- **Elements**:
  - Yellow bounding box (2px)
  - Small crosshair at center (6px arms, yellow)
  - Label: `class conf` with black background
- **Purpose**: Shows detections that were rejected by class/confidence filter (informational)

### 2.7 Pink Detection Center Dot (line 2621-2625)
- **Condition**: `last_det` exists and age < 1.0s
- **Elements**: Filled pink circle (r=12) + white border (2px) at detection center
- **Data**: `last_det[0], last_det[1]`

### 2.8 Pink Line: Center to Detection (line 2478-2507)
- **Condition**: `last_det` exists and age < 2.0s
- **Elements**:
  - Magenta line from frame center to detection center (2px)
  - Pixel distance label at midpoint: `XXXpx` (magenta, bold 0.65 scale, black background)
  - Meters distance label below: `X.Xm` (yellow, bold 0.65 scale, black background) — only if altitude > 0.5m
- **Data**: Detection coords, `gps_data["alt"]`, FOV calculations

### 2.9 Ground Coverage Dimensions (line 2580-2593)
- **Condition**: Altitude > 0.5m
- **Elements**:
  - Width label at bottom center: `<-- X.Xm -->` (muted amber with black outline)
  - Height label on right edge at mid-height: `X.Xm` (muted amber with black outline)
- **Data**: `ground_coverage(alt)` using sensor/focal length from config

### 2.10 Scale Bar (line 2600-2618)
- **Condition**: Altitude > 0.5m and `scale_1m > 5` pixels
- **Location**: Right side, y = h-100 (above info bars)
- **Elements**: White horizontal line with end ticks (2px), label `1m (XXm alt)` with black outline
- **Data**: Computed from FOV and altitude — shows how many pixels = 1 meter

### 2.11 Dummy Estimate Bar (line 2627-2651)
- **Location**: y = h-75 (third from bottom), full width, 25px height, black background
- **Content**:
  - When estimate available: `DUMMY EST: XX.XXXXXXX, -X.XXXXXXX (N obs)` in magenta
  - When no GPS: `DUMMY EST: NO GPS -- cannot estimate` in pink-red
  - When waiting: `DUMMY EST: waiting for detection...` in gray
  - Class/confidence badge at end: `[class 0.XX]` in cyan (bold)
- **Data**: `dummy_estimator.get_estimate()`, `draw_overlay._last_class`

### 2.12 FOV / Calibration Info Bar (line 2568-2598)
- **Location**: y = h-50 (second from bottom), full width, 25px height, black background
- **Content** (when altitude > 0.5m): `FOV:XXdeg | Ground:X.XxX.Xm @XXm | Cal@1m:XXxXXcm` in amber
- **Content** (when no altitude): `FOV:XXdeg  f=X.XXmm  sens=X.XXmm | Cal@1m:XXxXXcm` in amber
- **Data**: `FOV` dict, `ground_coverage()`, `config` values

### 2.13 GPS Overlay Bar (line 2509-2523)
- **Location**: Bottom 25px, full width, black background
- **Content**: `GPS: XX.XXXXXXX, -X.XXXXXXX | Alt: XX.Xm | Sats: XX` in orange, or `GPS: No Fix | Sats: X`
- **Data**: `gps_data["lat/lon/alt/sats"]`

### 2.14 Result Banner (line 2653-2666)
- **Condition**: `_result_banner is not None` and within 5 seconds of trigger
- **Location**: Top center, semi-transparent black rectangle
- **Content**: Large text (1.2 scale) like "TARGET FOUND" (green) or "SURVEY COMPLETE" (yellow), with black outline
- **Trigger**: SMART lock or survey completion (100 estimates reached)

---

## 3. Detection Snapshot Panels (Latest + Best)

### 3.1 Latest Detection Snapshot (`_snapshot_overlay`, line 1434)
- **Size**: 728px wide, aspect-preserved resize
- **Label badge**: "LATEST" (teal, top-left) with black background rectangle
- **Info bar**: Bottom 38px black rectangle covering old overlay text
  - Line 1: `DRONE: XX.XXXXXXX, -X.XXXXXXX` (yellow)
  - Line 2: `DUMMY EST: XX.XXXXXXX, -X.XXXXXXX  OFFSET: X.Xm  [class 0.XX]` (magenta + yellow)
- **Generated by**: Inference thread on each accepted detection, served at `/latest`

### 3.2 Best Detection Snapshot
- **Size**: 1024px wide
- **Label badge**: "BEST" (green, top-left)
- **Same info bar** as Latest but higher resolution
- **Selection criteria**: Detection with smallest normalized center distance (`center_dist < _best_center_dist`)
- **Served at**: `/best`

---

## 4. SMART Frames Grid (`render_smart_grid`, line 1768)

- **Size**: 1200 x 388 px (5 columns x 2 rows of 240x180 thumbnails + 28px banner)
- **Served at**: `/smart-grid`
- **Polls**: Updated on each new smart detection + periodic refresh

### Status Banner (top 28px)
| State | Color | Text |
|-------|-------|------|
| Waiting | Dark gray `(60,60,60)` | `WAITING FOR DETECTIONS  0/N` |
| Collecting | Dark amber `(0,100,180)` | `COLLECTING  X/N` |
| Locked | Dark green `(0,140,0)` | `LOCKED  N/N  spread X.XXm  |  XX.XXXXXXX, -X.XXXXXXX` |

### Thumbnail Slots
- **Empty slots**: Dim gray border `(50,50,50)`, gray number `#X`
- **Filled slots (unlocked)**: Detection frame thumbnail, amber border, orange number `#X`
- **Filled slots (locked)**: Green border (2px), green number
- **Best frame**: Green border (3px), star symbol `#X star`, GPS coords at bottom, "BEST" badge bottom-right, all in green

---

## 5. Interactive Satellite Map (`interactive_map.py`, line 517 in handler)

Self-contained canvas component with scroll-wheel zoom + click-drag pan.

### Map Elements
| Element | Visual | Data Source |
|---------|--------|-------------|
| **Map image** | Satellite JPEG (`map.jpg`) loaded once, pan/zoom via canvas transforms | `/map` endpoint |
| **Flight Area polygon** | Blue thin outline, very faint blue fill | `config.FLIGHT_AREA_GPS` |
| **SSSI No-Fly Zone** | Red outline (1.5px), faint red fill | `config.SSSI_GPS` |
| **Search Area polygon** | Yellow outline (2px), faint yellow fill | `config.SEARCH_AREA_GPS` |
| **Takeoff marker** | White filled circle (r=4) with blue outline, "H" label | `config.TAKEOFF_GPS` |
| **Drone position** | Blue filled circle (r=5-8, scales with zoom) + white outline | `/api/drone` poll (500ms) |
| **Heading arrow** | White arrow from drone center, rotated by yaw, with arrowhead | `drone.yaw` |
| **Camera footprint** | Dashed cyan/green rectangle on ground, rotated by yaw, faint fill | Computed from alt, sensor, focal, yaw |
| **Coverage trace** | Accumulated camera footprint polygons in very faint blue fill (max 2000) | Pushes each poll when drone moves |
| **GPS estimate dots** | Small circles with centrality heatmap: green (central, low pdist) to red (edge, high pdist) | `/api/estimates-full` poll (2000ms) |
| **SMART median star** | Magenta 5-pointed star + "SMART" label | When `smart.locked` and `smart.median` exists |
| **Ground truth star** | Yellow 5-pointed star (with black outline underneath) + "TRUE" label | Set via `/api/set-ground-truth` |
| **Scale bar** | White bar at bottom-left with distance label (auto-rounds to nice values: 1,2,5,10,20,50,100,200,500m) | Computed from view zoom level |
| **Info overlay** | Top-left: lat/lon, alt, sats, mode, detection count, coverage count | Combined drone + estimates data |
| **Zoom info** | Bottom-right: zoom percentage + "dblclick=reset" hint | View scale |

### Map Buttons (top-right)
- **Coverage: ON/OFF** toggle (green when on)
- **Clear Coverage** button

---

## 6. GPS Analysis Charts (`gps_charts.py`)

Four canvas-based charts, all client-side JavaScript with no server rendering.

### 6.1 Main Scatter Plot (500x400px, `drawScatter`)
- **Bullseye rings** at 1, 2, 3, 5, 10m from mean position
- **Color modes** (switchable via toolbar buttons):
  - **Pixel Centrality**: green (central) to red (edge) based on pixel distance from frame center
  - **Distance Centrality**: green to red based on real-world distance (meters)
  - **Altitude**: green (low) to red (high)
  - **Confidence**: green (high conf) to red (low conf)
- **Mean cross marker** (green)
- **SMART median star** (magenta, with label, when locked)
- **Ground truth star** (yellow, when set)
- **Best detection diamond** (cyan, when available)
- **Map background** (toggleable satellite crop behind dots)
- **Filter sliders** (per color mode): pdist min/max, distance min/max, alt min/max, conf min/max
- **Zoom/Pan**: Mouse wheel to zoom, drag to pan, double-click to reset
- **Hover tooltip**: Shows lat, lon, pdist, alt, conf for each point
- **Stats bar** (bottom): N filtered/total, CEP50, max spread, mean/median coords

### 6.2 Error Convergence Chart (500x200px, `drawConvergence`)
- **Three running error lines**:
  - Green = running mean error
  - Cyan = running weighted error (by 1/cdist^2)
  - Magenta = running median error
- **Reference**: Ground truth (if set) or final mean
- **Y-axis**: Error in meters (0.5, 1.0, 2.0, 5.0, 10.0m grid lines)
- **X-axis**: Detection count (1 to N)
- **Legend**: mean, weighted, median labels at bottom

### 6.3 Smart Cluster Chart (250x300px, `drawCluster`)
- **Before lock (< min_samples)**: Shows all arriving dots numbered, with spread info
- **After lock**: Shows tightest cluster dots numbered, with:
  - Bullseye rings at 0.1, 0.2, 0.5, 1.0m
  - Yellow cross at center
  - Cyan numbered dots with radial lines to center
  - Magenta star at SMART median
  - "LOCKED" status + spread + GPS coordinate
  - Bottom stats: total/cluster/rejected counts, spread, CEP50

### 6.4 Central Detections Chart (250x300px, `drawCentral`)
- **Filter**: Only detections with pixel_dist < 200px (close to frame center)
- **Title**: `CENTRAL (N/10, <200px)` in magenta
- **Bullseye rings** at appropriate scales
- **Heat-colored dots** based on pixel centrality
- **Stats**: CEP50 of central detections, total/central counts

---

## 7. CV Detection Pipeline Diagram (`cv_pipeline_visual.py`)

A styled 6-stage horizontal pipeline card layout with a FOV geometry canvas.

### Pipeline Stages (6 cards in a row)
| Stage | Icon | Name | Key Info Displayed |
|-------|------|------|--------------------|
| 1 | Camera | Camera | IMX296, 5.02x3.76mm, f=5.46mm, 1456x1088, BGR, 180deg flip |
| 2 | Gear | Preprocess | BGR pass-through, cv2.remap undistort (+1.5ms), no resize |
| 3 | Frame | Model Input | YOLOv8n TFLite, [1,640,640,3] f32, letterbox pad+resize |
| 4 | Brain | Inference | **Live**: Pi TFLite Xms (X.X FPS), Pi NCNN ~100ms, Laptop ~30ms. Output [1,5,8400], NMS |
| 5 | Target | Detection | Output format, pixel coords, threshold, class. **Live**: last conf, position |
| 6 | Pin | GPS Estimation | f_px formula, projection math, weight formula. **Live**: altitude |

### FOV Geometry Canvas (320x180px, `drawFOV`)
- **Sky-to-ground gradient** background
- **Dashed ground line** with "GROUND" label
- **Drone icon** at scaled altitude
- **FOV cone**: Semi-transparent green triangle from drone to ground
- **Ground coverage bracket**: Green bar with width label (e.g., "27.6 m")
- **Altitude line**: Dashed vertical with label
- **HFOV arc**: Small arc at drone with angle label
- **Detection marker**: Red dot on ground (when active)
- **GSD label** (top-left) and **dummy pixel height** (top-right)

### Summary Bar (bottom)
- Latency, FPS, Model, Input size, Sensor size, f_px

---

## 8. GPS Estimation Pipeline Diagram (`gps_pipeline_visual.py`)

An interactive SVG + compass visualization with sliders.

### Camera Projection Geometry SVG (440x340)
- **Sky/ground gradient** background
- **Drone body** with propeller arms (top center)
- **Altitude dashed line** with label
- **FOV cone** (cyan dashed triangle)
- **Ground coverage bar** (green) with tick marks and dimension label
- **Detection point** on ground (magenta circle)
- **Detection projection ray** (magenta dashed line from drone to ground)
- **Offset arrow** (dx line with arrowhead, magenta)
- **Camera view inset** (120x90px mini-frame preview):
  - Crosshair lines
  - Center dot (cyan)
  - Detection dot (magenta, movable)
  - dx/dy offset lines in frame
  - Resolution label
- **Legend**: Drone nadir, Detection, Ground coverage

### Interactive Controls
| Slider | Range | What it changes |
|--------|-------|----------------|
| Altitude (m) | 5-60 | FOV cone size, ground coverage, altitude label |
| Detection X (px) | 0-1456 | Detection position in frame and on ground |
| Detection Y (px) | 0-1088 | Detection position in frame and on ground |
| Yaw (deg) | 0-359 | Body frame rotation in compass |

### Yaw Rotation Compass SVG (260x260)
- **Compass ring** (r=100) with N/E/S/W labels and tick marks
- **Inner ring** (r=60, dashed)
- **Body frame axes** (rotate with yaw):
  - Cyan "fwd" arrow (forward direction)
  - Magenta "right" arrow
- **World frame axes** (fixed): Gray dashed N and E arrows

### 5-Step Calculation Cards
Each step is a styled card showing the math:
1. **Pixel Offset**: dx, dy from frame center
2. **Ground Offset (m)**: pixels to meters via altitude and f_px
3. **Yaw Rotation**: Forward/right to north/east
4. **Yaw compass** (the SVG above)
5. **GPS Conversion**: meters to lat/lon degrees

---

## 9. Saved Result Images

### 9.1 SMART Result Image (`generate_result_image`, line 1575)
- **Trigger**: SMART estimator locks (tightest cluster < max_spread)
- **Saved to**: `smart_detections/NNNN_XX.XXXXXXX_-X.XXXXXXX.png`
- **Top banner** (120-180px semi-transparent black):
  - Title: "SMART COORDINATE" in green (bold 1.4 scale, with black outline)
  - GPS line: `SMART: XX.XXXXXXX, -X.XXXXXXX` in magenta
  - Stats line: `Spread: X.XXm  CEP50: X.XXm  N=X` in gray
  - Drone GPS line: `DRONE: XX.XXXXXXX, -X.XXXXXXX` in cyan (if available)
  - Offset line: `OFFSET: X.Xm` in yellow (if available)
- **Body**: The detection frame with full overlay
- **Map panel** (bottom): Satellite map crop at target width with:
  - SSSI polygon (red outline)
  - Search area polygon (yellow outline)
  - Magenta star at estimated GPS position
  - White circle outline around star
  - Black label bar: `MAP: XX.XXXXXXX, -X.XXXXXXX` in magenta

### 9.2 Survey Result Image
- **Trigger**: 100 GPS estimates reached
- **Saved to**: `detections/RESULT_SURVEY_XX.XXXXXXX_-X.XXXXXXX.jpg`
- **Same format** as SMART result but:
  - Title: "SURVEY COMPLETE" in yellow
  - GPS method: tight-10 cluster median
  - Stats include: N, CEP50, method, tight10_spread, n_central

### 9.3 Normal Detection Snapshots (non-SMART mode)
- **Saved to**: `detections/det_NNNN_0.XX_XX.XXXXXXX_-X.XXXXXXX.jpg` (or simple names)
- **Content**: Detection frame with overlay + stamp lines on right side:
  - Time + confidence
  - Drone GPS + altitude
  - Dummy estimate + observation count
- **JSON sidecar**: Full metadata (detection, drone, FOV, estimate)

---

## 10. Server-Rendered Map (`render_map`, line 1868)

Legacy server-rendered JPEG at `/map-rendered` (replaced by interactive canvas map but still available).

- **Size**: 600px wide, aspect-preserved from map.jpg
- **Green dots**: All GPS estimates (r=3)
- **Magenta star**: SMART median (when locked)
- **Blue dot**: Drone position (r=5)
- **Title bar**: Black, `MAP: N estimates` in yellow

---

## 11. Server-Rendered Bullseye Plots (`render_bullseye`, line 1926)

Legacy server-rendered JPEG at `/bullseye` (replaced by `gps_charts.py` canvas charts but still generated).

5 panels (or 3 when SMART disabled), each 350x350px, assembled horizontally.

### Panel 1: GPS by Center Distance
- Satellite map crop background (toggleable) or dark background
- Bullseye rings at 1, 2, 3, 5, 10m
- Green cross at center (mean position)
- Heat-colored dots: green (central) to red (edge) by pixel distance
- Bottom: CEP50 + max spread + estimate GPS

### Panel 2: GPS by Altitude
- Same layout as Panel 1
- Color: green (low altitude) to red (high altitude)
- Vertical color bar on right side (altitude range)

### Panel 3: Error Convergence (Line Chart)
- Dark background
- Three colored lines: green (mean), cyan (weighted), magenta (median)
- Y-axis: error in meters (grid lines at 0.5, 1, 2, 5, 10m)
- X-axis: detection count
- Axes drawn, legend at bottom

### Panel 4: Smart Bullseye (SMART only)
- When locked: "LOCKED" + spread + GPS coordinate, numbered cyan dots with radial lines, magenta SMART star, bottom stats bar
- When unlocked: "searching..." + detection count + criteria

### Panel 5: Central Detections (SMART only)
- Filters detections with pixel_dist < 200
- Same heat-colored dots as Panel 1
- CEP50 of central-only detections

### SMART GPS Banner (bottom, when locked)
- Green bar across full width: `SMART GPS: XX.XXXXXXX, -X.XXXXXXX  (N samples, spread X.XXm)`

---

## 12. API Endpoints Summary

| Endpoint | Returns | Used By |
|----------|---------|---------|
| `/stream` | MJPEG multipart stream (~30fps) | Camera Feed panel |
| `/latest` | JPEG of latest detection snapshot | Latest Detection panel |
| `/best` | JPEG of best detection snapshot | Best Detection panel |
| `/smart-grid` | JPEG of smart frames 5x2 grid | SMART Frames panel |
| `/bullseye` | JPEG of 5-panel bullseye plots | Legacy (replaced by canvas) |
| `/map` | Static satellite map JPEG | Interactive map canvas background |
| `/map-rendered` | JPEG of server-rendered map with dots | Legacy |
| `/snapshot` | JPEG of latest detection or frame | Direct access |
| `/api/status` | JSON telemetry + stats | 2-second status polling |
| `/api/drone` | JSON drone position + heading | Interactive map (500ms poll) |
| `/api/estimates` | JSON GPS estimate list + smart | Interactive map |
| `/api/estimates-full` | JSON detailed estimates + smart cluster + ground truth | GPS charts (2s poll) |
| `/api/switch-model` | Switch AI model | Model dropdown |
| `/api/set-conf` | Change confidence threshold | Conf slider |
| `/api/set-class` | Change class filter | Class checkboxes |
| `/api/set-smart` | Change smart spread/count | Smart inputs |
| `/api/set-ground-truth` | Set known dummy position | GPS charts toolbar |
| `/api/clear-ground-truth` | Remove ground truth | GPS charts toolbar |
| `/api/toggle-bullseye-bg` | Toggle map background on bullseye | Legacy |
| `/api/clear-all` | Reset everything | Clear All button |
| `/api/reset-best` | Reset best detection only | Reset Best button |
