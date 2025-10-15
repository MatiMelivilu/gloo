from PySide6.QtWidgets import QLabel, QPushButton, QWidget
from PySide6.QtCore import QEvent
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QTimer
from appValues import AppValues
from logger_config import setup_logger
logger = setup_logger()

BOTON_HIDE = "background: transparent; border: none;"
#BOTON_HIDE="transparent"
class StartScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.button1 = None
        self.button2 = None
        self.initUI()

        # Variables para contar los clics
        self.config_click_count = 0
        self.config_timer = QTimer(self)
        self.config_timer.setSingleShot(True)
        self.config_timer.timeout.connect(self.reset_config_clicks)


    def go_to_idle_screen(self):
        self.inactivity_timer.stop()
        self.stacked_widget.setCurrentIndex(14)  # index del IdleVideoScreen

    def eventFilter(self, obj, event):
        # Reinicia el temporizador si detecta actividad (mouse o toque)
        if event.type() in (QEvent.MouseButtonPress, QEvent.TouchBegin):
            self.inactivity_timer.start()
        return super().eventFilter(obj, event)
                          
    def initUI(self):
        self.setWindowTitle("Gloo Car Wash")
        # Fondo con imagen
        self.label = QLabel(self)
        self.pixmap = QPixmap("./imagenes/1-Main.jpg")
        self.label.setPixmap(self.pixmap)
        self.label.setScaledContents(True)  # Importante para que se escale la imagen
        
        # Boton para cambiar de ventana 
        self.button1 = QPushButton("", self)
        self.button1.setStyleSheet(BOTON_HIDE)
        self.button1.clicked.connect(self.showProductWindow)
        
        # Boton para entrar en configuraciones (requiere 6 clics en 5 segundos)
        self.button2 = QPushButton("", self)
        self.button2.setGeometry(0, 0, 200, 200)
        self.button2.setStyleSheet(BOTON_HIDE)
        self.button2.clicked.connect(self.checkConfigAccess)

    def resizeEvent(self, event):
        size = self.size()
        self.label.resize(size)  # Ajusta el fondo al tamaño de la ventana
        if self.button1:
            btn1_width = int(size.width() * 0.85)
            btn1_height = int(size.height() * 1)
            x1 = size.width() - btn1_width - 40
            #y = size.height() - btn_height - 20
            y1 = 0
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
        logger.info("Iniciando venta. Seleccionando de productos")
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
        logger.info("Accediendo a configuracion...")
        self.stacked_widget.setCurrentIndex(8)
