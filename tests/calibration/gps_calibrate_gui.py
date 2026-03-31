#!/usr/bin/env python3
"""
GPS Calibration GUI — Beautiful OpenCV-based focal length calibration.

Launch on Pi with screen attached. Shows live camera feed with detection
overlay, step-by-step instructions, and real-time status panel.

USAGE:
    python tests/calibration/gps_calibrate_gui.py
    python tests/calibration/gps_calibrate_gui.py --no-mavlink
    python tests/calibration/gps_calibrate_gui.py --model cv_models/human.tflite

KEYS:
    H = enter camera height (type number + ENTER)
    D = enter target distance (type number + ENTER)
    SPACE = capture 10 frames
    N = next measurement
    Q = summary / quit
"""
import sys
import os
import time
import math
import threading
import argparse

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import cv2
import numpy as np
import config
from vision import VisionSystem

# ── Colors (BGR) ──
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
LIME = (0, 255, 100)
YELLOW = (0, 255, 255)
ORANGE = (0, 165, 255)
RED = (0, 0, 255)
CYAN = (255, 255, 0)
GRAY = (64, 64, 64)
LGRAY = (200, 200, 200)

# ── States ──
S_SETUP = 0
S_HEIGHT = 1
S_DISTANCE = 2
S_READY = 3
S_CAPTURING = 4
S_RESULTS = 5
S_SUMMARY = 6

STATE_NAMES = {S_SETUP: "SETUP", S_HEIGHT: "ENTER HEIGHT", S_DISTANCE: "ENTER DISTANCE",
               S_READY: "AIM AT TARGET", S_CAPTURING: "CAPTURING...", S_RESULTS: "RESULTS",
               S_SUMMARY: "SUMMARY"}
STATE_COLORS = {S_SETUP: YELLOW, S_HEIGHT: ORANGE, S_DISTANCE: ORANGE,
                S_READY: YELLOW, S_CAPTURING: GREEN, S_RESULTS: GREEN, S_SUMMARY: CYAN}

# ── GPS telemetry ──
gps = {"lat": 0.0, "lon": 0.0, "alt": 0.0, "yaw": 0.0, "sats": 0}


def mav_reader(mav):
    while True:
        try:
            msg = mav.recv_match(blocking=True, timeout=1)
            if msg is None:
                continue
            t = msg.get_type()
            if t == 'GLOBAL_POSITION_INT':
                gps["lat"] = msg.lat / 1e7
                gps["lon"] = msg.lon / 1e7
                gps["alt"] = msg.relative_alt / 1000.0
            elif t == 'ATTITUDE':
                gps["yaw"] = msg.yaw * 57.2958
            elif t == 'GPS_RAW_INT':
                gps["sats"] = msg.satellites_visible
        except Exception:
            time.sleep(0.1)


def txt(frame, text, pos, color=WHITE, scale=0.7, thick=1):
    cv2.putText(frame, text, pos, cv2.FONT_HERSHEY_SIMPLEX, scale, color, thick, cv2.LINE_AA)


def txt_bg(frame, text, pos, color=WHITE, scale=0.7, thick=1):
    font = cv2.FONT_HERSHEY_SIMPLEX
    (tw, th), bl = cv2.getTextSize(text, font, scale, thick)
    x, y = pos
    cv2.rectangle(frame, (x - 3, y - th - 3), (x + tw + 3, y + bl + 3), BLACK, -1)
    cv2.putText(frame, text, pos, font, scale, color, thick, cv2.LINE_AA)


