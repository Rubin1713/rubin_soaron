import asyncio
import json
import websockets
import threading
import time
from pymavlink import mavutil

# ----------------------------
# MAVLINK CONNECTION
# ----------------------------
mav = mavutil.mavlink_connection(
    '/dev/ttyACM0',
    baud=57600
)

print(" Waiting for heartbeat...")
mav.wait_heartbeat()
print(" MAVLink connected")

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

# ----------------------------
# MAVLINK READER THREAD
# ----------------------------
def mavlink_reader():
    while True:
        msg = mav.recv_match(blocking=True)
        if not msg:
            continue

        with lock:
            t = msg.get_type()

            if t == "HEARTBEAT":
                telemetry["ARM_STATUS"] = int(
                    msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
                )
                telemetry["FLIGHT_MODE"] = mavutil.mode_string_v10(msg)

            elif t == "SYS_STATUS":
                telemetry["BATTERY_STATUS"] = msg.battery_remaining

            elif t == "GPS_RAW_INT":
                telemetry["LATITUDE"] = msg.lat / 1e7
                telemetry["LONGITUDE"] = msg.lon / 1e7
                telemetry["GPS_SATELLITES_VISIBLE"] = msg.satellites_visible
                telemetry["GPS_FIX_TYPE"] = "3D Fix" if msg.fix_type >= 3 else "No Fix"
                telemetry["GPS_STRENGTH"] = "Strong" if msg.fix_type >= 3 else "Weak"

            elif t == "GLOBAL_POSITION_INT":
                telemetry["ALTITUDE"] = msg.relative_alt / 1000.0
                telemetry["SPEED_VX"] = msg.vx / 100.0
                telemetry["SPEED_VY"] = msg.vy / 100.0
                telemetry["SPEED_VZ"] = msg.vz / 100.0
                telemetry["HEADING"] = msg.hdg / 100.0

            elif t == "ATTITUDE":
                telemetry["ROLL"] = msg.roll
                telemetry["PITCH"] = msg.pitch
                telemetry["YAW"] = msg.yaw

            elif t == "VFR_HUD":
                telemetry["GROUND_SPEED"] = msg.groundspeed

            elif t == "DISTANCE_SENSOR":
                telemetry["LIDAR_DISTANCE"] = msg.current_distance / 100.0


threading.Thread(target=mavlink_reader, daemon=True).start()

# ----------------------------
# WEBSOCKET SERVER (10 Hz)
# ----------------------------
async def websocket_handler(websocket):
    print(" Flutter connected")

    try:
        while True:
            with lock:
                snapshot = telemetry.copy()

            await websocket.send(json.dumps({
                "error": False,
                "message": snapshot
            }))

            await asyncio.sleep(0.1)  # 🔥 10 Hz ONLY

    except websockets.ConnectionClosed:
        print(" Flutter disconnected")

# ----------------------------
# MAIN
# ----------------------------
async def main():
    print(" WebSocket ws://127.0.0.1:8765")
    async with websockets.serve(websocket_handler, "127.0.0.1", 8765):
        await asyncio.Future()

asyncio.run(main())
