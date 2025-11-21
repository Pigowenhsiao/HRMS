from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QCheckBox,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QComboBox, QAbstractItemView
)
from PySide6.QtCore import Qt
from hrms.persons.service import list_employees, get_employee, upsert_employee, delete_employee
from hrms.lookups.service import list_dept_codes, list_areas, list_jobs, list_vac_types
from hrms.core.reporting.reports import df_to_excel
import pandas as pd

class BasicWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("員工基本資料（CSV 版）")
        self.resize(980, 680)

        # form
        form = QFormLayout()
        self.emp_id = QLineEdit()
        self.dept = QComboBox(); self.dept.setEditable(True)
        self.name = QLineEdit()
        self.title = QLineEdit()
        self.onboard = QLineEdit()
        self.shift = QLineEdit()
        self.area = QComboBox(); self.area.setEditable(True)
        self.job = QComboBox(); self.job.setEditable(True)
        self.meno = QLineEdit()
        self.active = QCheckBox("在職(Active)")
        self.vac = QComboBox(); self.vac.setEditable(True)

        form.addRow("EMP_ID", self.emp_id)
        form.addRow("Dept_Code", self.dept)
        form.addRow("C_Name", self.name)
        form.addRow("Title", self.title)
        form.addRow("On_Board_Date", self.onboard)
        form.addRow("Shift", self.shift)
        form.addRow("Area", self.area)
        form.addRow("Function(職務)", self.job)
        form.addRow("Meno", self.meno)
        form.addRow("Active", self.active)
        form.addRow("VAC_ID", self.vac)

        # buttons
        btns = QHBoxLayout()
        self.btn_load = QPushButton("載入")
        self.btn_save = QPushButton("新增/更新")
        self.btn_delete = QPushButton("刪除")
        self.btn_clear = QPushButton("清空")
        self.btn_refresh = QPushButton("刷新清單")
        self.btn_export = QPushButton("匯出清單 Excel")
        btns.addWidget(self.btn_load)
        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_delete)
        btns.addWidget(self.btn_clear)
        btns.addWidget(self.btn_refresh)
        btns.addWidget(self.btn_export)

        # table
        self.table = QTableWidget(0, 10)
        self.table.setHorizontalHeaderLabels([
            "EMP_ID","Dept_Code","C_Name","Title","On_Board_Date","Shift","Area","Function","Meno","Active"
        ])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)

        # layout
        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addLayout(btns)
        root.addWidget(self.table, 1)

        # signals
        self.btn_load.clicked.connect(self.on_load)
        self.btn_save.clicked.connect(self.on_save)
        self.btn_delete.clicked.connect(self.on_delete)
        self.btn_clear.clicked.connect(self.on_clear)
        self.btn_refresh.clicked.connect(self.populate)
        self.btn_export.clicked.connect(self.on_export)

        # load lookups
        self._load_lookups()
        # init list
        self.populate()

    def _load_lookups(self):
        self.dept.clear(); self.dept.addItems(list_dept_codes())
        self.area.clear(); self.area.addItems(list_areas())
        self.job.clear(); self.job.addItems(list_jobs())
        self.vac.clear(); self.vac.addItems(list_vac_types())

    def populate(self):
        rows = list_employees(only_active=False, limit=500)
        self.table.setRowCount(0)
        for r in rows:
            i = self.table.rowCount()
            self.table.insertRow(i)
            vals = [r.get("EMP_ID",""), r.get("Dept_Code",""), r.get("C_Name",""), r.get("Title",""),
                    r.get("On_Board_Date",""), r.get("Shift",""), r.get("Area",""), r.get("Function",""),
                    r.get("Meno",""), "Y" if (r.get("Active","").lower()=="true") else "N"]
            for c, v in enumerate(vals):
                self.table.setItem(i, c, QTableWidgetItem(str(v)))

    def on_load(self):
        emp_id = self.emp_id.text().strip()
        if not emp_id:
            QMessageBox.warning(self, "提示", "請輸入 EMP_ID")
            return
        r = get_employee(emp_id)
        if not r:
            QMessageBox.information(self, "訊息", f"查無 EMP_ID={emp_id}")
            return
        self.dept.setCurrentText(r.get("Dept_Code",""))
        self.name.setText(r.get("C_Name","") or "")
        self.title.setText(r.get("Title","") or "")
        self.onboard.setText(r.get("On_Board_Date","") or "")
        self.shift.setText(r.get("Shift","") or "")
        self.area.setCurrentText(r.get("Area","") or "")
        self.job.setCurrentText(r.get("Function","") or "")
        self.meno.setText(r.get("Meno","") or "")
        self.active.setChecked(r.get("Active","").lower()=="true")
        self.vac.setCurrentText(r.get("VAC_ID","") or "")

    def on_save(self):
        emp_id = self.emp_id.text().strip()
        if not emp_id:
            QMessageBox.warning(self, "提示", "EMP_ID 不可空白")
            return
        row = {
            "EMP_ID": emp_id,
            "Dept_Code": self.dept.currentText().strip() or "",
            "C_Name": self.name.text().strip() or "",
            "Title": self.title.text().strip() or "",
            "On_Board_Date": self.onboard.text().strip() or "",
            "Shift": self.shift.text().strip() or "",
            "Area": self.area.currentText().strip() or "",
            "Function": self.job.currentText().strip() or "",
            "Meno": self.meno.text().strip() or "",
            "Active": "true" if self.active.isChecked() else "false",
            "VAC_ID": self.vac.currentText().split()[0] if self.vac.currentText().strip() else "",
        }
        upsert_employee(row)
        QMessageBox.information(self, "完成", f"已儲存 EMP_ID={emp_id}")
        self.populate()

    def on_delete(self):
        emp_id = self.emp_id.text().strip()
        if not emp_id:
            QMessageBox.warning(self, "提示", "請輸入 EMP_ID")
            return
        if QMessageBox.question(self, "確認", f"確定要刪除 EMP_ID={emp_id} ?") == QMessageBox.Yes:
            if delete_employee(emp_id):
                QMessageBox.information(self, "完成", f"已刪除 EMP_ID={emp_id}")
                self.populate()
            else:
                QMessageBox.warning(self, "提示", f"找不到 EMP_ID={emp_id}")

    def on_clear(self):
        self.emp_id.clear(); self.dept.setCurrentText(""); self.name.clear(); self.title.clear()
        self.onboard.clear(); self.shift.clear(); self.area.setCurrentText(""); self.job.setCurrentText("")
        self.meno.clear(); self.active.setChecked(True); self.vac.setCurrentText("")

    def on_export(self):
        rows = list_employees(only_active=False, limit=500)
        df = pd.DataFrame(rows)
        path = df_to_excel(df, prefix="BASIC_list")
        QMessageBox.information(self, "完成", f"已匯出：\n{path}")
