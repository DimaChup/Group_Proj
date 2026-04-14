"""Sim-tilt sign/convention calibration.

Places a dummy at known offsets from the drone and renders the simulated view
with pitch/roll/yaw applied. For each case it:
  1. Renders the perspective view via SimulationEnvironment.get_drone_view()
  2. Finds the dummy in the rendered frame via template matching
  3. Passes the found pixel to gps_utils.calculate_target_from_pixels()
  4. Compares the returned GPS estimate to the ground truth dummy position
  5. Saves an annotated PNG for visual inspection

Run:
    python tests/calibration/sim_tilt_calib.py

Output:
    tests/calibration/_calib_out/case_*.png   (annotated views)
    Console table with PASS/FAIL per case.
"""
import os
import sys
import math

# Add project root to path
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, ROOT)
os.chdir(ROOT)

os.environ.setdefault("DRONE_MODE", "SIMULATION")

import numpy as np
import cv2

import config
from utils import GeoTransformer
from simulator.simulation import SimulationEnvironment
from gps_utils import calculate_target_from_pixels

OUT = os.path.join(HERE, "_calib_out")
os.makedirs(OUT, exist_ok=True)


# ── Test setup ─────────────────────────────────────────────────────────────
TEST_LAT = 51.423406
TEST_LON = -2.671446
TEST_ALT = 35.0

config.REF_LAT = TEST_LAT
config.REF_LON = TEST_LON

geo = GeoTransformer(map_w_px=100)
sim_tmp = SimulationEnvironment(geo)
# Rebuild geo with proper map size (needed for proper pix_per_m)
geo = GeoTransformer(map_w_px=sim_tmp.map_w)
sim_tmp.geo = geo
drone_x, drone_y = geo.gps_to_pixels(TEST_LAT, TEST_LON)
print(f"Drone at map pixel ({drone_x:.1f}, {drone_y:.1f})")
print(f"Drone GPS: ({TEST_LAT}, {TEST_LON}) alt={TEST_ALT}m")
print(f"pix_per_m: {geo.pix_per_m:.4f}")
print()

sim = sim_tmp


def offset_to_dummy_xy(north_m, east_m):
    """Compute dummy map pixel position for a given N/E offset from drone."""
    d_lat = north_m / 111320.0
    d_lon = east_m / (111320.0 * math.cos(math.radians(TEST_LAT)))
    d_lat_deg = TEST_LAT + d_lat
    d_lon_deg = TEST_LON + d_lon
    return geo.gps_to_pixels(d_lat_deg, d_lon_deg)


def render_case(yaw_deg, pitch_deg, dummy_n_m, dummy_e_m):
    """Set up dummy, render view, return frame and ground truth info."""
    yaw = math.radians(yaw_deg)
    pitch = math.radians(pitch_deg)
    roll = 0.0

    dummy_x, dummy_y = offset_to_dummy_xy(dummy_n_m, dummy_e_m)
    sim.sim_targets = [(dummy_x, dummy_y)]
    sim.sim_target_types = ["dummy"]

    fov = 2 * math.atan(config.SENSOR_WIDTH_MM / (2 * config.FOCAL_LENGTH_MM))
    ground_w = 2 * TEST_ALT * math.tan(fov / 2)
    view_w_px = int(ground_w * sim.geo.pix_per_m)

    frame, _, _ = sim.get_drone_view(
        int(drone_x), int(drone_y), TEST_ALT, yaw,
        pitch=pitch, roll=roll,
    )
    return frame, (dummy_x, dummy_y), yaw, pitch


