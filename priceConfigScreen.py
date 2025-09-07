from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt
from appValues import AppValues

BOTON_HIDE = "background: transparent; border: none;"
#BOTON_HIDE = "transparent"
STYLE_ACTIVE = "font-size: 30px; background: #FBD556; border: 2px solid black;"
STYLE_INACTIVE = "font-size: 30px; background: white; border: 2px solid black;"


class PriceConfigScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.values = AppValues()
        self.active_input = None  # Input actualmente seleccionado

        self.label_background = QLabel(self)
        self.label_background.setPixmap(QPixmap("./imagenes/C3-priceConfig.jpg"))
        self.label_background.setScaledContents(True)
        self.values.numPromos_changed.connect(self.update_numPromos_label)

        # Campos de entrada
        self.input_ficha = QLineEdit(self)
        self.input_promo1_valor = QLineEdit(self)
        self.input_promo1_cantidad = QLineEdit(self)
        self.input_promo2_valor = QLineEdit(self)
        self.input_promo2_cantidad = QLineEdit(self)

        # Coordenadas y tamanos individuales
        self.input_ficha.setGeometry(345, 283, 190, 60)
        self.input_promo1_valor.setGeometry(300, 400, 190, 60)
        self.input_promo1_cantidad.setGeometry(490, 400, 100, 60)
        self.input_promo2_valor.setGeometry(300, 515, 190, 60)
        self.input_promo2_cantidad.setGeometry(490, 515, 100, 60)
        
        self.input_boxes = [
            self.input_ficha,
            self.input_promo1_valor,
            self.input_promo1_cantidad,
            self.input_promo2_valor,
            self.input_promo2_cantidad,
        ]


        for input_box in [
            self.input_ficha,
            self.input_promo1_valor,
            self.input_promo1_cantidad,
            self.input_promo2_valor,
            self.input_promo2_cantidad,
        ]:
            input_box.setStyleSheet("font-size: 30px; background: white; border: 2px solid black;")
            input_box.setReadOnly(True)
            input_box.setAlignment(Qt.AlignCenter)
            input_box.mousePressEvent = lambda e, box=input_box: self.set_active_input(box)
            
        self.input_ficha.setText(f"${self.values.valor_coin}")
        self.input_promo1_valor.setText(f"${self.values.valor_promo}")
        self.input_promo2_valor.setText(f"$")
        self.input_promo1_cantidad.setText(f"x{self.values.nPromos}")
        self.input_promo2_cantidad.setText("x")


        self.bBack = QPushButton("", self)
        self.bBack.setGeometry(385, 610, 230, 50)
        self.bBack.setStyleSheet(BOTON_HIDE)
        self.bBack.clicked.connect(self.returnToConfigMenuWindow)
        
        self.bGuardar = QPushButton("", self)
        self.bGuardar.setGeometry(630, 610, 230, 50)
        self.bGuardar.setStyleSheet(BOTON_HIDE)
        self.bGuardar.clicked.connect(self.guardar_valores)
        
        self.bSinPromos = QPushButton("", self)
        self.bSinPromos.setGeometry(242, 78, 250, 50)
        self.bSinPromos.clicked.connect(self.select0Promos)

        self.b1Promos = QPushButton("", self)
        self.b1Promos.setGeometry(497, 78, 250, 50)
        self.b1Promos.setStyleSheet(BOTON_HIDE)
        self.b1Promos.clicked.connect(self.select1Promos)

        self.b2Promos = QPushButton("", self)
        self.b2Promos.setGeometry(752, 78, 250, 50)
        self.b2Promos.setStyleSheet(BOTON_HIDE)
        self.b2Promos.clicked.connect(self.select2Promos)

        if self.values.numPromos == 0:
            self.bSinPromos.setStyleSheet("background: rgba(251, 213, 86, 100); border: none")
            self.b1Promos.setStyleSheet(BOTON_HIDE)
            self.b2Promos.setStyleSheet(BOTON_HIDE)
            
        elif self.values.numPromos == 1:
            self.bSinPromos.setStyleSheet(BOTON_HIDE)
            self.b1Promos.setStyleSheet("background: rgba(251, 213, 86, 100); border: none")
            self.b2Promos.setStyleSheet(BOTON_HIDE)
            
        elif self.values.numPromos == 2:
            self.bSinPromos.setStyleSheet(BOTON_HIDE)
            self.b2Promos.setStyleSheet("background: rgba(251, 213, 86, 100); border: none")
            self.b1Promos.setStyleSheet(BOTON_HIDE)
        
        else:
            self.bSinPromos.setStyleSheet(BOTON_HIDE)
            self.b2Promos.setStyleSheet(BOTON_HIDE)
            self.b1Promos.setStyleSheet(BOTON_HIDE)
            
        self.buttons = []
        self.initUI()

    def initUI(self):
        self.setFixedSize(1280, 720)
        self.label_background.resize(1280, 720)

        btn_w = 110
        btn_h = 70
        spacing = 0.5

        start_x = 640
        start_y = 230

        layout = [
            ['1', '2', '3'],
            ['4', '5', '6'],
            ['7', '8', '9'],
            ['a', '0', 'b']
        ]

        for row_index, row in enumerate(layout):
            for col_index, key in enumerate(row):
                x = start_x + col_index * (btn_w + spacing)
                y = start_y + row_index * (btn_h + spacing)

                btn = QPushButton(key, self)
                btn.setGeometry(x, y, btn_w, btn_h)
                btn.setStyleSheet(BOTON_HIDE)
                btn.setText('')

                if key == 'a':
                    btn.clicked.connect(self.backspace)
                else:
                    btn.clicked.connect(lambda checked, t=key: self.add_digit(t))

                self.buttons.append(btn)

    def set_active_input(self, input_box):
        self.active_input = input_box
        for box in self.input_boxes:
            if box == input_box:
                box.setStyleSheet(STYLE_ACTIVE)
            else:
                box.setStyleSheet(STYLE_INACTIVE)


    def add_digit(self, digit):
        if self.active_input:
            text = self.active_input.text()
        
            # Detecta si empieza con $ o x
            if text.startswith("$"):
                prefix = "$"
            elif text.startswith("x"):
                prefix = "x"
            else:
                prefix = ""

            # No permitir borrar el prefijo
            new_text = text + digit if text == prefix or len(text) < 10 else text
            self.active_input.setText(new_text)

    def backspace(self):
        if self.active_input:
            text = self.active_input.text()

            if text.startswith("$") or text.startswith("x"):
                if len(text) > 1:
                    self.active_input.setText(text[:-1])
            else:
                self.active_input.setText("")

    def get_clean_number(self, line_edit):
        text = line_edit.text()
        return ''.join(filter(str.isdigit, text))

    def guardar_valores(self):
        # Obtener los valores como enteros
        valor_ficha = int(self.get_clean_number(self.input_ficha))
        promo1_valor = int(self.get_clean_number(self.input_promo1_valor))
        promo1_cantidad = int(self.get_clean_number(self.input_promo1_cantidad))
        #promo2_valor = int(self.get_clean_number(self.input_promo2_valor))
        #promo2_cantidad = int(self.get_clean_number(self.input_promo2_cantidad))

        # Guardar en self.values
        self.values.set_valor_coin(valor_ficha)
        self.values.set_valor_promo(promo1_valor)
        self.values.set_nPromos(promo1_cantidad)

        # Si tienes mas setters para promos, podrias hacer algo como:
        # self.values.set_promo1(valor=promo1_valor, cantidad=promo1_cantidad)
        # self.values.set_promo2(valor=promo2_valor, cantidad=promo2_cantidad)

        print("Valores guardados:")
        #print("Ficha:", valor_ficha)
        #print("Promo 1:", promo1_valor, "x", promo1_cantidad)
        #print("Promo 2:", promo2_valor, "x", promo2_cantidad)
        self.stacked_widget.setCurrentIndex(10)

    def clear_input(self):
        if self.active_input:
            self.active_input.setText("")
            
    def empyFunction(self):
        pass

    def select0Promos(self):
        self.values.set_numPromos(0)

    def select1Promos(self):
        self.values.set_numPromos(1)

    def select2Promos(self):
        self.values.set_numPromos(2)

    def update_numPromos_label(self):
        if self.values.numPromos == 0:
            self.bSinPromos.setStyleSheet("background: rgba(251, 213, 86, 100); border: none")
            self.b1Promos.setStyleSheet(BOTON_HIDE)
            self.b2Promos.setStyleSheet(BOTON_HIDE)
            
        elif self.values.numPromos == 1:
            self.bSinPromos.setStyleSheet(BOTON_HIDE)
            self.b1Promos.setStyleSheet("background: rgba(251, 213, 86, 100); border: none")
            self.b2Promos.setStyleSheet(BOTON_HIDE)
            
        elif self.values.numPromos == 2:
            self.bSinPromos.setStyleSheet(BOTON_HIDE)
            self.b2Promos.setStyleSheet("background: rgba(251, 213, 86, 100); border: none")
            self.b1Promos.setStyleSheet(BOTON_HIDE)
        
        else:
            self.bSinPromos.setStyleSheet(BOTON_HIDE)
            self.b2Promos.setStyleSheet(BOTON_HIDE)
            self.b1Promos.setStyleSheet(BOTON_HIDE)

    def returnToConfigMenuWindow(self):
        self.stacked_widget.setCurrentIndex(10)
