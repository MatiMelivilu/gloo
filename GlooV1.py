import sys
from PySide6.QtWidgets import QApplication, QLabel, QPushButton, QStackedWidget, QWidget
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

class MainWindow(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Gloo Car Wash")
        self.setGeometry(100, 100, 1065, 595)
        
        # Fondo con imagen
        self.label = QLabel(self)
        self.label.setPixmap(QPixmap("./imagenes/gloo1.png"))
        self.label.setGeometry(0, 0, 1065, 595)
        self.label.setScaledContents(True)
        
        # Boton para cambiar de ventana
        self.button = QPushButton("", self)
        self.button.setGeometry(980, 20, 70, 70)
        self.button.setStyleSheet("background: transparent; border: none;")
        self.button.clicked.connect(self.showPromoWindow)
    
    def showPromoWindow(self):
        self.stacked_widget.setCurrentIndex(1)

class PromoWindow(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.initUI()
    
    def initUI(self):
        self.setWindowTitle("Comprar Fichas")
        self.setGeometry(100, 100, 1065, 595)
        
        # Fondo con imagen
        self.label = QLabel(self)
        self.label.setPixmap(QPixmap("./imagenes/gloo2.png"))
        self.label.setGeometry(0, 0, 1065, 595)
        self.label.setScaledContents(True)
        
        # Boton de regreso a la pantalla principal
        self.button_back = QPushButton("", self)
        self.button_back.setGeometry(980, 20, 70, 70)
        self.button_back.setStyleSheet("background: transparent;")
        self.button_back.clicked.connect(self.showMainWindow)
    
    def showMainWindow(self):
        self.stacked_widget.setCurrentIndex(0)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    stacked_widget = QStackedWidget()
    
    main_window = MainWindow(stacked_widget)
    promo_window = PromoWindow(stacked_widget)
    
    stacked_widget.addWidget(main_window)
    stacked_widget.addWidget(promo_window)
    stacked_widget.setCurrentIndex(0)
    
    stacked_widget.show()
    sys.exit(app.exec())
