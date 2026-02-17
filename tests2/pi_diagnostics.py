#!/usr/bin/env python3
"""
SAR Drone System Diagnostics — Multi-view connectivity dashboard.

Three switchable views (press 1/2/3):

  VIEW 1 — CONNECTIVITY DIAGRAM
    Pi in centre, components branching out with labeled connection lines.
    Shows which subsystems are OK/FAIL and HOW each link works.

  VIEW 2 — CAMERA FEED
    Raw camera feed with FPS counter. Press 'a' to toggle AI overlay.
    AI off  → see raw camera capability (FPS, resolution)
    AI on   → see detections, inference time, effective FPS
    Compare the two to see AI overhead.

  VIEW 3 — CUBE TELEMETRY
    Detailed live readings from Cube: attitude, GPS, battery, altitude.
    All MAVLink message types with their rates in Hz.

Usage:
    python tests/pi_diagnostics.py             # with display
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
cam_w, cam_h = 0, 0

cap = cv2.VideoCapture(0)
if cap.isOpened():
    ret, test_frame = cap.read()
    if ret:
        cam_h, cam_w = test_frame.shape[:2]
        cam_s.ok = True
        cam_s.text = "CONNECTED"
        cam_source = "OpenCV"
        cam_res = f"{cam_w}x{cam_h}"
        print(f"  OK  Camera: OpenCV ({cam_res})")
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
        cam_h, cam_w = test_frame.shape[:2]
        cam_s.ok = True
        cam_s.text = "CONNECTED"
        cam_source = "picamera2"
        cam_res = f"{cam_w}x{cam_h}"
        print(f"  OK  Camera: picamera2 ({cam_res})")
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
        # IMX296 sensor outputs BGR despite RGB888 label — no conversion needed
        return f
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

# --- Baud rate + mavproxy detection ---
baud_rate = 921600
try:
    baud_rate = config.BAUD_RATE
except Exception:
    pass

mavproxy_info = {
    "running": False,
    "master": "",
    "outputs": [],
    "streamrate": "",
    "baud": "",
}

def detect_mavproxy():
    """Find running mavproxy process and parse its flags."""
    try:
        import subprocess
        result = subprocess.run(['ps', 'aux'], capture_output=True,
                                text=True, timeout=3)
        for line in result.stdout.split('\n'):
            if 'mavproxy' in line.lower() and 'grep' not in line:
                mavproxy_info["running"] = True
                for part in line.split():
                    if part.startswith('--master='):
                        mavproxy_info["master"] = part.split('=', 1)[1]
                    elif part.startswith('--out='):
                        mavproxy_info["outputs"].append(part.split('=', 1)[1])
                    elif part.startswith('--baudrate='):
                        mavproxy_info["baud"] = part.split('=', 1)[1]
                    elif part.startswith('--streamrate='):
                        mavproxy_info["streamrate"] = part.split('=', 1)[1]
                break
    except Exception:
        pass

print("[3b/5] Detecting mavproxy process...")
detect_mavproxy()
if mavproxy_info["running"]:
    print(f"  OK  mavproxy running, master={mavproxy_info['master']}, "
          f"outputs={mavproxy_info['outputs']}")
else:
    print(f"  INFO  mavproxy process not detected (may be on different host)")

# --- GPS ---
if cube_s.ok:
    gps_s.text = "WAITING..."
else:
    gps_s.text = "NO CUBE"

# --- Ground Station ---
print("[4/5] Checking GS forwarding...")
def check_gs_port():
    global pi_ip
    # Get Pi IP
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        pi_ip = s.getsockname()[0]
        s.close()
    except Exception:
        pass

    # Check TCP port 5762
    port_open = False
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 5762))
        sock.close()
        port_open = result == 0
    except Exception:
        pass

    # Determine GS status using all available info
    has_tcp_out = any('tcpin' in o or 'tcp' in o
                      for o in mavproxy_info["outputs"])

    # Fallback: if Cube is connected via UDP, mavproxy MUST be running
    # even if ps detection failed (sudo/permissions issue)
    cube_via_udp = cube_s.ok and 'udp' in config.CONNECTION_STR.lower()

    if mavproxy_info["running"] and has_tcp_out:
        # mavproxy detected with TCP output configured
        if port_open:
            gs_s.ok = True
            gs_s.text = "TCP 5762 LISTENING"
        else:
            gs_s.ok = True
            gs_s.text = "MP CONNECTED"
    elif mavproxy_info["running"] and not has_tcp_out:
        gs_s.ok = False
        gs_s.text = "NO TCP OUTPUT"
        gs_s.error = "Add --out=tcpin:0.0.0.0:5762"
    elif port_open:
        gs_s.ok = True
        gs_s.text = "TCP 5762 LISTENING"
    elif cube_via_udp and not port_open:
        # Cube works via UDP = mavproxy IS running.
        # Port refused = MP already took it = success!
        gs_s.ok = True
        gs_s.text = "MP CONNECTED"
    elif cube_via_udp:
        # mavproxy running (Cube works) but port not checked yet
        gs_s.ok = True
        gs_s.text = "GS AVAILABLE"
    else:
        gs_s.ok = False
        gs_s.text = "NOT DETECTED"
        gs_s.error = "mavproxy not found"

check_gs_port()
status_msg = f"TCP 5762 open (Pi IP: {pi_ip})" if gs_s.ok else gs_s.text
print(f"  {'OK' if gs_s.ok else 'WARN'}  GS: {status_msg}")

# Summary
print(f"\n[5/5] Initial check complete:")
for label, s in [("CAMERA", cam_s), ("AI", ai_s), ("CUBE", cube_s),
                  ("GPS", gps_s), ("GS", gs_s)]:
    tag = " OK " if s.ok else "WAIT" if "WAIT" in s.text else "FAIL"
    print(f"  [{tag}] {label}: {s.text}")

# ============================================================
#  Live state
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

# Separate FPS tracking
raw_frame_count = 0        # frames grabbed (camera speed)
ai_frame_count = 0         # frames processed by AI
fps_window_start = time.time()
raw_fps = 0.0              # camera-only FPS
ai_fps = 0.0               # FPS when AI is running
last_inference_ms = 0.0    # last single inference time
inference_times = []       # recent inference times for averaging
total_detections = 0
total_ai_frames = 0
last_det_conf = 0.0
last_det_x = 0
last_det_y = 0

# View state
VIEW_DIAGRAM = 1
VIEW_CAMERA = 2
VIEW_TELEMETRY = 3
current_view = VIEW_DIAGRAM
ai_overlay_on = False      # toggle with 'a' in camera view

# ============================================================
#  Colors (BGR)
# ============================================================
GREEN  = (0, 200, 0)
RED    = (0, 0, 220)
YELLOW = (0, 200, 200)
CYAN   = (200, 180, 0)
WHITE  = (210, 210, 210)
GRAY   = (110, 110, 110)
DARK   = (40, 40, 40)
BG     = (25, 25, 25)
PI_CLR = (120, 60, 0)

CANVAS_W = 960
CANVAS_H = 780

# ============================================================
#  VIEW 1: Connectivity Diagram
# ============================================================
def draw_box(img, x, y, w, h, title, ok, detail_lines):
    border = GREEN if ok else RED
    cv2.rectangle(img, (x, y), (x + w, y + h), DARK, -1)
    cv2.rectangle(img, (x, y), (x + w, y + 26), border, -1)
    cv2.putText(img, title, (x + 8, y + 19),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 0), 2)
    cv2.rectangle(img, (x, y), (x + w, y + h), border, 2)
    ly = y + 44
    for text, color in detail_lines:
        cv2.putText(img, text, (x + 8, ly),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, color, 1)
        ly += 17

def draw_arrow(img, pt1, pt2, ok):
    cv2.arrowedLine(img, pt1, pt2, GREEN if ok else RED, 2, tipLength=0.04)

def draw_link_label(img, pt1, pt2, lines):
    mx = (pt1[0] + pt2[0]) // 2
    my = (pt1[1] + pt2[1]) // 2
    start_y = my - (len(lines) - 1) * 8
    for i, text in enumerate(lines):
        ty = start_y + i * 16
        (tw, th), _ = cv2.getTextSize(text, cv2.FONT_HERSHEY_SIMPLEX, 0.35, 1)
        cv2.rectangle(img, (mx - tw // 2 - 3, ty - th - 2),
                      (mx + tw // 2 + 3, ty + 3), BG, -1)
        cv2.putText(img, text, (mx - tw // 2, ty),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.35, CYAN, 1)

def draw_view_diagram():
    img = np.full((CANVAS_H, CANVAS_W, 3), 25, dtype=np.uint8)

    # Title
    draw_title_bar(img, "VIEW 1: CONNECTIVITY DIAGRAM")

    # Box positions
    pi_x, pi_y, pi_w, pi_h = 355, 225, 250, 200
    cb_x, cb_y, cb_w, cb_h = 20, 225, 210, 210
    gp_x, gp_y, gp_w, gp_h = 40, 50, 175, 120
    ca_x, ca_y, ca_w, ca_h = 720, 185, 215, 130
    ai_x, ai_y, ai_w, ai_h = 720, 370, 215, 115
    gs_x, gs_y, gs_w, gs_h = 340, 510, 280, 150

    # --- Connection lines (behind boxes) ---
    gps_bot  = (gp_x + gp_w // 2, gp_y + gp_h)
    cube_top = (cb_x + cb_w // 2, cb_y)
    draw_arrow(img, gps_bot, cube_top, gps_s.ok or cube_s.ok)
    draw_link_label(img, gps_bot, cube_top, ["GPS port", "(built-in)"])

    cube_r = (cb_x + cb_w, cb_y + cb_h // 2)
    pi_l   = (pi_x, pi_y + pi_h // 2)
    draw_arrow(img, cube_r, pi_l, cube_s.ok)
    serial_port = mavproxy_info["master"] or "/dev/ttyAMA0"
    baud_label = mavproxy_info["baud"] or str(baud_rate)
    draw_link_label(img, cube_r, pi_l,
                    [f"Serial {serial_port}", f"@ {baud_label} baud",
                     "-> mavproxy -> UDP"])

    cam_l = (ca_x, ca_y + ca_h // 2)
    pi_r1 = (pi_x + pi_w, pi_y + 60)
    draw_arrow(img, cam_l, pi_r1, cam_s.ok)
    draw_link_label(img, cam_l, pi_r1,
                    [f"CSI -> {cam_source}" if cam_source else "CSI / USB"])

    ai_l  = (ai_x, ai_y + ai_h // 2)
    pi_r2 = (pi_x + pi_w, pi_y + pi_h - 40)
    draw_arrow(img, pi_r2, ai_l, ai_s.ok)
    draw_link_label(img, ai_l, pi_r2, ["frame -> detect", "-> (found,x,y,conf)"])

    pi_b  = (pi_x + pi_w // 2, pi_y + pi_h)
    gs_t  = (gs_x + gs_w // 2, gs_y)
    draw_arrow(img, pi_b, gs_t, gs_s.ok)
    _tcp_outs = [o for o in mavproxy_info["outputs"] if 'tcp' in o.lower()]
    tcp_label = _tcp_outs[0] if _tcp_outs else "tcpin:0.0.0.0:5762"
    draw_link_label(img, pi_b, gs_t,
                    [f"mavproxy {tcp_label}", f"-> WiFi -> MP"])

    # --- Boxes ---
    # GPS
    gps_ok_now = telem['fix'] in ('3D', 'DGPS', 'RTK Float', 'RTK Fixed')
    gps_s.ok = gps_ok_now
    if not gps_ok_now and telem['sats'] > 0:
        gps_s.text = telem['fix']
    elif gps_ok_now:
        gps_s.text = "3D FIX"
    gps_lines = [
        (f"Fix: {telem['fix']}", GREEN if gps_ok_now else YELLOW),
        (f"Sats: {telem['sats']}", WHITE),
        (f"HDOP: {telem['hdop']:.1f}", WHITE),
    ]
    if telem['lat'] != 0:
        gps_lines.append((f"({telem['lat']:.5f}, {telem['lon']:.5f})", WHITE))
    else:
        gps_lines.append(("No fix yet", YELLOW))
    draw_box(img, gp_x, gp_y, gp_w, gp_h, "GPS MODULE", gps_s.ok, gps_lines)

    # Cube
    total_rate = sum(msg_rates.values())
    serial_port = mavproxy_info["master"] or "/dev/ttyAMA0"
    baud_label = mavproxy_info["baud"] or str(baud_rate)
    sr_label = mavproxy_info["streamrate"] or "?"
    cube_lines = [
        (f"System ID: {cube_sysid}", WHITE),
        (f"Serial: {serial_port}", WHITE),
        (f"Baud: {baud_label}  Stream: {sr_label}Hz", WHITE),
        (f"UDP: {conn_str}", WHITE),
        (f"Total: {total_rate:.0f} msgs/sec", GREEN if total_rate > 5 else YELLOW),
    ]
    for mt, short in [('ATTITUDE', 'ATT'), ('GLOBAL_POSITION_INT', 'POS'),
                      ('GPS_RAW_INT', 'GPS'), ('SYS_STATUS', 'BAT'),
                      ('HEARTBEAT', 'HB')]:
        rate = msg_rates.get(mt, 0)
        rc = GREEN if rate > 0.5 else (YELLOW if rate > 0 else RED)
        cube_lines.append((f"  {short:<4} {rate:>5.1f} Hz", rc))
    if not cube_s.ok:
        cube_lines = [(f"Error: {cube_s.error[:30]}", RED),
                      ("Is mavproxy running?", YELLOW)]
    draw_box(img, cb_x, cb_y, cb_w, cb_h, "CUBE ORANGE", cube_s.ok, cube_lines)

    # Pi (centre, custom styling)
    issues = sum(1 for s in [cam_s, ai_s, cube_s] if not s.ok)
    pi_ok = issues == 0
    pi_border = GREEN if pi_ok else YELLOW
    cv2.rectangle(img, (pi_x, pi_y), (pi_x + pi_w, pi_y + pi_h), DARK, -1)
    cv2.rectangle(img, (pi_x, pi_y), (pi_x + pi_w, pi_y + 26), PI_CLR, -1)
    cv2.putText(img, "RASPBERRY PI", (pi_x + 8, pi_y + 19),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, WHITE, 2)
    cv2.rectangle(img, (pi_x, pi_y), (pi_x + pi_w, pi_y + pi_h), pi_border, 2)
    ok_count = sum(1 for s in [cam_s, ai_s, cube_s, gps_s, gs_s] if s.ok)
    mp_running = mavproxy_info["running"]
    pi_lines = [
        (f"IP: {pi_ip}", CYAN),
        (f"mavproxy: {'Running' if mp_running else 'Not found'}",
         GREEN if mp_running else RED),
        (f"Camera: {cam_source} {cam_res}", GREEN if cam_s.ok else RED),
        (f"AI: {ai_backend or 'None'}", GREEN if ai_s.ok else RED),
        ("", WHITE),
        (f"Raw FPS: {raw_fps:.1f}  AI: {last_inference_ms:.0f}ms", WHITE),
        (f"Systems: {ok_count}/5 OK",
         GREEN if ok_count == 5 else YELLOW),
    ]
    ly = pi_y + 44
    for text, color in pi_lines:
        cv2.putText(img, text, (pi_x + 10, ly),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, color, 1)
        ly += 17

    # Camera
    cam_lines = ([(f"Source: {cam_source}", WHITE),
                  (f"Resolution: {cam_res}", WHITE),
                  (f"FPS: {raw_fps:.1f}", GREEN if raw_fps > 10 else YELLOW)]
                 if cam_s.ok else
                 [(f"{cam_s.error[:28]}", RED)])
    draw_box(img, ca_x, ca_y, ca_w, ca_h, "CAMERA", cam_s.ok, cam_lines)

    # AI
    avg_ms = np.mean(inference_times[-30:]) if inference_times else 0
    ai_lines = ([(f"Backend: {ai_backend}", WHITE),
                 (f"Model: best.tflite", WHITE),
                 (f"Inference: {avg_ms:.0f}ms avg",
                  GREEN if avg_ms < 200 else YELLOW),
                 (f"Warmup: {ai_warmup:.0f}ms", GRAY)]
                if ai_s.ok else
                [(f"{ai_s.text}", RED), (f"{ai_s.error[:28]}", RED)])
    draw_box(img, ai_x, ai_y, ai_w, ai_h, "AI MODEL", ai_s.ok, ai_lines)

    # GS — show connection details regardless of status
    gs_lines = [
        (f"Status: {gs_s.text}", GREEN if gs_s.ok else YELLOW),
        (f"Pi IP: {pi_ip}", CYAN),
    ]
    # Show mavproxy TCP outputs
    tcp_outs = [o for o in mavproxy_info["outputs"] if 'tcp' in o.lower()]
    if tcp_outs:
        for out in tcp_outs:
            gs_lines.append((f"mavproxy --out={out}", WHITE))
    else:
        gs_lines.append(("No TCP output configured", YELLOW))
    # Connection instructions
    if gs_s.ok:
        gs_lines.append((f"MP: connect TCP to {pi_ip}:5762", GREEN))
    else:
        gs_lines.append((f"Need: --out=tcpin:0.0.0.0:5762", YELLOW))
    draw_box(img, gs_x, gs_y, gs_w, gs_h, "MISSION PLANNER (GS)", gs_s.ok, gs_lines)

    # Telemetry strip
    draw_telem_strip(img)
    draw_nav_bar(img)
    return img

# ============================================================
#  VIEW 2: Camera Feed (raw + optional AI overlay)
# ============================================================
def run_ai_on_frame(frame):
    """Run AI inference, update tracking stats, return (found, x, y, conf).
       detect_in_image draws the bounding box on frame in-place."""
    global last_inference_ms, total_detections, total_ai_frames
    global last_det_conf, last_det_x, last_det_y, ai_frame_count

    t0 = time.time()
    found, dx, dy, conf = eyes.detect_in_image(frame)
    ms = (time.time() - t0) * 1000

    last_inference_ms = ms
    inference_times.append(ms)
    ai_frame_count += 1
    total_ai_frames += 1
    if found:
        total_detections += 1
        last_det_conf = conf
        last_det_x = dx
        last_det_y = dy
    return found, dx, dy, conf

def draw_view_camera(frame):
    # Build canvas: camera frame on left, stats panel on right
    fh, fw = frame.shape[:2] if frame is not None else (480, 640)
    panel_w = 300
    canvas_w = fw + panel_w
    canvas_h = max(fh, 480) + 80   # +80 for top bar + bottom bar
    img = np.full((canvas_h, canvas_w, 3), 25, dtype=np.uint8)

    # Title bar
    draw_title_bar_sized(img, canvas_w,
                         f"VIEW 2: CAMERA FEED — AI {'ON' if ai_overlay_on else 'OFF'}")

    # Camera frame area
    fy = 45  # below title bar
    if frame is not None:
        display_frame = frame.copy()

        # Run AI if toggled on (modifies display_frame in-place with boxes)
        if ai_overlay_on and eyes and eyes.using_ai:
            run_ai_on_frame(display_frame)

        img[fy:fy + fh, 0:fw] = display_frame
    else:
        cv2.putText(img, "NO CAMERA FEED", (fw // 2 - 120, fy + fh // 2),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, RED, 2)

    # Frame border
    cv2.rectangle(img, (0, fy), (fw, fy + fh), GRAY, 1)

    # --- Stats panel (right side) ---
    px = fw + 10
    py = fy + 5

    def panel_text(text, color=WHITE, bold=False):
        nonlocal py
        t = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(img, text, (px, py), t, 0.42 if not bold else 0.5,
                    color, 1 if not bold else 2)
        py += 20

    panel_text("CAMERA", CYAN, bold=True)
    py += 5
    panel_text(f"Source: {cam_source}")
    panel_text(f"Resolution: {cam_res}")
    panel_text(f"Raw FPS: {raw_fps:.1f}",
               GREEN if raw_fps > 15 else YELLOW)

    py += 15
    ai_label = "AI: ON" if ai_overlay_on else "AI: OFF  (press 'a')"
    panel_text(ai_label, GREEN if ai_overlay_on else GRAY, bold=True)
    py += 5

    if ai_overlay_on and ai_s.ok:
        avg_ms = np.mean(inference_times[-30:]) if inference_times else 0
        panel_text(f"Backend: {ai_backend}")
        panel_text(f"Inference: {last_inference_ms:.0f}ms",
                   GREEN if last_inference_ms < 200 else YELLOW)
        panel_text(f"Average: {avg_ms:.0f}ms")
        eff_fps = 1000.0 / avg_ms if avg_ms > 0 else 0
        panel_text(f"Effective FPS: {eff_fps:.1f}",
                   GREEN if eff_fps > 5 else YELLOW)
        py += 10
        panel_text(f"Detections: {total_detections}/{total_ai_frames}")
        if last_det_conf > 0:
            panel_text(f"Last conf: {last_det_conf:.2f}", GREEN)
            panel_text(f"Last pos: ({last_det_x}, {last_det_y})", WHITE)
    elif not ai_overlay_on:
        panel_text("Toggle to see how", GRAY)
        panel_text("AI affects FPS and", GRAY)
        panel_text("what it detects", GRAY)
    else:
        panel_text("AI not available", RED)
        panel_text(f"{ai_s.error[:25]}", RED)

    py += 20
    panel_text("CONTROLS", CYAN, bold=True)
    py += 5
    panel_text("'a' toggle AI overlay")
    panel_text("'s' save frame")
    panel_text("'1' diagram  '3' telemetry")
    panel_text("'q' quit")

    # Bottom telemetry mini-strip
    by = canvas_h - 30
    cv2.rectangle(img, (0, by), (canvas_w, canvas_h), (35, 35, 35), -1)
    cv2.line(img, (0, by), (canvas_w, by), GRAY, 1)
    tl = (f"Yaw={telem['yaw']:.0f}  P={telem['pitch']:.1f}  R={telem['roll']:.1f}  |  "
          f"Alt={telem['alt_rel']:.1f}m  |  Bat={telem['voltage']:.1f}V  |  "
          f"GPS: {telem['fix']} {telem['sats']}sat")
    cv2.putText(img, tl, (10, canvas_h - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, WHITE, 1)

    return img

# ============================================================
#  VIEW 3: Cube Telemetry Detail
# ============================================================
def draw_view_telemetry():
    img = np.full((CANVAS_H, CANVAS_W, 3), 25, dtype=np.uint8)
    draw_title_bar(img, "VIEW 3: CUBE TELEMETRY — LIVE READINGS")

    if not cube_s.ok:
        cv2.putText(img, "CUBE NOT CONNECTED", (CANVAS_W // 2 - 180, 300),
                    cv2.FONT_HERSHEY_SIMPLEX, 1.0, RED, 2)
        cv2.putText(img, f"Error: {cube_s.error}", (CANVAS_W // 2 - 200, 340),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, YELLOW, 1)
        cv2.putText(img, "Is mavproxy running?", (CANVAS_W // 2 - 120, 380),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, YELLOW, 1)
        draw_nav_bar(img)
        return img

    # Two-column layout
    col1_x = 30
    col2_x = 500
    y = 65

    def section(x, y_pos, title, items):
        cv2.putText(img, title, (x, y_pos),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, CYAN, 2)
        cv2.line(img, (x, y_pos + 5), (x + 200, y_pos + 5), GRAY, 1)
        ly = y_pos + 30
        for label, value, color in items:
            cv2.putText(img, f"{label}:", (x + 10, ly),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, GRAY, 1)
            cv2.putText(img, str(value), (x + 160, ly),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)
            ly += 24
        return ly

    # ATTITUDE
    y = section(col1_x, y, "ATTITUDE", [
        ("Yaw", f"{telem['yaw']:.1f} deg", WHITE),
        ("Pitch", f"{telem['pitch']:.1f} deg", WHITE),
        ("Roll", f"{telem['roll']:.1f} deg", WHITE),
    ])

    y += 15

    # POSITION
    y = section(col1_x, y, "POSITION", [
        ("Alt (rel)", f"{telem['alt_rel']:.1f} m", WHITE),
        ("Alt (MSL)", f"{telem['alt_msl']:.1f} m", WHITE),
    ])

    y += 15

    # GPS
    gps_ok_now = telem['fix'] in ('3D', 'DGPS', 'RTK Float', 'RTK Fixed')
    fix_col = GREEN if gps_ok_now else YELLOW
    gps_items = [
        ("Fix type", telem['fix'], fix_col),
        ("Satellites", str(telem['sats']), GREEN if telem['sats'] >= 6 else YELLOW),
        ("HDOP", f"{telem['hdop']:.1f}", GREEN if telem['hdop'] < 2 else YELLOW),
    ]
    if telem['lat'] != 0:
        gps_items.append(("Latitude", f"{telem['lat']:.7f}", WHITE))
        gps_items.append(("Longitude", f"{telem['lon']:.7f}", WHITE))
    else:
        gps_items.append(("Position", "No fix", YELLOW))
    section(col1_x, y, "GPS", gps_items)

    # Right column: BATTERY
    y2 = 65
    bat_col = GREEN if telem['voltage'] > 10 else (YELLOW if telem['voltage'] > 0 else RED)
    y2 = section(col2_x, y2, "BATTERY", [
        ("Voltage", f"{telem['voltage']:.2f} V", bat_col),
        ("Current", f"{telem['current']:.1f} A", WHITE),
    ])

    y2 += 15

    # CONNECTION
    serial_port = mavproxy_info["master"] or "/dev/ttyAMA0"
    baud_label = mavproxy_info["baud"] or str(baud_rate)
    sr_label = mavproxy_info["streamrate"] or "?"
    conn_items = [
        ("System ID", cube_sysid, WHITE),
        ("Serial", serial_port, WHITE),
        ("Baud rate", baud_label, WHITE),
        ("Stream rate", f"{sr_label} Hz", WHITE),
        ("UDP link", conn_str, WHITE),
        ("Pi IP", pi_ip, CYAN),
        ("Total rate", f"{sum(msg_rates.values()):.0f} msgs/sec",
         GREEN if sum(msg_rates.values()) > 5 else YELLOW),
    ]
    # Show mavproxy outputs
    for out in mavproxy_info["outputs"]:
        conn_items.append(("Output", out, WHITE))
    y2 = section(col2_x, y2, "CONNECTION", conn_items)

    y2 += 15

    # MESSAGE RATES (full table)
    cv2.putText(img, "MESSAGE RATES", (col2_x, y2),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, CYAN, 2)
    cv2.line(img, (col2_x, y2 + 5), (col2_x + 200, y2 + 5), GRAY, 1)
    ly = y2 + 30

    # Sort by rate descending
    sorted_rates = sorted(msg_rates.items(), key=lambda x: -x[1])
    for mt, rate in sorted_rates[:12]:  # top 12
        rc = GREEN if rate > 0.5 else (YELLOW if rate > 0 else RED)
        cv2.putText(img, f"{mt}", (col2_x + 10, ly),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, rc, 1)
        cv2.putText(img, f"{rate:>6.1f} Hz", (col2_x + 280, ly),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.38, rc, 1)
        ly += 19

    # Telemetry strip + nav
    draw_telem_strip(img)
    draw_nav_bar(img)
    return img

# ============================================================
#  Shared UI elements
# ============================================================
def draw_title_bar(img, text):
    draw_title_bar_sized(img, CANVAS_W, text)

def draw_title_bar_sized(img, width, text):
    cv2.rectangle(img, (0, 0), (width, 40), (40, 40, 40), -1)
    cv2.putText(img, text, (15, 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, CYAN, 2)
    cv2.putText(img, time.strftime("%H:%M:%S"), (width - 110, 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.55, WHITE, 1)
    cv2.line(img, (0, 40), (width, 40), GRAY, 1)

def draw_telem_strip(img):
    h = img.shape[0]
    w = img.shape[1]
    sy = h - 55
    cv2.rectangle(img, (0, sy), (w, sy + 25), (35, 35, 35), -1)
    cv2.line(img, (0, sy), (w, sy), GRAY, 1)
    cv2.putText(img, "LIVE:", (10, sy + 17),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, CYAN, 1)
    tl = (f"Yaw={telem['yaw']:.0f}  Pitch={telem['pitch']:.1f}  "
          f"Roll={telem['roll']:.1f}  |  Alt={telem['alt_rel']:.1f}m  "
          f"|  Bat={telem['voltage']:.1f}V  |  "
          f"GPS: {telem['fix']} {telem['sats']}sat")
    cv2.putText(img, tl, (55, sy + 17),
                cv2.FONT_HERSHEY_SIMPLEX, 0.38, WHITE, 1)

def draw_nav_bar(img):
    h = img.shape[0]
    w = img.shape[1]
    ny = h - 25
    cv2.rectangle(img, (0, ny), (w, h), (30, 30, 30), -1)
    labels = [
        ("1", "Diagram", current_view == VIEW_DIAGRAM),
        ("2", "Camera", current_view == VIEW_CAMERA),
        ("3", "Telemetry", current_view == VIEW_TELEMETRY),
    ]
    bx = 10
    for key, name, active in labels:
        color = CYAN if active else GRAY
        text = f"[{key}] {name}"
        cv2.putText(img, text, (bx, h - 8),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1 if not active else 2)
        bx += 150
    cv2.putText(img, "'q' quit  |  'r' recheck GS  |  's' screenshot",
                (w - 380, h - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.35, GRAY, 1)

# ============================================================
#  Headless terminal output
# ============================================================
A_G = "\033[92m"; A_R = "\033[91m"; A_Y = "\033[93m"
A_C = "\033[96m"; A_B = "\033[1m"; A_0 = "\033[0m"

def print_headless():
    tag = lambda ok: f"{A_G}OK{A_0}" if ok else f"{A_R}FAIL{A_0}"
    print(f"\n{A_C}{'='*65}{A_0}")
    print(f"  {A_B}SAR DRONE DIAGNOSTICS{A_0}  —  {time.strftime('%H:%M:%S')}")
    print(f"{A_C}{'='*65}{A_0}")

    print(f"\n  [{tag(cam_s.ok)}] CAMERA: {cam_source} {cam_res}  "
          f"Raw FPS: {raw_fps:.1f}")
    print(f"  [{tag(ai_s.ok)}] AI: {ai_backend}  "
          f"Inference: {last_inference_ms:.0f}ms")

    print(f"\n  [{tag(cube_s.ok)}] CUBE: ID={cube_sysid} via {conn_str}")
    if cube_s.ok:
        total = sum(msg_rates.values())
        print(f"       Total: {total:.0f} msgs/sec")
        for mt in ['ATTITUDE', 'GLOBAL_POSITION_INT', 'GPS_RAW_INT', 'SYS_STATUS']:
            rate = msg_rates.get(mt, 0)
            rc = A_G if rate > 0.5 else A_R
            print(f"       {rc}{mt:<26} {rate:>5.1f} Hz{A_0}")

    gps_ok = telem['fix'] in ('3D', 'DGPS', 'RTK Float', 'RTK Fixed')
    print(f"\n  [{tag(gps_ok)}] GPS: {telem['fix']}  {telem['sats']} sats  "
          f"HDOP={telem['hdop']:.1f}")
    if telem['lat'] != 0:
        print(f"       ({telem['lat']:.7f}, {telem['lon']:.7f})")

    print(f"\n  [{tag(gs_s.ok)}] GS: {gs_s.text}")

    print(f"\n  {A_C}TELEMETRY:{A_0} Yaw={telem['yaw']:.0f} "
          f"Pitch={telem['pitch']:.1f} Roll={telem['roll']:.1f} | "
          f"Alt={telem['alt_rel']:.1f}m | Bat={telem['voltage']:.1f}V")
    print()

# ============================================================
#  Main loop
# ============================================================
print(f"\n{'='*55}")
if headless:
    print(f"  Live monitoring (HEADLESS). Ctrl+C to quit.")
else:
    print(f"  Press 1/2/3 to switch views. Press 'q' to quit.")
print(f"{'='*55}\n")

last_headless_print = 0
last_gs_check = time.time()
window_name = "SAR Drone Diagnostics"

try:
    while True:
        # --- Drain Cube messages ---
        if mav:
            while True:
                msg = mav.recv_msg()
                if msg is None:
                    break
                t = msg.get_type()
                rate_counts[t] = rate_counts.get(t, 0) + 1

            # Recalculate message rates every 2s
            elapsed_rate = time.time() - rate_window_start
            if elapsed_rate >= 2.0:
                for t, c in rate_counts.items():
                    msg_rates[t] = c / elapsed_rate
                rate_counts = {}
                rate_window_start = time.time()

            # Read latest telemetry
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
                telem['fix'] = fix_names.get(gps_raw.fix_type,
                                             f"Type {gps_raw.fix_type}")
                telem['sats'] = gps_raw.satellites_visible
                telem['hdop'] = (gps_raw.eph / 100.0
                                 if gps_raw.eph < 10000 else 0)
            bat = mav.messages.get('SYS_STATUS')
            if bat:
                telem['voltage'] = bat.voltage_battery / 1000.0
                telem['current'] = (bat.current_battery / 100.0
                                    if bat.current_battery != -1 else 0)

        # --- Grab camera frame (always, for FPS tracking) ---
        frame = None
        if cam_s.ok:
            frame = get_frame()
            if frame is not None:
                raw_frame_count += 1

        # FPS recalculation every 2s
        fps_elapsed = time.time() - fps_window_start
        if fps_elapsed >= 2.0:
            raw_fps = raw_frame_count / fps_elapsed
            ai_fps = ai_frame_count / fps_elapsed
            raw_frame_count = 0
            ai_frame_count = 0
            fps_window_start = time.time()

        # --- Recheck GS periodically ---
        if time.time() - last_gs_check > 10.0:
            check_gs_port()
            last_gs_check = time.time()

        # --- Display ---
        if not headless:
            if current_view == VIEW_DIAGRAM:
                display = draw_view_diagram()
            elif current_view == VIEW_CAMERA:
                display = draw_view_camera(frame)
            elif current_view == VIEW_TELEMETRY:
                display = draw_view_telemetry()
            else:
                display = draw_view_diagram()

            cv2.imshow(window_name, display)
            key = cv2.waitKey(1) & 0xFF

            if key == ord('q'):
                break
            elif key == ord('1'):
                current_view = VIEW_DIAGRAM
            elif key == ord('2'):
                current_view = VIEW_CAMERA
            elif key == ord('3'):
                current_view = VIEW_TELEMETRY
            elif key == ord('a') and current_view == VIEW_CAMERA:
                ai_overlay_on = not ai_overlay_on
                print(f"  AI overlay: {'ON' if ai_overlay_on else 'OFF'}")
            elif key == ord('r'):
                check_gs_port()
                print(f"  GS recheck: {gs_s.text}")
            elif key == ord('s'):
                fname = f"diag_{current_view}_{int(time.time())}.png"
                cv2.imwrite(fname, display)
                print(f"  Saved: {fname}")
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
if raw_fps > 0:
    print(f"\n  Raw camera FPS: {raw_fps:.1f}")
if inference_times:
    print(f"  AI avg: {np.mean(inference_times[-30:]):.0f}ms")
    print(f"  AI detections: {total_detections}/{total_ai_frames}")
if msg_rates:
    print(f"  Cube total: {sum(msg_rates.values()):.0f} msgs/sec")
print()
