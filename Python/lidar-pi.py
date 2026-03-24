import socket
import time
import serial
import struct

UDP_IP = "172.20.10.3"   # IP vom Decision Pi
UDP_PORT = 5005

LIDAR_PORT = "/dev/ttyAMA10"
BAUD = 230400

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

lidar = serial.Serial(LIDAR_PORT, BAUD, timeout=0.1)

FRAME_LEN = 46
HEADER1 = 0x54
HEADER2 = 0x2C

buf = bytearray()

def in_front(angle):
    return angle < 30 or angle > 330

def get_front_distance():

    global buf
    front_min = None

    data = lidar.read(1024)
    buf.extend(data)

    while len(buf) >= FRAME_LEN:

        if buf[0] != HEADER1 or buf[1] != HEADER2:
            del buf[0]
            continue

        frame = bytes(buf[:FRAME_LEN])
        del buf[:FRAME_LEN]

        start_angle = struct.unpack_from("<H", frame, 4)[0] / 100
        end_angle = struct.unpack_from("<H", frame, 42)[0] / 100

        if end_angle < start_angle:
            end_angle += 360

        step = (end_angle - start_angle) / 11

        for i in range(12):

            offset = 6 + i * 3
            dist = struct.unpack_from("<H", frame, offset)[0]
            angle = (start_angle + step * i) % 360

            if dist > 0 and in_front(angle):

                if front_min is None or dist < front_min:
                    front_min = dist

    return front_min


while True:

    d = get_front_distance()

    if d is None:
        d = 9999

    msg = f"LIDAR {d}"
    sock.sendto(msg.encode(), (UDP_IP, UDP_PORT))

    time.sleep(0.05)
