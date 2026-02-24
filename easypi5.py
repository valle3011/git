from ultralytics import YOLO
from picamera2 import Picamera2
import cv2
import time

model = YOLO("yolov8n.onnx", task="detect")

picam2 = Picamera2()
config = picam2.create_preview_configuration(main={"size": (640, 640), "format": "RGB888"})
picam2.configure(config)
picam2.start()

i = 0
last_save = 0.0
last_print = 0.0

while True:
    frame = picam2.capture_array()

    i += 1
    if i % 3 != 0:
        continue

    results = model(frame, imgsz=640, conf=0.4, classes=[0], max_det=1, verbose=False)
    r = results[0]
    person = (r.boxes is not None and len(r.boxes) > 0)

    now = time.time()
    if now - last_print > 0.2:
        print("STOP" if person else "FREE")
        last_print = now

    # alle 1 Sekunde ein Debug-Bild schreiben
    if now - last_save > 1.0:
        out = frame.copy()
        if person:
            x1, y1, x2, y2 = r.boxes[0].xyxy[0]
            cv2.rectangle(out, (int(x1), int(y1)), (int(x2), int(y2)), (0, 255, 0), 2)
            cv2.putText(out, "STOP", (15, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 0, 255), 3)
        else:
            cv2.putText(out, "FREE", (15, 45), cv2.FONT_HERSHEY_SIMPLEX, 1.3, (0, 255, 0), 3)

        cv2.imwrite(f"debug_{int(time.time())}.jpg", out)
        print("saved debug.jpg")
        last_save = now
