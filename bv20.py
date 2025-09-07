import serial
import time

def crc16_ccitt(data: bytes, crc: int = 0xFFFF) -> int:
    for byte in data:
        crc ^= byte << 8
        for _ in range(8):
            if crc & 0x8000:
                crc = (crc << 1) ^ 0x1021
            else:
                crc <<= 1
            crc &= 0xFFFF
    return crc

def build_ssp_packet(address: int, command: int, data: bytes = b'') -> bytes:
    length = 1 + len(data)
    packet = bytearray()
    packet.append(0x7F)
    packet.append(address)
    packet.append(length)
    packet.append(command)
    packet.extend(data)
    crc = crc16_ccitt(packet[1:])
    packet.append(crc & 0xFF)
    packet.append((crc >> 8) & 0xFF)
    return bytes(packet)

# Configura la UART del BV20 (9600 bps, 8N1)
ser = serial.Serial("/dev/ttyUSB0", 9600, timeout=1)
time.sleep(1)

# Construir y enviar el paquete Request Setup
packet = build_ssp_packet(address=0x01, command=0x05)
ser.write(packet)
print("Enviado:", packet.hex())

# Leer respuesta
response = ser.read(64)
print("Respuesta:", response.hex())

ser.close()
