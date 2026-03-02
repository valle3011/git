from ultralytics import YOLO
import serial
import time
import cv2
import numpy as np

class MotorController:
    def __init__(self, port):
        self.ser = serial.Serial(port, 115200, timeout=1)
        time.sleep(5)   # Arduino reset delay

    def send(self, cmd):
        self.ser.write((cmd + "\n").encode())
        reply = self.ser.readline().decode().strip()
        print("Arduino:", reply)

    def move_forward(self):
        self.send("FORWARD")

    def turn_left(self):
        self.send("LEFT")

    def turn_right(self):
        self.send("RIGHT")

    def stop(self):
        self.send("STOP")

    def cleanup(self):
        self.stop()
        self.ser.close()



# CAMERA CLASS (Pi Cam)

class Camera:
    def __init__(self, width=640, height=480):
        self.cap = cv2.VideoCapture(0)
        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret:
            return None
        return frame

    def release(self):
        self.cap.release()


# VISION SYSTEM

class VisionSystem:
    def __init__(self):
        self.model = YOLO("yolov8n.pt")
        self.frame_width = 640

    #Red Light Detection 
    def detect_red_light(self, frame):
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

        lower_red1 = np.array([0, 120, 70])
        upper_red1 = np.array([10, 255, 255])
        lower_red2 = np.array([170, 120, 70])
        upper_red2 = np.array([180, 255, 255])

        mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
        mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
        mask = mask1 | mask2

        red_pixels = cv2.countNonZero(mask)

        return red_pixels > 2000  # tune threshold

    #YOLO Obstacle Detection
    def detect_obstacles(self, frame):
        results = self.model(frame, imgsz=320, conf=0.5, verbose=False)

        obstacles = []
        for r in results:
            for box in r.boxes:
                x1, y1, x2, y2 = map(int, box.xyxy[0])
                area = (x2 - x1) * (y2 - y1)
                cx = (x1 + x2) // 2
                obstacles.append((cx, area))

        return obstacles



# DECISION SYSTEM

class RobotController:
    def __init__(self, motor, camera, vision):
        self.motor = motor
        self.camera = camera
        self.vision = vision

        self.FRAME_LEFT = 640 * 0.4
        self.FRAME_RIGHT = 640 * 0.6
        self.AREA_THRESHOLD = 25000

    def run(self):
        try:
            while True:
                frame = self.camera.get_frame()
                if frame is None:
                    continue

                #Red Light Priority
                if self.vision.detect_red_light(frame):
                    print("Red Light Detected → STOP")
                    self.motor.stop()
                    continue

                #YOLO Obstacles
                obstacles = self.vision.detect_obstacles(frame)

                if obstacles:
                    cx, area = max(obstacles, key=lambda x: x[1])

                    if area > self.AREA_THRESHOLD:
                        self.motor.stop()

                    elif cx < self.FRAME_LEFT:
                        self.motor.turn_right()

                    elif cx > self.FRAME_RIGHT:
                        self.motor.turn_left()

                else:
                    print("Path Clear → Forward")
                    self.motor.move_forward()

                time.sleep(0.05)  # reduce CPU load

        except KeyboardInterrupt:
            self.motor.cleanup()
            self.camera.release()


# MAIN ENTRY POINT

if __name__ == "__main__":

    motor = MotorController(
    "/dev/serial/by-id/usb-Arduino_UNO_WiFi_R4_CMSIS-DAP_F412FA6FED58-if01"
)

    camera = Camera()
    vision = VisionSystem()

    robot = RobotController(motor, camera, vision)
    robot.run()
