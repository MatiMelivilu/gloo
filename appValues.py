import json
import os
from PySide6.QtCore import QObject, Signal

CONFIG_PATH = "./values.json"

class AppValues(QObject):
    _instance = None
    coins_changed = Signal(int)  
    nPromo_changed = Signal(int)
    nPromo2_changed = Signal(int)
    valor_coin_changed = Signal(int)  
    valor_promo_changed = Signal(int) 
    valor_promo2_changed = Signal(int) 
    toPay_changed = Signal(int) 
    Pay_changed = Signal(int) 
    numPromos_changed = Signal(int)
    historialCash_changed = Signal(int)
    historialCashless_changed = Signal(int)
    facturacionPOS_changed = Signal(str)

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(AppValues, cls).__new__(cls)  
        return cls._instance

    def __init__(self):
        if not hasattr(self, "_initialized"):
            super().__init__()
            self._load_from_json()
            self._initialized = True

    def _load_from_json(self):
        if os.path.exists(CONFIG_PATH):
            with open(CONFIG_PATH, "r") as f:
                data = json.load(f)
        else:
            data = {}

        self.coins = data.get("coins", 1)
        self.valor_coin = data.get("valor_coin", 1500)
        self.valor_promo = data.get("valor_promo", 5000)
        self.valor_promo2 = data.get("valor_promo", 10000)
        self.toPay = data.get("toPay", 1500)
        self.nPromos = data.get("nPromos", 4)
        self.nPromos2 = data.get("nPromos", 10)
        self.Pay = data.get("Pay", 0)
        self.numPromos = data.get("numPromos", 1)
        self.historialCash = data.get("historialCash", 0)
        self.historialCashless = data.get("historialCashless", 0)
        self.facturacionPOS = data.get("facturacionPOS", "on")

    def _save_to_json(self):
        data = {
            "coins": self.coins,
            "valor_coin": self.valor_coin,
            "valor_promo": self.valor_promo,
            "valor_promo2": self.valor_promo2,
            "toPay": self.toPay,
            "nPromos": self.nPromos,
            "nPromos2": self.nPromos2,
            "Pay": self.Pay,
            "numPromos": self.numPromos,
            "historialCash": self.historialCash,
            "historialCashless": self.historialCashless,
            "facturacionPOS": self.facturacionPOS
        }
        with open(CONFIG_PATH, "w") as f:
            json.dump(data, f, indent=4)

    def set_coins(self, value):
        if self.coins != value:
            self.coins = value
            self.coins_changed.emit(self.coins)
            self._save_to_json()

    def set_valor_coin(self, value):
        if self.valor_coin != value:
            self.valor_coin = value
            self.valor_coin_changed.emit(self.valor_coin)
            self._save_to_json()

    def set_valor_promo(self, value):
        if self.valor_promo != value:
            self.valor_promo = value
            self.valor_promo_changed.emit(self.valor_promo)
            self._save_to_json()

    def set_valor_promo2(self, value):
        if self.valor_promo2 != value:
            self.valor_promo2 = value
            self.valor_promo2_changed.emit(self.valor_promo2)
            self._save_to_json()

    def set_toPay(self, value):
        if self.toPay != value:
            self.toPay = value
            self.toPay_changed.emit(self.toPay)
            self._save_to_json()

    def set_nPromos(self, value):
        if self.nPromos != value:
            self.nPromos = value
            self.nPromo_changed.emit(self.nPromos)
            self._save_to_json()

    def set_nPromos2(self, value):
        if self.nPromos2 != value:
            self.nPromos2 = value
            self.nPromo2_changed.emit(self.nPromos2)
            self._save_to_json()

    def set_Pay(self, value):
        if self.Pay != value:
            self.Pay = value
            self.Pay_changed.emit(self.Pay)
            self._save_to_json()

    def set_numPromos(self, value):
        if self.numPromos != value:
            self.numPromos = value
            self.numPromos_changed.emit(self.numPromos)
            self._save_to_json()

    def set_historialCash(self, value):
        if self.historialCash != value:
            self.historialCash = value
            self.historialCash_changed.emit(self.historialCash)
            self._save_to_json()

    def set_historialCashless(self, value):
        if self.historialCashless != value:
            self.historialCashless = value
            self.historialCashless_changed.emit(self.historialCashless)
            self._save_to_json()

    def set_facturacionPOS(self, state):
        if self.facturacionPOS != state:
            self.facturacionPOS = state
            self.facturacionPOS_changed.emit(self.facturacionPOS)
            self._save_to_json()
