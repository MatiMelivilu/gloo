# logger_config.py
import logging
import os
from datetime import datetime

def setup_logger(name="AppLogger"):
    # Carpeta donde se guardarán los logs
    log_dir = os.path.join(os.path.expanduser("~"), "logs_app")
    os.makedirs(log_dir, exist_ok=True)

    # Nombre del archivo con fecha
    log_filename = os.path.join(log_dir, f"app_{datetime.now().strftime('%Y-%m-%d')}.log")

    # Configurar logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)

    # Formato detallado
    formatter = logging.Formatter(
        "%(asctime)s [%(levelname)s] %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Handler para archivo
    file_handler = logging.FileHandler(log_filename)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    # Handler para consola (opcional)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Evitar duplicados
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger

