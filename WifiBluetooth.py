"""import time

def get_wifi_stats():
    try:
        with open("/proc/net/wireless", "r") as f:
            lines = f.readlines()
            if len(lines) > 2:
                # Line 3 contains the actual stats for wlan0
                data = lines[2].split()
                # link_quality: based on a scale (usually out of 70)
                link_quality = float(data[2].replace('.', ''))
                # signal_level: strength in dBm (e.g., -50.0)
                signal_level = float(data[3].replace('.', ''))
                
                # Convert link quality to percentage (approximate)
                percentage = int((link_quality / 70) * 100)
                
                return {
                    "strength_dbm": signal_level,
                    "percentage": percentage
                }
    except Exception as e:
        print(f"Error reading wifi: {e}")
    return {"strength_dbm": 0, "percentage": 0}

# Example of how to use it
if __name__ == "__main__":
    while True:
        stats = get_wifi_stats()
        print(f"Signal: {stats['strength_dbm']} dBm | Strength: {stats['percentage']}%")
        time.sleep(1)
"""

import subprocess
import re
import time

def get_wifi_data():
    """Returns connected SSID and Signal Strength (dBm)."""
    try:
        # Get SSID
        ssid_output = subprocess.check_output(["iwgetid", "-r"]).decode("utf-8").strip()
        
        # Get Signal Level from /proc/net/wireless
        with open("/proc/net/wireless", "r") as f:
            lines = f.readlines()
            if len(lines) > 2:
                data = lines[2].split()
                signal_level = float(data[3].replace('.', ''))
                # Convert to 0-100% (Roughly -100dBm to -30dBm range)
                percentage = max(0, min(100, int(2 * (signal_level + 100))))
                return {"ssid": ssid_output, "strength": percentage, "dbm": signal_level}
    except Exception:
        return {"ssid": "Disconnected", "strength": 0, "dbm": -100}

def get_bluetooth_data():
    """Returns connected device name and RSSI (signal strength)."""
    try:
        # Get list of connected devices via hcitool
        # Note: Device must be paired and connected
        conn_output = subprocess.check_output(["hcitool", "con"]).decode("utf-8")
        # Extract MAC address (e.g., 00:11:22:33:44:55)
        addr_match = re.search(r'([0-9A-F]{2}:){5}[0-9A-F]{2}', conn_output, re.I)
        
        if addr_match:
            mac_addr = addr_match.group(0)
            # Get Device Name
            name_output = subprocess.check_output(["bluetoothctl", "info", mac_addr]).decode("utf-8")
            name = re.search(r"Name: (.*)", name_output).group(1)
            
            # Get RSSI (Signal Strength)
            rssi_output = subprocess.check_output(["hcitool", "rssi", mac_addr]).decode("utf-8")
            rssi_value = int(re.search(r"RSSI return value: (-?\d+)", rssi_output).group(1))
            
            # Map RSSI to 0-100% (Bluetooth RSSI is usually 0 to -20 for good, -60 for bad)
            bt_percentage = max(0, min(100, 100 + (rssi_value * 2)))
            
            return {"device": name, "strength": bt_percentage, "rssi": rssi_value}
    except Exception:
        pass
    return {"device": "None", "strength": 0, "rssi": 0}

if __name__ == "__main__":
    print("Starting Drone Comms Monitor...")
    while True:
        wifi = get_wifi_data()
        bt = get_bluetooth_data()
        
        print(f"--- Telemetry ---")
        print(f"WiFi: {wifi['ssid']} | Strength: {wifi['strength']}% ({wifi['dbm']} dBm)")
        print(f"BT:   {bt['device']} | Strength: {bt['strength']}% (RSSI: {bt['rssi']})")
        print("-" * 20)
        
        time.sleep(2) # Update every 2 seconds to save CPU
