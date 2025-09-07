import serial
import time

def cctalk_checksum(message):
    # Checksum = 256 - sum(message[1:]) % 256
    return (256 - sum(message[1:])) % 256

def build_cctalk_command(destination, command, data=[]):
    length = len(data)
    message = [destination, length, 1, command] + data
    checksum = cctalk_checksum([0] + message)  # prepend 0 for source (host = 0)
    return bytes([0] + message + [checksum])   # Source is always 0 (host)

def parse_cctalk_response(response):
    if not response or len(response) < 5:
        return None
    length = response[1]
    expected_len = 5 + length  # header (5) + data
    if len(response) < expected_len:
        print("?? Respuesta incompleta:", list(response))
        return None
    data = response[4:4 + length]
    return data


class NRIMoner:
    def __init__(self, port="/dev/ttyUSB0", baudrate=9600):
        self.ser = serial.Serial(port, baudrate=baudrate, timeout=0.1)

    def send_command(self, dest, cmd, data=[]):
        packet = build_cctalk_command(dest, cmd, data)
        self.ser.write(packet)
        time.sleep(0.05)
        response = self.ser.read(32)
        return parse_cctalk_response(response)

    def identify_device(self):
        return self.send_command(2, 254)  # Command 254: Request Manufacturer ID

    def enable_moner(self):
        return self.send_command(2, 231, [0])  # Command 231: Modify inhibit status ? 0 = habilitado

    def read_buffered_credit(self):
        return self.send_command(2, 229)  # Command 229: Read buffered credit

    def close(self):
        self.ser.close()


import serial
ser = serial.Serial("/dev/ttyUSB0", baudrate=9600, timeout=0.2)

# Comando Identify (a direccin 2)
cmd = bytes([0, 2, 0, 1, 254, (256 - (2 + 0 + 1 + 254)) % 256])
ser.write(cmd)
resp = ser.read(30)
print("Respuesta:", list(resp))

