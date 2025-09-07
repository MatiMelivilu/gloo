from PySide6.QtWidgets import QLabel, QPushButton, QWidget
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QTimer, QMetaObject, Qt, Slot
from gpiozero import Device, LED, Button
from gpiozero.pins.pigpio import PiGPIOFactory
from appValues import AppValues

Device.pin_factory = PiGPIOFactory()

BOTON_HIDE2 = "background: transparent; border: none;"
BOTON_HIDE1 = "background: black; border: none;"

class SuccessScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.values = AppValues()
        self.entregados = 0
        self.hopperPIN = LED(19)
        self.hopperPIN.on()
        self.sensorPIN = Button(2, pull_up=True, bounce_time=0.05)
        self.error_timeout = 10_000  # tiempo en milisegundos
        self.succesTime = 3_000
        self.entrega_timer = QTimer(self)
        self.entrega_timer.setSingleShot(True)
        self.entrega_timer.timeout.connect(self.hopperError)
        self.succesTimer = QTimer(self)
        self.succesTimer.setSingleShot(True)
        self.succesTimer.timeout.connect(self.showProductWindow)

        self.initUI()

    def enableSensor(self):
        self.sensorPIN.when_pressed = self.entregado_gpio
        
    def disableSensor(self):
        self.sensorPIN.when_pressed = None

    def initUI(self):
        global BOTON_HIDE1
        self.setWindowTitle("Gloo Car Wash")
        self.setGeometry(100, 100, 1065, 595)

        self.label = QLabel(self)
        self.pixmap = QPixmap("./imagenes/8-paySuccess.jpg")
        self.label.setPixmap(self.pixmap)
        self.label.setGeometry(0, 0, 1065, 595)
        self.label.setScaledContents(True)

        self.button1 = QPushButton("", self)
        self.button1.setGeometry(500, 470, 255, 50)
        self.button1.setStyleSheet(BOTON_HIDE1)
        # self.button1.clicked.connect(self.showProductWindow)

    def resizeEvent(self, event):
        size = self.size()
        self.label.resize(size)
        super().resizeEvent(event)

    def showProductWindow(self):
        self.hopperPIN.on()
        self.stacked_widget.setCurrentIndex(0)

    def showErrorWindow(self):
        self.hopperPIN.on()
        self.stacked_widget.setCurrentIndex(9)

    def entregado_gpio(self):
        # Esta funcion se ejecuta en un hilo externo
        # Redirigimos al hilo principal usando invokeMethod
        QMetaObject.invokeMethod(self, "entregado", Qt.QueuedConnection)

    @Slot()
    def entregado(self):
        self.entregados += 1
        print('ficha entregada', self.entregados)
        self.entrega_timer.start(self.error_timeout)  # reinicia el timer

        if self.entregados == self.values.coins:
            self.entrega_timer.stop()
            self.entregados = 0
            self.hopperPIN.on()
            self.disableSensor()
            self.values.set_Pay(0)
            self.button1.setStyleSheet(BOTON_HIDE2)
            self.succesTimer.start(self.succesTime)
            #self.button1.clicked.connect(self.showProductWindow)

    def entregaFichas(self):
        self.enableSensor()
        self.entregados = 0
        self.button1.setStyleSheet(BOTON_HIDE1)
        self.values.set_Pay(0)
        self.hopperPIN.off()
        self.entrega_timer.start(self.error_timeout)  # inicia el timer

    def hopperError(self):
        print("Error: No se detectaron fichas a tiempo.")
        self.values.set_Pay(0)
        self.hopperPIN.on()
        self.showErrorWindow()

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(1000, self.entregaFichas)
