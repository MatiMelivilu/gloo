import serial
import time

# --- Configuracion del Puerto Serie ---
SERIAL_PORT = '/dev/ttyUSB0'
BAUD_RATE = 9600  # O la velocidad de baudios configurada para tu validador
TIMEOUT = 0.1     # Tiempo de espera para la lectura del puerto serie

# --- Direcciones cctalk ---
HOST_ADDRESS = 0x01  # Direccion del host (PC)
VALIDATOR_ADDRESS = 0x28  # CORREGIDO: Direccion del validador (basado en la respuesta anterior)

# --- Comandos cctalk (Headers) ---
SIMPLE_POLL = 0xFE
READ_BILL_EVENTS = 0xF5
RESET_DEVICE = 0x01 # Resetear el contador de eventos del validador

# --- Funciones de Utilidad cctalk ---

def calculate_checksum(data):
    """Calcula el checksum cctalk para un paquete de datos."""
    checksum = sum(data)
    return (256 - (checksum % 256)) % 256

def create_cctalk_packet(destination, data_length, source, header, data_bytes=None):
    """Crea un paquete cctalk completo."""
    if data_bytes is None:
        data_bytes = []

    packet_without_checksum = [
        destination,
        data_length,
        source,
        header
    ] + data_bytes

    checksum = calculate_checksum(packet_without_checksum)
    return bytearray(packet_without_checksum + [checksum])

def parse_cctalk_response(response_bytes):
    """Parsea una respuesta cctalk y retorna un diccionario."""
    if not response_bytes:
        return None

    # Ajustado: la respuesta minima de cctalk (destino, longitud_datos, fuente, header, checksum) es de 5 bytes.
    if len(response_bytes) < 5:
        print(f"Respuesta cctalk demasiado corta. Bytes recibidos: {response_bytes.hex().upper()}")
        return None

    destination = response_bytes[0]
    data_length = response_bytes[1]
    source = response_bytes[2]
    header = response_bytes[3]

    # Asegurarse de que el paquete tiene suficientes bytes para el data_length reportado
    expected_length = 5 + data_length # Dest + Len + Source + Header + Checksum + Data
    if len(response_bytes) < expected_length:
        print(f"Respuesta cctalk incompleta. Esperado: {expected_length} bytes, Recibido: {len(response_bytes)} bytes.")
        return None

    received_data = response_bytes[4 : 4 + data_length] # Extraer solo los bytes de datos
    received_checksum = response_bytes[4 + data_length] # El checksum esta despues de los datos

    # Verificar el checksum de la respuesta
    calculated_checksum = calculate_checksum(response_bytes[0 : 4 + data_length]) # Sumar hasta antes del checksum recibido
    if calculated_checksum != received_checksum:
        print(f"Error de checksum: Calculado={calculated_checksum:02X}, Recibido={received_checksum:02X}")
        return None

    return {
        "destination": destination,
        "data_length": data_length,
        "source": source,
        "header": header,
        "data": received_data,
        "raw_bytes": response_bytes
    }

def print_packet_info(packet, name="Packet"):
    """Imprime informacion legible de un paquete."""
    print(f"{name}: {packet.hex().upper()}")
    print(f"  Destination: {packet[0]:02X}")
    print(f"  Data Length: {packet[1]:02X}")
    print(f"  Source:      {packet[2]:02X}")
    print(f"  Header:      {packet[3]:02X}")
    # Solo imprime Data si data_length es mayor que 0
    if len(packet) > 5: # Si hay mas de 5 bytes, significa que hay datos
        # Calculamos el final de los datos basados en el data_length del paquete recibido
        data_end_index = 4 + packet[1]
        if data_end_index > 4: # Si hay bytes de datos
            print(f"  Data:        {' '.join([f'{b:02X}' for b in packet[4:data_end_index]])}")
    print(f"  Checksum:    {packet[-1]:02X}")

# --- Conexion al Puerto Serie ---
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=TIMEOUT)
    print(f"Conectado a {SERIAL_PORT} a {BAUD_RATE} baudios.")
except serial.SerialException as e:
    print(f"Error al abrir el puerto serial: {e}")
    exit()

