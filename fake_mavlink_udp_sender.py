import time
import math
from pymavlink import mavutil

# UDP OUT (simulate HM30 Ground Unit)
master = mavutil.mavlink_connection(    #master is object for mavutil class 
    'udpout:127.0.0.1:14550',	#industry standard UDP port for mavlink protocol
    source_system=1,
    source_component=1
)

print(" Fake MAVLink UDP sender started on port 14550")

t0 = time.time()

while True:
    t = time.time() - t0

    # ================= HEARTBEAT =================
    master.mav.heartbeat_send(
        mavutil.mavlink.MAV_TYPE_QUADROTOR,
        mavutil.mavlink.MAV_AUTOPILOT_PX4,
        0,
        0,
        mavutil.mavlink.MAV_STATE_ACTIVE
    )

    # ================= GPS_RAW_INT =================
    lat = int((12.9716 + math.sin(t / 10) * 0.0001) * 1e7)
    lon = int((77.5946 + math.cos(t / 10) * 0.0001) * 1e7)
    alt_mm = int(10000 + math.sin(t) * 2000)  # mm

    master.mav.gps_raw_int_send(
        int(t * 1e6),   # time_usec
        3,              # fix_type (3D Fix)
        lat,
        lon,
        alt_mm,
        80,             # eph (cm)
        80,             # epv (cm)
        150,            # vel (cm/s)
        0,              # cog
        12              # satellites_visible
    )

    # ================= GLOBAL_POSITION_INT =================
    vx = int(math.sin(t) * 200)   # cm/s
    vy = int(math.cos(t) * 200)
    vz = int(math.sin(t / 2) * 100)

    master.mav.global_position_int_send(
        int(t * 1000),  # time_boot_ms
        lat,
        lon,
        alt_mm,
        alt_mm,
        vx,
        vy,
        vz,
        int((t * 20) % 360)
    )

    # ================= ATTITUDE =================
    roll  = math.sin(t) * 0.3
    pitch = math.cos(t) * 0.2
    yaw   = (t * 0.5) % (2 * math.pi)

    master.mav.attitude_send(
        int(t * 1000),
        roll,
        pitch,
        yaw,
        0.0,
        0.0,
        0.0
    )

    # ================= VFR_HUD =================
    master.mav.vfr_hud_send(
        abs(math.sin(t) * 5),   # groundspeed
        0,
        int((t * 20) % 360),    # heading
        50,
        alt_mm / 1000.0,
        80
    )

# ================= DISTANCE_SENSOR (LiDAR) =================
    lidar_cm = int((math.sin(t) + 1.5) * 100)  # 50cm–250cm

    master.mav.distance_sensor_send(
    	int(t * 1000),        # time_boot_ms
    	20,                   # min distance (cm)
    	300,                  # max distance (cm)
    	lidar_cm,             # current distance (cm)
    	mavutil.mavlink.MAV_DISTANCE_SENSOR_LASER,
    	0,                    # sensor id
    	0,                    # rotation = FORWARD 
    	0                     # covariance
    )


    time.sleep(0.1)

