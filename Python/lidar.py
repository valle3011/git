#!/usr/bin/env python3
import serial, struct, time, socket

# ----- LD06 -----
LIDAR_PORT = "/dev/ttyAMA10"
LIDAR_BAUD = 230400

# ----- Arduino -----
# meist /dev/ttyACM0 (UNO) oder /dev/ttyUSB0 (CH340)
ARDUINO_PORT = "/dev/ttyACM0"
ARDUINO_BAUD = 115200

# ----- UDP von Pi A -----
UDP_LISTEN_IP = "0.0.0.0"
UDP_LISTEN_PORT = 5005

# ----- LD06 Frame (typisch 47 Bytes, Header 0x54 0x2C) -----
FRAME_LEN = 47
HEADER1, HEADER2 = 0x54, 0x2C

# ----- Logik -----
FRONT_DEG = 10     # Frontsektor 350..360 und 0..10
STOP_MM = 300
SLOW_MM = 600      # optional
SEND_HZ = 20
CAM_TIMEOUT = 0.6  # wenn Kamera nichts sendet -> STOP (Safety)

lidar = serial.Serial(LIDAR_PORT, LIDAR_BAUD, timeout=0.05)
arduino = serial.Serial(ARDUINO_PORT, ARDUINO_BAUD, timeout=0.05)

udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp.bind((UDP_LISTEN_IP, UDP_LISTEN_PORT))
udp.setblocking(False)

buf = bytearray()

cam_state = "STOP"
last_cam_time = 0.0

def in_front(angle_deg: float) -> bool:
    return (angle_deg <= FRONT_DEG) or (angle_deg >= 360.0 - FRONT_DEG)

def read_cam_udp():
    global cam_state, last_cam_time
    for _ in range(10):
        try:
            data, _ = udp.recvfrom(1024)
        except BlockingIOError:
            return
        line = data.decode("ascii", errors="ignore").strip()
        if line.startswith("CAM="):
            val = line.split("=", 1)[1].strip()
            if val in ("GO", "STOP"):
                cam_state = val
                last_cam_time = time.time()

def lidar_front_min_mm():
    global buf
    front_min = None

    chunk = lidar.read(4096)
    if chunk:
        buf.extend(chunk)

    while len(buf) >= FRAME_LEN:
        if buf[0] != HEADER1 or buf[1] != HEADER2:
            del buf[0]
            continue

        frame = bytes(buf[:FRAME_LEN])
        del buf[:FRAME_LEN]

        start_angle = struct.unpack_from("<H", frame, 4)[0] / 100.0
        end_angle   = struct.unpack_from("<H", frame, 42)[0] / 100.0

        sa, ea = start_angle, end_angle
        if ea < sa:
            ea += 360.0
        step = (ea - sa) / 11.0

        for i in range(12):
            off = 6 + i * 3
            dist = struct.unpack_from("<H", frame, off)[0]  # mm
            angle = (sa + step * i) % 360.0

            if dist > 0 and in_front(angle):
                if front_min is None or dist < front_min:
                    front_min = dist

    return front_min

def fusion(front_mm: int, cam_state: str) -> tuple[str, str]:
    # Kamera Timeout -> STOP
    if time.time() - last_cam_time > CAM_TIMEOUT:
        return "STOP", "CAM_TIMEOUT"

    # LiDAR Notbremse
    if front_mm < STOP_MM:
        return "STOP", "LIDAR"

    # Kamera STOP
    if cam_state == "STOP":
        return "STOP", "CAM"

    # Optional: SLOW (wenn ihr wollt)
    if front_mm < SLOW_MM:
        return "SLOW", "LIDAR_SLOW"

    return "GO", "OK"

last_send = 0.0
last_cmd = None
front_mm = 9999

while True:
    read_cam_udp()

    f = lidar_front_min_mm()
    if f is not None:
        front_mm = f

    cmd, reason = fusion(front_mm, cam_state)

    now = time.time()
    if cmd != last_cmd or (now - last_send) >= 1.0 / SEND_HZ:
        # Arduino bekommt: CMD + F=Distanz
        arduino.write(f"CMD {cmd} F={front_mm} REASON={reason}\n".encode("ascii"))
        last_cmd = cmd
        last_send = now

    time.sleep(0.002)