def find_dummy_in_frame(frame):
    """Template-match sim.dummy_img against the rendered frame.

    Returns (cx, cy) pixel of best match, or None if template is missing.
    """
    if sim.dummy_img is None:
        return None
    template = sim.dummy_img
    if template.shape[2] == 4:
        # Use the RGB channels, weighted by alpha
        alpha = template[:, :, 3] / 255.0
        rgb = template[:, :, :3]
        template_gray = cv2.cvtColor(rgb, cv2.COLOR_BGR2GRAY)
    else:
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)

    # Scale template to expected size at test altitude (rough approximation)
    # Dummy is ~1.8m tall; pixels-per-metre at 35m altitude depends on FOV
    fov_h = 2 * math.atan(config.IMAGE_H / (2 * config.IMAGE_W) *
                           math.tan(math.radians(54.4 / 2)))
    ground_h_m = 2 * TEST_ALT * math.tan(fov_h / 2)
    px_per_m = config.IMAGE_H / ground_h_m
    expected_h_px = int(1.8 * px_per_m)

    if expected_h_px < 8 or expected_h_px > template_gray.shape[0]:
        expected_h_px = max(16, min(64, expected_h_px))

    scale = expected_h_px / template_gray.shape[0]
    new_w = max(4, int(template_gray.shape[1] * scale))
    new_h = max(4, int(template_gray.shape[0] * scale))
    small_template = cv2.resize(template_gray, (new_w, new_h))

    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    if small_template.shape[0] > frame_gray.shape[0] or small_template.shape[1] > frame_gray.shape[1]:
        return None
    res = cv2.matchTemplate(frame_gray, small_template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(res)
    if max_val < 0.3:
        return None
    cx = max_loc[0] + small_template.shape[1] // 2
    cy = max_loc[1] + small_template.shape[0] // 2
    return (cx, cy)


def gps_error_m(est_lat, est_lon, true_lat, true_lon):
    """Great-circle distance in metres (small-angle)."""
    d_lat = (est_lat - true_lat) * 111320.0
    d_lon = (est_lon - true_lon) * 111320.0 * math.cos(math.radians(true_lat))
    return math.sqrt(d_lat * d_lat + d_lon * d_lon)


def run_case(name, yaw_deg, pitch_deg, dummy_n_m, dummy_e_m):
    frame, (dummy_x, dummy_y), yaw, pitch = render_case(
        yaw_deg, pitch_deg, dummy_n_m, dummy_e_m)

    found = find_dummy_in_frame(frame)
    d_lat = TEST_LAT + dummy_n_m / 111320.0
    d_lon = TEST_LON + dummy_e_m / (111320.0 * math.cos(math.radians(TEST_LAT)))

    annotated = frame.copy()
    if found is None:
        status = "NO DETECTION"
        err = float("inf")
        est_lat = est_lon = None
    else:
        u, v = found
        cv2.circle(annotated, (u, v), 14, (0, 0, 255), 2)
        cv2.line(annotated, (u - 20, v), (u + 20, v), (0, 0, 255), 1)
        cv2.line(annotated, (u, v - 20), (u, v + 20), (0, 0, 255), 1)
        est_lat, est_lon = calculate_target_from_pixels(
            u, v, TEST_ALT, yaw, TEST_LAT, TEST_LON,
            config.IMAGE_W, config.IMAGE_H,
            config.SENSOR_WIDTH_MM, config.FOCAL_LENGTH_MM,
            drone_pitch=pitch, drone_roll=0.0,
        )
        err = gps_error_m(est_lat, est_lon, d_lat, d_lon)
        status = "PASS" if err < 3.0 else "FAIL"

    # Annotations
    def put(img, text, y):
        cv2.putText(img, text, (12, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                    (255, 255, 255), 2, cv2.LINE_AA)
        cv2.putText(img, text, (12, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55,
                    (0, 0, 0), 1, cv2.LINE_AA)
    put(annotated, f"{name}", 30)
    put(annotated, f"yaw={yaw_deg}  pitch={pitch_deg}", 55)
    put(annotated, f"dummy N={dummy_n_m}m E={dummy_e_m}m", 80)
    if est_lat is not None:
        est_n = (est_lat - TEST_LAT) * 111320.0
        est_e = (est_lon - TEST_LON) * 111320.0 * math.cos(math.radians(TEST_LAT))
        put(annotated, f"est  N={est_n:+.1f}m E={est_e:+.1f}m  err={err:.1f}m  [{status}]", 105)
    else:
        put(annotated, f"[{status}]", 105)

    out_path = os.path.join(OUT, f"{name}.png")
    cv2.imwrite(out_path, annotated)

    return status, err, est_lat, est_lon


# ── Cases ──────────────────────────────────────────────────────────────────
CASES = [
    # name, yaw, pitch, dummy N, dummy E
    ("01_nadir_N",   0,    0, 10, 0),
    ("02_nadir_E",   0,    0,  0,10),
    ("03_nadir_S",   0,    0,-10, 0),
    ("04_nadir_W",   0,    0,  0,-10),
    ("05_pitch_N",   0,   -6, 10, 0),
    ("06_pitch_E",   0,   -6,  0,10),
    ("07_pitch_S",   0,   -6,-10, 0),
    ("08_pitch_W",   0,   -6,  0,-10),
    ("09_yaw90_N",  90,    0, 10, 0),
    ("10_yaw90_E",  90,    0,  0,10),
    ("11_yaw90pitch_N", 90, -6, 10, 0),
    ("12_yaw90pitch_E", 90, -6,  0,10),
]

print(f"{'case':<22} {'yaw':>4} {'pitch':>6} {'dummyN':>7} {'dummyE':>7} {'estN':>7} {'estE':>7} {'err':>7}  status")
print("-" * 100)

n_pass = 0
n_fail = 0
for name, yaw, pitch, dn, de in CASES:
    status, err, est_lat, est_lon = run_case(name, yaw, pitch, dn, de)
    if est_lat is not None:
        est_n = (est_lat - TEST_LAT) * 111320.0
        est_e = (est_lon - TEST_LON) * 111320.0 * math.cos(math.radians(TEST_LAT))
        est_n_str = f"{est_n:+.1f}"
        est_e_str = f"{est_e:+.1f}"
        err_str = f"{err:.1f}"
    else:
        est_n_str = est_e_str = err_str = "---"
    print(f"{name:<22} {yaw:>4} {pitch:>6} {dn:>7} {de:>7} {est_n_str:>7} {est_e_str:>7} {err_str:>7}  {status}")
    if status == "PASS":
        n_pass += 1
    else:
        n_fail += 1

print("-" * 100)
print(f"Results: {n_pass} pass, {n_fail} fail")
print(f"Annotated PNGs saved to: {OUT}")
