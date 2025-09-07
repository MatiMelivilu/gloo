from datetime import date
from pdf417gen import encode
import os
import subprocess # Importar el modulo subprocess para ejecutar comandos del sistema

# --- Configuracion de la impresora ---
# Define el ancho maximo de caracteres por linea para tu impresora termica.
# Para papel de 57.5mm, un valor comun es entre 32 y 42 caracteres para fuentes estandar/condensadas.
# Si el texto se corta o se envuelve de forma inesperada, ajusta este valor.
MAX_CHARS_PER_LINE = 42

# Funcion para convertir los codigos PDF417 a una representacion ASCII
def render_pdf417_ascii(codes):
    """
    Convierte los codigos PDF417 generados por pdf417gen.encode()
    en una representacion ASCII para impresion en termica.
    """
    output = []
    # La funcion encode de pdf417gen devuelve directamente la matriz.
    for row in codes:
        # Usamos '?' (bloque completo) para representar los modulos negros del codigo de barras
        # y ' ' para los modulos blancos. Esto da una apariencia mas "codificada".
        line = "".join("?" if col else " " for col in row)
        output.append(line)
    return "\n".join(output)

# --------- DATOS DINAMICOS DE LA BOLETA ---------
boleta = {
    "folio": 182081,
    "fecha": date.today().strftime("%d-%m-%Y"),
    "rut_cliente": "99999999-9",
    "codigo_cliente": "999999999",
    "razon_social": "VENTA SIN NOMBRE",
    "detalle": [
        {"desc": "SERVICIOS SERVITECA", "codigo": "001", "cant": 1, "unit": 1261, "total": 1261},
        {"desc": "CAMBIO DE ACEITE", "codigo": "002", "cant": 1, "unit": 5000, "total": 5000}
    ],
    "total": 6261, # Suma de los totales de detalle
    "iva": 1000, # Ejemplo de IVA
    "verificacion_url": "www.facturacion.cl/tytspa/boleta",
    "timbre_base64": "EJEMPLO1234567890ABCDEF==" # Este texto es el que se codifica en el PDF417
}

# --------- GENERAR CODIGO PDF417 ---------
# El texto del timbre es lo que se codifica en el PDF417.
# Si el codigo PDF417 generado es demasiado ancho para MAX_CHARS_PER_LINE,
# considera reducir el parametro 'columns' en la funcion encode().
# Por ejemplo, 'columns=4' o 'columns=5'.
codes = encode(boleta["timbre_base64"], columns=6, security_level=5)
pdf417_text = render_pdf417_ascii(codes)

# --------- FORMATO DE BOLETA ---------
lines = []
lines.append("INVERSIONES Y SERVICIOS T&T SPA".center(MAX_CHARS_PER_LINE))
lines.append(f"RUT: 77.041.168-8".center(MAX_CHARS_PER_LINE))
lines.append("GIRO: SERVICIOS PARA EL TRANSPORTE,".center(MAX_CHARS_PER_LINE))
lines.append("LAVADO DE VEHICULOS, MANTENCIONES".center(MAX_CHARS_PER_LINE))
lines.append("CASA MATRIZ: RUTA 5 2680".center(MAX_CHARS_PER_LINE))
lines.append("Comuna: COQUIMBO - Ciudad: COQUIMBO".center(MAX_CHARS_PER_LINE))
lines.append("-" * MAX_CHARS_PER_LINE)
lines.append(f"Boleta Electronica Nro.: {boleta['folio']}")
lines.append(f"Fecha Emision: {boleta['fecha']}")
lines.append("-" * MAX_CHARS_PER_LINE)
lines.append(f"CLIENTE: {boleta['razon_social']}")
lines.append(f"RUT: {boleta['rut_cliente']} - Codigo: {boleta['codigo_cliente']}")
lines.append("Direccion:")
lines.append("Comuna:  - Ciudad:")
lines.append("-" * MAX_CHARS_PER_LINE)

# Encabezado de la tabla de detalle
header_format = "{:<15}{:<5}{:<8}{:<8}" # Descripcion, Cant., Unit., Valor
lines.append(header_format.format("Descripcion", "Cant.", "Unit.", "Valor"))
lines.append("-" * MAX_CHARS_PER_LINE)

