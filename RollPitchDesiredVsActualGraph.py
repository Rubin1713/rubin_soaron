import matplotlib.pyplot as plt
from pymavlink import mavutil
from matplotlib.animation import FuncAnimation
import math

# --- Step 1: Connection Setup ---
# Using your verified UDP connection for HM30
target_ip = "192.168.144.12" 
connection = mavutil.mavlink_connection(f'udpout:{target_ip}:19856')
print(f"--- Connected to {target_ip} | Waiting for Mavlink Data ---")

# Data Buffers for Rolling Window
data = {
    'act_p': [], 'des_p': [],
    'act_r': [], 'des_r': []
}
MAX_POINTS = 100 # How many points to show on the screen at once

# --- Step 2: Data Fetching ---
def fetch_telemetry():
    # Send heartbeat to HM30 to keep data flowing
    connection.mav.heartbeat_send(
        mavutil.mavlink.MAV_TYPE_GCS, 
        mavutil.mavlink.MAV_AUTOPILOT_INVALID, 0, 0, 0
    )

    # Listen for Actual Attitude and Desired Nav Output
    msg_act = connection.recv_match(type='ATTITUDE', blocking=True, timeout=0.1)
    msg_des = connection.recv_match(type='NAV_CONTROLLER_OUTPUT', blocking=True, timeout=0.1)
    
    if msg_act and msg_des:
        return {
            'rp': math.degrees(msg_act.pitch),
            'dp': msg_des.nav_pitch,        # ArduPilot NAV_CONTROLLER_OUTPUT is already in deg
            'rr': math.degrees(msg_act.roll),
            'dr': msg_des.nav_roll
        }
    return None

# --- Step 3: Graph Setup ---
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
plt.subplots_adjust(hspace=0.4)

def setup_axis(ax, title):
    ax.set_title(title)
    ax.set_ylabel("Degrees")
    ax.set_ylim(-30, 30) # Adjust based on your flight tilt limits
    ax.grid(True, alpha=0.3)
    return ax.plot([], [], 'b-', label='Actual')[0], ax.plot([], [], 'r--', label='Desired')[0]

line_act_p, line_des_p = setup_axis(ax1, "Pitch: Actual vs Desired")
line_act_r, line_des_r = setup_axis(ax2, "Roll: Actual vs Desired")
ax1.legend(loc='upper right')
ax2.legend(loc='upper right')

# --- Step 4: Animation Loop ---
def update(frame):
    vals = fetch_telemetry()
    if vals:
        data['act_p'].append(vals['rp'])
        data['des_p'].append(vals['dp'])
        data['act_r'].append(vals['rr'])
        data['des_r'].append(vals['dr'])
        
        # Maintain rolling window
        for key in data:
            if len(data[key]) > MAX_POINTS:
                data[key].pop(0)
            
        x = range(len(data['act_p']))
        line_act_p.set_data(x, data['act_p'])
        line_des_p.set_data(x, data['des_p'])
        line_act_r.set_data(x, data['act_r'])
        line_des_r.set_data(x, data['des_r'])
        
        ax1.set_xlim(0, MAX_POINTS)
        ax2.set_xlim(0, MAX_POINTS)
        
    return line_act_p, line_des_p, line_act_r, line_des_r

# Interval is 50ms (20Hz update)
ani = FuncAnimation(fig, update, interval=50, blit=True, cache_frame_data=False)
plt.show()
