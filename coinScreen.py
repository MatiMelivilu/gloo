from PySide6.QtWidgets import QLabel, QPushButton, QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont
from appValues import AppValues
from logger_config import setup_logger

logger = setup_logger()

BOTON_HIDE="background: transparent; border: none;"
#BOTON_HIDE="transparent"

class CoinScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.values = AppValues()
        self.initUI()
        
        self.values.coins_changed.connect(self.update_coin_label)
        self.values.toPay_changed.connect(self.update_toPay_label)

    def initUI(self):
        global BOTON_HIDE   
        self.setWindowTitle("Comprar Fichas")
        self.setGeometry(100, 100, 1065, 595)

        # Fondo con imagen
        self.background_label = QLabel(self)
        self.pixmap = QPixmap("./imagenes/3-NCoin.jpg")
        self.background_label.setPixmap(self.pixmap)
        self.background_label.setScaledContents(True)
        
        # Boton back
        self.bBack = QPushButton("", self)
        self.bBack.setGeometry(390, 492, 225, 55)
        self.bBack.setStyleSheet(BOTON_HIDE)  # Estilo para hacerlo invisible
        self.bBack.clicked.connect(self.returnToProductWindow)
        
        # Boton confirm
        self.bBack = QPushButton("", self)
        self.bBack.setGeometry(635, 492, 225, 55)
        self.bBack.setStyleSheet(BOTON_HIDE)  # Estilo para hacerlo invisible
        self.bBack.clicked.connect(self.goToTypePaymentWindow)

        # Boton "+"
        self.buttonPlus = QPushButton("", self)
        self.buttonPlus.setGeometry(690, 325, 60, 60)
        self.buttonPlus.setStyleSheet(BOTON_HIDE)  # Estilo para hacerlo invisible
        self.buttonPlus.clicked.connect(self.increase_coins)

         # Boton "-"
        self.buttonMinus = QPushButton("", self)
        self.buttonMinus.setGeometry(518, 325, 60, 60)
        self.buttonMinus.setStyleSheet(BOTON_HIDE)  # Estilo para hacerlo invisible
        self.buttonMinus.clicked.connect(self.decrease_coins)
        
        #Bloque variable de cantidad de fichas
        self.coins_label = QLabel(str(self.values.coins), self)
        self.coins_label.setGeometry(583,327,100,57)     
        # Cambiar el tamano y la tipografia
        font = QFont()
        font.setPointSize(30)  # Establecer el tamaoo de la fuente
        #font.setBold(True) # establecer negrita
        self.coins_label.setFont(font)
        self.coins_label.setAlignment(Qt.AlignCenter)
        self.coins_label.setStyleSheet("color: black; background-color: white; border: none;")
        
        #Bloque variable de subtotal
        self.toPay_label = QLabel(f"${str(self.values.toPay)}", self)
        self.toPay_label.setGeometry(657,415,200,40)     
        # Cambiar el tamano y la tipografia
        font2 = QFont()
        font2.setPointSize(30)  # Establecer el tamaoo de la fuente
        #font.setBold(True) # establecer negrita
        self.toPay_label.setFont(font2)
        self.toPay_label.setAlignment(Qt.AlignLeft)
        self.toPay_label.setStyleSheet("color: black; background-color: white; border: none;")

    def resizeEvent(self, event):
        size = self.size()
        self.background_label.resize(size)  # Ajusta el fondo al tamaño de la ventana
        super().resizeEvent(event)  

    def increase_coins(self):
        logger.info("incrementa en 1 ficha")
        if self.values.coins < 10:
            self.values.set_coins(self.values.coins + 1)
            monto = self.price_to_pay()
            self.values.set_toPay(monto)            
            self.price_to_pay()

    def decrease_coins(self):
        logger.info("decrementa en 1 ficha")
        if self.values.coins > 1: 
            self.values.set_coins(self.values.coins - 1)
            monto = self.price_to_pay()
            self.values.set_toPay(monto)
            
    def price_to_pay(self):
        if self.values.numPromos == 0:
            monto = self.values.coins * self.values.valor_coin
            self.values.set_cantidad_fichas(self.values.coins)
        elif self.values.numPromos == 1:
            promos = self.values.coins // self.values.nPromos
            coins = self.values.coins % self.values.nPromos
            monto = (promos * self.values.valor_promo)+(coins * self.values.valor_coin)  
            self.values.set_cantidad_fichas(coins)
            self.values.set_cantidad_promos(promos)
        logger.info(f"monto a pagar {monto}")
        return monto

    def update_coin_label(self, value):
        self.coins_label.setText(str(value))
        
    def update_toPay_label(self, value):
        self.toPay_label.setText(f"${str(value)}")

    def returnToProductWindow(self):
        logger.info("Regresando a seleccion de productos")
        self.stacked_widget.setCurrentIndex(1)
        
    def goToTypePaymentWindow(self):
        logger.info("Redirigiendo a seleccion de metodo de pagos")
        self.stacked_widget.setCurrentIndex(3)
        
