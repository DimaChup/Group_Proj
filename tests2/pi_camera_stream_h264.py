#!/usr/bin/env python3
"""
Camera Stream (H.264) — FFmpeg-based stream to ground station.

Alternative to pi_camera_stream.py (MJPEG). Uses FFmpeg to encode
H.264 video served as HLS — much lower bandwidth but more complex.

Comparison:
  MJPEG (pi_camera_stream.py):  ~0.5 Mbps, zero deps, any browser
  H.264 (this script):          ~0.05 Mbps, needs ffmpeg, uses hls.js

Requirements:
  Pi:  sudo apt install ffmpeg
  GS:  just a browser (hls.js loaded from CDN)

How it works:
  1. Python captures frames from camera (OpenCV or picamera2)
  2. Optionally runs AI detection overlay on each frame
  3. Pipes raw frames to ffmpeg subprocess
  4. ffmpeg encodes H.264 → HLS segments (.ts files + .m3u8 playlist)
  5. Built-in HTTP server serves HLS files + HTML player page
  6. Browser loads hls.js which plays the .m3u8 stream

Ground station:
  Open browser to http://<PI_IP>:8091/
  (different port from MJPEG so both can run simultaneously)

Options:
  --port 8091         HTTP port (default 8091)
  --fps 5             Target FPS (default 5)
  --bitrate 200k      H.264 bitrate (default 200k)
  --with-detection    Run AI detection overlay
  --headless          No local display

Usage:
  python tests2/pi_camera_stream_h264.py
  python tests2/pi_camera_stream_h264.py --with-detection
  python tests2/pi_camera_stream_h264.py --bitrate 500k --fps 10
"""
import sys
import os
import time
import shutil
import signal
import tempfile
import subprocess
import threading
from http.server import HTTPServer, SimpleHTTPRequestHandler

script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(script_dir)
sys.path.insert(0, project_root)

import cv2
import numpy as np

# --- Parse args ---
PORT = 8091
TARGET_FPS = 5
BITRATE = "200k"
WITH_DETECTION = "--with-detection" in sys.argv
HEADLESS = "--headless" in sys.argv

for i, arg in enumerate(sys.argv):
    if arg == "--port" and i + 1 < len(sys.argv):
        PORT = int(sys.argv[i + 1])
    elif arg == "--fps" and i + 1 < len(sys.argv):
        TARGET_FPS = int(sys.argv[i + 1])
    elif arg == "--bitrate" and i + 1 < len(sys.argv):
        BITRATE = sys.argv[i + 1]

# HLS output directory
HLS_DIR = tempfile.mkdtemp(prefix="hls_stream_")
running = True


def check_ffmpeg():
    """Check if ffmpeg is installed."""
    if shutil.which("ffmpeg") is None:
        print("  [FAIL] ffmpeg not found!")
        print("  Install with: sudo apt install ffmpeg")
        return False
    result = subprocess.run(["ffmpeg", "-version"], capture_output=True, text=True)
    version = result.stdout.split("\n")[0] if result.stdout else "unknown"
    print(f"  ffmpeg: {version}")
    return True


def setup_camera():
    """Open camera directly (same as MJPEG version)."""
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, test = cap.read()
        if ret:
            h, w = test.shape[:2]
            print(f"  Camera: OpenCV ({w}x{h})")
            return cap, None
        else:
            cap.release()

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


def get_frame(cap, picam):
    """Grab a frame."""
    if cap:
        ret, f = cap.read()
        return f if ret else None
    if picam:
        f = picam.capture_array()
        return f
    return None


class HLSHandler(SimpleHTTPRequestHandler):
    """Serve HLS files + player page."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=HLS_DIR, **kwargs)

    def do_GET(self):
        if self.path == '/':
            self.send_player_page()
        elif self.path == '/status':
            self.send_response(200)
            self.send_header('Content-Type', 'text/plain')
            self.end_headers()
            self.wfile.write(b'ok')
        else:
            # Add CORS headers for hls.js
            super().do_GET()

    def end_headers(self):
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Cache-Control', 'no-cache')
        super().end_headers()

    def send_player_page(self):
        html = f"""<!DOCTYPE html>
