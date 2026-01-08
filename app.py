"""import asyncio
import json
import os
import signal
import subprocess
import time

import serial.tools.list_ports
import websockets
from pymavlink import mavutil

# Global dictionary to hold the MAVLink data
data_dict = {
    "BATTERY_STATUS": None,
    "ARM_STATUS": None,
    "FLIGHT_MODE": None,
    "LONGITUDE": None,
    "LATITUDE": None,
    "ALTITUDE": None,
    "GPS_FIX_TYPE": None,
    "GPS_STRENGTH": None,
    "GPS_SATELLITES_VISIBLE": None,
    "SPEED_VX": None,
    "SPEED_VY": None,
    "SPEED_VZ": None,
    "GROUND_SPEED": None,
    "HEADING": None,
    "ROLL": None,
    "PITCH": None,
    "YAW": None,
}

connection = None


# Function to find the correct device node
def find_serial_device():
    ports = list(serial.tools.list_ports.comports())
    for port in ports:
        if "ttyUSB" in port.device or "ttyACM" in port.device:
            return port.device
    return None


# Function to decode the flight mode
def get_flight_mode(mode, connection):
    mode_mapping = connection.mode_mapping()
    for mode_name, mode_id in mode_mapping.items():
        if mode_id == mode:
            return mode_name
    return None


def gps_raw_int_callback(message):
    # GPS fix types
    gps_fix_types = {
        0: "No GPS",
        1: "No Fix",
        2: "2D Fix",
        3: "3D Fix",
        4: "DGPS",
        5: "RTK Float",
        6: "RTK Fixed",
        7: "Static",
        8: "PPP",
    }

    # Print GPS fix type
    fix_type = message.fix_type

    # HDOP (Horizontal Dilution of Precision)
    hdop = message.eph / 100.0

    if fix_type == 0:
        gps_quality = "unknown"

    # Overall GPS Signal Strength assessment based on HDOP
    elif fix_type >= 2:  # Ensure we have at least a 2D fix
        if hdop < 1.0:
            gps_quality = "full"
        elif hdop < 2.0:
            gps_quality = "strong"
        elif hdop < 5.0:
            gps_quality = "medium"
        else:
            gps_quality = "weak"
    else:
        gps_quality = "zero"

    return gps_quality, gps_fix_types.get(fix_type, "unknown")


def write_to_dict(msg, connection):
    global data_dict
    if msg.get_type() == "BATTERY_STATUS":
        data_dict["BATTERY_STATUS"] = msg.battery_remaining

    elif msg.get_type() == "HEARTBEAT":
        arming_status = msg.base_mode & mavutil.mavlink.MAV_MODE_FLAG_SAFETY_ARMED
        flight_mode = get_flight_mode(msg.custom_mode, connection)
        data_dict["ARM_STATUS"] = arming_status
        data_dict["FLIGHT_MODE"] = flight_mode

    elif msg.get_type() == "GPS_RAW_INT":
        strength, fix_type = gps_raw_int_callback(msg)
        data_dict["GPS_FIX_TYPE"] = fix_type
        data_dict["GPS_STRENGTH"] = strength
        data_dict["GPS_SATELLITES_VISIBLE"] = msg.satellites_visible
        data_dict["LATITUDE"] = (msg.lat / 1e7).__round__(3)
        data_dict["LONGITUDE"] = (msg.lon / 1e7).__round__(3)
        data_dict["ALTITUDE"] = msg.alt / 1000.0  # m

    elif msg.get_type() == "GLOBAL_POSITION_INT":
        data_dict["SPEED_VX"] = (msg.vx / 100.0).__round__(1)  # m/s
        data_dict["SPEED_VY"] = (msg.vy / 100.0).__round__(1)  # m/s
        data_dict["SPEED_VZ"] = (msg.vz / 100.0).__round__(1)  # m/s
        # data_dict["HEADING"] = msg.hdg

    elif msg.get_type() == "ATTITUDE":
        data_dict["ROLL"] = msg.roll.__round__(2)
        data_dict["PITCH"] = msg.pitch.__round__(2)
        data_dict["YAW"] = msg.yaw.__round__(2)

    elif msg.get_type() == "VFR_HUD":
        data_dict["GROUND_SPEED"] = msg.groundspeed.__round__(2)  # m/s
        data_dict["HEADING"] = msg.heading


async def update_dict(websocket):
    global connection

    while True:
        try:
            msg = connection.recv_match(blocking=False) #True2false changed
            if msg:
                write_to_dict(msg, connection)
                # print("Message received: \n", json.dumps(data_dict, indent=4))
            else:
                #print("No message") changed
                pass
            await asyncio.sleep(0)
        except Exception as e:
            print(f"Error: {e}")
            connection = None
            try:
                await connectDevice(websocket)
            except Exception as e:
                connection = None
                error_message = f"Error connecting to MAVLink device: {e}"
                await websocket.send(json.dumps(data_dict))
                await asyncio.sleep(1)  # Retry connection after delay
                continue
            await asyncio.sleep(1)  # Retry connection after delay
            continue

""" """ changes from old
async def send_data(websocket):
    global connection
    global data_dict
    while True:
        if connection is None or not connection.port.is_open:
            await asyncio.sleep(1)  # Retry connection after delay
            continue
        await websocket.send(json.dumps({"message": data_dict, "error": False}))
        await asyncio.sleep(0.1)  # Interval in seconds
""" """

async def send_data(websocket):
    global connection, data_dict
    while True:
        if connection is None or not connection.port.is_open:
            await asyncio.sleep(1)
            continue

        await websocket.send(json.dumps(data_dict))
        await asyncio.sleep(0.1)


async def connectDevice(websocket):
    global connection

    device = find_serial_device()
    if device is None:
        raise Exception("No serial device found")
    connection = mavutil.mavlink_connection(device, baud=115200)
    print(f"Connected to {device}")
  #  await websocket.send(json.dumps({"message": "connected", "error": True}))  changed

    connection.wait_heartbeat()
    print(
        "Heartbeat received from system (system %u component %u)"
        % (connection.target_system, connection.target_component)
    )

    # Function to request data stream
  
    connection.mav.request_data_stream_send(
    connection.target_system,
    connection.target_component,
    mavutil.mavlink.MAV_DATA_STREAM_ALL,
    10,
    1,
)

"""  """  # REQUEST STREAMS IMMEDIATELY
def request_data_stream():
    # Request all data streams at the highest rate
    connection.mav.request_data_stream_send(
        connection.target_system,
        connection.target_component,
        mavutil.mavlink.MAV_DATA_STREAM_ALL,
        10,
        1,
    )


async def read_mavlink_and_send(websocket, path):
    global connection
    while True:
        if connection is None or not connection.port.is_open:
            try:
                await connectDevice(websocket)
            except Exception as e:
                connection = None
                error_message = f"Error connecting to MAVLink device: {e}"
                await websocket.send(
                    json.dumps({"message": error_message, "error": True})
                )
                await asyncio.sleep(1)  # Retry connection after delay
                continue
       	print("Waiting for message")
        # Request data streams
    #    request_data_stream()  commented the old
        update_task = asyncio.create_task(update_dict(websocket))
        send_task = asyncio.create_task(send_data(websocket))

        try:
            await asyncio.gather(update_task, send_task)
        except Exception as e:
            print("WebSocket connection closed")
            connection = None
            update_task.cancel()
            send_task.cancel()
            break
""" """
async def read_mavlink_and_send(websocket, path):
    global connection
    while True:
        if connection is None or not connection.port.is_open:
            try:
                await connectDevice(websocket)
            except Exception:
                connection = None
                await asyncio.sleep(1)
                continue

        print("Waiting for message")

        update_task = asyncio.create_task(update_dict(websocket))
        send_task = asyncio.create_task(send_data(websocket))

        try:
            await asyncio.gather(update_task, send_task)
        except Exception:
            print("WebSocket connection closed")
            connection = None
            update_task.cancel()
            send_task.cancel()
            break

def kill_process_on_port(port):
    try:
        # Find the PID using the port
        result = subprocess.run(
            ["lsof", "-ti", f"tcp:{port}"], capture_output=True, text=True
        )
        pids = result.stdout.strip().split()
        for pid in pids:
            os.kill(int(pid), signal.SIGKILL)
        print(f"Killed process on port {port}")
    except Exception as e:
        print(f"Failed to kill process on port {port}: {e}")


port = 8765
# Kill any existing process on port 8765
# kill_process_on_port(port=port)

time.sleep(2)

start_server = websockets.serve(read_mavlink_and_send, "localhost", port=port)

asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever() """
# The above code is Old code 
#-------------------------------------------------------------------------------------------------------
# New code with fake telem.
import asyncio
import json
import time
import math
import random
import websockets


