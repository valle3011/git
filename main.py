import socket
import serial
import time
from picamera2 import Picamera2
import cv2
import numpy as np
import glob
from mpu6050 import mpu6050


# =========================
# SETTINGS
# =========================

# Change this if you want a fixed port, for example "/dev/ttyACM0"
# If None, the code will try to auto-detect the Arduino.
ARDUINO_PORT = None

ARDUINO_BAUD = 115200

# LiDAR UDP
LIDAR_LISTEN_IP = "0.0.0.0"
LIDAR_PORT = 5005

# Hailo model path
HEF_PATH = "/usr/share/hailo-models/yolov8s_h8l.hef"

# Camera
CAMERA_INDEX = 0
CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480

# Thresholds
STOP_MM = 300
SIDE_FREE_MM = 700
AREA_THRESHOLD = 25000


# =========================
# DEBUG
# =========================

def debug(msg):
    print(f"[DEBUG] {msg}", flush=True)


# =========================
# HELPERS
# =========================

def find_arduino_port():
    # First try stable by-id names
    by_id = glob.glob("/dev/serial/by-id/*Arduino*") + glob.glob("/dev/serial/by-id/*arduino*")
    if by_id:
        return by_id[0]

    # Then try ttyACM
    acm = glob.glob("/dev/ttyACM*")
    if acm:
        return acm[0]

    # Then try ttyUSB
    usb = glob.glob("/dev/ttyUSB*")
    if usb:
        return usb[0]

    return None


# =========================
# MOTOR CONTROLLER
# =========================

class MotorController:
    def __init__(self, port=None, baud=115200):
        if port is None:
            port = find_arduino_port()

        if port is None:
            raise RuntimeError("No Arduino serial port found")

        self.port = port
        debug(f"Opening Arduino port: {self.port} @ {baud}")
        self.ser = serial.Serial(self.port, baud, timeout=1)
        time.sleep(5)   # Arduino reset delay
        debug("Arduino serial ready")

    def send(self, cmd):
        debug(f"Sending to Arduino: {cmd}")
        self.ser.write((cmd + "\n").encode())
        reply = self.ser.readline().decode(errors="ignore").strip()
        debug(f"Arduino reply: {reply}")

    def move_forward(self):
        self.send("FORWARD")

    def turn_left(self):
        self.send("LEFT")

    def turn_right(self):
        self.send("RIGHT")

    def stop(self):
        self.send("STOP")

    def cleanup(self):
        try:
            self.stop()
        except Exception as e:
            debug(f"Motor cleanup warning: {e}")
        try:
            self.ser.close()
        except Exception as e:
            debug(f"Serial close warning: {e}")


# =========================
# CAMERA
# =========================

class Camera:
    def __init__(self, width=640, height=480):
        debug("Initializing Picamera2...")
        self.picam2 = Picamera2()
        config = self.picam2.create_preview_configuration(
            main={"size": (width, height), "format": "RGB888"}
        )
        self.picam2.configure(config)
        self.picam2.start()
        time.sleep(2)
        debug("Picamera2 OK")

    def get_frame(self):
        frame = self.picam2.capture_array()
        if frame is None:
            return None
        return cv2.cvtColor(frame, cv2.COLOR_RGB2BGR)

    def release(self):
        self.picam2.stop()
        debug("Camera released")

# =========================
# IMU
# =========================

class IMU:
    def __init__(self, address=0x68):
        debug("Initializing IMU...")
        self.sensor = mpu6050(address)
        debug("IMU OK")

    def get_data(self):
        accel = self.sensor.get_accel_data()
        gyro = self.sensor.get_gyro_data()

        debug(f"IMU ax={accel['x']:.2f}, ay={accel['y']:.2f}, az={accel['z']:.2f}")

        return {
            "ax": accel["x"],
            "ay": accel["y"],
            "az": accel["z"],
            "gx": gyro["x"],
            "gy": gyro["y"],
            "gz": gyro["z"]
        }


# =========================
# LIDAR UDP RECEIVER
# =========================

class LidarReceiver:
    def __init__(self, listen_ip="0.0.0.0", port=5005):
        debug(f"Starting LiDAR receiver on {listen_ip}:{port}")
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.sock.bind((listen_ip, port))
        self.sock.setblocking(False)

        self.front = 9999
        self.left = 9999
        self.right = 9999
        self.last_update = time.time()

    def update(self):
        try:
            data, addr = self.sock.recvfrom(1024)
            msg = data.decode().strip()
            debug(f"LiDAR packet from {addr}: {msg}")

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
            debug(f"LiDAR UDP error: {e}")

        debug(f"LiDAR values: F={self.front} L={self.left} R={self.right}")
        return self.front, self.left, self.right

    def is_stale(self, timeout=1.0):
        stale = (time.time() - self.last_update) > timeout
        if stale:
            debug("LiDAR DATA TIMEOUT")
        return stale


