#!/usr/bin/env python3
"""
Pre-flight connectivity test. Run before main.py to verify all links are working.
Auto-detects platform and connection - no hardcoded IPs.

Usage: python preflight.py
"""
import os
import sys
import socket
import platform
import subprocess

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# ==========================================
#          PLATFORM DETECTION
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

# ==========================================
#          INDIVIDUAL CHECKS
# ==========================================
def check_tcp(host, port, timeout=3):
    """Test if a TCP port is reachable."""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(timeout)
        sock.connect((host, port))
        sock.close()
        return True, f"{host}:{port} OPEN"
    except socket.timeout:
        return False, f"{host}:{port} TIMEOUT (is SITL/Mission Planner running?)"
    except ConnectionRefusedError:
        return False, f"{host}:{port} REFUSED (port not listening)"
    except OSError as e:
        return False, f"{host}:{port} ERROR: {e}"

def check_serial(path):
    """Test if a serial port exists."""
    if os.path.exists(path):
        return True, f"{path} EXISTS"
    return False, f"{path} NOT FOUND"

def check_camera(index=0):
    """Test if camera is accessible."""
    try:
        import cv2
        cap = cv2.VideoCapture(index)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                return True, f"Camera {index}: {frame.shape[1]}x{frame.shape[0]}"
        cap.release()
    except ImportError:
        return False, "OpenCV not installed"
    except Exception:
        pass
    return False, f"Camera {index}: NOT AVAILABLE"

def check_model(model_path="best.tflite"):
    """Test if AI model loads."""
    if not os.path.exists(model_path):
        return False, f"Model file not found: {model_path}"
    try:
        from vision import VisionSystem
        v = VisionSystem(camera_index=None, model_path=model_path)
        if v.using_ai:
            backend = "TFLite" if v._use_tflite_direct else "Ultralytics"
            return True, f"Model loaded ({backend})"
        return False, "Model file exists but failed to load (no backend available)"
    except Exception as e:
        return False, f"Error: {e}"

def check_mavlink(conn_str, baud=57600, timeout=5):
    """Test MAVLink heartbeat on the connection."""
    try:
        from pymavlink import mavutil
        if conn_str.startswith("/dev/"):
            m = mavutil.mavlink_connection(conn_str, baud=baud)
        else:
            m = mavutil.mavlink_connection(conn_str)
        hb = m.wait_heartbeat(timeout=timeout)
        m.close()
        if hb:
            baud_info = f", baud={baud}" if conn_str.startswith("/dev/") else ""
            return True, f"Heartbeat received (system {hb.get_srcSystem()}{baud_info})"
        if conn_str.startswith("/dev/"):
            return False, f"No heartbeat (baud={baud} - wrong baud rate?)"
        return False, "No heartbeat within timeout"
    except ImportError:
        return False, "pymavlink not installed"
    except Exception as e:
        return False, f"Error: {e}"

