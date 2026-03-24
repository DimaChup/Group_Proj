# config.py
# ==========================================
#       CONFIGURATION & SETTINGS
# ==========================================
import os
import platform
import subprocess

# --- AUTO-DETECT CONNECTION ---
def _detect_connection():
    """Auto-detect the best connection string. No hardcoded IPs."""
    # 1. Environment variable always wins
    env = os.environ.get("DRONE_CONN")
    if env:
        return env

    # 2. Pi: check for serial ports
    #    Use mavproxy UDP bridge (start mavproxy first!) because
    #    Python 3.13 + pyserial has broken serial reads on Pi.
    #    Start mavproxy with:
    #      sudo /opt/mavlink/mavlink-venv/bin/mavproxy.py \
    #        --master=/dev/ttyAMA0 --baudrate=921600 \
    #        --out=udpout:127.0.0.1:14550
    for port in ["/dev/ttyAMA0", "/dev/ttyACM0", "/dev/ttyUSB0"]:
        if os.path.exists(port):
            return "udpin:0.0.0.0:14550"

    # 3. WSL: auto-detect gateway IP to reach Windows SITL
    if platform.system() == "Linux":
        try:
            with open("/proc/version", "r") as f:
                if "microsoft" in f.read().lower():
                    result = subprocess.run(["ip", "route", "show", "default"],
                                            capture_output=True, text=True)
                    parts = result.stdout.strip().split()
                    if "via" in parts:
                        gw = parts[parts.index("via") + 1]
                        return f"tcp:{gw}:5762"
        except Exception:
            pass

    # 4. Default: Windows localhost
    return "tcp:127.0.0.1:5762"

# --- OPERATION MODE ---
# "SIMULATION": Uses map.jpg and mouse clicks for setup.
# "REAL": Uses Real Camera and assumes waypoints are loaded/generated elsewhere.
# Override with: export DRONE_MODE=REAL
MODE = os.environ.get("DRONE_MODE", "REAL")

# --- FLIGHT CONNECTION ---
# Auto-detects: Pi->serial, WSL->gateway IP, Windows->localhost
# Override with: export DRONE_CONN=tcp:172.20.80.1:5762
CONNECTION_STR = _detect_connection()   
BAUD_RATE = int(os.environ.get("DRONE_BAUD", 921600))

# --- ALTITUDES ---
TARGET_ALT = 50.0 # Search Altitude (Meters) — 50m for wider coverage
VERIFY_ALT = 15.0 # Descent Altitude for Verification

# --- MAP CONFIGURATION (Simulation Only) ---
MAP_FILE = "assets/map.jpg"
DUMMY_FILE = "assets/dummy.png"
CONE_FILE = "assets/cone.png"
MAP_WIDTH_METERS = 480.0
REF_LAT = 51.425106
REF_LON = -2.672257

# --- TARGET SPECS ---
TARGET_REAL_RADIUS_M = 0.15 # 15 cm radius
DUMMY_HEIGHT_M = 1.8
CONE_HEIGHT_M = 0.5         # traffic cone ~50cm

# --- CAMERA SPECS ---
# Update these for the Raspberry Pi Global Shutter Camera
SENSOR_WIDTH_MM = 5.02
# Calibrate: hold camera 1m above tape measure, read visible width in mm
# FOCAL_LENGTH_MM = 5020 / measured_width_mm
FOCAL_LENGTH_MM = 5.46  # Calibrated: 92cm visible at 1m height (2026-03-11)
IMAGE_W = 1456  # IMX296 native resolution (was 640x480, upgraded for full detail)
IMAGE_H = 1088  # vision.py resizes to model input (640x640) for inference
REAL_CAMERA_INDEX = 0 # Usually 0 for Pi Cam

# --- CAMERA WHITE BALANCE (Pi only) ---
# "auto", "daylight", "cloudy", "indoor", or "manual"
# Use "daylight" or "cloudy" for outdoor flights to fix blue tint
CAMERA_AWB_MODE = "auto"
# Manual colour gains (red, blue) — only used when AWB_MODE = "manual"
CAMERA_COLOUR_GAINS = (1.5, 1.2)
# Software color correction (gray world algorithm) — not needed after channel fix
CAMERA_COLOR_CORRECTION = False
CAMERA_FLIP_180 = True   # Camera mounted inverted on drone — flip image 180°

# --- CV DETECTION ---
# All scripts use best.tflite in root. To swap model on Pi:
#   cp cv_models/sar_v2_1088/best.tflite best.tflite  (retrained v2, recommended)
#   cp cv_models/sar_640/best.tflite best.tflite       (earlier 640x640 training)
CONFIDENCE_THRESHOLD = 0.4  # Min detection confidence (tune on flight day: lower=more detections+more false positives)

# --- SPEED SETTINGS ---
TRANSIT_SPEED_MPS = 15.0
SEARCH_SPEED_MPS = 10.0
FOCUS_SEARCH_SPEED_MPS = 5.0  # Slower in Focus Area (PLB beacon) — more detection time

