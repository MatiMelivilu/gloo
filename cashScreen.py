from PySide6.QtWidgets import QLabel, QPushButton, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QPixmap, QFont
from appValues import AppValues
import serial
import time
from datetime import date
from datetime import datetime
from gpiozero import Device, LED, Button
from gpiozero.pins.pigpio import PiGPIOFactory
from datetime import date
from zeep import Client
from escpos.printer import Usb
from pdf417gen import encode, render_image
from PIL import Image
import base64
import xml.etree.ElementTree as ET
import subprocess

Device.pin_factory = PiGPIOFactory()
PORT = '/dev/ttyUSB0'
BAUDRATE = 9600
COIN_ADDR = 2
BILL_ADDR = 40
HOST_ADDR = 1

BOTON_HIDE = "background: transparent; border: none;"


def checksum(msg):
    return (256 - sum(msg)) % 256

def build_packet(addr, cmd, data=[]):
    packet = [addr, len(data), HOST_ADDR, cmd] + data
    packet.append(checksum(packet))
    return bytes(packet)


class CoinReaderThread(QThread):
    coin_inserted = Signal(int)

    def __init__(self, gpio_config):
        super().__init__()
        self._running = True
        self.boleta_en_proceso = False
        self.gpio = gpio_config
        self.values = AppValues()
        try:
            self.ser = serial.Serial(PORT, BAUDRATE, timeout=1)
            self.enable_monedero()
            self.last_coin_counter = self.initialize_counter()
            self.last_bill_counter = self.initialize_counterBILL()
            print(self.last_coin_counter, "----" ,self.last_bill_counter)
        except serial.SerialException as e:
            print("Error al abrir el puerto serie:", e)
            self.ser = None
            self.last_coin_counter = 0
            self.last_bill_counter = 0
                    
    def enable_gpio_callbacks(self):
        self.gpio.ch1.when_pressed = self.ch1Detect
        self.gpio.ch2.when_pressed = self.ch2Detect
        self.gpio.ch3.when_pressed = self.ch3Detect
        self.gpio.ch4.when_pressed = self.ch4Detect

    def disable_gpio_callbacks(self):
        self.gpio.ch1.when_pressed = None
        self.gpio.ch2.when_pressed = None
        self.gpio.ch3.when_pressed = None
        self.gpio.ch4.when_pressed = None

    def ch1Detect(self):
        pass
        #self.coin_inserted.emit(1000)

    def ch2Detect(self):
        pass
        #self.coin_inserted.emit(10000)

    def ch3Detect(self):
        pass
        #self.coin_inserted.emit(2000)

    def ch4Detect(self):
        pass
        #self.coin_inserted.emit(5000)
        
    def initialize_counter(self):
        self.ser.reset_input_buffer()
        self.ser.write(build_packet(COIN_ADDR,229))
        time.sleep(0.1)
        raw = self.ser.read(16)
        if raw and len(raw) >= 10:
            return raw[9]
        return 0
        
    def initialize_counterBILL(self):
        self.ser.reset_input_buffer()
        self.ser.write(build_packet(BILL_ADDR,159))
        time.sleep(0.1)
        raw = self.ser.read(16)
        if raw and len(raw) >= 10:
            return raw[9]
        return 0
        
    def enable_monedero(self):
        if self.ser:
            self.ser.reset_input_buffer()
            self.ser.write(build_packet(COIN_ADDR, 2))
            time.sleep(0.1)
            self.ser.write(build_packet(COIN_ADDR, 245))
            time.sleep(0.1)
            self.ser.write(build_packet(COIN_ADDR, 230))
            time.sleep(0.1)
            self.ser.write(build_packet(COIN_ADDR, 231, [255, 255]))
            time.sleep(0.1)
            self.ser.write(build_packet(BILL_ADDR, 147, [0]))
            time.sleep(0.1)
            self.ser.write(build_packet(BILL_ADDR, 232, [0]))
            time.sleep(0.1)
            self.ser.write(build_packet(BILL_ADDR, 228, [1]))
            time.sleep(0.1)
            print('monto a pagar', self.values.toPay)
            if self.values.toPay < 1000:
                self.ser.write(build_packet(BILL_ADDR, 231, [0, 0]))
                print('enable', 0)
            elif self.values.toPay >= 1000 and self.values.toPay < 2000:
                self.ser.write(build_packet(BILL_ADDR, 231, [1, 0]))
                print('enable', 1)
            elif self.values.toPay >= 2000 and self.values.toPay < 5000:
                self.ser.write(build_packet(BILL_ADDR, 231, [3, 0]))
                print('enable', 3)
            elif self.values.toPay >= 5000 and self.values.toPay < 10000:
                self.ser.write(build_packet(BILL_ADDR, 231, [7, 0]))  
                print('enable', 7)  
            elif self.values.toPay >= 10000 and self.values.toPay < 20000:
                self.ser.write(build_packet(BILL_ADDR, 231, [15, 0]))
                print('enable', 15)
            else:
                self.ser.write(build_packet(BILL_ADDR, 231, [0, 0]))
            time.sleep(0.1)
            _ = self.ser.read(16)
            

    def run(self):
        state = 0
        while self._running and self.ser:
            self.ser.reset_input_buffer()
            if state == 0:
                self.ser.write(build_packet(COIN_ADDR, 229))
                state = 1
            elif state == 1:
                self.ser.write(build_packet(BILL_ADDR, 159))
                state = 0
            time.sleep(0.1)
            
            raw = self.ser.read(16)

            if raw and len(raw) >= 11:
                dispositivo = raw[7]
                evento = raw[9]
                #monedaInsertada = raw[9]
                #tipoMoneda = raw[10]
                tipo = raw[10]
                ecrow = raw[11]
                
                if dispositivo == COIN_ADDR:
                    if evento != self.last_coin_counter:
                        self.last_coin_counter = evento
                        valor = self.map_coin(tipo)
                        if valor > 0:
                            self.coin_inserted.emit(valor)
                elif dispositivo == BILL_ADDR:
                    if evento != self.last_bill_counter:
                        self.last_bill_counter = evento
                        if ecrow == 1:
                            valor = self.map_bill(tipo)
                            if valor > 0:
                                self.ser.write(build_packet(BILL_ADDR, 154,[1]))
                                self.coin_inserted.emit(valor)                
            time.sleep(0.1)

    def stop(self):
        self._running = False
        self.quit()
        self.wait()
        if self.ser:
            self.ser.close()

    def map_coin(self, tipo):
        return {
            1: 10,
            2: 50,
            3: 100,
            4: 100,
            5: 500
        }.get(tipo, 0)

    def map_bill(self, tipo):
        return {
            1: 1000,
            2: 2000,
            3: 5000,
            4: 10000,
            5: 20000
        }.get(tipo, 0)
