from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox, QAbstractItemView
)
import pandas as pd
import os

DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), '..', '..', 'data', 'TRAINING_RECORD.csv')

class TrainingRecordWindow(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("培訓紀錄（TRAINING_RECORD）管理")
        self.resize(800, 400)

        form = QFormLayout()
        self.tr_id = QLineEdit()
        self.emp_id = QLineEdit()
        self.tr_name = QLineEdit()
        self.tr_date = QLineEdit()
        form.addRow("TR_ID", self.tr_id)
        form.addRow("EMP_ID", self.emp_id)
        form.addRow("TR_Name", self.tr_name)
        form.addRow("TR_Date", self.tr_date)

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
        self.table.setHorizontalHeaderLabels(["TR_ID", "EMP_ID", "TR_Name", "TR_Date"])
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
            df = pd.DataFrame(columns=["TR_ID", "EMP_ID", "TR_Name", "TR_Date"])
        return df

    def write_csv(self, df):
        df.to_csv(DATA_PATH, index=False, encoding='utf-8')

    def populate(self):
        df = self.read_csv()
        self.table.setRowCount(0)
        for _, row in df.iterrows():
            i = self.table.rowCount()
            self.table.insertRow(i)
            self.table.setItem(i, 0, QTableWidgetItem(str(row["TR_ID"])))
            self.table.setItem(i, 1, QTableWidgetItem(str(row["EMP_ID"])))
            self.table.setItem(i, 2, QTableWidgetItem(str(row["TR_Name"])))
            self.table.setItem(i, 3, QTableWidgetItem(str(row["TR_Date"])))

    def on_load(self):
        tr_id = self.tr_id.text().strip()
        if not tr_id:
            QMessageBox.warning(self, "提示", "請輸入 TR_ID")
            return
        df = self.read_csv()
        row = df[df["TR_ID"] == tr_id]
        if row.empty:
            QMessageBox.information(self, "訊息", f"查無 TR_ID={tr_id}")
            return
        self.emp_id.setText(str(row.iloc[0]["EMP_ID"]))
        self.tr_name.setText(str(row.iloc[0]["TR_Name"]))
        self.tr_date.setText(str(row.iloc[0]["TR_Date"]))

    def on_save(self):
        tr_id = self.tr_id.text().strip()
        emp_id = self.emp_id.text().strip()
        tr_name = self.tr_name.text().strip()
        tr_date = self.tr_date.text().strip()
        if not tr_id:
            QMessageBox.warning(self, "提示", "TR_ID 不可空白")
            return
        df = self.read_csv()
        idx = df[df["TR_ID"] == tr_id].index
        if len(idx) > 0:
            df.loc[idx, "EMP_ID"] = emp_id
            df.loc[idx, "TR_Name"] = tr_name
            df.loc[idx, "TR_Date"] = tr_date
        else:
            df = pd.concat([df, pd.DataFrame({"TR_ID": [tr_id], "EMP_ID": [emp_id], "TR_Name": [tr_name], "TR_Date": [tr_date]})], ignore_index=True)
        self.write_csv(df)
        QMessageBox.information(self, "完成", f"已儲存 TR_ID={tr_id}")
        self.populate()

    def on_delete(self):
        tr_id = self.tr_id.text().strip()
        if not tr_id:
            QMessageBox.warning(self, "提示", "請輸入 TR_ID")
            return
        df = self.read_csv()
        idx = df[df["TR_ID"] == tr_id].index
        if len(idx) > 0:
            df = df.drop(idx)
            self.write_csv(df)
            QMessageBox.information(self, "完成", f"已刪除 TR_ID={tr_id}")
            self.populate()
        else:
            QMessageBox.warning(self, "提示", f"找不到 TR_ID={tr_id}")

    def on_clear(self):
        self.tr_id.clear()
        self.emp_id.clear()
        self.tr_name.clear()
        self.tr_date.clear()
