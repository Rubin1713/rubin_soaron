from pymavlink import mavutil
import math

# Try .11 first, if no data, stop and change to .12
target_ip = "192.168.144.12" 
connection = mavutil.mavlink_connection(f'udpout:{target_ip}:19856')

print(f"--- Listening on {target_ip} ---")

while True:
    # Send a heartbeat TO the HM30 to tell it "I am here, send me data"
    connection.mav.heartbeat_send(mavutil.mavlink.MAV_TYPE_GCS, 
                                 mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0)
    
    # Search specifically for the ATTITUDE message
    msg = connection.recv_match(type='ATTITUDE', blocking=True, timeout=2)
    msg_bat =connection.recv_match(type='BATTERY_STATUS', blocking=True)
    if not msg_bat:
        continue

    # Voltage array (per-cell, in millivolts)
    voltages = msg_bat.voltages
    # Current in 10 mA units → divide by 100 to get Amps
    current = msg_bat.current_battery / 100.0
    # Remaining battery percentage
    remaining = msg_bat.battery_remaining

    # --- Step 3: Print nicely ---
    print("Battery Report:")
  #  print(f"  Voltages (mV): {voltages}")
    print(f"  Current (A): {current}")
    print(f"  Remaining (%): {remaining}")
    print("-" * 40)
    
    if msg:
        # Convert Radians to Degrees
        roll = math.degrees(msg.roll)
        pitch = math.degrees(msg.pitch)
        yaw = math.degrees(msg.yaw)
        
        print(f"ROLL: {roll:.2f} | PITCH: {pitch:.2f} | YAW: {yaw:.2f}")
    else:
        print("No Attitude data yet... check if Pixhawk is ARMED or sending Heartbeats")
