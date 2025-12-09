# -*- coding: utf-8 -*-
"""
證照記錄管理視窗（SQLite 版本）
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QMessageBox, QComboBox, QTableView, QGroupBox, QLabel, QCheckBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from typing import List

from hrms.core.db.unit_of_work_sqlite import UnitOfWork
from repositories import CertifyRecordRepository, BasicRepository, CertifyItemRepository, CertifyTypeRepository
from domain.models import CertifyRecord


class CertifyRecordWindow(QDialog):
    """證照記錄管理視窗"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("證照記錄管理")
        self.resize(1100, 700)
        self._init_ui()
        self._load_data()
    
    def _init_ui(self):
        """初始化 UI"""
        main_layout = QVBoxLayout(self)
        
        # 搜尋條件
        search_group = QGroupBox("搜尋條件")
        search_layout = QHBoxLayout()
        
        search_layout.addWidget(QLabel("員工:"))
        self.search_emp = QComboBox()
        self.search_emp.setEditable(True)
        self.search_emp.currentTextChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_emp)
        
        search_layout.addWidget(QLabel("證照項目:"))
        self.search_certify = QComboBox()
        self.search_certify.setEditable(True)
        self.search_certify.currentTextChanged.connect(self._on_search_changed)
        search_layout.addWidget(self.search_certify)
        
        search_layout.addStretch()
        search_group.setLayout(search_layout)
        main_layout.addWidget(search_group)
        
        # 表單區域
        form_group = QGroupBox("證照記錄資料")
        form_layout = QFormLayout()
        
        self.recognition_code = QLineEdit()
        self.recognition_code.setMaxLength(50)
        form_layout.addRow("識別碼*:", self.recognition_code)
        
        self.emp_id = QComboBox()
        self.emp_id.setEditable(True)
        form_layout.addRow("員工編號*:", self.emp_id)
        
        self.certify_no = QComboBox()
        self.certify_no.setEditable(True)
        form_layout.addRow("證照編號*:", self.certify_no)
        
        self.update_date = QLineEdit()
        self.update_date.setMaxLength(20)
        form_layout.addRow("更新日期:", self.update_date)
        
        self.meno = QTextEdit()
        self.meno.setMaximumHeight(60)
        form_layout.addRow("備註:", self.meno)
        
        self.record_type = QComboBox()
        self.record_type.setEditable(True)
        form_layout.addRow("類型:", self.record_type)
        
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
        table_group = QGroupBox("證照記錄列表")
        table_layout = QVBoxLayout()
        
        self.table_model = QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels(["識別碼", "員工編號", "員工姓名", "證照編號", "證照名稱", "更新日期", "類型", "狀態"])
        
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
                record_repo = CertifyRecordRepository(uow.session)
                records = record_repo.list()
                self._update_table(records)
                
                # 載入下拉選單
                self._load_comboboxes()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"載入資料失敗:\n{str(e)}")
    
    def _load_comboboxes(self):
        """載入下拉選單選項"""
        try:
            with UnitOfWork() as uow:
                # 員工列表
                basic_repo = BasicRepository(uow.session)
                employees = basic_repo.list()
                
                self.search_emp.clear()
                self.search_emp.addItem("", "")
                self.emp_id.clear()
                for emp in employees:
                    display_text = f"{emp.EMP_ID} - {getattr(emp, 'C_Name', '')}"
                    self.search_emp.addItem(display_text, emp.EMP_ID)
                    self.emp_id.addItem(display_text, emp.EMP_ID)
                
                # 證照項目
                item_repo = CertifyItemRepository(uow.session)
                items = item_repo.list()
                
                self.search_certify.clear()
                self.search_certify.addItem("", "")
                self.certify_no.clear()
                for item in items:
                    display_text = f"{item.Certify_ID} - {item.Certify_Name}"
                    self.search_certify.addItem(display_text, item.Certify_ID)
                    self.certify_no.addItem(display_text, item.Certify_ID)
                
                # 證照類型
                type_repo = CertifyTypeRepository(uow.session)
                types = type_repo.list()
                
                self.record_type.clear()
                self.record_type.addItem("", "")
                for ct in types:
                    self.record_type.addItem(ct.Certify_Type, ct.Certify_Type)
        except Exception as e:
            print(f"載入下拉選單失敗: {e}")
    
    def _update_table(self, records: List[CertifyRecord]):
        """更新表格"""
        self.table_model.removeRows(0, self.table_model.rowCount())
        
        # 取得員工和證照名稱以供顯示
        emp_names = {}
        certify_names = {}
        
        try:
            with UnitOfWork() as uow:
                # 取得員工姓名
                basic_repo = BasicRepository(uow.session)
                employees = basic_repo.list()
                for emp in employees:
                    emp_names[emp.EMP_ID] = getattr(emp, 'C_Name', '')
                
                # 取得證照名稱
                item_repo = CertifyItemRepository(uow.session)
                items = item_repo.list()
                for item in items:
                    certify_names[item.Certify_ID] = item.Certify_Name
        except:
            pass
        
        for row, record in enumerate(records):
            self.table_model.insertRow(row)
            
            self.table_model.setItem(row, 0, QStandardItem(record.識別碼 or ""))
            self.table_model.setItem(row, 1, QStandardItem(record.EMP_ID or ""))
            
            emp_name = emp_names.get(record.EMP_ID, "")
            self.table_model.setItem(row, 2, QStandardItem(emp_name))
            
            self.table_model.setItem(row, 3, QStandardItem(record.Certify_NO or ""))
            
            certify_name = certify_names.get(record.Certify_NO, "")
            self.table_model.setItem(row, 4, QStandardItem(certify_name))
            
            self.table_model.setItem(row, 5, QStandardItem(record.Update_date or ""))
            self.table_model.setItem(row, 6, QStandardItem(record.Type or ""))
            
            status = "有效" if record.Active else "停用"
            self.table_model.setItem(row, 7, QStandardItem(status))
    
    def _on_search_changed(self):
        """搜尋條件變更"""
        filters = {}
        
        if self.search_emp.currentData():
            filters["EMP_ID"] = self.search_emp.currentData()
        
        if self.search_certify.currentData():
            filters["Certify_NO"] = self.search_certify.currentData()
        
        try:
            with UnitOfWork() as uow:
                repo = CertifyRecordRepository(uow.session)
                records = repo.list(filters=filters)
                self._update_table(records)
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"搜尋失敗:\n{str(e)}")
    
    def _on_table_double_click(self, index):
        """表格雙擊"""
        recognition_code = self.table_model.item(index.row(), 0).text()
        if recognition_code:
            self._load_record(recognition_code)
    
    def _load_record(self, recognition_code: str):
        """載入證照記錄"""
        try:
            with UnitOfWork() as uow:
                repo = CertifyRecordRepository(uow.session)
                record = repo.get_by_pk(recognition_code)
                
                if record:
                    self.recognition_code.setText(record.識別碼 or "")
                    
                    # 設定員工
                    index = self.emp_id.findData(record.EMP_ID)
                    if index >= 0:
                        self.emp_id.setCurrentIndex(index)
                    else:
                        self.emp_id.setCurrentText(record.EMP_ID or "")
                    
                    # 設定證照
                    index = self.certify_no.findData(record.Certify_NO)
                    if index >= 0:
                        self.certify_no.setCurrentIndex(index)
                    else:
                        self.certify_no.setCurrentText(record.Certify_NO or "")
                    
                    self.update_date.setText(record.Update_date or "")
                    self.meno.setPlainText(record.Meno or "")
                    
                    # 設定類型
                    index = self.record_type.findText(record.Type or "")
                    if index >= 0:
                        self.record_type.setCurrentIndex(index)
                    else:
                        self.record_type.setCurrentText(record.Type or "")
                    
                    self.active.setChecked(record.Active)
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"載入資料失敗:\n{str(e)}")
    
    def _validate_form(self) -> bool:
        """表單驗證"""
        errors = []
        
        if not self.recognition_code.text().strip():
            errors.append("識別碼不可空白")
        
        if not self.emp_id.currentText().strip():
            errors.append("員工編號不可空白")
        
        if not self.certify_no.currentText().strip():
            errors.append("證照編號不可空白")
        
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
                repo = CertifyRecordRepository(uow.session)
                
                recognition_code = self.recognition_code.text().strip()
                
                data = {
                    "識別碼": recognition_code,
                    "EMP_ID": self.emp_id.currentText().split(" - ")[0].strip(),
                    "Certify_NO": self.certify_no.currentText().split(" - ")[0].strip(),
                    "Update_date": self.update_date.text().strip(),
                    "Meno": self.meno.toPlainText(),
                    "Type": self.record_type.currentText().strip(),
                    "Active": self.active.isChecked()
                }
                
                repo.upsert(recognition_code, data)
                
                QMessageBox.information(self, "成功", "證照記錄已儲存")
                self._load_data()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"儲存資料失敗:\n{str(e)}")
    
    def _on_delete(self):
        """刪除"""
        recognition_code = self.recognition_code.text().strip()
        
        if not recognition_code:
            QMessageBox.warning(self, "警告", "請先載入要刪除的證照記錄")
            return
        
        reply = QMessageBox.question(
            self,
            "確認刪除",
            f"確定要刪除證照記錄 {recognition_code} 嗎?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                with UnitOfWork() as uow:
                    repo = CertifyRecordRepository(uow.session)
                    success = repo.delete(recognition_code)
                    
                    if success:
                        QMessageBox.information(self, "成功", f"證照記錄 {recognition_code} 已刪除")
                        self._clear_form()
                        self._load_data()
                    else:
                        QMessageBox.warning(self, "警告", "刪除失敗或記錄不存在")
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"刪除資料失敗:\n{str(e)}")
    
    def _clear_form(self):
        """清空表單"""
        self.recognition_code.clear()
        self.emp_id.setCurrentIndex(0)
        self.certify_no.setCurrentIndex(0)
        self.update_date.clear()
        self.meno.clear()
        self.record_type.setCurrentIndex(0)
        self.active.setChecked(True)
