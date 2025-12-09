# -*- coding: utf-8 -*-
"""
假別管理視窗（SQLite 版本）
簡單 CRUD 操作
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QMessageBox, QTableView, QGroupBox, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem

from hrms.core.db.unit_of_work_sqlite import UnitOfWork
from repositories import VacTypeRepository


class VacTypeWindow(QDialog):
    """假別管理視窗"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("假別管理")
        self.resize(700, 500)
        self._init_ui()
        self._load_data()
    
    def _init_ui(self):
        """初始化 UI"""
        main_layout = QVBoxLayout(self)
        
        form_group = QGroupBox("假別資料")
        form_layout = QFormLayout()
        
        self.vac_id = QLineEdit()
        self.vac_id.setMaxLength(10)
        form_layout.addRow("假別代碼*:", self.vac_id)
        
        self.vac_desc = QTextEdit()
        self.vac_desc.setMaximumHeight(60)
        form_layout.addRow("假別說明:", self.vac_desc)
        
        self.active = QCheckBox("有效")
        self.active.setChecked(True)
        form_layout.addRow("狀態:", self.active)
        
        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)
        
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
        
        table_group = QGroupBox("假別列表")
        table_layout = QVBoxLayout()
        
        self.table_model = QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels(["假別代碼", "假別說明", "狀態"])
        
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
                repo = VacTypeRepository(uow.session)
                vac_types = repo.list()
                self._update_table(vac_types)
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"載入資料失敗:\n{str(e)}")
    
    def _update_table(self, vac_types):
        """更新表格"""
        self.table_model.removeRows(0, self.table_model.rowCount())
        
        for row, vac in enumerate(vac_types):
            self.table_model.insertRow(row)
            
            self.table_model.setItem(row, 0, QStandardItem(vac.VAC_ID or ""))
            self.table_model.setItem(row, 1, QStandardItem(vac.VAC_DESC or ""))
            
            status = "有效" if vac.Active else "停用"
            self.table_model.setItem(row, 2, QStandardItem(status))
    
    def _on_table_double_click(self, index):
        """表格雙擊"""
        vac_id = self.table_model.item(index.row(), 0).text()
        self._load_vac_type(vac_id)
    
    def _load_vac_type(self, vac_id: str):
        """載入假別資料"""
        try:
            with UnitOfWork() as uow:
                repo = VacTypeRepository(uow.session)
                vac = repo.get_by_pk(vac_id)
                
                if vac:
                    self.vac_id.setText(vac.VAC_ID or "")
                    self.vac_desc.setPlainText(vac.VAC_DESC or "")
                    self.active.setChecked(vac.Active)
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"載入資料失敗:\n{str(e)}")
    
    def _on_save(self):
        """儲存"""
        if not self.vac_id.text().strip():
            QMessageBox.warning(self, "警告", "假別代碼不可空白")
            return
        
        try:
            with UnitOfWork() as uow:
                repo = VacTypeRepository(uow.session)
                
                vac_id = self.vac_id.text().strip()
                
                data = {
                    "VAC_ID": vac_id,
                    "VAC_DESC": self.vac_desc.toPlainText(),
                    "Active": self.active.isChecked()
                }
                
                repo.upsert(vac_id, data)
                
                QMessageBox.information(self, "成功", "假別資料已儲存")
                self._load_data()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"儲存資料失敗:\n{str(e)}")
    
    def _on_delete(self):
        """刪除假別"""
        vac_id = self.vac_id.text().strip()
        if not vac_id:
            QMessageBox.warning(self, "警告", "請先載入要刪除的假別")
            return
        
        reply = QMessageBox.question(
            self,
            "確認刪除",
            f"確定要刪除假別 {vac_id} 嗎?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                with UnitOfWork() as uow:
                    repo = VacTypeRepository(uow.session)
                    success = repo.delete(vac_id)
                    
                    if success:
                        QMessageBox.information(self, "成功", f"假別 {vac_id} 已刪除")
                        self._clear_form()
                        self._load_data()
                    else:
                        QMessageBox.warning(self, "警告", "刪除失敗或假別不存在")
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"刪除資料失敗:\n{str(e)}")
    
    def _clear_form(self):
        """清空表單"""
        self.vac_id.clear()
        self.vac_desc.clear()
        self.active.setChecked(True)
