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

Why MJPEG over FFmpeg/H.264:
  - MJPEG: ~0.5 Mbps at 320x240 5fps — trivial over WiFi
  - H.264 (ffmpeg): ~0.05-0.1 Mbps — 5-10x smaller but adds complexity
  - MJPEG needs zero dependencies, works in any browser via <img> tag
  - H.264 needs ffmpeg on Pi + VLC or HLS player on GS + adds latency
  - For drone ops, low latency > compression. MJPEG gives near-realtime.
  - H.264 would only matter for cellular/4G or 720p+ resolution.
  - Decision: MJPEG is good enough.. Revisit if bandwidth is an issue.

Ground station:
  Open browser to http://<PI_IP>:8090/
  e.g. http://192.168.1.121:8090/

Endpoints:
  /               Dashboard — both streams side by side + controls
  /stream-raw     Raw camera feed (fast, no AI overhead)
  /stream-cv      Camera + AI detection overlay (slower, ~4 FPS on Pi)
  /stream         Same as /stream-cv when detection is on, else /stream-raw
  /snapshot       Single JPEG frame

Options:
  --port 8090         HTTP port (default 8090)
  --res 320x240       Stream resolution (default 320x240)
  --fps 5             Target FPS (default 5)
  --quality 50        JPEG quality 1-100 (default 50)
  --with-detection    Enable AI detection (adds /stream-cv endpoint)
  --headless          No local display

Usage:
    python tests2/pi_camera_stream.py                          # basic stream
    python tests2/pi_camera_stream.py --with-detection         # dual streams
    python tests2/pi_camera_stream.py --res 160x120 --fps 3   # low bandwidth
"""
import sys
import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

import cv2
import numpy as np

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

# --- Globals (two separate frames: raw + CV overlay) ---
latest_raw_frame = None    # clean camera frame (no overlays)
latest_cv_frame = None     # frame with AI detection + guidance overlays
frame_lock = threading.Lock()


def serve_mjpeg(handler, frame_type):
    """Send MJPEG stream. frame_type is 'raw' or 'cv'."""
    handler.send_response(200)
    handler.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
    handler.end_headers()

    while True:
        with frame_lock:
            if frame_type == 'cv' and latest_cv_frame is not None:
                frame = latest_cv_frame
            elif latest_raw_frame is not None:
                frame = latest_raw_frame
            else:
                frame = None

        if frame is None:
            time.sleep(0.1)
            continue

        small = cv2.resize(frame, (STREAM_W, STREAM_H))
        _, jpeg = cv2.imencode('.jpg', small, [cv2.IMWRITE_JPEG_QUALITY, JPEG_QUALITY])
        data = jpeg.tobytes()

        try:
            handler.wfile.write(b'--frame\r\n')
            handler.wfile.write(b'Content-Type: image/jpeg\r\n')
            handler.wfile.write(f'Content-Length: {len(data)}\r\n\r\n'.encode())
            handler.wfile.write(data)
            handler.wfile.write(b'\r\n')
        except (BrokenPipeError, ConnectionResetError):
            break

        time.sleep(1.0 / TARGET_FPS)


class StreamHandler(BaseHTTPRequestHandler):
    """HTTP handler that serves dual MJPEG streams."""

    def do_GET(self):
        if self.path == '/stream-raw':
            serve_mjpeg(self, 'raw')

        elif self.path == '/stream-cv':
            if WITH_DETECTION:
                serve_mjpeg(self, 'cv')
            else:
                serve_mjpeg(self, 'raw')

        elif self.path == '/stream':
            # Default: CV if detection on, otherwise raw
            serve_mjpeg(self, 'cv' if WITH_DETECTION else 'raw')

        elif self.path == '/snapshot':
            with frame_lock:
                frame = latest_cv_frame if WITH_DETECTION else latest_raw_frame
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
            self._send_dashboard()
        else:
            self.send_response(404)
            self.end_headers()

    def _send_dashboard(self):
        """HTML dashboard with stream controls."""
        if WITH_DETECTION:
            streams_html = """
