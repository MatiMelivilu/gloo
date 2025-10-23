from PySide6.QtWidgets import QLabel, QPushButton, QWidget
from PySide6.QtGui import QPixmap
from PySide6.QtCore import QTimer, QMetaObject, Qt, Slot
from gpiozero import Device, LED, Button
from gpiozero.pins.pigpio import PiGPIOFactory
from appValues import AppValues
from datetime import date
from datetime import datetime
from zeep import Client
from escpos.printer import Usb
from pdf417gen import encode, render_image
from PIL import Image
import base64
import xml.etree.ElementTree as ET
import subprocess
import time
from logger_config import setup_logger
from facturacion_manager import FacturacionManager
from PySide6.QtCore import QThread

logger = setup_logger()

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
        self.sensorPIN = Button(2, bounce_time=0.05)
        self.error_timeout = 10_000  # tiempo en milisegundos
        self.succesTime = 3_000
        self.entrega_timer = QTimer(self)
        self.entrega_timer.setSingleShot(True)
        self.entrega_timer.timeout.connect(self.hopperError)
        self.succesTimer = QTimer(self)
        self.succesTimer.setSingleShot(True)
        self.succesTimer.timeout.connect(self.showProductWindow)
        self.boleta_en_proceso = False
        self.initUI()
        # === Configuración del generador de boletas (en hilo separado) ===
        self.boleta_thread = QThread()
        self.facturacion = FacturacionManager(queue_dir="/home/IdeasDigitales/gloo/boletas_queue")
        self.facturacion.moveToThread(self.boleta_thread)
        self.boleta_thread.start()

        # Señales informativas (opcional)
        self.facturacion.started.connect(lambda ctx: logger.info(f"Iniciando boleta: {ctx}"))
        self.facturacion.finished.connect(lambda ctx: logger.info(f"Boleta finalizada: {ctx}"))
        self.facturacion.error.connect(lambda code, ctx: logger.warning(f"Error boleta: {code} - {ctx}"))


    def enableSensor(self):
        logger.info("Habilitando sensor de entrega de fichas")
        self.sensorPIN.when_pressed = self.entregado_gpio
        
    def disableSensor(self):
        logger.info("Deshabilitando sensor de entrega de fichas")
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
        logger.info("Desactivando hopper")
        logger.info("Regresando a pantalla principal")
        self.values.set_Pay(0)
        self.stacked_widget.setCurrentIndex(0)

    def showErrorWindow(self):
        self.hopperPIN.on()
        logger.info("Desactivando hopper")
        self.values.set_Pay(0)
        self.stacked_widget.setCurrentIndex(9)

    def entregado_gpio(self):
        # Esta funcion se ejecuta en un hilo externo
        # Redirigimos al hilo principal usando invokeMethod
        QMetaObject.invokeMethod(self, "entregado", Qt.QueuedConnection)

    @Slot()
    def entregado(self):
        if self.boleta_en_proceso:
            return  # evitar reentrada
            
        self.entregados += 1
        print('ficha entregada', self.entregados)
        logger.info(f"Fichas entregadas {self.entregados}")
        self.entrega_timer.start(self.error_timeout)  # reinicia el timer

        if self.entregados == self.values.coins:
            logger.info("Entrega de fichas completa")
            self.boleta_en_proceso = True  # << Bloqueo
            self.entrega_timer.stop()

            self.entregados = 0
            self.hopperPIN.on()
            logger.info("Desactivando hopper")
            self.disableSensor()
            self.button1.setStyleSheet(BOTON_HIDE2)
            self.succesTimer.start(self.succesTime)
            #self.button1.clicked.connect(self.showProductWindow)
            try:
                print("generarndo boleta")
                logger.info("Generando boleta")
                exito = generar_y_enviar_boleta(self.values.Pay, self.values.coins, self.values.valor_coin)
                if not exito:
                    logger.warning("⚠️ Boleta no generada o no impresa, continuando sin bloqueo.")
            except Exception as e:
                print("Falla al emitir boleta")
                logger.error(f"Falla al emitir boleta {e}")
            finally:
                self.boleta_en_proceso = False  # << Libera bloqueo después
                
    """
    def entregaFichas(self):
        tFichas = self.values.cantidad_fichas_total + self.values.cantidad_fichas
        self.values.set_cantidad_fichas_total(tFichas)
        tPromos = self.values.cantidad_promos_total + self.values.cantidad_promos
        self.values.set_cantidad_promos_total(tPromos)
        self.enableSensor()
        self.entregados = 0
        self.button1.setStyleSheet(BOTON_HIDE1)
        self.hopperPIN.off()
        logger.info("Activando hopper")
        self.entrega_timer.start(self.error_timeout)  # inicia el timer
    """
    
    def entregaFichas(self):
        tFichas = self.values.cantidad_fichas_total + self.values.cantidad_fichas
        self.values.set_cantidad_fichas_total(tFichas)
        tPromos = self.values.cantidad_promos_total + self.values.cantidad_promos
        self.values.set_cantidad_promos_total(tPromos)

        self.enableSensor()
        self.entregados = 0
        self.button1.setStyleSheet(BOTON_HIDE1)
        self.hopperPIN.off()  # ← Activa el hopper
        logger.info("Activando hopper")
        self.entrega_timer.start(self.error_timeout)

        # === Inicia la generación de boleta en paralelo ===
        payload = {
            'monto_pagado': self.values.Pay,
            'cantidad_fichas': self.values.coins,
            'valor_unitario': self.values.valor_coin
        }
        logger.info("Iniciando generación de boleta en paralelo al hopper")
        self.facturacion.generate_and_print.emit(payload)
        self.values.set_Pay(0)

    def hopperError(self):
        print("Error: No se detectaron fichas a tiempo.")
        logger.error("Error: No se detectaron fichas a tiempo.")
        #print(self.values.folio)
        #self.values.set_Pay(0)
        self.hopperPIN.on()
        logger.info("Desactivando hopper")
        self.showErrorWindow()

    def showEvent(self, event):
        super().showEvent(event)
        QTimer.singleShot(1000, self.entregaFichas)
        

        
