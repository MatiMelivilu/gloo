from PySide6.QtWidgets import QLabel, QPushButton, QWidget, QVBoxLayout
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QPixmap, QFont
from appValues import AppValues
import serial
import time
from datetime import date
from datetime import datetime
from gpiozero import Device, LED, Button
from gpiozero.pins.pigpio import PiGPIOFactory
from datetime import date
from zeep import Client
from escpos.printer import Usb
from pdf417gen import encode, render_image
from PIL import Image
import base64
import xml.etree.ElementTree as ET
import subprocess
from logger_config import setup_logger

logger = setup_logger()

Device.pin_factory = PiGPIOFactory()
PORT = '/dev/ttyUSB0'
BAUDRATE = 9600
COIN_ADDR = 2
BILL_ADDR = 40
HOST_ADDR = 1

BOTON_HIDE = "background: transparent; border: none;"

def checksum(msg):
    return (256 - sum(msg)) % 256


def build_packet(addr, cmd, data=[]):
    packet = [addr, len(data), HOST_ADDR, cmd] + data
    packet.append(checksum(packet))
    return bytes(packet)


class CoinReaderThread(QThread):
    coin_inserted = Signal(int)

    def __init__(self, gpio_config=None):
        super().__init__()
        self._running = True
        self.values = AppValues()
        self.ser = None
        self.last_coin_counter = 0
        self.last_bill_counter = 0

    # -------------------------------
    #  Conexion persistente
    # -------------------------------
    def connect_serial(self):
        """
        Intenta conectar al puerto serial persistentemente.
        """
        while self._running and self.ser is None:
            try:
                self.ser = serial.Serial(PORT, BAUDRATE, timeout=1)
                print("? Conectado a", PORT)
                self.enable_monedero()
                self.last_coin_counter = self.initialize_counter()
                self.last_bill_counter = self.initialize_counterBILL()
                print("Counters iniciales:", self.last_coin_counter, self.last_bill_counter)
                break
            except serial.SerialException as e:
                print("?? Error al conectar:", e)
                self.ser = None
                time.sleep(2)

    def reconnect_if_needed(self):
        """
        Verifica que la conexion siga activa.
        Si no, intenta reconectarse.
        """
        if not self.ser or not self.ser.is_open:
            print("? Reconectando al puerto serial...")
            logger.info("? Reconectando al puerto serial...")
            self.ser = None
            self.connect_serial()

    # -------------------------------
    #  Inicializacion
    # -------------------------------
    def initialize_counter(self):
        if not self.ser:
            return 0
        logger.info("inicializando contador de monedero")
        self.ser.reset_input_buffer()
        self.ser.write(build_packet(COIN_ADDR, 229))
        time.sleep(0.2)
        raw = self.ser.read(16)
        if raw and len(raw) >= 10:
            return raw[9]
        return 0

    def initialize_counterBILL(self):
        if not self.ser:
            return 0
        logger.info("inicializando contador de billetero")
        self.ser.reset_input_buffer()
        self.ser.write(build_packet(BILL_ADDR, 159))
        time.sleep(0.2)
        raw = self.ser.read(16)
        if raw and len(raw) >= 10:
            return raw[9]
        return 0

    # -------------------------------
    #  Habilitacion / deshabilitacion
    # -------------------------------
    def enable_monedero(self):
        if not self.ser:
            return
        print("? Habilitando monedero y billetero...")
        logger.info("? Habilitando monedero y billetero...")
        self.ser.reset_input_buffer()
        try:
            # Monedero
            self.ser.write(build_packet(COIN_ADDR, 2))
            time.sleep(0.15)
            self.ser.write(build_packet(COIN_ADDR, 245))
            time.sleep(0.15)
            self.ser.write(build_packet(COIN_ADDR, 230))
            time.sleep(0.15)
            self.ser.write(build_packet(COIN_ADDR, 231, [255, 255]))
            time.sleep(0.15)

            # Billetero
            self.ser.write(build_packet(BILL_ADDR, 147, [0]))
            time.sleep(0.15)
            self.ser.write(build_packet(BILL_ADDR, 232, [0]))
            time.sleep(0.15)
            self.ser.write(build_packet(BILL_ADDR, 228, [1]))
            time.sleep(0.15)

            # Determina que billetes habilitar segun el monto
            print('Monto a pagar:', self.values.toPay)
            logger.info(f"monto a pagar: {self.values.toPay}")
            val = 0
            if self.values.toPay < 1000:
                val = 0
            elif self.values.toPay < 2000:
                val = 1
            elif self.values.toPay < 5000:
                val = 3
            elif self.values.toPay < 10000:
                val = 7
            elif self.values.toPay < 20000:
                val = 15

            self.ser.write(build_packet(BILL_ADDR, 231, [val, 0]))
            print('? Billetero habilitado con codigo:', val)
            time.sleep(0.15)
            _ = self.ser.read(16)

        except serial.SerialException as e:
            print("? Error al habilitar dispositivos:", e)

    def disable_monedero(self):
        if not self.ser:
            return
        print("? Deshabilitando monedero y billetero...")
        logger.info("? Deshabilitando monedero y billetero...")
        try:
            # Monedero OFF
            self.ser.write(build_packet(COIN_ADDR, 231, [0, 0]))
            time.sleep(0.15)
            # Billetero OFF
            self.ser.write(build_packet(BILL_ADDR, 231, [0, 0]))
            time.sleep(0.15)
        except Exception as e:
            print("Error al deshabilitar dispositivos:", e)
            logger.error("Error al deshabilitar dispositivos")

    # -------------------------------
    #  Ciclo principal
    # -------------------------------
    def run(self):
        state = 0
        self.connect_serial()

        while self._running:
            self.reconnect_if_needed()

            if not self.ser:
                time.sleep(1)
                continue

            try:
                self.ser.reset_input_buffer()
                if state == 0:
                    self.ser.write(build_packet(COIN_ADDR, 229))
                    state = 1
                else:
                    self.ser.write(build_packet(BILL_ADDR, 159))
                    state = 0

                time.sleep(0.15)
                raw = self.ser.read(16)

                if raw and len(raw) >= 11:
                    dispositivo = raw[7]
                    evento = raw[9]
                    tipo = raw[10]
                    ecrow = raw[11]

                    if dispositivo == COIN_ADDR:
                        if evento != self.last_coin_counter:
                            self.last_coin_counter = evento
                            valor = self.map_coin(tipo)
                            if valor > 0:
                                logger.info(f"Moneda de {valor} ingresada")
                                self.coin_inserted.emit(valor)

                    elif dispositivo == BILL_ADDR:
                        if evento != self.last_bill_counter:
                            self.last_bill_counter = evento
                            if ecrow == 1:
                                valor = self.map_bill(tipo)
                                if valor > 0:
                                    logger.info(f"Billete de {valor} ingresado")
                                    self.ser.write(build_packet(BILL_ADDR, 154, [1]))
                                    self.coin_inserted.emit(valor)

            except serial.SerialException as e:
                print("?? Error de comunicacion, reintentando:", e)
                logger.error("?? Error de comunicacion, reintentando")
                self.ser = None
                time.sleep(2)

            time.sleep(0.15)

    # -------------------------------
    #  Stop / limpieza
    # -------------------------------
    def stop(self):
        self._running = False
        self.disable_monedero()
        print("? Lectura detenida (sin cerrar puerto).")
        logger.info("? Lectura detenida (sin cerrar puerto).")

    # -------------------------------
    #  Mapeos
    # -------------------------------
    def map_coin(self, tipo):
        return {
            1: 10,
            2: 50,
            3: 100,
            4: 100,
            5: 500
        }.get(tipo, 0)

    def map_bill(self, tipo):
        return {
            1: 1000,
            2: 2000,
            3: 5000,
            4: 10000,
            5: 20000
        }.get(tipo, 0)

