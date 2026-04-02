# Passive Watch Browser Dashboard — Vision Document

> Single source of truth for the browser dashboard at `http://PI_IP:8090/`.
> File: `field_tools/passive_watch.py` (1476 lines).
> Reference: `video_test_compare.py` is the gold standard — replicate its visual quality in the browser.
> Updated: 2026-04-02 — Model selector, confidence slider, class filter, interactive map, CV/GPS pipeline visuals.

---

## 0. Feature Tracker — All Requested Features

### IMPLEMENTED (previous session)

| # | Feature | Status | Location |
|---|---------|--------|----------|
| 1 | Pink line from frame center to detection center | DONE | `draw_overlay()` in passive_watch.py |
| 2 | Pixel distance label at midpoint | DONE | `draw_overlay()` — magenta text |
| 3 | Real distance (meters) label at midpoint | DONE | `draw_overlay()` — `{px}px ({m:.1f}m)` |
| 4 | Scale bar (1m reference, altitude-dependent) | DONE | `draw_overlay()` — bottom-right, amber |
| 5 | Enhanced detection snapshot (/latest) with pink line + distances | DONE | `render_latest_detection()` |

### IMPLEMENTED (this session)

| # | Feature | Status | Location |
|---|---------|--------|----------|
| 6 | Model selector dropdown (4 models: Original, SAR v2 TFLite, SAR v2 NCNN, COCO Person) | DONE | Browser HTML dropdown + `/api/switch-model` endpoint |
| 7 | Confidence threshold slider (0.05-0.95) | DONE | Browser HTML slider + real-time update |
| 8 | Class filter dropdown (all/dummy/person) | DONE | Browser HTML dropdown + server-side filter |
| 9 | Runtime model switching via `/api/switch-model` | DONE | HTTP POST endpoint, hot-swaps VisionSystem |
| 10 | Interactive map with zoom/pan (Canvas-based) | DONE | `field_tools/interactive_map.py` |
| 11 | Live drone position on map (500ms polling via `/api/drone`) | DONE | Purple dot + heading arrow on Leaflet map |
| 12 | Camera footprint rectangle on map (FOV + altitude + yaw) | DONE | Purple FOV rectangle, rotated by yaw |
| 13 | GPS estimate dots on map | DONE | Heat-colored dots (green→yellow→red by centrality) |
| 14 | Smart cluster median star on map | DONE | Magenta dot (8px) when SmartEstimator locks |

### IN PROGRESS

| # | Feature | Status | Location |
|---|---------|--------|----------|
| 15 | CV pipeline visual diagram | IN PROGRESS | `field_tools/cv_pipeline_visual.py` |
| 16 | GPS estimation pipeline visual | IN PROGRESS | `field_tools/gps_pipeline_visual.py` |

### EXISTING (unchanged from earlier sessions)

| # | Feature | Status | Location |
|---|---------|--------|----------|
| 17 | MJPEG live stream | DONE | `/stream` endpoint, continuous ~20fps |
| 18 | GPS bullseye scatter plot | DONE | Plotly.js 3-panel chart (ALL / SMART / CENTER DIST) |
| 19 | Smart frames grid (5x2) | DONE | `/smart-grid` endpoint, 10 thumbnails |
| 20 | Latest detection thumbnail | DONE | `/latest` endpoint with overlay |
| 21 | Satellite map with estimates | DONE | Leaflet.js with CartoDB/OSM/satellite layers |
| 22 | FPS/GPS/Estimate/FOV info panels | DONE | `/api/status` JSON, polled every 2s |

---

## 1. Camera & Image Schematic

```
  IMX296 Global Shutter Sensor
  ┌─────────────────────────────────────┐
  │  Sensor: 5.02mm wide               │
  │  Focal length: 5.46mm              │
  │  Mounted INVERTED (CAMERA_FLIP_180)│
  └──────────────┬──────────────────────┘
                 │
                 ▼
  ┌─────────────────────────────────────┐
  │         Camera Frame                │
  │                                     │
  │   1456 pixels wide                  │
  │  ◄─────────────────────────────────►│
  │  ┌─────────────────────────────────┐│ ▲
  │  │ (0,0)              (1456,0)     ││ │
  │  │                                 ││ │
  │  │          (+) center             ││ 1088 pixels
  │  │        (728, 544)               ││ tall
  │  │                                 ││ │
  │  │ (0,1088)          (1456,1088)   ││ │
  │  └─────────────────────────────────┘│ ▼
  │                                     │
  │  Aspect ratio: 1.338 (4:3-ish)     │
  │  Output format: BGR (NOT RGB)       │
  │  No cvtColor needed                 │
  └─────────────────────────────────────┘
```

