# Cinematic Mission Animation -- Storyboard

> Each scene is a separate manim `Scene` class. Final video is stitched by rendering
> each scene then concatenating with ffmpeg. Total target: ~38 seconds.

---

## Data Constants (shared module: `mission_data.py`)

All scenes import coordinates and parameters from one shared file so values stay
consistent and match the real codebase (`config.py`, `transit.json`, `planning.py`).

```python
# --- GPS coordinates (lat, lon) from config.py ---
TAKEOFF_GPS = (51.42340640, -2.67144603)

SEARCH_AREA_GPS = [
    (51.42326957, -2.67094835),
    (51.42287025, -2.67004543),
    (51.42336623, -2.66816930),
    (51.42421477, -2.66880977),
    (51.42354070, -2.67127778),
]

FLIGHT_AREA_GPS = [
    (51.42342595, -2.67172077),
    (51.42124623, -2.67013403),
    (51.42244012, -2.66568782),
    (51.42469179, -2.66706023),
]

SSSI_GPS = [
    (51.42353587, -2.67145175),
    (51.42215640, -2.66976824),
    (51.42267105, -2.66770544),
    (51.42335592, -2.66816460),
    (51.42286083, -2.67004342),
    (51.42326667, -2.67096542),
    (51.42356862, -2.67132430),
]

FOCUS_AREA_GPS = [
    (51.42330494, -2.66982370),
    (51.42344371, -2.66949620),
    (51.42352782, -2.66980025),
    (51.42334973, -2.67001828),
]

TRANSIT_WAYPOINTS = [
    (51.42176480, -2.67011737, "T1"),
    (51.42247427, -2.66713882, "T2"),
    (51.42410412, -2.66830869, "T3"),
]

# --- Flight parameters from config.py ---
TARGET_ALT        = 35.0    # m  (search altitude)
VERIFY_ALT        = 15.0    # m
TRANSIT_SPEED_MPS = 15.0    # m/s
SEARCH_SPEED_MPS  = 8.0     # m/s (speed_for_altitude at 35 m)
FOCUS_SPEED_MPS   = 5.0     # m/s
HOVER_ALT         = 3.0     # m  (payload release)

# Servo timing (state_machine.py _handle_hover_target)
SERVO_PARTIAL_SEC = 3.0     # seconds into hover -> stage 1 partial release
SERVO_FULL_SEC    = 6.0     # seconds into hover -> stage 2 full release
HOVER_TOTAL_SEC   = 15.0    # total hover time before climb

# NFZ buffer
NFZ_WAYPOINT_BUFFER_M = 30.0
NFZ_HARD_BOUNDARY_M   = 3.0

# Camera footprint at search alt (from planning.py line 76)
SENSOR_WIDTH_MM   = 5.02
FOCAL_LENGTH_MM   = 5.46
IMAGE_W           = 1456
IMAGE_H           = 1088
GROUND_FOOTPRINT_W_M = (SENSOR_WIDTH_MM * TARGET_ALT) / FOCAL_LENGTH_MM  # ~32.1 m
GROUND_FOOTPRINT_H_M = GROUND_FOOTPRINT_W_M * (IMAGE_H / IMAGE_W)       # ~24.0 m

# Landing offset
LANDING_OFFSET_M = 7.5
```

### Coordinate System

All GPS coordinates must be projected to a local **metres-from-origin** frame for
manim. Use TAKEOFF_GPS as origin `(0, 0)`. Conversion:

```python
def gps_to_local(lat, lon):
    """(lat, lon) -> (x_east, y_north) in metres, origin at TAKEOFF_GPS."""
    dy = (lat - TAKEOFF_GPS[0]) * 111132.0
    dx = (lon - TAKEOFF_GPS[1]) * 111132.0 * cos(radians(TAKEOFF_GPS[0]))
    return (dx, dy)
```

Then scale the local-metres frame to fit a manim camera. Suggested: **1 manim unit =
25 metres** so the ~350 m wide field fits within [-7, 7] horizontally.

```python
SCALE = 1.0 / 25.0   # multiply metres by this to get manim units
```

### Colour Palette (consistent across all scenes)

