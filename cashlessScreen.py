from PySide6.QtWidgets import QLabel, QPushButton, QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import QTimer
from appValues import AppValues
import socket
import base64
import xml.etree.ElementTree as ET
from datetime import date
from zeep import Client
from logger_config import setup_logger

logger = setup_logger()

BOTON_HIDE="background: transparent; border: none;"
#BOTON_HIDE="transparent"
        
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
        logger.info("Regresando a seleccion de metodo de pagos")
        self.stacked_widget.setCurrentIndex(3)
        
    def goToErrorPay(self):
        logger.info("Redirigiendo a pago fallido")
        self.stacked_widget.setCurrentIndex(6)
        
    def goToSuccessPay(self):
        logger.info("Redirigiendo a entrega de fichas")
        self.stacked_widget.setCurrentIndex(7)        
        
    def pay(self):
        logger.info("Iniciando POS")
        pago = self.POS(self.values.toPay)
        if pago == 'Aprobado':
            logger.info("Pago aprobado")
            self.values.set_Pay(self.values.toPay)
            total_cash = (self.values.historialCashless + self.values.Pay)
            self.values.set_historialCashless(total_cash)            
            self.goToSuccessPay()
        else:
            logger.info("Error en pago")
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
