# -*- coding: utf-8 -*-
"""
班別管理視窗（SQLite 版本）
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QMessageBox, QComboBox, QTableView, QGroupBox, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from typing import List

from hrms.core.db.unit_of_work_sqlite import UnitOfWork
from repositories import ShiftRepository, SectionRepository
from domain.models import Shift


class ShiftWindow(QDialog):
    """班別管理視窗"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("班別管理")
        self.resize(900, 600)
        self._init_ui()
        self._load_data()
    
    def _init_ui(self):
        """初始化 UI"""
        main_layout = QVBoxLayout(self)
        
        # 表單
        form_group = QGroupBox("班別資料")
        form_layout = QFormLayout()
        
        self.shift = QLineEdit()
        self.shift.setMaxLength(50)
        form_layout.addRow("班別代碼*:", self.shift)
        
        self.dept = QComboBox()
        self.dept.setEditable(True)
        form_layout.addRow("部門*:", self.dept)
        
        self.shift_desc = QLineEdit()
        self.shift_desc.setMaxLength(200)
        form_layout.addRow("班別說明:", self.shift_desc)
        
        self.supervisor = QLineEdit()
        self.supervisor.setMaxLength(50)
        form_layout.addRow("主管:", self.supervisor)
        
        self.active = QCheckBox("有效")
        self.active.setChecked(True)
        form_layout.addRow("狀態:", self.active)
        
        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)
        
        # 按鈕
        btn_layout = QHBoxLayout()
        self.btn_save = QPushButton("儲存")
        self.btn_save.clicked.connect(self._on_save)
        btn_layout.addWidget(self.btn_save)
        
        self.btn_delete = QPushButton("刪除")
        self.btn_delete.clicked.connect(self._on_delete)
        btn_layout.addWidget(self.btn_delete)
        
        self.btn_clear = QPushButton("清空")
        self.btn_clear.clicked.connect(self._clear_form)
        btn_layout.addWidget(self.btn_clear)
        
        btn_layout.addStretch()
        main_layout.addLayout(btn_layout)
        
        # 表格
        table_group = QGroupBox("班別列表")
        table_layout = QVBoxLayout()
        
        self.table_model = QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels(["班別", "部門", "說明", "主管", "狀態"])
        
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.doubleClicked.connect(self._on_table_double_click)
        
        table_layout.addWidget(self.table_view)
        table_group.setLayout(table_layout)
        main_layout.addWidget(table_group)
    
    def _load_data(self):
        """載入資料"""
        try:
            with UnitOfWork() as uow:
                shift_repo = ShiftRepository(uow.session)
                shifts = shift_repo.list()
                self._update_table(shifts)
                
                # 載入部門選項
                dept_repo = SectionRepository(uow.session)
                sections = dept_repo.list()
                self.dept.clear()
                for section in sections:
                    self.dept.addItem(section.Dept_Code, section.Dept_Code)
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"載入資料失敗:\n{str(e)}")
    
    def _update_table(self, shifts: List[Shift]):
        """更新表格"""
        self.table_model.removeRows(0, self.table_model.rowCount())
        
        for row, shift in enumerate(shifts):
            self.table_model.insertRow(row)
            
            self.table_model.setItem(row, 0, QStandardItem(shift.Shift or ""))
            self.table_model.setItem(row, 1, QStandardItem(shift.L_Section or ""))
            self.table_model.setItem(row, 2, QStandardItem(shift.Shift_Desc or ""))
            self.table_model.setItem(row, 3, QStandardItem(shift.Supervisor or ""))
            
            status = "有效" if shift.Active else "停用"
            self.table_model.setItem(row, 4, QStandardItem(status))
    
    def _on_table_double_click(self, index):
        """表格雙擊"""
        shift_code = self.table_model.item(index.row(), 0).text()
        self._load_shift(shift_code)
    
    def _load_shift(self, shift: str):
        """載入班別資料"""
        try:
            with UnitOfWork() as uow:
                repo = ShiftRepository(uow.session)
                shift_obj = repo.get_by_pk(shift)
                
                if shift_obj:
                    self.shift.setText(shift_obj.Shift or "")
                    self.dept.setCurrentText(shift_obj.L_Section or "")
                    self.shift_desc.setText(shift_obj.Shift_Desc or "")
                    self.supervisor.setText(shift_obj.Supervisor or "")
                    self.active.setChecked(shift_obj.Active)
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"載入資料失敗:\n{str(e)}")
    
    def _validate_form(self) -> bool:
        """表單驗證"""
        errors = []
        
        if not self.shift.text().strip():
            errors.append("班別代碼不可空白")
        
        if not self.dept.currentText().strip():
            errors.append("部門不可空白")
        
        if errors:
            QMessageBox.warning(self, "資料驗證失敗", "\n".join(errors))
            return False
        
        return True
    
    def _on_save(self):
        """儲存"""
        if not self._validate_form():
            return
        
        try:
            with UnitOfWork() as uow:
                repo = ShiftRepository(uow.session)
                
                shift_code = self.shift.text().strip()
                
                data = {
                    "Shift": shift_code,
                    "L_Section": self.dept.currentText().strip(),
                    "Shift_Desc": self.shift_desc.text().strip(),
                    "Supervisor": self.supervisor.text().strip(),
                    "Active": self.active.isChecked()
                }
                
                repo.upsert(shift_code, data)
                
                QMessageBox.information(self, "成功", "班別資料已儲存")
                self._load_data()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"儲存資料失敗:\n{str(e)}")
    
    def _on_delete(self):
        """刪除"""
        shift = self.shift.text().strip()
        if not shift:
            QMessageBox.warning(self, "警告", "請先載入要刪除的班別")
            return
        
        reply = QMessageBox.question(
            self,
            "確認刪除",
            f"確定要刪除班別 {shift} 嗎?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                with UnitOfWork() as uow:
                    repo = ShiftRepository(uow.session)
                    success = repo.delete(shift)
                    
                    if success:
                        QMessageBox.information(self, "成功", f"班別 {shift} 已刪除")
                        self._clear_form()
                        self._load_data()
                    else:
                        QMessageBox.warning(self, "警告", "刪除失敗或班別不存在")
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"刪除資料失敗:\n{str(e)}")
    
    def _clear_form(self):
        """清空表單"""
        self.shift.clear()
        self.dept.setCurrentIndex(0)
        self.shift_desc.clear()
        self.supervisor.clear()
        self.active.setChecked(True)
