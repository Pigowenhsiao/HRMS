from PySide6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QAbstractItemView
import pandas as pd
import os
class BasicCSVWindow(QDialog):
    def __init__(self, csv_name, columns, parent=None):
        super().__init__(parent)
        self.csv_name = csv_name
        self.columns = columns
        self.setWindowTitle(f"{csv_name} 管理")
        self.resize(900, 400)
        form = QFormLayout()
        self.inputs = {}
        for col in columns:
            self.inputs[col] = QLineEdit()
            form.addRow(col, self.inputs[col])
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
        self.table = QTableWidget(0, len(columns))
        self.table.setHorizontalHeaderLabels(columns)
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
    def get_data_path(self):
        return os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '..', '..', 'data', self.csv_name)
    def read_csv(self):
        try:
            df = pd.read_csv(self.get_data_path(), encoding='utf-8')
        except Exception:
            df = pd.DataFrame(columns=self.columns)
        return df
    def write_csv(self, df):
        df.to_csv(self.get_data_path(), index=False, encoding='utf-8')
    def populate(self):
        df = self.read_csv()
        self.table.setRowCount(0)
        for _, row in df.iterrows():
            i = self.table.rowCount()
            self.table.insertRow(i)
            for c, col in enumerate(self.columns):
                self.table.setItem(i, c, QTableWidgetItem(str(row.get(col, ""))))
    def on_load(self):
        key = self.inputs[self.columns[0]].text().strip()
        if not key:
            QMessageBox.warning(self, "提示", f"請輸入 {self.columns[0]}")
            return
        df = self.read_csv()
        row = df[df[self.columns[0]] == key]
        if row.empty:
            QMessageBox.information(self, "訊息", f"查無 {self.columns[0]}={key}")
            return
        for col in self.columns:
            self.inputs[col].setText(str(row.iloc[0].get(col, "")))
    def on_save(self):
        key = self.inputs[self.columns[0]].text().strip()
        if not key:
            QMessageBox.warning(self, "提示", f"{self.columns[0]} 不可空白")
            return
        df = self.read_csv()
        idx = df[df[self.columns[0]] == key].index
        row_data = {col: self.inputs[col].text().strip() for col in self.columns}
        if len(idx) > 0:
            for col in self.columns:
                df.loc[idx, col] = row_data[col]
        else:
            df = pd.concat([df, pd.DataFrame([row_data])], ignore_index=True)
        self.write_csv(df)
        QMessageBox.information(self, "完成", f"已儲存 {self.columns[0]}={key}")
        self.populate()
    def on_delete(self):
        key = self.inputs[self.columns[0]].text().strip()
        if not key:
            QMessageBox.warning(self, "提示", f"請輸入 {self.columns[0]}")
            return
        df = self.read_csv()
        idx = df[df[self.columns[0]] == key].index
        if len(idx) > 0:
            df = df.drop(idx)
            self.write_csv(df)
            QMessageBox.information(self, "完成", f"已刪除 {self.columns[0]}={key}")
            self.populate()
        else:
            QMessageBox.warning(self, "提示", f"找不到 {self.columns[0]}={key}")
    def on_clear(self):
        for col in self.columns:
            self.inputs[col].clear()
