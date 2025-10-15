from PySide6.QtWidgets import QLabel, QPushButton, QWidget
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QTimer, QMetaObject, Qt, Slot
from gpiozero import Device, LED, Button
from gpiozero.pins.pigpio import PiGPIOFactory
from appValues import AppValues
from datetime import date
from datetime import datetime
from zeep import Client
from escpos.printer import Usb
from pdf417gen import encode, render_image
from PIL import Image
import base64
import xml.etree.ElementTree as ET
import subprocess
import time

Device.pin_factory = PiGPIOFactory()

BOTON_HIDE2 = "background: transparent; border: none;"
BOTON_HIDE1 = "background: black; border: none;"


# === Paso 1: Obtener datos desde el servicio web ===
def obtener_ticket_boleta(tipo_dte, folio):
    wsdl = 'http://ws.facturacion.cl/WSDS/wsplano.asmx?wsdl'
    client = Client(wsdl)

    params = {
        'login': {
            'Usuario': base64.b64encode("TYTSPA".encode()).decode(),
            'Rut': base64.b64encode("1-9".encode()).decode(),#77041168-8
            'Clave': base64.b64encode("plano91098".encode()).decode(),#9e31781522
            'Puerto': base64.b64encode("1".encode()).decode(),
            'IncluyeLink': base64.b64encode("1".encode()).decode()
        },
        'ticket': base64.b64encode(f"ticket@{tipo_dte}@{folio}".encode()).decode()
    }

    try:
        response = client.service.getBoletaTicket(**params)
        return response
    except Exception as e:
        print("Error al obtener ticket:", e)
        return None

# === Paso 2: Procesar XML y extraer los valores necesarios ===
def imprimir_ticket(xml_data):
    def safe_b64decode(elem):
        if elem is None or elem.text is None:
            return ""
        try:
            return base64.b64decode(elem.text).decode('utf-8')
        except UnicodeDecodeError:
            return base64.b64decode(elem.text).decode('latin-1')  # Fallback seguro

    try:
        root = ET.fromstring(xml_data)
        mensaje = root.find('Mensaje')

        if mensaje is None:
            raise ValueError("No se encontro el nodo <Mensaje>")

        head = safe_b64decode(mensaje.find('Head'))
        foot = safe_b64decode(mensaje.find('Foot'))
        ted = safe_b64decode(mensaje.find('TED'))  # Campo a convertir en PDF417

        print("=== Datos procesados ===")
        print("HEAD:\n", head)
        print("TED:\n", ted)
        print("FOOT:\n", foot)

        # === Paso 3: Generar cdigo PDF417 ===
        codes = encode(ted, columns=24, security_level=5)
        img = render_image(codes, scale=3)  # Ajusta la escala si es necesario

        # Convertir imagen a blanco y negro puro (modo 1-bit)
        bw_img = img.convert("1")

        # Redimensionar si excede ancho del papel (max ~384 px para 58mm a 203 DPI)
        max_width = 570
        if bw_img.width > max_width:
            new_height = int((max_width / bw_img.width) * bw_img.height)
            bw_img = bw_img.resize((max_width, new_height), Image.LANCZOS)

        # === Paso 4: Conectar con la impresora USB === 4b43:3538 (Personal)
        VENDOR_ID = 0x4b43  # Ajustar segn el modelo con `lsusb` 0fe6
        PRODUCT_ID = 0x3538 # 811e
        printer = Usb(idVendor=VENDOR_ID, idProduct=PRODUCT_ID, in_ep=0x82, out_ep=0x02) #in_ep=0x81 out_ep=0x01

        # === Paso 5: Imprimir en el orden correcto ===
        printer.text(head)  # Imprimir encabezado
        printer.image(bw_img)  # Imprimir cdigo PDF417
        printer.text(foot)  # Imprimir pie de pgina
        timestamp = datetime.now().strftime("creado por facturacion.cl - %d-%m-%Y %H:%M:%S")
        printer.text(f"\n{timestamp}\n")
        printer.text("\n")
        printer.cut()  # Corte de papel
        printer.close()

        print("? Ticket enviado a la impresora.")

    except Exception as e:
        print("Error al imprimir ticket:", e)
        

