# -*- coding: utf-8 -*-
"""
部門管理視窗（SQLite 版本）
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QTextEdit,
    QPushButton, QMessageBox, QTableView, QGroupBox, QLabel
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from typing import List

from hrms.core.db.unit_of_work_sqlite import UnitOfWork
from repositories import SectionRepository, BasicRepository
from domain.models import Section


class DeptWindow(QDialog):
    """部門管理視窗"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("部門管理")
        self.resize(900, 600)
        
        self._init_ui()
        self._load_data()
    
    def _init_ui(self):
        """初始化 UI"""
        main_layout = QVBoxLayout(self)
        
        # 表單區域
        form_group = self._create_form_group()
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
        table_group = QGroupBox("部門列表")
        table_layout = QVBoxLayout()
        
        self.table_model = QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels(["部門代碼", "部門名稱", "部門說明", "主管"])
        
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.doubleClicked.connect(self._on_table_double_click)
        
        table_layout.addWidget(self.table_view)
        table_group.setLayout(table_layout)
        main_layout.addWidget(table_group)
    
    def _create_form_group(self) -> QGroupBox:
        """建立表單區域"""
        group = QGroupBox("部門資料")
        layout = QFormLayout()
        
        self.dept_code = QLineEdit()
        self.dept_code.setMaxLength(50)
        layout.addRow("部門代碼*:", self.dept_code)
        
        self.dept_name = QLineEdit()
        self.dept_name.setMaxLength(200)
        layout.addRow("部門名稱*:", self.dept_name)
        
        self.dept_desc = QTextEdit()
        self.dept_desc.setMaximumHeight(80)
        layout.addRow("部門說明:", self.dept_desc)
        
        self.supervisor = QLineEdit()
        self.supervisor.setMaxLength(50)
        layout.addRow("主管:", self.supervisor)
        
        group.setLayout(layout)
        return group
    
    def _load_data(self):
        """載入資料"""
        try:
            with UnitOfWork() as uow:
                repo = SectionRepository(uow.session)
                sections = repo.list()
                
                self._update_table(sections)
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"載入資料失敗:\n{str(e)}")
    
    def _update_table(self, sections: List[Section]):
        """更新表格"""
        self.table_model.removeRows(0, self.table_model.rowCount())
        
        for row, section in enumerate(sections):
            self.table_model.insertRow(row)
            
            self.table_model.setItem(row, 0, QStandardItem(section.Dept_Code or ""))
            self.table_model.setItem(row, 1, QStandardItem(section.Dept_Name or ""))
            self.table_model.setItem(row, 2, QStandardItem(section.Dept_Desc or ""))
            self.table_model.setItem(row, 3, QStandardItem(section.Supervisor or ""))
    
    def _on_table_double_click(self, index):
        """表格雙擊"""
        dept_code = self.table_model.item(index.row(), 0).text()
        self._load_section(dept_code)
    
    def _load_section(self, dept_code: str):
        """載入部門資料"""
        try:
            with UnitOfWork() as uow:
                repo = SectionRepository(uow.session)
                section = repo.get_by_pk(dept_code)
                
                if section:
                    self.dept_code.setText(section.Dept_Code or "")
                    self.dept_name.setText(section.Dept_Name or "")
                    self.dept_desc.setPlainText(section.Dept_Desc or "")
                    self.supervisor.setText(section.Supervisor or "")
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"載入部門資料失敗:\n{str(e)}")
    
    def _validate_form(self) -> bool:
        """表單驗證"""
        errors = []
        
        if not self.dept_code.text().strip():
            errors.append("部門代碼不可空白")
        
        if not self.dept_name.text().strip():
            errors.append("部門名稱不可空白")
        
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
                repo = SectionRepository(uow.session)
                
                dept_code = self.dept_code.text().strip()
                
                # 檢查是否有員工
                basic_repo = BasicRepository(uow.session)
                has_employees = basic_repo.has_department_employees(dept_code)
                
                data = {
                    "Dept_Code": dept_code,
                    "Dept_Name": self.dept_name.text().strip(),
                    "Dept_Desc": self.dept_desc.toPlainText(),
                    "Supervisor": self.supervisor.text().strip()
                }
                
                # 如果是更新且部門代碼變更，需要檢查外鍵
                existing = repo.get_by_pk(dept_code)
                if existing and dept_code != existing.Dept_Code and has_employees:
                    QMessageBox.warning(self, "警告", "該部門已有員工，無法變更部門代碼")
                    return
                
                repo.upsert(dept_code, data)
                
                QMessageBox.information(self, "成功", "部門資料已儲存")
                self._load_data()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"儲存資料失敗:\n{str(e)}")
    
    def _on_delete(self):
        """刪除"""
        dept_code = self.dept_code.text().strip()
        if not dept_code:
            QMessageBox.warning(self, "警告", "請先載入要刪除的部門")
            return
        
        try:
            with UnitOfWork() as uow:
                # 檢查是否有員工
                basic_repo = BasicRepository(uow.session)
                if basic_repo.has_department_employees(dept_code):
                    QMessageBox.warning(self, "警告", "該部門仍有員工，無法刪除")
                    return
                
                repo = SectionRepository(uow.session)
                
                reply = QMessageBox.question(
                    self,
                    "確認刪除",
                    f"確定要刪除部門 {dept_code} 嗎?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    success = repo.delete(dept_code)
                    
                    if success:
                        QMessageBox.information(self, "成功", f"部門 {dept_code} 已刪除")
                        self._clear_form()
                        self._load_data()
                    else:
                        QMessageBox.warning(self, "警告", "刪除失敗或部門不存在")
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"刪除資料失敗:\n{str(e)}")
    
    def _clear_form(self):
        """清空表單"""
        self.dept_code.clear()
        self.dept_name.clear()
        self.dept_desc.clear()
        self.supervisor.clear()


if __name__ == "__main__":
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    window = DeptWindow()
    window.show()
    sys.exit(app.exec())