**Image specs (from config.py):**

| Parameter | Value | Source |
|-----------|-------|--------|
| IMAGE_W | 1456 px | IMX296 native |
| IMAGE_H | 1088 px | IMX296 native |
| SENSOR_WIDTH_MM | 5.02 mm | IMX296 datasheet |
| FOCAL_LENGTH_MM | 5.46 mm | Calibrated 2026-03-11 (92cm visible at 1m) |
| f_px (derived) | 1577.25 px | `5.46 * 1456 / 5.02` |
| H-FOV (derived) | 49.3 deg | `2 * arctan(5.02 / (2 * 5.46))` |
| V-FOV (derived) | 36.8 deg | `H-FOV * 1088 / 1456` |

---

## 2. FOV Calibration Schematic

```
                    Drone at altitude h
                         ●
                        /|\
                       / | \
                      /  |  \
                     /   |   \
                    / θ/2|    \         θ = H-FOV = 49.3°
                   /     |     \
                  /      |h     \
                 /       |       \
                /        |        \
  ─────────────/─────────┼─────────\──────────── Ground
              ◄──── W/2 ─┼─ W/2 ───►
              ◄──────── W ─────────►

  Ground width:   W = h * SENSOR_WIDTH_MM / FOCAL_LENGTH_MM
                  W = h * 5.02 / 5.46
                  W = h * 0.9194

  Ground height:  H = W * IMAGE_H / IMAGE_W
                  H = W * 1088 / 1456
                  H = W * 0.7473

  Examples:
  ┌──────────┬───────────┬───────────┬──────────────┐
  │ Altitude │ Ground W  │ Ground H  │ 1px = metres │
  ├──────────┼───────────┼───────────┼──────────────┤
  │   10 m   │   9.2 m   │   6.9 m   │  0.0063 m    │
  │   20 m   │  18.4 m   │  13.7 m   │  0.0127 m    │
  │   35 m   │  32.2 m   │  24.1 m   │  0.0222 m    │
  │   50 m   │  46.0 m   │  34.4 m   │  0.0317 m    │
  └──────────┴───────────┴───────────┴──────────────┘

  Pixel resolution at altitude h:
    1 pixel = h / f_px = h / 1577.25 metres
```

**FOV was calibrated by:**
1. Placing camera at known height (1m) above ruler
2. Measuring visible width (92cm)
3. Computing: `FOCAL_LENGTH_MM = SENSOR_WIDTH_MM * 1m / 0.92m = 5.46mm`
4. Cross-validated with DJI video: `tools/fov_calibrate_video.py` → 54.4 deg HFOV for DJI crop (different lens)

---

## 3. Pixel-to-Distance Equation

The core equation that converts a detection's pixel position into a real-world GPS coordinate.

