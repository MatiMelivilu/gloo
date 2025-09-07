import base64
from zeep import Client
from datetime import date

PAGADO = 3500
CANTIDAD = 4
UNITARIO = 1000

# 1. Datos de la boleta
datos_boleta = {
    'TipoDocumento': 39,
    'IndServicio': 0,
    'FechaEmision': date.today().isoformat(),    # 'YYYY-MM-DD'
    'TipoDTE': 3,
    'Folio': 0,
    'RutEmisor': '66666666-6',
    'CodSucursal': '',
    'RazonSocial': '',
    'Giro': '',
    'Direccion': '',
    'Comuna': '',
    'Ciudad': '',
    'Email': ''
}

totales = {
    'MontoExento': 0,
    'MontoNeto': 0,
    'MontoIva': 0,
    'MontoTotal': PAGADO,
    'IVAPropio': 0,
    'IVATercero': 0,
    'OtrosImpuestos': 0,
    'MontoOtros': 0
}

# Lista de items; puedes agregar tantos como necesites
detalle = [
    {
        'NroLinea': 1,
        'Codigo': 1,
        'Descripcion': 'Fichas de lavado',
        'DescAdicional': 0,
        'Cantidad': CANTIDAD,
        'PrecioUnitario': UNITARIO,
        'DescuentoMonto': 0,
        'MontoTotalLinea': PAGADO,
        'TipoItem': 'INT1',
        'UnidadMedida': 'UN',
        'PorcDescuento': (((CANTIDAD*UNITARIO) - PAGADO)/(CANTIDAD*UNITARIO))*100,
        'ValorDescuento': ((CANTIDAD*UNITARIO) - PAGADO)
    },
    # puedes anadir mas lineas aqui...
]

# 2. Genera el contenido ?plano?
lines = []

# Cabecera
lines.append("->Boleta<-")
b = datos_boleta
cab = ";".join([
    str(b['TipoDocumento']),
    str(b['IndServicio']),
    b['FechaEmision'],
    str(b['TipoDTE']),
    str(b['Folio']),
    "",   # campo reservado
    "",   # campo reservado
    "",   # campo reservado
    b['RutEmisor'],
    str(b['CodSucursal']),
    b['RazonSocial'],
    b['Giro'],
    b['Direccion'],
    b['Comuna'],
    b['Ciudad'],
    b['Email'],
    ""
])
lines.append(cab)

# Totales
lines.append("->BoletaTotales<-")
t = totales
tot = ";".join(str(t[k]) for k in [
    'MontoExento','MontoNeto','MontoIva','MontoTotal',
    'IVAPropio','IVATercero','OtrosImpuestos','MontoOtros'
]) + ";"
lines.append(tot)

# Detalle
lines.append("->BoletaDetalle<-")
for item in detalle:
    det = ";".join([
        str(item['NroLinea']),
        str(item['Codigo']),
        str(item['Descripcion']),
        str(item['DescAdicional']),
        str(item['Cantidad']),
        str(item['PrecioUnitario']),
        str(item['DescuentoMonto']),
        str(item['MontoTotalLinea']),
        str(item['TipoItem']),
        str(item['UnidadMedida']),
        "",  # campo reservado
        str(item['PorcDescuento']),
        str(item['ValorDescuento'])
    ]) + ";"
    lines.append(det)

contenido_plano = "\n".join(lines)

# 3. Guardar en boleta.txt
with open('boleta.txt', 'w', encoding='utf-8') as f:
    f.write(contenido_plano)

# 4. Enviar a facturacion.cl via SOAP
wsdl = 'http://ws.facturacion.cl/WSDS/wsplano.asmx?wsdl'
client = Client(wsdl)

params = {
    'login': {
        'Usuario': base64.b64encode("TYTSPA".encode()).decode(),
        'Rut': base64.b64encode("1-9".encode()).decode(),
        'Clave': base64.b64encode("plano91098".encode()).decode(),
        'Puerto': base64.b64encode("0".encode()).decode()
    },
    'file': base64.b64encode(contenido_plano.encode('utf-8')).decode(),
    'formato': "1"
}

try:
    response = client.service.Procesar(**params)
    print("Respuesta del servidor:")
    print(response)
except Exception as e:
    print("Error al procesar la boleta:", e)
