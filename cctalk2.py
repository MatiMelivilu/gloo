import serial
import time

# Configuracion del puerto serie
PORT = '/dev/ttyUSB0'
BAUDRATE = 9600

# Direcciones CCTalk
DEVICE_ADDR = 2   # Direccion del monedero
HOST_ADDR = 1     # Direccion del host (Raspberry Pi)

CNT = 0
def checksum(msg):
    return (256 - sum(msg)) % 256

def build_packet(cmd, data=[]):
    packet = [DEVICE_ADDR, len(data), HOST_ADDR, cmd] + data
    packet.append(checksum(packet))
    return bytes(packet)

def send_command(ser, cmd, data=[], response_size=16):
    ser.reset_input_buffer()
    ser.write(build_packet(cmd, data))
    time.sleep(0.3)
    return ser.read(response_size)

def reset_device(ser):
    print("Reiniciando dispositivo...")
    response = send_command(ser, 1)
    print("Respuesta reset:", list(response))

def enable_monedero(ser):
    print("Habilitando monedero...")
    print("ID:", list(send_command(ser, 2)))
    print("Status:", list(send_command(ser, 245)))
    print("Producto:", list(send_command(ser, 230)))

    # Habilitar todos los canales
    response = send_command(ser, 231, [0xFF, 0xFF])
    print("Enable canales:", list(response))

    # Confirmar estado de canales
    response = send_command(ser, 248)
    print("Estado de canales:", list(response))

def read_raw_bytes_from_monedero(ser):
    global CNT

    # Solicita eventos
    send_command(ser, 254)
    time.sleep(0.1)

    ser.write(build_packet(229))
    time.sleep(0.4)
    raw = ser.read(ser.in_waiting or 16)

    if not raw:
        print("Sin respuesta del monedero.")
        return

    data = list(raw)
    print("Datos crudos:", data)

    if len(data) >= 15:
        monedaInsertada = data[9]
        deteccionMoneda = data[10]
        if CNT != monedaInsertada:
            CNT = monedaInsertada
            print("Moneda detectada")
            print("Codigo de canal:", deteccionMoneda)
            if deteccionMoneda == 0:
                print('Moneda no reconocida')
            elif deteccionMoneda == 1:
                print('$10 pesos')
            elif deteccionMoneda == 2:
                print('$50 pesos')    
            elif deteccionMoneda == 3:
                print('$100 pesos')
            elif deteccionMoneda == 4:
                print('$100 pesos') 
            elif deteccionMoneda == 5:
                print('$500 pesos') 
            else:
                print('Evento raro o canal desconocido')

def main():
    print("Iniciando comunicacion con el monedero en", PORT)
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=1) as ser:
            reset_device(ser)
            enable_monedero(ser)
            print("Listo. Esperando monedas...\n")
            while True:
                read_raw_bytes_from_monedero(ser)
                time.sleep(0.05)
    except serial.SerialException as e:
        print("Error al abrir el puerto serie:", e)
    except KeyboardInterrupt:
        print("\nPrograma detenido por el usuario.")

if __name__ == "__main__":
    main()
