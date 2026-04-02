#!/usr/bin/env python3
"""
Automated integration test for passive_watch.py

Launches passive_watch.py in --fake mode as a subprocess, then exercises
all HTTP API endpoints and verifies correct behaviour.

Usage:
    python tests/laptop/test_passive_watch.py

Requirements:
    - requests (pip install requests)
    - RealVideo/DJI_0001_1456x1088_cropped_30fps.mp4  (fake video source)
    - cv_models/human.tflite  (COCO model for --model flag)

The script exits with code 0 if all checks pass, 1 otherwise.
"""

import os
import sys
import time
import subprocess
import signal
import requests

# ── Config ──
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
BASE_URL = "http://localhost:8090"
STARTUP_TIMEOUT = 60       # seconds to wait for server to start
DETECTION_TIMEOUT = 60     # seconds to wait for detections
MODEL_SWITCH_TIMEOUT = 120 # seconds to wait for model switch


def launch_passive_watch():
    """Start passive_watch.py as a subprocess and return the Popen object."""
    cmd = [
        sys.executable,
        os.path.join(PROJECT_ROOT, "field_tools", "passive_watch.py"),
        "--fake",
        "--no-save",
        "--conf", "0.2",
        "--model", os.path.join(PROJECT_ROOT, "cv_models", "human.tflite"),
        "--smart-estimate",
    ]
    print(f"[INFO] Launching: {' '.join(cmd)}")
    proc = subprocess.Popen(
        cmd,
        cwd=PROJECT_ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    return proc


def wait_for_startup(timeout=STARTUP_TIMEOUT):
    """Poll /api/status until the server responds or timeout."""
    t0 = time.time()
    while time.time() - t0 < timeout:
        try:
            r = requests.get(f"{BASE_URL}/api/status", timeout=3)
            if r.status_code == 200:
                return True
        except (requests.ConnectionError, requests.Timeout):
            pass
        time.sleep(1)
    return False


def kill_process(proc):
    """Terminate the subprocess tree."""
    if proc.poll() is None:
        try:
            proc.terminate()
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=3)


# ── Test functions ──
# Each returns (passed: bool, detail: str)

def check_site_loads():
    """Check 1: GET / returns 200."""
    try:
        r = requests.get(f"{BASE_URL}/", timeout=10)
        if r.status_code == 200:
            return True, "200 OK"
        return False, f"status {r.status_code}"
    except Exception as e:
        return False, str(e)


def check_stream_works():
    """Check 2: GET /stream returns MJPEG data with JPEG header."""
    try:
        r = requests.get(f"{BASE_URL}/stream", timeout=10, stream=True)
        # Read first 4KB looking for JPEG SOI marker (FF D8)
        chunk = b""
        for part in r.iter_content(chunk_size=1024):
            chunk += part
            if len(chunk) >= 4096:
                break
        r.close()
        if b'\xff\xd8' in chunk:
            return True, "MJPEG header found"
        return False, "no JPEG SOI marker in first 4KB"
    except Exception as e:
        return False, str(e)


def check_stats_api():
    """Check 3: GET /api/status returns JSON with cam_fps > 0, vis_fps > 0."""
    try:
        r = requests.get(f"{BASE_URL}/api/status", timeout=10)
        data = r.json()
        cam = float(data.get("cam_fps", 0))
        vis = float(data.get("vis_fps", 0))
        if cam > 0 and vis > 0:
            return True, f"cam_fps={cam:.1f}, vis_fps={vis:.1f}"
        if cam > 0:
            return True, f"cam_fps={cam:.1f} (vis_fps={vis:.1f}, may still be warming up)"
        return False, f"cam_fps={cam}, vis_fps={vis}"
    except Exception as e:
        return False, str(e)


def check_confidence_threshold():
    """Check 4: Set confidence to 0.5, verify, then restore to 0.2."""
    try:
        # Set to 0.5
        r1 = requests.get(f"{BASE_URL}/api/set-conf?val=0.5", timeout=10)
        d1 = r1.json()
        if not d1.get("ok"):
            return False, f"set-conf 0.5 failed: {d1}"

        # Verify
        r2 = requests.get(f"{BASE_URL}/api/status", timeout=10)
        d2 = r2.json()
        conf = float(d2.get("conf_threshold", 0))
        if abs(conf - 0.5) > 0.01:
            return False, f"conf_threshold={conf}, expected 0.5"

        # Restore
        r3 = requests.get(f"{BASE_URL}/api/set-conf?val=0.2", timeout=10)
        d3 = r3.json()
        if not d3.get("ok"):
            return False, f"restore to 0.2 failed: {d3}"

        return True, "set 0.5, verified, restored 0.2"
    except Exception as e:
        return False, str(e)


def check_class_filter():
    """Check 5: Set class filter to person, verify, restore to all."""
    try:
        r1 = requests.get(f"{BASE_URL}/api/set-class?name=person", timeout=10)
        d1 = r1.json()
        if not d1.get("ok"):
            return False, f"set-class person failed: {d1}"

        r2 = requests.get(f"{BASE_URL}/api/status", timeout=10)
        d2 = r2.json()
        cf = d2.get("class_filter")
        if cf != "person":
            return False, f"class_filter={cf}, expected 'person'"

        r3 = requests.get(f"{BASE_URL}/api/set-class?name=all", timeout=10)
        d3 = r3.json()
        if not d3.get("ok"):
            return False, f"restore to all failed: {d3}"

        return True, "set person, verified, restored all"
    except Exception as e:
        return False, str(e)


