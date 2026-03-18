#!/usr/bin/env python3
"""
capture_training.py — Record video + take photos from drone camera for training data.

Run during flight to collect real images of the dummy from various altitudes/angles.
Use these images later to retrain the model with real data instead of synthetic composites.

ZERO commands sent. Just records. Safe to run anytime.

Run on Pi:
    python3 capture_training.py
    python3 capture_training.py --video          # also record continuous video
    python3 capture_training.py --interval 2     # auto-capture every 2 seconds

Controls (keyboard in terminal):
    SPACE = take a photo now
    V     = start/stop video recording
    Q     = quit

Open stream in browser:
    http://<PI_IP>:8091/stream

Photos saved to: training_data/photos/
Video saved to:  training_data/video/
"""
import sys
import os
import time
import signal
import threading
import argparse
import subprocess
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

signal.signal(signal.SIGINT, signal.SIG_DFL)

if not os.environ.get('DISPLAY'):
    os.environ.pop('QT_QPA_PLATFORM', None)

import cv2
import numpy as np

# Optional mavlink for GPS tagging
try:
    from pymavlink import mavutil
    HAS_MAV = True
except ImportError:
    HAS_MAV = False

# ── Globals ──
latest_jpeg = None
frame_lock = threading.Lock()
gps_data = {"lat": 0.0, "lon": 0.0, "alt": 0.0, "sats": 0, "yaw": 0.0}

COPTER_MODES = {
    0: "STABILIZE", 2: "ALT_HOLD", 3: "AUTO", 4: "GUIDED",
    5: "LOITER", 6: "RTL", 9: "LAND", 16: "POSHOLD",
}


class StreamHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/stream':
            self.send_response(200)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            while True:
                try:
                    with frame_lock:
                        jpg = latest_jpeg
                    if jpg:
                        self.wfile.write(b'--frame\r\n')
                        self.wfile.write(b'Content-Type: image/jpeg\r\n\r\n')
                        self.wfile.write(jpg)
                        self.wfile.write(b'\r\n')
                    time.sleep(0.1)
                except BrokenPipeError:
                    break
        else:
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(b'''<!DOCTYPE html>
<html><head><title>Training Capture</title>
<style>
  body { background:#111; color:#eee; font-family:monospace; margin:0; padding:20px; }
  h1 { color:#0f0; margin:0 0 10px; }
  .info { color:#888; margin-bottom:10px; }
  img { max-width:100%; border:1px solid #333; }
</style>
</head><body>
<h1>Training Data Capture</h1>
<div class="info">Stream only. Controls in terminal: SPACE=photo V=video Q=quit</div>
<img src="/stream" alt="Camera Feed">
</body></html>''')

    def log_message(self, *a):
        pass


class ThreadedServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


def mavlink_reader(mav):
    while True:
        try:
            msg = mav.recv_match(blocking=True, timeout=1)
            if msg is None:
                continue
            mtype = msg.get_type()
            if mtype == 'GLOBAL_POSITION_INT':
                gps_data["lat"] = msg.lat / 1e7
                gps_data["lon"] = msg.lon / 1e7
                gps_data["alt"] = msg.relative_alt / 1000.0
            elif mtype == 'GPS_RAW_INT':
                gps_data["sats"] = msg.satellites_visible
            elif mtype == 'ATTITUDE':
                import math
                gps_data["yaw"] = math.degrees(msg.yaw) % 360
        except Exception:
            time.sleep(0.1)


def open_camera(w=640, h=480):
    """Open camera (picamera2 or OpenCV)."""
    try:
        from picamera2 import Picamera2
        cam = Picamera2()
        cam.configure(cam.create_preview_configuration(
            main={"format": "RGB888", "size": (w, h)}))
        cam.start()
        time.sleep(1)
        return ("picam", cam)
    except Exception:
        pass
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, w)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, h)
    if cap.isOpened():
        return ("cv2", cap)
    return None


def get_frame(cam_info):
    cam_type, cam = cam_info
    if cam_type == "picam":
        return cam.capture_array()
    else:
        ret, frame = cam.read()
        return frame if ret else None


