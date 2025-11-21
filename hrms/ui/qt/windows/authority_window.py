from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QAbstractItemView
import pandas as pd
import os
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '..', '..', 'data', 'Authority.csv')
class AuthorityWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("權限（Authority）管理")
        self.resize(600, 400)
        form = QFormLayout()
        self.auth_id = QLineEdit()
        self.auth_name = QLineEdit()
        form.addRow("Auth_ID", self.auth_id)
        form.addRow("Auth_Name", self.auth_name)
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
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Auth_ID", "Auth_Name"])
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
            df = pd.DataFrame(columns=["Auth_ID", "Auth_Name"])
        return df
    def write_csv(self, df):
        df.to_csv(DATA_PATH, index=False, encoding='utf-8')
    def populate(self):
        df = self.read_csv()
        self.table.setRowCount(0)
        for _, row in df.iterrows():
            i = self.table.rowCount()
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(row.get("Auth_ID", ""))))
            self.table.setItem(i, 1, QTableWidgetItem(str(row.get("Auth_Name", ""))))
    def on_load(self):
        auth_id = self.auth_id.text().strip()
        if not auth_id:
            QMessageBox.warning(self, "提示", "請輸入 Auth_ID")
            return
        df = self.read_csv()
        row = df[df["Auth_ID"] == auth_id]
        if row.empty:
            QMessageBox.information(self, "訊息", f"查無 Auth_ID={auth_id}")
            return
        self.auth_name.setText(str(row.iloc[0]["Auth_Name"]))
    def on_save(self):
        auth_id = self.auth_id.text().strip()
        auth_name = self.auth_name.text().strip()
        if not auth_id:
            QMessageBox.warning(self, "提示", "Auth_ID 不可空白")
            return
        df = self.read_csv()
        idx = df[df["Auth_ID"] == auth_id].index
        if len(idx) > 0:
            df.loc[idx, "Auth_Name"] = auth_name
        else:
            df = pd.concat([df, pd.DataFrame({"Auth_ID": [auth_id], "Auth_Name": [auth_name]})], ignore_index=True)
        self.write_csv(df)
        QMessageBox.information(self, "完成", f"已儲存 Auth_ID={auth_id}")
        self.populate()
    def on_delete(self):
        auth_id = self.auth_id.text().strip()
        if not auth_id:
            QMessageBox.warning(self, "提示", "請輸入 Auth_ID")
            return
        df = self.read_csv()
        idx = df[df["Auth_ID"] == auth_id].index
        if len(idx) > 0:
            df = df.drop(idx)
            self.write_csv(df)
            QMessageBox.information(self, "完成", f"已刪除 Auth_ID={auth_id}")
            self.populate()
        else:
            QMessageBox.warning(self, "提示", f"找不到 Auth_ID={auth_id}")
    def on_clear(self):
        self.auth_id.clear()
        self.auth_name.clear()
