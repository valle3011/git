import socket
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


# CAMERA CLASS
# If you later switch to Picamera2, replace this class.
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
            "ax": accel["x"],
            "ay": accel["y"],
            "az": accel["z"],
            "gx": gyro["x"],
            "gy": gyro["y"],
            "gz": gyro["z"]
        }


class LidarReceiver:
    def __init__(self, listen_ip="0.0.0.0", port=5005):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((listen_ip, port))
        self.sock.setblocking(False)

        self.front = 9999
        self.left = 9999
        self.right = 9999
        self.last_update = 0.0

    def update(self):
        try:
            data, _ = self.sock.recvfrom(1024)
            msg = data.decode().strip()

            values = {}
            for part in msg.split(";"):
                if "=" in part:
                    k, v = part.split("=", 1)
                    values[k] = int(v)

            self.front = values.get("F", self.front)
            self.left = values.get("L", self.left)
            self.right = values.get("R", self.right)
            self.last_update = time.time()

        except BlockingIOError:
            pass
        except Exception as e:
            print("LiDAR UDP Fehler:", e)

        return self.front, self.left, self.right

    def is_stale(self, timeout=0.5):
        return (time.time() - self.last_update) > timeout


class HailoDetector:
    def __init__(self, hef_path="/usr/share/hailo-models/yolov8s_h8l.hef"):
        self.hef_path = hef_path

        # Placeholder setup
        # This only stores the path for now.
        # Replace this later with real Hailo inference code.
        self.device = None
        self.network_group = None

        try:
            self.device = hailo_platform.Device()
            self.network_group = self.device.configure(hef_path)
            print(f"Hailo loaded: {hef_path}")
        except Exception as e:
            print("Hailo init warning:", e)
            print("Running with placeholder detector (no real boxes yet).")

    def detect(self, frame):
        # TODO:
        # 1. preprocess frame
        # 2. run Hailo inference
        # 3. decode boxes
        # 4. return [(x1, y1, x2, y2), ...]
        return []


class VisionSystem:
    def __init__(self):
        self.detector = HailoDetector("/usr/share/hailo-models/yolov8s_h8l.hef")
        self.frame_width = 640

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
        return red_pixels > 2000

    def detect_obstacles(self, frame):
        results = self.detector.detect(frame)

        obstacles = []
        for (x1, y1, x2, y2) in results:
            area = (x2 - x1) * (y2 - y1)
            cx = (x1 + x2) // 2
            obstacles.append((cx, area))

        return obstacles


class RobotController:
    def __init__(self, motor, camera, vision, imu, lidar):
        self.motor = motor
        self.camera = camera
        self.vision = vision
        self.imu = imu
        self.lidar = lidar

        self.FRAME_LEFT = 640 * 0.4
        self.FRAME_RIGHT = 640 * 0.6
        self.AREA_THRESHOLD = 25000

        self.STOP_MM = 300
        self.SIDE_FREE_MM = 700

    def run(self):
        try:
            while True:
                frame = self.camera.get_frame()
                if frame is None:
                    continue

                imu_data = self.imu.get_data()
                front_dist, left_dist, right_dist = self.lidar.update()

                print(f"LiDAR F={front_dist} L={left_dist} R={right_dist}")

                # Optional failsafe if LiDAR data stops arriving
                if self.lidar.is_stale(timeout=1.0):
                    print("LiDAR timeout → STOP")
                    self.motor.stop()
                    time.sleep(0.05)
                    continue

                # IMU priority
                if abs(imu_data["ax"]) > 8 or abs(imu_data["ay"]) > 8:
                    print("Tilt/Collision detected → STOP")
                    self.motor.stop()
                    continue

                # LiDAR front stop priority
                if front_dist < self.STOP_MM:
                    print("LiDAR Front obstacle → STOP")
                    self.motor.stop()
                    continue

                # Red light priority
                if self.vision.detect_red_light(frame):
                    print("Red Light Detected → STOP")
                    self.motor.stop()
                    continue

                # Camera/Hailo obstacles
                obstacles = self.vision.detect_obstacles(frame)

                if obstacles:
                    cx, area = max(obstacles, key=lambda x: x[1])

                    if area > self.AREA_THRESHOLD:
                        print("Large obstacle → STOP")
                        self.motor.stop()

                    elif cx < self.FRAME_LEFT:
                        if right_dist > self.SIDE_FREE_MM:
                            print("Obstacle left → turn right")
                            self.motor.turn_right()
                        else:
                            print("Obstacle left but right blocked → STOP")
                            self.motor.stop()

                    elif cx > self.FRAME_RIGHT:
                        if left_dist > self.SIDE_FREE_MM:
                            print("Obstacle right → turn left")
                            self.motor.turn_left()
                        else:
                            print("Obstacle right but left blocked → STOP")
                            self.motor.stop()

                    else:
                        print("Obstacle center → STOP")
                        self.motor.stop()

                else:
                    if front_dist >= self.STOP_MM:
                        print("Path Clear → Forward")
                        self.motor.move_forward()
                    else:
                        print("LiDAR says blocked → STOP")
                        self.motor.stop()

                time.sleep(0.05)

        except KeyboardInterrupt:
            print("Programm beendet")
        finally:
            self.motor.cleanup()
            self.camera.release()


if __name__ == "__main__":
    motor = MotorController(
        "/dev/serial/by-id/usb-Arduino_UNO_WiFi_R4_CMSIS-DAP_F412FA6FED58-if01"
    )

    camera = Camera()
    vision = VisionSystem()
    imu = IMU()
    lidar = LidarReceiver(port=5005)

    robot = RobotController(motor, camera, vision, imu, lidar)
    robot.run()