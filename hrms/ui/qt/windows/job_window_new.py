# -*- coding: utf-8 -*-
"""
職務管理視窗（SQLite 版本）
簡單的 CRUD 操作
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QMessageBox, QTableView, QGroupBox
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QStandardItemModel, QStandardItem
from typing import List

from hrms.core.db.unit_of_work_sqlite import UnitOfWork
from repositories import JobRepository
from domain.models import Job


class JobWindow(QDialog):
    """職務管理視窗"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("職務管理")
        self.resize(700, 500)
        self._init_ui()
        self._load_data()
    
    def _init_ui(self):
        """初始化 UI"""
        main_layout = QVBoxLayout(self)
        
        # 表單區域
        form_group = QGroupBox("職務資料")
        form_layout = QFormLayout()
        
        self.job = QLineEdit()
        self.job.setMaxLength(100)
        form_layout.addRow("職務名稱*:", self.job)
        
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
        table_group = QGroupBox("職務列表")
        table_layout = QVBoxLayout()
        
        self.table_model = QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels(["職務名稱"])
        
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
                repo = JobRepository(uow.session)
                jobs = repo.list()
                self._update_table(jobs)
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"載入資料失敗:\n{str(e)}")
    
    def _update_table(self, jobs: List[Job]):
        """更新表格"""
        self.table_model.removeRows(0, self.table_model.rowCount())
        
        for row, job in enumerate(jobs):
            self.table_model.insertRow(row)
            self.table_model.setItem(row, 0, QStandardItem(job.L_Job or ""))
    
    def _on_table_double_click(self, index):
        """表格雙擊"""
        job_name = self.table_model.item(index.row(), 0).text()
        self.job.setText(job_name)
    
    def _validate_form(self) -> bool:
        """表單驗證"""
        if not self.job.text().strip():
            QMessageBox.warning(self, "資料驗證失敗", "職務名稱不可空白")
            return False
        return True
    
    def _on_save(self):
        """儲存"""
        if not self._validate_form():
            return
        
        try:
            with UnitOfWork() as uow:
                repo = JobRepository(uow.session)
                
                job_name = self.job.text().strip()
                
                data = {"L_Job": job_name}
                
                repo.upsert(job_name, data)
                
                QMessageBox.information(self, "成功", "職務資料已儲存")
                self._load_data()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"儲存資料失敗:\n{str(e)}")
    
    def _on_delete(self):
        """刪除"""
        job_name = self.job.text().strip()
        if not job_name:
            QMessageBox.warning(self, "警告", "請先載入要刪除的職務")
            return
        
        reply = QMessageBox.question(
            self,
            "確認刪除",
            f"確定要刪除職務 {job_name} 嗎?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                with UnitOfWork() as uow:
                    repo = JobRepository(uow.session)
                    success = repo.delete(job_name)
                    
                    if success:
                        QMessageBox.information(self, "成功", f"職務 {job_name} 已刪除")
                        self._clear_form()
                        self._load_data()
                    else:
                        QMessageBox.warning(self, "警告", "刪除失敗或職務不存在")
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"刪除資料失敗:\n{str(e)}")
    
    def _clear_form(self):
        """清空表單"""
        self.job.clear()
