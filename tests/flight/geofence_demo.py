#!/usr/bin/env python3
"""
Geofence Demo — Upload hardware fence to ArduCopter and test it.

Demonstrates the 3-layer geofence approach:
  1. Plan-time: filter waypoints that are inside NFZ
  2. Software: speed reduction + repulsion near boundary
  3. Hardware: ArduCopter polygon fence with auto-RTL on breach

Usage:
    # With SITL running in Mission Planner:
    python tests/flight/geofence_demo.py

    # Just show the zones (no connection needed):
    python tests/flight/geofence_demo.py --dry-run

    # Test breach (fly toward SSSI to trigger hardware fence):
    python tests/flight/geofence_demo.py --test-breach

Controls:
    Q = quit
    F = toggle fence enable/disable
    B = attempt to fly toward SSSI (test breach)
"""
import sys
import os
import time
import math

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)
os.chdir(project_root)

import cv2
import numpy as np
import config

# Load KML zones
if hasattr(config, 'load_kml_zones'):
    config.load_kml_zones()

DRY_RUN = "--dry-run" in sys.argv
TEST_BREACH = "--test-breach" in sys.argv


# ── GPS math ──────────────────────────────────────────────────────────

def gps_distance(lat1, lon1, lat2, lon2):
    """Haversine distance in meters."""
    R = 6371000
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (math.sin(dlat / 2) ** 2 +
         math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) *
         math.sin(dlon / 2) ** 2)
    return R * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))


def point_in_polygon(lat, lon, polygon):
    """Ray-casting point-in-polygon test."""
    n = len(polygon)
    inside = False
    j = n - 1
    for i in range(n):
        yi, xi = polygon[i]
        yj, xj = polygon[j]
        if ((yi > lon) != (yj > lon)) and \
           (lat < (xj - xi) * (lon - yi) / (yj - yi) + xi):
            inside = not inside
        j = i
    return inside


def min_distance_to_polygon(lat, lon, polygon):
    """Minimum distance in meters from point to polygon boundary."""
    min_dist = float('inf')
    n = len(polygon)
    for i in range(n):
        j = (i + 1) % n
        ax, ay = polygon[i]
        bx, by = polygon[j]
        # Project point onto segment
        dx, dy = bx - ax, by - ay
        if dx == 0 and dy == 0:
            d = gps_distance(lat, lon, ax, ay)
        else:
            t = max(0, min(1, ((lat - ax) * dx + (lon - ay) * dy) / (dx * dx + dy * dy)))
            proj_lat = ax + t * dx
            proj_lon = ay + t * dy
            d = gps_distance(lat, lon, proj_lat, proj_lon)
        min_dist = min(min_dist, d)
    return min_dist


def validate_waypoint(lat, lon, alt, flight_area, exclusion_zones,
                      alt_min=2, alt_max=60):
    """Check if a waypoint is safe. Returns (valid, reason)."""
    if alt > alt_max:
        return False, f"Alt {alt:.0f}m > max {alt_max}m"
    if alt < alt_min:
        return False, f"Alt {alt:.0f}m < min {alt_min}m"
    if flight_area and not point_in_polygon(lat, lon, flight_area):
        return False, "Outside flight area"
    for i, zone in enumerate(exclusion_zones):
        if point_in_polygon(lat, lon, zone):
            return False, f"Inside exclusion zone {i}"
        dist = min_distance_to_polygon(lat, lon, zone)
        if dist < 5:
            return False, f"Within 5m of exclusion zone {i} ({dist:.1f}m)"
    return True, "OK"


# ── Hardware fence upload ─────────────────────────────────────────────

def set_param(master, name, value):
    """Set a parameter on the autopilot."""
    from pymavlink import mavutil
    master.mav.param_set_send(
        master.target_system, master.target_component,
        name.encode('utf-8') if isinstance(name, str) else name,
        value,
        mavutil.mavlink.MAV_PARAM_TYPE_REAL32
    )
    msg = master.recv_match(type='PARAM_VALUE', blocking=True, timeout=3)
    if msg:
        print(f"  {name} = {msg.param_value}")
        return True
    print(f"  {name} — no ACK")
    return False