# === Paso 1: Obtener datos desde el servicio web ===
def obtener_ticket_boleta(tipo_dte, folio):
    wsdl = 'http://ws.facturacion.cl/WSDS/wsplano.asmx?wsdl'
    client = Client(wsdl)

    params = {
        'login': {
            'Usuario': base64.b64encode("TYTSPA".encode()).decode(),
            'Rut': base64.b64encode("77041168-8".encode()).decode(),
            'Clave': base64.b64encode("9e31781522".encode()).decode(),
            'Puerto': base64.b64encode("1".encode()).decode(),
            'IncluyeLink': base64.b64encode("1".encode()).decode()
        },
        'ticket': base64.b64encode(f"ticket@{tipo_dte}@{folio}".encode()).decode()
    }

    try:
        response = client.service.getBoletaTicket(**params)
        return response
    except Exception as e:
        #print("Error al obtener ticket:", e)
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

        #print("=== Datos procesados ===")
        #print("HEAD:\n", head)
        #print("TED:\n", ted)
        #print("FOOT:\n", foot)

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

        # === Paso 4: Conectar con la impresora USB ===
        VENDOR_ID = 0x0fe6  # Ajustar segn el modelo con `lsusb` 0fe6
        PRODUCT_ID = 0x811e # 811e
        printer = Usb(idVendor=VENDOR_ID, idProduct=PRODUCT_ID, in_ep=0x81, out_ep=0x01)

        # === Paso 5: Imprimir en el orden correcto ===
        printer.text(head)  # Imprimir encabezado
        printer.image(bw_img)  # Imprimir cdigo PDF417
        printer.text(foot)  # Imprimir pie de pgina
        timestamp = datetime.now().strftime("creado por facturacion.cl - %d-%m-%Y %H:%M:%S")
        printer.text(f"\n{timestamp}\n")
        printer.text("\n")
        printer.cut()  # Corte de papel
        printer.close()

        #print("? Ticket enviado a la impresora.")

    except Exception as e:
        #print("Error al imprimir ticket:", e)
        pass

