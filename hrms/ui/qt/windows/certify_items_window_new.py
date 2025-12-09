# -*- coding: utf-8 -*-
"""
證照項目管理視窗（SQLite 版本）
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QMessageBox, QComboBox, QTableView, QGroupBox, QLabel, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from typing import List

from hrms.core.db.unit_of_work_sqlite import UnitOfWork
from repositories import CertifyItemRepository, CertifyTypeRepository, SectionRepository
from domain.models import CertifyItem


class CertifyItemsWindow(QDialog):
    """證照項目管理視窗"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("證照項目管理")
        self.resize(1100, 700)
        self._init_ui()
        self._load_data()
    
    def _init_ui(self):
        """初始化 UI"""
        main_layout = QVBoxLayout(self)
        
        # 搜尋條件
        search_group = QGroupBox("搜尋條件")
        search_layout = QHBoxLayout()
        
        search_layout.addWidget(QLabel("部門:"))
        self.search_dept = QComboBox()
        self.search_dept.setEditable(True)
        self.search_dept.currentTextChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_dept)
        
        search_layout.addWidget(QLabel("證照類型:"))
        self.search_type = QComboBox()
        self.search_type.setEditable(True)
        self.search_type.currentTextChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_type)
        
        search_layout.addStretch()
        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)
        
        # 表單區域
        form_group = QGroupBox("證照項目資料")
        form_layout = QFormLayout()
        
        self.dept = QComboBox()
        self.dept.setEditable(True)
        form_layout.addRow("部門*:", self.dept)
        
        self.certify_id = QLineEdit()
        self.certify_id.setMaxLength(50)
        form_layout.addRow("證照ID*:", self.certify_id)
        
        self.certify_type = QComboBox()
        self.certify_type.setEditable(True)
        form_layout.addRow("證照類型*:", self.certify_type)
        
        self.certify_name = QLineEdit()
        self.certify_name.setMaxLength(500)
        form_layout.addRow("證照名稱*:", self.certify_name)
        
        self.certify_time = QLineEdit()
        self.certify_time.setMaxLength(20)
        form_layout.addRow("證照時數:", self.certify_time)
        
        self.certify_grade = QLineEdit()
        self.certify_grade.setMaxLength(50)
        form_layout.addRow("證照等級:", self.certify_grade)
        
        self.score = QLineEdit()
        self.score.setPlaceholderText("分數")
        form_layout.addRow("分數:", self.score)
        
        self.remark = QTextEdit()
        self.remark.setMaximumHeight(60)
        form_layout.addRow("備註:", self.remark)
        
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
        table_group = QGroupBox("證照項目列表")
        table_layout = QVBoxLayout()
        
        self.table_model = QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels(["部門", "證照ID", "類型", "名稱", "時數", "等級", "分數", "狀態"])
        
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
                item_repo = CertifyItemRepository(uow.session)
                items = item_repo.list()
                self._update_table(items)
                
                # 載入下拉選單
                self._load_comboboxes()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"載入資料失敗:\n{str(e)}")
    
    def _load_comboboxes(self):
        """載入下拉選單選項"""
        try:
            with UnitOfWork() as uow:
                # 部門
                section_repo = SectionRepository(uow.session)
                sections = section_repo.list()
                self.search_dept.clear()
                self.search_dept.addItem("", "")
                self.dept.clear()
                for section in sections:
                    self.search_dept.addItem(section.Dept_Code, section.Dept_Code)
                    self.dept.addItem(section.Dept_Code, section.Dept_Code)
                
                # 證照類型
                type_repo = CertifyTypeRepository(uow.session)
                types = type_repo.list()
                self.search_type.clear()
                self.search_type.addItem("", "")
                self.certify_type.clear()
                for ct in types:
                    self.search_type.addItem(ct.Certify_Type, ct.Certify_Type)
                    self.certify_type.addItem(ct.Certify_Type, ct.Certify_Type)
        except Exception as e:
            print(f"載入下拉選單失敗: {e}")
    
    def _update_table(self, items: List[CertifyItem]):
        """更新表格"""
        self.table_model.removeRows(0, self.table_model.rowCount())
        
        for row, item in enumerate(items):
            self.table_model.insertRow(row)
            
            self.table_model.setItem(row, 0, QStandardItem(item.Dept or ""))
            self.table_model.setItem(row, 1, QStandardItem(item.Certify_ID or ""))
            self.table_model.setItem(row, 2, QStandardItem(item.Certify_Type or ""))
            self.table_model.setItem(row, 3, QStandardItem(item.Certify_Name or ""))
            self.table_model.setItem(row, 4, QStandardItem(item.Certify_time or ""))
            self.table_model.setItem(row, 5, QStandardItem(item.Certify_Grade or ""))
            self.table_model.setItem(row, 6, QStandardItem(str(item.Score) if item.Score else ""))
            
            status = "有效" if item.Active else "停用"
            self.table_model.setItem(row, 7, QStandardItem(status))
    
    def _on_search_changed(self):
        """搜尋條件變更"""
        filters = {}
        
        if self.search_dept.currentText():
            filters["Dept"] = self.search_dept.currentText()
        
        if self.search_type.currentText():
            filters["Certify_Type"] = self.search_type.currentText()
        
        try:
            with UnitOfWork() as uow:
                repo = CertifyItemRepository(uow.session)
                items = repo.list(filters=filters)
                self._update_table(items)
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"搜尋失敗:\n{str(e)}")
    
    def _on_table_double_click(self, index):
        """表格雙擊"""
        item_id = self.table_model.item(index.row(), 1).text()
        dept = self.table_model.item(index.row(), 0).text()
        self._load_item(dept, item_id)
    
    def _load_item(self, dept: str, certify_id: str):
        """載入證照項目"""
        try:
            with UnitOfWork() as uow:
                repo = CertifyItemRepository(uow.session)
                item = repo.get_by_pk(dept, certify_id)
                
                if item:
                    self.dept.setCurrentText(item.Dept or "")
                    self.certify_id.setText(item.Certify_ID or "")
                    self.certify_type.setCurrentText(item.Certify_Type or "")
                    self.certify_name.setText(item.Certify_Name or "")
                    self.certify_time.setText(item.Certify_time or "")
                    self.certify_grade.setText(item.Certify_Grade or "")
                    self.score.setText(str(item.Score) if item.Score else "")
                    self.remark.setPlainText(item.Remark or "")
                    self.active.setChecked(item.Active)
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"載入資料失敗:\n{str(e)}")
    
    def _validate_form(self) -> bool:
        """表單驗證"""
        errors = []
        
        if not self.dept.currentText().strip():
            errors.append("部門不可空白")
        
        if not self.certify_id.text().strip():
            errors.append("證照ID不可空白")
        
        if not self.certify_type.currentText().strip():
            errors.append("證照類型不可空白")
        
        if not self.certify_name.text().strip():
            errors.append("證照名稱不可空白")
        
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
                repo = CertifyItemRepository(uow.session)
                
                dept = self.dept.currentText().strip()
                certify_id = self.certify_id.text().strip()
                
                data = {
                    "Dept": dept,
                    "Certify_ID": certify_id,
                    "Certify_Type": self.certify_type.currentText().strip(),
                    "Certify_Name": self.certify_name.text().strip(),
                    "Certify_time": self.certify_time.text().strip(),
                    "Certify_Grade": self.certify_grade.text().strip(),
                    "Score": float(self.score.text()) if self.score.text() else None,
                    "Remark": self.remark.toPlainText(),
                    "Active": self.active.isChecked()
                }
                
                repo.upsert(dept, data)
                
                QMessageBox.information(self, "成功", "證照項目已儲存")
                self._load_data()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"儲存資料失敗:\n{str(e)}")
    
    def _on_delete(self):
        """刪除"""
        dept = self.dept.currentText().strip()
        certify_id = self.certify_id.text().strip()
        
        if not dept or not certify_id:
            QMessageBox.warning(self, "警告", "請先載入要刪除的證照項目")
            return
        
        reply = QMessageBox.question(
            self,
            "確認刪除",
            f"確定要刪除證照項目 {certify_id} 嗎?\n注意：這將影響所有相關的證照記錄!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                with UnitOfWork() as uow:
                    repo = CertifyItemRepository(uow.session)
                    success = repo.delete(dept, certify_id)
                    
                    if success:
                        QMessageBox.information(self, "成功", f"證照項目 {certify_id} 已刪除")
                        self._clear_form()
                        self._load_data()
                    else:
                        QMessageBox.warning(self, "警告", "刪除失敗或項目不存在")
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"刪除資料失敗:\n{str(e)}")
    
    def _clear_form(self):
        """清空表單"""
        self.dept.setCurrentIndex(0)
        self.certify_id.clear()
        self.certify_type.setCurrentIndex(0)
        self.certify_name.clear()
        self.certify_time.clear()
        self.certify_grade.clear()
        self.score.clear()
        self.remark.clear()
        self.active.setChecked(True)
