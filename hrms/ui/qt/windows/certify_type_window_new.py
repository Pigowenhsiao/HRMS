# -*- coding: utf-8 -*-
"""
認證類型管理視窗（SQLite 版本）
簡單 CRUD 操作
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QMessageBox, QTableView, QGroupBox, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem

from hrms.core.db.unit_of_work_sqlite import UnitOfWork
from repositories import CertifyTypeRepository


class CertifyTypeWindow(QDialog):
    """認證類型管理視窗"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("認證類型管理")
        self.resize(700, 500)
        self._init_ui()
        self._load_data()
    
    def _init_ui(self):
        """初始化 UI"""
        main_layout = QVBoxLayout(self)
        
        form_group = QGroupBox("認證類型資料")
        form_layout = QFormLayout()
        
        self.certify_type = QLineEdit()
        self.certify_type.setMaxLength(50)
        form_layout.addRow("認證類型*:", self.certify_type)
        
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
        
        table_group = QGroupBox("認證類型列表")
        table_layout = QVBoxLayout()
        
        self.table_model = QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels(["認證類型"])
        
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
                repo = CertifyTypeRepository(uow.session)
                certify_types = repo.list()
                self._update_table(certify_types)
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"載入資料失敗:\n{str(e)}")
    
    def _update_table(self, certify_types):
        """更新表格"""
        self.table_model.removeRows(0, self.table_model.rowCount())
        
        for row, ct in enumerate(certify_types):
            self.table_model.insertRow(row)
            
            self.table_model.setItem(row, 0, QStandardItem(ct.Certify_Type or ""))
    
    def _on_table_double_click(self, index):
        """表格雙擊"""
        certify_type = self.table_model.item(index.row(), 0).text()
        self._load_certify_type(certify_type)
    
    def _load_certify_type(self, certify_type: str):
        """載入認證類型資料"""
        try:
            with UnitOfWork() as uow:
                repo = CertifyTypeRepository(uow.session)
                ct = repo.get_by_pk(certify_type)
                
                if ct:
                    self.certify_type.setText(ct.Certify_Type or "")
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"載入資料失敗:\n{str(e)}")
    
    def _on_save(self):
        """儲存"""
        if not self.certify_type.text().strip():
            QMessageBox.warning(self, "警告", "認證類型不可空白")
            return
        
        try:
            with UnitOfWork() as uow:
                repo = CertifyTypeRepository(uow.session)
                
                certify_type = self.certify_type.text().strip()
                
                data = {
                    "Certify_Type": certify_type
                }
                
                repo.upsert(certify_type, data)
                
                QMessageBox.information(self, "成功", "認證類型資料已儲存")
                self._load_data()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"儲存資料失敗:\n{str(e)}")
    
    def _on_delete(self):
        """刪除認證類型"""
        certify_type = self.certify_type.text().strip()
        if not certify_type:
            QMessageBox.warning(self, "警告", "請先載入要刪除的認證類型")
            return
        
        reply = QMessageBox.question(
            self,
            "確認刪除",
            f"確定要刪除認證類型 {certify_type} 嗎?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                with UnitOfWork() as uow:
                    repo = CertifyTypeRepository(uow.session)
                    success = repo.delete(certify_type)
                    
                    if success:
                        QMessageBox.information(self, "成功", f"認證類型 {certify_type} 已刪除")
                        self._clear_form()
                        self._load_data()
                    else:
                        QMessageBox.warning(self, "警告", "刪除失敗或認證類型不存在")
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"刪除資料失敗:\n{str(e)}")
    
    def _clear_form(self):
        """清空表單"""
        self.certify_type.clear()