def extraer_folio(xml_respuesta):
    try:
        root = ET.fromstring(xml_respuesta)
        documento = root.find(".//Documento/Folio")

        if documento is not None:
            return documento.text
        else:
            raise ValueError("No se encontra el numero de folio en la respuesta.")
    except Exception as e:
        print("Error al extraer folio:", e)
        return None

def generar_y_enviar_boleta(monto_pagado, cantidad_fichas, valor_unitario):
    UNITARIO = valor_unitario
    PAGADO = monto_pagado
    CANTIDAD = cantidad_fichas

    datos_boleta = {
        'TipoDTE': 39,
        'Folio': 0,
        'FechaEmision': date.today().isoformat(),
        'IndServicio': 3,
        'IndMntNeto': 0,
        'PeriodoDesde': '',
        'PeriodoHasta': '',
        'FechaVenc': '',
        'RUTCliente': '66666666-6',
        'CodInterno': 'coinMCH1',
        'RSCliente': 'Venta sin nombre',
        'GiroCliente': '',
        'DirCliente': '',
        'ComCliente': '',
        'CiuCliente': '',
        'Email': ''
    }
    sucursal = {
        "Nombre_sucursal": "AUTOLAVADO V2"#CASA MATRIZ
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

    detalle = [{
        'NroLinea': 1,
        'Codigo': 1,
        'Descripcion': 'Fichas de lavado',
        'IndExencion': 0,
        'Cantidad': CANTIDAD,
        'PrecioUnitario': UNITARIO,
        'ValorExento': 0,
        'MontoTotalLinea': PAGADO,
        'TipoItem': 'INT1',
        'UnidadMedida': 'UN',
        'PorcDescuento': (((CANTIDAD*UNITARIO) - PAGADO)/(CANTIDAD*UNITARIO))*100 if CANTIDAD > 0 else 0,
        'ValorDescuento': ((CANTIDAD*UNITARIO) - PAGADO)
    }]

    lines = []
    lines.append("->Boleta<-")
    b = datos_boleta
    cab = ";".join([
        str(b['TipoDTE']),
        str(b['Folio']),
        b['FechaEmision'],
        str(b['IndServicio']),
        str(b['IndMntNeto']),
        b['PeriodoDesde'],
        b['PeriodoHasta'],
        b['FechaVenc'],
        b['RUTCliente'],
        b['CodInterno'],
        b['RSCliente'],
        b['GiroCliente'],
        b['DirCliente'],
        b['ComCliente'],
        b['CiuCliente'],
        b['Email']
    ])+';'
    lines.append(cab)

    lines.append("->BoletaSucursal<-")
    suc = ";".join([
        sucursal["Nombre_sucursal"]
    ]) + ";"
    lines.append(suc)

    lines.append("->BoletaTotales<-")
    t = totales
    tot = ";".join(str(t[k]) for k in [
        'MontoExento', 'MontoNeto', 'MontoIva', 'MontoTotal',
        'IVAPropio', 'IVATercero', 'OtrosImpuestos', 'MontoOtros'
    ]) + ";"
    lines.append(tot)

    lines.append("->BoletaDetalle<-")
    for item in detalle:
        det = ";".join([
            str(item['NroLinea']),
            str(item['Codigo']),
            str(item['Descripcion']),
            str(item['IndExencion']),
            str(item['Cantidad']),
            str(item['PrecioUnitario']),
            str(item['ValorExento']),
            str(item['MontoTotalLinea']),
            str(item['TipoItem']),
            str(item['UnidadMedida']),
            "",
            str(item['PorcDescuento']),
            str(item['ValorDescuento'])
        ]) + ";"
        lines.append(det)

    contenido_plano = "\n".join(lines)

    wsdl = 'http://ws.facturacion.cl/WSDS/wsplano.asmx?wsdl'
    client = Client(wsdl)

    params = {
        'login': {
            'Usuario': base64.b64encode("TYTSPA".encode()).decode(),
            'Rut': base64.b64encode("1-9".encode()).decode(),#77041168-8
            'Clave': base64.b64encode("plano91098".encode()).decode(),#9e31781522
            'Puerto': base64.b64encode("1".encode()).decode(),
            'IncluyeLink': base64.b64encode("1".encode()).decode()
        },
        'file': base64.b64encode(contenido_plano.encode('utf-8')).decode(),
        'formato': "1"
    }

    try:
        response = client.service.Procesar(**params)
        print("Boleta enviada correctamente:", response)

        # Extraer el nmero de folio de la respuesta XML
        folio = extraer_folio(response)

        if folio:
            time.sleep(2)
            #print(f"? Numero de folio obtenido: {folio}")
            xml_ticket = obtener_ticket_boleta(39, folio)
            if xml_ticket:
                imprimir_ticket(xml_ticket)
        else:
            print("? No se pudo obtener el numero de folio.")
            

    except Exception as e:
        print("Error al procesar la boleta:", e)
        

class SuccessScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.values = AppValues()
        self.entregados = 0
        self.hopperPIN = LED(19)
        self.hopperPIN.on()
        self.sensorPIN = Button(2, bounce_time=0.05)
        self.error_timeout = 10_000  # tiempo en milisegundos
        self.succesTime = 3_000
        self.entrega_timer = QTimer(self)
        self.entrega_timer.setSingleShot(True)
        self.entrega_timer.timeout.connect(self.hopperError)
        self.succesTimer = QTimer(self)
        self.succesTimer.setSingleShot(True)
        self.succesTimer.timeout.connect(self.showProductWindow)
        self.boleta_en_proceso = False
        self.initUI()

    def enableSensor(self):
        self.sensorPIN.when_pressed = self.entregado_gpio
        
    def disableSensor(self):
        self.sensorPIN.when_pressed = None

    def initUI(self):
        global BOTON_HIDE1
        self.setWindowTitle("Gloo Car Wash")
        self.setGeometry(100, 100, 1065, 595)

        self.label = QLabel(self)
        self.pixmap = QPixmap("./imagenes/8-paySuccess.jpg")
        self.label.setPixmap(self.pixmap)
        self.label.setGeometry(0, 0, 1065, 595)
        self.label.setScaledContents(True)

        self.button1 = QPushButton("", self)
        self.button1.setGeometry(500, 470, 255, 50)
        self.button1.setStyleSheet(BOTON_HIDE1)
        # self.button1.clicked.connect(self.showProductWindow)

    def resizeEvent(self, event):
        size = self.size()
        self.label.resize(size)
        super().resizeEvent(event)

    def showProductWindow(self):
        self.hopperPIN.on()
        self.stacked_widget.setCurrentIndex(0)

    def showErrorWindow(self):
        self.hopperPIN.on()
        self.stacked_widget.setCurrentIndex(9)

    def entregado_gpio(self):
        # Esta funcion se ejecuta en un hilo externo
        # Redirigimos al hilo principal usando invokeMethod
        QMetaObject.invokeMethod(self, "entregado", Qt.QueuedConnection)

    @Slot()
    def entregado(self):
        if self.boleta_en_proceso:
            return  # evitar reentrada
            
        self.entregados += 1
        print('ficha entregada', self.entregados)
        self.entrega_timer.start(self.error_timeout)  # reinicia el timer

        if self.entregados == self.values.coins:
            self.boleta_en_proceso = True  # << Bloqueo
            self.entrega_timer.stop()

            self.entregados = 0
            self.hopperPIN.on()
            self.disableSensor()
            self.button1.setStyleSheet(BOTON_HIDE2)
            self.succesTimer.start(self.succesTime)
            #self.button1.clicked.connect(self.showProductWindow)
            try:
                print("generarndo boleta")
                generar_y_enviar_boleta(self.values.Pay, self.values.coins, self.values.valor_coin)
            except Exception as e:
                print("Falla al emitir boleta")
            finally:
                self.values.set_Pay(0)
                self.boleta_en_proceso = False  # << Libera bloqueo después

            
    def entregaFichas(self):
        tFichas = self.values.cantidad_fichas_total + self.values.cantidad_fichas
        self.values.set_cantidad_fichas_total(tFichas)
        tPromos = self.values.cantidad_promos_total + self.values.cantidad_promos
        self.values.set_cantidad_promos_total(tPromos)
        self.enableSensor()
        self.entregados = 0
        self.button1.setStyleSheet(BOTON_HIDE1)
        self.values.set_Pay(0)
        self.hopperPIN.off()
        self.entrega_timer.start(self.error_timeout)  # inicia el timer

    def hopperError(self):
        print("Error: No se detectaron fichas a tiempo.")
        #print(self.values.folio)
        #self.values.set_Pay(0)
        self.hopperPIN.on()
        self.showErrorWindow()

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(1000, self.entregaFichas)
        

        