<div style="display:flex;gap:20px;justify-content:center;flex-wrap:wrap">
  <div>
    <h3 style="color:#0f0">Raw Camera (fast)</h3>
    <img src="/stream-raw" style="width:480px;border:2px solid #0f0"/>
  </div>
  <div>
    <h3 style="color:#ff0">AI Detection (slower)</h3>
    <img src="/stream-cv" style="width:480px;border:2px solid #ff0"/>
  </div>
</div>"""
        else:
            streams_html = """
<div style="text-align:center">
  <h3 style="color:#0f0">Camera Feed</h3>
  <img src="/stream" style="max-width:90%;border:2px solid #0f0"/>
</div>"""

        html = f"""<html><head><title>Drone Camera</title>
<meta http-equiv="refresh" content="0; url=/" hidden>
</head>
<body style="background:#111;color:#fff;text-align:center;font-family:monospace;padding:20px">
<h2>SAR Drone Camera Feed</h2>
{streams_html}
<br>
<table style="margin:auto;color:#aaa;border-collapse:collapse">
<tr><td style="padding:4px 12px;text-align:right">Resolution:</td><td style="text-align:left">{STREAM_W}x{STREAM_H}</td></tr>
<tr><td style="padding:4px 12px;text-align:right">FPS:</td><td style="text-align:left">{TARGET_FPS}</td></tr>
<tr><td style="padding:4px 12px;text-align:right">Quality:</td><td style="text-align:left">{JPEG_QUALITY}%</td></tr>
<tr><td style="padding:4px 12px;text-align:right">Detection:</td><td style="text-align:left">{'ON' if WITH_DETECTION else 'OFF'}</td></tr>
</table>
<p style="color:#666;font-size:12px;margin-top:20px">
Endpoints: <a href="/stream-raw" style="color:#0f0">/stream-raw</a>
| <a href="/stream-cv" style="color:#ff0">/stream-cv</a>
| <a href="/snapshot" style="color:#88f">/snapshot</a>
</p>
</body></html>"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        pass


# ── Camera setup (same approach as diagnostics) ──

def setup_camera():
    """Open camera directly, same as diagnostics does."""
    cap = None
    picam = None

    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, test = cap.read()
        if ret:
            h, w = test.shape[:2]
            print(f"  Camera: OpenCV ({w}x{h})")
            return cap, None
        else:
            cap.release()
            cap = None
    else:
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
            test = picam.capture_array()
            h, w = test.shape[:2]
            print(f"  Camera: picamera2 ({w}x{h})")
            return None, picam
        except Exception as e:
            print(f"  [FAIL] No camera: {e}")
            return None, None

    return None, None


def get_frame(cap, picam):
    """Grab a frame — same as diagnostics get_frame()."""
    if cap:
        ret, f = cap.read()
        return f if ret else None
    if picam:
        f = picam.capture_array()
        return f
    return None


