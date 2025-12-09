# -*- coding: utf-8 -*-
"""
權限管理視窗（SQLite 版本）
使用者帳號與權限設定
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QMessageBox, QTableView, QGroupBox, QCheckBox, QComboBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from typing import List

from hrms.core.db.unit_of_work_sqlite import UnitOfWork
from repositories import AuthorityRepository
from domain.models import Authority


class AuthorityWindow(QDialog):
    """權限管理視窗"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("權限管理")
        self.resize(900, 600)
        self._init_ui()
        self._load_data()
    
    def _init_ui(self):
        """初始化 UI"""
        main_layout = QVBoxLayout(self)
        
        # 表單
        form_group = QGroupBox("權限資料")
        form_layout = QFormLayout()
        
        self.s_account = QLineEdit()
        self.s_account.setMaxLength(50)
        form_layout.addRow("使用者帳號*:", self.s_account)
        
        self.auth_type = QComboBox()
        self.auth_type.setEditable(True)
        self.auth_type.addItems(["", "01", "02", "03", "04", "05", "06", "07", "08", "09", "10"])
        form_layout.addRow("權限類型:", self.auth_type)
        
        self.active = QCheckBox("有效")
        self.active.setChecked(True)
        form_layout.addRow("狀態:", self.active)
        
        self.update_date = QLineEdit()
        self.update_date.setPlaceholderText("自動填入")
        self.update_date.setReadOnly(True)
        form_layout.addRow("更新日期:", self.update_date)
        
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
        table_group = QGroupBox("權限列表")
        table_layout = QVBoxLayout()
        
        self.table_model = QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels(["帳號", "權限類型", "更新日期", "有效"])
        
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
                repo = AuthorityRepository(uow.session)
                authorities = repo.list()
                self._update_table(authorities)
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"載入資料失敗:\n{str(e)}")
    
    def _update_table(self, authorities: List[Authority]):
        """更新表格"""
        self.table_model.removeRows(0, self.table_model.rowCount())
        
        for row, auth in enumerate(authorities):
            self.table_model.insertRow(row)
            
            self.table_model.setItem(row, 0, QStandardItem(auth.S_Account or ""))
            self.table_model.setItem(row, 1, QStandardItem(auth.Auth_type or ""))
            self.table_model.setItem(row, 2, QStandardItem(auth.Update_Date or ""))
            
            status = "是" if auth.Active else "否"
            self.table_model.setItem(row, 3, QStandardItem(status))
    
    def _on_table_double_click(self, index):
        """表格雙擊"""
        account = self.table_model.item(index.row(), 0).text()
        self._load_authority(account)
    
    def _load_authority(self, account: str):
        """載入權限資料"""
        try:
            with UnitOfWork() as uow:
                repo = AuthorityRepository(uow.session)
                auth = repo.get_by_pk(account)
                
                if auth:
                    self.s_account.setText(auth.S_Account or "")
                    self.auth_type.setCurrentText(auth.Auth_type or "")
                    self.active.setChecked(auth.Active)
                    self.update_date.setText(auth.Update_Date or "")
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"載入資料失敗:\n{str(e)}")
    
    def _on_save(self):
        """儲存"""
        if not self.s_account.text().strip():
            QMessageBox.warning(self, "警告", "使用者帳號不可空白")
            return
        
        try:
            with UnitOfWork() as uow:
                repo = AuthorityRepository(uow.session)
                
                account = self.s_account.text().strip()
                
                import datetime
                data = {
                    "S_Account": account,
                    "Auth_type": self.auth_type.currentText().strip(),
                    "Active": self.active.isChecked(),
                    "Update_Date": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                
                repo.upsert(account, data)
                
                QMessageBox.information(self, "成功", "權限資料已儲存")
                self._load_data()
                self._clear_form()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"儲存資料失敗:\n{str(e)}")
    
    def _on_delete(self):
        """刪除"""
        account = self.s_account.text().strip()
        if not account:
            QMessageBox.warning(self, "警告", "請先載入要刪除的帳號")
            return
        
        reply = QMessageBox.question(
            self,
            "確認刪除",
            f"確定要刪除帳號 {account} 的權限嗎?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                with UnitOfWork() as uow:
                    repo = AuthorityRepository(uow.session)
                    success = repo.delete(account)
                    
                    if success:
                        QMessageBox.information(self, "成功", f"帳號 {account} 的權限已刪除")
                        self._clear_form()
                        self._load_data()
                    else:
                        QMessageBox.warning(self, "警告", "刪除失敗或帳號不存在")
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"刪除資料失敗:\n{str(e)}")
    
    def _clear_form(self):
        """清空表單"""
        self.s_account.clear()
        self.auth_type.setCurrentIndex(0)
        self.active.setChecked(True)
        self.update_date.clear()
