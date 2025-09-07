from PySide6.QtWidgets import QLabel, QPushButton, QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import QTimer
from appValues import AppValues


BOTON_HIDE="background: transparent; border: none;"
#BOTON_HIDE="transparent"

class MenuConfigScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.values = AppValues()
        self.button1 = None
        self.button2 = None
        self.button3 = None
        self.button4 = None     
        self.button5 = None  
        self.initUI()
    def initUI(self):
        global BOTON_HIDE        
        # Fondo con imagen
        self.label = QLabel(self)

        self.pixmap = QPixmap("./imagenes/C2.0-options.jpg")
        self.label.setPixmap(self.pixmap)
        self.label.setScaledContents(True)  # Importante para que se escale la imagen
        
        # Boton de 1 ficha
        self.button1 = QPushButton("", self)
        self.button1.setStyleSheet(BOTON_HIDE)  # Estilo para hacerlo invisible
        self.button1.clicked.connect(self.SelectPrecio)
        
        # Boton de 2 fichas
        self.button2 = QPushButton("", self)
        self.button2.setStyleSheet(BOTON_HIDE)  # Estilo para hacerlo invisible
        self.button2.clicked.connect(self.SelectHistorial)
        
        # Boton de Promo
        self.button3 = QPushButton("", self)
        self.button3.setStyleSheet(BOTON_HIDE)  # Estilo para hacerlo invisible
        self.button3.clicked.connect(self.SelectPOS)
        
        # Boton de otro monto
        self.button4 = QPushButton("", self)
        self.button4.setStyleSheet(BOTON_HIDE)  # Estilo para hacerlo invisible
        self.button4.clicked.connect(self.SelectPulsos)
        
        # Boton de regreso
        self.button5 = QPushButton("", self)
        self.button5.setStyleSheet(BOTON_HIDE)  # Estilo para hacerlo invisible
        self.button5.clicked.connect(self.returnToMainWindow)
        
        
    def resizeEvent(self, event):
        size = self.size()
        self.label.resize(size)  # Ajusta el fondo al tamaño de la ventana
        if self.button1:
            btn1_width = int(size.width() * 0.19)
            btn1_height = int(size.height() * 0.1)
            x1 = size.width() - btn1_width - 927
            y1 = size.height() - btn1_height - 250
            self.button1.setGeometry(x1, y1, btn1_width, btn1_height)
            
        if self.button2:
            btn2_width = int(size.width() * 0.19)
            btn2_height = int(size.height() * 0.1)
            x2 = size.width() - btn2_width - 655
            y2 = size.height() - btn2_height - 250
            self.button2.setGeometry(x2, y2, btn2_width, btn2_height)

        if self.button3:
            btn3_width = int(size.width() * 0.19)
            btn3_height = int(size.height() * 0.1)
            x3 = size.width() - btn3_width - 383
            y3 = size.height() - btn3_height - 250
            self.button3.setGeometry(x3, y3, btn3_width, btn3_height)
            
        if self.button4:
            btn4_width = int(size.width() * 0.19)
            btn4_height = int(size.height() * 0.1)
            x4 = size.width() - btn4_width - 110
            y4 = size.height() - btn4_height - 250
            self.button4.setGeometry(x4, y4, btn4_width, btn4_height)           

        if self.button5:
            btn5_width = int(size.width() * 0.06)
            btn5_height = int(size.height() * 0.1)
            x5 = size.width() - btn5_width - 1165
            y5 = size.height() - btn5_height - 610
            self.button5.setGeometry(x5, y5, btn5_width, btn5_height)  
                                   
        super().resizeEvent(event)      
            
    def SelectPrecio(self):
        self.label.setPixmap(QPixmap("./imagenes/C2.1-priceSelect.jpg"))
        QTimer.singleShot(500, self.showPriceConfig)  # Espera 0.5 segundos    
        
    def SelectHistorial(self):
        self.label.setPixmap(QPixmap("./imagenes/C2.2-historicalSelect.jpg"))
        QTimer.singleShot(500, self.showHistorialWindow)  # Espera 0.5 segundos 

    def SelectPOS(self):
        self.label.setPixmap(QPixmap("./imagenes/C2.3-posSelect.jpg"))
        QTimer.singleShot(500, self.showPOSConfig)  # Espera 0.5 segundos 
    def SelectPulsos(self):
        self.label.setPixmap(QPixmap("./imagenes/C2.4-precioPulsos.jpg"))
        #QTimer.singleShot(500, self.showPaymentWindow)  # Espera 0.5 segundos 

    def showPriceConfig(self):
        self.stacked_widget.setCurrentIndex(11)
        self.label.setPixmap(QPixmap("./imagenes/C2.0-options.jpg"))

    def showPOSConfig(self):
        self.stacked_widget.setCurrentIndex(13)
        self.label.setPixmap(QPixmap("./imagenes/C2.0-options.jpg"))        
           
    def showHistorialWindow(self):
        self.stacked_widget.setCurrentIndex(12)
        self.label.setPixmap(QPixmap("./imagenes/C2.0-options.jpg"))           
                           
    def returnToMainWindow(self):
        self.stacked_widget.setCurrentIndex(0)
