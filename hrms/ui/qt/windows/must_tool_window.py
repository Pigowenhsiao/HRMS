from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QAbstractItemView
import pandas as pd
import os
DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '..', '..', 'data', 'MUST_TOOL.csv')
class MustToolWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("必備工具（MUST_TOOL）管理")
        self.resize(600, 400)
        form = QFormLayout()
        self.tool_id = QLineEdit()
        self.tool_name = QLineEdit()
        form.addRow("Tool_ID", self.tool_id)
        form.addRow("Tool_Name", self.tool_name)
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
        self.table.setHorizontalHeaderLabels(["Tool_ID", "Tool_Name"])
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
            df = pd.DataFrame(columns=["Tool_ID", "Tool_Name"])
        return df
    def write_csv(self, df):
        df.to_csv(DATA_PATH, index=False, encoding='utf-8')
    def populate(self):
        df = self.read_csv()
        self.table.setRowCount(0)
        for _, row in df.iterrows():
            i = self.table.rowCount()
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(row["Tool_ID"])))
            self.table.setItem(i, 1, QTableWidgetItem(str(row["Tool_Name"])))
    def on_load(self):
        tool_id = self.tool_id.text().strip()
        if not tool_id:
            QMessageBox.warning(self, "提示", "請輸入 Tool_ID")
            return
        df = self.read_csv()
        row = df[df["Tool_ID"] == tool_id]
        if row.empty:
            QMessageBox.information(self, "訊息", f"查無 Tool_ID={tool_id}")
            return
        self.tool_name.setText(str(row.iloc[0]["Tool_Name"]))
    def on_save(self):
        tool_id = self.tool_id.text().strip()
        tool_name = self.tool_name.text().strip()
        if not tool_id:
            QMessageBox.warning(self, "提示", "Tool_ID 不可空白")
            return
        df = self.read_csv()
        idx = df[df["Tool_ID"] == tool_id].index
        if len(idx) > 0:
            df.loc[idx, "Tool_Name"] = tool_name
        else:
            df = pd.concat([df, pd.DataFrame({"Tool_ID": [tool_id], "Tool_Name": [tool_name]})], ignore_index=True)
        self.write_csv(df)
        QMessageBox.information(self, "完成", f"已儲存 Tool_ID={tool_id}")
        self.populate()
    def on_delete(self):
        tool_id = self.tool_id.text().strip()
        if not tool_id:
            QMessageBox.warning(self, "提示", "請輸入 Tool_ID")
            return
        df = self.read_csv()
        idx = df[df["Tool_ID"] == tool_id].index
        if len(idx) > 0:
            df = df.drop(idx)
            self.write_csv(df)
            QMessageBox.information(self, "完成", f"已刪除 Tool_ID={tool_id}")
            self.populate()
        else:
            QMessageBox.warning(self, "提示", f"找不到 Tool_ID={tool_id}")
    def on_clear(self):
        self.tool_id.clear()
        self.tool_name.clear()
