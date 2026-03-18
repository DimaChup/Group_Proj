#!/usr/bin/env python3
"""
Buzzer Test — play melodies on the Cube's buzzer via MAVLink PLAY_TUNE.

WHAT:    Connects to the Cube via mavproxy and sends 15 different PLAY_TUNE
         MAVLink messages to test the buzzer hardware. Includes simple beeps,
         detection alerts, classical music (Fur Elise), game themes (Mario,
         Tetris), movie themes (Pirates, Imperial March), and pop songs.
WHY:     Verifies the buzzer hardware works before relying on it for in-flight
         audio alerts (detection beep, landing confirmation, alarm). Also a
         morale booster at the field.
WHEN:    During initial hardware setup, or at the field to confirm buzzer is
         audible. Run once after assembling the drone.
WHERE:   Pi only (needs Cube connection via mavproxy). Could work on laptop
         with SITL but SITL has no physical buzzer.
ENV:     pienv on Pi. Needs pymavlink and mavproxy running in another terminal.
MODELS:  none — no AI or camera involved.
RISK:    none — PLAY_TUNE is a harmless MAVLink command, does not affect flight
         controller state, arming, or motors.

USAGE:
    python tests/hardware/buzzer_test.py

FLAGS:
    None

OUTPUT:
    Terminal log of each melody being played. Listen for buzzer audio.
    At the end, prints troubleshooting tips if no sound was heard.

BEST PRACTICES:
    - Start mavproxy first (e.g. with udpout to 14550)
    - If the built-in buzzer is too quiet, connect an external buzzer to BUZZ port
    - Some Cube variants have no built-in buzzer — check your hardware

DEPENDENCIES:
    pymavlink, config.py (for CONNECTION_STR)
"""
import sys
import os
import time
script_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(script_dir))
sys.path.insert(0, project_root)

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

# Test 6: Fur Elise (Beethoven)
beep("MFO5T120L8ED#ED#EL8<B>DC L4<A", "Fur Elise - part 1")
time.sleep(3)
beep("MFO4T120L8CEA L4B L8EG#B L4>C", "Fur Elise - part 2")
time.sleep(3)
beep("MFO5T120L8ED#ED#E<B>DC L4<A", "Fur Elise - part 3")
time.sleep(4)

# Test 7: Nokia ringtone
beep("MFO5T180L8E.D.L4F#.G#.L8C#.D.L4E.F#.L8B.<A.L4>C#.E.L2A", "Nokia tune")
time.sleep(5)

# Test 8: Super Mario Bros theme
beep("MFO5T200L8EEpEpCE L4G L4<G", "Mario - intro")
time.sleep(3)
beep("MFO5T200L8<C.p>L8<G.p>L8<E.pA.B.A#.A.", "Mario - underground")
time.sleep(4)

# Test 9: Tetris (Korobeiniki)
beep("MFO5T150L4EL8BCD L4DCL8BA L4ACE L4DC L2B", "Tetris - part 1")
time.sleep(3)
beep("MFO5T150L8pCL4EL8DC L4<B>L8BCD L4E L4C L4<A L2A", "Tetris - part 2")
time.sleep(4)

# Test 10: Pirates of the Caribbean
beep("MFO4T120L8AAA L8A.L16G L8A.L16G L4A L8A.L16G L8A.L16G L8A>C<", "Pirates - part 1")
time.sleep(3)
beep("MFO4T120L4DL8D.L16CL8D.L16CL4DL8FEL4DL8CL2<A", "Pirates - part 2")
time.sleep(4)

# Test 11: Still Dre (Dr. Dre ft. Snoop Dogg) - extended
beep("MFO5T120L8EEE>C<BAL4GL8EEE>C<BAL4G", "Still Dre - part 1")
time.sleep(3)
beep("MFO5T120L8EEE>C<BAL4EL8DDDBA<GL4A", "Still Dre - part 2")
time.sleep(4)

# Test 12: Lose Yourself (Eminem) - extended
beep("MFO4T140L16DDDDL8DL16DDDL8FL4EL8D", "Lose Yourself - part 1")
time.sleep(3)
beep("MFO4T140L16DDDDL8DL16DDDL8CL4<BL8>D", "Lose Yourself - part 2")
time.sleep(4)

# Test 13: In Da Club (50 Cent) - extended
beep("MFO4T108L8G<G>GL4AL8GFL4EL8DC", "In Da Club - part 1")
time.sleep(3)
beep("MFO4T108L8<G>GGL4AL8GFL4EL2D", "In Da Club - part 2")
time.sleep(4)

# Test 14: Imperial March (Star Wars)
beep("MFO4T120L4GGG L8E-.L16B-L4GL8E-.L16B-L2G", "Imperial March - part 1")
time.sleep(3)
beep("MFO5T120L4DDL4DL8<E-.L16B-L4GL8E-.L16B-L2G", "Imperial March - part 2")
time.sleep(4)

# Test 15: Never Gonna Give You Up (Rick Astley) - rickroll the drone
beep("MFO4T114L8GGAB-L4>DL8D<B-L2A", "Rickroll - part 1")
time.sleep(3)
beep("MFO4T114L8GGAB-L4>CL8<AL2G", "Rickroll - part 2")
time.sleep(4)

print("\n[DONE] Did you hear the buzzer?")
print("  If not, check:")
print("  - Cube has a buzzer connected")
print("  - Volume is audible (some Cubes have quiet built-in buzzers)")
print("  - Try connecting an external buzzer to the BUZZ port")
