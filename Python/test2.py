import socket
import time

TARGET_IP = "172.20.10.3"   # IP von Decision-Pi
PORT = 5005

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

distance = 1000

while True:
    msg = f"DIST {distance}"
    sock.sendto(msg.encode(), (TARGET_IP, PORT))
    print("Gesendet:", msg)

    distance -= 100
    if distance < 100:
        distance = 1000

    time.sleep(1)
