from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QCheckBox,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
)
from PySide6.QtCore import Qt
from ...services.employees import list_employees, get_employee, upsert_employee, delete_employee

class EmployeeBasicDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("員工基本資料（TE_BASIC）")
        self.resize(800, 600)

        # Widgets
        form = QFormLayout()
        self.emp_id = QLineEdit()
        self.dept = QLineEdit()
        self.name = QLineEdit()
        self.onboard = QLineEdit()
        self.area = QLineEdit()
        self.active = QCheckBox("在職(Active)")
        form.addRow("EMP_ID", self.emp_id)
        form.addRow("Dept_Code", self.dept)
        form.addRow("C_Name", self.name)
        form.addRow("On_Board_Date", self.onboard)
        form.addRow("Area", self.area)
        form.addRow("", self.active)

        btns = QHBoxLayout()
        self.btn_load = QPushButton("載入")
        self.btn_save = QPushButton("新增/更新")
        self.btn_delete = QPushButton("刪除")
        self.btn_clear = QPushButton("清空")
        self.btn_refresh = QPushButton("刷新清單")
        btns.addWidget(self.btn_load)
        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_delete)
        btns.addWidget(self.btn_clear)
        btns.addWidget(self.btn_refresh)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["EMP_ID","Dept_Code","C_Name","On_Board_Date","Area","Active"])
        self.table.setSelectionBehavior(self.table.SelectRows)
        self.table.setEditTriggers(self.table.NoEditTriggers)

        # Layout
        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addLayout(btns)
        root.addWidget(self.table, 1)

        # Signals
        self.btn_load.clicked.connect(self.on_load)
        self.btn_save.clicked.connect(self.on_save)
        self.btn_delete.clicked.connect(self.on_delete)
        self.btn_clear.clicked.connect(self.on_clear)
        self.btn_refresh.clicked.connect(self.populate)

        self.populate()

    def populate(self):
        emps = list_employees(only_active=False, limit=200)
        self.table.setRowCount(0)
        for e in emps:
            r = self.table.rowCount()
            self.table.insertRow(r)
            self.table.setItem(r, 0, QTableWidgetItem(str(e.EMP_ID or "")))
            self.table.setItem(r, 1, QTableWidgetItem(str(e.Dept_Code or "")))
            self.table.setItem(r, 2, QTableWidgetItem(str(e.C_Name or "")))
            self.table.setItem(r, 3, QTableWidgetItem(str(e.On_Board_Date or "")))
            self.table.setItem(r, 4, QTableWidgetItem(str(e.Area or "")))
            self.table.setItem(r, 5, QTableWidgetItem("Y" if e.Active else "N"))

    def on_load(self):
        emp_id = self.emp_id.text().strip()
        if not emp_id:
            QMessageBox.warning(self, "提示", "請先輸入 EMP_ID")
            return
        e = get_employee(emp_id)
        if not e:
            QMessageBox.information(self, "訊息", f"查無 EMP_ID={emp_id}")
            return
        self.dept.setText(e.Dept_Code or "")
        self.name.setText(e.C_Name or "")
        self.onboard.setText(e.On_Board_Date or "")
        self.area.setText(e.Area or "")
        self.active.setChecked(bool(e.Active))

    def on_save(self):
        emp_id = self.emp_id.text().strip()
        if not emp_id:
            QMessageBox.warning(self, "提示", "EMP_ID 不可空白")
            return
        obj = upsert_employee(
            emp_id=emp_id,
            dept_code=self.dept.text().strip() or None,
            c_name=self.name.text().strip() or None,
            on_board_date=self.onboard.text().strip() or None,
            area=self.area.text().strip() or None,
            active=self.active.isChecked(),
        )
        QMessageBox.information(self, "完成", f"已儲存 EMP_ID={obj.EMP_ID}")
        self.populate()

    def on_delete(self):
        emp_id = self.emp_id.text().strip()
        if not emp_id:
            QMessageBox.warning(self, "提示", "請先輸入 EMP_ID")
            return
        if QMessageBox.question(self, "確認", f"確定刪除 EMP_ID={emp_id} ?") == QMessageBox.Yes:
            ok = delete_employee(emp_id)
            if ok:
                QMessageBox.information(self, "完成", f"已刪除 EMP_ID={emp_id}")
                self.populate()
            else:
                QMessageBox.warning(self, "提示", f"找不到 EMP_ID={emp_id}")

    def on_clear(self):
        self.emp_id.clear()
        self.dept.clear()
        self.name.clear()
        self.onboard.clear()
        self.area.clear()
        self.active.setChecked(True)
