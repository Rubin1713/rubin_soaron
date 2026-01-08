import asyncio
import json
import websockets
from pymavlink import mavutil

# ----------------------------
# MAVLink UDP INPUT (HM30 SIM)
# ----------------------------
mav = mavutil.mavlink_connection(            #mav is object for mavutil class
    'udpin:127.0.0.1:14550',
    source_system=255
)

print(" Listening for MAVLink UDP on port 14550")

# ----------------------------
# TELEMETRY STATE (NO NULLS)
# ----------------------------
telemetry = {
    "BATTERY_STATUS": 80,
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

    "HEADING": 0,
    "ROLL": 0.0,
    "PITCH": 0.0,
    "YAW": 0.0,

    "LIDAR_DISTANCE": 0.0,
}

# ----------------------------
# MAVLINK DECODER
# ----------------------------
def update_from_mavlink(msg):
    if msg.get_type() == "HEARTBEAT":
        telemetry["ARM_STATUS"] = int(
            msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
        )
        telemetry["FLIGHT_MODE"] = mavutil.mode_string_v10(msg)

    elif msg.get_type() == "GPS_RAW_INT":
        telemetry["LATITUDE"] = msg.lat / 1e7
        telemetry["LONGITUDE"] = msg.lon / 1e7
        telemetry["ALTITUDE"] = msg.alt / 1000.0
        telemetry["GPS_SATELLITES_VISIBLE"] = msg.satellites_visible
        telemetry["GPS_FIX_TYPE"] = "3D Fix" if msg.fix_type >= 3 else "No Fix"
        telemetry["GPS_STRENGTH"] = "Strong" if msg.fix_type >= 3 else "Weak"

    elif msg.get_type() == "GLOBAL_POSITION_INT":
        telemetry["SPEED_VX"] = msg.vx / 100.0
        telemetry["SPEED_VY"] = msg.vy / 100.0
        telemetry["SPEED_VZ"] = msg.vz / 100.0
        telemetry["HEADING"] = msg.hdg / 100.0

    elif msg.get_type() == "ATTITUDE":
        telemetry["ROLL"] = msg.roll
        telemetry["PITCH"] = msg.pitch
        telemetry["YAW"] = msg.yaw

    elif msg.get_type() == "VFR_HUD":
        telemetry["GROUND_SPEED"] = msg.groundspeed

    elif msg.get_type() == "DISTANCE_SENSOR":
        telemetry["LIDAR_DISTANCE"] = msg.current_distance / 100.0


# ----------------------------
# WEBSOCKET SERVER
# ----------------------------
async def websocket_handler(websocket):
    print("Flutter connected")

    try:
        while True:
            msg = mav.recv_match(blocking=False)       # make recv function non blocking and msg is the instance of all received data
            if msg:
                update_from_mavlink(msg)	       # update default telemetry with received mavlink telemetry

            await websocket.send(json.dumps({		# Send the data in the form of JSON into websockets (Flutter also must use this format) 
                "error": False,
                "message": telemetry
            }))

            await asyncio.sleep(0.1)

    except websockets.ConnectionClosed:			# exceptions for if websocket connection is lost
        print(" Flutter disconnected")

#-----------------------------------
#MAIN FUNCTION
#-----------------------------------
async def main():			
    print(" WebSocket running on ws://127.0.0.1:8765")
    async with websockets.serve(websocket_handler, "127.0.0.1", 8765):   # Client handler, default localhost port, loopback address for local server
        await asyncio.Future()


asyncio.run(main())	#entry point of main()