| Element | Colour | Hex |
|---------|--------|-----|
| Flight Area boundary | WHITE, dashed | #FFFFFF |
| Search Area polygon | BLUE_C fill 0.15 | #58C4DD |
| SSSI / NFZ | RED_C fill 0.25, red dashed border | #FC6255 |
| Focus Area (PLB) | ORANGE fill 0.2 | #FF8C00 |
| TOL marker | GREEN dot + label | #83C167 |
| Transit path | YELLOW dashed line | #FFFF00 |
| Drone icon | WHITE triangle, small | #FFFFFF |
| Camera footprint | TEAL_C rectangle, stroke only | #5CD0B3 |
| Coverage strips | GREEN_C fill 0.3 | #83C167 |
| Detection bbox | RED rectangle, stroke 3 | #FC6255 |
| GPS estimate dots | YELLOW_C small dots | #FFFF00 |
| Return path | GREY dashed line | #888888 |
| Payload drop line | ORANGE dashed vertical | #FF8C00 |

---

## Scene 1: Overview (`SceneOverview`) -- 5 seconds

### Purpose
Establish the operational area. Show all zones so the viewer understands the spatial
layout before any movement begins.

### State machine states active
None (pre-mission context).

### Camera
- Static bird's-eye. Frame width ~400 m to fit the entire Flight Area with padding.
- Camera centre: centroid of Flight Area.

### Timing breakdown
| Time | Action |
|------|--------|
| 0.0-0.5 s | Title "SAR Drone Mission" fades in at top, subtitle "Autonomous Search and Rescue" below |
| 0.5-1.5 s | Flight Area boundary draws on (white dashed Polygon) |
| 1.5-2.5 s | SSSI/NFZ polygon fills in (red, semi-transparent) with label "SSSI No-Fly Zone" |
| 2.5-3.5 s | Search Area polygon fills in (blue, semi-transparent) with label "Search Area" |
| 3.5-4.0 s | TOL dot + label "Take-Off / Landing" appears (green Dot at TAKEOFF_GPS) |
| 4.0-5.0 s | All labels settle; hold for readability |

### Manim objects
```
title         = Text("SAR Drone Mission", font_size=42, weight=BOLD)
subtitle      = Text("Autonomous Search and Rescue", font_size=24, color=GREY_B)
flight_poly   = DashedVMobject(Polygon(*flight_area_pts, color=WHITE), dashed_ratio=0.6)
sssi_poly     = Polygon(*sssi_pts, fill_color=RED_C, fill_opacity=0.25, stroke_color=RED)
search_poly   = Polygon(*search_pts, fill_color=BLUE_C, fill_opacity=0.15, stroke_color=BLUE)
tol_dot       = Dot(tol_pt, radius=0.08, color=GREEN)
tol_label     = Text("TOL", font_size=16, color=GREEN).next_to(tol_dot, DOWN, 0.1)
sssi_label    = Text("SSSI No-Fly Zone", font_size=14, color=RED).move_to(sssi_centroid)
search_label  = Text("Search Area", font_size=14, color=BLUE).move_to(search_centroid)
```

### Data needed from config.py
- `FLIGHT_AREA_GPS` (4 corners)
- `SSSI_GPS` (7 corners)
- `SEARCH_AREA_GPS` (5 corners)
- `TAKEOFF_GPS`

---

## Scene 2: Transit (`SceneTransit`) -- 5 seconds

### Purpose
Show takeoff and the transit path from TOL around the NFZ to the search area entry
point. Emphasise that the drone goes AROUND the NFZ, not through it.

### State machine states active
`INIT -> CONNECTING -> ARMING -> TAKEOFF -> PRE_WAYPOINTS`

The state machine does:
1. Arm + takeoff to TARGET_ALT (35 m)
2. Fly pre-waypoints (transit.json): TOL -> T1 -> T2 -> T3
3. Then TRANSIT_TO_SEARCH: T3 -> first search waypoint

### Camera
- Start zoomed on TOL. Smoothly pull out to show full field by t=2 s.
- Camera tracks the drone along the transit path.

