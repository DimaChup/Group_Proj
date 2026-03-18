#!/usr/bin/env python3
"""
SAR Drone System Readiness Check
Run before any flight to verify all subsystems.
ZERO commands sent. Safe to run anytime.

Usage:
    python field_tools/system_readiness.py
    python field_tools/system_readiness.py --quick     # skip slow checks (model FPS, HTTP)
    python field_tools/system_readiness.py --no-cube   # skip Cube check (indoor testing)
"""
import sys
import os
import time
import json
import socket
import platform
import shutil
import argparse
import subprocess
from collections import namedtuple

# Add project root
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)
os.chdir(PROJECT_ROOT)

# Colors
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
BOLD = '\033[1m'
RESET = '\033[0m'

CheckResult = namedtuple('CheckResult', ['name', 'status', 'message'])

def status_color(status):
    return {'PASS': GREEN, 'WARN': YELLOW, 'FAIL': RED, 'SKIP': BLUE}.get(status, '')

# ═══════════════════════════════════════════════════════
# CHECK 1: Platform
# ═══════════════════════════════════════════════════════
def check_platform():
    py_ver = sys.version.split()[0]
    os_name = platform.system()
    hostname = socket.gethostname()

    # Detect platform type
    if os.path.exists('/proc/device-tree/model'):
        try:
            with open('/proc/device-tree/model') as f:
                if 'Raspberry' in f.read():
                    ptype = 'Raspberry Pi'
                else:
                    ptype = 'Linux'
        except Exception:
            ptype = 'Linux'
    elif os_name == 'Windows':
        ptype = 'Windows'
    else:
        ptype = os_name

    # IP addresses
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        primary_ip = s.getsockname()[0]
        s.close()
    except Exception:
        primary_ip = "unknown"

    # Disk space
    stat = shutil.disk_usage(PROJECT_ROOT)
    free_gb = stat.free / (1024**3)

    info = f"Python {py_ver}, {ptype}, {hostname}, IP: {primary_ip}, Disk: {free_gb:.1f}GB free"

    if tuple(int(x) for x in py_ver.split('.')[:2]) < (3, 10):
        return CheckResult('Platform', 'WARN', info + " (Python < 3.10)")
    if free_gb < 0.1:
        return CheckResult('Platform', 'FAIL', info + " (disk critical)")
    return CheckResult('Platform', 'PASS', info)

# ═══════════════════════════════════════════════════════
# CHECK 2: Network
# ═══════════════════════════════════════════════════════
def check_network():
    issues = []

    # Primary IP
    ip = None
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
    except Exception:
        issues.append("No network route")

    # Internet test
    internet_ok = False
    try:
        socket.setdefaulttimeout(2)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect(("8.8.8.8", 53))
        s.close()
        internet_ok = True
    except Exception:
        issues.append("No internet (OK if in field)")

    # mavproxy UDP port
    mavproxy_port = False
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('0.0.0.0', 14550))
        s.close()
        # Port was FREE — means mavproxy is NOT sending to it yet
        issues.append("UDP 14550 free (mavproxy not sending?)")
    except OSError:
        # Port in use — mavproxy is active
        mavproxy_port = True

    msg = f"IP: {ip or 'none'}"
    if internet_ok:
        msg += ", internet OK"
    if mavproxy_port:
        msg += ", mavproxy UDP active"

    if not ip:
        return CheckResult('Network', 'FAIL', msg)
    if issues:
        return CheckResult('Network', 'WARN', msg + " | " + "; ".join(issues))
    return CheckResult('Network', 'PASS', msg)

