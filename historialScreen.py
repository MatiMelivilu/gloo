from PySide6.QtWidgets import QLabel, QPushButton, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QPixmap, QFont
from appValues import AppValues
from sendEmail import EmailSender
from datetime import datetime

BOTON_HIDE = "background: transparent; border: none;"
#BOTON_HIDE = "transparent;"

class HistorialScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.values = AppValues()
        self.email = EmailSender()
        self.coin_thread = None
        self.initUI()
        self.values.historialCash_changed.connect(self.update_historialCash_label)
        self.values.historialCashless_changed.connect(self.update_historialCashless_label)

    def initUI(self):
        self.setWindowTitle("Comprar Fichas")
        self.setGeometry(100, 100, 1065, 595)

        self.background_label = QLabel(self)
        pixmap = QPixmap("./imagenes/C4-historical.jpg")
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)

        self.bBack = QPushButton("", self)
        self.bBack.setGeometry(380, 550, 480, 55)
        self.bBack.setStyleSheet(BOTON_HIDE)
        self.bBack.clicked.connect(self.returnToProductWindow)

        self.bEnviar = QPushButton("Enviar", self)
        self.bEnviar.setGeometry(310, 435, 300, 65)
        self.bEnviar.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px solid black;
                color: black;
                font-weight: bold;
                font-size: 40px;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #f0f0f0;
            }
            QPushButton:pressed {
                background-color: #FBD556;
            }
        """)
        self.bEnviar.clicked.connect(self.enviarHistorial)
        
        self.email_label = QLabel(f"Correo: {self.values.correo}", self)
        self.email_label.setGeometry(300, 510, 600, 35)
        font = QFont()
        font.setPointSize(15)
        self.email_label.setFont(font)
        self.email_label.setAlignment(Qt.AlignLeft)
        self.email_label.setStyleSheet("color: black; background-color: white; border: none;")

        self.historialCash_label = QLabel(f"${str(self.values.historialCash)}", self)
        self.historialCash_label.setGeometry(770, 250, 210, 50)
        font = QFont()
        font.setPointSize(30)
        self.historialCash_label.setFont(font)
        self.historialCash_label.setAlignment(Qt.AlignLeft)
        self.historialCash_label.setStyleSheet("color: black; background-color: white; border: none;")

        self.historialCashless_label = QLabel(f"${str(self.values.historialCashless)}", self)
        self.historialCashless_label.setGeometry(770, 325, 210, 50)
        font2 = QFont()
        font2.setPointSize(30)
        self.historialCashless_label.setFont(font2)
        self.historialCashless_label.setAlignment(Qt.AlignLeft)
        self.historialCashless_label.setStyleSheet("color: black; background-color: white; border: none;")
        
        self.total_label = QLabel(f"${str(self.values.historialCashless + self.values.historialCash)}", self)
        self.total_label.setGeometry(770, 450, 210, 50)
        self.total_label.setFont(font2)
        self.total_label.setAlignment(Qt.AlignLeft)
        self.total_label.setStyleSheet("color: black; background-color: white; border: none;")

    def resizeEvent(self, event):
        size = self.size()
        self.background_label.resize(size)
        super().resizeEvent(event)

    def update_historialCash_label(self, value):
        self.historialCash_label.setText(f"${str(value)}")
        self.total_label.setText(f"${str(self.values.historialCashless + self.values.historialCash)}")

    def update_historialCashless_label(self, value):
        self.historialCashless_label.setText(f"${str(value)}")
        self.total_label.setText(f"${str(self.values.historialCashless + self.values.historialCash)}")
        
    def enviarHistorial(self):
        self.email.enviar_resumen_venta(self.values.fecha_inicio, self.values.correo, self.values.historialCashless, self.values.historialCash, self.values.cantidad_fichas_total, self.values.cantidad_promos_total)
        self.values.set_historialCash(0)
        self.values.set_historialCashless(0)
        self.values.set_cantidad_fichas_total(0)
        self.values.set_cantidad_promos_total(0)
        current_time = datetime.now().strftime("%d-%m-%Y")
        self.values.set_fecha_inicio(current_time)

    def returnToProductWindow(self):
        self.stacked_widget.setCurrentIndex(10)

    def showEvent(self, event):
        super().showEvent(event)
        
    def go_to_success_screen(self):
        self.stacked_widget.setCurrentIndex(7)