```
  INPUTS (per detection frame):
  ┌──────────────────────────────────────────────────┐
  │  From detection (vision.py):                     │
  │    cx, cy = pixel coords of detection center     │
  │                                                  │
  │  From GPS telemetry (mavlink_reader thread):     │
  │    drone_lat, drone_lon = GPS position (deg)     │
  │    alt = altitude AGL (metres)                   │
  │    yaw = heading (0°=North, CW positive)         │
  │                                                  │
  │  From config.py (constants):                     │
  │    IMAGE_W = 1456      IMAGE_H = 1088            │
  │    SENSOR_WIDTH_MM = 5.02                        │
  │    FOCAL_LENGTH_MM = 5.46                        │
  │    f_px = 1577.25  (derived once at startup)     │
  └──────────────────────────────────────────────────┘

  STEP 1: Normalise detection to [0,1]
  ┌──────────────────────────────────────────────────┐
  │  norm_x = cx / IMAGE_W     (0 = left, 1 = right)│
  │  norm_y = cy / IMAGE_H     (0 = top, 1 = bottom)│
  └──────────────────────────────────────────────────┘

  STEP 2: Pixel offset from frame centre
  ┌──────────────────────────────────────────────────┐
  │  dx_px = (norm_x - 0.5) * IMAGE_W               │
  │  dy_px = (norm_y - 0.5) * IMAGE_H               │
  │                                                  │
  │  Range: dx_px ∈ [-728, +728]                     │
  │         dy_px ∈ [-544, +544]                     │
  │  Sign:  +dx = right of centre                    │
  │         +dy = below centre                       │
  └──────────────────────────────────────────────────┘

  STEP 3: Pinhole model — pixels to metres on ground
  ┌──────────────────────────────────────────────────┐
  │                                                  │
  │  dx_m = dx_px * alt / f_px                       │
  │  dy_m = dy_px * alt / f_px                       │
  │                                                  │
  │  This is the KEY equation:                       │
  │                                                  │
  │     ground_distance = pixel_offset * altitude    │
  │                       ─────────────────────────  │
  │                         focal_length_pixels      │
  │                                                  │
  │  f_px = FOCAL_LENGTH_MM * IMAGE_W / SENSOR_W_MM │
  │       = 5.46 * 1456 / 5.02                      │
  │       = 1577.25 pixels                           │
  │                                                  │
  │  Example at 35m:                                 │
  │    dx_px = 200 → dx_m = 200 * 35 / 1577 = 4.4m │
  └──────────────────────────────────────────────────┘

  STEP 4: Camera frame → World frame (yaw rotation)
  ┌──────────────────────────────────────────────────┐
  │  Camera convention:                              │
  │    Top of image = drone forward (North at yaw=0) │
  │    +dx = right = East at yaw=0                   │
  │    +dy = down = backward = South at yaw=0        │
  │                                                  │
  │  Convert to drone frame:                         │
  │    forward_m = -dy_m     (up in image = forward) │
  │    right_m   =  dx_m     (right = right)         │
  │                                                  │
  │  Rotate by yaw (compass, CW positive):           │
  │    north_m = forward_m * cos(yaw) - right_m * sin(yaw) │
  │    east_m  = forward_m * sin(yaw) + right_m * cos(yaw) │
  └──────────────────────────────────────────────────┘

  STEP 5: Metres → GPS offset
  ┌──────────────────────────────────────────────────┐
  │  lat_m_per_deg = 111133 - 560 * cos(2 * lat)    │
  │  lon_m_per_deg = 111133 * cos(lat)               │
  │                                                  │
  │  At Bristol (51.42°N):                           │
  │    lat_m_per_deg ≈ 111,255 m/deg                 │
  │    lon_m_per_deg ≈ 69,407 m/deg                  │
  │                                                  │
  │  est_lat = drone_lat + north_m / lat_m_per_deg   │
  │  est_lon = drone_lon + east_m  / lon_m_per_deg   │
  └──────────────────────────────────────────────────┘

  OUTPUT:
  ┌──────────────────────────────────────────────────┐
  │  (est_lat, est_lon) = estimated target GPS       │
  └──────────────────────────────────────────────────┘
```

### Weighting Formula

Each observation is weighted by altitude and centrality:

```
  base_weight = 1 / alt^2

  dist_from_centre = sqrt(dx_px^2 + dy_px^2)
  max_diagonal = sqrt(728^2 + 544^2) = 911.2 px
  centre_factor = 1 + 4 * max(0, 1 - dist_from_centre / (max_diagonal * 0.3))

  final_weight = base_weight * centre_factor

  ┌──────────────────────────────────────────────────────┐
  │  Location      │ Alt  │ base_w │ centre │ final_w   │
  ├────────────────┼──────┼────────┼────────┼───────────│
  │  Centre, 10m   │  10  │ 0.0100 │  5.0   │  0.0500   │
  │  Centre, 30m   │  30  │ 0.0011 │  5.0   │  0.0056   │
  │  Edge, 10m     │  10  │ 0.0100 │  1.0   │  0.0100   │
  │  Edge, 30m     │  30  │ 0.0011 │  1.0   │  0.0011   │
  └──────────────────────────────────────────────────────┘

  Final GPS estimate = weighted average of all observations:
    est_lat = sum(lat_i * w_i) / sum(w_i)
    est_lon = sum(lon_i * w_i) / sum(w_i)
```

---

## 4. GPS-Frame Association

### Current State: NO LOCK (Race Condition)

```
  MAIN THREAD                      MAVLINK THREAD
  ──────────                       ──────────────
  frame = get_frame()              msg = recv_match()
  detect_in_image(frame)           gps_data["lat"] = ... ◄── can update HERE
  d_lat = gps_data["lat"]  ◄──┐   gps_data["lon"] = ... ◄── or HERE
  d_lon = gps_data["lon"]  ◄──┘   gps_data["alt"] = ...
  d_alt = gps_data["alt"]
  add_observation(d_lat, d_lon, d_alt, ...)
```

**Risk:** `d_lat` could be from message N, `d_lon` from message N+1. At 5 m/s with 10Hz GPS, worst case ~0.5m error per mismatch.

**In --fake mode:** GPS is updated per video frame from SRT telemetry. Same field-by-field issue but single-threaded so no actual race.

**Fix needed:** Snapshot `gps_data` atomically at frame capture time:
```python
with gps_lock:
    gps_snap = dict(gps_data)
# then use gps_snap throughout the frame
```

---

## 5. Dashboard Layout

