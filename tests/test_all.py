#!/usr/bin/env python3
"""
Full system connectivity test. Checks every link and shows
a connectivity map of what talks to what.

Usage: python tests/test_all.py
"""
import sys
import os
import socket
import platform
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ===========================================
#          CHECKS (self-contained)
# ==========================================

def detect_platform():
    if platform.system() == "Windows":
        return "WINDOWS"
    try:
        with open("/proc/version", "r") as f:
            if "microsoft" in f.read().lower():
                return "WSL"
    except Exception:
        pass
    try:
        with open("/proc/cpuinfo", "r") as f:
            if "raspberry" in f.read().lower():
                return "PI"
    except Exception:
        pass
    return "LINUX"

def check_tcp(host, port, timeout=3):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        sock.close()
        return True, f"{host}:{port} OPEN"
    except socket.timeout:
        return False, f"{host}:{port} TIMEOUT"
    except ConnectionRefusedError:
        return False, f"{host}:{port} REFUSED"
    except OSError as e:
        return False, f"{host}:{port} {e}"

def check_serial(path):
    if os.path.exists(path):
        return True, f"{path} EXISTS"
    return False, f"{path} NOT FOUND"

def check_heartbeat(conn_str, baud=57600, timeout=5):
    try:
        from pymavlink import mavutil
        if conn_str.startswith("/dev/"):
            m = mavutil.mavlink_connection(conn_str, baud=baud)
        else:
            m = mavutil.mavlink_connection(conn_str)
        hb = m.wait_heartbeat(timeout=timeout)
        m.close()
        if hb:
            return True, f"System {hb.get_srcSystem()}"
        return False, "No heartbeat"
    except ImportError:
        return False, "pymavlink not installed"
    except Exception as e:
        return False, str(e)

def check_camera(index=0):
    try:
        import cv2
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                return True, f"{frame.shape[1]}x{frame.shape[0]}"
        cap.release()
    except ImportError:
        return False, "OpenCV not installed"
    except Exception:
        pass
    return False, "NOT AVAILABLE"

def check_model(model_path="best.tflite"):
    if not os.path.exists(model_path):
        return False, "File not found"
    try:
        from vision import VisionSystem
        v = VisionSystem(camera_index=None, model_path=model_path)
        if v.using_ai:
            backend = "TFLite" if v._use_tflite_direct else "Ultralytics"
            return True, backend
        return False, "No backend"
    except Exception as e:
        return False, str(e)

# ==========================================
#          MAIN
# ==========================================

def main():
    print("=" * 55)
    print("         FULL SYSTEM CONNECTIVITY TEST")
    print("=" * 55)

    plat = detect_platform()

    # Load config
    try:
        import config
        conn_str = config.CONNECTION_STR
        baud = config.BAUD_RATE
        mode = config.MODE
    except Exception:
        conn_str = "tcp:127.0.0.1:5762"
        baud = 57600
        mode = "SIMULATION"

    print(f"\n  Platform:   {plat}")
    print(f"  Mode:       {mode}")
    print(f"  Connection: {conn_str}")

    # --- Run all checks ---
    print(f"\n{'─' * 55}")
    results = {}

    # 1. Connection (TCP or Serial)
    if conn_str.startswith("tcp:"):
        parts = conn_str.replace("tcp:", "").split(":")
        host, port = parts[0], int(parts[1])
        ok, msg = check_tcp(host, port)
        results["LINK"] = (ok, f"TCP {msg}")
    elif conn_str.startswith("/dev/"):
        ok, msg = check_serial(conn_str)
        results["LINK"] = (ok, f"Serial {msg}")
    else:
        results["LINK"] = (False, f"Unknown: {conn_str}")

    # 2. Heartbeat
    if results["LINK"][0]:
        ok, msg = check_heartbeat(conn_str, baud)
        results["HEARTBEAT"] = (ok, msg)
    else:
        results["HEARTBEAT"] = (None, "Skipped")

    # 3. Camera
    if mode == "REAL":
        ok, msg = check_camera(0)
        results["CAMERA"] = (ok, msg)
    else:
        results["CAMERA"] = (None, "Skipped (SIM)")

    # 4. AI Model
    ok, msg = check_model()
    results["AI MODEL"] = (ok, msg)

    # --- Print results table ---
    print(f"\n  {'Check':<14} {'Status':<8} {'Details'}")
    print(f"  {'─'*14} {'─'*8} {'─'*28}")
    for name, (ok, msg) in results.items():
        if ok is True:
            status = "OK"
        elif ok is False:
            status = "FAIL"
        else:
            status = "SKIP"
        print(f"  {name:<14} {status:<8} {msg}")

    # --- Connectivity Map ---
    link_ok = results["LINK"][0] is True
    hb_ok = results["HEARTBEAT"][0] is True
    cam_ok = results["CAMERA"][0] is True
    ai_ok = results["AI MODEL"][0] is True

    print(f"\n{'─' * 55}")
    print("  CONNECTIVITY MAP")
    print(f"{'─' * 55}\n")

    if plat in ("WINDOWS", "WSL"):
        # Laptop/Dev setup
        fc_label = "SITL/Mission Planner"
        link_label = "TCP"
    else:
        # Pi setup
        fc_label = "Cube (FC)"
        link_label = "Serial"

    link_arrow = "<=====>" if (link_ok and hb_ok) else "- - X -" if not link_ok else "<=?=?=>"
    cam_arrow = "<=====>" if cam_ok else "- - - -" if results["CAMERA"][0] is None else "- - X -"
    ai_arrow = "[loaded]" if ai_ok else "[ FAIL ]"

    if plat == "PI" or mode == "REAL":
        print(f"  +------------------+    {link_label}     +------------------+")
        print(f"  | Raspberry Pi     |{link_arrow}| {fc_label:<16} |")
        print(f"  |                  |             +------------------+")
        print(f"  |  AI Model {ai_arrow}|")
        print(f"  |                  |")
        print(f"  |  Camera  {cam_arrow} |")
        print(f"  +------------------+")
    else:
        print(f"  +------------------+    {link_label}     +------------------+")
        print(f"  | This Machine     |{link_arrow}| {fc_label:<16} |")
        print(f"  |                  |             +------------------+")
        print(f"  |  AI Model {ai_arrow}|")
        print(f"  +------------------+")

    # --- Summary ---
    fails = [k for k, (ok, _) in results.items() if ok is False]
    passes = [k for k, (ok, _) in results.items() if ok is True]

    print(f"\n{'─' * 55}")
    if fails:
        print(f"  ISSUES ({len(fails)}):")
        for f in fails:
            print(f"    - {f}: {results[f][1]}")

        if "LINK" in fails and plat == "WSL":
            print("\n  WSL TIP: Check firewall:")
            print("    netsh advfirewall firewall add rule name=\"SITL\" dir=in action=allow protocol=TCP localport=5762")
        if "HEARTBEAT" in fails:
            print("\n  TIP: Is the flight controller / SITL running?")
        if "CAMERA" in fails:
            print("\n  TIP: Check camera wiring. Try: libcamera-hello")
        if "AI MODEL" in fails:
            print("\n  TIP: Is best.tflite in the project root?")
    else:
        print(f"  ALL CHECKS PASSED ({len(passes)}/{len(passes)})")
        print(f"  Ready: python main.py")

    print(f"{'─' * 55}\n")
    return len(fails) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