### Timing breakdown
| Time | Action |
|------|--------|
| 0.0-0.5 s | Drone icon appears at TOL. State label: "ARMING". Altitude gauge: 0 m |
| 0.5-1.5 s | Drone climbs. Altitude gauge animates 0 -> 35 m. State: "TAKEOFF". Small vertical arrow shows climb. Camera zooms out. |
| 1.5-2.0 s | State: "PRE_WAYPOINTS". Speed label "15 m/s" appears. Drone starts moving toward T1 |
| 2.0-2.5 s | Drone reaches T1 (dot + "T1" label appears). Yellow dashed line traces behind drone. |
| 2.5-3.5 s | Drone flies T1 -> T2. T2 label appears. Path clearly goes south of NFZ. |
| 3.5-4.5 s | Drone flies T2 -> T3. T3 label appears. Path curves around east side of NFZ. |
| 4.5-5.0 s | State: "TRANSIT_TO_SEARCH". Drone heads toward search polygon entry. |

### Manim objects
```
# Background: all zone polygons from Scene 1 (dimmed, fill_opacity 0.08)
drone         = Triangle(fill_color=WHITE, fill_opacity=1).scale(0.12)
                # Oriented in direction of travel via .rotate()
altitude_bar  = Rectangle(width=0.15, height=0, fill_color=TEAL, fill_opacity=0.8)
                # Grows from 0 to full height (represents 35 m)
alt_label     = Text("0 m", font_size=14).next_to(altitude_bar, RIGHT)
                # Updates: "0 m" -> "35 m"
state_badge   = RoundedRectangle(corner_radius=0.05, width=2.2, height=0.35,
                    fill_color=DARK_GREY, fill_opacity=0.8)
                # Contains state text, top-right corner
transit_path  = VMobject(color=YELLOW, stroke_width=2)
                # Built incrementally as drone moves (TracedPath or manual append)
speed_label   = Text("15 m/s", font_size=14, color=YELLOW)
wp_dots       = [Dot(t1_pt), Dot(t2_pt), Dot(t3_pt)]  # appear on arrival
wp_labels     = [Text("T1"), Text("T2"), Text("T3")]
```

### Data needed
- `TAKEOFF_GPS` -> origin
- `TRANSIT_WAYPOINTS` (T1, T2, T3) from transit.json
- `TARGET_ALT = 35.0`
- `TRANSIT_SPEED_MPS = 15.0`
- First search waypoint (compute from lawnmower pattern start corner)

### Key visual: NFZ avoidance
The transit path goes TOL (northwest) -> T1 (south) -> T2 (east) -> T3 (northeast),
clearly routing AROUND the SSSI polygon. Draw a brief red glow on the NFZ boundary
as the drone passes closest to it (~t=3 s).

---

## Scene 3: Search Pattern (`SceneSearch`) -- 8 seconds

### Purpose
Show the lawnmower boustrophedon pattern. Camera footprint sweeps the search area.
Coverage fills in behind.  Drone does NOT enter NFZ buffer.

### State machine states active
`SEARCH` (with `_advance_waypoint` cycling through waypoint list)

The planner generates parallel strips aligned to the polygon's longest edge
(~70 deg from north based on the search polygon shape). Strips spaced by
camera ground footprint * 0.8 (20% overlap). Drone zigzags: left-to-right on
even strips, right-to-left on odd strips.

### Camera
- Bird's-eye covering the full search area. Slight zoom in compared to Scene 1
  (search polygon fills ~80% of frame).
- Static camera -- the pattern itself is the movement.

### Timing breakdown
| Time | Action |
|------|--------|
| 0.0-0.5 s | Drone enters search polygon from T3 side. State: "SEARCH". Speed: "8 m/s" |
| 0.5-1.0 s | Camera footprint rectangle appears around drone (TEAL outline, ~32x24 m at scale). First coverage strip begins filling green behind. |
| 1.0-6.5 s | Drone flies lawnmower pattern. ~8-10 strips visible. Each strip: drone moves along, green fill trails behind (0.3 opacity). At each turn, drone rotates 180 deg. Coverage counter in corner: "12%" -> "24%" -> ... -> "68%". The pattern is at ~70 deg angle to horizontal. |
| 5.0 s | Drone approaches NFZ buffer zone. A faint pink "buffer" line (30 m inside NFZ, from NFZ_WAYPOINT_BUFFER_M) is visible. The lawnmower strip ENDS before crossing it. Drone turns back. Brief label: "NFZ Buffer 30m" |
| 6.5-7.0 s | Slow the animation. Coverage: "74%". Drone is mid-strip. |
| 7.0-8.0 s | Coverage continues. End on ~"82%". Hold for transition. |