# Altitude-dependent speed: linear from (20m, 6 m/s) to (50m, 10 m/s)
SPEED_ALT_LOW = 20.0   # metres — below this, use SPEED_AT_LOW
SPEED_ALT_HIGH = 50.0  # metres — above this, use SPEED_AT_HIGH
SPEED_AT_LOW = 6.0     # m/s at low altitude (less blur)
SPEED_AT_HIGH = 10.0   # m/s at high altitude (faster coverage)

def speed_for_altitude(alt):
    """Linear interpolation: slower at low alt (less blur), faster at high alt."""
    if alt <= SPEED_ALT_LOW:
        return SPEED_AT_LOW
    if alt >= SPEED_ALT_HIGH:
        return SPEED_AT_HIGH
    ratio = (alt - SPEED_ALT_LOW) / (SPEED_ALT_HIGH - SPEED_ALT_LOW)
    return SPEED_AT_LOW + ratio * (SPEED_AT_HIGH - SPEED_AT_LOW)

# --- REAL MODE SEARCH AREA ---
# --- SEARCH AREA ---
# Load from AENGM0074.kml at runtime (see load_kml_zones() below)
# Fallback: define manually if KML not found
SEARCH_AREA_GPS = [
    # (lat, lon) - polygon corners, at least 3 points
    # These are overwritten by load_kml_zones() if AENGM0074.kml exists
    (51.42530, -2.67260),
    (51.42530, -2.67180),
    (51.42480, -2.67180),
    (51.42480, -2.67260),
]

# These get populated by load_kml_zones()
FLIGHT_AREA_GPS = []
SSSI_GPS = []
TAKEOFF_GPS = None
FOCUS_AREA_GPS = []

def load_kml_zones(kml_path="flight_plans/AENGM0074.kml"):
    """Parse KML file and populate GPS zone variables."""
    global SEARCH_AREA_GPS, FLIGHT_AREA_GPS, SSSI_GPS, TAKEOFF_GPS, FOCUS_AREA_GPS, REF_LAT, REF_LON
    import xml.etree.ElementTree as ET

    if not os.path.exists(kml_path):
        print(f"[CONFIG] KML not found: {kml_path} — using fallback SEARCH_AREA_GPS")
        return False

    ns = {"kml": "http://www.opengis.net/kml/2.2"}
    tree = ET.parse(kml_path)
    root = tree.getroot()

    def parse_coords(coord_text):
        """Parse KML coordinate string (lon,lat,alt) → list of (lat, lon)."""
        pts = []
        for token in coord_text.strip().split():
            parts = token.split(",")
            if len(parts) >= 2:
                lon, lat = float(parts[0]), float(parts[1])
                pts.append((lat, lon))
        # Remove closing point if it duplicates the first
        if len(pts) > 1 and pts[0] == pts[-1]:
            pts = pts[:-1]
        return pts

    for pm in root.iter("{http://www.opengis.net/kml/2.2}Placemark"):
        name_el = pm.find("kml:name", ns)
        if name_el is None:
            continue
        name = name_el.text.strip()

        # Point placemark (Take-Off)
        point = pm.find(".//kml:Point/kml:coordinates", ns)
        if point is not None:
            parts = point.text.strip().split(",")
            if len(parts) >= 2:
                lon, lat = float(parts[0]), float(parts[1])
                if "take" in name.lower() or "off" in name.lower():
                    TAKEOFF_GPS = (lat, lon)
                    # NOTE: Do NOT overwrite REF_LAT/REF_LON here.
                    # Those define the map.jpg origin (top-left corner).
                    # Changing them breaks all GPS↔pixel conversions.

        # Polygon placemarks
        coords = pm.find(".//kml:Polygon/kml:outerBoundaryIs/kml:LinearRing/kml:coordinates", ns)
        if coords is not None:
            pts = parse_coords(coords.text)
            lower = name.lower()
            if "survey" in lower:
                SEARCH_AREA_GPS = pts
            elif "flight" in lower:
                FLIGHT_AREA_GPS = pts
            elif "sssi" in lower:
                SSSI_GPS = pts
            elif "focus" in lower:
                FOCUS_AREA_GPS = pts

    print(f"[CONFIG] Loaded KML: {kml_path}")
    print(f"  Take-Off:     {TAKEOFF_GPS}")
    print(f"  Survey Area:  {len(SEARCH_AREA_GPS)} corners")
    print(f"  Flight Area:  {len(FLIGHT_AREA_GPS)} corners")
    print(f"  SSSI:         {len(SSSI_GPS)} corners")
    return True

# Call load_kml_zones() explicitly when needed:
#   import config
#   config.load_kml_zones()         # default: AENGM0074.kml
#   config.load_kml_zones("path/to/other.kml")

# --- LOGGING ---
LOG_FILE = "logs/flight_log.csv"