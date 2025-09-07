from PySide6.QtWidgets import QLabel, QPushButton, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QPixmap, QFont
from appValues import AppValues
import socket

BOTON_HIDE = "background: transparent; border: none;"
#BOTON_HIDE = "transparent;"

class POSScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.values = AppValues()
        self.coin_thread = None
        self.initUI()
        self.values.facturacionPOS_changed.connect(self.update_facturacion_label)
       
    def initUI(self):
        self.setWindowTitle("Comprar Fichas")
        self.setGeometry(100, 100, 1065, 595)

        self.background_label = QLabel(self)
        pixmap = QPixmap("./imagenes/C5-POS.jpg")
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)

        self.bBack = QPushButton("", self)
        self.bBack.setGeometry(380, 550, 480, 55)
        self.bBack.setStyleSheet(BOTON_HIDE)
        self.bBack.clicked.connect(self.returnToProductWindow)

        self.bPOLL = QPushButton("", self)
        self.bPOLL.setGeometry(270, 175, 310, 60)
        self.bPOLL.setStyleSheet(BOTON_HIDE)
        self.bPOLL.clicked.connect(self.Poll)

        self.bCierre = QPushButton("", self)
        self.bCierre.setGeometry(270, 265, 310, 60)
        self.bCierre.setStyleSheet(BOTON_HIDE)
        self.bCierre.clicked.connect(self.cierre_caja)

        self.bCarga = QPushButton("", self)
        self.bCarga.setGeometry(270, 365, 310, 60)
        self.bCarga.setStyleSheet(BOTON_HIDE)
        self.bCarga.clicked.connect(self.cargar_llaves)

        self.bFacturacion = QPushButton("", self)
        self.bFacturacion.setGeometry(270, 455, 310, 60)
        self.bFacturacion.setStyleSheet(BOTON_HIDE)
        self.bFacturacion.clicked.connect(self.facturacionSET)

        font = QFont()
        font.setPointSize(15)
        self.poll_label = QLabel(f"POLL:", self)
        self.poll_label.setGeometry(620, 260, 350, 40)
        self.poll_label.setFont(font)
        self.poll_label.setAlignment(Qt.AlignLeft)
        self.poll_label.setStyleSheet("color: black; background-color: #FBD556; border: none;")

        self.cierre_label = QLabel(f"Cierre:", self)
        self.cierre_label.setGeometry(620, 310, 350, 40)
        self.cierre_label.setFont(font)
        self.cierre_label.setAlignment(Qt.AlignLeft)
        self.cierre_label.setStyleSheet("color: black; background-color: #FBD556; border: none;")

        self.carga_label = QLabel(f"Carga:", self)
        self.carga_label.setGeometry(620, 360, 350, 40)
        self.carga_label.setFont(font)
        self.carga_label.setAlignment(Qt.AlignLeft)
        self.carga_label.setStyleSheet("color: black; background-color: #FBD556; border: none;")
        
        self.facturacion_label = QLabel(f"Facturacion POS: {self.values.facturacionPOS}", self)
        self.facturacion_label.setGeometry(620, 410, 350, 40)
        self.facturacion_label.setFont(font)
        self.facturacion_label.setAlignment(Qt.AlignLeft)
        self.facturacion_label.setStyleSheet("color: black; background-color: #FBD556; border: none;")

    def Poll(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 3000))  
        client_socket.send(("06").encode())
        respuesta = client_socket.recv(1024).decode()
        self.poll_label.setText(f"POLL: {respuesta}")
        client_socket.close()
        return respuesta 

    def cierre_caja(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 3000))  
        client_socket.send(("03").encode())
        respuesta = client_socket.recv(1024).decode()
        self.cierre_label.setText(f"Cierre: {respuesta}")
        client_socket.close()
        return respuesta 

    def cargar_llaves(self):
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client_socket.connect(('localhost', 3000))  
        client_socket.send(("02").encode())
        respuesta = client_socket.recv(1024).decode()
        self.carga_label.setText(f"Carga: {respuesta}")
        client_socket.close()
        return respuesta 
        
    def facturacionSET(self):
        if self.values.facturacionPOS == "on":
            self.values.set_facturacionPOS("off")
        elif self.values.facturacionPOS == "off":
            self.values.set_facturacionPOS("on")

    def resizeEvent(self, event):
        size = self.size()
        self.background_label.resize(size)
        super().resizeEvent(event)
        
    def update_facturacion_label(self, state):
        self.facturacion_label.setText(f"Facturacion POS: {state}")

    def returnToProductWindow(self):
        self.stacked_widget.setCurrentIndex(10)

    def showEvent(self, event):
        super().showEvent(event)
        self.poll_label.setText(f"POLL:")
        self.cierre_label.setText(f"Cierre:")
        self.carga_label.setText(f"Carga:")
        