### Manim objects
```
# Background zones (same as Scene 1, dimmed)
search_poly   = Polygon(*search_pts, fill_color=BLUE_C, fill_opacity=0.1, stroke_color=BLUE)
sssi_poly     = Polygon(*sssi_pts, fill_color=RED_C, fill_opacity=0.2, stroke_color=RED)
nfz_buffer    = DashedVMobject(Polygon(*nfz_buffer_pts, color=PINK), dashed_ratio=0.5)
                # 30 m inset from SSSI polygon (approximate visually)

drone         = Triangle(fill_color=WHITE, fill_opacity=1).scale(0.10)
cam_footprint = Rectangle(width=fw, height=fh, stroke_color=TEAL, stroke_width=1.5,
                    fill_opacity=0)
                # fw, fh = GROUND_FOOTPRINT_W_M * SCALE, GROUND_FOOTPRINT_H_M * SCALE
                # Moves with drone, rotated to match scan angle

coverage_strips = VGroup()
                # Each strip: a thin filled rectangle (green, 0.3 opacity)
                # Added one at a time as drone completes each pass

coverage_counter = Text("Coverage: 0%", font_size=18, color=GREEN)
                   # Top-left corner, updated per strip

speed_label   = Text("8 m/s", font_size=14, color=YELLOW)
state_badge   = # same as Scene 2 but "SEARCH"

# Lawnmower waypoints: precomputed list of (x, y) in manim coords
# ~15-20 waypoints forming the zigzag. Drone animates along this path.
search_path = VMobject()  # thin white line showing upcoming pattern (faint)
```

### Data needed
- `SEARCH_AREA_GPS` (5 corners) -> local coords
- `SSSI_GPS` -> local coords + 30 m buffer inset
- `TARGET_ALT = 35.0`
- `GROUND_FOOTPRINT_W_M` (~32 m), `GROUND_FOOTPRINT_H_M` (~24 m)
- Search speed: `speed_for_altitude(35) = 8.0` m/s (linear interp: 35 m is between 20 and 50)
- Scan angle: ~70 deg (longest edge of the search polygon; compute from `cv2.minAreaRect`)
- Strip spacing: `GROUND_FOOTPRINT_W_M * 0.8 = ~25.7 m`

### How to compute the lawnmower pattern for animation
Replicate the planner logic:
1. Project search polygon corners to local metres.
2. Find the minimum-area bounding rectangle (longest edge angle ~ 70 deg).
3. Rotate polygon so longest edge is horizontal.
4. Generate horizontal scan lines spaced by `strip_spacing` (25.7 m).
5. For each scan line, clip to polygon boundary -> get (x_start, x_end).
6. Zigzag: even lines left-to-right, odd lines right-to-left.
7. Connect endpoints with turn segments.
8. Rotate all points back by -70 deg.
9. Convert to manim coordinates.

---

## Scene 4: PLB Beacon + Focus Area (`SceneBeacon`) -- 4 seconds

### Purpose
PLB (Personal Locator Beacon) activates mid-search. The drone abandons the
broad search and redirects to a smaller Focus Area polygon for tighter scanning.

### State machine states active
`SEARCH` -> `_trigger_beacon_redirect()` is called ->
pattern regenerates inside FOCUS_AREA_GPS at FOCUS_SEARCH_SPEED_MPS (5 m/s).

What actually happens in code (`_trigger_beacon_redirect`, line 753):
- Loads `flight_plans/focus_area.json` (or falls back to `config.FOCUS_AREA_GPS`)
- Replaces the planner's search polygon with the focus area polygon
- Regenerates the lawnmower pattern (tighter, slower)
- Sets `_beacon_triggered = True`
- Speed drops to `min(FOCUS_SEARCH_SPEED_MPS, speed_for_altitude(alt))` = 5 m/s

### Camera
- Start at Scene 3's view (full search area).
- At t=1.5 s, camera zooms in smoothly to frame the Focus Area at ~80% of view.

