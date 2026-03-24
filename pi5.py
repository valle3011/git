from ultralytics import YOLO
import serial
import time
import cv2
import numpy as np
from mpu6050 import mpu6050
import hailo_platform

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


class IMU:
    def __init__(self, address=0x68):
        self.sensor = mpu6050(address)

    def get_data(self):
        accel = self.sensor.get_accel_data()
        gyro = self.sensor.get_gyro_data()

        return {
            "ax": accel['x'],
            "ay": accel['y'],
            "az": accel['z'],
            "gx": gyro['x'],
            "gy": gyro['y'],
            "gz": gyro['z']
        }
class HailoDetector:
    def __init__(self, hef_path):
        self.device = hailo_platform.Device()
        self.network_group = self.device.configure(hef_path)

    def detect(self, frame):
        # preprocess frame here
        # run inference using hailo API
        # return boxes like before
        return []

class VisionSystem:

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
  
    def __init__(self):
        self.detector = HailoDetector("yolov8n.hef")
        self.frame_width = 640

    def detect_obstacles(self, frame):
        results = self.detector.detect(frame)

        obstacles = []
        for (x1, y1, x2, y2) in results:
            area = (x2 - x1) * (y2 - y1)
            cx = (x1 + x2) // 2
            obstacles.append((cx, area))

        return obstacles



# DECISION SYSTEM

class RobotController:
    def __init__(self, motor, camera, vision, imu):
        self.motor = motor
        self.camera = camera
        self.vision = vision
        self.imu = imu

        self.FRAME_LEFT = 640 * 0.4
        self.FRAME_RIGHT = 640 * 0.6
        self.AREA_THRESHOLD = 25000

    def run(self):
        try:
            while True:
                frame = self.camera.get_frame()
                if frame is None:
                    continue

                imu_data = self.imu.get_data()

            # Example: detect tilt / collision
                if abs(imu_data["ax"]) > 8 or abs(imu_data["ay"]) > 8:
                    print("Tilt/Collision detected → STOP")
                    self.motor.stop()
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
    imu = IMU()

    robot = RobotController(motor, camera, vision, imu)
    robot.run()
