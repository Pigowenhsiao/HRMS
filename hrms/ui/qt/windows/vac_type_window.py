from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QAbstractItemView
)
import pandas as pd
import os

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '..', '..', 'data', 'VAC_Type.csv')

class VacTypeWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("假別（VAC_Type）管理")
        self.resize(600, 400)

        form = QFormLayout()
        self.vac_id = QLineEdit()
        self.vac_name = QLineEdit()
        form.addRow("VAC_ID", self.vac_id)
        form.addRow("VAC_Name", self.vac_name)

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
        self.table.setHorizontalHeaderLabels(["VAC_ID", "VAC_Name"])
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
            df = pd.DataFrame(columns=["VAC_ID", "VAC_Name"])
        return df

    def write_csv(self, df):
        df.to_csv(DATA_PATH, index=False, encoding='utf-8')

    def populate(self):
        df = self.read_csv()
        self.table.setRowCount(0)
        for _, row in df.iterrows():
            i = self.table.rowCount()
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(row.get("VAC_ID", ""))))
            self.table.setItem(i, 1, QTableWidgetItem(str(row.get("VAC_Name", ""))))

    def on_load(self):
        vac_id = self.vac_id.text().strip()
        if not vac_id:
            QMessageBox.warning(self, "提示", "請輸入 VAC_ID")
            return
        df = self.read_csv()
        row = df[df["VAC_ID"] == vac_id]
        if row.empty:
            QMessageBox.information(self, "訊息", f"查無 VAC_ID={vac_id}")
            return
        self.vac_name.setText(str(row.iloc[0]["VAC_Name"]))

    def on_save(self):
        vac_id = self.vac_id.text().strip()
        vac_name = self.vac_name.text().strip()
        if not vac_id:
            QMessageBox.warning(self, "提示", "VAC_ID 不可空白")
            return
        df = self.read_csv()
        idx = df[df["VAC_ID"] == vac_id].index
        if len(idx) > 0:
            df.loc[idx, "VAC_Name"] = vac_name
        else:
            df = pd.concat([df, pd.DataFrame({"VAC_ID": [vac_id], "VAC_Name": [vac_name]})], ignore_index=True)
        self.write_csv(df)
        QMessageBox.information(self, "完成", f"已儲存 VAC_ID={vac_id}")
        self.populate()

    def on_delete(self):
        vac_id = self.vac_id.text().strip()
        if not vac_id:
            QMessageBox.warning(self, "提示", "請輸入 VAC_ID")
            return
        df = self.read_csv()
        idx = df[df["VAC_ID"] == vac_id].index
        if len(idx) > 0:
            df = df.drop(idx)
            self.write_csv(df)
            QMessageBox.information(self, "完成", f"已刪除 VAC_ID={vac_id}")
            self.populate()
        else:
            QMessageBox.warning(self, "提示", f"找不到 VAC_ID={vac_id}")

    def on_clear(self):
        self.vac_id.clear()
        self.vac_name.clear()
