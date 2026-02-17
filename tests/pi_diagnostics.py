#!/usr/bin/env python3
"""
SAR Drone System Diagnostics — Visual network topology dashboard.

Shows the Pi in the CENTRE with all subsystems branching out:
  LEFT:   Cube Orange (Serial → mavproxy → UDP)
  TOP:    GPS Module (built-in on Cube)
  RIGHT:  Camera (CSI/USB) + AI Model (TFLite/YOLO)
  BOTTOM: Ground Station / Mission Planner (TCP via WiFi)

Each connection line shows HOW the link works.
Each component box shows live status + data rates.
Bottom strip shows live telemetry values.

Usage:
    python tests/pi_diagnostics.py             # with display (Pi monitor / VNC)
    python tests/pi_diagnostics.py --headless   # terminal only (SSH)
"""
import sys
import os
import time
import math
import socket
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

headless = "--headless" in sys.argv

import cv2

# ============================================================
#  Status tracking
# ============================================================
class Status:
    def __init__(self):
        self.ok = False
        self.text = "CHECKING"
        self.error = ""

cam_s  = Status()
ai_s   = Status()
cube_s = Status()
gps_s  = Status()
gs_s   = Status()
pi_ip  = "unknown"

# ============================================================
#  Phase 1: Check all subsystems
# ============================================================
print("=" * 55)
print("  SAR DRONE SYSTEM DIAGNOSTICS")
print("=" * 55)

# --- Camera ---
print("\n[1/5] Checking camera...")
cap = None
picam = None
cam_source = ""
cam_res = ""

cap = cv2.VideoCapture(0)
if cap.isOpened():
    ret, test_frame = cap.read()
    if ret:
        h, w = test_frame.shape[:2]
        cam_s.ok = True
        cam_s.text = "CONNECTED"
        cam_source = "OpenCV"
        cam_res = f"{w}x{h}"
        print(f"  OK  Camera: OpenCV ({w}x{h})")
    else:
        cap.release()
        cap = None

if cap is None:
    try:
        from picamera2 import Picamera2
        picam = Picamera2()
        picam.configure(picam.create_preview_configuration(
            main={"size": (640, 480), "format": "RGB888"}
        ))
        picam.start()
        time.sleep(1)
        test_frame = picam.capture_array()
        h, w = test_frame.shape[:2]
        cam_s.ok = True
        cam_s.text = "CONNECTED"
        cam_source = "picamera2"
        cam_res = f"{w}x{h}"
        print(f"  OK  Camera: picamera2 ({w}x{h})")
    except Exception as e:
        cam_s.text = "FAILED"
        cam_s.error = str(e)[:60]
        print(f"  FAIL  Camera: {e}")

def get_frame():
    if cap:
        ret, f = cap.read()
        return f if ret else None
    if picam:
        f = picam.capture_array()
        return cv2.cvtColor(f, cv2.COLOR_RGB2BGR)
    return None

# --- AI Model ---
print("[2/5] Checking AI model...")
eyes = None
ai_backend = ""
ai_warmup = 0
try:
    from vision import VisionSystem
    eyes = VisionSystem(camera_index=None, model_path="best.tflite")
    if eyes.using_ai:
        ai_backend = "TFLite" if eyes._use_tflite_direct else "Ultralytics"
        ai_s.ok = True
        ai_s.text = "LOADED"
        t0 = time.time()
        eyes.detect_in_image(np.zeros((480, 640, 3), dtype=np.uint8))
        ai_warmup = (time.time() - t0) * 1000
        print(f"  OK  AI: {ai_backend} (warmup {ai_warmup:.0f}ms)")
    else:
        ai_s.text = "NOT LOADED"
        ai_s.error = "No model or backend"
        print(f"  WARN  AI model not loaded")
except Exception as e:
    ai_s.text = "FAILED"
    ai_s.error = str(e)[:60]
    print(f"  FAIL  AI: {e}")

# --- Cube ---
print("[3/5] Checking Cube connection...")
mav = None
conn_str = ""
cube_sysid = ""
try:
    from pymavlink import mavutil
    import config
    conn_str = config.CONNECTION_STR
    mav = mavutil.mavlink_connection(conn_str)
    mav.wait_heartbeat(timeout=5)
    cube_s.ok = True
    cube_s.text = "CONNECTED"
    cube_sysid = str(mav.target_system)
    try:
        mav.mav.request_data_stream_send(
            mav.target_system, mav.target_component,
            mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1
        )
    except Exception:
        pass
    print(f"  OK  Cube: system {cube_sysid} via {conn_str}")
