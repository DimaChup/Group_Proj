#!/usr/bin/env python3
"""
passive_watch.py — Passive camera observer with web stream + auto snapshots.

ZERO commands sent to anything. Just watches, detects, streams, saves.

Run on Pi via SSH:
    cd ~/dima/Group_Proj
    source pienv/bin/activate
    DISPLAY= python passive_watch.py

Open in laptop browser:
    http://<PI_IP>:8090/          (stream page)
    http://<PI_IP>:8090/stream    (raw MJPEG)
    http://<PI_IP>:8090/snapshot  (latest detection frame)

Options:
    --port 8090         HTTP port (default 8090)
    --conf 0.4          Confidence threshold (default 0.4)
    --fps 5             Max inference FPS (default 5)
    --save-dir detections   Where to save snapshots (default: detections/)
    --no-save           Don't save snapshots, stream only
"""
import sys
import os
import time
import signal
import threading
import argparse
import subprocess
from http.server import HTTPServer, BaseHTTPRequestHandler
from socketserver import ThreadingMixIn

# Ensure Ctrl+C works
signal.signal(signal.SIGINT, signal.SIG_DFL)

# Headless OpenCV
if not os.environ.get('DISPLAY'):
    os.environ.pop('QT_QPA_PLATFORM', None)

import cv2
import numpy as np
from vision import VisionSystem

# ── Globals for streaming ──
latest_jpeg = None
latest_det_jpeg = None
frame_lock = threading.Lock()

# ── Args ──
parser = argparse.ArgumentParser(description="Passive camera watch + stream + snapshots")
parser.add_argument('--port', type=int, default=8090)
parser.add_argument('--conf', type=float, default=0.4)
parser.add_argument('--fps', type=float, default=5)
parser.add_argument('--save-dir', default='detections')
parser.add_argument('--no-save', action='store_true')
args = parser.parse_args()


# ── HTML page ──
HTML_PAGE = """<!DOCTYPE html>
<html><head><title>SAR Passive Watch</title>
<style>
  body { background:#111; color:#eee; font-family:monospace; margin:0; padding:20px; }
  h1 { color:#0f0; margin:0 0 10px; }
  .stats { color:#888; margin-bottom:10px; }
  img { max-width:100%; border:1px solid #333; }
</style>
</head><body>
<h1>SAR Passive Watch</h1>
<div class="stats" id="stats">Starting...</div>
<img src="/stream" alt="Camera Feed">
<script>
  setInterval(()=>{
    fetch('/api/status').then(r=>r.json()).then(d=>{
      document.getElementById('stats').textContent =
        `Frames: ${d.frames} | Detections: ${d.detections} (${d.det_pct}%) | FPS: ${d.fps} | Saved: ${d.saved}`;
    });
  }, 1000);
</script>
</body></html>"""


# ── HTTP Server ──
class Handler(BaseHTTPRequestHandler):
    def log_message(self, format, *a):
        pass  # silent

    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.end_headers()
            self.wfile.write(HTML_PAGE.encode())

        elif self.path == '/stream':
            self.send_response(200)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=frame')
            self.end_headers()
            while True:
                try:
                    with frame_lock:
                        jpeg = latest_jpeg
                    if jpeg:
                        self.wfile.write(b'--frame\r\n')
                        self.wfile.write(b'Content-Type: image/jpeg\r\n\r\n')
                        self.wfile.write(jpeg)
                        self.wfile.write(b'\r\n')
                    time.sleep(0.05)
                except BrokenPipeError:
                    break

        elif self.path == '/snapshot':
            with frame_lock:
                jpeg = latest_det_jpeg or latest_jpeg
            if jpeg:
                self.send_response(200)
                self.send_header('Content-Type', 'image/jpeg')
                self.end_headers()
                self.wfile.write(jpeg)
            else:
                self.send_response(503)
                self.end_headers()

        elif self.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            import json
            self.wfile.write(json.dumps(stats).encode())

        else:
            self.send_response(404)
            self.end_headers()


class ThreadedServer(ThreadingMixIn, HTTPServer):
    daemon_threads = True