# ═══════════════════════════════════════════════════════
# CHECK 3: Camera
# ═══════════════════════════════════════════════════════
def check_camera():
    try:
        import config
    except Exception as e:
        return CheckResult('Camera', 'FAIL', f'Cannot import config: {e}')

    if config.MODE == 'SIMULATION':
        # Check webcam
        try:
            import cv2
            cap = cv2.VideoCapture(0)
            if not cap.isOpened():
                cap.release()
                return CheckResult('Camera', 'WARN', 'No webcam (OK for simulation)')
            ret, frame = cap.read()
            cap.release()
            if not ret:
                return CheckResult('Camera', 'WARN', 'Webcam open but no frame')
            h, w = frame.shape[:2]
            return CheckResult('Camera', 'PASS', f'Webcam OK: {w}x{h}')
        except Exception as e:
            return CheckResult('Camera', 'WARN', f'No camera: {e} (OK for simulation)')

    # REAL mode — need picamera2 or OpenCV
    try:
        import cv2
    except ImportError:
        return CheckResult('Camera', 'FAIL', 'OpenCV not installed')

    # Try picamera2 first
    try:
        from picamera2 import Picamera2
        cam = Picamera2()
        cam_config = cam.create_still_configuration(main={"size": (config.IMAGE_W, config.IMAGE_H)})
        cam.configure(cam_config)
        cam.start()
        frame = cam.capture_array()
        cam.stop()
        cam.close()
        h, w = frame.shape[:2]
        return CheckResult('Camera', 'PASS', f'Pi camera OK: {w}x{h}')
    except ImportError:
        pass
    except Exception as e:
        return CheckResult('Camera', 'FAIL', f'Pi camera error: {e}')

    # Fallback to OpenCV
    try:
        camera_idx = getattr(config, 'CAMERA_INDEX', 0)
        cap = cv2.VideoCapture(camera_idx)
        if not cap.isOpened():
            cap.release()
            return CheckResult('Camera', 'FAIL', 'Camera not accessible')
        ret, frame = cap.read()
        cap.release()
        if not ret:
            return CheckResult('Camera', 'FAIL', 'Camera open but no frame')
        h, w = frame.shape[:2]
        return CheckResult('Camera', 'PASS', f'Camera OK: {w}x{h}')
    except Exception as e:
        return CheckResult('Camera', 'FAIL', f'Camera error: {e}')

# ═══════════════════════════════════════════════════════
# CHECK 4: AI Model
# ═══════════════════════════════════════════════════════
def check_model(quick=False):
    model_path = os.path.join(PROJECT_ROOT, 'best.tflite')
    if not os.path.exists(model_path):
        return CheckResult('AI Model', 'FAIL', 'best.tflite not found in project root')

    size_mb = os.path.getsize(model_path) / (1024**2)

    try:
        from vision import VisionSystem
        v = VisionSystem(camera_index=None, model_path=model_path)
        if not v.using_ai:
            return CheckResult('AI Model', 'FAIL', f'Model exists ({size_mb:.1f}MB) but no backend available')

        backend = 'TFLite' if hasattr(v, '_tflite_interpreter') and v._tflite_interpreter else 'Ultralytics'

        if quick:
            return CheckResult('AI Model', 'PASS', f'{size_mb:.1f}MB, {backend} backend loaded')

        # Inference speed test (5 frames)
        import numpy as np
        import cv2
        test_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        test_frame[200:280, 280:360] = [0, 128, 255]  # orange blob

        times = []
        for _ in range(5):
            t0 = time.time()
            found, x, y, conf = v.detect_in_image(test_frame)
            times.append((time.time() - t0) * 1000)

        avg_ms = sum(times) / len(times)
        fps = 1000 / avg_ms if avg_ms > 0 else 0

        msg = f'{size_mb:.1f}MB, {backend}, {avg_ms:.0f}ms ({fps:.1f} FPS)'
        if avg_ms > 500:
            return CheckResult('AI Model', 'WARN', msg + ' (slow)')
        return CheckResult('AI Model', 'PASS', msg)
    except Exception as e:
        return CheckResult('AI Model', 'FAIL', str(e))