except Exception as e:
    cube_s.text = "FAILED"
    cube_s.error = str(e)[:60]
    print(f"  FAIL  Cube: {e}")

# --- GPS ---
if cube_s.ok:
    gps_s.text = "WAITING..."
else:
    gps_s.text = "NO CUBE"

# --- Ground Station ---
print("[4/5] Checking GS forwarding port...")
def check_gs_port():
    global pi_ip
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 5762))
        sock.close()
        if result == 0:
            gs_s.ok = True
            gs_s.text = "PORT OPEN"
        else:
            gs_s.ok = False
            gs_s.text = "PORT CLOSED"
    except Exception:
        gs_s.ok = False
        gs_s.text = "CHECK FAILED"
    # Get Pi IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        pi_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass

check_gs_port()
if gs_s.ok:
    print(f"  OK  GS: TCP 5762 open (Pi IP: {pi_ip})")
else:
    print(f"  WARN  GS: {gs_s.text}")

# Summary
print(f"\n[5/5] Initial check complete:")
for label, s in [("CAMERA", cam_s), ("AI", ai_s), ("CUBE", cube_s),
                  ("GPS", gps_s), ("GS", gs_s)]:
    tag = " OK " if s.ok else "WAIT" if "WAIT" in s.text else "FAIL"
    print(f"  [{tag}] {label}: {s.text}")

# ============================================================
#  Live monitoring state
# ============================================================
telem = {
    "yaw": 0.0, "pitch": 0.0, "roll": 0.0,
    "alt_rel": 0.0, "alt_msl": 0.0,
    "lat": 0.0, "lon": 0.0,
    "fix": "---", "sats": 0, "hdop": 0.0,
    "voltage": 0.0, "current": 0.0,
}

msg_rates = {}
rate_counts = {}
rate_window_start = time.time()

frame_count = 0
frame_start_time = time.time()
camera_fps = 0.0
inference_times = []

# ============================================================
#  Drawing helpers
# ============================================================
# Colors (BGR)
GREEN  = (0, 200, 0)
RED    = (0, 0, 220)
YELLOW = (0, 200, 200)
CYAN   = (200, 180, 0)
WHITE  = (210, 210, 210)
GRAY   = (110, 110, 110)
DARK   = (40, 40, 40)
BG     = (25, 25, 25)
PI_CLR = (120, 60, 0)  # dark blue for Pi box

W = 960
H = 720

