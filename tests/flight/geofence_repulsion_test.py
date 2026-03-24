#!/usr/bin/env python3
"""
Geofence Repulsion Test — Visualize potential field repulsion on the map.

Shows:
- SSSI no-fly zone (red polygon)
- Flight area boundary (green polygon)
- Search waypoints (cyan dots)
- Repulsion field as arrows (yellow/red vectors)
- Click anywhere to see repulsion vector at that point

Usage:
    source test_env/Scripts/activate
    python tests/flight/geofence_repulsion_test.py

Controls:
    Left-click = show repulsion vector at that point
    Right-click = simulate drone flying from click point toward SSSI
    R = reset
    Q = quit
"""
import sys
import os

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)
os.chdir(project_root)

import cv2
import numpy as np
import math
import config

if hasattr(config, 'load_kml_zones'):
    config.load_kml_zones()

from utils import GeoTransformer
from geofence import NFZGeofence
from planning import PathPlanner


def draw_arrow(img, start, end, color, thickness=2, tip_length=0.3):
    """Draw arrow from start to end pixel coords."""
    cv2.arrowedLine(img, tuple(start), tuple(end), color, thickness, tipLength=tip_length)


def main():
    # Load map
    map_path = "assets/map.jpg"
    if not os.path.exists(map_path):
        map_path = "map.jpg"
    base_img = cv2.imread(map_path)
    if base_img is None:
        print("[!] map.jpg not found")
        return

    h, w = base_img.shape[:2]
    geo = GeoTransformer(w)
    fence = NFZGeofence(geo)

    print("=" * 60)
    print("  GEOFENCE REPULSION VISUALIZER")
    print("=" * 60)
    print(f"  Map: {w}x{h}")
    print(f"  SSSI: {len(config.SSSI_GPS)} corners")
    print(f"  Flight Area: {len(config.FLIGHT_AREA_GPS)} corners")
    print()
    print("  Left-click  = show repulsion at point")
    print("  Right-click  = simulate flight toward SSSI")
    print("  R = reset, Q = quit")
    print("=" * 60)

    # Generate search waypoints
    search_poly_px = [geo.gps_to_pixels(lat, lon) for lat, lon in config.SEARCH_AREA_GPS]
    planner = PathPlanner(geo, search_poly_px)
    waypoints = planner.generate_search_pattern(w, h, config.TAKEOFF_GPS)
    print(f"  Search waypoints: {len(waypoints)}")

    # Draw base map with zones
    def draw_base():
        img = base_img.copy()

        # Flight area (green)
        if config.FLIGHT_AREA_GPS:
            pts = np.array([geo.gps_to_pixels(lat, lon)
                            for lat, lon in config.FLIGHT_AREA_GPS], dtype=np.int32)
            cv2.polylines(img, [pts], True, (0, 255, 0), 2)

        # Search area (cyan)
        if config.SEARCH_AREA_GPS:
            pts = np.array([geo.gps_to_pixels(lat, lon)
                            for lat, lon in config.SEARCH_AREA_GPS], dtype=np.int32)
            cv2.polylines(img, [pts], True, (255, 255, 0), 2)

        # SSSI (red with translucent fill)
        if config.SSSI_GPS:
            pts = np.array([geo.gps_to_pixels(lat, lon)
                            for lat, lon in config.SSSI_GPS], dtype=np.int32)
            overlay = img.copy()
            cv2.fillPoly(overlay, [pts], (0, 0, 100))
            cv2.addWeighted(overlay, 0.3, img, 0.7, 0, img)
            cv2.polylines(img, [pts], True, (0, 0, 255), 3)
            cx, cy = pts.mean(axis=0).astype(int)
            cv2.putText(img, "SSSI NO-FLY", (cx - 60, cy),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

        # Draw buffer zones (dashed circles approximation)
        if config.SSSI_GPS:
            pts = np.array([geo.gps_to_pixels(lat, lon)
                            for lat, lon in config.SSSI_GPS], dtype=np.int32)
            # 10m buffer (hard boundary - RTL)
            buffer_10 = int(10 * geo.pix_per_m)
            # 25m buffer (soft boundary - speed reduction starts)
            buffer_25 = int(25 * geo.pix_per_m)

            # Draw expanded polygons for buffer visualization
            for buf_px, color, label in [(buffer_10, (0, 0, 200), "10m RTL"),
                                          (buffer_25, (0, 200, 200), "25m SLOW")]:
                # Offset polygon outward (approximate with dilated contour)
                mask = np.zeros((h, w), dtype=np.uint8)
                cv2.fillPoly(mask, [pts], 255)
                kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (buf_px * 2, buf_px * 2))
                dilated = cv2.dilate(mask, kernel)
                contours, _ = cv2.findContours(dilated, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
                if contours:
                    cv2.drawContours(img, contours, -1, color, 1)

        # Waypoints (cyan dots + path)
        for i, wp in enumerate(waypoints):
            px = geo.gps_to_pixels(wp[0], wp[1])
            cv2.circle(img, tuple(px), 3, (255, 200, 0), -1)
            if i > 0:
                prev = geo.gps_to_pixels(waypoints[i-1][0], waypoints[i-1][1])
                cv2.line(img, tuple(prev), tuple(px), (255, 200, 0), 1)

        # Home
        if config.TAKEOFF_GPS:
            px = geo.gps_to_pixels(config.TAKEOFF_GPS[0], config.TAKEOFF_GPS[1])
            cv2.circle(img, tuple(px), 8, (255, 255, 255), -1)
            cv2.putText(img, "HOME", (px[0] + 12, px[1] + 5),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

        return img

    # Draw repulsion field as a grid of arrows
    def draw_repulsion_field(img):
        """Draw repulsion vectors on a grid across the map."""
        step = 40  # pixels between sample points
        for y in range(step, h - step, step):
            for x in range(step, w - step, step):
                lat, lon = geo.pixels_to_gps(x, y)
                dist_m, is_inside = fence.distance_to_boundary(lat, lon)

                if dist_m > 30:  # only show within 30m
                    continue

                off_lat, off_lon = fence.repulsive_offset(lat, lon)
                if abs(off_lat) < 1e-8 and abs(off_lon) < 1e-8:
                    continue

                # Convert offset to pixel direction
                end_lat = lat + off_lat * 5  # amplify for visibility
                end_lon = lon + off_lon * 5
                end_px = geo.gps_to_pixels(end_lat, end_lon)

                # Color by distance (red = close, yellow = far)
                if dist_m < 10:
                    color = (0, 0, 255)  # red = danger
                elif dist_m < 15:
                    color = (0, 128, 255)  # orange
                else:
                    color = (0, 255, 255)  # yellow

                draw_arrow(img, (x, y), end_px, color, 2)

        return img

    # Mouse callback
    click_data = {'lat': None, 'lon': None, 'sim_path': None}

    def on_mouse(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            lat, lon = geo.pixels_to_gps(x, y)
            click_data['lat'] = lat
            click_data['lon'] = lon
            click_data['sim_path'] = None

            dist_m, is_inside = fence.distance_to_boundary(lat, lon)
            status, speed_factor = fence.check_position(lat, lon)
            off_lat, off_lon = fence.repulsive_offset(lat, lon)

            print(f"\n  Click: ({lat:.6f}, {lon:.6f})")
            print(f"    Distance to SSSI: {dist_m:.1f}m {'(INSIDE!)' if is_inside else ''}")
            print(f"    Status: {status}, speed factor: {speed_factor:.2f}")
            print(f"    Repulsion offset: ({off_lat:.8f}, {off_lon:.8f})")
            if abs(off_lat) > 1e-8 or abs(off_lon) > 1e-8:
                off_m = math.sqrt((off_lat * 111320)**2 + (off_lon * 111320 * math.cos(math.radians(lat)))**2)
                print(f"    Repulsion magnitude: {off_m:.2f}m")

        elif event == cv2.EVENT_RBUTTONDOWN:
            # Simulate flight from click point toward SSSI
            lat, lon = geo.pixels_to_gps(x, y)
            click_data['sim_path'] = simulate_flight(lat, lon, fence, geo)
            print(f"\n  Simulated flight from ({lat:.6f}, {lon:.6f}) - {len(click_data['sim_path'])} steps")

    def simulate_flight(start_lat, start_lon, fence, geo, steps=100, speed_mps=5.0):
        """Simulate a drone flying toward SSSI with repulsion active."""
        path = [(start_lat, start_lon)]
        lat, lon = start_lat, start_lon
        dt = 0.5  # seconds per step

        # Target: center of SSSI (fly toward it)
        sssi_center_lat = sum(p[0] for p in config.SSSI_GPS) / len(config.SSSI_GPS)
        sssi_center_lon = sum(p[1] for p in config.SSSI_GPS) / len(config.SSSI_GPS)

        for _ in range(steps):
            # Attractive force toward SSSI center
            dlat = sssi_center_lat - lat
            dlon = sssi_center_lon - lon
            dist_to_target = math.sqrt((dlat * 111320)**2 +
                                        (dlon * 111320 * math.cos(math.radians(lat)))**2)
            if dist_to_target < 1:
                break

            # Normalize attractive direction
            att_lat = dlat / dist_to_target * speed_mps * dt / 111320
            att_lon = dlon / dist_to_target * speed_mps * dt / (111320 * math.cos(math.radians(lat)))

            # Repulsive offset
            off_lat, off_lon = fence.repulsive_offset(lat, lon)

            # Speed reduction
            _, speed_factor = fence.check_position(lat, lon)
            status, _ = fence.check_position(lat, lon)

            if status == 'critical':
                # RTL triggered — stop
                path.append((lat, lon))
                break

            # Apply both forces
            new_lat = lat + att_lat * speed_factor + off_lat * 0.3
            new_lon = lon + att_lon * speed_factor + off_lon * 0.3

            lat, lon = new_lat, new_lon
            path.append((lat, lon))

        return path

    # Main display loop
    cv2.namedWindow("Geofence Repulsion", cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    cv2.setMouseCallback("Geofence Repulsion", on_mouse)

    base = draw_base()
    base = draw_repulsion_field(base)

    while True:
        display = base.copy()

        # Draw click point
        if click_data['lat'] is not None:
            px = geo.gps_to_pixels(click_data['lat'], click_data['lon'])
            cv2.circle(display, tuple(px), 8, (255, 0, 255), -1)

            # Draw repulsion vector at click point
            off_lat, off_lon = fence.repulsive_offset(click_data['lat'], click_data['lon'])
            if abs(off_lat) > 1e-8 or abs(off_lon) > 1e-8:
                end_lat = click_data['lat'] + off_lat * 10
                end_lon = click_data['lon'] + off_lon * 10
                end_px = geo.gps_to_pixels(end_lat, end_lon)
                draw_arrow(display, px, end_px, (255, 0, 255), 3)

        # Draw simulated flight path
        if click_data['sim_path']:
            path = click_data['sim_path']
            for i in range(len(path) - 1):
                p1 = geo.gps_to_pixels(path[i][0], path[i][1])
                p2 = geo.gps_to_pixels(path[i+1][0], path[i+1][1])
                # Color gradient: green at start, red near end
                t = i / max(len(path) - 1, 1)
                color = (0, int(255 * (1 - t)), int(255 * t))
                cv2.line(display, tuple(p1), tuple(p2), color, 2)
            # Mark start and end
            start_px = geo.gps_to_pixels(path[0][0], path[0][1])
            end_px = geo.gps_to_pixels(path[-1][0], path[-1][1])
            cv2.circle(display, tuple(start_px), 8, (0, 255, 0), -1)
            cv2.circle(display, tuple(end_px), 8, (0, 0, 255), -1)
            cv2.putText(display, "START", (start_px[0] + 10, start_px[1]),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
            cv2.putText(display, "STOPPED", (end_px[0] + 10, end_px[1]),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)

        # HUD
        cv2.putText(display, "Left-click: repulsion vector | Right-click: simulate flight toward SSSI",
                    (20, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

        cv2.imshow("Geofence Repulsion", display)
        key = cv2.waitKey(50) & 0xFF
        if key == ord('q') or key == 27:
            break
        elif key == ord('r') or key == ord('R'):
            click_data['lat'] = None
            click_data['lon'] = None
            click_data['sim_path'] = None

    cv2.destroyAllWindows()
    print("Done.")


if __name__ == '__main__':
    main()