### Timing breakdown
| Time | Action |
|------|--------|
| 0.0-0.5 s | Flash: "PLB SIGNAL RECEIVED" in bold orange text, centre screen. Pulsing radio wave circles emanate from focus area centroid (2-3 expanding rings). |
| 0.5-1.5 s | Focus Area polygon draws on (orange fill, 0.2 opacity, orange stroke). Label: "Focus Area". Old coverage strips fade to 0.1 opacity. |
| 1.5-2.5 s | Camera zooms in on Focus Area. New tighter lawnmower pattern draws as faint lines inside Focus Area. Speed label changes: "8 m/s" -> "5 m/s". Drone redirects toward Focus Area entry. |
| 2.5-4.0 s | Drone flies 2-3 strips of the tighter pattern inside Focus Area. Coverage strips (green) fill behind. Pattern is visibly tighter/closer spaced than Scene 3. |

### Manim objects
```
# Background: all zones from previous scenes
plb_flash     = Text("PLB SIGNAL RECEIVED", font_size=36, color=ORANGE, weight=BOLD)
                # FadeIn + FadeOut over 1 s
radio_rings   = [Circle(radius=r, stroke_color=ORANGE, stroke_opacity=0.6)
                 for r in [0.3, 0.6, 0.9]]
                # Animate: GrowFromCenter + FadeOut, staggered by 0.2 s
focus_poly    = Polygon(*focus_pts, fill_color=ORANGE, fill_opacity=0.2,
                    stroke_color=ORANGE, stroke_width=2)
focus_label   = Text("Focus Area", font_size=14, color=ORANGE)
speed_label   = Text("5 m/s", font_size=14, color=YELLOW)  # replaces "8 m/s"
focus_pattern = VMobject(color=WHITE, stroke_opacity=0.3)
                # Thin lines showing the tighter lawnmower inside focus area
```

### Data needed
- `FOCUS_AREA_GPS` (4 corners) -> local coords
- `FOCUS_SEARCH_SPEED_MPS = 5.0`
- Tighter strip spacing (same formula but focus polygon is ~50x30 m, so maybe 3-4 strips)

---

## Scene 5: Detection (`SceneDetection`) -- 3 seconds

### Purpose
The AI detects the casualty. GPS estimation dots cluster. Operator confirms.

### State machine states active
`SEARCH` -> detection triggers -> `CENTERING` -> `VERIFY` -> operator presses Y

What happens in code:
1. `_process_detection()` in SEARCH: CV returns (found=True, px_u, px_v, conf).
   GPS position estimated via `calculate_target_gps(px_u, px_v)`.
2. Detection queued, `_pop_valid_target()` returns it.
3. State -> `CENTERING`: drone flies to estimated GPS, refines position.
   Within 1.0 m -> state -> `VERIFY`.
4. `VERIFY`: 120 s timeout. Operator sees stream. Presses Y.
5. Y -> `selecting_landing_side = True` -> operator picks N/E/S/W -> `APPROACH`.

### Camera
- Zoomed in on the focus area (continuing from Scene 4).
- Slight zoom in further when detection happens.

### Timing breakdown
| Time | Action |
|------|--------|
| 0.0-0.5 s | Drone is mid-strip. Suddenly a RED FLASH pulse on the scan line where the dummy is. A small person icon / silhouette appears on the ground. |
| 0.5-1.2 s | Bounding box (red rectangle) snaps around the dummy. Confidence label: "0.94" next to box. State badge: "CENTERING". Yellow GPS estimation dots appear (3-5 scattered within ~2 m of true position). |
| 1.2-2.0 s | Drone moves toward the cluster of GPS dots (centering). Dots converge. State: "VERIFY". A countdown "120s" appears faintly. The camera footprint is now centred on the dummy. |
| 2.0-2.5 s | Operator prompt: "Confirm Target? Y / N / I" text appears. Brief pause. |
| 2.5-3.0 s | Green "Y" key press animation. Text: "TARGET CONFIRMED". State: "APPROACH". Direction arrow shows the chosen landing side (e.g., South). |

### Manim objects
```
dummy_icon    = SVGMobject("person.svg") or Circle(radius=0.04, color=RED)
                # Small marker at dummy GPS position
red_flash     = Rectangle(width=scan_strip_width, height=0.02, fill_color=RED,
                    fill_opacity=0.6)
                # Brief flash along the scan line, FadeIn + FadeOut
bbox          = Rectangle(width=0.12, height=0.16, stroke_color=RED, stroke_width=3)
                # Around dummy
conf_label    = Text("0.94", font_size=14, color=RED).next_to(bbox, UR, 0.05)
gps_dots      = VGroup(*[Dot(pt, radius=0.02, color=YELLOW) for pt in gps_estimates])
                # 4-5 dots scattered near dummy, then converge
verify_prompt = Text("Confirm? Y / N / I", font_size=18, color=WHITE)
y_confirm     = Text("Y", font_size=28, color=GREEN, weight=BOLD)
                # Scale pulse animation
confirmed_txt = Text("TARGET CONFIRMED", font_size=20, color=GREEN)
```

