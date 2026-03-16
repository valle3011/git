import smbus
import time

bus = smbus.SMBus(1)
addr = 0x68

bus.write_byte_data(addr, 0x6B, 0)

def read_word(reg):
    high = bus.read_byte_data(addr, reg)
    low = bus.read_byte_data(addr, reg+1)
    value = (high << 8) + low
    if value >= 0x8000:
        value = -((65535 - value) + 1)
    return value

while True:
    gyro_x = read_word(0x43)
    gyro_y = read_word(0x45)
    gyro_z = read_word(0x47)

    print(gyro_x, gyro_y, gyro_z)
    time.sleep(1)