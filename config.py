# config.py
# ==========================================
#       CONFIGURATION & SETTINGS
# ==========================================
import os

# --- OPERATION MODE ---
# "SIMULATION": Uses map.jpg and mouse clicks for setup.
# "REAL": Uses Real Camera and assumes waypoints are loaded/generated elsewhere.
# Override with: export DRONE_MODE=REAL
MODE = os.environ.get("DRONE_MODE", "SIMULATION")

# --- FLIGHT CONNECTION ---
# Windows sim: 'tcp:127.0.0.1:5762'
# WSL sim:     'tcp:<gateway-ip>:5762'  (run: ip route show default | awk '{print $3}')
# Pi real:     '/dev/ttyAMA0'
# Override with: export DRONE_CONN=tcp:172.20.80.1:5762
CONNECTION_STR = os.environ.get("DRONE_CONN", 'tcp:127.0.0.1:5762')
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

# --- LOGGING ---
LOG_FILE = "flight_log.csv"