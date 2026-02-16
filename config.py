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
    for port in ["/dev/ttyAMA0", "/dev/ttyACM0", "/dev/ttyUSB0"]:
        if os.path.exists(port):
            return port

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
MODE = os.environ.get("DRONE_MODE", "SIMULATION")

# --- FLIGHT CONNECTION ---
# Auto-detects: Pi->serial, WSL->gateway IP, Windows->localhost
# Override with: export DRONE_CONN=tcp:172.20.80.1:5762
CONNECTION_STR = _detect_connection()   
BAUD_RATE = int(os.environ.get("DRONE_BAUD", 57600))

# --- ALTITUDES ---
TARGET_ALT = 30.0 # Search Altitude (Meters)
VERIFY_ALT = 15.0 # Descent Altitude for Verification

# --- MAP CONFIGURATION (Simulation Only) ---
MAP_FILE = "map.jpg"
DUMMY_FILE = "dummy.png"
MAP_WIDTH_METERS = 480.0  
REF_LAT = 51.425106  
REF_LON = -2.672257

# --- TARGET SPECS ---
TARGET_REAL_RADIUS_M = 0.15 # 15 cm radius 
DUMMY_HEIGHT_M = 1.8        

# --- CAMERA SPECS ---
# Update these for the Raspberry Pi Global Shutter Camera
SENSOR_WIDTH_MM = 5.02
FOCAL_LENGTH_MM = 6.0
IMAGE_W = 640
IMAGE_H = 480
REAL_CAMERA_INDEX = 0 # Usually 0 for Pi Cam

# --- SPEED SETTINGS ---
TRANSIT_SPEED_MPS = 15.0  
SEARCH_SPEED_MPS = 10.0   

# --- REAL MODE SEARCH AREA ---
# Define your search area as GPS coordinates (lat, lon corners)
# Measure these on Google Maps or Mission Planner before flight day
# The same lawnmower planner from simulation will generate the pattern
SEARCH_AREA_GPS = [
    # (lat, lon) - polygon corners, at least 3 points
    # Example: a rectangle near Bristol (REPLACE with your real area)
    (51.42530, -2.67260),
    (51.42530, -2.67180),
    (51.42480, -2.67180),
    (51.42480, -2.67260),
]

# --- LOGGING ---
LOG_FILE = "flight_log.csv"