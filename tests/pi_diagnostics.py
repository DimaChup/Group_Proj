#!/usr/bin/env python3
"""
SAR Drone System Diagnostics — Visual connectivity and health dashboard.

One script to check EVERYTHING:
  - Camera connected? What source? FPS?
  - AI model loaded? What backend? Inference speed?
  - Cube Orange connected? What messages? At what rate?
  - GPS fix? Satellites? Position?
  - Ground Station reachable? TCP port open?

Shows HOW each connection works (the signal path) and LIVE data rates.

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
#  Subsystem status tracking
# ============================================================
class Subsystem:
    def __init__(self, name, path=""):
        self.name = name
        self.ok = False
        self.status = "CHECKING..."
        self.info = {}
        self.path = path
        self.error = ""

cam  = Subsystem("CAMERA")
ai   = Subsystem("AI MODEL")
cube = Subsystem("CUBE ORANGE")
gps  = Subsystem("GPS")
gs   = Subsystem("GROUND STATION",
                 "[Cube] -> Serial -> [mavproxy] -> TCP:5762 -> WiFi -> [Mission Planner]")

# ============================================================
#  Phase 1: Check each subsystem
# ============================================================
print("=" * 55)
print("  SAR DRONE SYSTEM DIAGNOSTICS")
print("=" * 55)

# --- Camera ---
print("\n[1/5] Checking camera...")
cap = None
picam = None

cap = cv2.VideoCapture(0)
if cap.isOpened():
    ret, test_frame = cap.read()
    if ret:
        h, w = test_frame.shape[:2]
        cam.ok = True
        cam.status = "CONNECTED"
        cam.info = {"source": "OpenCV", "res": f"{w}x{h}"}
        cam.path = "[USB/CSI Camera] -> cv2.VideoCapture -> BGR frames"
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
        cam.ok = True
        cam.status = "CONNECTED"
        cam.info = {"source": "picamera2", "res": f"{w}x{h}"}
        cam.path = "[Pi CSI Camera] -> picamera2 (RGB888) -> cvtColor -> BGR"
        print(f"  OK  Camera: picamera2 ({w}x{h})")
    except Exception as e:
        cam.status = "FAILED"
        cam.error = str(e)[:80]
        cam.path = "No camera backend available"
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
try:
    from vision import VisionSystem
    eyes = VisionSystem(camera_index=None, model_path="best.tflite")
    if eyes.using_ai:
        backend = "TFLite" if eyes._use_tflite_direct else "Ultralytics"
        ai.ok = True
        ai.status = "LOADED"
        ai.info = {"backend": backend, "model": "best.tflite"}
        if eyes._use_tflite_direct:
            ai.info["input"] = str(eyes._input_shape)
            ai.path = "[Frame] -> BGR2RGB -> Resize -> Float32/255 -> TFLite -> NMS"
        else:
            ai.path = "[Frame] -> Ultralytics YOLO engine -> Detection boxes"
        # Warmup inference
        t0 = time.time()
        eyes.detect_in_image(np.zeros((480, 640, 3), dtype=np.uint8))
        warmup = (time.time() - t0) * 1000
        ai.info["warmup_ms"] = f"{warmup:.0f}"
        print(f"  OK  AI: {backend} (warmup {warmup:.0f}ms)")
    else:
        ai.status = "NOT LOADED"
        ai.error = "No model file or no backend available"
        ai.path = "best.tflite not found or no TFLite/Ultralytics installed"
        print(f"  WARN  AI model not loaded")
except Exception as e:
    ai.status = "FAILED"
    ai.error = str(e)[:80]
    print(f"  FAIL  AI: {e}")

# --- Cube ---
print("[3/5] Checking Cube connection...")
mav = None
try:
    from pymavlink import mavutil
    import config
    conn_str = config.CONNECTION_STR
    cube.path = f"[Cube] -> Serial -> [mavproxy] -> UDP -> [{conn_str}]"

    mav = mavutil.mavlink_connection(conn_str)
    mav.wait_heartbeat(timeout=5)
    cube.ok = True
    cube.status = "CONNECTED"
    cube.info = {"sysid": str(mav.target_system), "conn": conn_str}

    # Request streams
    try:
        mav.mav.request_data_stream_send(
            mav.target_system, mav.target_component,
            mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1
        )
    except Exception:
        pass
    print(f"  OK  Cube: system {mav.target_system} via {conn_str}")
except Exception as e:
    cube.status = "FAILED"
    cube.error = str(e)[:80]
    if "udp" in cube.path.lower():
        cube.error += " | Is mavproxy running?"
    print(f"  FAIL  Cube: {e}")

# --- GPS (will update live, initial state from Cube) ---
gps.path = "[Cube GPS module] -> MAVLink GPS_RAW_INT + GLOBAL_POSITION_INT"
if cube.ok:
    gps.status = "WAITING FOR DATA..."
else:
    gps.status = "NO CUBE"
    gps.error = "Cube not connected — cannot read GPS"

# --- Ground Station (check TCP port) ---
print("[4/5] Checking GS forwarding port...")
def check_gs_port():
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 5762))
        sock.close()
        if result == 0:
            gs.ok = True
            gs.status = "PORT OPEN"
            gs.info["port"] = "5762"
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                s.connect(("8.8.8.8", 80))
                gs.info["pi_ip"] = s.getsockname()[0]
                s.close()
            except Exception:
                gs.info["pi_ip"] = "unknown"
            return True
        else:
            gs.ok = False
            gs.status = "PORT CLOSED"
            gs.error = "Add --out=tcpin:0.0.0.0:5762 to mavproxy"
            return False
    except Exception as e:
        gs.ok = False
        gs.status = "CHECK FAILED"
        gs.error = str(e)[:80]
        return False

check_gs_port()
if gs.ok:
    print(f"  OK  GS: TCP 5762 open (Pi IP: {gs.info.get('pi_ip', '?')})")
else:
    print(f"  WARN  GS: {gs.status} — {gs.error}")

# Summary
print(f"\n[5/5] Initial check complete:")
systems = [cam, ai, cube, gps, gs]
for s in systems:
    tag = " OK " if s.ok else "WARN" if "WAIT" in s.status else "FAIL"
    print(f"  [{tag}] {s.name}: {s.status}")

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

msg_rates = {}       # message_type -> Hz
rate_counts = {}     # counts in current window
rate_window_start = time.time()

frame_count = 0
frame_start_time = time.time()
camera_fps = 0.0
inference_times = []

# ============================================================
#  Dashboard drawing (OpenCV)
# ============================================================
# Colors (BGR)
C_GREEN  = (0, 200, 0)
C_RED    = (0, 0, 220)
C_YELLOW = (0, 220, 220)
C_CYAN   = (220, 200, 0)
C_WHITE  = (220, 220, 220)
C_GRAY   = (120, 120, 120)
C_DARK   = (40, 40, 40)

DASH_W = 820
DASH_H = 720

def dot(img, x, y, ok):
    cv2.circle(img, (x, y), 8, C_GREEN if ok else C_RED, -1)

def draw_section(img, y, height, sub, lines):
    """Draw one subsystem section. lines = list of (text, color) tuples."""
    cv2.rectangle(img, (10, y), (DASH_W - 10, y + height), C_DARK, -1)
    col = C_GREEN if sub.ok else C_RED
    dot(img, 30, y + 20, sub.ok)
    cv2.putText(img, f"{sub.name}: {sub.status}", (50, y + 25),
                cv2.FONT_HERSHEY_SIMPLEX, 0.6, col, 2)
    ly = y + 50
    for text, color in lines:
        cv2.putText(img, text, (50, ly),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.42, color, 1)
        ly += 20
    # Connection path at bottom
    cv2.putText(img, sub.path, (50, y + height - 8),
                cv2.FONT_HERSHEY_SIMPLEX, 0.35, C_CYAN, 1)
    return y + height + 8

def draw_dashboard():
    img = np.full((DASH_H, DASH_W, 3), 25, dtype=np.uint8)
    y = 5

    # Title bar
    cv2.rectangle(img, (10, y), (DASH_W - 10, y + 40), (50, 50, 50), -1)
    cv2.putText(img, "SAR DRONE SYSTEM DIAGNOSTICS", (20, y + 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.75, C_CYAN, 2)
    cv2.putText(img, time.strftime("%H:%M:%S"), (DASH_W - 140, y + 28),
                cv2.FONT_HERSHEY_SIMPLEX, 0.65, C_WHITE, 1)
    y += 52

    # --- Camera ---
    cam_lines = []
    if cam.ok:
        cam_lines.append((f"Source: {cam.info.get('source','')}   |   "
                          f"Resolution: {cam.info.get('res','')}   |   "
                          f"FPS: {camera_fps:.1f}", C_WHITE))
    else:
        cam_lines.append((f"Error: {cam.error}", C_RED))
    y = draw_section(img, y, 70, cam, cam_lines)

    # --- AI ---
    ai_lines = []
    if ai.ok:
        avg_ms = np.mean(inference_times[-30:]) if inference_times else 0
        ai_lines.append((f"Backend: {ai.info.get('backend','')}   |   "
                         f"Inference: {avg_ms:.0f}ms avg   |   "
                         f"Warmup: {ai.info.get('warmup_ms','')}ms", C_WHITE))
    else:
        ai_lines.append((f"Error: {ai.error}", C_RED))
    y = draw_section(img, y, 70, ai, ai_lines)

    # --- Cube (larger section with message rates) ---
    cube_lines = []
    if cube.ok:
        cube_lines.append((f"System ID: {cube.info.get('sysid','')}   |   "
                           f"Connection: {cube.info.get('conn','')}", C_WHITE))
        cube_lines.append(("", C_WHITE))  # spacer
        # Message rate table
        tracked = [
            ('HEARTBEAT',          ''),
            ('ATTITUDE',           f"Yaw={telem['yaw']:.0f}  Pitch={telem['pitch']:.1f}  Roll={telem['roll']:.1f}"),
            ('GLOBAL_POSITION_INT', f"Alt={telem['alt_rel']:.1f}m rel   ({telem['lat']:.5f}, {telem['lon']:.5f})"),
            ('GPS_RAW_INT',        f"{telem['fix']}  {telem['sats']} sats  HDOP={telem['hdop']:.1f}"),
            ('SYS_STATUS',         f"Bat={telem['voltage']:.1f}V  {telem['current']:.1f}A"),
        ]
        for msg_type, detail in tracked:
            rate = msg_rates.get(msg_type, 0)
            rate_col = C_GREEN if rate > 0.5 else (C_YELLOW if rate > 0 else C_RED)
            line = f"  {msg_type:<26} {rate:>5.1f} Hz    {detail}"
            cube_lines.append((line, rate_col))
    else:
        cube_lines.append((f"Error: {cube.error}", C_RED))
        cube_lines.append(("Is mavproxy running? Check terminal 1.", C_YELLOW))
    cube_height = 70 + len(cube_lines) * 20
    y = draw_section(img, y, cube_height, cube, cube_lines)

    # --- GPS ---
    gps_ok = telem['fix'] in ('3D', 'DGPS', 'RTK Float', 'RTK Fixed')
    if gps_ok:
        gps.ok = True
        gps.status = f"3D FIX  ({telem['sats']} sats)"
    elif telem['sats'] > 0:
        gps.ok = False
        gps.status = f"{telem['fix']}  ({telem['sats']} sats)"
    elif cube.ok:
        gps.ok = False
        gps.status = telem['fix'] if telem['fix'] != '---' else "WAITING..."

    gps_lines = []
    if telem['lat'] != 0:
        gps_lines.append((f"Position: ({telem['lat']:.7f}, {telem['lon']:.7f})   "
                          f"HDOP: {telem['hdop']:.1f}   Alt MSL: {telem['alt_msl']:.1f}m", C_WHITE))
    else:
        gps_lines.append(("No position fix  —  take drone outside, antenna facing UP", C_YELLOW))
    y = draw_section(img, y, 70, gps, gps_lines)

    # --- Ground Station ---
    gs_lines = []
    if gs.ok:
        ip = gs.info.get('pi_ip', '?')
        gs_lines.append((f"TCP port 5762 open   |   Pi IP: {ip}   |   "
                         f"In MP: connect TCP to {ip}:5762", C_WHITE))
    else:
        gs_lines.append(("Start mavproxy with:  --out=tcpin:0.0.0.0:5762", C_YELLOW))
    y = draw_section(img, y, 70, gs, gs_lines)

    # --- Footer ---
    cv2.putText(img, "Press 'q' to quit   |   'r' to recheck GS port   |   "
                "'s' to save screenshot",
                (20, DASH_H - 12), cv2.FONT_HERSHEY_SIMPLEX, 0.38, C_GRAY, 1)

    return img

# ============================================================
#  Headless terminal output
# ============================================================
# ANSI colors
A_GREEN  = "\033[92m"
A_RED    = "\033[91m"
A_YELLOW = "\033[93m"
A_CYAN   = "\033[96m"
A_RESET  = "\033[0m"
A_BOLD   = "\033[1m"

def print_headless_status():
    tag = lambda ok: f"{A_GREEN} OK {A_RESET}" if ok else f"{A_RED}FAIL{A_RESET}"
    print(f"\n{A_CYAN}{'='*60}{A_RESET}")
    print(f"  {A_BOLD}SAR DRONE DIAGNOSTICS{A_RESET}  —  {time.strftime('%H:%M:%S')}")
    print(f"{A_CYAN}{'='*60}{A_RESET}")

    print(f"\n  [{tag(cam.ok)}]  CAMERA: {cam.status}")
    if cam.ok:
        print(f"         Source: {cam.info.get('source','')}  Res: {cam.info.get('res','')}  FPS: {camera_fps:.1f}")
    print(f"         {A_CYAN}{cam.path}{A_RESET}")

    print(f"\n  [{tag(ai.ok)}]  AI MODEL: {ai.status}")
    if ai.ok:
        avg_ms = np.mean(inference_times[-30:]) if inference_times else 0
        print(f"         Backend: {ai.info.get('backend','')}  Inference: {avg_ms:.0f}ms avg")
    print(f"         {A_CYAN}{ai.path}{A_RESET}")

    print(f"\n  [{tag(cube.ok)}]  CUBE: {cube.status}")
    if cube.ok:
        print(f"         System: {cube.info.get('sysid','')}  via {cube.info.get('conn','')}")
        tracked = ['HEARTBEAT', 'ATTITUDE', 'GLOBAL_POSITION_INT', 'GPS_RAW_INT', 'SYS_STATUS']
        for mt in tracked:
            rate = msg_rates.get(mt, 0)
            rc = A_GREEN if rate > 0.5 else (A_YELLOW if rate > 0 else A_RED)
            print(f"         {rc}{mt:<26} {rate:>5.1f} Hz{A_RESET}")
        print(f"         Yaw={telem['yaw']:.0f}  Pitch={telem['pitch']:.1f}  Roll={telem['roll']:.1f}  "
              f"Alt={telem['alt_rel']:.1f}m  Bat={telem['voltage']:.1f}V")
    print(f"         {A_CYAN}{cube.path}{A_RESET}")

    gps_ok = telem['fix'] in ('3D', 'DGPS', 'RTK Float', 'RTK Fixed')
    gt = tag(gps_ok)
    print(f"\n  [{gt}]  GPS: {telem['fix']}  {telem['sats']} sats  HDOP={telem['hdop']:.1f}")
    if telem['lat'] != 0:
        print(f"         ({telem['lat']:.7f}, {telem['lon']:.7f})  Alt MSL={telem['alt_msl']:.1f}m")
    else:
        print(f"         {A_YELLOW}No fix — take drone outside{A_RESET}")
    print(f"         {A_CYAN}{gps.path}{A_RESET}")

    print(f"\n  [{tag(gs.ok)}]  GROUND STATION: {gs.status}")
    if gs.ok:
        print(f"         Pi IP: {gs.info.get('pi_ip','?')}  ->  connect MP to {gs.info.get('pi_ip','?')}:5762")
    else:
        print(f"         {A_YELLOW}Add --out=tcpin:0.0.0.0:5762 to mavproxy{A_RESET}")
    print(f"         {A_CYAN}{gs.path}{A_RESET}")
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
        # --- Update telemetry from Cube ---
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

            # Run AI inference for speed measurement
            if eyes and eyes.using_ai:
                t0 = time.time()
                eyes.detect_in_image(frame)
                inference_times.append((time.time() - t0) * 1000)

        # --- Periodically recheck GS port ---
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
                print_headless_status()
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
print(f"\n{'='*55}")
print(f"  DIAGNOSTICS SUMMARY")
print(f"{'='*55}")
for s in [cam, ai, cube, gps, gs]:
    tag = "  OK " if s.ok else " FAIL"
    print(f"  [{tag}]  {s.name}: {s.status}")
    if s.path:
        print(f"          Path: {s.path}")
if frame_count > 0:
    print(f"\n  Camera frames: {frame_count}")
    print(f"  Camera FPS:    {camera_fps:.1f}")
if inference_times:
    print(f"  AI inference:  {np.mean(inference_times[-30:]):.0f}ms avg")
if msg_rates:
    total_hz = sum(msg_rates.values())
    print(f"  Cube msg rate: {total_hz:.0f} msgs/sec total")
print()
