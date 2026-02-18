#!/usr/bin/env python3
"""
Camera Stream — send live camera feed to ground station.

Runs a lightweight MJPEG server on the Pi. Open in any browser on the
ground station laptop to see what the drone sees.

How it works:
  - Pi captures full 640x480 for AI detection (unchanged)
  - Downscales to 320x240 (or custom) for streaming
  - Serves MJPEG over HTTP — works in any browser, no plugins needed
  - Bandwidth: ~0.3-0.8 Mbps at 320x240, 5fps — fine over WiFi

Ground station:
  Open browser to http://<PI_IP>:8090/stream
  e.g. http://192.168.1.121:8090/stream

Options:
  --port 8090         HTTP port (default 8090)
  --res 320x240       Stream resolution (default 320x240)
  --fps 5             Target FPS (default 5)
  --quality 50        JPEG quality 1-100 (default 50)
  --with-detection    Run AI detection and overlay boxes on stream
  --headless          No local display

Usage:.
    python tests2/pi_camera_stream.py                          # basic stream
    python tests2/pi_camera_stream.py --with-detection         # stream + AI overlay
    python tests2/pi_camera_stream.py --res 160x120 --fps 3   # low bandwidth
"""
import sys
import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import cv2
import numpy as np
from vision import VisionSystem

# --- Parse args ---
PORT = 8090
STREAM_W, STREAM_H = 320, 240
TARGET_FPS = 5
JPEG_QUALITY = 50
WITH_DETECTION = "--with-detection" in sys.argv
HEADLESS = "--headless" in sys.argv

for i, arg in enumerate(sys.argv):
    if arg == "--port" and i + 1 < len(sys.argv):
        PORT = int(sys.argv[i + 1])
    elif arg == "--res" and i + 1 < len(sys.argv):
        parts = sys.argv[i + 1].split("x")
        STREAM_W, STREAM_H = int(parts[0]), int(parts[1])
    elif arg == "--fps" and i + 1 < len(sys.argv):
        TARGET_FPS = int(sys.argv[i + 1])
    elif arg == "--quality" and i + 1 < len(sys.argv):
        JPEG_QUALITY = int(sys.argv[i + 1])

# --- Globals ---
latest_frame = None
frame_lock = threading.Lock()
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
model_path = os.path.join(project_root, "best.tflite")


