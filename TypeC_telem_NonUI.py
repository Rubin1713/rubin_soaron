from pymavlink import mavutil
import time

# 1. Connect to Pixhawk via HM30 USB
master = mavutil.mavlink_connection(
    '/dev/ttyACM0',
    baud=57600
)

print("Waiting for heartbeat...")
master.wait_heartbeat()
print("Heartbeat received")

print("Listening for ALTITUDE + LiDAR...")

lidar_cm = None
altitude_m = None

while True:
    msg = master.recv_match(
        type=['DISTANCE_SENSOR', 'GLOBAL_POSITION_INT'],
        blocking=True
    )

    if not msg:
        continue

    msg_type = msg.get_type()

    # 2. LiDAR (TFmini)
    if msg_type == 'DISTANCE_SENSOR':
        lidar_cm = msg.current_distance
        lidar_m = lidar_cm / 100.0

    # 3. Altitude (relative to takeoff)
    elif msg_type == 'GLOBAL_POSITION_INT':
        altitude_m = msg.relative_alt / 1000.0  # mm → meters

    # 4. Print only when both are available
    if lidar_cm is not None and altitude_m is not None:
        print(
            f"Altitude: {altitude_m:.2f} m | "
            f"LiDAR: {lidar_m:.2f} m"
        )

    time.sleep(0.02)
