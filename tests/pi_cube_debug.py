#!/usr/bin/env python3
"""
Quick diagnostic: what MAVLink messages is the Cube actually sending?
Prints every message type and how often each arrives over 5 seconds.

Usage:
    python tests/pi_cube_debug.py
"""
import sys
import os
import time
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from pymavlink import mavutil
import config

conn_str = config.CONNECTION_STR
print(f"[CUBE] Connecting: {conn_str}")
mav = mavutil.mavlink_connection(conn_str)
print("[CUBE] Waiting for heartbeat...")
mav.wait_heartbeat(timeout=10)
print(f"[CUBE] Connected to system {mav.target_system}")

# Request all streams
try:
    mav.mav.request_data_stream_send(
        mav.target_system, mav.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_ALL, 10, 1
    )
except Exception:
    pass

print(f"\nListening for 5 seconds...\n")

counts = {}
start = time.time()
while time.time() - start < 5.0:
    msg = mav.recv_msg()
    if msg:
        t = msg.get_type()
        counts[t] = counts.get(t, 0) + 1

print(f"{'Message Type':<35} {'Count':>6}")
print("-" * 42)
for t, c in sorted(counts.items(), key=lambda x: -x[1]):
    print(f"  {t:<33} {c:>6}")

print(f"\nTotal messages: {sum(counts.values())}")

# Now show one sample of the key ones
print(f"\n--- Latest values in mav.messages ---")
for key in ['GLOBAL_POSITION_INT', 'ATTITUDE', 'GPS_RAW_INT', 'SYS_STATUS']:
    if key in mav.messages:
        print(f"\n  {key}:")
        msg = mav.messages[key]
        for field in msg.get_fieldnames():
            print(f"    {field} = {getattr(msg, field)}")
    else:
        print(f"\n  {key}: NOT RECEIVED")