# ==========================================
#            MAIN REPORT
# ==========================================
def main():
    print("=" * 55)
    print("         PRE-FLIGHT CONNECTIVITY TEST")
    print("=" * 55)

    # --- Platform ---
    plat = detect_platform()
    print(f"\n  [PLATFORM]   {plat}")

    # --- Mode (read from config.py so it matches main.py) ---
    try:
        import config as _cfg
        mode = _cfg.MODE
    except Exception:
        mode = os.environ.get("DRONE_MODE", "REAL")
    print(f"  [MODE]       {mode}")

    # --- Connection string (from config auto-detect) ---
    try:
        import config
        conn_str = config.CONNECTION_STR
        baud = config.BAUD_RATE
    except Exception:
        conn_str = "tcp:127.0.0.1:5762"
        baud = 57600

    env_conn = os.environ.get("DRONE_CONN")
    if env_conn:
        src = "DRONE_CONN env var"
    elif plat == "WSL" and "127.0.0.1" not in conn_str:
        src = "auto-detected WSL gateway"
    elif conn_str.startswith("/dev/"):
        src = "auto-detected serial port"
    else:
        src = "default"
    baud_info = f", baud={baud}" if conn_str.startswith("/dev/") else ""
    print(f"  [CONNECTION] {conn_str}{baud_info} ({src})")

    # --- Run checks ---
    results = []
    print(f"\n{'─' * 55}")
    print("  RUNNING CHECKS...")
    print(f"{'─' * 55}\n")

    # 1. TCP or Serial check
    if conn_str.startswith("tcp:"):
        parts = conn_str.replace("tcp:", "").split(":")
        host, port = parts[0], int(parts[1])
        ok, msg = check_tcp(host, port)
        tag = "TCP PORT"
    elif conn_str.startswith("/dev/"):
        ok, msg = check_serial(conn_str)
        tag = "SERIAL"
    else:
        ok, msg = False, f"Unknown connection type: {conn_str}"
        tag = "CONN"

    # If connection failed, prompt user to enter IP manually
    if not ok and not conn_str.startswith("/dev/"):
        status = "FAIL"
        print(f"  [{status:4s}] {tag:12s}  {msg}")
        print(f"\n  Connection failed. Is SITL/Mission Planner running?")
        print(f"  If it's on another machine, enter its IP address.")
        print(f"  (Find it with 'ipconfig' on Windows or 'hostname -I' on Linux)")
        user_ip = input("\n  Enter IP address (or press Enter to skip): ").strip()
        if user_ip:
            conn_str = f"tcp:{user_ip}:5762"
            print(f"  Trying: {conn_str}")
            ok, msg = check_tcp(user_ip, 5762)
            if ok:
                print(f"\n  Connected! To skip this prompt next time, run:")
                print(f"    export DRONE_CONN={conn_str}")

    status = "OK" if ok else "FAIL"
    print(f"  [{status:4s}] {tag:12s}  {msg}")
    results.append((tag, ok, msg))

    # 2. MAVLink heartbeat (only if port/serial was reachable)
    if ok:
        hb_ok, hb_msg = check_mavlink(conn_str, baud=baud)
        status = "OK" if hb_ok else "FAIL"
        print(f"  [{status:4s}] {'HEARTBEAT':12s}  {hb_msg}")
        results.append(("HEARTBEAT", hb_ok, hb_msg))
    else:
        print(f"  [SKIP] {'HEARTBEAT':12s}  Skipped (connection not reachable)")
        results.append(("HEARTBEAT", None, "Skipped"))

    # 3. Camera (only in REAL mode)
    if mode == "REAL":
        cam_ok, cam_msg = check_camera(0)
        status = "OK" if cam_ok else "FAIL"
        print(f"  [{status:4s}] {'CAMERA':12s}  {cam_msg}")
        results.append(("CAMERA", cam_ok, cam_msg))
    else:
        print(f"  [SKIP] {'CAMERA':12s}  Skipped (simulation mode)")
        results.append(("CAMERA", None, "Skipped"))

    # 4. AI Model
    model_ok, model_msg = check_model()
    status = "OK" if model_ok else "FAIL"
    print(f"  [{status:4s}] {'AI MODEL':12s}  {model_msg}")
    results.append(("AI MODEL", model_ok, model_msg))

    # --- Summary ---
    fails = [r for r in results if r[1] is False]
    passes = [r for r in results if r[1] is True]
    skips = [r for r in results if r[1] is None]

    print(f"\n{'─' * 55}")
    print(f"  RESULT: {len(passes)} passed, {len(fails)} failed, {len(skips)} skipped")
    print(f"{'─' * 55}")

    if fails:
        print("\n  ISSUES TO FIX:")
        for tag, _, msg in fails:
            print(f"    - {tag}: {msg}")

        # Platform-specific hints
        if plat == "WSL" and any(t == "TCP PORT" for t, _, _ in fails):
            print("\n  WSL HINT: Check Windows Firewall allows port 5762:")
            print("    netsh advfirewall firewall add rule name=\"SITL\" dir=in action=allow protocol=TCP localport=5762")
        if any(t == "HEARTBEAT" for t, _, _ in fails):
            print("\n  HINT: Is Mission Planner / SITL running and listening?")

    if not fails:
        print("\n  All checks passed. Ready to fly:")
        print(f"    python main.py")

    print()
    return len(fails) == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