def main():
    global latest_jpeg

    parser = argparse.ArgumentParser(description="Capture training photos/video from drone")
    parser.add_argument('--video', action='store_true', help='Also record continuous video')
    parser.add_argument('--interval', type=float, default=0, help='Auto-capture photo every N seconds (0=manual only)')
    parser.add_argument('--port', type=int, default=8091, help='Stream port (default 8091)')
    parser.add_argument('--fps', type=int, default=30, help='Video recording FPS (default 30)')
    parser.add_argument('--res', default='640x480', help='Camera resolution WxH (default 640x480)')
    parser.add_argument('--no-mavlink', action='store_true', help='Skip mavlink connection')
    args = parser.parse_args()

    # Create output dirs
    photo_dir = "training_data/photos"
    video_dir = "training_data/video"
    os.makedirs(photo_dir, exist_ok=True)
    os.makedirs(video_dir, exist_ok=True)

    # Detect IP
    pi_ip = "localhost"
    try:
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True, timeout=3)
        ip = result.stdout.strip().split()[0]
        if ip:
            pi_ip = ip
    except Exception:
        pass

    print("=" * 50)
    print("  TRAINING DATA CAPTURE")
    print("  Photos + Video for model retraining")
    print("  ZERO commands sent. Safe to run anytime.")
    print("=" * 50)

    # Connect mavlink
    mav = None
    if not args.no_mavlink and HAS_MAV:
        try:
            print("[MAV] Connecting to udpin:0.0.0.0:14550...")
            mav = mavutil.mavlink_connection('udpin:0.0.0.0:14550')
            while True:
                msg = mav.recv_match(type='HEARTBEAT', blocking=True, timeout=5)
                if msg and msg.type != 6:
                    print(f"[MAV] Connected!")
                    break
            t = threading.Thread(target=mavlink_reader, args=(mav,), daemon=True)
            t.start()
        except Exception as e:
            print(f"[MAV] Failed: {e} — continuing without GPS")
            mav = None

    # Parse resolution
    res_parts = args.res.split('x')
    cam_w, cam_h = int(res_parts[0]), int(res_parts[1])

    # Open camera
    print(f"[CAM] Opening camera at {cam_w}x{cam_h}...")
    cam_info = open_camera(cam_w, cam_h)
    if cam_info is None:
        print("[ERROR] No camera found!")
        return
    print(f"[CAM] Opened via {cam_info[0]}")

    # Start stream server
    server = ThreadedServer(('0.0.0.0', args.port), StreamHandler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    print(f"\n  Stream: http://{pi_ip}:{args.port}/stream")

    # Controls
    print("\n  Controls:")
    print("    SPACE = take photo")
    print("    V     = start/stop video")
    if args.interval > 0:
        print(f"    Auto-capture every {args.interval}s")
    print("    Q/Ctrl+C = quit\n")

    # Non-blocking keyboard
    if os.name != 'nt':
        import select
        import tty
        import termios
        old_settings = termios.tcgetattr(sys.stdin)
        tty.setcbreak(sys.stdin.fileno())

    photo_count = 0
    recording = args.video
    video_writer = None
    last_auto = 0

    vid_frame_count = 0
    if recording:
        vpath = os.path.join(video_dir, f"flight_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi")
        video_writer = cv2.VideoWriter(vpath, cv2.VideoWriter_fourcc(*'MJPG'), args.fps, (cam_w, cam_h))
        if not video_writer.isOpened():
            print(f"[REC] ERROR: VideoWriter failed to open!")
            recording = False
        else:
            print(f"[REC] Recording to {vpath} ({cam_w}x{cam_h} @{args.fps}fps)")

    try:
        while True:
            frame = get_frame(cam_info)
            if frame is None:
                continue

            # Flip 180° (camera mounted upside down)
            frame = cv2.flip(frame, -1)

            # Update stream
            _, jpg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 70])
            with frame_lock:
                latest_jpeg = jpg.tobytes()

            # Write video
            if recording and video_writer:
                video_writer.write(frame)
                vid_frame_count += 1

            now = time.time()

            # Auto-capture
            if args.interval > 0 and now - last_auto >= args.interval:
                last_auto = now
                photo_count += 1
                lat, lon, alt = gps_data["lat"], gps_data["lon"], gps_data["alt"]
                ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                fname = f"{ts}_{alt:.0f}m_{photo_count:04d}.jpg"
                cv2.imwrite(os.path.join(photo_dir, fname), frame)
                print(f"  [AUTO] Photo {photo_count}: {fname} ({alt:.0f}m, {gps_data['sats']}sats)")

            # Check keyboard
            if os.name != 'nt':
                import select as sel
                if sel.select([sys.stdin], [], [], 0)[0]:
                    key = sys.stdin.read(1)

                    if key == ' ':
                        photo_count += 1
                        lat, lon, alt = gps_data["lat"], gps_data["lon"], gps_data["alt"]
                        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
                        fname = f"{ts}_{alt:.0f}m_{photo_count:04d}.jpg"
                        cv2.imwrite(os.path.join(photo_dir, fname), frame)
                        print(f"  [PHOTO] {photo_count}: {fname} ({alt:.0f}m, {gps_data['sats']}sats)")

                    elif key.lower() == 'v':
                        if recording:
                            recording = False
                            if video_writer:
                                video_writer.release()
                                video_writer = None
                            print(f"  [REC] Stopped recording ({vid_frame_count} frames written)")
                            vid_frame_count = 0
                        else:
                            recording = True
                            vpath = os.path.join(video_dir,
                                                 f"flight_{datetime.now().strftime('%Y%m%d_%H%M%S')}.avi")
                            video_writer = cv2.VideoWriter(vpath,
                                                           cv2.VideoWriter_fourcc(*'MJPG'), args.fps, (cam_w, cam_h))
                            print(f"  [REC] Recording to {vpath}")

                    elif key.lower() == 'q':
                        break

    except KeyboardInterrupt:
        pass
    finally:
        if os.name != 'nt':
            termios.tcsetattr(sys.stdin, termios.TCSADRAIN, old_settings)
        if video_writer:
            video_writer.release()

    print(f"\n  Done! {photo_count} photos saved to {photo_dir}/")
    if recording:
        print(f"  Video saved to {video_dir}/")


if __name__ == "__main__":
    main()