```
  ┌─────────────────────────────────────────────────────────────────┐
  │ SAR Passive Watch                                    (#0f0 h1) │
  │ CAM:fps VIS:fps STR:fps Det:N(%) Saved:N             (#888)   │
  │ DRONE: lat,lon Alt:m Sats:N Mode:str                  (#0af)  │
  │ EST: lat,lon (N obs)                                   (#f0f)  │
  │ FOV: deg                                               (#b90)  │
  ├──────────────────────────────────┬──────────────────────────────┤
  │                                  │ ┌─────────┬────────────┐    │
  │                                  │ │ Latest  │ Best       │    │
  │     Camera Feed                  │ │ Det     │ (Central)  │    │
  │     (MJPEG /stream)              │ │ (#f0f)  │ (#ff0)     │    │
  │     3fr width                    │ ├─────────┴────────────┤    │
  │                                  │ │ SMART Frames (10)    │    │
  │                                  │ │ 5x2 grid thumbnails  │    │
  │                                  │ 2fr width              │    │
  ├───────────┬──────────────────────┼──────────────────────────────┤
  │ Leaflet   │ Plotly Bullseye      │ SMART Frames                │
  │ Map       │ (3-panel chart)      │ (duplicate)                 │
  │           │ + centrality slider  │                             │
  │ 1fr       │ 1fr                  │ 1fr                         │
  ├───────────┴──────────────────────┴──────────────────────────────┤
  │ GPS Estimation Math Diagram (/equation)                        │
  └─────────────────────────────────────────────────────────────────┘

  Responsive: columns collapse to single-column at <1000px viewport.
  Background: #111 dark theme, monospace font throughout.
```

---

## 6. Bullseye Panels — Current vs Intended

### Current Plotly (3 panels in browser):

| Panel | Title | Center | Color | Unique Feature |
|-------|-------|--------|-------|----------------|
| 1 | ALL DETECTIONS | Arithmetic mean | heat(pixel_dist or ground_dist) | Green rings 1,2,3,5,10m |
| 2 | SMART CLUSTER | Smart median | Yellow #ff0 | Numbered dots + magenta median diamond |
| 3 | CENTER DIST | **Arithmetic mean** | heat(same as P1) | Cyan diamond (estimate) + CEP50 stats |

### BUG: Panel 1 and Panel 3 are redundant

Both plot `eM, nM` (same arrays) with `colors` (same array), centered on `meanLat, meanLon` (same center). Panel 3 only adds the estimate diamond — otherwise identical scatter.

**The static OpenCV bullseye has a 4th panel** (CENTRALITY meters) that colors by `ground_dist_m` instead of `pixel_dist`. This panel is missing from Plotly.

### Proposed fix:

| Panel | Title | Center | Color | Purpose |
|-------|-------|--------|-------|---------|
| 1 | ALL DETECTIONS | Arithmetic mean | heat(pixel_dist) | Raw scatter — how spread are detections? |
| 2 | SMART CLUSTER | Smart median | Yellow numbered | Tightest 10 — convergence quality |
| 3 | CENTER DIST | **Weighted estimate** | heat(ground_dist_m) | Error from best guess + CEP50 stats |

**Changes needed in `updateBullseye()`:**
1. Compute separate `eM3, nM3` arrays centered on `estimate.lat/lon` instead of `meanLat/meanLon`
2. Color Panel 3 by `ground_dist_m` (not same `colors` array as Panel 1)
3. This makes each panel genuinely different

### Color Toggle Button

The "Color: pixel_dist" button toggles `colorMode` between `pixel_dist` and `ground_dist_m`. This currently affects Panels 1 AND 3 identically. After the fix, Panel 1 would always use pixel_dist and Panel 3 would always use ground_dist_m — the toggle could be removed or kept for Panel 1 only.

### Centrality Slider

Slider (0-500 pixels) filters detections by `pixel_dist < threshold`. Value 500 = show all. Filtering happens client-side only (JS). Server always sends all detections.

---

## 7. Panel Specifications (Detailed)

### 7a. Camera Feed (`/stream`)
- MJPEG multipart stream, continuous ~20fps
- Full `draw_overlay()` applied (see Section 9)
- Left 3fr of row 1

### 7b. Latest Detection (`/latest`)
- Crop around bounding box with margin
- Resized to 600px wide
- Overlays: cyan crosshair, green bbox, magenta dot, magenta line, distance label
- Info strip below (dark bg, 3 lines):
  - Cyan: `DETECT: {class} conf={conf:.2f} cdist={px_dist:.0f}px {dist_m:.1f}m`
  - Gray: `DRONE: {alt:.1f}m AGL {lat:.6f}, {lon:.6f}`
  - Green: `TARGET: {est_lat:.7f}, {est_lon:.7f}`
- JPEG quality 95

