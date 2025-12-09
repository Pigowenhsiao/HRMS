# -*- coding: utf-8 -*-
"""
認證總表管理視窗（SQLite 版本）
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QMessageBox, QTableView, QGroupBox, QLabel, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from typing import List

from hrms.core.db.unit_of_work_sqlite import UnitOfWork
from repositories import CertifyRepository
from domain.models import Certify


class CertifyWindow(QDialog):
    """認證總表管理視窗"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("認證總表管理")
        self.resize(800, 600)
        self._init_ui()
        self._load_data()
    
    def _init_ui(self):
        """初始化 UI"""
        main_layout = QVBoxLayout(self)
        
        # 搜尋條件
        search_group = QGroupBox("搜尋條件")
        search_layout = QHBoxLayout()
        
        search_layout.addWidget(QLabel("狀態:"))
        self.search_active = QCheckBox("僅顯示有效")
        self.search_active.setChecked(True)
        self.search_active.stateChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_active)
        
        search_layout.addStretch()
        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)
        
        # 表單區域
        form_group = QGroupBox("認證資料")
        form_layout = QFormLayout()
        
        self.certify_id = QLineEdit()
        self.certify_id.setMaxLength(50)
        form_layout.addRow("識別碼*:", self.certify_id)
        
        self.certify_name = QLineEdit()
        self.certify_name.setMaxLength(50)
        form_layout.addRow("認證名稱*:", self.certify_name)
        
        self.certify_desc = QLineEdit()
        self.certify_desc.setMaxLength(200)
        form_layout.addRow("認證說明:", self.certify_desc)
        
        self.active = QCheckBox("有效")
        self.active.setChecked(True)
        form_layout.addRow("狀態:", self.active)
        
        form_group.setLayout(form_layout)
        main_layout.addWidget(form_group)
        
        # 按鈕區域
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
        
        # 表格區域
        table_group = QGroupBox("認證列表")
        table_layout = QVBoxLayout()
        
        self.table_model = QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels(["識別碼", "認證名稱", "認證說明", "狀態"])
        
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.doubleClicked.connect(self._on_table_double_click)
        
        table_layout.addWidget(self.table_view)
        table_group.setLayout(table_layout)
        main_layout.addWidget(table_group)
    
    def _load_data(self):
        """載入資料"""
        try:
            with UnitOfWork() as uow:
                repo = CertifyRepository(uow.session)
                
                filters = {}
                if self.search_active.isChecked():
                    filters["Active"] = True
                
                certifies = repo.list(filters=filters)
                self._update_table(certifies)
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"載入資料失敗:\n{str(e)}")
    
    def _update_table(self, certifies: List[Certify]):
        """更新表格"""
        self.table_model.removeRows(0, self.table_model.rowCount())
        
        for row, certify in enumerate(certifies):
            self.table_model.insertRow(row)
            
            self.table_model.setItem(row, 0, QStandardItem(str(certify.識別碼 or "")))
            self.table_model.setItem(row, 1, QStandardItem(certify.Certify or ""))
            self.table_model.setItem(row, 2, QStandardItem(certify.Certify_Desc or ""))
            
            status = "有效" if certify.Active else "停用"
            self.table_model.setItem(row, 3, QStandardItem(status))
    
    def _on_search_changed(self):
        """搜尋條件變更"""
        self._load_data()
    
    def _on_table_double_click(self, index):
        """表格雙擊"""
        certify_id = self.table_model.item(index.row(), 0).text()
        self._load_certify(certify_id)
    
    def _load_certify(self, certify_id: str):
        """載入認證資料"""
        try:
            with UnitOfWork() as uow:
                repo = CertifyRepository(uow.session)
                
                # 識別碼是整數類型，需要轉換
                try:
                    certify_id_int = int(certify_id)
                except ValueError:
                    QMessageBox.warning(self, "警告", "識別碼必須為數字")
                    return
                
                certify = repo.get_by_pk(certify_id_int)
                
                if certify:
                    self.certify_id.setText(str(certify.識別碼 or ""))
                    self.certify_name.setText(certify.Certify or "")
                    self.certify_desc.setText(certify.Certify_Desc or "")
                    self.active.setChecked(certify.Active)
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"載入認證資料失敗:\n{str(e)}")
    
    def _validate_form(self) -> bool:
        """表單驗證"""
        errors = []
        
        if not self.certify_id.text().strip():
            errors.append("識別碼不可空白")
        
        if not self.certify_name.text().strip():
            errors.append("認證名稱不可空白")
        
        # 檢查識別碼是否為數字
        try:
            int(self.certify_id.text().strip())
        except ValueError:
            errors.append("識別碼必須為數字")
        
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
                repo = CertifyRepository(uow.session)
                
                # 識別碼是整數
                certify_id = int(self.certify_id.text().strip())
                
                data = {
                    "識別碼": certify_id,
                    "Certify": self.certify_name.text().strip(),
                    "Certify_Desc": self.certify_desc.text().strip(),
                    "Active": self.active.isChecked()
                }
                
                repo.upsert(certify_id, data)
                
                QMessageBox.information(self, "成功", "認證資料已儲存")
                self._load_data()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"儲存資料失敗:\n{str(e)}")
    
    def _on_delete(self):
        """刪除"""
        certify_id = self.certify_id.text().strip()
        if not certify_id:
            QMessageBox.warning(self, "警告", "請先載入要刪除的認證")
            return
        
        reply = QMessageBox.question(
            self,
            "確認刪除",
            f"確定要刪除認證 {certify_id} 嗎?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                with UnitOfWork() as uow:
                    repo = CertifyRepository(uow.session)
                    
                    # 識別碼是整數
                    try:
                        certify_id_int = int(certify_id)
                    except ValueError:
                        QMessageBox.warning(self, "警告", "識別碼必須為數字")
                        return
                    
                    success = repo.delete(certify_id_int)
                    
                    if success:
                        QMessageBox.information(self, "成功", f"認證 {certify_id} 已刪除")
                        self._clear_form()
                        self._load_data()
                    else:
                        QMessageBox.warning(self, "警告", "刪除失敗或認證不存在")
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"刪除資料失敗:\n{str(e)}")
    
    def _clear_form(self):
        """清空表單"""
        self.certify_id.clear()
        self.certify_name.clear()
        self.certify_desc.clear()
        self.active.setChecked(True)
