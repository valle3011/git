from ultralytics import YOLO
import cv2

# Load ONNX model
model = YOLO("best.onnx")

# Open camera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        print("Camera not working")
        break

    # Run YOLO inference
    results = model(frame, imgsz=320, conf=0.5)

    for r in results:
        for box in r.boxes:
            cls = int(box.cls[0])
            name = model.names[cls]

            if name == "person":
                x1, y1, x2, y2 = box.xyxy[0]
                x_center = (x1 + x2) / 2
                frame_center = frame.shape[1] / 2

                if x_center < frame_center:
                    print("TURN LEFT")
                else:
                    print("TURN RIGHT")

    cv2.imshow("Detection", frame)

    if cv2.waitKey(1) == 27:  # ESC key
        break

cap.release()
cv2.destroyAllWindows()