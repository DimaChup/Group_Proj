#!/usr/bin/env python3
"""
Pi Test 3b: Buzzer test - plays melodies on the Cube's buzzer via MAVLink.

Requires mavproxy running in another terminal.

Usage:
    python tests/pi_3b_buzzer.py
"""
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymavlink import mavutil

# Connect to Cube
import config
conn_str = config.CONNECTION_STR
print(f"[CUBE] Connecting: {conn_str}")
mav = mavutil.mavlink_connection(conn_str)
print("[CUBE] Waiting for heartbeat...")
mav.wait_heartbeat(timeout=10)
print(f"[CUBE] Connected to system {mav.target_system}")

def beep(tune, label=""):
    """Play a tune on the Cube's buzzer via MAVLink PLAY_TUNE."""
    try:
        mav.mav.play_tune_send(
            mav.target_system, mav.target_component,
            tune.encode(),
            b""
        )
        if label:
            print(f"  Playing: {label}")
    except Exception as e:
        print(f"  Buzzer error: {e}")

print("\n[BUZZER TEST] Playing melodies on Cube buzzer...\n")

# Test 1: Simple beep
beep("MFT200L8CDE", "Simple beep (C-D-E)")
time.sleep(2)

# Test 2: Detection alert
beep("MFT200L8CDEF", "Detection alert (C-D-E-F)")
time.sleep(2)

# Test 3: Happy melody
beep("MFT200L4CDEFEDCL2C", "Happy melody")
time.sleep(3)

# Test 4: Alarm / urgent
beep("MFT300L16CECECECE", "Alarm - fast beeps")
time.sleep(2)

# Test 5: Success fanfare
beep("MFT200L4CEG>C", "Success fanfare (C-E-G-C)")
time.sleep(3)

print("\n[DONE] Did you hear the buzzer?")
print("  If not, check:")
print("  - Cube has a buzzer connected")
print("  - Volume is audible (some Cubes have quiet built-in buzzers)")
print("  - Try connecting an external buzzer to the BUZZ port")