def draw_box(img, x, y, w, h, title, ok, detail_lines):
    """Draw a component box with colored title bar and detail lines."""
    border = GREEN if ok else RED
    # Fill
    cv2.rectangle(img, (x, y), (x + w, y + h), DARK, -1)
    # Title bar
    cv2.rectangle(img, (x, y), (x + w, y + 26), border, -1)
    # Title text (black on colored bar)
    cv2.putText(img, title, (x + 8, y + 19),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    # Border
    cv2.rectangle(img, (x, y), (x + w, y + h), border, 2)
    # Detail lines
    ly = y + 44
    for text, color in detail_lines:
        cv2.putText(img, text, (x + 8, ly),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, color, 1)
        ly += 17
    return ly

def draw_arrow(img, pt1, pt2, ok):
    """Draw connection arrow with arrowhead at pt2."""
    color = GREEN if ok else RED
    cv2.arrowedLine(img, pt1, pt2, color, 2, tipLength=0.04)

def draw_line_label(img, pt1, pt2, lines):
    """Draw label(s) at the midpoint of a connection line."""
    mx = (pt1[0] + pt2[0]) // 2
    my = (pt1[1] + pt2[1]) // 2
    # Offset multiple lines
    start_y = my - (len(lines) - 1) * 8
    for i, text in enumerate(lines):
        ty = start_y + i * 16
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.35, 1)
        # Dark background
        cv2.rectangle(img, (mx - tw // 2 - 3, ty - th - 2),
                      (mx + tw // 2 + 3, ty + 3), BG, -1)
        cv2.putText(img, text, (mx - tw // 2, ty),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, CYAN, 1)

def draw_dashboard():
    img = np.full((H, W, 3), 25, dtype=np.uint8)

    # ---- Title ----
    cv2.putText(img, "SAR DRONE — SYSTEM CONNECTIVITY", (20, 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, CYAN, 2)
    cv2.putText(img, time.strftime("%H:%M:%S"), (W - 130, 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, WHITE, 1)
    cv2.line(img, (15, 38), (W - 15, 38), GRAY, 1)

    # ============================================================
    #  BOX POSITIONS (Pi centre, components branch out)
    # ============================================================
    # Pi — centre
    pi_x, pi_y, pi_w, pi_h = 355, 225, 250, 200

    # Cube — left
    cb_x, cb_y, cb_w, cb_h = 20, 235, 200, 180

    # GPS — top (above and slightly left of Pi, connects to Cube)
    gp_x, gp_y, gp_w, gp_h = 40, 50, 175, 120

    # Camera — right
    ca_x, ca_y, ca_w, ca_h = 720, 185, 215, 130

    # AI — right, below camera
    ai_x, ai_y, ai_w, ai_h = 720, 370, 215, 115

    # GS — bottom
    gs_x, gs_y, gs_w, gs_h = 355, 530, 250, 110

    # ============================================================
    #  CONNECTION LINES (draw behind boxes)
    # ============================================================

    # GPS → Cube (vertical, left side)
    gps_bottom = (gp_x + gp_w // 2, gp_y + gp_h)
    cube_top   = (cb_x + cb_w // 2, cb_y)
    draw_arrow(img, gps_bottom, cube_top, gps_s.ok or cube_s.ok)
    draw_line_label(img, gps_bottom, cube_top, ["GPS port", "(built-in)"])

    # Cube → Pi (horizontal)
    cube_right = (cb_x + cb_w, cb_y + cb_h // 2)
    pi_left    = (pi_x, pi_y + pi_h // 2)
    draw_arrow(img, cube_right, pi_left, cube_s.ok)
    draw_line_label(img, cube_right, pi_left,
                    ["Serial /dev/ttyAMA0", "-> mavproxy", "-> UDP:14550"])

    # Camera → Pi (horizontal)
    cam_left  = (ca_x, ca_y + ca_h // 2)
    pi_right1 = (pi_x + pi_w, pi_y + 60)
    draw_arrow(img, cam_left, pi_right1, cam_s.ok)
    link_text = f"CSI -> {cam_source}" if cam_source else "CSI / USB"
    draw_line_label(img, cam_left, pi_right1, [link_text])

    # AI ↔ Pi (diagonal to right-bottom)
    ai_left   = (ai_x, ai_y + ai_h // 2)
    pi_right2 = (pi_x + pi_w, pi_y + pi_h - 40)
    draw_arrow(img, pi_right2, ai_left, ai_s.ok)
    draw_line_label(img, ai_left, pi_right2, ["frame -> detect", "-> (found,x,y,conf)"])

    # Pi → GS (vertical, bottom)
    pi_bottom = (pi_x + pi_w // 2, pi_y + pi_h)
    gs_top    = (gs_x + gs_w // 2, gs_y)
    draw_arrow(img, pi_bottom, gs_top, gs_s.ok)
    draw_line_label(img, pi_bottom, gs_top,
                    ["mavproxy TCP:5762", "-> WiFi ->", "Mission Planner"])

    # ============================================================
    #  BOXES (draw on top of lines)
    # ============================================================

    # --- GPS box ---
    gps_ok_live = telem['fix'] in ('3D', 'DGPS', 'RTK Float', 'RTK Fixed')
    if gps_ok_live:
        gps_s.ok = True
        gps_s.text = "3D FIX"
    elif telem['sats'] > 0:
        gps_s.ok = False
        gps_s.text = f"{telem['fix']}"
    elif cube_s.ok:
        gps_s.ok = False
        gps_s.text = telem['fix'] if telem['fix'] != '---' else "WAITING"

    gps_lines = [
        (f"Fix: {telem['fix']}", GREEN if gps_ok_live else YELLOW),
        (f"Sats: {telem['sats']}", WHITE),
        (f"HDOP: {telem['hdop']:.1f}", WHITE),
    ]
    if telem['lat'] != 0:
        gps_lines.append((f"({telem['lat']:.5f}, {telem['lon']:.5f})", WHITE))
    else:
        gps_lines.append(("No fix yet", YELLOW))
    draw_box(img, gp_x, gp_y, gp_w, gp_h, "GPS MODULE", gps_s.ok, gps_lines)

    # --- Cube box ---
    total_rate = sum(msg_rates.values())
    cube_lines = [
        (f"System ID: {cube_sysid}", WHITE),
        (f"Via: {conn_str}", WHITE),
        (f"Total: {total_rate:.0f} msgs/sec", GREEN if total_rate > 5 else YELLOW),
    ]
    # Key message rates
    for mt, short in [('ATTITUDE', 'ATT'), ('GLOBAL_POSITION_INT', 'POS'),
                      ('GPS_RAW_INT', 'GPS'), ('SYS_STATUS', 'BAT'),
                      ('HEARTBEAT', 'HB')]:
        rate = msg_rates.get(mt, 0)
        rc = GREEN if rate > 0.5 else (YELLOW if rate > 0 else RED)
        cube_lines.append((f"  {short:<4} {rate:>5.1f} Hz", rc))
    if not cube_s.ok:
        cube_lines = [
            (f"Error: {cube_s.error[:30]}", RED),
            ("Is mavproxy running?", YELLOW),
        ]
    draw_box(img, cb_x, cb_y, cb_w, cb_h, "CUBE ORANGE", cube_s.ok, cube_lines)

    # --- Pi box (centre, slightly larger, special color) ---
    # Draw with custom styling for the hub
    issues = sum(1 for s in [cam_s, ai_s, cube_s] if not s.ok)
    pi_ok = issues == 0
    pi_border = GREEN if pi_ok else YELLOW
    cv2.rectangle(img, (pi_x, pi_y), (pi_x + pi_w, pi_y + pi_h), DARK, -1)
    cv2.rectangle(img, (pi_x, pi_y), (pi_x + pi_w, pi_y + 26), PI_CLR, -1)
    cv2.putText(img, "RASPBERRY PI", (pi_x + 8, pi_y + 19),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, WHITE, 2)
    cv2.rectangle(img, (pi_x, pi_y), (pi_x + pi_w, pi_y + pi_h), pi_border, 2)

    pi_lines = [
        (f"IP: {pi_ip}", WHITE),
        (f"mavproxy: {'Running' if cube_s.ok else 'Not detected'}", GREEN if cube_s.ok else RED),
        (f"Camera: {cam_source} {cam_res}", GREEN if cam_s.ok else RED),
        (f"AI: {ai_backend}", GREEN if ai_s.ok else RED),
        ("", WHITE),
        (f"Camera FPS: {camera_fps:.1f}", WHITE),
    ]
    avg_ms = np.mean(inference_times[-30:]) if inference_times else 0
    pi_lines.append((f"AI inference: {avg_ms:.0f}ms", WHITE))
    # Count OK vs total
    ok_count = sum(1 for s in [cam_s, ai_s, cube_s, gps_s, gs_s] if s.ok)
    pi_lines.append((f"Systems: {ok_count}/5 OK", GREEN if ok_count == 5 else YELLOW))

    ly = pi_y + 44
    for text, color in pi_lines:
        cv2.putText(img, text, (pi_x + 10, ly),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, color, 1)
        ly += 17

    # --- Camera box ---
    cam_lines = []
    if cam_s.ok:
        cam_lines = [
            (f"Source: {cam_source}", WHITE),
            (f"Resolution: {cam_res}", WHITE),
            (f"FPS: {camera_fps:.1f}", GREEN if camera_fps > 10 else YELLOW),
        ]
    else:
        cam_lines = [
            (f"Error:", RED),
            (f"{cam_s.error[:28]}", RED),
        ]
    draw_box(img, ca_x, ca_y, ca_w, ca_h, "CAMERA", cam_s.ok, cam_lines)

    # --- AI box ---
    ai_lines = []
    if ai_s.ok:
        ai_lines = [
            (f"Backend: {ai_backend}", WHITE),
            (f"Model: best.tflite", WHITE),
            (f"Inference: {avg_ms:.0f}ms avg", GREEN if avg_ms < 200 else YELLOW),
            (f"Warmup: {ai_warmup:.0f}ms", GRAY),
        ]
    else:
        ai_lines = [
            (f"{ai_s.text}", RED),
            (f"{ai_s.error[:28]}", RED),
        ]
    draw_box(img, ai_x, ai_y, ai_w, ai_h, "AI MODEL", ai_s.ok, ai_lines)

    # --- GS box ---
    gs_lines = []
    if gs_s.ok:
        gs_lines = [
            (f"TCP 5762: OPEN", GREEN),
            (f"Pi IP: {pi_ip}", WHITE),
            (f"In MP: connect to {pi_ip}:5762", CYAN),
        ]
    else:
        gs_lines = [
            (f"TCP 5762: {gs_s.text}", RED),
            (f"Add to mavproxy:", YELLOW),
            (f"  --out=tcpin:0.0.0.0:5762", YELLOW),
        ]
    draw_box(img, gs_x, gs_y, gs_w, gs_h, "MISSION PLANNER (GS)", gs_s.ok, gs_lines)

    # ============================================================
    #  LIVE TELEMETRY STRIP (bottom)
    # ============================================================
    strip_y = H - 45
    cv2.rectangle(img, (0, strip_y), (W, H), (35, 35, 35), -1)
    cv2.line(img, (0, strip_y), (W, strip_y), GRAY, 1)

    cv2.putText(img, "LIVE TELEMETRY", (15, strip_y + 16),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, CYAN, 1)

    tl = (f"Yaw={telem['yaw']:.0f}   Pitch={telem['pitch']:.1f}   "
          f"Roll={telem['roll']:.1f}   |   "
          f"Alt={telem['alt_rel']:.1f}m rel   {telem['alt_msl']:.1f}m MSL   |   "
          f"Bat={telem['voltage']:.1f}V   |   "
          f"Spd={telem.get('ground_speed', 0):.1f}m/s")
    cv2.putText(img, tl, (15, strip_y + 36),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, WHITE, 1)

    # Footer controls
    cv2.putText(img, "'q' quit  |  'r' recheck GS  |  's' screenshot",
                (W - 370, strip_y + 16), cv2.FONT_HERSHEY_SIMPLEX, 0.33, GRAY, 1)

    return img

# ============================================================
#  Headless terminal output
# ============================================================
A_G = "\033[92m"; A_R = "\033[91m"; A_Y = "\033[93m"
A_C = "\033[96m"; A_B = "\033[1m"; A_0 = "\033[0m"

def print_headless():
    tag = lambda ok: f"{A_G}OK{A_0}" if ok else f"{A_R}FAIL{A_0}"
    print(f"\n{A_C}{'='*65}{A_0}")
    print(f"  {A_B}SAR DRONE CONNECTIVITY{A_0}  —  {time.strftime('%H:%M:%S')}")
    print(f"{A_C}{'='*65}{A_0}")

    print(f"\n       [{tag(gps_s.ok)}] GPS: {telem['fix']}  {telem['sats']} sats  "
          f"HDOP={telem['hdop']:.1f}")
    if telem['lat'] != 0:
        print(f"            ({telem['lat']:.7f}, {telem['lon']:.7f})")
    print(f"            {A_C}| GPS port (built-in){A_0}")

    print(f"\n  [{tag(cube_s.ok)}] CUBE ----Serial->mavproxy->UDP---- "
          f"[{'RASPBERRY PI':^18}] ----CSI/USB---- [{tag(cam_s.ok)}] CAMERA")
    if cube_s.ok:
        total = sum(msg_rates.values())
        print(f"       ID:{cube_sysid} {total:.0f}msg/s"
              f"                IP: {pi_ip}"
              f"                {cam_source} {cam_res} {camera_fps:.1f}fps")
        tracked = ['ATTITUDE', 'GLOBAL_POSITION_INT', 'GPS_RAW_INT', 'SYS_STATUS']
        for mt in tracked:
            rate = msg_rates.get(mt, 0)
            rc = A_G if rate > 0.5 else (A_Y if rate > 0 else A_R)
            print(f"         {rc}{mt:<26} {rate:>5.1f} Hz{A_0}")

    avg_ms = np.mean(inference_times[-30:]) if inference_times else 0
    print(f"\n                                           {A_C}|{A_0}")
    print(f"                                  [{tag(ai_s.ok)}] AI: {ai_backend}  "
          f"{avg_ms:.0f}ms")

    print(f"\n                                 {A_C}| TCP:5762 WiFi{A_0}")
    print(f"                          [{tag(gs_s.ok)}] MISSION PLANNER")
    if gs_s.ok:
        print(f"                               Connect MP to {pi_ip}:5762")

    print(f"\n  {A_C}TELEMETRY:{A_0} Yaw={telem['yaw']:.0f} Pitch={telem['pitch']:.1f} "
          f"Roll={telem['roll']:.1f} | Alt={telem['alt_rel']:.1f}m | "
          f"Bat={telem['voltage']:.1f}V")
    print()

# ============================================================
#  Main live loop
# ============================================================
print(f"\n{'='*55}")
if headless:
    print(f"  Live monitoring (HEADLESS). Ctrl+C to quit.")
else:
    print(f"  Live monitoring (DISPLAY). Press 'q' to quit.")
print(f"{'='*55}\n")

last_headless_print = 0
last_gs_check = time.time()

try:
    while True:
        # --- Drain Cube messages + update telemetry ---
        if mav:
            while True:
                msg = mav.recv_msg()
                if msg is None:
                    break
                t = msg.get_type()
                rate_counts[t] = rate_counts.get(t, 0) + 1

            # Recalculate rates every 2 seconds
            elapsed_rate = time.time() - rate_window_start
            if elapsed_rate >= 2.0:
                for t, c in rate_counts.items():
                    msg_rates[t] = c / elapsed_rate
                rate_counts = {}
                rate_window_start = time.time()

            # Read latest telemetry from cache
            att = mav.messages.get('ATTITUDE')
            if att:
                telem['yaw'] = math.degrees(att.yaw)
                telem['pitch'] = math.degrees(att.pitch)
                telem['roll'] = math.degrees(att.roll)

            pos = mav.messages.get('GLOBAL_POSITION_INT')
            if pos:
                telem['lat'] = pos.lat / 1e7
                telem['lon'] = pos.lon / 1e7
                telem['alt_msl'] = pos.alt / 1000.0
                telem['alt_rel'] = pos.relative_alt / 1000.0

            gps_raw = mav.messages.get('GPS_RAW_INT')
            if gps_raw:
                fix_names = {0: "No GPS", 1: "No Fix", 2: "2D", 3: "3D",
                             4: "DGPS", 5: "RTK Float", 6: "RTK Fixed"}
                telem['fix'] = fix_names.get(gps_raw.fix_type, f"Type {gps_raw.fix_type}")
                telem['sats'] = gps_raw.satellites_visible
                telem['hdop'] = gps_raw.eph / 100.0 if gps_raw.eph < 10000 else 0

            bat = mav.messages.get('SYS_STATUS')
            if bat:
                telem['voltage'] = bat.voltage_battery / 1000.0
                telem['current'] = bat.current_battery / 100.0 if bat.current_battery != -1 else 0

        # --- Camera frame + FPS ---
        frame = get_frame()
        if frame is not None:
            frame_count += 1
            elapsed_cam = time.time() - frame_start_time
            if elapsed_cam > 0:
                camera_fps = frame_count / elapsed_cam
            # AI inference for speed tracking
            if eyes and eyes.using_ai:
                t0 = time.time()
                eyes.detect_in_image(frame)
                inference_times.append((time.time() - t0) * 1000)

        # --- Recheck GS port periodically ---
        if time.time() - last_gs_check > 10.0:
            check_gs_port()
            last_gs_check = time.time()

        # --- Display ---
        if not headless:
            dashboard = draw_dashboard()
            cv2.imshow("SAR Drone Diagnostics", dashboard)
            key = cv2.waitKey(30) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('r'):
                check_gs_port()
            elif key == ord('s'):
                cv2.imwrite("diagnostics_screenshot.png", dashboard)
                print("  Saved: diagnostics_screenshot.png")
        else:
            now = time.time()
            if now - last_headless_print > 3.0:
                last_headless_print = now
                print_headless()
            time.sleep(0.05)

except KeyboardInterrupt:
    print("\nStopping...")

# Cleanup
if cap:
    cap.release()
if picam:
    try:
        picam.stop()
    except Exception:
        pass
cv2.destroyAllWindows()

# Final summary
ok_count = sum(1 for s in [cam_s, ai_s, cube_s, gps_s, gs_s] if s.ok)
print(f"\n{'='*55}")
print(f"  DIAGNOSTICS SUMMARY  ({ok_count}/5 systems OK)")
print(f"{'='*55}")
for label, s in [("CAMERA", cam_s), ("AI MODEL", ai_s), ("CUBE", cube_s),
                  ("GPS", gps_s), ("GS", gs_s)]:
    tag = " OK " if s.ok else "FAIL"
    print(f"  [{tag}]  {label}: {s.text}")
if frame_count > 0:
    print(f"\n  Frames: {frame_count}   FPS: {camera_fps:.1f}")
if inference_times:
    print(f"  AI avg: {np.mean(inference_times[-30:]):.0f}ms")
if msg_rates:
    print(f"  Cube:   {sum(msg_rates.values()):.0f} msgs/sec")
print()
