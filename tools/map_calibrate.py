#!/usr/bin/env python3
"""
Map GPS Calibration Tool
========================
Click landmarks on map.jpg, provide their real GPS coordinates.
Computes optimal REF_LAT, REF_LON, MAP_WIDTH_METERS for config.py.

Usage:
    python tools/map_calibrate.py

Instructions:
    1. Click a landmark on the map (crossroads, building corner, etc.)
    2. Enter its real GPS coordinates (from Google Maps / Apple Maps)
    3. Repeat for 2-4 landmarks (more = better)
    4. Press ENTER with no input to calculate
    5. Tool prints new config values + error analysis

Current config:
    REF_LAT = 51.425106  (top-left corner)
    REF_LON = -2.672257  (top-left corner)
    MAP_WIDTH_METERS = 480.0
"""

import sys, os, math, threading, queue
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np
import config

# ── State ──
clicked_points = []     # [(px_x, px_y)]
gps_points = []         # [(lat, lon)]
current_click = None
map_img = None
display_scale = 1.0

# ── Zoom/Pan state ──
zoom_level = 1.0        # 1.0 = fit-to-window, higher = zoomed in
pan_x = 0.0             # center of view in full-res pixel coords
pan_y = 0.0
DISP_W = 1400
DISP_H = 1000
dragging = False
drag_start = None       # (mouse_x, mouse_y) at drag start
pan_start = None        # (pan_x, pan_y) at drag start
needs_redraw = True

# ── Threaded input state ──
input_queue = queue.Queue()
input_requested = threading.Event()
waiting_for_input = False   # True while GPS prompt is active in terminal


def screen_to_full(sx, sy):
    """Convert screen pixel to full-res map pixel."""
    # Visible region in full-res coords
    vis_w = map_img.shape[1] / zoom_level
    vis_h = map_img.shape[0] / zoom_level
    left = pan_x - vis_w / 2
    top = pan_y - vis_h / 2
    fx = left + sx * vis_w / DISP_W
    fy = top + sy * vis_h / DISP_H
    return fx, fy


def on_mouse(event, x, y, flags, param):
    global current_click, zoom_level, pan_x, pan_y, dragging, drag_start, pan_start, needs_redraw

    if event == cv2.EVENT_MOUSEWHEEL:
        # Zoom toward mouse position
        old_fx, old_fy = screen_to_full(x, y)
        if flags > 0:
            zoom_level = min(zoom_level * 1.3, 30.0)
        else:
            zoom_level = max(zoom_level / 1.3, 1.0)
        # After zoom, adjust pan so the point under the mouse stays put
        new_fx, new_fy = screen_to_full(x, y)
        pan_x += old_fx - new_fx
        pan_y += old_fy - new_fy
        _clamp_pan()
        needs_redraw = True

    elif event == cv2.EVENT_RBUTTONDOWN:
        dragging = True
        drag_start = (x, y)
        pan_start = (pan_x, pan_y)

    elif event == cv2.EVENT_MOUSEMOVE and dragging:
        vis_w = map_img.shape[1] / zoom_level
        vis_h = map_img.shape[0] / zoom_level
        dx = (x - drag_start[0]) * vis_w / DISP_W
        dy = (y - drag_start[1]) * vis_h / DISP_H
        pan_x = pan_start[0] - dx
        pan_y = pan_start[1] - dy
        _clamp_pan()
        needs_redraw = True

    elif event == cv2.EVENT_RBUTTONUP:
        dragging = False

    elif event == cv2.EVENT_LBUTTONDOWN:
        full_x, full_y = screen_to_full(x, y)
        full_x, full_y = int(full_x), int(full_y)
        if 0 <= full_x < map_img.shape[1] and 0 <= full_y < map_img.shape[0]:
            current_click = (full_x, full_y)
            print(f"\n  Clicked pixel: ({full_x}, {full_y})")
            print(f"  Enter GPS as: lat,lon  (e.g. 51.42345,-2.67123)")
            print(f"  Or press ENTER to skip and calculate with existing points.")
            needs_redraw = True


def _clamp_pan():
    """Keep pan within map bounds."""
    global pan_x, pan_y
    h, w = map_img.shape[:2]
    vis_w = w / zoom_level
    vis_h = h / zoom_level
    pan_x = max(vis_w / 2, min(pan_x, w - vis_w / 2))
    pan_y = max(vis_h / 2, min(pan_y, h - vis_h / 2))


