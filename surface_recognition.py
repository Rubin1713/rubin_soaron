import cv2
from ultralytics import YOLO
import threading
import time

# --- CONFIGURATION ---
RTSP_URL = "rtsp://192.168.144.25:8554/main.264"
surface_model = YOLO("best2_ncnn_model",task="classify")
color_model   = YOLO("colorwall_ncnn_model",task="classify")

class RTSPStream:
    def _init_(self, url):
        self.cap = cv2.VideoCapture(url, cv2.CAP_FFMPEG)
        self.cap.set(cv2.CAP_PROP_BUFFERSIZE, 1) # Force minimum buffering
        self.status, self.frame = self.cap.read()
        self.stopped = False

    def start(self):
        # Dedicated thread to constantly empty the RTSP buffer
        threading.Thread(target=self.update, args=(), daemon=True).start()
        return self

    def update(self):
        while not self.stopped:
            if not self.cap.isOpened():
                self.stopped = True
            else:
                self.status, self.frame = self.cap.read()

    def get_frame(self):
        return self.frame

    def stop(self):
        self.stopped = True
        self.cap.release()

# Start the dedicated reader thread
stream = RTSPStream(RTSP_URL).start()
time.sleep(2) # Allow buffer to warm up

print("Vision Active. Press 'q' on the video window to exit.")

while True:
    frame = stream.get_frame()
    if frame is None:
        continue

    # 1. Faster Inference: Resize before processing
    small_frame = cv2.resize(frame, (224,224 ))

    # 2. Run Models
    s_results = surface_model(small_frame, verbose=False)
    c_results = color_model(small_frame, verbose=False)

    # 3. Logic
    try:
        if s_results[0].probs is not None:
            s_id = int(s_results[0].probs.top1)
            s_name=s_results[0].names[s_id]
        else:
            s_name="N/A"
			
        if c_results[0].probs is not None:
            c_id = int(c_results[0].probs.top1)
            c_name=c_results[0].names[c_id]
        else:
            c_name="N/A"
    except Exception as e:
        s_name,c_name="Error","Error"

    # 4. Fast UI: Only draw on the original frame
    cv2.putText(frame, f"S: {s_name} C: {c_name}", (10, 50), 
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    
    cv2.imshow("Drone Cockpit Vision", frame)

    # Key 'q' works better now because the loop isn't 'stuck' in the buffer
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

stream.stop()
cv2.destroyAllWindows()