### 7c. Best (Most Central) Detection (`/best`)
- Same format as Latest Detection
- Only updates when new detection has smaller pixel distance from frame center
- Persists across entire session

### 7d. SMART Frames Grid (`/smart-grid`)
- 5x2 grid = 10 thumbnails, each 240x180px
- Canvas: 1200x360px
- Cyan `#N` label on each thumbnail
- Green border when cluster is locked
- **BUG: Shows first 10 from `all_estimates` (FIFO), NOT the 10 that form the locked cluster**
- JPEG quality 95

### 7e. Interactive Map (Leaflet.js)

**Interaction:** Scroll to zoom, drag to pan, pinch on mobile. "Fit Detections" button auto-zooms to show all markers with 20% padding.

**Tile layers:**
- Dark CartoDB (default, online): `basemaps.cartocdn.com/dark_all/`
- OSM Standard (online): `tile.openstreetmap.org`
- Satellite (local, offline): `/assets/map.jpg` overlaid on map bounds

**Markers on the map:**

```
  MARKER LEGEND
  ┌─────────────────────────────────────────────────────┐
  │  ▓ Purple FOV rectangle (#9900ff, 15% fill)         │
  │    = Camera ground footprint at current altitude     │
  │    Sized by: alt * SENSOR_W / FOCAL_L * aspect      │
  │    Rotated by drone yaw (heading)                    │
  │    Popup: "Camera FOV", altitude AGL                 │
  │    Updates at 5Hz (200ms) via /api/drone             │
  │                                                      │
  │  ● Purple dot (4px) #7700ff                          │
  │    = Drone GPS position (centre of FOV rectangle)    │
  │    Popup: Alt + Yaw                                  │
  │                                                      │
  │  → Purple heading arrow (#cc44ff, 3px line)          │
  │    = Direction drone is facing (yaw)                 │
  │    Length proportional to altitude (alt * 0.4, min 5m)│
  │                                                      │
  │  ● Small (3px) heat-colored dots                     │
  │    = Individual detection GPS estimates               │
  │    Green = detection near image centre                │
  │    Yellow = medium offset                             │
  │    Red = detection near image edge                    │
  │    Popup: Det #N, Alt, Pixel dist, Ground dist        │
  │                                                      │
  │  ● Magenta dot (8px) #ff00ff                         │
  │    = SMART median (locked cluster centre)             │
  │    Only appears when SmartEstimator locks              │
  │    Popup: SMART Median, lat/lon, Spread               │
  │                                                      │
  │  ⚠ MISSING: Weighted estimate (DummyEstimator)       │
  │    is sent in /api/detections but NOT plotted          │
  │    on the map. Consider adding as cyan diamond.        │
  └─────────────────────────────────────────────────────┘
```

**FOV Rectangle Math:**
```
  ground_width  = altitude * SENSOR_WIDTH_MM / FOCAL_LENGTH_MM
  ground_height = ground_width * IMAGE_H / IMAGE_W

  4 corners rotated by yaw around drone position:
    Forward-Left, Forward-Right, Back-Right, Back-Left
    Each rotated: [north, east] = R(yaw) * [forward, right]
    Converted to GPS: lat += north/111320, lon += east/(111320*cos(lat))
```

**Update rates:**
- **Drone FOV + dot + arrow**: **5Hz** (200ms) via lightweight `/api/drone` (~120 bytes)
- **Detection dots + SMART**: 1Hz via `/api/detections` (~4KB)
- **Stats + images**: 0.5Hz (2s) via `/api/status`

**New `/api/drone` endpoint:** Returns only `{lat, lon, alt, yaw}` — 97% smaller than `/api/detections`, enabling smooth 5Hz map updates without bandwidth waste.

### 7f. GPS Estimation Math (`/equation`)
- Static 900x500px diagram, cached after first render
- Shows 4-step pipeline: pixel offset → pinhole model → yaw rotation → GPS coords
- Shows config values (f_px, SENSOR_WIDTH, IMAGE dimensions)
- **Missing:** FOV angle visualization, altitude sensitivity table, pixel-per-metre scale

### 7g. Error Convergence Chart — NOT YET IMPLEMENTED
- Intended: 600x400px line graph, error vs detection count
- Only useful in --fake mode (known ground truth)
- Endpoint `/convergence` referenced in spec but not coded

---

## 8. HTTP Endpoints (15 total)

