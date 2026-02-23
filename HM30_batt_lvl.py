import socket
import time

# Use the IP that works with your ping
HM30_IP = "192.168.144.12"
UDP_PORT = 19856 

# Packet for CMD 0x16 (Request System Settings) with valid CRC16 
# [STX, CTRL, LEN_L, LEN_H, SEQ_L, SEQ_H, CMD_ID, CRC_L, CRC_H]
REQ_PACKET = bytearray([0x55, 0x66, 0x01, 0x00, 0x00, 0x00, 0x00, 0x16, 0xb2, 0xa6])

def get_gu_voltage():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(2.0)
    
    try:
        # Send the request to the Ground Unit
        sock.sendto(REQ_PACKET, (HM30_IP, UDP_PORT))
        
        # Capture the response
        raw_data, addr = sock.recvfrom(2048)
        
        # Search for the SIYI header 0x5566 [cite: 7]
        header_idx = raw_data.find(b'\x55\x66')
        
        if header_idx != -1:
            packet = raw_data[header_idx:]
            
            # Verify CMD ID 0x16 
            if len(packet) >= 12 and packet[7] == 0x16:
                # Byte 11 is 'Rc_bat' (Ground Unit Battery Level x 10V) 
                rc_bat_raw = packet[11]
                voltage = rc_bat_raw / 10.0
                
                # --- NEW LOGIC START ---
                # Linear Mapping: 7.0V = 20%, 8.4V = 100%
                # Formula: P = 20 + ((V - 7.0) / (8.4 - 7.0)) * (100 - 20)
                percentage = 20 + ((voltage - 7.0) / 1.4) * 80
                
                # Clamp percentage between 0 and 100 for display
                display_pct = max(0, min(100, percentage))
                
                # Check for low voltage alert
                alert_msg = ""
                if display_pct < 20:
                    alert_msg = " [LOW VOLTAGE DETECTED]"
                
                # Clear line and print updated status
                print(f"\r[HM30] GU Voltage: {voltage:.1f}V | Battery: {display_pct:.1f}%{alert_msg}", flush=True)
                # --- NEW LOGIC END ---
                
        else:
            print("\r[!] Header 5566 not found in the UDP stream",  flush=True)

    except socket.timeout:
        print("\r[!] No response - Check if Ground Unit is in UDP mode", end="", flush=True)
    except ZeroDivisionError:
        pass # Handle unexpected math errors
    finally:
        sock.close()

if __name__ == "__main__":
    print(f"Connecting to SIYI HM30 at {HM30_IP}...")
    while True:
        get_gu_voltage()
        time.sleep(1)