# ═══════════════════════════════════════════════════════
# CHECK 5: Cube/MAVLink
# ═══════════════════════════════════════════════════════
def check_cube(skip=False):
    if skip:
        return CheckResult('Cube/MAVLink', 'SKIP', 'Skipped (--no-cube)')

    try:
        import config
        from pymavlink import mavutil
    except ImportError:
        return CheckResult('Cube/MAVLink', 'FAIL', 'pymavlink not installed')

    try:
        m = mavutil.mavlink_connection(config.CONNECTION_STR, baud=921600)
        hb = m.wait_heartbeat(timeout=3)
        if not hb:
            m.close()
            return CheckResult('Cube/MAVLink', 'FAIL', f'No heartbeat on {config.CONNECTION_STR}')

        # Mode
        mode = 'UNKNOWN'
        armed = False
        try:
            mode_num = hb.custom_mode
            MODES = {0: 'STABILIZE', 2: 'ALT_HOLD', 3: 'AUTO', 4: 'GUIDED',
                     5: 'LOITER', 6: 'RTL', 9: 'LAND'}
            mode = MODES.get(mode_num, f'MODE_{mode_num}')
            armed = bool(hb.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
        except Exception:
            pass

        # GPS
        gps_info = ''
        try:
            gps_msg = m.recv_match(type='GPS_RAW_INT', blocking=True, timeout=2)
            if gps_msg:
                fix_names = {0: 'NO_FIX', 1: 'NO_FIX', 2: '2D', 3: '3D',
                             4: 'DGPS', 5: 'RTK_FLOAT', 6: 'RTK_FIXED'}
                fix = fix_names.get(gps_msg.fix_type, f'TYPE_{gps_msg.fix_type}')
                sats = gps_msg.satellites_visible
                hdop = gps_msg.eph / 100
                gps_info = f', GPS: {fix} {sats}sats HDOP={hdop:.1f}'
        except Exception:
            pass

        # Battery
        batt_info = ''
        try:
            batt_msg = m.recv_match(type='SYS_STATUS', blocking=True, timeout=2)
            if batt_msg:
                voltage = batt_msg.voltage_battery / 1000
                remaining = batt_msg.battery_remaining
                batt_info = f', Batt: {voltage:.1f}V ({remaining}%)'
                if remaining < 20:
                    m.close()
                    return CheckResult('Cube/MAVLink', 'WARN',
                                       f'{mode}{"(ARMED)" if armed else ""}{gps_info}{batt_info} LOW BATTERY')
        except Exception:
            pass

        m.close()

        msg = f'{mode}{"(ARMED)" if armed else ""}{gps_info}{batt_info}'

        if gps_msg and gps_msg.fix_type < 3:
            return CheckResult('Cube/MAVLink', 'WARN', msg + ' (no 3D fix)')

        return CheckResult('Cube/MAVLink', 'PASS', msg)
    except Exception as e:
        return CheckResult('Cube/MAVLink', 'FAIL', str(e))

# ═══════════════════════════════════════════════════════
# CHECK 6: Flight Plans
# ═══════════════════════════════════════════════════════
def check_flight_plans():
    issues = []
    details = []

    for name, path, min_pts in [
        ('search_area', 'flight_plans/search_area.json', 3),
        ('waypoints', 'flight_plans/waypoints.json', 2),
        ('transit', 'flight_plans/transit.json', 2),
    ]:
        full = os.path.join(PROJECT_ROOT, path)
        if os.path.exists(full):
            try:
                with open(full) as f:
                    data = json.load(f)
                if len(data) >= min_pts:
                    details.append(f'{name}({len(data)}pts)')
                else:
                    issues.append(f'{name}: only {len(data)} points (need {min_pts}+)')
            except json.JSONDecodeError:
                issues.append(f'{name}: invalid JSON')
            except Exception as e:
                issues.append(f'{name}: {e}')
        else:
            issues.append(f'{name}: not found')

    # KML
    kml_path = os.path.join(PROJECT_ROOT, 'flight_plans/AENGM0074.kml')
    if os.path.exists(kml_path):
        try:
            import config
            config.load_kml_zones(kml_path)
            details.append(f'KML({len(config.SEARCH_AREA_GPS)}pts)')
        except AttributeError:
            details.append('KML(found, no loader)')
        except Exception:
            issues.append('KML parse error')
    else:
        issues.append('KML not found')

    msg = ', '.join(details) if details else 'No plans found'
    if issues:
        return CheckResult('Flight Plans', 'WARN', msg + ' | Missing: ' + '; '.join(issues))
    return CheckResult('Flight Plans', 'PASS', msg)

# ═══════════════════════════════════════════════════════
# CHECK 7: Calibration
# ═══════════════════════════════════════════════════════
def check_calibration():
    calib_path = os.path.join(PROJECT_ROOT, 'calibration_data.npz')
    if not os.path.exists(calib_path):
        return CheckResult('Calibration', 'WARN', 'calibration_data.npz not found (uncalibrated OK)')

    try:
        import numpy as np
        data = np.load(calib_path)
        if 'mtx' in data and 'dist' in data:
            return CheckResult('Calibration', 'PASS', 'Lens calibration loaded')
        return CheckResult('Calibration', 'WARN', 'Calibration file missing mtx/dist')
    except Exception as e:
        return CheckResult('Calibration', 'WARN', f'Calibration load error: {e}')

# ═══════════════════════════════════════════════════════
# CHECK 8: HTTP Stream
# ═══════════════════════════════════════════════════════
def check_http_stream(quick=False):
    if quick:
        return CheckResult('HTTP Stream', 'SKIP', 'Skipped (--quick)')

    try:
        import cv2
        import numpy as np
    except ImportError as e:
        return CheckResult('HTTP Stream', 'FAIL', f'Missing dependency: {e}')

    import threading
    from http.server import HTTPServer, BaseHTTPRequestHandler

    test_port = 18090  # Use non-standard port to avoid conflicts

    # Check if standard port is in use
    std_port_busy = False
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        s.connect(('127.0.0.1', 8090))
        s.close()
        std_port_busy = True
    except Exception:
        pass

    try:
        # Generate test JPEG
        frame = np.zeros((240, 320, 3), dtype=np.uint8)
        cv2.putText(frame, 'READINESS TEST', (40, 130),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        _, jpeg = cv2.imencode('.jpg', frame)
        jpeg_bytes = jpeg.tobytes()

        class Handler(BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200)
                self.send_header('Content-Type', 'image/jpeg')
                self.end_headers()
                self.wfile.write(jpeg_bytes)

            def log_message(self, *args):
                pass  # suppress logs

        server = HTTPServer(('127.0.0.1', test_port), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()

        # Test fetch
        import urllib.request
        resp = urllib.request.urlopen(f'http://127.0.0.1:{test_port}/', timeout=2)
        ok = resp.getcode() == 200 and len(resp.read()) > 100
        server.shutdown()

        if ok:
            msg = 'HTTP stream OK'
            if std_port_busy:
                msg += ' (port 8090 in use — script already running?)'
            return CheckResult('HTTP Stream', 'PASS', msg)
        return CheckResult('HTTP Stream', 'FAIL', 'Server responded but bad data')
    except Exception as e:
        try:
            server.shutdown()
        except Exception:
            pass
        return CheckResult('HTTP Stream', 'FAIL', str(e))

# ═══════════════════════════════════════════════════════
# CHECK 9: Config Sanity
# ═══════════════════════════════════════════════════════
def check_config():
    try:
        import config
    except Exception as e:
        return CheckResult('Config', 'FAIL', f'Cannot import config: {e}')

    issues = []
    checks = [
        ('TARGET_ALT', lambda x: 5 <= x <= 100),
        ('VERIFY_ALT', lambda x: 3 <= x <= 50),
        ('IMAGE_W', lambda x: 320 <= x <= 4000),
        ('IMAGE_H', lambda x: 240 <= x <= 3000),
        ('SEARCH_SPEED_MPS', lambda x: 1 <= x <= 30),
        ('CONFIDENCE_THRESHOLD', lambda x: 0.05 <= x <= 0.95),
        ('FOCAL_LENGTH_MM', lambda x: 1 <= x <= 20),
    ]

    for param, validator in checks:
        if not hasattr(config, param):
            issues.append(f'Missing {param}')
        else:
            try:
                val = getattr(config, param)
                if not validator(val):
                    issues.append(f'{param}={val} (unusual)')
            except Exception:
                issues.append(f'{param}: validation error')

    if issues:
        return CheckResult('Config', 'WARN', '; '.join(issues))
    return CheckResult('Config', 'PASS',
                       f'All values OK (MODE={config.MODE}, ALT={config.TARGET_ALT}m)')

# ═══════════════════════════════════════════════════════
# CHECK 10: Disk Space
# ═══════════════════════════════════════════════════════
def check_disk():
    try:
        stat = shutil.disk_usage(PROJECT_ROOT)
    except Exception as e:
        return CheckResult('Disk Space', 'FAIL', f'Cannot read disk: {e}')

    free_gb = stat.free / (1024**3)
    total_gb = stat.total / (1024**3)

    if free_gb < 0.1:
        return CheckResult('Disk Space', 'FAIL', f'{free_gb:.2f}GB free — critical')
    if free_gb < 0.5:
        return CheckResult('Disk Space', 'WARN', f'{free_gb:.2f}GB free — low')
    return CheckResult('Disk Space', 'PASS', f'{free_gb:.1f}GB free / {total_gb:.0f}GB total')

# ═══════════════════════════════════════════════════════
# CHECK 11: Model Inventory
# ═══════════════════════════════════════════════════════
def check_models():
    models_found = []
    search_paths = [
        ('best.tflite', 'Active model (root)'),
        ('cv_models/original_best.tflite', 'Original baseline'),
        ('cv_models/sar_v2_1088/best.tflite', 'v2-1088 RECOMMENDED'),
        ('cv_models/sar_640/best.tflite', 'v1 at 640'),
        ('cv_models/sar_1280/best.tflite', 'v1 at 1280'),
        ('cv_models/human.tflite', 'COCO person detector'),
        ('cv_models/custom_yolov8n.tflite', 'Custom YOLOv8n'),
    ]

    for path, desc in search_paths:
        full = os.path.join(PROJECT_ROOT, path)
        if os.path.exists(full):
            try:
                size = os.path.getsize(full) / (1024**2)
                models_found.append((path, size, desc))
            except Exception:
                models_found.append((path, 0.0, desc + ' (size unknown)'))

    return CheckResult('Models', 'PASS', f'{len(models_found)} models available'), models_found

# ═══════════════════════════════════════════════════════
# REPORT
# ═══════════════════════════════════════════════════════
def print_report(results, models):
    width = 78
    print()
    print(f'{BOLD}{"=" * width}')
    print(f'  SAR DRONE — SYSTEM READINESS CHECK')
    print(f'  {time.strftime("%Y-%m-%d %H:%M:%S")}')
    print(f'{"=" * width}{RESET}')
    print()

    passes = warns = fails = skips = 0
    for r in results:
        c = status_color(r.status)
        icon = {'PASS': '+', 'WARN': '!', 'FAIL': 'X', 'SKIP': 'o'}.get(r.status, '?')
        print(f'  {c}[{icon}] {r.status:4s}{RESET}  {r.name:18s}  {r.message}')
        if r.status == 'PASS':
            passes += 1
        elif r.status == 'WARN':
            warns += 1
        elif r.status == 'FAIL':
            fails += 1
        else:
            skips += 1

    # Model inventory
    if models:
        print(f'\n  {BOLD}Available Models:{RESET}')
        for path, size, desc in models:
            active = ' <- ACTIVE' if path == 'best.tflite' else ''
            print(f'    {size:6.1f}MB  {path:45s}  {desc}{active}')

    # GO/NO-GO
    print(f'\n{"=" * width}')
    if fails == 0:
        print(f'  {GREEN}{BOLD}GO — {passes} PASS, {warns} WARN, {fails} FAIL, {skips} SKIP{RESET}')
    else:
        print(f'  {RED}{BOLD}NO-GO — {fails} FAIL(s) detected. Fix before flight.{RESET}')
        print(f'  {passes} PASS, {warns} WARN, {fails} FAIL, {skips} SKIP')
    print(f'{"=" * width}\n')

    return fails == 0

# ═══════════════════════════════════════════════════════
# MAIN
# ═══════════════════════════════════════════════════════
def main():
    parser = argparse.ArgumentParser(description='SAR Drone System Readiness Check')
    parser.add_argument('--quick', action='store_true',
                        help='Skip slow checks (model FPS, HTTP)')
    parser.add_argument('--no-cube', action='store_true',
                        help='Skip Cube/MAVLink check')
    args = parser.parse_args()

    results = []
    models = []

    checks = [
        ('Platform', lambda: check_platform()),
        ('Network', lambda: check_network()),
        ('Camera', lambda: check_camera()),
        ('AI Model', lambda: check_model(quick=args.quick)),
        ('Cube/MAVLink', lambda: check_cube(skip=args.no_cube)),
        ('Flight Plans', lambda: check_flight_plans()),
        ('Calibration', lambda: check_calibration()),
        ('HTTP Stream', lambda: check_http_stream(quick=args.quick)),
        ('Config', lambda: check_config()),
        ('Disk Space', lambda: check_disk()),
    ]

    for name, check_fn in checks:
        try:
            print(f'  Checking {name}...', end='\r')
            result = check_fn()
            results.append(result)
        except Exception as e:
            results.append(CheckResult(name, 'FAIL', f'Unexpected error: {e}'))

    # Model inventory (always runs)
    try:
        print(f'  Checking Models...', end='\r')
        model_result, models = check_models()
        results.append(model_result)
    except Exception as e:
        results.append(CheckResult('Models', 'FAIL', str(e)))

    go = print_report(results, models)
    sys.exit(0 if go else 1)


if __name__ == '__main__':
    main()
