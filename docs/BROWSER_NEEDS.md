# Browser Dashboard — User Needs & Requirements

> Master tracking document. Every need documented here so we don't repeat ourselves.
> Updated each session. Agents check this before making changes.

## Layout Requirements

| Area | Width | Content | Status |
|------|-------|---------|--------|
| Camera Feed | 50% | Live MJPEG stream with full HUD overlay | WORKING |
| Latest Detection | 25% | Snapshot of camera feed at moment of detection | NEEDS FIX — was turned into camera feed clone |
| Best Detection | 25% | Most central detection snapshot (frozen) | NEEDS FIX — same issue |
| Satellite Map | 25% | Interactive canvas map with zoom/pan/drone/footprint | NEEDS RESIZE from 50% to 25% |
| GPS Analysis | 25% | Client-side Canvas scatter charts | IN PLACE |
| CV Pipeline | 50% | Detection pipeline diagram | WORKING |
| GPS Pipeline | 50% | GPS estimation pipeline diagram | WORKING |
| SMART Frames | Below detections | Grid of clustered detection frames | WORKING |

## Camera Feed (MUST NOT BREAK)
- Plays at real-time speed (1 second per second)
- ~30fps from fake video, matches Pi camera rate
- Full HUD: GPS bar, FPS bar, compass, crosshair, pink line, scale bar, detection box, FOV bar, estimate bar
- Stream sleep: 0.033s (30fps cap) — DO NOT reduce further
- This is the PRIMARY display — must never slow down

## Latest Detection Panel
- Should be a SNAPSHOT (frozen frame) from the camera feed at moment of detection
- Same HUD as camera feed (it's a copy of the overlayed display frame)
- Updates when a NEW detection happens
- Should NOT be a live mirror of the camera feed
- 25% page width

## Best Detection Panel  
- Same as Latest Detection but only updates when a MORE CENTRAL detection is found
- Green highlight or label to distinguish from Latest
- Tracks best across entire session

## Model Switching
- 4 models: Original (best.tflite), SAR v2 TFLite, SAR v2 NCNN, COCO Person
- Default launch: COCO Person with conf 0.2
- Must switch smoothly mid-session without freezing stream
- Class filter auto-resets to "all" on switch
- Timeout: 10 seconds for large model loads
- KNOWN ISSUE: switching from COCO to smaller models may timeout on laptop

## Satellite Map
- Interactive Canvas with zoom (scroll), pan (drag)
- Drone position dot updates every 500ms
- Camera footprint rectangle rotates with yaw
- GPS estimate dots (green)
- Smart cluster median star (magenta)
- Search area polygon, flight boundary, SSSI zone overlays
- Scale bar
- Width: 25% of page (NOT 50%)

## GPS Analysis Charts (Client-Side Canvas)
- Single scatter plot with toggleable coloring (Altitude/Centrality/Confidence)
- Map background toggle
- Error convergence line chart
- Smart cluster mini-chart
- Zoom/pan, click dots for details
- Polls /api/estimates-full every 1s
- Width: 25% of page

## Detection Overlay (on camera feed)
- Pink line from center to detection: BIGGER labels, black background for contrast
- Pixel distance (magenta) + real meters (cyan)
- Detection box: green with black outline text for readability on grass
- Crosshair: cyan with black outline, visible on any background
- Scale bar: white, bottom-right
- All on-video text: outline technique (black first, color on top)

## Performance Rules (DO NOT VIOLATE)
- Stream sleep: 0.033s — never go below
- Image polling: 2s for status, no faster for images
- render_latest_detection on detection events only (not every frame)
- JPEG quality: 80 for thumbnails, 70 for stream
- Dashboard overhead: <5% of detection pipeline CPU
- Site is READ-ONLY display — must not slow down detection

## What Works (DO NOT BREAK)
- Camera feed at real-time speed
- Model selector with 4 models
- Confidence slider
- Class filter dropdown
- Interactive map with zoom/pan/drone/footprint
- GPS charts (client-side Canvas)
- CV pipeline visual
- GPS pipeline visual with calibration table
- Map calibration tool (tools/map_calibrate.py)
- Pink line + distance labels on stream
- Crosshair on stream
- Scale bar on stream
- Clear All button (resets everything)
- Reset Best button (clears best detection only)
- Coverage trace on satellite map
- Map background ON by default (bullseye + GPS charts)
- Model switch with XNNPACK deadlock fix

## Recently Added Features
- GPS chart filter sliders (centrality/altitude/confidence min/max ranges)
- SRT pitch/roll extraction for camera feed display
- Bird class in filter dropdown (COCO classifies dummy as bird)
- Camera coverage trace on interactive map (green trail showing scanned area)