| Path | Type | Cache | Source Variable | Not Ready |
|------|------|-------|-----------------|-----------|
| `/` | text/html | — | HTML_PAGE | N/A |
| `/stream` | multipart MJPEG | — | `latest_jpeg` | Skips frame |
| `/snapshot` | image/jpeg | — | `latest_det_jpeg` or `latest_jpeg` | 503 |
| `/latest` | image/jpeg | no-cache | `latest_detection_jpeg` | 503 |
| `/best` | image/jpeg | no-cache | `latest_best_jpeg` | 503 |
| `/smart-grid` | image/jpeg | no-cache | `latest_smart_grid_jpeg` | 503 |
| `/map` | image/jpeg | no-cache | `latest_map_jpeg` | 503 |
| `/bullseye` | image/jpeg | no-cache | `latest_bullseye` | 503 |
| `/equation` | image/jpeg | 24hr cache | `_equation_jpeg` | 503 |
| `/toggle-bullseye-bg` | text/plain | — | `_bullseye_map_bg` | Toggle |
| `/toggle-map-bg` | text/plain | — | `_map_show_bg` | Toggle |
| `/clear` | text/plain | — | Resets all state | Returns "CLEARED" |
| `/api/status` | JSON | — | `stats` dict | N/A |
| `/api/drone` | JSON | no-cache | `gps_data` (lat,lon,alt,yaw) | N/A |
| `/api/detections` | JSON | no-cache | `_all_gps_estimates` + estimators | N/A |
| `/assets/map.jpg` | image/jpeg | 24hr cache | File from disk | 404 |

### `/api/status` JSON:
```json
{
  "cam_fps", "vis_fps", "stream_fps",
  "detections", "det_pct", "saved",
  "gps_lat", "gps_lon", "alt", "sats", "flight_mode",
  "est_lat", "est_lon", "est_obs",
  "fov_deg", "cal_1m_w", "cal_1m_h"
}
```

### `/api/detections` JSON:
```json
{
  "detections": [{"lat", "lon", "pixel_dist", "alt", "ground_dist_m"}, ...],
  "smart": {"locked", "spread", "median_lat", "median_lon", "samples": [...]},
  "estimate": {"lat", "lon", "obs"},
  "drone_lat", "drone_lon",
  "config": {"f_px", "image_w", "image_h"}
}
```

### Polling intervals:
- `/api/status` → every 2s (updates stats + refreshes latest/best/smart-grid images)
- `/api/detections` → every 1s (updates Plotly bullseye + Leaflet map)
- `/stream` → continuous MJPEG

---

## 9. Stream Overlay (`draw_overlay`)

Applied to every frame before MJPEG encoding.

### Always visible:

| Element | Color (BGR) | Position | Data |
|---------|-------------|----------|------|
| Center crosshair | Cyan (255,255,0) | Frame centre ±30px | Static reference |
| FPS bar | Black bg, cyan text | Top-left strip | `CAM:X VIS:X STR:X` |
| Attitude | Gray (180,180,180) | Top-right | `Y:X P:X R:X` |
| Flight mode | Light gray (200,200,200) | Top-right | e.g. `GUIDED` |
| Compass rose | Gray circle + green arrow | Top-right corner | Yaw heading arrow |
| "FRONT" label | Gray (100,100,100) | Top-centre | Camera orientation |
| FOV bar | Black bg, amber text | Bottom strip -50px | `FOV:Xdeg | Ground:WxHm @Xm` |
| Width/height | Amber (0,140,180) | Bottom + left edge | `<-- X.Xm -->` and `X.Xm` |
| DUMMY EST bar | Black bg, magenta text | Bottom strip -75px | `DUMMY EST: lat, lon (N obs)` |
| GPS bar | Black bg, orange text | Bottom strip -25px | `GPS: lat, lon | Alt: Xm | Sats: N` |

### When detection active (fades over 2 seconds):

| Element | Color (BGR) | Details |
|---------|-------------|---------|
| Bounding box | Green (0,int(255*alpha),0) | alpha = max(0.3, 1.0 - age/2.0) |
| Box label | Same green | `AI {conf:.2f} [{class}]` |
| Magenta line | Magenta (255,0,255) | Centre → detection, 3px |
| Detection dot | Magenta (255,0,255) | 12px circle, white outline |
| Distance label | Magenta (255,0,255) | `{px}px ({m:.1f}m)` at midpoint |

---

## 10. Data Flow