# =========================
# HAILO PLACEHOLDER
# =========================

class HailoDetector:
    def __init__(self, hef_path=HEF_PATH):
        self.hef_path = hef_path

        try:
            with open(self.hef_path, "rb") as f:
                f.read(1)
            debug(f"Hailo HEF found: {self.hef_path}")
        except Exception as e:
            debug(f"Hailo HEF error: {e}")

        debug("Hailo detector currently running in placeholder mode")

    def detect(self, frame):
        # Placeholder:
        # Replace later with real Hailo inference.
        return []


# =========================
# VISION
# =========================

class VisionSystem:
    def __init__(self):
        debug("Initializing vision system...")
        self.detector = HailoDetector(HEF_PATH)
        self.frame_width = CAMERA_WIDTH
        debug("Vision system OK")

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
        debug(f"Red pixels: {red_pixels}")
        return red_pixels > 2000

    def detect_obstacles(self, frame):
        results = self.detector.detect(frame)

        obstacles = []
        for (x1, y1, x2, y2) in results:
            area = (x2 - x1) * (y2 - y1)
            cx = (x1 + x2) // 2
            obstacles.append((cx, area))

        debug(f"Obstacle count: {len(obstacles)}")
        return obstacles


# =========================
# ROBOT CONTROLLER
# =========================

class RobotController:
    def __init__(self, motor, camera, vision, imu, lidar):
        self.motor = motor
        self.camera = camera
        self.vision = vision
        self.imu = imu
        self.lidar = lidar

        self.FRAME_LEFT = CAMERA_WIDTH * 0.4
        self.FRAME_RIGHT = CAMERA_WIDTH * 0.6
        self.AREA_THRESHOLD = AREA_THRESHOLD

        self.STOP_MM = STOP_MM
        self.SIDE_FREE_MM = SIDE_FREE_MM

    def run(self):
        debug("Robot loop started")
        try:
            while True:
                debug("=== LOOP START ===")

                frame = self.camera.get_frame()
                if frame is None:
                    debug("Camera frame is None")
                    time.sleep(0.05)
                    continue

                imu_data = self.imu.get_data()
                front_dist, left_dist, right_dist = self.lidar.update()

                # LiDAR timeout failsafe
                if self.lidar.is_stale(timeout=1.0):
                    debug("LiDAR timeout -> STOP")
                    self.motor.stop()
                    time.sleep(0.05)
                    continue

                # IMU priority
                if abs(imu_data["ax"]) > 8 or abs(imu_data["ay"]) > 8:
                    debug("Tilt/Collision detected -> STOP")
                    self.motor.stop()
                    time.sleep(0.05)
                    continue

                # LiDAR front stop priority
                if front_dist < self.STOP_MM:
                    debug("LiDAR front obstacle -> STOP")
                    self.motor.stop()
                    time.sleep(0.05)
                    continue

                # Red light priority
                if self.vision.detect_red_light(frame):
                    debug("Red light detected -> STOP")
                    self.motor.stop()
                    time.sleep(0.05)
                    continue

                # Camera/Hailo obstacles
                obstacles = self.vision.detect_obstacles(frame)

                if obstacles:
                    cx, area = max(obstacles, key=lambda x: x[1])
                    debug(f"Biggest obstacle: cx={cx}, area={area}")

                    if area > self.AREA_THRESHOLD:
                        debug("Large obstacle -> STOP")
                        self.motor.stop()

                    elif cx < self.FRAME_LEFT:
                        if right_dist > self.SIDE_FREE_MM:
                            debug("Obstacle left -> turn right")
                            self.motor.turn_right()
                        else:
                            debug("Obstacle left but right blocked -> STOP")
                            self.motor.stop()

                    elif cx > self.FRAME_RIGHT:
                        if left_dist > self.SIDE_FREE_MM:
                            debug("Obstacle right -> turn left")
                            self.motor.turn_left()
                        else:
                            debug("Obstacle right but left blocked -> STOP")
                            self.motor.stop()

                    else:
                        debug("Obstacle center -> STOP")
                        self.motor.stop()

                else:
                    if front_dist >= self.STOP_MM:
                        debug("Path clear -> FORWARD")
                        self.motor.move_forward()
                    else:
                        debug("LiDAR says blocked -> STOP")
                        self.motor.stop()

                time.sleep(0.05)

        except KeyboardInterrupt:
            debug("Program stopped by user")
        finally:
            debug("Cleaning up...")
            self.motor.cleanup()
            self.camera.release()


# =========================
# MAIN
# =========================

if __name__ == "__main__":
    debug("PROGRAM STARTED")

    motor = MotorController(ARDUINO_PORT, ARDUINO_BAUD)
    camera = Camera()
    vision = VisionSystem()
    imu = IMU()
    lidar = LidarReceiver(LIDAR_LISTEN_IP, LIDAR_PORT)

    robot = RobotController(motor, camera, vision, imu, lidar)
    robot.run()