### Data needed
- Dummy position: place within FOCUS_AREA_GPS (e.g., centroid of focus area)
- Confidence: 0.94 (representative)
- GPS scatter: 4-5 points within 2 m radius of true dummy position
- Landing direction: South (arbitrary, for illustration)

---

## Scene 6: Descent + Payload (`SceneDescent`) -- 5 seconds

### Purpose
Switch to a SIDE VIEW (quasi-3D profile) to show the descent from 35 m to 3 m and
the dual-stage payload release. This is the most visually dramatic scene.

### State machine states active
`APPROACH` -> `HOVER_TARGET`

What happens in code:
1. `APPROACH`: drone flies to `landing_lat, landing_lon` at 3.0 m altitude.
   `landing_offset_7_5m()` placed the landing spot 7.5 m from target in chosen direction.
2. When within 2.0 m horizontal and alt < 4.0 m -> `HOVER_TARGET`.
3. `HOVER_TARGET` (15 s total):
   - t=0-3 s: hold position at 3 m
   - t=3 s: SERVO STAGE 1 -- partial release (PWM 1300)
   - t=6 s: SERVO STAGE 2 -- full release (PWM 1100)
   - t=15 s: servo closed (PWM 1500), climb back to search alt

### Camera
- **Side view / profile view**: X-axis = horizontal distance, Y-axis = altitude.
- Ground line at bottom. Sky gradient at top.
- Frame: ~50 m wide, 0-40 m tall.

### Timing breakdown
| Time | Action |
|------|--------|
| 0.0-0.5 s | Transition: bird's-eye fades, side-view fades in. Ground line (brown/green). Dummy icon on ground at centre. Drone at 35 m directly above, offset 7.5 m to the right. Horizontal dashed line shows the 7.5 m offset. Altitude scale on left: 0, 10, 20, 30, 35 m. |
| 0.5-1.5 s | State: "APPROACH". Drone descends diagonally: 35 m altitude, 7.5 m offset -> 3 m altitude, 0 m offset (above landing spot). Smooth bezier curve. Altitude label tracks: "35 m" -> "15 m" -> "5 m" -> "3 m". A "7.5 m offset" dimension line + label between dummy and landing spot on ground. |
| 1.5-2.0 s | State: "HOVER_TARGET". Drone holds at 3 m. Timer appears: "0 / 15 s". |
| 2.0-2.5 s | Timer: "3 s". SERVO STAGE 1: orange flash on drone. Text: "Partial Release". Payload (small orange circle) detaches slightly but held by second latch. Dashed line from drone to partially-lowered payload. |
| 2.5-3.5 s | Timer: "6 s". SERVO STAGE 2: second orange flash. Text: "Full Release". Payload drops: animated fall from 3 m to ground (0.3 s). Small bounce/impact puff on landing. "PAYLOAD DEPLOYED" text in green. |
| 3.5-4.0 s | Timer fast-forwards to "15 s". Drone begins climbing. Altitude: 3 m -> 35 m. |
| 4.0-5.0 s | Drone at 35 m. State: "RETURN_TRANSIT". Side view holds briefly before transition. |

