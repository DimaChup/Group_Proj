"""
Lawnmower Pattern Visualizer — draw a polygon, see the search pattern at different altitudes.

Usage:
    python tools/lawnmower_visual.py
    python tools/lawnmower_visual.py --altitude 30
    python tools/lawnmower_visual.py --compare   (shows 4 altitudes side by side)

Controls:
    LEFT-CLICK  = add polygon vertex
    RIGHT-CLICK = close polygon and generate pattern
    R           = reset polygon
    1/2/3/4     = switch altitude (15m / 20m / 30m / 50m)
    C           = compare mode (4 altitudes side by side)
    Q           = quit
"""
import cv2
import numpy as np
import math
import argparse


# Pi camera specs (calibrated)
HFOV_DEG = 49.4       # from 92cm at 1m measurement
ASPECT = 4 / 3        # camera aspect ratio
OVERLAP = 0.20        # 20% overlap between lanes


def ground_footprint(altitude, hfov_deg=HFOV_DEG, aspect=ASPECT):
    """Calculate ground coverage at given altitude. Returns (width_m, height_m)."""
    hfov_rad = math.radians(hfov_deg)
    w = 2 * altitude * math.tan(hfov_rad / 2)
    h = w / aspect
    return w, h


def generate_lawnmower(polygon_pts, altitude, canvas_size, scale):
    """Generate lawnmower waypoints for a polygon at given altitude.

    Args:
        polygon_pts: list of (x, y) pixel coords on canvas
        altitude: flight altitude in meters
        canvas_size: (w, h) of canvas
        scale: pixels per meter

    Returns:
        waypoints: list of (x, y) pixel coords
        strips: list of ((x1,y1), (x2,y2)) scan lines
        lane_width_m: lane spacing in meters
        footprint: (w_m, h_m) ground footprint
    """
    if len(polygon_pts) < 3:
        return [], [], 0, (0, 0)

    w_m, h_m = ground_footprint(altitude)
    lane_spacing_m = w_m * (1 - OVERLAP)
    lane_spacing_px = int(lane_spacing_m * scale)
    if lane_spacing_px < 2:
        lane_spacing_px = 2

    # Create mask from polygon
    cw, ch = canvas_size
    mask = np.zeros((ch, cw), dtype=np.uint8)
    poly = np.array([polygon_pts], dtype=np.int32)
    cv2.fillPoly(mask, poly, 255)

    # Find optimal scan angle (aligned to longest edge)
    rect = cv2.minAreaRect(poly[0])
    (center, size, angle) = rect
    scan_angle = angle + 90 if size[0] < size[1] else angle

    # Rotate mask
    M = cv2.getRotationMatrix2D(center, scan_angle, 1.0)
    M_inv = cv2.invertAffineTransform(M)
    rotated = cv2.warpAffine(mask, M, (cw, ch))

    # Find scan lines
    points = cv2.findNonZero(rotated)
    if points is None:
        return [], [], lane_spacing_m, (w_m, h_m)
    x, y, w, h = cv2.boundingRect(points)

    strips = []
    for scan_y in range(y + lane_spacing_px // 2, y + h, lane_spacing_px):
        if scan_y >= ch:
            break
        row = rotated[scan_y, :]
        pixels = np.where(row == 255)[0]
        if len(pixels) > 0:
            x_start = pixels[0]
            x_end = pixels[-1]
            strips.append(((x_start, scan_y), (x_end, scan_y)))

    # Convert back to original coords and build zigzag
    waypoints = []
    direction = 1
    original_strips = []
    for s in strips:
        pts_rot = np.array([[s[0], s[1]]], dtype=np.float32)
        pts_orig = cv2.transform(pts_rot, M_inv)[0]
        p1 = (int(pts_orig[0][0]), int(pts_orig[0][1]))
        p2 = (int(pts_orig[1][0]), int(pts_orig[1][1]))
        if direction == 1:
            original_strips.append((p1, p2))
            waypoints.append(p1)
            waypoints.append(p2)
        else:
            original_strips.append((p2, p1))
            waypoints.append(p2)
            waypoints.append(p1)
        direction *= -1

    return waypoints, original_strips, lane_spacing_m, (w_m, h_m)


def draw_pattern(canvas, polygon_pts, altitude, scale, label=""):
    """Draw the polygon, lawnmower pattern, and annotations on canvas."""
    h_canvas, w_canvas = canvas.shape[:2]

    # Draw polygon fill (translucent)
    if len(polygon_pts) >= 3:
        overlay = canvas.copy()
        poly = np.array([polygon_pts], dtype=np.int32)
        cv2.fillPoly(overlay, poly, (40, 60, 40))
        cv2.addWeighted(overlay, 0.5, canvas, 0.5, 0, canvas)
        cv2.polylines(canvas, poly, True, (0, 200, 0), 2)

    waypoints, strips, lane_m, (fw, fh) = generate_lawnmower(
        polygon_pts, altitude, (w_canvas, h_canvas), scale)

    if not waypoints:
        return canvas

    # Draw scan lanes as filled rectangles (showing camera footprint width)
    footprint_px = int(fw * scale)
    for (p1, p2) in strips:
        # Draw thin lane fill
        half = footprint_px // 2
        mid_y = (p1[1] + p2[1]) // 2
        # Create rotated rectangle along the strip
        dx = p2[0] - p1[0]
        dy = p2[1] - p1[1]
        length = math.sqrt(dx**2 + dy**2)
        if length < 1:
            continue
        angle = math.degrees(math.atan2(dy, dx))
        center = ((p1[0]+p2[0])//2, (p1[1]+p2[1])//2)
        rect_pts = cv2.boxPoints(((center[0], center[1]), (length, footprint_px), angle))
        rect_pts = np.int32(rect_pts)
        overlay2 = canvas.copy()
        cv2.fillPoly(overlay2, [rect_pts], (30, 50, 30))
        cv2.addWeighted(overlay2, 0.3, canvas, 0.7, 0, canvas)

    # Draw zigzag path
    for i in range(len(waypoints) - 1):
        p1 = waypoints[i]
        p2 = waypoints[i + 1]
        # Alternate colors for scan vs turn
        if i % 2 == 0:
            color = (0, 255, 255)  # cyan = scan line
            thick = 2
        else:
            color = (100, 100, 255)  # red-ish = turn
            thick = 1
        cv2.line(canvas, p1, p2, color, thick)

    # Draw waypoints
    for i, wp in enumerate(waypoints):
        cv2.circle(canvas, wp, 3, (255, 255, 255), -1)

    # Start/end markers
    if waypoints:
        cv2.circle(canvas, waypoints[0], 8, (0, 255, 0), 2)
        cv2.putText(canvas, "START", (waypoints[0][0]+10, waypoints[0][1]),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        cv2.circle(canvas, waypoints[-1], 8, (0, 0, 255), 2)
        cv2.putText(canvas, "END", (waypoints[-1][0]+10, waypoints[-1][1]),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)

    # Stats
    n_lanes = len(strips)
    total_dist = sum(math.sqrt((waypoints[i+1][0]-waypoints[i][0])**2 +
                               (waypoints[i+1][1]-waypoints[i][1])**2) / scale
                     for i in range(len(waypoints)-1))

    # Info panel
    info_lines = [
        f"{label}Altitude: {altitude}m" if label else f"Altitude: {altitude}m",
        f"FOV: {HFOV_DEG:.1f} deg, Footprint: {fw:.1f}m x {fh:.1f}m",
        f"Lane spacing: {lane_m:.1f}m ({OVERLAP*100:.0f}% overlap)",
        f"Lanes: {n_lanes}, Waypoints: {len(waypoints)}",
        f"Total path: {total_dist:.0f}m",
    ]
    y0 = 15
    cv2.rectangle(canvas, (0, 0), (350, y0 + 18 * len(info_lines)), (0, 0, 0), -1)
    for i, line in enumerate(info_lines):
        cv2.putText(canvas, line, (8, y0 + i * 18),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.42, (200, 200, 200), 1)

    # Scale bar (bottom-right)
    scale_m = 10 if total_dist > 100 else 5
    scale_px = int(scale_m * scale)
    sx = w_canvas - scale_px - 20
    sy = h_canvas - 25
    cv2.line(canvas, (sx, sy), (sx + scale_px, sy), (255, 255, 255), 2)
    cv2.line(canvas, (sx, sy-5), (sx, sy+5), (255, 255, 255), 2)
    cv2.line(canvas, (sx+scale_px, sy-5), (sx+scale_px, sy+5), (255, 255, 255), 2)
    cv2.putText(canvas, f"{scale_m}m", (sx + scale_px//2 - 10, sy - 10),
               cv2.FONT_HERSHEY_SIMPLEX, 0.4, (255, 255, 255), 1)

    return canvas


def compare_altitudes(polygon_pts, scale):
    """Show 4 altitudes side by side in a 2x2 grid."""
    altitudes = [15, 20, 30, 50]
    tile_w, tile_h = 500, 500
    grid = np.zeros((tile_h * 2, tile_w * 2, 3), dtype=np.uint8)

    # Scale polygon to fit tiles
    for idx, alt in enumerate(altitudes):
        tile = np.zeros((tile_h, tile_w, 3), dtype=np.uint8)
        tile[:] = (20, 20, 20)
        # Scale polygon to tile
        scaled_pts = [(int(x * tile_w / 800), int(y * tile_h / 800)) for x, y in polygon_pts]
        tile_scale = scale * tile_w / 800
        draw_pattern(tile, scaled_pts, alt, tile_scale, label=f"[{alt}m] ")
        r, c = idx // 2, idx % 2
        grid[r*tile_h:(r+1)*tile_h, c*tile_w:(c+1)*tile_w] = tile

    # Grid lines
    cv2.line(grid, (tile_w, 0), (tile_w, tile_h*2), (60, 60, 60), 2)
    cv2.line(grid, (0, tile_h), (tile_w*2, tile_h), (60, 60, 60), 2)

    return grid


def main():
    parser = argparse.ArgumentParser(description="Lawnmower pattern visualizer")
    parser.add_argument("--altitude", type=int, default=20, help="Flight altitude (default 20m)")
    parser.add_argument("--compare", action="store_true", help="Show 4 altitudes side by side")
    parser.add_argument("--scale", type=float, default=5.0, help="Pixels per meter (default 5.0)")
    parser.add_argument("--map", default="assets/map.jpg", help="Background map image (default map.jpg)")
    parser.add_argument("--map-scale", type=float, default=0, help="Map pixels per meter (auto-detect from config if 0)")
    args = parser.parse_args()

    # Try to load map as background
    bg_img = None
    import os
    map_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", args.map)
    if os.path.exists(map_path):
        bg_img = cv2.imread(map_path)
        if bg_img is not None:
            print(f"Loaded map: {map_path} ({bg_img.shape[1]}x{bg_img.shape[0]})")
    if bg_img is None and os.path.exists(args.map):
        bg_img = cv2.imread(args.map)
        if bg_img is not None:
            print(f"Loaded map: {args.map} ({bg_img.shape[1]}x{bg_img.shape[0]})")

    if bg_img is not None:
        # Use map dimensions, scale down for display
        max_disp = 900
        mh, mw = bg_img.shape[:2]
        disp_scale = min(max_disp / mw, max_disp / mh, 1.0)
        canvas_w = int(mw * disp_scale)
        canvas_h = int(mh * disp_scale)
        bg_img = cv2.resize(bg_img, (canvas_w, canvas_h))
        # Try to get map scale from config (pix_per_m)
        if args.map_scale > 0:
            scale = args.map_scale * disp_scale
        else:
            try:
                import sys
                sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))
                from utils import GeoTransformer
                import config
                geo = GeoTransformer()
                scale = geo.pix_per_m * disp_scale
                print(f"Map scale from config: {geo.pix_per_m:.1f} px/m (display: {scale:.1f} px/m)")
            except Exception as e:
                scale = args.scale
                print(f"Could not auto-detect map scale ({e}), using {scale} px/m")
    else:
        canvas_w, canvas_h = 800, 800
        scale = args.scale  # px per meter
        print(f"No map found, using blank canvas")
    altitude = args.altitude
    polygon_pts = []
    closed = False

    win = "Lawnmower Pattern — LEFT-CLICK=add vertex, RIGHT-CLICK=close, R=reset, C=compare, Q=quit"
    cv2.namedWindow(win, cv2.WINDOW_AUTOSIZE)

    def on_mouse(event, mx, my, flags, param):
        nonlocal closed
        if event == cv2.EVENT_LBUTTONDOWN and not closed:
            polygon_pts.append((mx, my))
        elif event == cv2.EVENT_RBUTTONDOWN and len(polygon_pts) >= 3:
            closed = True

    cv2.setMouseCallback(win, on_mouse)

    print(f"Canvas: {canvas_w}x{canvas_h} ({canvas_w/scale:.0f}m x {canvas_h/scale:.0f}m)")
    print(f"Scale: {scale} px/m")
    print(f"Camera HFOV: {HFOV_DEG:.1f} deg, Aspect: {ASPECT:.2f}")
    print(f"Overlap: {OVERLAP*100:.0f}%")
    print(f"\nDraw a polygon (left-click vertices, right-click to close)")

    while True:
        if bg_img is not None:
            canvas = bg_img.copy()
        else:
            canvas = np.zeros((canvas_h, canvas_w, 3), dtype=np.uint8)
            canvas[:] = (20, 20, 20)

        # Draw grid
        grid_m = 10
        grid_px = int(grid_m * scale)
        for x in range(0, canvas_w, grid_px):
            cv2.line(canvas, (x, 0), (x, canvas_h), (30, 30, 30), 1)
        for y in range(0, canvas_h, grid_px):
            cv2.line(canvas, (0, y), (canvas_w, y), (30, 30, 30), 1)

        if closed and len(polygon_pts) >= 3:
            draw_pattern(canvas, polygon_pts, altitude, scale)
        else:
            # Draw polygon in progress
            for i, pt in enumerate(polygon_pts):
                cv2.circle(canvas, pt, 5, (0, 200, 0), -1)
                if i > 0:
                    cv2.line(canvas, polygon_pts[i-1], pt, (0, 150, 0), 2)
            if polygon_pts:
                cv2.putText(canvas, f"Vertices: {len(polygon_pts)} | Right-click to close",
                           (10, canvas_h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (150, 150, 150), 1)

        # Bottom HUD
        cv2.rectangle(canvas, (0, canvas_h - 35), (canvas_w, canvas_h), (0, 0, 0), -1)
        hud = f"Alt: {altitude}m | 1=15m 2=20m 3=30m 4=50m | C=compare | R=reset | Q=quit"
        cv2.putText(canvas, hud, (10, canvas_h - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.38, (150, 150, 150), 1)

        cv2.imshow(win, canvas)
        key = cv2.waitKey(30) & 0xFF

        if key == ord('q'):
            break
        elif key == ord('r'):
            polygon_pts.clear()
            closed = False
        elif key == ord('1'):
            altitude = 15
        elif key == ord('2'):
            altitude = 20
        elif key == ord('3'):
            altitude = 30
        elif key == ord('4'):
            altitude = 50
        elif key == ord('c') and closed and len(polygon_pts) >= 3:
            grid = compare_altitudes(polygon_pts, scale)
            cv2.imshow("Altitude Comparison (15m / 20m / 30m / 50m)", grid)

    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