# ── Stats ──
stats = {"frames": 0, "detections": 0, "det_pct": "0", "fps": "0.0", "saved": 0}


# ── Main ──
def main():
    global latest_jpeg, latest_det_jpeg

    # Auto-detect IP
    pi_ip = "localhost"
    try:
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True, timeout=3)
        ip = result.stdout.strip().split()[0]
        if ip:
            pi_ip = ip
    except Exception:
        pass

    print("=" * 50)
    print("  SAR PASSIVE WATCH")
    print("  Camera + Detection + Stream + Snapshots")
    print("  ZERO commands sent. Safe to run anytime.")
    print("=" * 50)
    print(f"  Confidence: {args.conf}")
    print(f"  Max FPS:    {args.fps}")
    if not args.no_save:
        os.makedirs(args.save_dir, exist_ok=True)
        print(f"  Saving to:  {args.save_dir}/")
    else:
        print("  Saving:     OFF")
    print()
    print(f"  Dashboard:  http://{pi_ip}:{args.port}/")
    print(f"  Stream:     http://{pi_ip}:{args.port}/stream")
    print(f"  Snapshot:   http://{pi_ip}:{args.port}/snapshot")
    print()

    # Start camera + AI
    eyes = VisionSystem(camera_index=0, model_path="best.tflite")
    if not eyes.using_ai:
        print("[WARN] AI model not loaded — stream only, no detection")
    print("[OK] Camera ready. Ctrl+C to stop.\n")

    # Start HTTP server
    server = ThreadedServer(('0.0.0.0', args.port), Handler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    print(f"[OK] Stream serving on port {args.port}\n")

    # Camera loop
    frame_count = 0
    det_count = 0
    saved_count = 0
    start_time = time.time()
    last_inference = 0
    min_interval = 1.0 / args.fps if args.fps > 0 else 0

    while True:
        frame = eyes.get_frame()
        if frame is None:
            time.sleep(0.01)
            continue

        frame_count += 1
        display = frame.copy()
        now = time.time()

        # Run detection (throttled)
        if eyes.using_ai and (now - last_inference) >= min_interval:
            last_inference = now
            found, x, y, conf = eyes.detect_in_image(frame)

            if found and conf >= args.conf:
                det_count += 1
                h, w = frame.shape[:2]
                cx, cy = int(x * w), int(y * h)
                box = 40

                # Draw on display frame
                cv2.rectangle(display, (cx - box, cy - box), (cx + box, cy + box), (0, 255, 0), 2)
                cv2.putText(display, f"{conf:.2f}", (cx - box, cy - box - 5),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

                # Save snapshot
                if not args.no_save:
                    saved_count += 1
                    fname = f"det_{saved_count:04d}_{conf:.2f}.jpg"
                    cv2.imwrite(os.path.join(args.save_dir, fname), display)

                # Update latest detection jpeg for /snapshot endpoint
                _, det_jpg = cv2.imencode('.jpg', display, [cv2.IMWRITE_JPEG_QUALITY, 85])
                with frame_lock:
                    latest_det_jpeg = det_jpg.tobytes()

        # Encode for stream
        _, jpg = cv2.imencode('.jpg', display, [cv2.IMWRITE_JPEG_QUALITY, 60])
        with frame_lock:
            latest_jpeg = jpg.tobytes()

        # Update stats
        elapsed = now - start_time
        fps = frame_count / elapsed if elapsed > 0 else 0
        det_pct = (det_count / frame_count * 100) if frame_count > 0 else 0
        stats.update({
            "frames": frame_count,
            "detections": det_count,
            "det_pct": f"{det_pct:.0f}",
            "fps": f"{fps:.1f}",
            "saved": saved_count,
        })

        # Terminal output every 50 frames
        if frame_count % 50 == 0:
            print(f"  #{frame_count} FPS:{fps:.1f} Det:{det_count} ({det_pct:.0f}%) Saved:{saved_count}")

    eyes.release()
    server.shutdown()


if __name__ == "__main__":
    main()
