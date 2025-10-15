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
    folio_changed = Signal(str)
    cantidad_promos_changed = Signal(int)
    cantidad_fichas_changed = Signal(int)
    cantidad_promos_total_changed = Signal(int)
    cantidad_fichas_total_changed = Signal(int)
    correo_changed = Signal(str)
    fecha_inicio_changed = Signal(str)
    
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
        self.folio = data.get("folio", "0")
        self.cantidad_promos = data.get("cantidad_promos", 0)
        self.cantidad_promos_total = data.get("cantidad_promos_total", 0)       
        self.cantidad_fichas = data.get("cantidad_fichas",0) 
        self.cantidad_fichas_total = data.get("cantidad_fichas_total",0) 
        self.correo = data.get("correo", "matias.melivilu27@gmail.com")
        self.fecha_inicio = data.get("Fecha_inicio","0000-00-00")

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
            "facturacionPOS": self.facturacionPOS,
            "folio": self.folio,
            "cantidad_promos": self.cantidad_promos,
            "cantidad_promos_total": self.cantidad_promos_total,
            "cantidad_fichas": self.cantidad_fichas,
            "cantidad_fichas_total": self.cantidad_fichas_total,
            "correo": self.correo,
            "fecha_inicio": self.fecha_inicio
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

    def set_folio(self, state):
        if self.folio != state:
            self.folio = state
            self.folio_changed.emit(self.folio)
            self._save_to_json()

    def set_cantidad_promos(self, state):
        if self.cantidad_promos != state:
            self.cantidad_promos = state
            self.cantidad_promos_changed.emit(self.cantidad_promos)
            self._save_to_json()
            
    def set_cantidad_promos_total(self, state):
        if self.cantidad_promos_total != state:
            self.cantidad_promos_total = state
            self.cantidad_promos_total_changed.emit(self.cantidad_promos_total)
            self._save_to_json()
            
    def set_cantidad_fichas(self, state):
        if self.cantidad_fichas != state:
            self.cantidad_fichas = state
            self.cantidad_fichas_changed.emit(self.cantidad_fichas)
            self._save_to_json()
            
    def set_cantidad_fichas_total(self, state):
        if self.cantidad_fichas_total != state:
            self.cantidad_fichas_total = state
            self.cantidad_fichas_total_changed.emit(self.cantidad_fichas_total)
            self._save_to_json()

    def set_correo(self, state):
        if self.correo != state:
            self.correo = state
            self.correo_changed.emit(self.correo)
            self._save_to_json()


    def set_fecha_inicio(self, state):
        if self.fecha_inicio != state:
            self.fecha_inicio = state
            self.fecha_inicio_changed.emit(self.fecha_inicio)
            self._save_to_json()