class StreamHandler(BaseHTTPRequestHandler):
    """HTTP handler that serves MJPEG stream."""

    def do_GET(self):
        if self.path == '/stream':
            self.send_response(200)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()

            while True:
                with frame_lock:
                    frame = latest_frame

                if frame is None:
                    time.sleep(0.1)
                    continue

                # Downscale for streaming
                small = cv2.resize(frame, (STREAM_W, STREAM_H))
                _, jpeg = cv2.imencode('.jpg', small, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
                data = jpeg.tobytes()

                try:
                    self.wfile.write(b'--frame\r\n')
                    self.wfile.write(b'Content-Type: image/jpeg\r\n')
                    self.wfile.write(f'Content-Length: {len(data)}\r\n\r\n'.encode())
                    self.wfile.write(data)
                    self.wfile.write(b'\r\n')
                except (BrokenPipeError, ConnectionResetError):
                    break

                time.sleep(1.0 / TARGET_FPS)

        elif self.path == '/snapshot':
            # Single JPEG frame
            with frame_lock:
                frame = latest_frame
            if frame is None:
                self.send_response(503)
                self.end_headers()
                return

            small = cv2.resize(frame, (STREAM_W, STREAM_H))
            _, jpeg = cv2.imencode('.jpg', small, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
            self.send_response(200)
            self.send_header('Content-Type', 'image/jpeg')
            self.send_header('Content-Length', str(len(jpeg)))
            self.end_headers()
            self.wfile.write(jpeg.tobytes())

        elif self.path == '/':
            # Simple HTML page with embedded stream
            html = f"""<html><head><title>Drone Camera</title></head>
<body style="background:#111;color:#fff;text-align:center;font-family:monospace">
<h2>SAR Drone Camera Feed</h2>
<img src="/stream" style="max-width:100%;border:2px solid #0f0"/>
<p>Resolution: {STREAM_W}x{STREAM_H} | FPS: {TARGET_FPS} | Quality: {JPEG_QUALITY}%</p>
<p>Detection: {'ON' if WITH_DETECTION else 'OFF'}</p>
</body></html>"""
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress per-request logging


def camera_loop(eyes):
    """Capture frames and optionally run detection."""
    global latest_frame
    frame_count = 0
    det_count = 0
    start = time.time()

    print("  Camera loop running...")

    while True:
        frame = eyes.get_frame()
        if frame is None:
            time.sleep(0.05)
            continue

        frame_count += 1
        display = frame.copy()

        h, w = display.shape[:2]
        cx, cy = w // 2, h // 2

        if WITH_DETECTION:
            found, px, py, conf = eyes.detect_in_image(frame)
            if found:
                det_count += 1
                # Detection marker + confidence
                cv2.circle(display, (px, py), 15, (0, 255, 0), 2)
                cv2.putText(display, f"{conf:.2f}", (px + 10, py - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)

                # Guidance line from centre to target
                cv2.line(display, (cx, cy), (px, py), (0, 255, 0), 2)

                # Direction guidance (same as passive_flight)
                margin = w // 6
                if px < cx - margin:
                    direction = "LEFT"
                elif px > cx + margin:
                    direction = "RIGHT"
                else:
                    direction = ""
                if py < cy - margin:
                    direction = ("FORWARD " + direction).strip()
                elif py > cy + margin:
                    direction = ("BACK " + direction).strip()
                if not direction:
                    direction = "CENTRED"

                color = (0, 255, 0) if direction == "CENTRED" else (0, 255, 255)
                cv2.putText(display, direction, (cx - 60, h - 20),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
                cv2.putText(display, f"TARGET conf={conf:.2f}", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            else:
                cv2.putText(display, "NO TARGET", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Crosshair
        cv2.drawMarker(display, (cx, cy), (0, 255, 255),
                        cv2.MARKER_CROSS, 20, 1)

        # Stats overlay
        elapsed = time.time() - start
        fps = frame_count / elapsed if elapsed > 0 else 0
        det_rate = det_count / frame_count * 100 if frame_count > 0 else 0
        cv2.putText(display, f"FPS:{fps:.1f} Det:{det_rate:.0f}%",
                     (5, h - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

        with frame_lock:
            latest_frame = display

        if not HEADLESS:
            cv2.imshow("Pi Camera", display)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break

        # Print stats every 30 frames
        if frame_count % 30 == 0:
            det_rate = det_count / frame_count * 100 if frame_count > 0 else 0
            print(f"  #{frame_count} FPS:{fps:.1f} Det:{det_rate:.0f}%")


def main():
    print()
    print("=" * 60)
    print("   CAMERA STREAM — Live feed to ground station")
    print("=" * 60)
    print()
    print(f"  Stream:     {STREAM_W}x{STREAM_H} @ {TARGET_FPS}fps")
    print(f"  Quality:    {JPEG_QUALITY}%")
    print(f"  Detection:  {'ON' if WITH_DETECTION else 'OFF'}")
    print(f"  Port:       {PORT}")
    print(f"  Headless:   {HEADLESS}")
    print()

    # Initialize camera
    if WITH_DETECTION:
        print(f"  Loading AI model: {model_path}")
        eyes = VisionSystem(camera_index=0, model_path=model_path)
        if not eyes.using_ai:
            print("  [WARN] AI model not loaded — streaming without detection")
    else:
        eyes = VisionSystem(camera_index=0, model_path="__none__")

    # Get Pi IP for display
    pi_ip = "???"
    try:
        import subprocess
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True, timeout=3)
        pi_ip = result.stdout.strip().split()[0]
    except Exception:
        pass

    print(f"\n  Open in browser on ground station:")
    print(f"    http://{pi_ip}:{PORT}/")
    print(f"    http://{pi_ip}:{PORT}/stream    (raw MJPEG)")
    print(f"    http://{pi_ip}:{PORT}/snapshot  (single frame)")
    print()

    # Start HTTP server in background thread
    server = HTTPServer(('0.0.0.0', PORT), StreamHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    print(f"  HTTP server started on port {PORT}")

    # Run camera loop (main thread)
    try:
        camera_loop(eyes)
    except KeyboardInterrupt:
        pass

    if not HEADLESS:
        cv2.destroyAllWindows()
    eyes.release()
    server.shutdown()
    print("\n  Stream stopped.")


if __name__ == "__main__":
    main()
