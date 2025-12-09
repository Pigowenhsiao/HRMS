# -*- coding: utf-8 -*-
"""
工站管理視窗（SQLite 版本）
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QMessageBox, QTableView, QGroupBox, QLabel, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from typing import List

from hrms.core.db.unit_of_work_sqlite import UnitOfWork
from repositories import ShopRepository
from domain.models import Shop

class ShopWindow(QDialog):
    """工站管理視窗"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("工站管理")
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
        form_group = QGroupBox("工站資料")
        form_layout = QFormLayout()
        
        self.shop = QLineEdit()
        self.shop.setMaxLength(50)
        form_layout.addRow("工站代碼*:", self.shop)
        
        self.shop_desc = QLineEdit()
        self.shop_desc.setMaxLength(200)
        form_layout.addRow("工站說明*:", self.shop_desc)
        
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
        table_group = QGroupBox("工站列表")
        table_layout = QVBoxLayout()
        
        self.table_model = QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels(["工站代碼", "工站說明", "狀態"])
        
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
                repo = ShopRepository(uow.session)
                
                filters = {}
                if self.search_active.isChecked():
                    filters["Active"] = True
                
                shops = repo.list(filters=filters)
                self._update_table(shops)
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"載入資料失敗:\n{str(e)}")
    
    def _update_table(self, shops: List[Shop]):
        """更新表格"""
        self.table_model.removeRows(0, self.table_model.rowCount())
        
        for row, shop in enumerate(shops):
            self.table_model.insertRow(row)
            
            self.table_model.setItem(row, 0, QStandardItem(shop.SHOP or ""))
            self.table_model.setItem(row, 1, QStandardItem(shop.SHOP_DESC or ""))
            
            status = "有效" if shop.Active else "停用"
            self.table_model.setItem(row, 2, QStandardItem(status))
    
    def _on_search_changed(self):
        """搜尋條件變更"""
        self._load_data()
    
    def _on_table_double_click(self, index):
        """表格雙擊"""
        shop_code = self.table_model.item(index.row(), 0).text()
        self._load_shop(shop_code)
    
    def _load_shop(self, shop_code: str):
        """載入工站資料"""
        try:
            with UnitOfWork() as uow:
                repo = ShopRepository(uow.session)
                shop = repo.get_by_pk(shop_code)
                
                if shop:
                    self.shop.setText(shop.SHOP or "")
                    self.shop_desc.setText(shop.SHOP_DESC or "")
                    self.active.setChecked(shop.Active)
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"載入工站資料失敗:\n{str(e)}")
    
    def _validate_form(self) -> bool:
        """表單驗證"""
        errors = []
        
        if not self.shop.text().strip():
            errors.append("工站代碼不可空白")
        
        if not self.shop_desc.text().strip():
            errors.append("工站說明不可空白")
        
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
                repo = ShopRepository(uow.session)
                
                shop_code = self.shop.text().strip()
                
                data = {
                    "SHOP": shop_code,
                    "SHOP_DESC": self.shop_desc.text().strip(),
                    "Active": self.active.isChecked()
                }
                
                repo.upsert(shop_code, data)
                
                QMessageBox.information(self, "成功", "工站資料已儲存")
                self._load_data()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"儲存資料失敗:\n{str(e)}")
    
    def _on_delete(self):
        """刪除"""
        shop_code = self.shop.text().strip()
        if not shop_code:
            QMessageBox.warning(self, "警告", "請先載入要刪除的工站")
            return
        
        reply = QMessageBox.question(
            self,
            "確認刪除",
            f"確定要刪除工站 {shop_code} 嗎?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                with UnitOfWork() as uow:
                    repo = ShopRepository(uow.session)
                    success = repo.delete(shop_code)
                    
                    if success:
                        QMessageBox.information(self, "成功", f"工站 {shop_code} 已刪除")
                        self._clear_form()
                        self._load_data()
                    else:
                        QMessageBox.warning(self, "警告", "刪除失敗或工站不存在")
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"刪除資料失敗:\n{str(e)}")
    
    def _clear_form(self):
        """清空表單"""
        self.shop.clear()
        self.shop_desc.clear()
        self.active.setChecked(True)