import subprocess
import os
import time
import socket

RTSP_URL="rtsp://192.168.144.25:8554/main.264"
SAVE_PATH=os.path.expanduser("~/Videos")
CHECK_INTERVAL=3

if not os.path.exists(SAVE_PATH):
	os.makedirs(SAVE_PATH,mode=0o755, exist_ok=True)
def is_camera_online(url):
	ip="192.168.144.25"
	port=8554
	try:
		with socket.create_connection((ip,port),timeout=2):
			return True
	except OSError:
		return False
			
print("MONITORING HM30 CAMERA LINK")

active_process=None

try:
	while True:
		online=is_camera_online(RTSP_URL)
		if online and active_process is None:
			timestamp=time.strftime("%Y%m%d-%H%M%S")
			filename=os.path.join(SAVE_PATH,f"drone_{timestamp}.mkv")
			print(f"--------Camera detected! starting recording:{filename}---")
			cmd=['ffmpeg','-y','-rtsp_transport','udp','-i',RTSP_URL,'-c','copy','-f','matroska','-fflags','flush_packets',filename]
			active_process= subprocess.Popen(cmd,stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
			
		elif not online and active_process is not None:
			print("Camera offline.stopping Recording")
			active_process.terminate()
			active_process.wait()
			active_process=None
			
		time.sleep(CHECK_INTERVAL)
		
except KeyboardInterrupt:
	if active_process:
		active_process.terminate()
	print("\n Monitor Stopped")
