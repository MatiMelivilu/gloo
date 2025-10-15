from PySide6.QtWidgets import QLabel, QPushButton, QWidget, QHBoxLayout, QVBoxLayout
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QFont
from PySide6.QtCore import QTimer
from appValues import AppValues


BOTON_HIDE="background: transparent; border: none;"
#BOTON_HIDE="transparent"

class ProductScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.values = AppValues()
        self.button1 = None
        self.button2 = None
        self.button3 = None
        self.button4 = None     
        self.button5 = None  
        self.price_label = None 
        self.price2_label= None
        self.price3_label= None
        self.initUI()
        self.values.valor_coin_changed.connect(self.update_valor_coin_label)
        self.values.valor_promo_changed.connect(self.update_valor_promo_label)
        self.values.nPromo_changed.connect(self.update_nPromos_label)
        self.values.numPromos_changed.connect(self.update_numPromos_label)
           
    def initUI(self):
        global BOTON_HIDE
        self.setWindowTitle("Comprar Fichas")
        self.setGeometry(100, 100, 1065, 595)
        
        # Fondo con imagen
        self.label = QLabel(self)
        if self.values.numPromos == 0:
            self.pixmap = QPixmap("./imagenes/2.0.1-Promos.jpg")
        elif self.values.numPromos == 1:
            self.pixmap = QPixmap("./imagenes/2.0-Promos.jpg")
        elif self.values.numPromos == 2:
            self.pixmap = QPixmap("./imagenes/2.0-Promos.jpg")
        self.label.setPixmap(self.pixmap)
        self.label.setScaledContents(True)  # Importante para que se escale la imagen
        
        # Boton de 1 ficha
        self.button1 = QPushButton("", self)
        self.button1.setStyleSheet(BOTON_HIDE)  # Estilo para hacerlo invisible
        self.button1.clicked.connect(self.SelectCoin1)
        
        # Boton de 2 fichas
        self.button2 = QPushButton("", self)
        self.button2.setStyleSheet(BOTON_HIDE)  # Estilo para hacerlo invisible
        self.button2.clicked.connect(self.SelectCoin2)
        
        # Boton de Promo
        self.button3 = QPushButton("", self)
        self.button3.setStyleSheet(BOTON_HIDE)  # Estilo para hacerlo invisible
        self.button3.clicked.connect(self.SelectCoinPromo)
        
        # Boton de otro monto
        self.button4 = QPushButton("", self)
        self.button4.setStyleSheet(BOTON_HIDE)  # Estilo para hacerlo invisible
        self.button4.clicked.connect(self.SelectCoin)
        
        # Boton de regreso
        self.button5 = QPushButton("", self)
        self.button5.setStyleSheet(BOTON_HIDE)  # Estilo para hacerlo invisible
        self.button5.clicked.connect(self.returnToMainWindow)
        
        #Valor de una ficha
        self.price_label = QLabel(f"${str(self.values.valor_coin)}", self)
        #self.price_label.setGeometry(187,366,143,40)     
        # Cambiar el tamano y la tipografia
        font = QFont("Poppins")
        font.setPointSize(25)  # Establecer el tamaoo de la fuente
        font2 = QFont("Poppins")
        font2.setPointSize(22)  # Establecer el tamaoo de la fuente
        self.price_label.setFont(font)
        self.price_label.setAlignment(Qt.AlignCenter)
        self.price_label.setStyleSheet("color: black; background-color: white; border: none;")
        self.price_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        #Valor de 2 ficha
        self.price2_label = QLabel(f"${str(self.values.valor_coin*2)}", self)    
        self.price2_label.setFont(font)
        self.price2_label.setAlignment(Qt.AlignCenter)
        self.price2_label.setStyleSheet("color: black; background-color: white; border: none;") 
        self.price2_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)       

        #Valor de promo
        if self.values.numPromos == 0:
            self.price3_label = QLabel(f"{str(self.values.nPromos)}X\n${str(self.values.valor_promo)}", self)    
            self.price3_label.setFont(font2)
            self.price3_label.setAlignment(Qt.AlignCenter)
            self.price3_label.setStyleSheet("color: transparent; background-color: transparent; border: none;") 
        elif self.values.numPromos == 1: 
            self.price3_label = QLabel(f"{str(self.values.nPromos)}X\n${str(self.values.valor_promo)}", self)    
            self.price3_label.setFont(font2)
            self.price3_label.setAlignment(Qt.AlignCenter)
            self.price3_label.setStyleSheet("color: black; background-color: white; border: none;")   

        elif self.values.numPromos == 2: 
            self.price3_label = QLabel(f"", self)    
            self.price3_label.setFont(font2)
            self.price3_label.setAlignment(Qt.AlignCenter)
            self.price3_label.setStyleSheet("color: black; background-color: white; border: none;")
        self.price3_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)   
       
    def resizeEvent(self, event):
        size = self.size()
        self.label.resize(size)  # Ajusta el fondo al tamaño de la ventana
        if self.button1:
            btn1_width = int(size.width() * 0.14)
            btn1_height = int(size.height() * 0.25)
            x1 = size.width() - btn1_width - 880
            y1 = size.height() - btn1_height - 195
            self.button1.setGeometry(x1, y1, btn1_width, btn1_height)
            
        if self.button2:
            btn2_width = int(size.width() * 0.14)
            btn2_height = int(size.height() * 0.25)
            x2 = size.width() - btn2_width - 660
            y2 = size.height() - btn2_height - 195
            self.button2.setGeometry(x2, y2, btn2_width, btn2_height)

        if self.button3:
            btn3_width = int(size.width() * 0.14)
            btn3_height = int(size.height() * 0.25)
            x3 = size.width() - btn3_width - 440
            y3 = size.height() - btn3_height - 195
            self.button3.setGeometry(x3, y3, btn3_width, btn3_height)
            
        if self.button4:
            btn4_width = int(size.width() * 0.14)
            btn4_height = int(size.height() * 0.25)
            x4 = size.width() - btn4_width - 220
            y4 = size.height() - btn4_height - 195
            self.button4.setGeometry(x4, y4, btn4_width, btn4_height)           

        if self.button5:
            btn5_width = int(size.width() * 0.06)
            btn5_height = int(size.height() * 0.1)
            x5 = size.width() - btn5_width - 1165
            y5 = size.height() - btn5_height - 610
            self.button5.setGeometry(x5, y5, btn5_width, btn5_height)  
            
        if self.price_label:
            label1_width = int(size.width() * 0.13)
            label1_height = int(size.height() * 0.1)
            xl1 = size.width() - label1_width - 886
            yl1 = size.height() - label1_height - 210
            self.price_label.setGeometry(xl1, yl1, label1_width, label1_height) 

        if self.price2_label:
            label2_width = int(size.width() * 0.13)
            label2_height = int(size.height() * 0.1)
            xl2 = size.width() - label2_width - 667
            yl2 = size.height() - label2_height - 209
            self.price2_label.setGeometry(xl2, yl2, label2_width, label2_height) 

        if self.price3_label:
            label3_width = int(size.width() * 0.13)
            label3_height = int(size.height() * 0.09)
            xl3 = size.width() - label3_width - 454
            yl3 = size.height() - label3_height - 210
            self.price3_label.setGeometry(xl3, yl3, label3_width, label3_height) 
                                  
        super().resizeEvent(event)      
            
    def SelectCoin1(self):
        self.values.set_cantidad_fichas(1)
        self.values.set_cantidad_promos(0)
        self.values.set_coins(1)
        self.values.set_toPay(self.values.valor_coin * self.values.coins)
          # Imagen resaltada
        if self.values.numPromos == 0:
            self.label.setPixmap(QPixmap("./imagenes/2.1.1-fichas1.jpg"))
        elif self.values.numPromos == 1:
            self.label.setPixmap(QPixmap("./imagenes/2.1-fichas1.jpg")) 
        elif self.values.numPromos == 2:
            self.label.setPixmap(QPixmap("./imagenes/2.1-fichas1.jpg"))       
        self.price_label.setStyleSheet("color: black; background-color: #FBD556; border: none;") 
        QTimer.singleShot(500, self.showPaymentWindow)  # Espera 0.5 segundos    
        
    def SelectCoin2(self):
        self.values.set_cantidad_fichas(2)
        self.values.set_cantidad_promos(0)
        self.values.set_coins(2)
        self.values.set_toPay(self.values.valor_coin * self.values.coins)
        if self.values.numPromos == 0:
            self.label.setPixmap(QPixmap("./imagenes/2.2.1-fichas2.jpg"))
        elif self.values.numPromos == 1:
            self.label.setPixmap(QPixmap("./imagenes/2.2-fichas2.jpg"))
        elif self.values.numPromos == 2:
            self.label.setPixmap(QPixmap("./imagenes/2.2-fichas2.jpg"))
        self.price2_label.setStyleSheet("color: black; background-color: #FBD556; border: none;")
        QTimer.singleShot(500, self.showPaymentWindow)  # Espera 0.5 segundos  

    def SelectCoinPromo(self):
        if self.values.numPromos == 0:
            self.label.setPixmap(QPixmap("./imagenes/2.0.1-Promos.jpg"))
        elif self.values.numPromos == 1:
            self.values.set_cantidad_promos(1)
            self.values.set_cantidad_fichas(0)
            self.values.set_coins(self.values.nPromos)
            self.values.set_toPay(self.values.valor_promo)
            self.label.setPixmap(QPixmap("./imagenes/2.3-Promo.jpg"))  # Imagen resaltada
            self.price3_label.setStyleSheet("color: black; background-color: #FBD556; border: none;")
            QTimer.singleShot(500, self.showPaymentWindow)  # Espera 0.5 segundos  
        elif self.values.numPromos == 2:
            self.label.setPixmap(QPixmap("./imagenes/2.3-Promo.jpg"))  # Imagen resaltada
            self.price3_label.setStyleSheet("color: black; background-color: #FBD556; border: none;")
            QTimer.singleShot(500, self.empyFunction)  # Espera 0.5 segundos  
            
    def SelectCoin(self):
        if self.values.numPromos == 0:
            self.label.setPixmap(QPixmap("./imagenes/2.4.1-otro.jpg"))
        elif self.values.numPromos == 1:
           self.label.setPixmap(QPixmap("./imagenes/2.4-otro.jpg"))
        elif self.values.numPromos == 2:
           self.label.setPixmap(QPixmap("./imagenes/2.4-otro.jpg"))
        QTimer.singleShot(500, self.showCoinWindow)  # Espera 0.5 segundos  

    def showPaymentWindow(self):
        self.stacked_widget.setCurrentIndex(3)
        if self.values.numPromos == 0:
            self.label.setPixmap(QPixmap("./imagenes/2.0.1-Promos.jpg"))
        elif self.values.numPromos == 1:
            self.label.setPixmap(QPixmap("./imagenes/2.0-Promos.jpg")) 
            self.price3_label.setStyleSheet("color: black; background-color: white; border: none;")
        elif self.values.numPromos == 2:
            self.label.setPixmap(QPixmap("./imagenes/2.0-Promos.jpg"))
            self.price3_label.setStyleSheet("color: black; background-color: white; border: none;") 
        self.price_label.setStyleSheet("color: black; background-color: white; border: none;") 
        self.price2_label.setStyleSheet("color: black; background-color: white; border: none;") 
        
           
    def showCoinWindow(self):
        self.stacked_widget.setCurrentIndex(2)
        if self.values.numPromos == 0:
            self.label.setPixmap(QPixmap("./imagenes/2.0.1-Promos.jpg"))
        elif self.values.numPromos == 1:
            self.label.setPixmap(QPixmap("./imagenes/2.0-Promos.jpg")) 
        elif self.values.numPromos == 2:
            self.label.setPixmap(QPixmap("./imagenes/2.0-Promos.jpg"))         
    def update_valor_coin_label(self, value):
        self.price_label.setText(f"${str(value)}")
        self.price2_label.setText(f"${str(value*2)}")
        
    def update_valor_promo_label(self, value):
        self.price3_label.setText(f"{str(self.values.nPromos)}X\n${str(self.values.valor_promo)}")
        
    def update_nPromos_label(self, value):
        self.price3_label.setText(f"{str(self.values.nPromos)}X\n${str(self.values.valor_promo)}")

    def update_numPromos_label(self):
        if self.values.numPromos == 0:
            self.label.setPixmap(QPixmap("./imagenes/2.0.1-Promos.jpg"))
            self.price3_label.setStyleSheet("color: transparent; background-color: transparent; border: none;") 
        elif self.values.numPromos == 1:
            self.label.setPixmap(QPixmap("./imagenes/2.0-Promos.jpg"))
            self.price3_label.setStyleSheet("color: black; background-color: white; border: none;") 
            self.price3_label.setText(f"{str(self.values.nPromos)}X\n${str(self.values.valor_promo)}")
        elif self.values.numPromos == 2:
            self.label.setPixmap(QPixmap("./imagenes/2.0-Promos.jpg"))
            self.price3_label.setStyleSheet("color: black; background-color: white; border: none;") 
            self.price3_label.setText(f"")
            
    def empyFunction(self):
        pass
        
    def returnToMainWindow(self):
        self.stacked_widget.setCurrentIndex(0)
