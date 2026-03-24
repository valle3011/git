import socket
import time
import serial
import struct

TARGET_IP = "172.20.10.3"   # IP von der anderen Pi
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

def in_left(angle):
    return 60 <= angle <= 120

def in_right(angle):
    return 240 <= angle <= 300

def get_distances():
    global buf

    front_min = None
    left_min = None
    right_min = None

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

            if dist <= 0:
                continue

            if in_front(angle):
                if front_min is None or dist < front_min:
                    front_min = dist

            if in_left(angle):
                if left_min is None or dist < left_min:
                    left_min = dist

            if in_right(angle):
                if right_min is None or dist < right_min:
                    right_min = dist

    return front_min, left_min, right_min

while True:
    f, l, r = get_distances()

    if f is None:
        f = 9999
    if l is None:
        l = 9999
    if r is None:
        r = 9999

    msg = f"F={f} L={l} R={r}"
    sock.sendto(msg.encode(), (TARGET_IP, PORT))
    print("Gesendet:", msg)

    time.sleep(0.05)
