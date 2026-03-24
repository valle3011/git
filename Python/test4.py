import serial

ser = serial.Serial("/dev/ttyAMA0", 230400, timeout=1)

print("Starte LiDAR Test...")

while True:
    data = ser.read(50)

    if data:
        print(data)
