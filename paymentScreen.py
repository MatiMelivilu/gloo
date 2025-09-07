from PySide6.QtWidgets import QLabel, QPushButton, QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import QTimer
from appValues import AppValues

BOTON_HIDE="background: transparent; border: none;"
#BOTON_HIDE="transparent"

class PaymentScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.button5 = None
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Comprar Fichas")
        self.setGeometry(100, 100, 1065, 595)

        # Fondo con imagen
        self.background_label = QLabel(self)
        self.pixmap = QPixmap("./imagenes/4.0-Payment.jpg")
        self.background_label.setPixmap(self.pixmap)
        self.background_label.setScaledContents(True)
        
        # Boton de regreso
        self.button5 = QPushButton("", self)
        self.button5.setStyleSheet(BOTON_HIDE)  # Estilo para hacerlo invisible
        self.button5.clicked.connect(self.returnToProductWindow)
        
        # Boton efectivo
        self.bBack = QPushButton("", self)
        self.bBack.setGeometry(238, 370, 390, 133)
        self.bBack.setStyleSheet(BOTON_HIDE)  # Estilo para hacerlo invisible
        self.bBack.clicked.connect(self.SelectCash)
        
        # Boton tarjeta
        self.bBack = QPushButton("", self)
        self.bBack.setGeometry(680, 370, 390, 133)
        self.bBack.setStyleSheet(BOTON_HIDE)  # Estilo para hacerlo invisible
        self.bBack.clicked.connect(self.SelectCashless)

    def resizeEvent(self, event):
        size = self.size()
        self.background_label.resize(size)  # Ajusta el fondo al tamaño de la ventana
        if self.button5:
            btn5_width = int(size.width() * 0.06)
            btn5_height = int(size.height() * 0.1)
            x5 = size.width() - btn5_width - 1165
            y5 = size.height() - btn5_height - 610
            self.button5.setGeometry(x5, y5, btn5_width, btn5_height)  
        super().resizeEvent(event)  

    def SelectCash(self):
        self.background_label.setPixmap(QPixmap("./imagenes/4.1-cashSelect.jpg"))  # Imagen resaltada
        QTimer.singleShot(500, self.goToCash)  # Espera 0.5 segundos  
        
    def SelectCashless(self):
        self.background_label.setPixmap(QPixmap("./imagenes/4.2-cashlessSelect.jpg"))  # Imagen resaltada
        QTimer.singleShot(500, self.goToCashless)  # Espera 0.5 segundos  
       
    def returnToProductWindow(self):
        self.stacked_widget.setCurrentIndex(1)
        
    def goToCash(self):
        self.stacked_widget.setCurrentIndex(4)
        self.background_label.setPixmap(QPixmap("./imagenes/4.0-Payment.jpg"))
        
    def goToCashless(self):
        self.stacked_widget.setCurrentIndex(5)
        self.background_label.setPixmap(QPixmap("./imagenes/4.0-Payment.jpg"))
        
