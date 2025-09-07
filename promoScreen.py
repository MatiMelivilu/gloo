from PySide6.QtWidgets import QLabel, QPushButton, QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont

#BOTON_HIDE="background: transparent; border: none;"
BOTON_HIDE="transparent"

class PromoScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Comprar Fichas")
        self.setGeometry(100, 100, 1065, 595)

        # Fondo con imagen
        self.background_label = QLabel(self)
        self.background_label.setPixmap(QPixmap("./imagenes/Gloo Interface 2.0_page-0006.jpg"))
        self.background_label.setGeometry(0, 0, 1065, 595)
        self.background_label.setScaledContents(True)
        
        # Boton back
        self.bBack = QPushButton("", self)
        self.bBack.setGeometry(335, 445, 190, 45)
        self.bBack.setStyleSheet(BOTON_HIDE)  # Estilo para hacerlo invisible
        self.bBack.clicked.connect(self.returnToProductWindow)
        
        # Boton confirm
        self.bBack = QPushButton("", self)
        self.bBack.setGeometry(535, 445, 190, 45)
        self.bBack.setStyleSheet(BOTON_HIDE)  # Estilo para hacerlo invisible
        self.bBack.clicked.connect(self.goToTypePaymentWindow)
        

    def returnToProductWindow(self):
        self.stacked_widget.setCurrentIndex(1)
        
    def goToTypePaymentWindow(self):
        self.stacked_widget.setCurrentIndex(0)
