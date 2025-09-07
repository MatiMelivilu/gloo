from PySide6.QtWidgets import QLabel, QPushButton, QWidget
from PySide6.QtGui import QPixmap
from appValues import AppValues

BOTON_HIDE="background: transparent; border: none;"
#BOTON_HIDE="transparent"

class ErrorScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.initUI()
                  
    def initUI(self):
        global BOTON_HIDE
        self.setWindowTitle("Gloo Car Wash")
        self.setGeometry(100, 100, 1065, 595)
        
        # Fondo con imagen
        self.label = QLabel(self)
        self.pixmap = QPixmap("./imagenes/7-payError.jpg")
        self.label.setPixmap(self.pixmap)
        self.label.setScaledContents(True)
        
        # Boton para volver
        self.button1 = QPushButton("", self)
        self.button1.setGeometry(390, 465, 235, 55)
        self.button1.setStyleSheet(BOTON_HIDE)
        self.button1.clicked.connect(self.returnToPaymentScreen)
        
        # Boton para reintentar
        self.button2 = QPushButton("", self)
        self.button2.setGeometry(645, 465, 235, 55)
        self.button2.setStyleSheet(BOTON_HIDE)
        self.button2.clicked.connect(self.returnToCashlessScreen)

    def resizeEvent(self, event):
        size = self.size()
        self.label.resize(size)  # Ajusta el fondo al tamaño de la ventana
        super().resizeEvent(event)         
   
    def returnToPaymentScreen(self):
        self.stacked_widget.setCurrentIndex(3)

    def returnToCashlessScreen(self):
        self.stacked_widget.setCurrentIndex(5)
