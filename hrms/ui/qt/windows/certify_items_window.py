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
        self.item_id = QLineEdit()
        self.item_name = QLineEdit()
        form.addRow("Item_ID", self.item_id)
        form.addRow("Item_Name", self.item_name)
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
        self.table.setHorizontalHeaderLabels(["Item_ID", "Item_Name"])
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
            df = pd.DataFrame(columns=["Item_ID", "Item_Name"])
        return df
    def write_csv(self, df):
        df.to_csv(DATA_PATH, index=False, encoding='utf-8')
    def populate(self):
        df = self.read_csv()
        self.table.setRowCount(0)
        for _, row in df.iterrows():
            i = self.table.rowCount()
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(row["Item_ID"])))
            self.table.setItem(i, 1, QTableWidgetItem(str(row["Item_Name"])))
    def on_load(self):
        item_id = self.item_id.text().strip()
        if not item_id:
            QMessageBox.warning(self, "提示", "請輸入 Item_ID")
            return
        df = self.read_csv()
        row = df[df["Item_ID"] == item_id]
        if row.empty:
            QMessageBox.information(self, "訊息", f"查無 Item_ID={item_id}")
            return
        self.item_name.setText(str(row.iloc[0]["Item_Name"]))
    def on_save(self):
        item_id = self.item_id.text().strip()
        item_name = self.item_name.text().strip()
        if not item_id:
            QMessageBox.warning(self, "提示", "Item_ID 不可空白")
            return
        df = self.read_csv()
        idx = df[df["Item_ID"] == item_id].index
        if len(idx) > 0:
            df.loc[idx, "Item_Name"] = item_name
        else:
            df = pd.concat([df, pd.DataFrame({"Item_ID": [item_id], "Item_Name": [item_name]})], ignore_index=True)
        self.write_csv(df)
        QMessageBox.information(self, "完成", f"已儲存 Item_ID={item_id}")
        self.populate()
    def on_delete(self):
        item_id = self.item_id.text().strip()
        if not item_id:
            QMessageBox.warning(self, "提示", "請輸入 Item_ID")
            return
        df = self.read_csv()
        idx = df[df["Item_ID"] == item_id].index
        if len(idx) > 0:
            df = df.drop(idx)
            self.write_csv(df)
            QMessageBox.information(self, "完成", f"已刪除 Item_ID={item_id}")
            self.populate()
        else:
            QMessageBox.warning(self, "提示", f"找不到 Item_ID={item_id}")
    def on_clear(self):
        self.item_id.clear()
        self.item_name.clear()
