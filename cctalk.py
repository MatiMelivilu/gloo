import serial
import time

# Configuracion del puerto y direcciones
PORT = '/dev/ttyUSB0'  # Cambia esto si tu puerto es diferente
BAUDRATE = 9600
DEVICE_ADDR = 40       # Direccion del BV20 (por defecto)
HOST_ADDR = 1

def checksum(msg):
    return (256 - sum(msg)) % 256

def build_packet(cmd, data=[]):
    packet = [DEVICE_ADDR, len(data), HOST_ADDR, cmd] + data
    packet.append(checksum(packet))
    return bytes(packet)

def send_command(ser, cmd, data=[], response_size=64, label=None):
    ser.reset_input_buffer()
    ser.write(build_packet(cmd, data))
    time.sleep(0.05)
    response = ser.read(response_size)
    if label:
        print(f"{label}: {list(response)}")
    return response

def menu():
    print("\n--- MENU BV20 - ccTalk ---")
    print("1 - Test de conexion (SIMPLE_POLL)")
    print("2 - Habilitar billetero (SET_INHIBITS)")
    print("3 - Leer eventos (READ_BUFFERED_BILL_EV)")
    print("4 - Leer firmware (REQUEST_SOFTWARE_REVISION)")
    print("5 - Leer numero de serie (SERIAL_NUMBER)")
    print("6 - Leer ID de canal")
    print("7 - Reiniciar BV20")
    print("0 - Salir")

def main():
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=1) as ser:
            while True:
                menu()
                choice = input("Selecciona una opcion: ")

                if choice == "1":
                    send_command(ser, 254, label="SIMPLE_POLL")
                elif choice == "2":
                    send_command(ser, 231, [255, 255], label="SET_INHIBITS")
                elif choice == "3":
                    send_command(ser, 159, label="READ_BUFFERED_BILL_EV", response_size=32)
                elif choice == "4":
                    send_command(ser, 241, label="FIRMWARE")
                elif choice == "5":
                    send_command(ser, 242, label="SERIAL_NUMBER")
                elif choice == "6":
                    canal = input("Canal a consultar (ej: 1): ")
                    try:
                        canal = int(canal)
                        send_command(ser, 157, [canal], label=f"REQUEST_BILL_ID canal {canal}")
                    except ValueError:
                        print("Canal invalido.")
                elif choice == "7":
                    send_command(ser, 1, label="RESET_DEVICE")
                elif choice == "0":
                    print("Saliendo...")
                    break
                else:
                    print("Opcion invalida.")
                time.sleep(0.3)
    except serial.SerialException as e:
        print("Error al abrir el puerto serial:", e)
    except KeyboardInterrupt:
        print("\nPrograma detenido por el usuario.")

if __name__ == "__main__":
    main()
