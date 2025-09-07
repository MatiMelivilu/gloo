from PySide6.QtWidgets import QLabel, QPushButton, QWidget
from PySide6.QtCore import Qt
from PySide6.QtCore import QTimer
from PySide6.QtGui import QPixmap, QFont
from appValues import AppValues

BOTON_HIDE = "background: transparent; border: none;"
#BOTON_HIDE="transparent"
class hopperErrorScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.values = AppValues()
        self.button1 = None
        self.button2 = None
        self.initUI()
        self.values.coins_changed.connect(self.update_coin_label)

        # Variables para contar los clics
        self.config_click_count = 0
        self.config_timer = QTimer(self)
        self.config_timer.setSingleShot(True)
        self.config_timer.timeout.connect(self.reset_config_clicks)
                  
    def initUI(self):
        self.setWindowTitle("Gloo Car Wash")
        # Fondo con imagen
        self.label = QLabel(self)
        self.pixmap = QPixmap("./imagenes/hopperError.png")
        self.label.setPixmap(self.pixmap)
        self.label.setScaledContents(True)  # Importante para que se escale la imagen
        
        # Boton para cambiar de ventana 
        self.button1 = QPushButton("", self)
        self.button1.setStyleSheet(BOTON_HIDE)
        #self.button1.clicked.connect(self.showProductWindow)
        
        # Boton para entrar en configuraciones (requiere 6 clics en 5 segundos)
        self.button2 = QPushButton("", self)
        self.button2.setGeometry(0, 0, 200, 200)
        self.button2.setStyleSheet(BOTON_HIDE)
        self.button2.clicked.connect(self.checkConfigAccess)
        
        #Valor de una ficha
        self.coins_label = QLabel(f"{str(self.values.coins)}", self)
        #self.price_label.setGeometry(187,366,143,40)     
        # Cambiar el tamano y la tipografia
        font = QFont("Poppins")
        font.setPointSize(35)  # Establecer el tamaoo de la fuente
        self.coins_label.setFont(font)
        self.coins_label.setAlignment(Qt.AlignCenter)
        self.coins_label.setStyleSheet("color: black; background-color: #FBD556; border: none;")
        self.coins_label.setGeometry(530,640,210,50) 

    def resizeEvent(self, event):
        size = self.size()
        self.label.resize(size)  # Ajusta el fondo al tamaño de la ventana
        if self.button1:
            btn1_width = int(size.width() * 0.25)
            btn1_height = int(size.height() * 0.1)
            x1 = size.width() - btn1_width - 40
            #y = size.height() - btn_height - 20
            y1 = 40
            self.button1.setGeometry(x1, y1, btn1_width, btn1_height)
            
        if self.button2:
            btn2_width = int(size.width() * 0.1)
            btn2_height = int(size.height() * 0.15)
            x2 = 0
            #y = size.height() - btn_height - 20
            y2 = 0
            self.button2.setGeometry(x2, y2, btn2_width, btn2_height)
        super().resizeEvent(event)  

    def showProductWindow(self):
        self.stacked_widget.setCurrentIndex(1)

    def checkConfigAccess(self):
        """Verifica si se ha presionado el boton 6 veces en menos de 5 segundos."""
        if self.config_click_count == 0:
            self.config_timer.start(5000)  # Iniciar temporizador de 5 segundos

        self.config_click_count += 1

        if self.config_click_count >= 6:
            self.openConfigWindow()
            self.reset_config_clicks()

    def reset_config_clicks(self):
        """Reinicia el contador de clics si pasa mas de 5 segundos."""
        self.config_click_count = 0

    def openConfigWindow(self):
        """Accion que se ejecuta al presionar 6 veces en 5 segundos."""
        print("Accediendo a configuracion...")  # Aqui puedes cambiar de ventana o abrir un cuadro de dilogo
        self.stacked_widget.setCurrentIndex(0)
        
    def update_coin_label(self, value):
        self.coins_label.setText(str(value))