def upload_fence(master, inclusion_points, exclusion_polygons):
    """Upload inclusion + exclusion polygons to ArduCopter fence."""
    from pymavlink import mavutil

    # Build flat list of fence items
    items = []

    # Inclusion polygon (flight area boundary)
    if inclusion_points:
        inc_count = len(inclusion_points)
        for lat, lon in inclusion_points:
            items.append({
                'cmd': mavutil.mavlink.MAV_CMD_NAV_FENCE_POLYGON_VERTEX_INCLUSION,
                'param1': inc_count,
                'lat': lat, 'lon': lon
            })

    # Exclusion polygons (no-fly zones)
    for exc_poly in exclusion_polygons:
        exc_count = len(exc_poly)
        for lat, lon in exc_poly:
            items.append({
                'cmd': mavutil.mavlink.MAV_CMD_NAV_FENCE_POLYGON_VERTEX_EXCLUSION,
                'param1': exc_count,
                'lat': lat, 'lon': lon
            })

    total = len(items)
    if total == 0:
        print("No fence points to upload")
        return False

    print(f"Uploading fence: {total} vertices...")

    # Send MISSION_COUNT with fence type
    master.mav.mission_count_send(
        master.target_system, master.target_component,
        total, mavutil.mavlink.MAV_MISSION_TYPE_FENCE
    )

    # Respond to each request
    for i in range(total):
        msg = master.recv_match(
            type=['MISSION_REQUEST_INT', 'MISSION_REQUEST'],
            blocking=True, timeout=5)
        if msg is None:
            print(f"  Timeout at vertex {i}")
            return False

        item = items[msg.seq]
        master.mav.mission_item_int_send(
            master.target_system, master.target_component,
            msg.seq,
            mavutil.mavlink.MAV_FRAME_GLOBAL,
            item['cmd'],
            0, 0,           # current, autocontinue
            item['param1'],  # vertex count for this polygon
            0, 0, 0,        # param2-4
            int(item['lat'] * 1e7),
            int(item['lon'] * 1e7),
            0,              # altitude (unused for fence)
            mavutil.mavlink.MAV_MISSION_TYPE_FENCE
        )

    # Wait for ACK
    ack = master.recv_match(type='MISSION_ACK', blocking=True, timeout=5)
    if ack and ack.type == mavutil.mavlink.MAV_MISSION_ACCEPTED:
        print(f"  Fence uploaded OK: {total} vertices")
        return True
    else:
        result = ack.type if ack else "no response"
        print(f"  Fence upload FAILED: {result}")
        return False


def setup_hardware_fence(master, alt_max=60, alt_min=2):
    """Configure and enable ArduCopter hardware fence."""
    print("\n=== HARDWARE FENCE SETUP ===")

    # Set parameters
    params = {
        'FENCE_ENABLE': 1,
        'FENCE_TYPE': 13,       # max alt (1) + polygon (4) + min alt (8)
        'FENCE_ACTION': 1,      # RTL or Land
        'FENCE_ALT_MAX': alt_max,
        'FENCE_ALT_MIN': alt_min,
        'FENCE_MARGIN': 3,      # 3m warning buffer
    }
    for name, value in params.items():
        set_param(master, name, value)

    # Upload polygons
    inclusion = config.FLIGHT_AREA_GPS if hasattr(config, 'FLIGHT_AREA_GPS') else []
    exclusion = [config.SSSI_GPS] if hasattr(config, 'SSSI_GPS') and config.SSSI_GPS else []

    if inclusion or exclusion:
        success = upload_fence(master, inclusion, exclusion)
    else:
        print("  No polygons defined in config — skipping upload")
        success = False

    # Enable
    set_param(master, 'FENCE_ENABLE', 1)
    print(f"  Hardware fence: {'ACTIVE' if success else 'FAILED'}")
    return success


