from PySide6.QtWidgets import QLabel, QPushButton, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QPixmap, QFont
from appValues import AppValues

BOTON_HIDE = "background: transparent; border: none;"
#BOTON_HIDE = "transparent;"

class HistorialScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.values = AppValues()
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

        self.bBorrar = QPushButton("", self)
        self.bBorrar.setGeometry(320, 440, 280, 60)
        self.bBorrar.setStyleSheet(BOTON_HIDE)
        self.bBorrar.clicked.connect(self.borrarHistorial)

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
        
    def borrarHistorial(self):
        self.values.set_historialCash(0)
        self.values.set_historialCashless(0)

    def returnToProductWindow(self):
        self.stacked_widget.setCurrentIndex(10)

    def showEvent(self, event):
        super().showEvent(event)
        
    def go_to_success_screen(self):
        self.stacked_widget.setCurrentIndex(7)
