from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QAbstractItemView
import pandas as pd
import os
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '..', '..', 'data', 'CERTIFY_TYPE.csv')
class CertifyTypeWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("證照類型（CERTIFY_TYPE）管理")
        self.resize(600, 400)
        form = QFormLayout()
        self.type_id = QLineEdit()
        self.type_name = QLineEdit()
        form.addRow("Type_ID", self.type_id)
        form.addRow("Type_Name", self.type_name)
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
        self.table.setHorizontalHeaderLabels(["Type_ID", "Type_Name"])
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
            df = pd.DataFrame(columns=["Type_ID", "Type_Name"])
        return df
    def write_csv(self, df):
        df.to_csv(DATA_PATH, index=False, encoding='utf-8')
    def populate(self):
        df = self.read_csv()
        self.table.setRowCount(0)
        for _, row in df.iterrows():
            i = self.table.rowCount()
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(row.get("Type_ID", ""))))
            self.table.setItem(i, 1, QTableWidgetItem(str(row.get("Type_Name", ""))))
    def on_load(self):
        type_id = self.type_id.text().strip()
        if not type_id:
            QMessageBox.warning(self, "提示", "請輸入 Type_ID")
            return
        df = self.read_csv()
        row = df[df["Type_ID"] == type_id]
        if row.empty:
            QMessageBox.information(self, "訊息", f"查無 Type_ID={type_id}")
            return
        self.type_name.setText(str(row.iloc[0]["Type_Name"]))
    def on_save(self):
        type_id = self.type_id.text().strip()
        type_name = self.type_name.text().strip()
        if not type_id:
            QMessageBox.warning(self, "提示", "Type_ID 不可空白")
            return
        df = self.read_csv()
        idx = df[df["Type_ID"] == type_id].index
        if len(idx) > 0:
            df.loc[idx, "Type_Name"] = type_name
        else:
            df = pd.concat([df, pd.DataFrame({"Type_ID": [type_id], "Type_Name": [type_name]})], ignore_index=True)
        self.write_csv(df)
        QMessageBox.information(self, "完成", f"已儲存 Type_ID={type_id}")
        self.populate()
    def on_delete(self):
        type_id = self.type_id.text().strip()
        if not type_id:
            QMessageBox.warning(self, "提示", "請輸入 Type_ID")
            return
        df = self.read_csv()
        idx = df[df["Type_ID"] == type_id].index
        if len(idx) > 0:
            df = df.drop(idx)
            self.write_csv(df)
            QMessageBox.information(self, "完成", f"已刪除 Type_ID={type_id}")
            self.populate()
        else:
            QMessageBox.warning(self, "提示", f"找不到 Type_ID={type_id}")
    def on_clear(self):
        self.type_id.clear()
        self.type_name.clear()
