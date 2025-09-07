from PySide6.QtWidgets import QLabel, QPushButton, QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import QTimer
from appValues import AppValues
import socket
import base64
from datetime import date
from zeep import Client

BOTON_HIDE="background: transparent; border: none;"
#BOTON_HIDE="transparent"
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
            'Rut': base64.b64encode("1-9".encode()).decode(),
            'Clave': base64.b64encode("plano91098".encode()).decode(),
            'Puerto': base64.b64encode("0".encode()).decode()
        },
        'file': base64.b64encode(contenido_plano.encode('utf-8')).decode(),
        'formato': "1"
    }

    try:
        response = client.service.Procesar(**params)
        print("Boleta enviada correctamente:", response)
    except Exception as e:
        print("Error al procesar la boleta:", e)
        
class CashlessScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.values = AppValues()
        self.initUI()
        self.values.toPay_changed.connect(self.update_toPay_label)

    def initUI(self):
        global BOTON_HIDE   
        self.setWindowTitle("Comprar Fichas")
        self.setGeometry(100, 100, 1065, 595)

        # Fondo con imagen
        self.background_label = QLabel(self)
        self.pixmap = QPixmap("./imagenes/6-targetPay.jpg")
        self.background_label.setPixmap(self.pixmap)
        self.background_label.setScaledContents(True)
        
        # Boton back
        self.bBack = QPushButton("", self)
        self.bBack.setGeometry(35, 35, 75, 75)
        self.bBack.setStyleSheet(BOTON_HIDE)  # Estilo para hacerlo invisible
        self.bBack.clicked.connect(self.returnToProductWindow)
              
        #Bloque variable de monto a pagar
        self.toPay_label = QLabel(f"${str(self.values.toPay)}", self)
        self.toPay_label.setGeometry(589,382,210,50)     
        # Cambiar el tamano y la tipografia
        font = QFont()
        font.setPointSize(30)  # Establecer el tamaoo de la fuente
        #font.setBold(True) # establecer negrita
        self.toPay_label.setFont(font)
        self.toPay_label.setAlignment(Qt.AlignLeft)
        self.toPay_label.setStyleSheet("color: black; background-color: white; border: none;")

    def resizeEvent(self, event):
        size = self.size()
        self.background_label.resize(size)  # Ajusta el fondo al tamaño de la ventana
        super().resizeEvent(event)  
              
    def update_coin_label(self, value):
        self.coins_label.setText(str(value))
        
    def update_toPay_label(self, value):
        self.toPay_label.setText(f"${str(value)}")

    def returnToProductWindow(self):
        self.stacked_widget.setCurrentIndex(3)
        
    def goToErrorPay(self):
        self.stacked_widget.setCurrentIndex(6)
        
    def goToSuccessPay(self):
        self.stacked_widget.setCurrentIndex(7)        
        
    def pay(self):
        pago = self.POS(self.values.toPay)
        if pago == 'Aprobado':
            total_cash = (self.values.historialCashless + self.values.toPay)
            self.values.set_historialCashless(total_cash)
            if self.values.facturacionPOS == "on":
                generar_y_enviar_boleta(self.values.toPay, self.values.coins, self.values.valor_coin)
            else:
                print("no se genera boleta en facturacion.cl")
            
            self.goToSuccessPay()
        else:
            self.goToErrorPay()
        
    def POS(self, precio):
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            client_socket.connect(('localhost', 3000))  
            client_socket.send(("01" + str(precio)).encode()) 
            respuesta = client_socket.recv(1024).decode()
            client_socket.close()
            return respuesta
        except Exception as e:
            print("Error en POS:", e)
            return None

    def showEvent(self, event):
        """Se ejecuta automaticamente cuando la ventana se muestra."""
        super().showEvent(event)
        QTimer.singleShot(1000, lambda: self.pay())