# ── Software fence checks ─────────────────────────────────────────────

def check_software_fence(lat, lon, alt):
    """Layer 2: software-side boundary check. Returns (status, details)."""
    flight_area = config.FLIGHT_AREA_GPS if hasattr(config, 'FLIGHT_AREA_GPS') else []
    sssi = config.SSSI_GPS if hasattr(config, 'SSSI_GPS') else []
    exclusion_zones = [sssi] if sssi else []

    valid, reason = validate_waypoint(lat, lon, alt, flight_area, exclusion_zones)

    if not valid:
        return 'BLOCKED', reason

    # Distance warnings
    if sssi:
        dist = min_distance_to_polygon(lat, lon, sssi)
        if dist < 10:
            return 'CRITICAL', f"SSSI {dist:.0f}m away — RTL!"
        elif dist < 25:
            speed_factor = 0.3 + 0.7 * ((dist - 10) / 15)
            return 'WARNING', f"SSSI {dist:.0f}m — speed {speed_factor:.0%}"

    if flight_area:
        dist = min_distance_to_polygon(lat, lon, flight_area)
        if dist < 10:
            return 'WARNING', f"Flight boundary {dist:.0f}m away"

    return 'SAFE', 'OK'


# ── Waypoint filtering (Layer 1) ──────────────────────────────────────

def filter_waypoints(waypoints, buffer_m=10):
    """Layer 1: remove waypoints that violate geofence."""
    flight_area = config.FLIGHT_AREA_GPS if hasattr(config, 'FLIGHT_AREA_GPS') else []
    sssi = config.SSSI_GPS if hasattr(config, 'SSSI_GPS') else []
    exclusion_zones = [sssi] if sssi else []

    safe = []
    skipped = 0
    for lat, lon in waypoints:
        # Check exclusion zones only (flight area inclusion check
        # uses GPS ray-casting which can be inaccurate — use pixel-based
        # geofence.py for production)
        too_close = False
        for zone in exclusion_zones:
            if point_in_polygon(lat, lon, zone):
                too_close = True
                break
            if min_distance_to_polygon(lat, lon, zone) < buffer_m:
                too_close = True
                break
        if not too_close:
            safe.append((lat, lon))
            else:
                skipped += 1
        else:
            skipped += 1

    if skipped:
        print(f"  Filtered: {skipped} waypoints removed ({buffer_m}m buffer)")
    return safe


# ── Visualization ─────────────────────────────────────────────────────

