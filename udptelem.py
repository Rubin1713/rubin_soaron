import asyncio
import json
import websockets
import threading
import time
import math
import os
import subprocess
from pymavlink import mavutil

def kill_existing_server(port):
	try:
		result=subprocess.check_output(["lsof","-t",f"-i:{port}"])
		pids=result.decode().split()
		for pid in pids:
			print(f"cleaning ghost process on port {port}:PID {pid}")
			os.system(f"kill -9 {pid}")
	except subprocess.CalledProcessError:
		pass
kill_existing_server(8765)
# ----------------------------
# MAVLINK CONNECTION (UDP MODE)
# ----------------------------
# Confirming 192.168.144.12 as the server address
mav = mavutil.mavlink_connection('udpout:192.168.144.12:19856')

def connect_to_hm30():
    print("--- Attempting to Wake Up HM30 LAN Port ---")
    while True:
        # Send a heartbeat TO the HM30 to tell it "I am here, send data to this IP"
        # This is the "trigger" that was working in your udptry script
        mav.mav.heartbeat_send(
            mavutil.mavlink.MAV_TYPE_GCS, 
            mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0
        )
        
        # Wait for a response with a short timeout
        msg = mav.wait_heartbeat(timeout=1.0)
        if msg:
            print(f"--- MAVLink Connected (System {mav.target_system}) ---")
            break
        else:
            print("Still waiting for HM30 heartbeat... (Check Link LED)")

# Run the connection trigger BEFORE starting threads
connect_to_hm30()

# ----------------------------
# SHARED TELEMETRY STATE
# ----------------------------
telemetry = {
    "BATTERY_STATUS": 0,
    "ARM_STATUS": 0,
    "FLIGHT_MODE": "UNKNOWN",
    "LATITUDE": 0.0,
    "LONGITUDE": 0.0,
    "ALTITUDE": 0.0,
    "GPS_FIX_TYPE": "No Fix",
    "GPS_STRENGTH": "Unknown",
    "GPS_SATELLITES_VISIBLE": 0,
    "SPEED_VX": 0.0,
    "SPEED_VY": 0.0,
    "SPEED_VZ": 0.0,
    "GROUND_SPEED": 0.0,
    "HEADING": 0.0,
    "ROLL": 0.0,
    "PITCH": 0.0,
    "YAW": 0.0,
    "LIDAR_DISTANCE": 0.0,
}

lock = threading.Lock()

def mavlink_reader():
    while True:
        msg = mav.recv_match(blocking=True)
        if not msg:
            continue

        with lock:
            t = msg.get_type()
            if t == "HEARTBEAT":
                telemetry["ARM_STATUS"] = int(msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED)
                telemetry["FLIGHT_MODE"] = mavutil.mode_string_v10(msg)
            elif t == "SYS_STATUS":
                telemetry["BATTERY_STATUS"] = msg.battery_remaining    
            elif t == "GPS_RAW_INT":
                telemetry["LATITUDE"] = msg.lat / 1e7
                telemetry["LONGITUDE"] = msg.lon / 1e7
                telemetry["GPS_SATELLITES_VISIBLE"] = msg.satellites_visible
                telemetry["GPS_FIX_TYPE"] = "3D Fix" if msg.fix_type >= 3 else "No Fix"
            elif t == "GLOBAL_POSITION_INT":
                telemetry["ALTITUDE"] = msg.relative_alt / 1000.0
                telemetry["HEADING"] = msg.hdg / 100.0
                telemetry["SPEED_VX"] = msg.vx / 100.0
                telemetry["SPEED_VY"] = msg.vy / 100.0
                telemetry["SPEED_VZ"] = msg.vz / 100.0
            elif t == "ATTITUDE":
                telemetry["ROLL"] = math.degrees(msg.roll)
                telemetry["PITCH"] = math.degrees(msg.pitch)
                telemetry["YAW"] = math.degrees(msg.yaw)
            elif t == "VFR_HUD":
                telemetry["GROUND_SPEED"] = msg.groundspeed
            elif t == "DISTANCE_SENSOR":
                telemetry["LIDAR_DISTANCE"] = msg.current_distance /100.0

threading.Thread(target=mavlink_reader, daemon=True).start()

async def websocket_handler(websocket):
    print(" Flutter Connected")
    try:
        while True:
            with lock:
                snapshot = telemetry.copy()
            await websocket.send(json.dumps({"error": False, "message": snapshot}))
            await asyncio.sleep(0.1)
    except websockets.ConnectionClosed:
        print(" Flutter Disconnected")

async def main():
    print(" WebSocket Server at ws://127.0.0.1:8765")
    async with websockets.serve(websocket_handler, "127.0.0.1", 8765,reuse_address=True):
        await asyncio.Future()

asyncio.run(main())
