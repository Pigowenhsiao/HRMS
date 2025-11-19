from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QPushButton, QLabel
from .basic_window import BasicWindow

class StartPage(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HRMS CSV - Start Page")
        cw = QWidget(self)
        lay = QVBoxLayout(cw)

        lay.addWidget(QLabel("HRMS（CSV 後端）"))

        btn_basic = QPushButton("員工基本資料（TE_BASIC 範例）")
        btn_basic.clicked.connect(self.open_basic)
        lay.addWidget(btn_basic)

        cw.setLayout(lay)
        self.setCentralWidget(cw)

    def open_basic(self):
        dlg = BasicWindow(self)
        dlg.exec()