def draw_panel(frame, w, h, state, height_m, dist_m, buf, conf, measurements, gps_data):
    """Draw right-side status panel."""
    pw = 340
    x = w - pw

    # Semi-transparent background
    overlay = frame[0:h, x:w].copy()
    cv2.rectangle(frame, (x, 0), (w, h), GRAY, -1)
    cv2.addWeighted(frame[0:h, x:w], 0.75, overlay, 0.25, 0, frame[0:h, x:w])
    cv2.line(frame, (x, 0), (x, h), LGRAY, 2)

    y = 30
    txt(frame, "GPS CALIBRATION", (x + 10, y), CYAN, 0.9, 2)
    y += 35
    txt(frame, f"State: {STATE_NAMES[state]}", (x + 10, y), STATE_COLORS[state], 0.7, 2)
    y += 35

    # Config
    txt(frame, "CONFIG", (x + 10, y), CYAN, 0.6, 1)
    y += 25
    txt(frame, f"FOCAL: {config.FOCAL_LENGTH_MM:.2f}mm", (x + 10, y), WHITE, 0.55)
    y += 22
    txt(frame, f"SENSOR: {config.SENSOR_WIDTH_MM}mm", (x + 10, y), WHITE, 0.55)
    y += 22
    txt(frame, f"IMAGE: {config.IMAGE_W}x{config.IMAGE_H}", (x + 10, y), WHITE, 0.55)
    y += 30

    # Current input
    txt(frame, "MEASUREMENT", (x + 10, y), CYAN, 0.6, 1)
    y += 25
    txt(frame, f"Height: {height_m:.2f}m" if height_m > 0 else "Height: ---", (x + 10, y),
        GREEN if height_m > 0 else YELLOW, 0.6)
    y += 22
    txt(frame, f"Distance: {dist_m:.2f}m" if dist_m >= 0 else "Distance: ---", (x + 10, y),
        GREEN if dist_m > 0 else YELLOW, 0.6)
    y += 22
    if buf:
        txt(frame, f"Typing: {buf}_", (x + 10, y), LIME, 0.65, 2)
    y += 30

    # Detection
    txt(frame, "DETECTION", (x + 10, y), CYAN, 0.6, 1)
    y += 25
    c = GREEN if conf > 0.3 else (YELLOW if conf > 0 else RED)
    txt(frame, f"Confidence: {conf:.3f}" if conf > 0 else "Confidence: ---", (x + 10, y), c, 0.6)
    y += 30

    # Telemetry
    txt(frame, "TELEMETRY", (x + 10, y), CYAN, 0.6, 1)
    y += 25
    txt(frame, f"Alt: {gps_data['alt']:.1f}m  Yaw: {gps_data['yaw']:.0f}deg", (x + 10, y), WHITE, 0.55)
    y += 22
    txt(frame, f"Sats: {gps_data['sats']}  GPS: {gps_data['lat']:.5f},{gps_data['lon']:.5f}",
        (x + 10, y), WHITE, 0.5)
    y += 30

    # History
    if measurements:
        txt(frame, f"HISTORY ({len(measurements)} measurements)", (x + 10, y), CYAN, 0.6, 1)
        y += 25
        for i, m in enumerate(measurements[-4:], len(measurements) - min(3, len(measurements) - 1)):
            err_c = GREEN if abs(m["error_pct"]) < 10 else YELLOW
            txt(frame, f"#{i}: f={m['focal_mm']:.2f}mm err={m['error_pct']:+.1f}%",
                (x + 10, y), err_c, 0.5)
            y += 20


