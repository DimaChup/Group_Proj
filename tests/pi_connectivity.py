#!/usr/bin/env python3
"""
Quick connectivity check — what's talking to what?

Usage:
    python tests/pi_connectivity.py

Shows status of all connections in one clear view.
"""
import sys
import os
import time
import socket

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check(name, func):
    """Run a check, print result."""
    try:
        ok, detail = func()
        status = "OK" if ok else "FAIL"
        symbol = "+" if ok else "X"
        print(f"  [{symbol}] {name:22s}  {detail}")
        return ok
    except Exception as e:
        print(f"  [X] {name:22s}  ERROR: {e}")
        return False


def check_camera_opencv():
    """Try OpenCV camera (laptop webcam)."""
    import cv2
    cap = cv2.VideoCapture(0)
    if cap.isOpened():
        ret, frame = cap.read()
        cap.release()
        if ret:
            return True, f"{frame.shape[1]}x{frame.shape[0]} via OpenCV"
        return False, "Opened but no frames"
    cap.release()
    return False, "Not available"


def check_camera_picamera2():
    """Try picamera2 (Pi CSI camera)."""
    from picamera2 import Picamera2
    cam = Picamera2()
    cam.configure(cam.create_preview_configuration(
        main={"size": (640, 480), "format": "RGB888"}
    ))
    cam.start()
    time.sleep(0.5)
    frame = cam.capture_array()
    cam.stop()
    cam.close()
    return True, f"{frame.shape[1]}x{frame.shape[0]} via picamera2"


def check_camera():
    """Try OpenCV first, then picamera2."""
    try:
        return check_camera_opencv()
    except Exception:
        pass
    try:
        return check_camera_picamera2()
    except Exception as e:
        return False, f"No camera: {e}"


def check_ai_model():
    """Check if best.tflite loads."""
    model_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "best.tflite")
    if not os.path.exists(model_path):
        return False, "best.tflite NOT FOUND"

    size_mb = os.path.getsize(model_path) / (1024 * 1024)

    # Try loading
    from vision import VisionSystem
    v = VisionSystem(camera_index=None, model_path="best.tflite")
    if v.using_ai:
        backend = "TFLite" if v._use_tflite_direct else "Ultralytics"
        return True, f"best.tflite ({size_mb:.1f}MB) via {backend}"
    return False, f"best.tflite exists ({size_mb:.1f}MB) but failed to load"


def check_cube_udp():
    """Check Cube via mavproxy UDP bridge (udpin:0.0.0.0:14550)."""
    from pymavlink import mavutil
    mav = mavutil.mavlink_connection("udpin:0.0.0.0:14550")

    # Try to get heartbeat
    msg = mav.recv_match(type='HEARTBEAT', blocking=True, timeout=3)
    if msg is None:
        mav.close()
        return False, "No heartbeat (is mavproxy running?)"

    # Get vehicle info
    autopilot = msg.autopilot  # 3 = ArduPilot
    vtype = msg.type  # 2 = quadcopter

    # Try to get GPS
    gps_msg = mav.recv_match(type='GLOBAL_POSITION_INT', blocking=True, timeout=2)
    gps_info = ""
    if gps_msg:
        lat = gps_msg.lat / 1e7
        lon = gps_msg.lon / 1e7
        alt = gps_msg.relative_alt / 1000.0
        if abs(lat) > 0.1:
            gps_info = f", GPS: {lat:.5f},{lon:.5f} alt={alt:.1f}m"
        else:
            gps_info = ", GPS: no fix"

    # Try to get battery
    bat_msg = mav.recv_match(type='SYS_STATUS', blocking=True, timeout=2)
    bat_info = ""
    if bat_msg and bat_msg.voltage_battery > 0:
        bat_info = f", Battery: {bat_msg.voltage_battery/1000:.1f}V"

    mav.close()
    return True, f"Heartbeat OK (ArduPilot quad){gps_info}{bat_info}"


def check_mavproxy_running():
    """Check if mavproxy process is running."""
    import subprocess
    try:
        result = subprocess.run(["pgrep", "-f", "mavproxy"], capture_output=True, text=True, timeout=3)
        if result.stdout.strip():
            return True, f"PID {result.stdout.strip().split()[0]}"
        return False, "Not running — start it first!"
    except FileNotFoundError:
        # Windows — can't check
        return True, "(can't verify on Windows)"
    except Exception as e:
        return False, str(e)


def check_mission_planner_port():
    """Check if TCP port 5762 is listening (for Mission Planner)."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.bind(("0.0.0.0", 5762))
        sock.close()
        # If we can bind, nothing is listening — mavproxy tcpin not active
        return False, "Port 5762 not listening (add --out=tcpin:0.0.0.0:5762 to mavproxy)"
    except OSError:
        # Port in use = mavproxy is listening = good
        return True, "Port 5762 listening (Mission Planner can connect)"


def check_config():
    """Show config.py connection settings."""
    import config
    mode = config.MODE
    conn = config.CONNECTION_STR
    return True, f"MODE={mode}, CONN={conn}"


# ── Main ─────────────────────────────────────────────────────
def main():
    print()
    print("=" * 60)
    print("   CONNECTIVITY CHECK — What's talking to what?")
    print("=" * 60)

    # Architecture diagram
    print()
    print("   Expected setup:")
    print("   ┌────────┐  serial  ┌────┐  mavproxy  ┌────────────┐")
    print("   │  Cube  │─────────>│ Pi │────UDP─────>│ Pi scripts │")
    print("   └────────┘          └────┘────TCP─────>│ Mission    │")
    print("   ┌────────┐   CSI      │                │ Planner    │")
    print("   │ Camera │───────────>│                │ (laptop)   │")
    print("   └────────┘            │                └────────────┘")
    print()

    print("─" * 60)
    results = {}

    # 1. Config
    print("\n  CONFIG:")
    results['config'] = check("config.py", check_config)

    # 2. Camera
    print("\n  CAMERA:")
    results['camera'] = check("Camera", check_camera)

    # 3. AI Model
    print("\n  AI MODEL:")
    results['model'] = check("AI Model (TFLite)", check_ai_model)

    # 4. Mavproxy
    print("\n  CUBE CONNECTION:")
    results['mavproxy'] = check("Mavproxy process", check_mavproxy_running)

    if results['mavproxy']:
        results['cube'] = check("Cube heartbeat (UDP)", check_cube_udp)
        results['mp_port'] = check("Mission Planner port", check_mission_planner_port)
    else:
        print("  [X] Cube heartbeat (UDP)    Skipped (mavproxy not running)")
        print("  [X] Mission Planner port    Skipped (mavproxy not running)")
        print()
        print("  START MAVPROXY FIRST:")
        print("  sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \\")
        print("    --master=/dev/ttyAMA0 --baudrate=921600 --streamrate=10 \\")
        print("    --out=udpout:127.0.0.1:14550 --out=tcpin:0.0.0.0:5762")
        results['cube'] = False
        results['mp_port'] = False

    # Summary
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    failed = total - passed

    print()
    print("─" * 60)
    if failed == 0:
        print(f"  ALL {total} CHECKS PASSED — ready to go!")
    else:
        print(f"  {passed}/{total} passed, {failed} failed")

        if not results.get('camera'):
            print("    Fix: Is camera ribbon connected? Run: libcamera-hello")
        if not results.get('model'):
            print("    Fix: Is best.tflite in project root?")
        if not results.get('mavproxy'):
            print("    Fix: Start mavproxy (see command above)")
        if not results.get('cube'):
            print("    Fix: Is Cube powered? Check serial cable.")

    print()
    return failed == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
