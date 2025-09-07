from PySide6.QtWidgets import QWidget, QVBoxLayout
from PySide6.QtCore import QProcess, Qt, QTimer
import os

class IdleVideoScreen(QWidget):
    def __init__(self, stacked_widget, return_index, video_path="./video/Gloo_Huachalalume.mp4"):
        super().__init__()
        self.stacked_widget = stacked_widget
        self.return_index = return_index
        self.video_path = video_path

        self.setStyleSheet("background-color: black;")
        self.setCursor(Qt.BlankCursor)  # Oculta el cursor

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)

        self.process = QProcess(self)
        self.process.setProgram("mpv")
        self.process.setArguments([
            "--really-quiet",
            "--loop",
            "--no-border",
            "--geometry=100%x100%",
            "--wid={}".format(int(self.winId())),
            self.video_path
        ])
        self.process.start()

        # Escuchar toques o clics para volver a la pantalla principal
        self.setAttribute(Qt.WA_AcceptTouchEvents, True)

    def mousePressEvent(self, event):
        self.close_video()

    def touchEvent(self, event):
        self.close_video()

    def close_video(self):
        if self.process.state() == QProcess.Running:
            self.process.terminate()
        self.stacked_widget.setCurrentIndex(self.return_index)

        # Reiniciar temporizador de inactividad si volvemos a StartScreen
        start_screen = self.stacked_widget.widget(self.return_index)
        if hasattr(start_screen, "inactivity_timer"):
            start_screen.inactivity_timer.start()

