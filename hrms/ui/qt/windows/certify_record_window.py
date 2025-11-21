from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QAbstractItemView
import pandas as pd
import os
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '..', '..', 'data', 'CERTIFY_RECORD.csv')
class CertifyRecordWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("證照紀錄（CERTIFY_RECORD）管理")
        self.resize(700, 400)
        form = QFormLayout()
        self.record_id = QLineEdit()
        self.emp_id = QLineEdit()
        self.certify_id = QLineEdit()
        self.date = QLineEdit()
        form.addRow("Record_ID", self.record_id)
        form.addRow("EMP_ID", self.emp_id)
        form.addRow("Certify_ID", self.certify_id)
        form.addRow("Date", self.date)
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
        self.table = QTableWidget(0, 4)
        self.table.setHorizontalHeaderLabels(["Record_ID", "EMP_ID", "Certify_ID", "Date"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addLayout(btns)
        root.addWidget(self.table, 1)
        self.btn_load.clicked.connect(self.on_load)
        self.btn_save.clicked.connect(self.on_save)
        self.btn_delete.clicked.connect(self.on_delete)
        self.btn_clear.clicked.connect(self.on_clear)
        self.btn_refresh.clicked.connect(self.populate)
        self.populate()
    def read_csv(self):
        try:
            df = pd.read_csv(DATA_PATH, encoding='utf-8')
        except Exception:
            df = pd.DataFrame(columns=["Record_ID", "EMP_ID", "Certify_ID", "Date"])
        return df
    def write_csv(self, df):
        df.to_csv(DATA_PATH, index=False, encoding='utf-8')
    def populate(self):
        df = self.read_csv()
        self.table.setRowCount(0)
        for _, row in df.iterrows():
            i = self.table.rowCount()
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(row["Record_ID"])))
            self.table.setItem(i, 1, QTableWidgetItem(str(row["EMP_ID"])))
            self.table.setItem(i, 2, QTableWidgetItem(str(row["Certify_ID"])))
            self.table.setItem(i, 3, QTableWidgetItem(str(row["Date"])))
    def on_load(self):
        record_id = self.record_id.text().strip()
        if not record_id:
            QMessageBox.warning(self, "提示", "請輸入 Record_ID")
            return
        df = self.read_csv()
        row = df[df["Record_ID"] == record_id]
        if row.empty:
            QMessageBox.information(self, "訊息", f"查無 Record_ID={record_id}")
            return
        self.emp_id.setText(str(row.iloc[0]["EMP_ID"]))
        self.certify_id.setText(str(row.iloc[0]["Certify_ID"]))
        self.date.setText(str(row.iloc[0]["Date"]))
    def on_save(self):
        record_id = self.record_id.text().strip()
        emp_id = self.emp_id.text().strip()
        certify_id = self.certify_id.text().strip()
        date = self.date.text().strip()
        if not record_id:
            QMessageBox.warning(self, "提示", "Record_ID 不可空白")
            return
        df = self.read_csv()
        idx = df[df["Record_ID"] == record_id].index
        if len(idx) > 0:
            df.loc[idx, "EMP_ID"] = emp_id
            df.loc[idx, "Certify_ID"] = certify_id
            df.loc[idx, "Date"] = date
        else:
            df = pd.concat([df, pd.DataFrame({"Record_ID": [record_id], "EMP_ID": [emp_id], "Certify_ID": [certify_id], "Date": [date]})], ignore_index=True)
        self.write_csv(df)
        QMessageBox.information(self, "完成", f"已儲存 Record_ID={record_id}")
        self.populate()
    def on_delete(self):
        record_id = self.record_id.text().strip()
        if not record_id:
            QMessageBox.warning(self, "提示", "請輸入 Record_ID")
            return
        df = self.read_csv()
        idx = df[df["Record_ID"] == record_id].index
        if len(idx) > 0:
            df = df.drop(idx)
            self.write_csv(df)
            QMessageBox.information(self, "完成", f"已刪除 Record_ID={record_id}")
            self.populate()
        else:
            QMessageBox.warning(self, "提示", f"找不到 Record_ID={record_id}")
    def on_clear(self):
        self.record_id.clear()
        self.emp_id.clear()
        self.certify_id.clear()
        self.date.clear()
