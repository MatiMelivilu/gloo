from PySide6.QtWidgets import QWidget, QPushButton, QLabel, QLineEdit
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

CLAVE_CORRECTA = "1234"
BOTON_HIDE = "background: transparent; border: none;"
#BOTON_HIDE = "font-size: 60px; background: #FBD556; border: 2px solid black;"


class ConfigScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.password = ""

        self.label_background = QLabel(self)
        self.label_background.setPixmap(QPixmap("./imagenes/C1-inPassword.jpg"))
        self.label_background.setScaledContents(True)

        self.password_input = QLineEdit(self)
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setReadOnly(True)
        self.password_input.setAlignment(Qt.AlignCenter)
        self.password_input.setStyleSheet("font-size: 30px; background: white; border: 2px solid black;")

        self.bBack = QPushButton("", self)
        self.bBack.setGeometry(35, 35, 75, 75)
        self.bBack.setStyleSheet("font-size: 60px; background: #FBD556; border: 2px solid black;")
        self.bBack.clicked.connect(self.returnToProductWindow)
        self.bBack.setText('X')

        self.buttons = []
        self.initUI()

    def initUI(self):
        self.setFixedSize(1280, 720)
        self.label_background.resize(1280, 720)

        # Campo de contrasena (ajustado visualmente al diseno)
        self.password_input.setGeometry(500, 238, 260, 60)

        # Tamano y espacio entre botones
        btn_w = 110
        btn_h = 70
        spacing = 0.5

        start_x = 460
        start_y = 320

        # Matriz del teclado numurico
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
                #btn.setStyleSheet("font-size: 24px; background-color: white; border: 2px solid black; border-radius: 10px;")
                btn.setStyleSheet(BOTON_HIDE)
                btn.setText('')
                
                if key == 'a':
                    btn.clicked.connect(self.backspace)
                elif key == 'b':
                    btn.clicked.connect(self.validate_password)
                else:
                    btn.clicked.connect(lambda checked, t=key: self.add_digit(t))

                self.buttons.append(btn)

    def add_digit(self, digit):
        if len(self.password) < 6:
            self.password += digit
            self.password_input.setText("?" * len(self.password))

    def backspace(self):
        self.password = self.password[:-1]
        self.password_input.setText("?" * len(self.password))

    def validate_password(self):
        if self.password == CLAVE_CORRECTA:
            print("Contrasena correcta. Accediendo...")
            self.stacked_widget.setCurrentIndex(10)  # Cambia a la ventana deseada
        else:
            print("Contrasena incorrecta.")
            self.password = ""
            self.password_input.setText("")

    def returnToProductWindow(self):
        self.stacked_widget.setCurrentIndex(0)

    def showEvent(self, event):
        super().showEvent(event)
        self.password = ""
        self.password_input.setText("")

