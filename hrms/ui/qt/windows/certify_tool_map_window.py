from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QAbstractItemView
import pandas as pd
import os
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '..', '..', 'data', 'CERTIFY_TOOL_MAP.csv')
class CertifyToolMapWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("證照工具對應（CERTIFY_TOOL_MAP）管理")
        self.resize(700, 400)
        form = QFormLayout()
        self.map_id = QLineEdit()
        self.certify_id = QLineEdit()
        self.tool_id = QLineEdit()
        form.addRow("Map_ID", self.map_id)
        form.addRow("Certify_ID", self.certify_id)
        form.addRow("Tool_ID", self.tool_id)
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
        self.table = QTableWidget(0, 3)
        self.table.setHorizontalHeaderLabels(["Map_ID", "Certify_ID", "Tool_ID"])
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
            df = pd.DataFrame(columns=["Map_ID", "Certify_ID", "Tool_ID"])
        return df
    def write_csv(self, df):
        df.to_csv(DATA_PATH, index=False, encoding='utf-8')
    def populate(self):
        df = self.read_csv()
        self.table.setRowCount(0)
        for _, row in df.iterrows():
            i = self.table.rowCount()
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(row.get("Map_ID", ""))))
            self.table.setItem(i, 1, QTableWidgetItem(str(row.get("Certify_ID", ""))))
            self.table.setItem(i, 2, QTableWidgetItem(str(row.get("Tool_ID", ""))))
    def on_load(self):
        map_id = self.map_id.text().strip()
        if not map_id:
            QMessageBox.warning(self, "提示", "請輸入 Map_ID")
            return
        df = self.read_csv()
        row = df[df["Map_ID"] == map_id]
        if row.empty:
            QMessageBox.information(self, "訊息", f"查無 Map_ID={map_id}")
            return
        self.certify_id.setText(str(row.iloc[0]["Certify_ID"]))
        self.tool_id.setText(str(row.iloc[0]["Tool_ID"]))
    def on_save(self):
        map_id = self.map_id.text().strip()
        certify_id = self.certify_id.text().strip()
        tool_id = self.tool_id.text().strip()
        if not map_id:
            QMessageBox.warning(self, "提示", "Map_ID 不可空白")
            return
        df = self.read_csv()
        idx = df[df["Map_ID"] == map_id].index
        if len(idx) > 0:
            df.loc[idx, "Certify_ID"] = certify_id
            df.loc[idx, "Tool_ID"] = tool_id
        else:
            df = pd.concat([df, pd.DataFrame({"Map_ID": [map_id], "Certify_ID": [certify_id], "Tool_ID": [tool_id]})], ignore_index=True)
        self.write_csv(df)
        QMessageBox.information(self, "完成", f"已儲存 Map_ID={map_id}")
        self.populate()
    def on_delete(self):
        map_id = self.map_id.text().strip()
        if not map_id:
            QMessageBox.warning(self, "提示", "請輸入 Map_ID")
            return
        df = self.read_csv()
        idx = df[df["Map_ID"] == map_id].index
        if len(idx) > 0:
            df = df.drop(idx)
            self.write_csv(df)
            QMessageBox.information(self, "完成", f"已刪除 Map_ID={map_id}")
            self.populate()
        else:
            QMessageBox.warning(self, "提示", f"找不到 Map_ID={map_id}")
    def on_clear(self):
        self.map_id.clear()
        self.certify_id.clear()
        self.tool_id.clear()
