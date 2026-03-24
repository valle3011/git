#!/usr/bin/env python3
import serial
import struct
import time

# ----- LD06 Einstellungen -----
PORT = "/dev/ttyAMA0"
BAUD = 230400

FRAME_LEN = 46
HEADER1 = 0x54
HEADER2 = 0x2C

# ----- Logik -----
FRONT_DEG = 10
STOP_MM = 300
SLOW_MM = 600

lidar = serial.Serial(PORT, BAUD, timeout=0.1)

buf = bytearray()
front_mm = 9999


def in_front(angle):
    return angle <= FRONT_DEG or angle >= 360 - FRONT_DEG


def lidar_front_min_mm():
    global buf
    front_min = None

    data = lidar.read(4096)
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

        sa = start_angle
        ea = end_angle

        if ea < sa:
            ea += 360

        step = (ea - sa) / 11

        for i in range(12):

            offset = 6 + i * 3
            dist = struct.unpack_from("<H", frame, offset)[0]
            angle = (sa + step * i) % 360

            if dist > 0 and in_front(angle):

                if front_min is None or dist < front_min:
                    front_min = dist

    return front_min


while True:

    f = lidar_front_min_mm()

    if f is not None:
        front_mm = f

    # Entscheidung
    if front_mm < STOP_MM:
        decision = "STOP"
    elif front_mm < SLOW_MM:
        decision = "SLOW"
    else:
        decision = "GO"

    print(f"Front distance: {front_mm} mm   ->   {decision}")

    time.sleep(0.05)