def draw_zones(img, geo):
    """Draw all geofence zones on map image."""
    # Flight area (green)
    if hasattr(config, 'FLIGHT_AREA_GPS') and config.FLIGHT_AREA_GPS:
        pts = np.array([geo.gps_to_pixels(lat, lon)
                        for lat, lon in config.FLIGHT_AREA_GPS], dtype=np.int32)
        cv2.polylines(img, [pts], True, (0, 255, 0), 2)
        cx, cy = pts.mean(axis=0).astype(int)
        cv2.putText(img, "FLIGHT AREA", (cx - 60, cy),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    # Search area (cyan)
    if hasattr(config, 'SEARCH_AREA_GPS') and config.SEARCH_AREA_GPS:
        pts = np.array([geo.gps_to_pixels(lat, lon)
                        for lat, lon in config.SEARCH_AREA_GPS], dtype=np.int32)
        cv2.polylines(img, [pts], True, (255, 255, 0), 2)

    # SSSI no-fly zone (red with fill)
    if hasattr(config, 'SSSI_GPS') and config.SSSI_GPS:
        pts = np.array([geo.gps_to_pixels(lat, lon)
                        for lat, lon in config.SSSI_GPS], dtype=np.int32)
        overlay = img.copy()
        cv2.fillPoly(overlay, [pts], (0, 0, 80))
        cv2.addWeighted(overlay, 0.3, img, 0.7, 0, img)
        cv2.polylines(img, [pts], True, (0, 0, 255), 3)
        cx, cy = pts.mean(axis=0).astype(int)
        cv2.putText(img, "SSSI NFZ", (cx - 50, cy),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)

    # Takeoff point (white circle)
    if hasattr(config, 'TAKEOFF_GPS') and config.TAKEOFF_GPS:
        px = geo.gps_to_pixels(config.TAKEOFF_GPS[0], config.TAKEOFF_GPS[1])
        cv2.circle(img, tuple(px), 8, (255, 255, 255), -1)
        cv2.putText(img, "HOME", (px[0] + 12, px[1] + 5),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    return img


# ── Main ──────────────────────────────────────────────────────────────

def main():
    from utils import GeoTransformer

    print("=" * 60)
    print("  GEOFENCE DEMO — 3-Layer Protection")
    print("=" * 60)

    # Load map
    map_img = cv2.imread("assets/map.jpg")
    if map_img is None:
        map_img = cv2.imread("map.jpg")
    if map_img is None:
        print("[!] map.jpg not found")
        return
    h, w = map_img.shape[:2]

    # Geo transformer
    geo = GeoTransformer(w)
    print(f"Map: {w}x{h}, scale: {geo.pix_per_m:.2f} px/m")

    # Show zones
    print(f"\nZones from KML:")
    if config.FLIGHT_AREA_GPS:
        print(f"  Flight Area: {len(config.FLIGHT_AREA_GPS)} corners")
    if config.SEARCH_AREA_GPS:
        print(f"  Search Area: {len(config.SEARCH_AREA_GPS)} corners")
    if config.SSSI_GPS:
        print(f"  SSSI NFZ:    {len(config.SSSI_GPS)} corners")
    if config.TAKEOFF_GPS:
        print(f"  Takeoff:     ({config.TAKEOFF_GPS[0]:.6f}, {config.TAKEOFF_GPS[1]:.6f})")

    # === LAYER 1: Plan-time waypoint filtering ===
    print(f"\n--- LAYER 1: Plan-Time Waypoint Filtering ---")
    from planning import PathPlanner
    planner = PathPlanner(geo, [geo.gps_to_pixels(lat, lon)
                                for lat, lon in config.SEARCH_AREA_GPS])
    raw_wps = planner.generate_search_pattern(w, h, config.TAKEOFF_GPS)
    print(f"  Raw waypoints: {len(raw_wps)}")
    safe_wps = filter_waypoints(raw_wps, buffer_m=10)
    print(f"  Safe waypoints: {len(safe_wps)}")

    # === LAYER 2: Software runtime checks ===
    print(f"\n--- LAYER 2: Software Runtime Checks ---")
    test_points = [
        config.TAKEOFF_GPS,
        config.SEARCH_AREA_GPS[0] if config.SEARCH_AREA_GPS else None,
        config.SSSI_GPS[0] if config.SSSI_GPS else None,
    ]
    for pt in test_points:
        if pt:
            status, detail = check_software_fence(pt[0], pt[1], config.TARGET_ALT)
            print(f"  ({pt[0]:.6f}, {pt[1]:.6f}) -> {status}: {detail}")

    # === Visualization ===
    display = map_img.copy()
    display = draw_zones(display, geo)

    # Draw raw waypoints (red = unsafe, green = safe)
    safe_set = set(safe_wps)
    for i, wp in enumerate(raw_wps):
        px = geo.gps_to_pixels(wp[0], wp[1])
        color = (0, 200, 0) if wp in safe_set else (0, 0, 255)
        cv2.circle(display, tuple(px), 4, color, -1)
        if i > 0:
            prev_px = geo.gps_to_pixels(raw_wps[i - 1][0], raw_wps[i - 1][1])
            cv2.line(display, tuple(prev_px), tuple(px), color, 1)

    # Legend
    cv2.putText(display, "Green = safe waypoint", (20, 30),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 200, 0), 2)
    cv2.putText(display, "Red = filtered (too close to NFZ)", (20, 55),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    cv2.putText(display, "Red fill = SSSI no-fly zone", (20, 80),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 200), 2)

    if DRY_RUN:
        print(f"\n--- DRY RUN — No connection ---")
        print(f"  Layer 3 (hardware fence) would upload:")
        if config.FLIGHT_AREA_GPS:
            print(f"    Inclusion: {len(config.FLIGHT_AREA_GPS)} vertices (flight area)")
        if config.SSSI_GPS:
            print(f"    Exclusion: {len(config.SSSI_GPS)} vertices (SSSI)")
        print(f"    FENCE_TYPE=13, FENCE_ACTION=1 (RTL), ALT_MAX=60m")

        cv2.namedWindow("Geofence Demo", cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
        cv2.imshow("Geofence Demo", display)
        print(f"\nPress Q to quit.")
        while True:
            key = cv2.waitKey(100) & 0xFF
            if key == ord('q') or key == 27:
                break
        cv2.destroyAllWindows()
        return

    # === LAYER 3: Hardware fence ===
    print(f"\n--- LAYER 3: Hardware Fence (ArduCopter) ---")
    from pymavlink import mavutil

    print(f"Connecting to {config.CONNECTION_STR}...")
    master = mavutil.mavlink_connection(config.CONNECTION_STR)
    master.wait_heartbeat(timeout=10)
    print(f"  Connected: system {master.target_system}")

    success = setup_hardware_fence(master, alt_max=60, alt_min=2)

    # Monitor fence status
    print(f"\n--- MONITORING (Q=quit, F=toggle fence) ---")
    cv2.namedWindow("Geofence Demo", cv2.WINDOW_NORMAL | cv2.WINDOW_KEEPRATIO)
    fence_enabled = True

    while True:
        # Read telemetry
        msg = master.recv_match(blocking=False)
        if msg:
            mtype = msg.get_type()
            if mtype == 'GLOBAL_POSITION_INT':
                lat = msg.lat / 1e7
                lon = msg.lon / 1e7
                alt = msg.relative_alt / 1000.0

                # Software check
                status, detail = check_software_fence(lat, lon, alt)

                # Draw drone position
                frame = display.copy()
                px = geo.gps_to_pixels(lat, lon)
                color = {'SAFE': (0, 255, 0), 'WARNING': (0, 255, 255),
                         'CRITICAL': (0, 0, 255), 'BLOCKED': (0, 0, 255)}
                cv2.circle(frame, tuple(px), 10, color.get(status, (255, 255, 255)), -1)
                cv2.circle(frame, tuple(px), 10, (255, 255, 255), 2)

                # HUD
                cv2.putText(frame, f"Alt: {alt:.1f}m  Status: {status}",
                            (20, h - 40), cv2.FONT_HERSHEY_SIMPLEX, 0.6,
                            color.get(status, (255, 255, 255)), 2)
                cv2.putText(frame, f"Fence: {'ON' if fence_enabled else 'OFF'}  {detail}",
                            (20, h - 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5,
                            (200, 200, 200), 1)

                cv2.imshow("Geofence Demo", frame)

            elif mtype == 'FENCE_STATUS':
                if msg.breach_status:
                    print(f"  !!! FENCE BREACH: type={msg.breach_type}, "
                          f"count={msg.breach_count}")

        key = cv2.waitKey(10) & 0xFF
        if key == ord('q') or key == 27:
            break
        elif key == ord('f') or key == ord('F'):
            fence_enabled = not fence_enabled
            set_param(master, 'FENCE_ENABLE', 1 if fence_enabled else 0)
            print(f"  Fence {'ENABLED' if fence_enabled else 'DISABLED'}")

    cv2.destroyAllWindows()
    print("Done.")


if __name__ == '__main__':
    main()
