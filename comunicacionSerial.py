import serial
import time

PORT = '/dev/ttyUSB0'   # Ajusta el puerto si es necesario
BAUDRATE = 9600
TIMEOUT = 1

try:
    ser = serial.Serial(PORT, BAUDRATE, timeout=TIMEOUT)
    print(f"Puerto serial {PORT} abierto exitosamente a {BAUDRATE} baudios.")
    time.sleep(2)

    # Enviar mensaje inicial (opcional)
    message_to_send = "Hola desde Python!\n"
    ser.write(message_to_send.encode('utf-8'))
    print(f"Enviado: '{message_to_send.strip()}'")

    # Leer continuamente
    print("Esperando datos... (Ctrl+C para salir)")
    while True:
        received_data = ser.readline()
        if received_data:
            print(f"Recibido: '{received_data.decode('utf-8', errors='ignore').strip()}'")
        else:
            # Si deseas ver cuando no hay datos, puedes descomentar esto:
            # print("Sin datos...")
            pass

except serial.SerialException as e:
    print(f"Error de puerto serial: {e}")
except KeyboardInterrupt:
    print("\nLectura interrumpida por el usuario.")
except Exception as e:
    print(f"Ocurrio un error inesperado: {e}")
finally:
    if 'ser' in locals() and ser.is_open:
        ser.close()
        print(f"Puerto serial {PORT} cerrado.")
