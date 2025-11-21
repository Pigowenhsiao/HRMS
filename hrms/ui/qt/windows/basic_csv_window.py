from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Sequence

import pandas as pd
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QComboBox,
)

from hrms.core.config import settings


def _resolve_data_dir() -> Path:
    """Return the absolute directory that stores the CSV files."""
    configured = Path(settings.database.csv.data_dir)
    if configured.is_absolute():
        return configured
    project_root = Path(__file__).resolve().parents[4]
    return (project_root / configured).resolve()


@dataclass(frozen=True)
class LookupSpec:
    source_csv: str
    value_column: str
    label_columns: Sequence[str] = ()


class BasicCSVWindow(QDialog):
    def __init__(
        self,
        csv_name: str,
        columns: List[str],
        parent=None,
        lookups: Optional[Dict[str, LookupSpec]] = None,
    ):
        super().__init__(parent)
        if not columns:
            raise ValueError("columns must not be empty")
        self.csv_name = csv_name
        self.columns = columns
        self._data_path = _resolve_data_dir() / self.csv_name
        self.lookups = lookups or {}
        self._lookup_widgets: Dict[str, QComboBox] = {}

        self.setWindowTitle(f"{csv_name} CSV Editor")
        self.resize(900, 400)

        form = QFormLayout()
        self.inputs = {}
        for col in self.columns:
            if col in self.lookups:
                combo = QComboBox()
                combo.setEditable(True)
                self.inputs[col] = combo
                self._lookup_widgets[col] = combo
            else:
                self.inputs[col] = QLineEdit()
            form.addRow(col, self.inputs[col])

        btns = QHBoxLayout()
        self.btn_load = QPushButton("Load")
        self.btn_save = QPushButton("Add/Update")
        self.btn_delete = QPushButton("Delete")
        self.btn_clear = QPushButton("Clear")
        self.btn_refresh = QPushButton("Refresh")
        btns.addWidget(self.btn_load)
        btns.addWidget(self.btn_save)
        btns.addWidget(self.btn_delete)
        btns.addWidget(self.btn_clear)
        btns.addWidget(self.btn_refresh)

        self.table = QTableWidget(0, len(self.columns))
        self.table.setHorizontalHeaderLabels(self.columns)
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
        self.table.cellDoubleClicked.connect(self.on_table_double_clicked)

        self.populate()

    def _ensure_parent_dir(self):
        self._data_path.parent.mkdir(parents=True, exist_ok=True)

    def read_csv(self) -> pd.DataFrame:
        if not self._data_path.exists():
            return pd.DataFrame(columns=self.columns)
        try:
            df = pd.read_csv(self._data_path, encoding="utf-8", dtype=str, keep_default_na=False)
        except Exception:
            return pd.DataFrame(columns=self.columns)
        for col in self.columns:
            if col not in df.columns:
                df[col] = ""
        return df[self.columns]

    def write_csv(self, df: pd.DataFrame):
        self._ensure_parent_dir()
        df = df[self.columns]
        df.to_csv(self._data_path, index=False, encoding="utf-8")

    def populate(self):
        self.reload_lookup_options()
        df = self.read_csv()
        self.table.setRowCount(0)
        for _, row in df.iterrows():
            i = self.table.rowCount()
            self.table.insertRow(i)
            for c, col in enumerate(self.columns):
                self.table.setItem(i, c, QTableWidgetItem(str(row.get(col, ""))))

    def _key_value(self) -> str:
        return self._get_widget_value(self.columns[0])

    def _get_widget_value(self, col: str) -> str:
        widget = self.inputs[col]
        if isinstance(widget, QComboBox):
            data = widget.currentData()
            text = widget.currentText().strip()
            if data is not None and str(data).strip():
                return str(data).strip()
            return text
        return widget.text().strip()

    def _set_widget_value(self, col: str, value: str):
        widget = self.inputs[col]
        if isinstance(widget, QComboBox):
            combo: QComboBox = widget
            combo.blockSignals(True)
            idx = combo.findData(value)
            if idx >= 0:
                combo.setCurrentIndex(idx)
            else:
                combo.setCurrentText(value or "")
            combo.blockSignals(False)
        else:
            widget.setText(value or "")

    def _read_external_csv(self, csv_name: str) -> pd.DataFrame:
        path = _resolve_data_dir() / csv_name
        if not path.exists():
            return pd.DataFrame()
        try:
            return pd.read_csv(path, encoding="utf-8", dtype=str, keep_default_na=False)
        except Exception:
            return pd.DataFrame()

    def reload_lookup_options(self):
        for col, spec in self.lookups.items():
            combo = self._lookup_widgets.get(col)
            if combo is None:
                continue
            df = self._read_external_csv(spec.source_csv)
            seen = set()
            options: List[tuple[str, str]] = []
            for _, row in df.iterrows():
                raw_val = str(row.get(spec.value_column, "")).strip()
                if not raw_val or raw_val in seen:
                    continue
                seen.add(raw_val)
                label_parts = []
                for field in spec.label_columns:
                    part = str(row.get(field, "")).strip()
                    if part:
                        label_parts.append(part)
                label = raw_val
                if label_parts:
                    label = f"{raw_val} - {' / '.join(label_parts)}"
                options.append((label, raw_val))
            current_value = self._get_widget_value(col)
            combo.blockSignals(True)
            combo.clear()
            combo.addItem("", "")
            for label, val in options:
                combo.addItem(label, val)
            if current_value:
                idx = combo.findData(current_value)
                if idx >= 0:
                    combo.setCurrentIndex(idx)
                else:
                    combo.setCurrentText(current_value)
            else:
                combo.setCurrentIndex(0)
            combo.blockSignals(False)

    def on_load(self):
        key = self._key_value()
        if not key:
            QMessageBox.warning(self, "Warning", f"Please enter {self.columns[0]}")
            return
        df = self.read_csv()
        row = df[df[self.columns[0]] == key]
        if row.empty:
            QMessageBox.information(self, "Info", f"No data found for {self.columns[0]}={key}")
            return
        for col in self.columns:
            self._set_widget_value(col, str(row.iloc[0].get(col, "")))

    def on_save(self):
        key = self._key_value()
        if not key:
            QMessageBox.warning(self, "Warning", f"{self.columns[0]} is required.")
            return
        df = self.read_csv()
        idx = df[df[self.columns[0]] == key].index
        row_data = {col: self._get_widget_value(col) for col in self.columns}
        if len(idx) > 0:
            for col in self.columns:
                df.loc[idx, col] = row_data[col]
        else:
            df = pd.concat([df, pd.DataFrame([row_data])], ignore_index=True)
        self.write_csv(df)
        QMessageBox.information(self, "Success", f"Saved {self.columns[0]}={key}")
        self.populate()

    def on_delete(self):
        key = self._key_value()
        if not key:
            QMessageBox.warning(self, "Warning", f"Please enter {self.columns[0]}")
            return
        df = self.read_csv()
        idx = df[df[self.columns[0]] == key].index
        if len(idx) > 0:
            df = df.drop(idx)
            self.write_csv(df)
            QMessageBox.information(self, "Success", f"Deleted {self.columns[0]}={key}")
            self.populate()
        else:
            QMessageBox.warning(self, "Warning", f"{self.columns[0]}={key} not found.")

    def on_clear(self):
        for col in self.columns:
            widget = self.inputs[col]
            if isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)
                widget.setCurrentText("")
            else:
                widget.clear()

    def on_table_double_clicked(self, row: int, _column: int):
        for idx, col in enumerate(self.columns):
            item = self.table.item(row, idx)
            if item:
                self._set_widget_value(col, item.text())
