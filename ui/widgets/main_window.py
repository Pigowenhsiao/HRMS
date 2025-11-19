from PySide6.QtWidgets import QMainWindow, QPushButton, QWidget, QVBoxLayout
from .employee_basic import EmployeeBasicDialog

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HRMS - Python v2")
        root = QWidget(self)
        layout = QVBoxLayout(root)

        btn_basic = QPushButton("員工基本資料（介面示範）", self)
        btn_basic.clicked.connect(self.open_basic)
        layout.addWidget(btn_basic)

        root.setLayout(layout)
        self.setCentralWidget(root)

    def open_basic(self):
        dlg = EmployeeBasicDialog(self)
        dlg.exec()
