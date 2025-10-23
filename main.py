import serial
import threading
import socket
import subprocess
import os
import signal
import sys
import datetime
import time
from PySide6.QtWidgets import QApplication, QStackedWidget
from PySide6.QtCore import QTimer
from PySide6.QtGui import QCursor
from PySide6.QtCore import Qt
from startScreen import StartScreen
from productScreen import ProductScreen
from coinScreen import CoinScreen
from promoScreen import PromoScreen
from appValues import AppValues
from paymentScreen import PaymentScreen
from cashScreen import CashScreen
from cashlessScreen import CashlessScreen
from errorPay import ErrorScreen
from successPay import SuccessScreen
from configScreen import ConfigScreen
from hopperError import hopperErrorScreen
from menuConfig import MenuConfigScreen
from priceConfigScreen import PriceConfigScreen
from historialScreen import HistorialScreen
from POS import POSScreen
from IdleVideoScreen import IdleVideoScreen
from gpio_config import GPIOConfig
from logger_config import setup_logger

# Crear logger global
logger = setup_logger()

def handle_exit(signum, frame):
    logger.info("Saliendo del sistema, cerrando proceso Node.js...")
    if node_process.poll() is None:
        node_process.terminate()
    sys.exit()


def handle_exit(signum, frame):
    if node_process.poll() is None:
        node_process.terminate()
    sys.exit()

if __name__ == "__main__":
    # Ruta al programa Node.js
    node_program = "./control_Pago_POS_v2.js"

    # Verificar si el archivo Node.js existe
    if not os.path.exists(node_program):
        logger.error(f"Archivo Node.js no encontrado en: {node_program}")
        print("El programa Node.js no se encuentra en la ruta especificada.")
        exit()

    # Asociar la señal SIGINT (Ctrl+C) al manejador de salida
    signal.signal(signal.SIGINT, handle_exit)

    # Ejecutar el programa Node.js
    node_process = subprocess.Popen(["node", node_program])
    logger.info(f"Proceso Node.js iniciado con PID: {node_process.pid}")
    app = QApplication(sys.argv)
    app.setOverrideCursor(QCursor(Qt.BlankCursor))
    stacked_widget = QStackedWidget()
    
    start_window = StartScreen(stacked_widget)
    product_window = ProductScreen(stacked_widget)
    coin_view = CoinScreen(stacked_widget)
    promo_view = PromoScreen(stacked_widget)
    payment_window = PaymentScreen(stacked_widget)
    
    gpio_config = GPIOConfig()
    cash_screen = CashScreen(stacked_widget, gpio_config)
    
    cashless_screen = CashlessScreen(stacked_widget)
    error_screen = ErrorScreen(stacked_widget)
    success_screen = SuccessScreen(stacked_widget)
    config_screen = ConfigScreen(stacked_widget)
    hopperError_screen = hopperErrorScreen(stacked_widget)
    menuConfig_screen = MenuConfigScreen(stacked_widget)
    priceConfig_screen = PriceConfigScreen(stacked_widget)
    historial_screen = HistorialScreen(stacked_widget)
    pos_screen = POSScreen(stacked_widget)
    #idle_screen = IdleVideoScreen(stacked_widget, return_index = 0)
    
    stacked_widget.addWidget(start_window) #index 0
    stacked_widget.addWidget(product_window) #index 1
    stacked_widget.addWidget(coin_view) # index 2
    stacked_widget.addWidget(payment_window) #index 3
    stacked_widget.addWidget(cash_screen) #index 4
    stacked_widget.addWidget(cashless_screen) #index 5
    stacked_widget.addWidget(error_screen) #index 6
    stacked_widget.addWidget(success_screen) #index 7
    stacked_widget.addWidget(config_screen) #index 8
    stacked_widget.addWidget(hopperError_screen) #index 9
    stacked_widget.addWidget(menuConfig_screen) #index 10
    stacked_widget.addWidget(priceConfig_screen)#index 11
    stacked_widget.addWidget(historial_screen) #index 12
    stacked_widget.addWidget(pos_screen)#index 13
    #stacked_widget.addWidget(idle_screen)#index 14
    stacked_widget.setCurrentIndex(0)
    stacked_widget.showFullScreen()
    stacked_widget.show()
    sys.exit(app.exec())
    
    # Si la interfaz se cierra, se termina el proceso de Node.js
    if node_process.poll() is None:
        node_process.terminate()
