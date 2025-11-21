from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QAbstractItemView
)
import pandas as pd
import os

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '..', '..', 'data', 'SHOP.csv')

class ShopWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("廠區（SHOP）管理")
        self.resize(600, 400)

        form = QFormLayout()
        self.shop_id = QLineEdit()
        self.shop_name = QLineEdit()
        form.addRow("Shop_ID", self.shop_id)
        form.addRow("Shop_Name", self.shop_name)

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
        self.table.setHorizontalHeaderLabels(["Shop_ID", "Shop_Name"])
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
            df = pd.DataFrame(columns=["Shop_ID", "Shop_Name"])
        return df

    def write_csv(self, df):
        df.to_csv(DATA_PATH, index=False, encoding='utf-8')

    def populate(self):
        df = self.read_csv()
        self.table.setRowCount(0)
        for _, row in df.iterrows():
            i = self.table.rowCount()
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(row.get("Shop_ID", ""))))
            self.table.setItem(i, 1, QTableWidgetItem(str(row.get("Shop_Name", ""))))

    def on_load(self):
        shop_id = self.shop_id.text().strip()
        if not shop_id:
            QMessageBox.warning(self, "提示", "請輸入 Shop_ID")
            return
        df = self.read_csv()
        row = df[df["Shop_ID"] == shop_id]
        if row.empty:
            QMessageBox.information(self, "訊息", f"查無 Shop_ID={shop_id}")
            return
        self.shop_name.setText(str(row.iloc[0]["Shop_Name"]))

    def on_save(self):
        shop_id = self.shop_id.text().strip()
        shop_name = self.shop_name.text().strip()
        if not shop_id:
            QMessageBox.warning(self, "提示", "Shop_ID 不可空白")
            return
        df = self.read_csv()
        idx = df[df["Shop_ID"] == shop_id].index
        if len(idx) > 0:
            df.loc[idx, "Shop_Name"] = shop_name
        else:
            df = pd.concat([df, pd.DataFrame({"Shop_ID": [shop_id], "Shop_Name": [shop_name]})], ignore_index=True)
        self.write_csv(df)
        QMessageBox.information(self, "完成", f"已儲存 Shop_ID={shop_id}")
        self.populate()

    def on_delete(self):
        shop_id = self.shop_id.text().strip()
        if not shop_id:
            QMessageBox.warning(self, "提示", "請輸入 Shop_ID")
            return
        df = self.read_csv()
        idx = df[df["Shop_ID"] == shop_id].index
        if len(idx) > 0:
            df = df.drop(idx)
            self.write_csv(df)
            QMessageBox.information(self, "完成", f"已刪除 Shop_ID={shop_id}")
            self.populate()
        else:
            QMessageBox.warning(self, "提示", f"找不到 Shop_ID={shop_id}")

    def on_clear(self):
        self.shop_id.clear()
        self.shop_name.clear()