def generate_fake_telemetry(): 				         # fake telemetry generator using current time 
    t = time.time()						 # takes current time to get randomsed values for all telem. values excet battery
    return {
        "BATTERY_STATUS": random.randint(60, 95),
        "ARM_STATUS": 1,
        "FLIGHT_MODE": "GUIDED",
        "LATITUDE": round(12.9716 + math.sin(t / 10) * 0.0001, 6),
        "LONGITUDE": round(77.5946 + math.cos(t / 10) * 0.0001, 6),
        "ALTITUDE": round(10 + math.sin(t / 3) * 2, 1),
        "GPS_FIX_TYPE": "3D Fix",
        "GPS_STRENGTH": "Strong",
        "GPS_SATELLITES_VISIBLE": 12,
        "SPEED_VX": round(math.sin(t) * 2, 2),
        "SPEED_VY": round(math.cos(t) * 2, 2),
        "SPEED_VZ": 0.0,
        "GROUND_SPEED": round(abs(math.sin(t)) * 3, 2),
        "HEADING": int((t * 20) % 360),
        "ROLL": round(math.sin(t) * 15, 1),
        "PITCH": round(math.cos(t) * 10, 1),
        "YAW": int((t * 20) % 360),
        "LIDAR_DISTANCE": round(0.5 + abs(math.sin(t)) * 4, 2), # meters (0.5 → 4.5)

    }

async def handler(websocket):     		 	      	# client handler
    print("Flutter connected")

    try:
        while True:
            payload = {					     	# dict formated payload similar to format in flutter 
                "error": False,
                "message": generate_fake_telemetry()
            }

            await websocket.send(json.dumps(payload))	        # converted to json and send through websocket server to clients
            await asyncio.sleep(0.1)

    except websockets.ConnectionClosed:
        print("Flutter disconnected")

async def main():  						# async used to do concurrent tasks
    print(" WebSocket running on ws://127.0.0.1:8765")
    async with websockets.serve(handler, "127.0.0.1", 8765):    # websocket server with client handler, loopback address (localhost) and port number
        await asyncio.Future()  				# run continuously forever
        
asyncio.run(main())						# entry point of function --> points to main()

