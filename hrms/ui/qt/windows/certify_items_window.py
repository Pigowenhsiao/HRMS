from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QAbstractItemView
import pandas as pd
import os
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '..', '..', 'data', 'CERTIFY_ITEMS.csv')
class CertifyItemsWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("證照項目（CERTIFY_ITEMS）管理")
        self.resize(600, 400)
        form = QFormLayout()
        self.certify_id = QLineEdit()
        self.certify_name = QLineEdit()
        form.addRow("Certify_ID", self.certify_id)
        form.addRow("Certify_Name", self.certify_name)
        btns = QHBoxLayout()
        self.btn_load = QPushButton("載入")
        self.btn_save = QPushButton("新增/更新")
        self.btn_delete = QPushButton("刪除")
        self.btn_clear = QPushButton("清空")
        self.btn_refresh = QPushButton("刷新清單")
        btns.addWidget(self.btn_refresh)
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Certify_ID", "Certify_Name"])
        self.table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        root = QVBoxLayout(self)
        root.addLayout(form)
        root.addLayout(btns)
        root.addWidget(self.table, 1)
        self.btn_load.clicked.connect(self.on_load)
        self.btn_save.clicked.connect(self.on_save)
        self.btn_delete.clicked.connect(self.on_delete)
        self.table.setHorizontalHeaderLabels(["Certify_ID", "Certify_Name"])
        self.btn_refresh.clicked.connect(self.populate)
        self.populate()
    def read_csv(self):
        try:
            df = pd.read_csv(DATA_PATH, encoding='utf-8')
        except Exception:
            df = pd.DataFrame(columns=["Certify_ID", "Certify_Name"])
        return df
    def write_csv(self, df):
        df.to_csv(DATA_PATH, index=False, encoding='utf-8')
    def populate(self):
        df = self.read_csv()
        self.table.setRowCount(0)
        for _, row in df.iterrows():
            i = self.table.rowCount()
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(row.get("Certify_ID", ""))))
            self.table.setItem(i, 1, QTableWidgetItem(str(row.get("Certify_Name", ""))))
    def on_load(self):
        certify_id = self.certify_id.text().strip()
        if not certify_id:
            QMessageBox.warning(self, "提示", "請輸入 Certify_ID")
            return
        df = self.read_csv()
        row = df[df["Certify_ID"] == certify_id]
        if row.empty:
            QMessageBox.information(self, "訊息", f"查無 Certify_ID={certify_id}")
            return
        self.certify_name.setText(str(row.iloc[0]["Certify_Name"]))
    def on_save(self):
        certify_id = self.certify_id.text().strip()
        certify_name = self.certify_name.text().strip()
        if not certify_id:
            QMessageBox.warning(self, "提示", "Certify_ID 不可空白")
            return
        df = self.read_csv()
        idx = df[df["Certify_ID"] == certify_id].index
        if len(idx) > 0:
            df.loc[idx, "Certify_Name"] = certify_name
        else:
            df = pd.concat([df, pd.DataFrame({"Certify_ID": [certify_id], "Certify_Name": [certify_name]})], ignore_index=True)
        self.write_csv(df)
        QMessageBox.information(self, "完成", f"已儲存 Certify_ID={certify_id}")
        self.populate()
    def on_delete(self):
        certify_id = self.certify_id.text().strip()
        if not certify_id:
            QMessageBox.warning(self, "提示", "請輸入 Certify_ID")
            return
        df = self.read_csv()
        idx = df[df["Certify_ID"] == certify_id].index
        if len(idx) > 0:
            df = df.drop(idx)
            self.write_csv(df)
            QMessageBox.information(self, "完成", f"已刪除 Certify_ID={certify_id}")
            self.populate()
        else:
            QMessageBox.warning(self, "提示", f"找不到 Certify_ID={certify_id}")
    def on_clear(self):
        self.certify_id.clear()
        self.certify_name.clear()