class CashScreen(QWidget):
    def __init__(self, stacked_widget, gpio_config):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.values = AppValues()
        self.gpio_config = gpio_config
        self.coin_thread = None
        self.initUI()
        self.values.toPay_changed.connect(self.update_toPay_label)
        self.values.Pay_changed.connect(self.update_Pay_label)

    # -------------------------
    # Interfaz
    # -------------------------
    def initUI(self):
        self.setWindowTitle("Comprar Fichas")
        self.setGeometry(100, 100, 1065, 595)

        # Fondo
        self.background_label = QLabel(self)
        pixmap = QPixmap("./imagenes/5-coinInsert.jpg")
        self.background_label.setPixmap(pixmap)
        self.background_label.setScaledContents(True)

        # Boton volver
        self.bBack = QPushButton("", self)
        self.bBack.setGeometry(35, 35, 75, 75)
        self.bBack.setStyleSheet(BOTON_HIDE)
        self.bBack.clicked.connect(self.returnToProductWindow)

        # Labels de monto
        font = QFont()
        font.setPointSize(30)

        self.toPay_label = QLabel(f"${str(self.values.toPay)}", self)
        self.toPay_label.setGeometry(552, 357, 210, 50)
        self.toPay_label.setFont(font)
        self.toPay_label.setAlignment(Qt.AlignLeft)
        self.toPay_label.setStyleSheet("color: black; background-color: white; border: none;")

        self.Pay_label = QLabel(f"${str(self.values.Pay)}", self)
        self.Pay_label.setGeometry(700, 445, 210, 50)
        self.Pay_label.setFont(font)
        self.Pay_label.setAlignment(Qt.AlignLeft)
        self.Pay_label.setStyleSheet("color: black; background-color: white; border: none;")

    def resizeEvent(self, event):
        size = self.size()
        self.background_label.resize(size)
        super().resizeEvent(event)

    # -------------------------
    # Actualizaciones visuales
    # -------------------------
    def update_toPay_label(self, value):
        self.toPay_label.setText(f"${str(value)}")

    def update_Pay_label(self, value):
        self.Pay_label.setText(f"${str(value)}")

    # -------------------------
    # Eventos de pantalla
    # -------------------------
    def showEvent(self, event):
        super().showEvent(event)
        self.values.set_Pay(0)
        QTimer.singleShot(1000, self.payCash)

    def hideEvent(self, event):
        super().hideEvent(event)
        self.stopCashReader()

    def returnToProductWindow(self):
        logger.info("Regresando a la ventana de seleccion de tipo de pago")
        self.stopCashReader()
        self.stacked_widget.setCurrentIndex(3)

    # -------------------------
    # Control del lector
    # -------------------------
    def payCash(self):
        """
        Inicia el hilo del lector de monedas/billetes si no esta corriendo.
        """
        if self.coin_thread is None:
            self.coin_thread = CoinReaderThread(self.gpio_config)
            self.coin_thread.coin_inserted.connect(self.update_payment)
            self.coin_thread.start()

    def stopCashReader(self):
        """
        Detiene el hilo de lectura sin cerrar la conexion fisica.
        """
        if self.coin_thread:
            print("? Deteniendo lector de efectivo (sin cerrar conexion).")
            logger.info("? Deteniendo lector de efectivo (sin cerrar conexion)")
            self.coin_thread.stop()  # Ahora solo deshabilita billetero/monedero
            self.coin_thread.wait(1000)
            self.coin_thread = None


    # -------------------------
    # Logica de pago
    # -------------------------
    def update_payment(self, amount):
        self.values.Pay += amount
        self.Pay_label.setText(f"${str(self.values.Pay)}")

        if self.values.Pay >= self.values.toPay:
            logger.info("Pago completado.")
            total_cash = self.values.historialCash + self.values.Pay
            self.values.set_historialCash(total_cash)
            self.stopCashReader()
            self.go_to_success_screen()

    def go_to_success_screen(self):
        logger.info("Redirigiendo a entrega de fichas.")
        self.Pay_label.setText(f"${str(self.values.Pay)}")
        self.stacked_widget.setCurrentIndex(7)

