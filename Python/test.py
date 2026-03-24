import serial
import time

PORT = "/dev/ttyAMA10"
BAUD = 230400

lidar = serial.Serial(PORT, BAUD, timeout=0.1)

while True:
    data = lidar.read(100)

    if data:
        print(len(data), data[:10])