# --- Bucle Principal para Comunicacion ---
try:
    # 1. Resetear el contador de eventos del validador (opcional, pero recomendado al inicio)
    print("\n--- Enviando comando RESET_DEVICE ---")
    reset_command = create_cctalk_packet(VALIDATOR_ADDRESS, 0x00, HOST_ADDRESS, RESET_DEVICE)
    print_packet_info(reset_command, "Reset Command")
    ser.write(reset_command)
    time.sleep(0.1) # Pequena pausa para que el validador procese
    response_bytes = ser.read_all()
    if response_bytes:
        parsed_response = parse_cctalk_response(response_bytes)
        if parsed_response:
            print_packet_info(parsed_response["raw_bytes"], "Reset Response")
            # Un header de 0x00 (ACK) es la respuesta esperada para el reset exitoso.
            # Sin embargo, tu validador esta respondiendo con el mismo comando, 0x01.
            # Consideramos esto un ACK si el header es 0x00, o si es un eco del comando (0x01) con data_length 0.
            if parsed_response["header"] == 0x00 or \
               (parsed_response["header"] == RESET_DEVICE and parsed_response["data_length"] == 0x00):
                print("Validador reseteado con exito (ACK o eco de comando recibido).")
            else:
                print(f"Validador respondio al reset con Header inesperado: {parsed_response['header']:02X}")
        else:
            print("No se pudo parsear la respuesta del reset.")
    else:
        print("No se recibio respuesta al comando RESET_DEVICE.")


    while True:
        # 2. Enviar Simple Poll para verificar la conexion
        print("\n--- Enviando comando SIMPLE_POLL ---")
        poll_command = create_cctalk_packet(VALIDATOR_ADDRESS, 0x00, HOST_ADDRESS, SIMPLE_POLL)
        print_packet_info(poll_command, "Poll Command")
        ser.write(poll_command)

        # Esperar y leer la respuesta
        time.sleep(0.1) # Pequena pausa
        response_bytes = ser.read_all() # Lee todo lo que este en el buffer

        if response_bytes:
            parsed_response = parse_cctalk_response(response_bytes)
            if parsed_response:
                print_packet_info(parsed_response["raw_bytes"], "Poll Response")
                # El Simple Poll deberia devolver un ACK (0x00) si todo esta bien.
                # Tu validador parece estar haciendo eco del comando (0xFE) con data_length 0.
                if parsed_response["header"] == 0x00 or \
                   (parsed_response["header"] == SIMPLE_POLL and parsed_response["data_length"] == 0x00):
                    print("Validador responde al Simple Poll (ACK o eco de comando).")
                else:
                    print(f"Validador respondio con Header inesperado: {parsed_response['header']:02X}")
            else:
                print("No se pudo parsear la respuesta del Simple Poll.")
        else:
            print("No se recibio respuesta al Simple Poll. Verifique la conexion o la direccion.")

        # 3. Leer Eventos del Validador de Billetes
        print("\n--- Enviando comando READ_BILL_EVENTS ---")
        read_events_command = create_cctalk_packet(VALIDATOR_ADDRESS, 0x00, HOST_ADDRESS, READ_BILL_EVENTS)
        print_packet_info(read_events_command, "Read Bill Events Command")
        ser.write(read_events_command)

        # Esperar y leer la respuesta
        time.sleep(0.1)
        response_bytes = ser.read_all()

        if response_bytes:
            parsed_response = parse_cctalk_response(response_bytes)
            if parsed_response:
                print_packet_info(parsed_response["raw_bytes"], "Read Bill Events Response")

                # El header de la respuesta a READ_BILL_EVENTS debe ser READ_BILL_EVENTS (0xF5)
                # Tu validador esta haciendo eco del comando con data_length 0.
                if parsed_response["header"] == READ_BILL_EVENTS:
                    if parsed_response["data_length"] > 0: # <-- Importante: Verificar si hay datos antes de acceder
                        event_counter = parsed_response["data"][0] # Primer byte es el contador
                        events_data = parsed_response["data"][1:] # Resto son los eventos

                        print(f"Contador de eventos del validador: {event_counter}")

                        num_events = len(events_data) // 2 # Asumiendo 2 bytes por evento
                        if num_events > 0:
                            for i in range(num_events):
                                event_code = events_data[i * 2]
                                bill_number = events_data[i * 2 + 1]
                                print(f"  Evento {i+1}: Codigo={event_code:02X}, Billete/Numero={bill_number:02X}")
                                # Aqui puedes agregar logica para interpretar los codigos de evento y numeros de billete
                                # segun la documentacion de tu validador.
                        else:
                            print("No hay eventos de billetes reportados en la respuesta (datos de evento vacios).")
                    else:
                        print("La respuesta a READ_BILL_EVENTS no contiene datos (Data Length es 0).")
                        print("Esto puede indicar que no hay eventos pendientes o un comportamiento inusual del validador.")
                else:
                    print(f"Header inesperado en la respuesta de eventos: {parsed_response['header']:02X}")
            else:
                print("No se pudo parsear la respuesta de lectura de eventos.")
        else:
            print("No se recibio respuesta al comando READ_BILL_EVENTS.")

        time.sleep(1) # Esperar un segundo antes de la siguiente iteracion

except KeyboardInterrupt:
    print("\nPrograma terminado por el usuario.")
except Exception as e:
    print(f"Ocurrio un error: {e}")
finally:
    if ser.is_open:
        ser.close()
        print("Puerto serial cerrado.")