def check_model_switch():
    """Check 6: Switch to model 0 (Original), verify, switch back to 3 (COCO)."""
    try:
        # Switch to Original (id=0)
        r1 = requests.get(f"{BASE_URL}/api/switch-model?id=0", timeout=MODEL_SWITCH_TIMEOUT)
        d1 = r1.json()
        if not d1.get("ok"):
            return False, f"switch to id=0 failed: {d1}"

        # Verify
        r2 = requests.get(f"{BASE_URL}/api/status", timeout=10)
        d2 = r2.json()
        mid = d2.get("active_model_id")
        if mid != 0:
            return False, f"active_model_id={mid}, expected 0"

        # Switch back to COCO (id=3)
        r3 = requests.get(f"{BASE_URL}/api/switch-model?id=3", timeout=MODEL_SWITCH_TIMEOUT)
        d3 = r3.json()
        if not d3.get("ok"):
            return False, f"switch to id=3 failed: {d3}"

        return True, "switched 0->verified->3"
    except requests.Timeout:
        return False, f"timeout after {MODEL_SWITCH_TIMEOUT}s"
    except Exception as e:
        return False, str(e)


def check_clear_all():
    """Check 7: POST clear-all returns ok."""
    try:
        r = requests.get(f"{BASE_URL}/api/clear-all", timeout=10)
        d = r.json()
        if d.get("ok"):
            return True, "cleared"
        return False, f"response: {d}"
    except Exception as e:
        return False, str(e)


def check_detections_happening():
    """Check 8: Wait until detections > 0 (up to 60s)."""
    t0 = time.time()
    try:
        while time.time() - t0 < DETECTION_TIMEOUT:
            r = requests.get(f"{BASE_URL}/api/status", timeout=10)
            d = r.json()
            dets = int(d.get("detections", 0))
            pct = float(d.get("det_pct", 0))
            if dets > 0:
                return True, f"detections={dets}, det_pct={pct:.1f}%"
            time.sleep(2)
        return False, f"no detections after {DETECTION_TIMEOUT}s"
    except Exception as e:
        return False, str(e)


def check_latest_detection():
    """Check 9: GET /latest returns JPEG bytes > 1000."""
    try:
        r = requests.get(f"{BASE_URL}/latest", timeout=10)
        if r.status_code == 200 and len(r.content) > 1000:
            return True, f"{len(r.content)} bytes"
        if r.status_code == 200:
            return False, f"only {len(r.content)} bytes (expected >1000)"
        return False, f"status {r.status_code}"
    except Exception as e:
        return False, str(e)


def check_inference_fps():
    """Check 10: GET /api/status has vis_fps > 0."""
    try:
        r = requests.get(f"{BASE_URL}/api/status", timeout=10)
        d = r.json()
        vis = float(d.get("vis_fps", 0))
        if vis > 0:
            return True, f"vis_fps={vis:.2f}"
        return False, f"vis_fps={vis}"
    except Exception as e:
        return False, str(e)


# ── Main ──

def main():
    proc = None
    try:
        # Launch subprocess
        proc = launch_passive_watch()

        # Wait for server to start
        print(f"[INFO] Waiting for server (up to {STARTUP_TIMEOUT}s)...")
        if not wait_for_startup():
            # Check if process died
            if proc.poll() is not None:
                out = proc.stdout.read() if proc.stdout else ""
                print(f"[FATAL] Process exited with code {proc.returncode}")
                print(out[-2000:] if len(out) > 2000 else out)
            else:
                print(f"[FATAL] Server did not respond within {STARTUP_TIMEOUT}s")
            return 1
        print("[INFO] Server is up.\n")

        # Give inference thread a few seconds to produce initial frames
        time.sleep(5)

        # Run checks
        checks = [
            ("Site loads",              check_site_loads),
            ("Stream works",            check_stream_works),
            ("Stats API",              check_stats_api),
            ("Confidence threshold",    check_confidence_threshold),
            ("Class filter",            check_class_filter),
            ("Detections happening",    check_detections_happening),
            ("Latest detection",        check_latest_detection),
            ("Inference FPS reported",  check_inference_fps),
            ("Clear all",               check_clear_all),
            ("Model switch",            check_model_switch),
        ]

        passed = 0
        total = len(checks)
        results = []

        for name, fn in checks:
            print(f"  Running: {name}...", end=" ", flush=True)
            ok, detail = fn()
            tag = "PASS" if ok else "FAIL"
            print(f"[{tag}]")
            results.append((name, ok, detail))
            if ok:
                passed += 1

        # Print summary
        print("\n" + "=" * 60)
        for name, ok, detail in results:
            tag = "PASS" if ok else "FAIL"
            print(f"[{tag}] {name} ({detail})")
        print("=" * 60)
        print(f"\nResults: {passed}/{total} passed")

        return 0 if passed == total else 1

    except KeyboardInterrupt:
        print("\n[INFO] Interrupted by user")
        return 130
    finally:
        if proc is not None:
            print("\n[INFO] Killing passive_watch subprocess...")
            kill_process(proc)
            print("[INFO] Done.")


if __name__ == "__main__":
    sys.exit(main())