### Manim objects
```
# Side-view specific:
ground_line   = Line(LEFT*6, RIGHT*6, color="#5a3d2b", stroke_width=4)
                # or a thin green/brown rectangle for grass
sky_gradient  = Rectangle(width=12, height=8, fill_color=["#1a1a2e", "#16213e"],
                    fill_opacity=0.3)
alt_axis      = NumberLine(x_range=[0, 40, 10], length=6, rotation=90*DEGREES,
                    include_numbers=True, font_size=12, label_direction=LEFT)
                # Vertical axis on left side

drone_side    = VGroup(
    Rectangle(width=0.4, height=0.08, fill_color=WHITE, fill_opacity=0.9),
    # Two "rotor" lines
    Line(LEFT*0.25, LEFT*0.25+UP*0.06), Line(RIGHT*0.25, RIGHT*0.25+UP*0.06),
)
dummy_side    = VGroup(
    Circle(radius=0.05, fill_color=RED, fill_opacity=0.8),  # head
    Line(ORIGIN, DOWN*0.12, color=RED),  # body
)
                # On ground line at centre

offset_dim    = DashedLine(dummy_pos, landing_pos, color=GREY)
offset_label  = Text("7.5 m", font_size=12, color=GREY)

payload       = Circle(radius=0.04, fill_color=ORANGE, fill_opacity=1)
                # Initially attached to drone, then drops
drop_path     = Line(drone_hover_pos, ground_pos, color=ORANGE, stroke_opacity=0.3)
                # Dashed vertical showing drop trajectory

stage1_txt    = Text("Partial Release", font_size=14, color=ORANGE)
stage2_txt    = Text("Full Release", font_size=14, color=ORANGE)
deployed_txt  = Text("PAYLOAD DEPLOYED", font_size=20, color=GREEN, weight=BOLD)

hover_timer   = Text("0 / 15 s", font_size=14, color=WHITE)
                # Top-right, updates
```

### Data needed
- `HOVER_ALT = 3.0` m
- `TARGET_ALT = 35.0` m
- `LANDING_OFFSET_M = 7.5` m
- Servo timings: 3 s (partial), 6 s (full), 15 s (total hover)
- `SERVO_PARTIAL_PWM = 1300`, `SERVO_FULL_PWM = 1100` (for labels if desired)

---

## Scene 7: Return Home (`SceneReturn`) -- 5 seconds

### Purpose
Back to bird's-eye. Drone climbs to 35 m and flies the SAME transit path in REVERSE
(T3 -> T2 -> T1 -> TOL). Emphasise it does NOT cut across the NFZ.

### State machine states active
`HOVER_TARGET` (climb) -> `RETURN_TRANSIT` -> `RETURN_HOME` -> `LANDING`

What happens in code:
1. After hover complete, `RETURN_TRANSIT`: climb to search alt, then fly
   `pre_waypoints` in reverse order (index decrements: T3 -> T2 -> T1).
2. When all return transit WPs done -> `RETURN_HOME`: fly to `home_lat, home_lon`
   at `TARGET_ALT`.
3. Within 2.0 m of home -> `LANDING` -> `DONE`.

### Camera
- Transition from side view back to bird's-eye (same framing as Scene 2).
- Camera follows drone along return path.

### Timing breakdown
| Time | Action |
|------|--------|
| 0.0-0.5 s | Transition to bird's-eye. Drone at dummy location, climbing. State: "RETURN_TRANSIT". Altitude label: "3 m -> 35 m" (quick climb animation). |
| 0.5-1.0 s | Drone at 35 m. Begins flying toward T3. Grey dashed line traces behind drone (return path). Speed: "15 m/s". |
| 1.0-2.0 s | Drone reaches T3 (grey dot pulse). Continues to T2. Return path clearly goes around east side of NFZ. NFZ gets a brief red glow. |
| 2.0-3.0 s | T2 reached. Drone continues to T1. Path goes south of NFZ. |
| 3.0-4.0 s | T1 reached. State: "RETURN_HOME". Drone heads northwest toward TOL. |
| 4.0-4.5 s | Drone arrives at TOL. State: "LANDING". Altitude: "35 m -> 0 m" (quick descent animation). |
| 4.5-5.0 s | Drone on ground at TOL. State: "DONE". Green pulse on TOL marker. |

### Manim objects
```
# Background: all zone polygons (same as Scene 1)
# Outbound transit path from Scene 2 still visible (yellow dashed, dimmed)
return_path   = VMobject(color=GREY, stroke_width=2, stroke_opacity=0.7)
                # Built incrementally as drone moves (dashed)
drone         = Triangle(...)  # same as Scene 2
state_badge   = ...  # updates: RETURN_TRANSIT -> RETURN_HOME -> LANDING -> DONE
speed_label   = Text("15 m/s", font_size=14, color=GREY)
alt_label     = ...  # brief climb/descent animations

# Reuse transit waypoint markers from Scene 2 (T1, T2, T3) -- grey this time
```