def draw_instructions(frame, state, buf, frame_count):
    """Draw instructions on the camera view."""
    y = 40

    if state == S_SETUP:
        txt_bg(frame, "GPS ESTIMATE CALIBRATION", (20, y), LIME, 1.0, 2)
        y += 50
        txt_bg(frame, "Calibrate focal length for accurate GPS estimation", (20, y), WHITE, 0.7)
        y += 45
        txt_bg(frame, "1. Hold camera pointing DOWN at target", (20, y), WHITE, 0.65)
        y += 35
        txt_bg(frame, "2. Measure height + distance with tape", (20, y), WHITE, 0.65)
        y += 35
        txt_bg(frame, "3. Capture frames for calibration", (20, y), WHITE, 0.65)
        y += 55
        txt_bg(frame, "Press H to start", (20, y), YELLOW, 1.0, 2)

    elif state == S_HEIGHT:
        txt_bg(frame, "STEP 1: Camera Height", (20, y), LIME, 1.0, 2)
        y += 50
        txt_bg(frame, "Type height in meters, press ENTER", (20, y), WHITE, 0.7)
        y += 50
        txt_bg(frame, f"Height: {buf if buf else '0.0'} m", (20, y), CYAN, 1.2, 2)
        y += 60
        txt_bg(frame, "e.g. 1.5 = standing, 2.0 = arm raised", (20, y), YELLOW, 0.6)

    elif state == S_DISTANCE:
        txt_bg(frame, "STEP 2: Target Distance", (20, y), LIME, 1.0, 2)
        y += 50
        txt_bg(frame, "Horizontal offset from directly below camera", (20, y), WHITE, 0.65)
        y += 40
        txt_bg(frame, "Type distance in meters, press ENTER", (20, y), WHITE, 0.7)
        y += 50
        txt_bg(frame, f"Distance: {buf if buf else '0.0'} m", (20, y), CYAN, 1.2, 2)
        y += 60
        txt_bg(frame, "0.5 = half meter, 1.0 = one meter to side", (20, y), YELLOW, 0.6)

    elif state == S_READY:
        txt_bg(frame, "STEP 3: Aim at Target", (20, y), LIME, 1.0, 2)
        y += 50
        txt_bg(frame, "Point camera DOWN at the target", (20, y), WHITE, 0.7)
        y += 40
        txt_bg(frame, "Green box should appear on target", (20, y), WHITE, 0.7)
        y += 60
        txt_bg(frame, "Press SPACE to capture", (20, y), YELLOW, 1.0, 2)

    elif state == S_CAPTURING:
        txt_bg(frame, "CAPTURING...", (20, y), GREEN, 1.2, 2)
        y += 60
        txt_bg(frame, f"Frame {frame_count} / 10", (20, y), CYAN, 1.0, 2)
        y += 50
        # Progress bar
        bw = 400
        cv2.rectangle(frame, (20, y), (20 + bw, y + 30), LGRAY, 2)
        filled = int(bw * frame_count / 10)
        cv2.rectangle(frame, (20, y), (20 + filled, y + 30), GREEN, -1)
        y += 50
        txt_bg(frame, "Hold steady!", (20, y), YELLOW, 0.8)


def draw_results(frame, m):
    """Draw measurement results on camera view."""
    y = 40
    txt_bg(frame, "RESULTS", (20, y), LIME, 1.0, 2)
    y += 45
    txt_bg(frame, f"Detections: {m['n_det']}/10", (20, y),
           GREEN if m['n_det'] >= 7 else YELLOW, 0.8)
    y += 35
    txt_bg(frame, f"Confidence: {m['conf']:.3f}", (20, y),
           GREEN if m['conf'] > 0.3 else YELLOW, 0.8)
    y += 35
    txt_bg(frame, f"Spread: {m['spread']:.1f}px", (20, y),
           GREEN if m['spread'] < 20 else YELLOW, 0.8)
    y += 45
    txt_bg(frame, f"Actual:    {m['actual_m']:.3f}m", (20, y), WHITE, 0.85)
    y += 35
    txt_bg(frame, f"Estimated: {m['est_m']:.3f}m", (20, y), WHITE, 0.85)
    y += 40
    c = GREEN if abs(m['error_pct']) < 10 else (YELLOW if abs(m['error_pct']) < 25 else RED)
    txt_bg(frame, f"Error: {m['error_m']:+.3f}m ({m['error_pct']:+.1f}%)", (20, y), c, 1.0, 2)
    y += 50
    txt_bg(frame, f"Focal: {config.FOCAL_LENGTH_MM:.2f} -> {m['focal_mm']:.2f}mm", (20, y), CYAN, 0.9, 2)
    y += 55
    txt_bg(frame, "N = next measurement   Q = summary", (20, y), YELLOW, 0.7)