<html><head>
<title>Drone Camera (H.264)</title>
<script src="https://cdn.jsdelivr.net/npm/hls.js@latest"></script>
</head>
<body style="background:#111;color:#fff;text-align:center;font-family:monospace">
<h2>SAR Drone Camera Feed (H.264/HLS)</h2>
<video id="video" style="max-width:100%;border:2px solid #0f0" controls autoplay muted></video>
<p>Bitrate: {BITRATE} | FPS: {TARGET_FPS} | Detection: {'ON' if WITH_DETECTION else 'OFF'}</p>
<p id="status" style="color:#888">Connecting...</p>
<script>
var video = document.getElementById('video');
var status = document.getElementById('status');
if (Hls.isSupported()) {{
    var hls = new Hls({{
        liveSyncDurationCount: 1,
        liveMaxLatencyDurationCount: 3,
        liveDurationInfinity: true,
        lowLatencyMode: true
    }});
    hls.loadSource('/stream.m3u8');
    hls.attachMedia(video);
    hls.on(Hls.Events.MANIFEST_PARSED, function() {{
        video.play();
        status.textContent = 'Stream connected';
        status.style.color = '#0f0';
    }});
    hls.on(Hls.Events.ERROR, function(event, data) {{
        if (data.fatal) {{
            status.textContent = 'Stream error — retrying...';
            status.style.color = '#f00';
            setTimeout(function() {{ hls.loadSource('/stream.m3u8'); }}, 2000);
        }}
    }});
}} else if (video.canPlayType('application/vnd.apple.mpegurl')) {{
    video.src = '/stream.m3u8';
    video.addEventListener('loadedmetadata', function() {{ video.play(); }});
}} else {{
    status.textContent = 'Browser does not support HLS';
    status.style.color = '#f00';
}}
</script>
</body></html>"""
        self.send_response(200)
        self.send_header('Content-Type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())

    def log_message(self, format, *args):
        pass


def camera_loop(cap, picam, eyes, ffmpeg_proc):
    """Capture frames, run detection, pipe to ffmpeg."""
    global running
    frame_count = 0
    det_count = 0
    start = time.time()

    can_detect = WITH_DETECTION and eyes is not None and eyes.using_ai
    print(f"  Camera loop running... (detection={'ON' if can_detect else 'OFF'})")

    frame_interval = 1.0 / TARGET_FPS

    while running:
        t0 = time.time()

        frame = get_frame(cap, picam)
        if frame is None:
            time.sleep(0.05)
            continue

        frame_count += 1
        h, w = frame.shape[:2]
        cx, cy = w // 2, h // 2

        # Detection
        found = False
        if can_detect:
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
            else:
                cv2.putText(frame, "NO TARGET", (10, 30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)

        # Crosshair + stats
        cv2.drawMarker(frame, (cx, cy), (0, 255, 255), cv2.MARKER_CROSS, 20, 1)
        elapsed = time.time() - start
        fps = frame_count / elapsed if elapsed > 0 else 0
        det_rate = det_count / frame_count * 100 if frame_count > 0 else 0
        cv2.putText(frame, f"FPS:{fps:.1f} Det:{det_rate:.0f}%",
                     (5, h - 5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

        # Pipe frame to ffmpeg
        try:
            ffmpeg_proc.stdin.write(frame.tobytes())
        except (BrokenPipeError, OSError):
            print("  [WARN] ffmpeg pipe broken — stopping")
            break

        if not HEADLESS:
            cv2.imshow("Pi Camera (H.264)", frame)
            key = cv2.waitKey(1) & 0xFF
            if key == ord('q') or key == 27:
                break

        if frame_count % 30 == 0:
            print(f"  #{frame_count} FPS:{fps:.1f} Det:{det_count}/{frame_count} ({det_rate:.0f}%)")

        # Rate limit to target FPS
        dt = time.time() - t0
        if dt < frame_interval:
            time.sleep(frame_interval - dt)

    running = False


def main():
    global running

    print()
    print("=" * 60)
    print("   CAMERA STREAM (H.264/HLS) — FFmpeg pipeline")
    print("=" * 60)
    print()
    print(f"  FPS:        {TARGET_FPS}")
    print(f"  Bitrate:    {BITRATE}")
    print(f"  Detection:  {'ON' if WITH_DETECTION else 'OFF'}")
    print(f"  Port:       {PORT}")
    print(f"  HLS dir:    {HLS_DIR}")
    print()

    # Check ffmpeg
    print("[1] Checking ffmpeg...")
    if not check_ffmpeg():
        return

    # Open camera
    print("\n[2] Opening camera...")
    cap, picam = setup_camera()
    if cap is None and picam is None:
        return

    # Get frame size
    test_frame = get_frame(cap, picam)
    if test_frame is None:
        print("  [FAIL] Can't grab test frame")
        return
    h, w = test_frame.shape[:2]
    print(f"  Frame size: {w}x{h}")

    # Load AI model
    eyes = None
    if WITH_DETECTION:
        print("\n[3] Loading AI model...")
        from vision import VisionSystem
        model_path = os.path.join(project_root, "best.tflite")
        eyes = VisionSystem(camera_index=None, model_path=model_path)
        if eyes.using_ai:
            backend = "TFLite" if eyes._use_tflite_direct else "Ultralytics"
            print(f"  AI backend: {backend}")
            # Warmup
            eyes.detect_in_image(np.zeros((480, 640, 3), dtype=np.uint8))
            print("  Warmup done")
        else:
            print("  [WARN] AI not loaded")

    # Start ffmpeg — raw BGR frames in, HLS segments out
    print("\n[4] Starting ffmpeg pipeline...")
    ffmpeg_cmd = [
        "ffmpeg",
        "-y",                           # overwrite
        "-f", "rawvideo",               # input format
        "-vcodec", "rawvideo",
        "-pix_fmt", "bgr24",            # OpenCV BGR
        "-s", f"{w}x{h}",              # frame size
        "-r", str(TARGET_FPS),          # input FPS
        "-i", "-",                      # read from stdin
        "-c:v", "libx264",             # H.264 codec
        "-preset", "ultrafast",         # lowest latency
        "-tune", "zerolatency",         # no buffering
        "-b:v", BITRATE,               # target bitrate
        "-g", str(TARGET_FPS),          # keyframe every 1 sec
        "-f", "hls",                    # output HLS
        "-hls_time", "1",              # 1 second segments
        "-hls_list_size", "3",         # keep 3 segments
        "-hls_flags", "delete_segments+append_list",
        "-hls_segment_filename", os.path.join(HLS_DIR, "seg_%03d.ts"),
        os.path.join(HLS_DIR, "stream.m3u8"),
    ]
    print(f"  Command: {' '.join(ffmpeg_cmd[:6])}... (truncated)")

    ffmpeg_proc = subprocess.Popen(
        ffmpeg_cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.PIPE,
    )
    print(f"  ffmpeg PID: {ffmpeg_proc.pid}")

    # Start HTTP server
    print(f"\n[5] Starting HTTP server on port {PORT}...")
    server = HTTPServer(('0.0.0.0', PORT), HLSHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()

    # Get IP
    pi_ip = "???"
    try:
        result = subprocess.run(['hostname', '-I'], capture_output=True, text=True, timeout=3)
        pi_ip = result.stdout.strip().split()[0]
    except Exception:
        pass

    print(f"\n  Open in browser on ground station:")
    print(f"    http://{pi_ip}:{PORT}/")
    print(f"\n  Note: HLS has ~2-4 sec latency (normal for H.264 segments)")
    print(f"  MJPEG version (lower latency): python tests2/pi_camera_stream.py")
    print()

    # Run camera loop
    try:
        camera_loop(cap, picam, eyes, ffmpeg_proc)
    except KeyboardInterrupt:
        pass

    # Cleanup
    running = False
    print("\n  Stopping...")

    try:
        ffmpeg_proc.stdin.close()
    except Exception:
        pass
    ffmpeg_proc.wait(timeout=5)

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

    # Clean up HLS temp files
    try:
        shutil.rmtree(HLS_DIR)
    except Exception:
        pass

    print("  Stream stopped.")


if __name__ == "__main__":
    main()