def extraer_folio(xml_respuesta):
    try:
        root = ET.fromstring(xml_respuesta)
        documento = root.find(".//Documento/Folio")

        if documento is not None:
            return documento.text
        else:
            raise ValueError("No se encontra el numero de folio en la respuesta.")
    except Exception as e:
        #print("Error al extraer folio:", e)
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
            'Rut': base64.b64encode("77041168-8".encode()).decode(),
            'Clave': base64.b64encode("9e31781522".encode()).decode(),
            'Puerto': base64.b64encode("1".encode()).decode(),
            'IncluyeLink': base64.b64encode("1".encode()).decode()
        },
        'file': base64.b64encode(contenido_plano.encode('utf-8')).decode(),
        'formato': "1"
    }

    try:
        response = client.service.Procesar(**params)
        #print("Boleta enviada correctamente:", response)

        # Extraer el nmero de folio de la respuesta XML
        folio = extraer_folio(response)

        if folio:
            time.sleep(2)
            #print(f"? Numero de folio obtenido: {folio}")
            xml_ticket = obtener_ticket_boleta(39, folio)
            if xml_ticket:
                imprimir_ticket(xml_ticket)
        else:
            #print("? No se pudo obtener el numero de folio.")
            pass

    except Exception as e:
        #print("Error al procesar la boleta:", e)
        pass


class CashScreen(QWidget):
    def __init__(self, stacked_widget, gpio_config):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.values = AppValues()
        self.gpio_config = gpio_config
        self.coin_thread = None
        self.boleta_en_proceso = False
        self.initUI()
        self.values.toPay_changed.connect(self.update_toPay_label)
        self.values.Pay_changed.connect(self.update_Pay_label)
    def initUI(self):
        self.setWindowTitle("Comprar Fichas")
        self.setGeometry(100, 100, 1065, 595)

        self.background_label = QLabel(self)
        pixmap = QPixmap("./imagenes/5-coinInsert.jpg")
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)

        self.bBack = QPushButton("", self)
        self.bBack.setGeometry(35, 35, 75, 75)
        self.bBack.setStyleSheet(BOTON_HIDE)
        self.bBack.clicked.connect(self.returnToProductWindow)

        self.toPay_label = QLabel(f"${str(self.values.toPay)}", self)
        self.toPay_label.setGeometry(552, 357, 210, 50)
        font = QFont()
        font.setPointSize(30)
        self.toPay_label.setFont(font)
        self.toPay_label.setAlignment(Qt.AlignLeft)
        self.toPay_label.setStyleSheet("color: black; background-color: white; border: none;")

        self.Pay_label = QLabel(f"${str(self.values.Pay)}", self)
        self.Pay_label.setGeometry(700, 445, 210, 50)
        font2 = QFont()
        font2.setPointSize(30)
        self.Pay_label.setFont(font2)
        self.Pay_label.setAlignment(Qt.AlignLeft)
        self.Pay_label.setStyleSheet("color: black; background-color: white; border: none;")

    def resizeEvent(self, event):
        size = self.size()
        self.background_label.resize(size)
        super().resizeEvent(event)

    def update_toPay_label(self, value):
        self.toPay_label.setText(f"${str(value)}")

    def update_Pay_label(self, value):
        self.Pay_label.setText(f"${str(value)}")

    def returnToProductWindow(self):
        self.boleta_en_proceso = False
        self.stopCashReader()
        self.gpio_config.inhibit.on()
        self.stacked_widget.setCurrentIndex(3)

    def showEvent(self, event):
        super().showEvent(event)
        self.values.set_Pay(0)
        QTimer.singleShot(1000, self.payCash)

    def hideEvent(self, event):
        super().hideEvent(event)
        self.stopCashReader()

    def stopCashReader(self):
        if self.coin_thread:
            self.coin_thread.disable_gpio_callbacks()
            self.coin_thread.stop()
            self.coin_thread = None

    def payCash(self):
        if self.coin_thread is None:
            self.coin_thread = CoinReaderThread(self.gpio_config)
            self.coin_thread.coin_inserted.connect(self.update_payment)
            self.coin_thread.start()
            self.gpio_config.inhibit.off()
            QTimer.singleShot(300, self.coin_thread.enable_gpio_callbacks)

    def update_payment(self, amount):
        if self.boleta_en_proceso:
            return
        self.values.Pay += amount
        self.Pay_label.setText(f"${str(self.values.Pay)}")

        if self.values.Pay >= self.values.toPay:
            self.boleta_en_proceso = True
            print("Pago completo. Generando boleta.")
            total_cash = (self.values.historialCash + self.values.Pay)
            self.values.set_historialCash(total_cash)
            self.gpio_config.inhibit.on()
            self.stopCashReader()

            cantidad_fichas = self.values.toPay

            try:
                generar_y_enviar_boleta(self.values.toPay, self.values.coins, self.values.valor_coin)
            except Exception as e:
                print("Falla al emitir boleta")

            self.values.set_Pay(0)

            self.go_to_success_screen()

    def go_to_success_screen(self):
        self.boleta_en_proceso = False
        self.values.set_Pay(0)
        #self.values.set_toPay(0)
        self.Pay_label.setText(f"${str(self.values.Pay)}")
        self.stacked_widget.setCurrentIndex(7)