```
  Camera Frame
    │
    ├─► detect_in_image(frame) → (found, cx, cy, conf)
    │     cx, cy = pixel coords in 1456x1088 frame
    │
    ├─► [read gps_data] → d_lat, d_lon, d_alt, d_yaw
    │     ⚠ NO LOCK — potential race with mavlink thread
    │
    ├─► Normalise: norm_x = cx/1456, norm_y = cy/1088
    │
    ├─► DummyEstimator.add_observation(lat, lon, alt, yaw, norm_x, norm_y)
    │     → pixel offset → pinhole model → yaw rotate → GPS offset
    │     → weighted accumulation → (est_lat, est_lon)
    │
    ├─► _all_gps_estimates.append((est_lat, est_lon, pixel_dist, alt))
    │
    ├─► SmartEstimator.add(est_lat, est_lon, pixel_dist, frame, alt)
    │     → greedy tightest-10 clustering → lock when spread < 0.5m
    │
    ├─► draw_overlay(frame) → latest_jpeg (stream)
    │
    ├─► render_latest_detection() → latest_detection_jpeg
    │
    ├─► if more_central: _best_detection → latest_best_jpeg
    │
    └─► Every ~2s:
         ├─► render_bullseye(all_estimates, smart) → latest_bullseye
         ├─► render_map(all_estimates, smart) → latest_map_jpeg
         └─► render_smart_grid(smart) → latest_smart_grid_jpeg
```

---

## 11. Detection Coordinate Chain

Full chain from camera pixel to browser display:

```
  vision.py detect_in_image(frame)
    │
    ├─ Resize frame to 640x640 (YOLO input)
    ├─ Run TFLite inference
    ├─ Raw output: either pixel coords [0-640] or normalised [0-1]
    ├─ Heuristic: if raw_cx > 1.5 → pixel coords, else normalised
    ├─ Scale back to original frame:
    │    if pixel: cx = raw_cx * 1456/640, cy = raw_cy * 1088/640
    │    if norm:  cx = raw_cx * 1456,     cy = raw_cy * 1088
    │
    └─► Returns (found, cx, cy, conf)
         cx, cy = INTEGER pixel coords in 1456x1088 space

  passive_watch.py main loop
    │
    ├─ pixel_dist = sqrt((cx - 728)^2 + (cy - 544)^2)
    │    max possible: 911.2 px (corner detection)
    │
    ├─ norm_x = cx / 1456,  norm_y = cy / 1088
    │
    └─► DummyEstimator.add_observation(lat, lon, alt, yaw, norm_x, norm_y)

  /api/detections endpoint
    │
    ├─ ground_dist_m = pixel_dist * alt / f_px
    │    = pixel_dist * alt / 1577.25
    │
    └─► Browser JS: Plotly scatter, Leaflet markers, heat coloring
```

---

## 12. CLI Flags

| Flag | Default | Purpose |
|------|---------|---------|
| `--port` | 8090 | HTTP server port |
| `--conf` | 0.4 | Detection confidence threshold |
| `--fps` | 5 | Max inference FPS (throttle) |
| `--save-dir` | `detections/` | Snapshot output directory |
| `--no-save` | off | Disable snapshot saving |
| `--no-mavlink` | off | Skip mavproxy connection |
| `--model` | `best.tflite` | TFLite model path |
| `--simple-names` | off | Clean filenames, no JSON sidecars |
| `--class-filter` | none | Only save matching class (e.g. `person`) |
| `--smart-estimate` | off | Enable smart clustering |
| `--smart-min` | 10 | Min detections before clustering |
| `--smart-radius` | 0.5 | Max spread (m) for cluster lock |
| `--fake` | off | Replay DJI video + SRT telemetry |
| `--fake-video` | `RealVideo/DJI_0001_...30fps.mp4` | Video file for replay |
| `--fake-srt` | `RealVideo/DJI_2026...V.SRT` | SRT telemetry file |

---

## 13. Key Classes

### DummyEstimator
- Accumulates weighted GPS observations
- Weight = `(1/alt^2) * centre_factor`
- Centre factor: 5x for detections at image centre, 1x at edges
- `get_estimate()` returns weighted mean (lat, lon, count)

### SmartEstimator
- Greedy minimax clustering: finds tightest 10 observations
- Locks when spread < `max_spread` (0.5m)
- After lock: rejects new observations, `ready()` returns True
- `get_median()` returns per-dimension median (not geometric median)
- `get_cep50()` returns median radial error from median centre

### RollingFPS
- 3-second rolling window
- Three instances: cam, vis, stream

---

## 14. Known Issues & Bugs

| Issue | Severity | Location | Description |
|-------|----------|----------|-------------|
| GPS race condition | HIGH | main loop + mavlink_reader | No lock on gps_data dict, fields updated individually by background thread |
| Panel 1/3 redundant | MEDIUM | updateBullseye() JS | Same data, same colors, same center — Panel 3 only adds estimate diamond |
| Smart grid != locked cluster | MEDIUM | render_smart_grid() | Shows first 10 FIFO frames, not the 10 that form the locked cluster |
| Missing Plotly Panel 4 | LOW | updateBullseye() JS | OpenCV has ground_dist_m panel, Plotly doesn't |
| Frame memory growth | LOW | SmartEstimator.add() | Stores full frame.copy() per detection, unbounded before lock |