def draw_summary(frame, measurements, w, h):
    """Draw final summary screen."""
    # Dark overlay
    cv2.rectangle(frame, (0, 0), (w, h), BLACK, -1)

    y = 50
    txt(frame, "CALIBRATION COMPLETE", (30, y), LIME, 1.2, 2)
    y += 55

    for i, m in enumerate(measurements, 1):
        c = GREEN if abs(m['error_pct']) < 10 else YELLOW
        txt(frame, f"#{i}: h={m['height_m']:.1f}m  d={m['actual_m']:.2f}m  "
            f"f={m['focal_mm']:.2f}mm  err={m['error_pct']:+.1f}%", (30, y), c, 0.65)
        y += 30

    y += 20

    # Weighted average
    total_w = 0
    weighted_f = 0
    for m in measurements:
        weight = m['conf'] / max(1, m['spread'])
        weighted_f += m['focal_mm'] * weight
        total_w += weight
    avg_f = weighted_f / total_w if total_w > 0 else config.FOCAL_LENGTH_MM

    cv2.rectangle(frame, (20, y - 10), (w - 20, y + 100), (30, 60, 30), -1)
    cv2.rectangle(frame, (20, y - 10), (w - 20, y + 100), GREEN, 2)
    y += 20
    txt(frame, f"FOCAL_LENGTH_MM = {avg_f:.2f}", (40, y), CYAN, 1.3, 2)
    y += 40
    txt(frame, f"(was {config.FOCAL_LENGTH_MM:.2f}, change: {avg_f - config.FOCAL_LENGTH_MM:+.2f}mm)",
        (40, y), WHITE, 0.7)
    y += 50

    # Accuracy table
    txt(frame, "Expected accuracy:", (30, y), YELLOW, 0.7)
    y += 30
    for alt in [10, 20, 30, 50]:
        gw = alt * config.SENSOR_WIDTH_MM / avg_f
        px_per_m = avg_f * config.IMAGE_W / (config.SENSOR_WIDTH_MM * alt)
        txt(frame, f"  {alt}m alt: ground {gw:.1f}m wide, 1px = {1/px_per_m:.3f}m",
            (30, y), WHITE, 0.55)
        y += 25

    y += 20
    txt(frame, "Update config.py with the value above", (30, y), YELLOW, 0.8)
    y += 35
    txt(frame, "Press Q to exit", (30, y), LGRAY, 0.7)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--no-mavlink', action='store_true')
    parser.add_argument('--model', default='best.tflite')
    parser.add_argument('--conf', type=float, default=0.2)
    args = parser.parse_args()

    print("[CAM] Opening camera + AI...")
    eyes = VisionSystem(camera_index=0, model_path=args.model)
    if not eyes.using_ai:
        print("[ERROR] AI model not loaded!")
        return

    # MAVLink
    if not args.no_mavlink:
        try:
            from pymavlink import mavutil
            mav = mavutil.mavlink_connection('udpin:0.0.0.0:14550')
            msg = mav.recv_match(type='HEARTBEAT', blocking=True, timeout=5)
            if msg:
                print("[MAV] Connected")
                threading.Thread(target=mav_reader, args=(mav,), daemon=True).start()
                time.sleep(1)
        except Exception as e:
            print(f"[MAV] {e}")

    f_px = config.FOCAL_LENGTH_MM * config.IMAGE_W / config.SENSOR_WIDTH_MM

    win = "GPS Calibration"
    cv2.namedWindow(win, cv2.WINDOW_NORMAL)
    cv2.resizeWindow(win, 1456, 900)

    state = S_SETUP
    buf = ""
    height_m = 0.0
    dist_m = 0.0
    detections = []
    frame_count = 0
    measurements = []
    last_conf = 0.0
    last_result = None

    try:
        while True:
            frame = eyes.get_frame()
            if frame is None:
                time.sleep(0.01)
                continue

            h, w = frame.shape[:2]

            # Detection (always running for live preview)
            found, cx, cy, conf = eyes.detect_in_image(frame)
            if found and conf >= args.conf:
                last_conf = conf

            # Capture frames
            if state == S_CAPTURING and found and conf >= args.conf:
                norm_x = cx / w
                norm_y = cy / h
                detections.append((norm_x, norm_y, conf))
                frame_count = len(detections)

                if frame_count >= 10:
                    # Process
                    avg_x = sum(d[0] for d in detections) / len(detections)
                    avg_y = sum(d[1] for d in detections) / len(detections)
                    avg_c = sum(d[2] for d in detections) / len(detections)
                    sp_x = max(d[0] for d in detections) - min(d[0] for d in detections)
                    sp_y = max(d[1] for d in detections) - min(d[1] for d in detections)
                    spread = math.sqrt((sp_x * config.IMAGE_W)**2 + (sp_y * config.IMAGE_H)**2)

                    dx_px = (avg_x - 0.5) * config.IMAGE_W
                    dy_px = (avg_y - 0.5) * config.IMAGE_H
                    px_dist = math.sqrt(dx_px**2 + dy_px**2)
                    est_dist = px_dist * height_m / f_px

                    if dist_m > 0.05:
                        f_px_new = px_dist * height_m / dist_m
                        focal_new = f_px_new * config.SENSOR_WIDTH_MM / config.IMAGE_W
                        error_m = est_dist - dist_m
                        error_pct = 100 * error_m / dist_m
                    else:
                        focal_new = config.FOCAL_LENGTH_MM
                        error_m = 0
                        error_pct = 0

                    last_result = {
                        "height_m": height_m, "actual_m": dist_m, "est_m": est_dist,
                        "error_m": error_m, "error_pct": error_pct,
                        "focal_mm": focal_new, "n_det": len(detections),
                        "conf": avg_c, "spread": spread,
                    }
                    measurements.append(last_result)
                    state = S_RESULTS

            # Crosshair
            cx_f, cy_f = w // 2, h // 2
            cv2.line(frame, (cx_f - 35, cy_f), (cx_f + 35, cy_f), CYAN, 2)
            cv2.line(frame, (cx_f, cy_f - 35), (cx_f, cy_f + 35), CYAN, 2)
            cv2.circle(frame, (cx_f, cy_f), 5, CYAN, -1)

            # Draw UI
            if state == S_RESULTS and last_result:
                draw_results(frame, last_result)
            elif state == S_SUMMARY:
                draw_summary(frame, measurements, w, h)
            else:
                draw_instructions(frame, state, buf, frame_count)

            draw_panel(frame, w, h, state, height_m, dist_m, buf, last_conf, measurements, gps)

            cv2.imshow(win, frame)
            key = cv2.waitKey(10) & 0xFF
            if key == 255:
                continue

            # ── Key handling ──
            if key == ord('q') or key == 27:
                if state == S_SUMMARY:
                    break
                elif measurements:
                    state = S_SUMMARY
                else:
                    break

            elif state == S_SETUP and key == ord('h'):
                state = S_HEIGHT
                buf = ""

            elif state == S_HEIGHT:
                if 48 <= key <= 57:
                    buf += chr(key)
                elif key == ord('.') and '.' not in buf:
                    buf += '.'
                elif key == 8 and buf:
                    buf = buf[:-1]
                elif key == 13 and buf:
                    try:
                        height_m = float(buf)
                        if height_m > 0:
                            state = S_DISTANCE
                            buf = ""
                    except ValueError:
                        pass

            elif state == S_DISTANCE:
                if 48 <= key <= 57:
                    buf += chr(key)
                elif key == ord('.') and '.' not in buf:
                    buf += '.'
                elif key == 8 and buf:
                    buf = buf[:-1]
                elif key == 13 and buf:
                    try:
                        dist_m = float(buf)
                        state = S_READY
                        buf = ""
                    except ValueError:
                        pass

            elif state == S_READY and key == ord(' '):
                state = S_CAPTURING
                detections = []
                frame_count = 0

            elif state == S_RESULTS:
                if key == ord('n'):
                    state = S_SETUP
                    buf = ""

    except KeyboardInterrupt:
        pass

    cv2.destroyAllWindows()
    eyes.release()

    # Print summary to terminal too
    if measurements:
        print("\n" + "=" * 60)
        print("  CALIBRATION RESULTS")
        print("=" * 60)
        total_w = 0
        weighted_f = 0
        for i, m in enumerate(measurements, 1):
            print(f"  #{i}: h={m['height_m']:.1f}m d={m['actual_m']:.2f}m "
                  f"f={m['focal_mm']:.2f}mm err={m['error_pct']:+.1f}%")
            weight = m['conf'] / max(1, m['spread'])
            weighted_f += m['focal_mm'] * weight
            total_w += weight
        avg_f = weighted_f / total_w if total_w > 0 else config.FOCAL_LENGTH_MM
        print(f"\n  FOCAL_LENGTH_MM = {avg_f:.2f}  (was {config.FOCAL_LENGTH_MM:.2f})")
        print("=" * 60)


if __name__ == "__main__":
    main()