def get_viewport():
    """Get the visible region as a cropped + resized display image."""
    h, w = map_img.shape[:2]
    vis_w = w / zoom_level
    vis_h = h / zoom_level
    left = int(max(0, pan_x - vis_w / 2))
    top = int(max(0, pan_y - vis_h / 2))
    right = int(min(w, left + vis_w))
    bottom = int(min(h, top + vis_h))
    crop = map_img[top:bottom, left:right]
    return cv2.resize(crop, (DISP_W, DISP_H), interpolation=cv2.INTER_AREA), left, top, vis_w, vis_h


def full_to_screen(fx, fy, left, top, vis_w, vis_h):
    """Convert full-res pixel coords to screen coords."""
    sx = int((fx - left) * DISP_W / vis_w)
    sy = int((fy - top) * DISP_H / vis_h)
    return sx, sy


def draw_markers():
    """Draw all calibration points on the viewport."""
    disp, left, top, vis_w, vis_h = get_viewport()

    # Scale marker sizes based on zoom
    marker_size = max(10, int(30 / zoom_level * 2))
    circle_r = max(5, int(15 / zoom_level * 2))
    font_scale = max(0.4, min(1.2, 0.6 * zoom_level / 2 + 0.3))

    for i, ((px, py), (lat, lon)) in enumerate(zip(clicked_points, gps_points)):
        sx, sy = full_to_screen(px, py, left, top, vis_w, vis_h)
        if -50 < sx < DISP_W + 50 and -50 < sy < DISP_H + 50:
            cv2.drawMarker(disp, (sx, sy), (0, 0, 255), cv2.MARKER_CROSS, marker_size, 3)
            cv2.circle(disp, (sx, sy), circle_r, (0, 0, 255), 2, cv2.LINE_AA)
            label = f"P{i+1}: {lat:.6f}, {lon:.6f}"
            cv2.putText(disp, label, (sx + 20, sy - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, (0, 0, 255), 2, cv2.LINE_AA)
            cv2.putText(disp, label, (sx + 20, sy - 10),
                       cv2.FONT_HERSHEY_SIMPLEX, font_scale, (255, 255, 255), 1, cv2.LINE_AA)

    # Current (unconfirmed) click
    if current_click:
        sx, sy = full_to_screen(current_click[0], current_click[1], left, top, vis_w, vis_h)
        if -50 < sx < DISP_W + 50 and -50 < sy < DISP_H + 50:
            cv2.drawMarker(disp, (sx, sy), (0, 255, 255), cv2.MARKER_CROSS, marker_size, 3)
            cv2.putText(disp, "CLICK — enter GPS in terminal", (sx + 20, sy + 5),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 255), 1, cv2.LINE_AA)

    # Info bar
    cv2.rectangle(disp, (0, 0), (DISP_W, 40), (0, 0, 0), -1)
    info = f"MAP CALIBRATION | Points: {len(gps_points)} | Zoom: {zoom_level:.1f}x | Scroll=zoom  RightDrag=pan  LeftClick=mark"
    cv2.putText(disp, info, (10, 28), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1, cv2.LINE_AA)

    # Current config footer
    cv2.rectangle(disp, (0, DISP_H - 30), (DISP_W, DISP_H), (0, 0, 0), -1)
    cfg = f"REF_LAT={config.REF_LAT} REF_LON={config.REF_LON} MAP_W={config.MAP_WIDTH_METERS}m  |  {map_img.shape[1]}x{map_img.shape[0]}px"
    cv2.putText(disp, cfg, (10, DISP_H - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1, cv2.LINE_AA)

    return disp


def calibrate(pixel_points, gps_coords, img_w, img_h):
    """
    Given N pixel-GPS pairs, compute optimal REF_LAT, REF_LON, MAP_WIDTH_METERS.

    Method: least-squares fit.
    Model: px_x = (lon - REF_LON) * 111320 * cos(mean_lat) * (img_w / MAP_WIDTH_METERS)
           px_y = (REF_LAT - lat) * 111320 * (img_w / MAP_WIDTH_METERS)

    Unknowns: REF_LAT, REF_LON, ppm (pixels per meter)
    """
    n = len(pixel_points)
    if n < 2:
        print("  Need at least 2 points!")
        return None

    # Use mean GPS as initial reference
    mean_lat = sum(g[0] for g in gps_coords) / n
    mean_lon = sum(g[1] for g in gps_coords) / n
    cos_lat = math.cos(math.radians(mean_lat))

    if n == 2:
        # Exact solution from 2 points
        (px1, py1), (px2, py2) = pixel_points
        (lat1, lon1), (lat2, lon2) = gps_coords

        # Ground distance between points
        dn_m = (lat1 - lat2) * 111320
        de_m = (lon1 - lon2) * 111320 * cos_lat
        ground_dist = math.sqrt(dn_m**2 + de_m**2)

        # Pixel distance
        pixel_dist = math.sqrt((px1 - px2)**2 + (py1 - py2)**2)

        if ground_dist < 0.1 or pixel_dist < 1:
            print("  Points too close together!")
            return None

        ppm = pixel_dist / ground_dist  # pixels per meter

        # Compute REF_LAT/LON from first point
        # px_x = (lon - REF_LON) * 111320 * cos_lat * ppm
        # px_y = (REF_LAT - lat) * 111320 * ppm
        ref_lon = lon1 - px1 / (111320 * cos_lat * ppm)
        ref_lat = lat1 + py1 / (111320 * ppm)
        map_w = img_w / ppm

    else:
        # Least-squares with N >= 3 points
        # Build system: for each point i:
        #   px_x_i = (lon_i - ref_lon) * 111320 * cos_lat * ppm
        #   px_y_i = (ref_lat - lat_i) * 111320 * ppm
        # Linearise: let a = 111320 * cos_lat * ppm, b = 111320 * ppm
        #   px_x_i = lon_i * a - ref_lon * a
        #   px_y_i = ref_lat * b - lat_i * b

        # Solve for ppm from all pairwise distances
        ppms = []
        for i in range(n):
            for j in range(i + 1, n):
                dn = (gps_coords[i][0] - gps_coords[j][0]) * 111320
                de = (gps_coords[i][1] - gps_coords[j][1]) * 111320 * cos_lat
                gd = math.sqrt(dn**2 + de**2)
                pd = math.sqrt((pixel_points[i][0] - pixel_points[j][0])**2 +
                               (pixel_points[i][1] - pixel_points[j][1])**2)
                if gd > 0.1 and pd > 1:
                    ppms.append(pd / gd)

        if not ppms:
            print("  All points too close!")
            return None

        ppm = sum(ppms) / len(ppms)
        map_w = img_w / ppm

        # Compute REF_LAT/LON as mean of estimates from each point
        ref_lats = []
        ref_lons = []
        for (px, py), (lat, lon) in zip(pixel_points, gps_coords):
            rl = lat + py / (111320 * ppm)
            ro = lon - px / (111320 * cos_lat * ppm)
            ref_lats.append(rl)
            ref_lons.append(ro)

        ref_lat = sum(ref_lats) / len(ref_lats)
        ref_lon = sum(ref_lons) / len(ref_lons)

    # ── Error analysis ──
    print(f"\n{'='*60}")
    print(f"  CALIBRATION RESULTS ({n} points)")
    print(f"{'='*60}")
    print(f"  REF_LAT         = {ref_lat:.8f}  (was {config.REF_LAT})")
    print(f"  REF_LON         = {ref_lon:.8f}  (was {config.REF_LON})")
    print(f"  MAP_WIDTH_METERS = {map_w:.1f}    (was {config.MAP_WIDTH_METERS})")
    print(f"  Pixels/meter    = {ppm:.2f}      (was {img_w / config.MAP_WIDTH_METERS:.2f})")
    print()

    # Per-point error
    total_err = 0
    for i, ((px, py), (lat, lon)) in enumerate(zip(pixel_points, gps_coords)):
        # Expected pixel from new calibration
        exp_x = (lon - ref_lon) * 111320 * cos_lat * ppm
        exp_y = (ref_lat - lat) * 111320 * ppm
        err_px = math.sqrt((px - exp_x)**2 + (py - exp_y)**2)
        err_m = err_px / ppm
        total_err += err_m
        print(f"  P{i+1}: pixel error = {err_px:.1f}px ({err_m:.2f}m)")

    avg_err = total_err / n
    print(f"\n  Average error: {avg_err:.2f}m")

    # Delta from current
    print(f"\n  Changes:")
    print(f"    REF_LAT:  {ref_lat - config.REF_LAT:+.8f} deg ({(ref_lat - config.REF_LAT) * 111320:+.1f}m)")
    print(f"    REF_LON:  {ref_lon - config.REF_LON:+.8f} deg ({(ref_lon - config.REF_LON) * 111320 * cos_lat:+.1f}m)")
    print(f"    MAP_W:    {map_w - config.MAP_WIDTH_METERS:+.1f}m")

    print(f"\n  To apply, update config.py:")
    print(f"    REF_LAT = {ref_lat:.8f}")
    print(f"    REF_LON = {ref_lon:.8f}")
    print(f"    MAP_WIDTH_METERS = {map_w:.1f}")
    print(f"{'='*60}\n")

    return ref_lat, ref_lon, map_w


def main():
    global map_img, pan_x, pan_y, zoom_level, current_click, needs_redraw, waiting_for_input

    map_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                            config.MAP_FILE)
    map_img = cv2.imread(map_path)
    if map_img is None:
        print(f"ERROR: Cannot load {map_path}")
        sys.exit(1)

    h, w = map_img.shape[:2]
    pan_x = w / 2
    pan_y = h / 2

    print(f"\n  Map: {w}x{h} pixels")
    print(f"  Current calibration:")
    print(f"    REF_LAT = {config.REF_LAT}")
    print(f"    REF_LON = {config.REF_LON}")
    print(f"    MAP_WIDTH_METERS = {config.MAP_WIDTH_METERS}")
    print(f"    Pixels/meter = {w / config.MAP_WIDTH_METERS:.2f}")

    win = "Map GPS Calibration"
    cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)
    cv2.setMouseCallback(win, on_mouse)

    print(f"\n  CONTROLS:")
    print(f"  Scroll wheel   = zoom in/out")
    print(f"  Right-drag      = pan")
    print(f"  Left-click      = mark landmark")
    print(f"  R               = reset zoom")
    print(f"  Q / ESC         = quit")
    print(f"\n  WORKFLOW:")
    print(f"  1. Click a landmark on the map")
    print(f"  2. Enter GPS as lat,lon in THIS terminal (e.g. 51.42345,-2.67123)")
    print(f"  3. Repeat for 2-4 landmarks")
    print(f"  4. Press ENTER with no input to calculate\n")

    # ── Threaded terminal input ──
    def input_thread_fn():
        while True:
            input_requested.wait()
            input_requested.clear()
            try:
                s = input("  GPS> ").strip()
                input_queue.put(s)
            except EOFError:
                input_queue.put(None)
                break

    input_thread = threading.Thread(target=input_thread_fn, daemon=True)
    input_thread.start()

    while True:
        if needs_redraw:
            disp = draw_markers()
            cv2.imshow(win, disp)
            needs_redraw = False

        key = cv2.waitKey(50) & 0xFF

        if key == ord('q') or key == 27:
            break
        elif key == ord('r'):
            zoom_level = 1.0
            pan_x = w / 2
            pan_y = h / 2
            needs_redraw = True

        # Request terminal input when a click is pending and we haven't asked yet
        if current_click is not None and not waiting_for_input:
            waiting_for_input = True
            input_requested.set()

        # Check if the input thread returned a result
        if waiting_for_input and not input_queue.empty():
            gps_str = input_queue.get()

            if gps_str is None:
                # EOFError
                break

            if not gps_str:
                # Empty input — calculate with existing points
                if len(gps_points) >= 2:
                    calibrate(clicked_points, gps_points, w, h)
                else:
                    print(f"  Need at least 2 points (have {len(gps_points)})")
                current_click = None
                waiting_for_input = False
                needs_redraw = True
                continue

            try:
                parts = gps_str.replace(' ', '').split(',')
                lat = float(parts[0])
                lon = float(parts[1])
                clicked_points.append(current_click)
                gps_points.append((lat, lon))
                print(f"  Added P{len(gps_points)}: pixel ({current_click[0]}, {current_click[1]}) -> GPS ({lat:.6f}, {lon:.6f})")
                current_click = None
                waiting_for_input = False
                needs_redraw = True
            except (ValueError, IndexError):
                print("  Invalid format. Use: lat,lon (e.g. 51.42345,-2.67123)")
                # Keep waiting_for_input True, re-request input for same click
                input_requested.set()

    cv2.destroyAllWindows()

    if len(gps_points) >= 2:
        print("\n  Final calibration:")
        calibrate(clicked_points, gps_points, w, h)


if __name__ == "__main__":
    main()