### Data needed
- Same transit waypoints in reverse: T3, T2, T1, TOL
- `TRANSIT_SPEED_MPS = 15.0`
- `TARGET_ALT = 35.0`

---

## Scene 8: Mission Complete (`SceneComplete`) -- 3 seconds

### Purpose
Summary stats. Clean ending.

### State machine states active
`DONE`

### Camera
- Static. Centre frame.

### Timing breakdown
| Time | Action |
|------|--------|
| 0.0-0.5 s | Background dims. All zone polygons still faintly visible. |
| 0.5-1.5 s | Stats appear one by one (staggered FadeIn, 0.25 s each):  - "Coverage: 96%"  - "Flight Time: 8 min 32 s"  - "Detections: 1 confirmed"  - "Payload: Deployed"  |
| 1.5-2.0 s | Large green checkmark (SVG or constructed from lines) draws on at centre. |
| 2.0-2.5 s | "MISSION COMPLETE" text fades in below checkmark, bold, green. |
| 2.5-3.0 s | Everything holds, then gentle fade to black. |

### Manim objects
```
stats = VGroup(
    Text("Coverage: 96%", font_size=22),
    Text("Flight Time: 8 min 32 s", font_size=22),
    Text("Detections: 1 confirmed", font_size=22),
    Text("Payload: Deployed", font_size=22),
).arrange(DOWN, buff=0.3).move_to(UP*0.5)

checkmark     = VMobject(color=GREEN, stroke_width=6)
                # Two line segments forming a tick: short down-right + long up-right
                # Or use Create animation on a pre-built path
complete_txt  = Text("MISSION COMPLETE", font_size=36, color=GREEN, weight=BOLD)
                .next_to(checkmark, DOWN, 0.3)
```

### Data needed
- Representative stats (not from config -- these are illustrative):
  - Coverage: 96% (typical for our polygon)
  - Flight time: ~8 min 32 s (rough estimate: 30 s takeoff + 60 s transit +
    300 s search + 30 s detection + 60 s descent/hover + 60 s return + 12 s landing)
  - Detections: 1 confirmed
  - Payload: Deployed

---

## Implementation Notes

### File structure
```
report/manim/
  CINEMATIC_STORYBOARD.md    <- THIS FILE
  mission_data.py            <- Shared constants (GPS coords, config values, gps_to_local())
  scene_01_overview.py       <- SceneOverview
  scene_02_transit.py        <- SceneTransit
  scene_03_search.py         <- SceneSearch
  scene_04_beacon.py         <- SceneBeacon
  scene_05_detection.py      <- SceneDetection
  scene_06_descent.py        <- SceneDescent
  scene_07_return.py         <- SceneReturn
  scene_08_complete.py       <- SceneComplete
  render_all.sh              <- Renders each scene + stitches with ffmpeg
```

### Rendering command (per scene)
```bash
manim -qh --fps 30 scene_01_overview.py SceneOverview
```

### Stitching command
```bash
ffmpeg -f concat -safe 0 -i filelist.txt -c copy cinematic_mission.mp4
```
where `filelist.txt` lists the 8 scene videos in order.

### Transition strategy
Each scene begins with a 0.3 s fade-from-black and ends with a 0.3 s fade-to-black.
This gives clean cuts when concatenated. Alternative: use `self.play(FadeOut(*self.mobjects))`
at scene end.

### Drone movement animation
Use `MoveAlongPath` or manual `animate.move_to()` with rate functions. For the
lawnmower pattern, pre-build a `VMobject` path and use `MoveAlongPath(drone, path,
run_time=X)`. Rotate the drone triangle to face the direction of travel using
`drone.animate.rotate(angle)` at each turn.

### State badge
A persistent HUD element in the top-right corner showing the current state machine
state. Use `Transform(state_text, new_state_text)` for transitions. Brief white
flash on state change.

### Altitude gauge (Scenes 2, 6, 7)
A vertical bar on the right side of frame. Height proportional to altitude.
`altitude_bar.animate.stretch_to_fit_height(new_h)` with numeric label.

### Coverage counter (Scene 3)
`DecimalNumber` mobject that increments. Or `Text` that gets replaced with
`Transform` at each strip completion.

### GPS estimation dots (Scene 5)
Create 4-5 `Dot` objects at slightly scattered positions (use numpy random with
seed for reproducibility). Animate them converging to the true position during
CENTERING.