def camera_loop(cap, picam, eyes):
    """Capture frames, store raw + CV versions for dual streaming."""
    global latest_raw_frame, latest_cv_frame
    frame_count = 0
    det_count = 0
    start = time.time()

    can_detect = WITH_DETECTION and eyes is not None and eyes.using_ai
    print(f"  Camera loop running... (detection={'ON' if can_detect else 'OFF'})")

    while True:
        frame = get_frame(cap, picam)
        if frame is None:
            time.sleep(0.05)
            continue

        frame_count += 1
        h, w = frame.shape[:2]
        cx, cy = w // 2, h // 2

        # Store raw frame (crosshair only — no AI overlay)
        raw = frame.copy()
        cv2.drawMarker(raw, (cx, cy), (0, 255, 255), cv2.MARKER_CROSS, 20, 1)

        # --- Detection on separate copy (same as passive_flight) ---
        found = False
        conf = 0.0
        px, py = 0, 0
        if can_detect:
            # detect_in_image draws bbox on frame in-place
            found, px, py, conf = eyes.detect_in_image(frame)

        if found:
            det_count += 1
            cv2.circle(frame, (int(px), int(py)), 15, (0, 255, 0), 2)
            cv2.line(frame, (cx, cy), (int(px), int(py)), (0, 255, 0), 2)

            margin = w // 6
            direction = ""
            if px < cx - margin:
                direction = "LEFT"
            elif px > cx + margin:
                direction = "RIGHT"
            if py < cy - margin:
                direction = ("FORWARD " + direction).strip()
            elif py > cy + margin:
                direction = ("BACK " + direction).strip()
            if not direction:
                direction = "CENTRED"

            color = (0, 255, 0) if direction == "CENTRED" else (0, 255, 255)
            cv2.putText(frame, direction, (cx - 60, h - 20),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
            cv2.putText(frame, f"TARGET conf={conf:.2f}", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
            print(f"  ** DETECTED ** conf={conf:.2f} at ({px},{py}) -> {direction}")

        elif can_detect:
            cv2.putText(frame, "NO TARGET", (10, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Crosshair + stats on CV frame
        cv2.drawMarker(frame, (cx, cy), (0, 255, 255), cv2.MARKER_CROSS, 20, 1)
        elapsed = time.time() - start
        fps = frame_count / elapsed if elapsed > 0 else 0
        det_rate = det_count / frame_count * 100 if frame_count > 0 else 0
        cv2.putText(frame, f"FPS:{fps:.1f} Det:{det_rate:.0f}%",
                     (5, h - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

        # Update both frames atomically
        with frame_lock:
            latest_raw_frame = raw
            latest_cv_frame = frame

        if not HEADLESS:
            cv2.imshow("Pi Camera", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break

        if frame_count % 30 == 0:
            print(f"  #{frame_count} FPS:{fps:.1f} Det:{det_count}/{frame_count} ({det_rate:.0f}%)")


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

    # ── Open camera directly (same as diagnostics) ──
    print("[1] Opening camera...")
    cap, picam = setup_camera()
    if cap is None and picam is None:
        print("  [FAIL] No camera available — exiting")
        return

    test_frame = get_frame(cap, picam)
    if test_frame is not None:
        print(f"  Test frame: {test_frame.shape} dtype={test_frame.dtype}")
    else:
        print("  [WARN] Test frame failed")

    # ── Load AI model separately (same as diagnostics) ──
    eyes = None
    if WITH_DETECTION:
        print("\n[2] Loading AI model...")
        model_path = os.path.join(project_root, "best.tflite")
        print(f"  Model path: {model_path}")
        print(f"  File exists: {os.path.exists(model_path)}")

        from vision import VisionSystem
        eyes = VisionSystem(camera_index=None, model_path=model_path)

        if eyes.using_ai:
            backend = "TFLite" if eyes._use_tflite_direct else "Ultralytics"
            print(f"  AI backend: {backend}")

            print("  Running warmup inference...")
            t0 = time.time()
            dummy_frame = np.zeros((480, 640, 3), dtype=np.uint8)
            eyes.detect_in_image(dummy_frame)
            warmup_ms = (time.time() - t0) * 1000
            print(f"  Warmup: {warmup_ms:.0f}ms")

            if test_frame is not None:
                print("  Testing detection on real frame...")
                test_copy = test_frame.copy()
                found, tx, ty, tc = eyes.detect_in_image(test_copy)
                print(f"  Real frame test: found={found} conf={tc:.3f} at ({tx},{ty})")
        else:
            print("  [WARN] AI model NOT loaded — streaming without detection")

    # Get Pi IP
    pi_ip = "???"
    try:
        import subprocess
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True, timeout=3)
        pi_ip = result.stdout.strip().split()[0]
    except Exception:
        pass

    print(f"\n  Open in browser on ground station:")
    print(f"    http://{pi_ip}:{PORT}/")
    if WITH_DETECTION:
        print(f"    http://{pi_ip}:{PORT}/stream-raw  (fast, no AI)")
        print(f"    http://{pi_ip}:{PORT}/stream-cv   (with AI overlay)")
    print(f"    http://{pi_ip}:{PORT}/snapshot    (single frame)")
    print()

    # Start HTTP server
    server = HTTPServer(('0.0.0.0', PORT), StreamHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    print(f"  HTTP server started on port {PORT}")

    # Run camera loop (main thread)
    try:
        camera_loop(cap, picam, eyes)
    except KeyboardInterrupt:
        pass

    if not HEADLESS:
        cv2.destroyAllWindows()
    if cap:
        cap.release()
    if picam:
        try:
            picam.stop()
        except Exception:
            pass
    server.shutdown()
    print("\n  Stream stopped.")


if __name__ == "__main__":
    main()