---

## 15. What's Missing vs video_test_compare.py

| Feature | video_test_compare | Browser Dashboard | Priority |
|---------|-------------------|-------------------|----------|
| Centrality filter | Built-in panel | JS slider (works) | DONE |
| Model switching | M key, 4 models | Dropdown + `/api/switch-model` | DONE |
| Confidence threshold | Hardcoded | Slider (0.05-0.95) | DONE |
| Class filter | Hardcoded | Dropdown (all/dummy/person) | DONE |
| Error convergence chart | Full line graph | Not implemented | Medium |
| Altitude-colored scatter | Panel 5 | Missing | Medium |
| 4m central bullseye | Panel 4 (first 10 within 4m) | Missing | Low |
| Confidence weighting | In scatter | Not in estimation | Medium |
| CSV error logging | Full per-detection CSV | Detection photos only | Low |
| Ground truth markers | Yellow cross at TRUE_DUMMY | N/A (no ground truth in real) | Low |

---

## 16. External Libraries (CDN)

| Library | Version | CDN URL | Purpose |
|---------|---------|---------|---------|
| Leaflet CSS | 1.9.4 | `unpkg.com/leaflet@1.9.4/dist/leaflet.css` | Map styling |
| Leaflet JS | 1.9.4 | `unpkg.com/leaflet@1.9.4/dist/leaflet.js` | Interactive maps |
| Plotly JS | 2.35.2 | `cdn.plot.ly/plotly-2.35.2.min.js` | Charts/bullseye |

**Offline note:** Leaflet tiles need internet (CartoDB/OSM). The satellite overlay (`/assets/map.jpg`) works offline. Plotly JS must be cached or bundled for offline use.

---

## 17. Quality Standards

- **Canvas sizes**: 600px per panel minimum
- **JPEG quality**: 95 for rendered panels, 85 for stream
- **Font rendering**: cv2.LINE_AA on all text, FONT_HERSHEY_SIMPLEX
- **Heat coloring**: `heatColor(val)` — 0.0=green, 0.5=yellow, 1.0=red
- **Ring colors**: (50,50,50) on black bg, (120,120,120) on map bg
- **Marker sizes**: minimum 5px dots, 12px for special markers

---

## 18. Consolidated Improvement List

All suggestions and fixes for the browser dashboard, ranked by priority.

### HIGH — Fix before next use

| # | Issue | Details |
|---|-------|---------|
| 1 | **GPS race condition** | Add `threading.Lock` around `gps_data` reads/writes. Snapshot gps_data atomically at frame capture time. |
| 2 | **Panel 1/3 redundancy** | Panel 3 must center on weighted estimate (not mean) and color by ground_dist_m (not pixel_dist). See Section 6. |
| 3 | **Smart grid shows wrong frames** | `render_smart_grid()` shows first 10 FIFO frames. Should show the 10 frames that form the locked cluster. |
| 4 | **Add estimate marker to map** | DummyEstimator weighted estimate is in `/api/detections` but not plotted on Leaflet map. Add cyan diamond marker. |

### MEDIUM — Improve quality

| # | Issue | Details |
|---|-------|---------|
| 5 | **Faster drone marker** | Reduce `/api/detections` poll from 1000ms to 333ms (3Hz). GPS arrives faster than we poll. |
| 6 | **Add Plotly Panel 4** | Static bullseye has ground_dist_m panel — add to Plotly as 4th subplot. |
| 7 | **Equation diagram: add FOV** | Show FOV cone angle, altitude sensitivity table, pixel-per-metre scale. |
| 8 | **Error convergence chart** | `/convergence` endpoint — line graph of error vs detection count. Only useful in --fake mode. |
| 9 | **Altitude-colored scatter** | 5th panel from video_test_compare — missing entirely. |
| 10 | **Confidence weighting** | Add confidence to weight formula in DummyEstimator (currently only altitude + centrality). |

### LOW — Nice to have

| # | Issue | Details |
|---|-------|---------|
| 11 | **Frame memory growth** | SmartEstimator stores full frame.copy() per detection. Cap at N frames or clear after lock. |
| 12 | ~~**Model switching**~~ | ~~M key in video_test_compare — not applicable to live stream but could add dropdown.~~ **DONE** — dropdown + `/api/switch-model` + confidence slider + class filter. |
| 13 | **CSV error logging** | Full per-detection CSV with GPS error (needs ground truth). |
| 14 | **4m central bullseye** | Panel showing only first 10 detections within 4m — from video_test_compare. |
| 15 | **Offline Plotly** | Bundle plotly.min.js locally for Pi hotspot use without internet. |