for item in boleta["detalle"]:
    # Ajusta el formato para que cada linea de detalle quepa en MAX_CHARS_PER_LINE
    # Se asume que la descripcion puede ser larga y se envolvera si es necesario.
    # Para simplificar, ajustamos los campos numericos.
    desc_line = item['desc']
    lines.append(desc_line) # La descripcion puede ocupar una o mas lineas

    # Formateo para alinear las columnas de codigo, cantidad, unitario y total
    # Ajusta los anchos de los campos segun sea necesario para que la suma no exceda MAX_CHARS_PER_LINE
    # Ejemplo: Codigo (8), Cant (4), Unit (8), Total (8) = 28 + espacios
    detail_line_format = "{:<8} {:<4.0f}x{:<8.0f} {:<8.0f}"
    lines.append(detail_line_format.format(item['codigo'], item['cant'], item['unit'], item['total']))

lines.append("-" * MAX_CHARS_PER_LINE) # Linea de separacion antes del total
# Alinea el total a la derecha, ajustando el espaciado
total_str = f"T O T A L {boleta['total']:.2f}"
lines.append(total_str.rjust(MAX_CHARS_PER_LINE))

lines.append("")
lines.append(f"El IVA de esta boleta es ${boleta['iva']:.2f}".ljust(MAX_CHARS_PER_LINE))
lines.append("")
lines.append("Timbre Electronico S.I.I.".center(MAX_CHARS_PER_LINE))
lines.append("Resol. 80 del 2014".center(MAX_CHARS_PER_LINE))
lines.append(f"Verifique Doc.: {boleta['verificacion_url']}".center(MAX_CHARS_PER_LINE))
lines.append("")
lines.append(pdf417_text) # Agrega el codigo PDF417 a las lineas de la boleta
lines.append("")
lines.append("Gracias por su compra".center(MAX_CHARS_PER_LINE))
lines.append("No se aceptan devoluciones".center(MAX_CHARS_PER_LINE))
lines.append("Atencion: 9 a 18 h".center(MAX_CHARS_PER_LINE))

# --------- PREPARAR Y ENVIAR A LA IMPRESORA USANDO EL COMANDO LP ---------
output_filename = "boleta.bin"
# Unir todas las lineas con saltos de linea y anadir el comando de corte ESC/POS
# El comando de corte automatico para ESC/POS es \x1D\x56\x00
# Asegurate de que el string se codifique a bytes para la impresora
printer_content = "\n".join(lines) + "\n\n\n\n\n\n\x1D\x56\x00"

try:
    # Escribir el contenido en un archivo binario
    with open(output_filename, "wb") as f:
        f.write(printer_content.encode('latin-1')) # Usar una codificacion compatible con impresoras termicas

    # Ejecutar el comando lp para imprimir el archivo
    # Asegurate de que la impresora 'HS-K24' este correctamente configurada en tu sistema CUPS
    print_command = ["lp", "-d", "HS-K24", "-o", "raw", output_filename]
    result = subprocess.run(print_command, capture_output=True, text=True, check=True)

    print(f"\nBoleta enviada a la impresora '{boleta['folio']}' exitosamente.")
    print(f"Salida del comando lp: {result.stdout}")

except FileNotFoundError:
    print(f"Error: El comando 'lp' o el archivo '{output_filename}' no se encontraron.")
    print("Asegurate de que CUPS este instalado y configurado correctamente, y que el archivo se haya creado.")
except subprocess.CalledProcessError as e:
    print(f"Error al ejecutar el comando lp: {e}")
    print(f"Stderr: {e.stderr}")
    print("Verifica si la impresora 'HS-K24' esta en linea y configurada correctamente en CUPS.")
    print("Puedes usar 'lpstat -p' para ver el estado de las impresoras.")
except Exception as e:
    print(f"Ocurrio un error inesperado: {e}")
finally:
    # Limpiar el archivo temporal
    if os.path.exists(output_filename):
        os.remove(output_filename)
        print(f"Archivo temporal '{output_filename}' eliminado.")
