import socket
import time
import serial
import struct

TARGET_IP = "172.20.10.3"   # IP von Decision-Pi
PORT = 5005

LIDAR_PORT = "/dev/ttyAMA0"
LIDAR_BAUD = 230400

FRAME_LEN = 46
HEADER1 = 0x54
HEADER2 = 0x2C

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
lidar = serial.Serial(LIDAR_PORT, LIDAR_BAUD, timeout=0.1)

buf = bytearray()

def in_front(angle):
    return angle <= 30 or angle >= 330

def get_front_distance():
    global buf
    front_min = None

    data = lidar.read(1024)
    if data:
        buf.extend(data)

    while len(buf) >= FRAME_LEN:
        if buf[0] != HEADER1 or buf[1] != HEADER2:
            del buf[0]
            continue

        frame = bytes(buf[:FRAME_LEN])
        del buf[:FRAME_LEN]

        start_angle = struct.unpack_from("<H", frame, 4)[0] / 100.0
        end_angle = struct.unpack_from("<H", frame, 42)[0] / 100.0

        if end_angle < start_angle:
            end_angle += 360.0

        step = (end_angle - start_angle) / 11.0

        for i in range(12):
            offset = 6 + i * 3
            dist = struct.unpack_from("<H", frame, offset)[0]
            angle = (start_angle + step * i) % 360.0

            if dist > 0 and in_front(angle):
                if front_min is None or dist < front_min:
                    front_min = dist

    return front_min

while True:
    d = get_front_distance()
    if d is None:
        d = 9999

    msg = f"DIST {d}"
    sock.sendto(msg.encode(), (TARGET_IP, PORT))
    print("Gesendet:", msg)

    time.sleep(0.05)
