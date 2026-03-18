#!/usr/bin/env python3
"""
Camera Stream Fast — threaded MJPEG stream with non-blocking AI detection.

WHAT:    Captures frames in the main thread at full camera speed (~25 FPS) and runs
         AI detection in a separate background thread (~4 FPS). The detection overlay
         (bounding box, direction, confidence) is drawn on every frame using the latest
         AI result, so the stream stays smooth while AI updates asynchronously. Also
         provides an /ai-snapshot endpoint to inspect the exact frame the model sees
         (useful for checking motion blur).
WHY:     The basic camera_stream.py runs detection synchronously, capping the entire
         stream to ~4 FPS. This threaded version decouples capture from inference,
         giving a smooth ~25 FPS stream with AI overlay updating at inference speed.
WHEN:    Use whenever you need a live camera feed with AI detection and smooth video.
         Preferred over camera_stream.py when AI is enabled. Good for manual flights
         where the pilot needs a responsive video feed with detection indicators.
WHERE:   Pi (primary) or laptop (webcam fallback). Headless-safe with --headless.
ENV:     Pi venv (picamera2, opencv-headless, ai-edge-litert) or laptop venv (opencv, ultralytics).
MODELS:  best.tflite from project root (YOLOv8n, ~3.3MB). Only loaded if --with-detection.
RISK:    none — sends ZERO commands to the drone. Read-only camera + AI.

USAGE:
    python tests/diagnostics/camera_stream_fast.py --with-detection
    python tests/diagnostics/camera_stream_fast.py --with-detection --fps 20 --quality 70
    python tests/diagnostics/camera_stream_fast.py --res 640x480 --fps 10
    python tests/diagnostics/camera_stream_fast.py --with-detection --headless

FLAGS:
    --port PORT         HTTP server port (default: 8090)
    --res WxH           Stream resolution, e.g. 320x240 (default: 320x240)
    --fps N             Target stream FPS (default: 15)
    --quality N         JPEG quality 1-100 (default: 50)
    --with-detection    Enable threaded AI detection overlay
    --headless          Suppress cv2.imshow window (for SSH/PuTTY)

OUTPUT:
    HTTP endpoints:
      /             — HTML page with embedded stream and AI links
      /stream       — raw MJPEG stream at target FPS
      /snapshot     — single JPEG frame (downscaled)
      /stream-ai    — MJPEG stream of only AI-processed frames (~4 FPS)
      /ai-snapshot  — full-resolution JPEG of last frame fed to AI (blur inspection)
    Terminal: periodic stream FPS, AI FPS, and detection count

BEST PRACTICES:
    - Use this instead of camera_stream.py when you need AI + smooth video
    - Check /ai-snapshot in browser to verify the model sees sharp images
    - Use --headless on Pi over SSH
    - Higher --fps increases WiFi bandwidth; 15 FPS is a good default

DEPENDENCIES:
    opencv-python (or opencv-python-headless), numpy, vision.py (project module)
    Optional: picamera2 (Pi), ultralytics or ai-edge-litert (AI backend)
"""
import sys
import os
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

import cv2
import numpy as np

# --- Parse args ---
PORT = 8090
STREAM_W, STREAM_H = 320, 240
TARGET_FPS = 15
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

# Detection results shared between threads
det_lock = threading.Lock()
det_result = {
    "found": False,
    "px": 0, "py": 0,
    "conf": 0.0,
    "direction": "",
    "det_count": 0,
    "inf_fps": 0.0,
}

# The exact frame being fed to AI (for smear/blur inspection)
ai_frame = None
ai_frame_lock = threading.Lock()


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

        elif self.path == '/ai-snapshot':
            # The exact frame the AI model last processed (check for smear/blur)
            with ai_frame_lock:
                frame = ai_frame
            if frame is None:
                self.send_response(503)
                self.end_headers()
                return

            # Full resolution, high quality — so you can inspect blur properly
            _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 95])
            self.send_response(200)
            self.send_header('Content-Type', 'image/jpeg')
            self.send_header('Content-Length', str(len(jpeg)))
            self.end_headers()
            self.wfile.write(jpeg.tobytes())

        elif self.path == '/stream-ai':
            # Live stream of only the frames AI is processing (~4fps)
            self.send_response(200)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()

            last_count = -1
            while True:
                with det_lock:
                    count = det_result["det_count"] + det_result.get("_inf_total", 0)
                with ai_frame_lock:
                    frame = ai_frame

                if frame is None or count == last_count:
                    time.sleep(0.05)
                    continue
                last_count = count

                _, jpeg = cv2.imencode('.jpg', frame, [cv2.IMWRITE_JPEG_QUALITY, 90])
                data = jpeg.tobytes()
                try:
                    self.wfile.write(b'--frame\r\n')
                    self.wfile.write(b'Content-Type: image/jpeg\r\n')
                    self.wfile.write(f'Content-Length: {len(data)}\r\n\r\n'.encode())
                    self.wfile.write(data)
                    self.wfile.write(b'\r\n')
                except (BrokenPipeError, ConnectionResetError):
                    break

        elif self.path == '/':
            det_mode = "THREADED" if WITH_DETECTION else "OFF"
            ai_links = ""
            if WITH_DETECTION:
                ai_links = """<p><a href="/stream-ai" style="color:#0ff">AI Input Stream (~4fps)</a> |
<a href="/ai-snapshot" style="color:#0ff">AI Snapshot</a>
— see exactly what the model sees (check for blur/smear)</p>"""
            html = f"""<html><head><title>Drone Camera (Fast)</title></head>
<body style="background:#111;color:#fff;text-align:center;font-family:monospace">
<h2>SAR Drone Camera Feed (Fast Stream)</h2>
<img src="/stream" style="max-width:100%;border:2px solid #0f0"/>
<p>Resolution: {STREAM_W}x{STREAM_H} | FPS: {TARGET_FPS} | Quality: {JPEG_QUALITY}%</p>
<p>Detection: {det_mode}</p>
{ai_links}
</body></html>"""
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(html.encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass


def detection_thread(eyes):
    """Background thread: runs AI detection on latest frame continuously."""
    global det_result, ai_frame
    inf_count = 0
    inf_start = time.time()

    while True:
        # Grab the latest frame
        with frame_lock:
            frame = latest_frame

        if frame is None:
            time.sleep(0.05)
            continue

        # Save the exact frame being fed to AI (for blur inspection)
        with ai_frame_lock:
            ai_frame = frame.copy()

        # Run AI inference (this is the slow part: ~250ms)
        found, px, py, conf = eyes.detect_in_image(frame)
        inf_count += 1

        elapsed = time.time() - inf_start
        inf_fps = inf_count / elapsed if elapsed > 0 else 0

        # Compute direction
        h, w = frame.shape[:2]
        cx, cy = w // 2, h // 2
        direction = ""
        if found:
            margin = w // 6
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

        # Store result for main thread to draw
        with det_lock:
            old_count = det_result["det_count"]
            det_result = {
                "found": found,
                "px": px if found else 0,
                "py": py if found else 0,
                "conf": conf if found else 0.0,
                "direction": direction,
                "det_count": old_count + (1 if found else 0),
                "inf_fps": inf_fps,
                "_inf_total": inf_count,
            }

        if found:
            print(f"  ** DETECTED ** conf={conf:.2f} at ({px},{py}) -> {direction}  [AI: {inf_fps:.1f} fps]")


def draw_detection_overlay(frame, result):
    """Draw detection overlay on frame using latest AI result."""
    h, w = frame.shape[:2]
    cx, cy = w // 2, h // 2

    if result["found"]:
        px, py = int(result["px"]), int(result["py"])
        conf = result["conf"]
        direction = result["direction"]

        cv2.circle(frame, (px, py), 15, (0, 255, 0), 2)
        cv2.line(frame, (cx, cy), (px, py), (0, 255, 0), 2)

        color = (0, 255, 0) if direction == "CENTRED" else (0, 255, 255)
        cv2.putText(frame, direction, (cx - 60, h - 20),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, color, 2)
        cv2.putText(frame, f"TARGET conf={conf:.2f}", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 2)
    else:
        cv2.putText(frame, "NO TARGET", (10, 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

    # Show AI inference FPS
    cv2.putText(frame, f"AI: {result['inf_fps']:.1f} fps", (w - 130, 20),
                cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 200, 200), 1)


def main():
    global latest_frame

    print()
    print("=" * 60)
    print("   CAMERA STREAM (FAST) — Threaded detection")
    print("=" * 60)
    print()
    print(f"  Stream:     {STREAM_W}x{STREAM_H} @ {TARGET_FPS}fps")
    print(f"  Quality:    {JPEG_QUALITY}%")
    print(f"  Detection:  {'THREADED' if WITH_DETECTION else 'OFF'}")
    print(f"  Port:       {PORT}")
    print(f"  Headless:   {HEADLESS}")
    print()

    # ── Camera + AI — same as passive_flight.py ──
    from vision import VisionSystem
    model_path = os.path.join(project_root, "best.tflite")

    if WITH_DETECTION:
        print(f"  Loading AI model: {model_path}")
        eyes = VisionSystem(camera_index=0, model_path=model_path)
        if not eyes.using_ai:
            print("  [WARN] AI model not loaded — camera only, no detection")
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
    print(f"    http://{pi_ip}:{PORT}/stream       (live MJPEG)")
    print(f"    http://{pi_ip}:{PORT}/snapshot     (single frame)")
    if WITH_DETECTION:
        print(f"    http://{pi_ip}:{PORT}/stream-ai    (AI input frames ~4fps)")
        print(f"    http://{pi_ip}:{PORT}/ai-snapshot  (last frame fed to AI)")
    print()

    # Start HTTP server in background thread
    server = HTTPServer(('0.0.0.0', PORT), StreamHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    print(f"  HTTP server started on port {PORT}")

    # Start detection thread (if enabled)
    if WITH_DETECTION and eyes.using_ai:
        det_thread = threading.Thread(target=detection_thread, args=(eyes,), daemon=True)
        det_thread.start()
        print("  Detection thread started (AI runs in background)")
    print()

    # ── Camera loop — grabs frames as fast as possible ──
    frame_count = 0
    start = time.time()

    print("  Camera loop running...")

    try:
        while True:
            frame = eyes.get_frame()
            if frame is None:
                time.sleep(0.05)
                continue

            frame_count += 1
            h, w = frame.shape[:2]
            cx, cy = w // 2, h // 2

            # Draw detection overlay from background thread results
            if WITH_DETECTION and eyes.using_ai:
                with det_lock:
                    result = dict(det_result)
                draw_detection_overlay(frame, result)

            # Crosshair
            cv2.drawMarker(frame, (cx, cy), (0, 255, 255),
                            cv2.MARKER_CROSS, 20, 1)

            # Stats
            elapsed = time.time() - start
            fps = frame_count / elapsed if elapsed > 0 else 0
            det_count = det_result["det_count"] if WITH_DETECTION else 0
            det_rate = det_count / frame_count * 100 if frame_count > 0 else 0
            cv2.putText(frame, f"FPS:{fps:.1f} Det:{det_rate:.0f}%",
                         (5, h - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

            # Update frame for HTTP streaming
            with frame_lock:
                latest_frame = frame

            if not HEADLESS:
                cv2.imshow("Pi Camera (Fast)", frame)
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q') or key == 27:
                    break

            if frame_count % 60 == 0:
                ai_fps = det_result["inf_fps"] if WITH_DETECTION else 0
                print(f"  #{frame_count} Stream:{fps:.1f}fps AI:{ai_fps:.1f}fps Det:{det_count}/{frame_count} ({det_rate:.0f}%)")

    except KeyboardInterrupt:
        pass

    if not HEADLESS:
        cv2.destroyAllWindows()
    eyes.release()
    server.shutdown()
    print("\n  Stream stopped.")


if __name__ == "__main__":
    main()
