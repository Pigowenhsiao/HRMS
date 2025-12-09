# -*- coding: utf-8 -*-
"""
證照記錄管理視窗（SQLite 版本）
包含證照到期提醒功能
重點：處理 9,605 筆資料，必須使用分頁和高效搜尋
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit,
    QPushButton, QMessageBox, QComboBox, QTableView, QGroupBox, 
    QLabel, QCheckBox, QDateEdit, QSplitter
)
from PySide6.QtCore import Qt, QDate
from PySide6.QtGui import QStandardItemModel, QStandardItem, QColor
from typing import List, Optional
from datetime import datetime, timedelta

from hrms.core.db.unit_of_work_sqlite import UnitOfWork
from repositories import TrainingRecordRepository, BasicRepository, CertifyItemRepository
from domain.models import TrainingRecord


class TrainingRecordWindow(QDialog):
    """
    證照記錄管理視窗
    重點功能：
    - 分頁顯示（每頁 50 筆，處理 9,605 筆資料）
    - 多條件搜尋（員工、證照、日期）
    - 證照到期提醒（30 天內到期標紅色）
    - 批次操作（未來可擴充）
    """
    
    PAGE_SIZE = 50  # 每頁 50 筆，避免載入過多資料
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("證照記錄管理（含到期提醒）")
        self.resize(1400, 800)
        
        self.current_page = 1
        self.total_records = 0
        self.search_filters = {}
        self._expiring_days = 30  # 預設 30 天內到期提醒
        
        self._init_ui()
        self._load_comboboxes()
        self._load_data()
    
    def _init_ui(self):
        """初始化 UI"""
        main_layout = QVBoxLayout(self)
        
        # 搜尋區域
        search_group = self._create_search_group()
        main_layout.addWidget(search_group)
        
        # 證照到期提醒區域
        alert_group = self._create_alert_group()
        main_layout.addWidget(alert_group)
        
        # 資料表格區域
        table_group = self._create_table_group()
        main_layout.addWidget(table_group, 1)
        
        # 表單區域
        form_group = self._create_form_group()
        main_layout.addWidget(form_group)
        
        # 分頁控制
        pagination_group = self._create_pagination_group()
        main_layout.addWidget(pagination_group)
    
    def _create_search_group(self) -> QGroupBox:
        """建立搜尋區域"""
        group = QGroupBox("搜尋條件")
        layout = QHBoxLayout()
        
        # 員工編號
        layout.addWidget(QLabel("員工編號:"))
        self.search_emp_id = QLineEdit()
        self.search_emp_id.setPlaceholderText("輸入員工編號...")
        self.search_emp_id.textChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_emp_id)
        
        # 員工姓名（模糊搜尋）
        layout.addWidget(QLabel("員工姓名:"))
        self.search_emp_name = QLineEdit()
        self.search_emp_name.setPlaceholderText("輸入姓名...")
        self.search_emp_name.textChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_emp_name)
        
        # 證照項目
        layout.addWidget(QLabel("證照項目:"))
        self.search_certify = QComboBox()
        self.search_certify.setEditable(True)
        self.search_certify.currentTextChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_certify)
        
        # 日期範圍
        layout.addWidget(QLabel("核發日期 從:"))
        self.search_date_from = QDateEdit()
        self.search_date_from.setCalendarPopup(True)
        self.search_date_from.setDisplayFormat("yyyy-MM-dd")
        self.search_date_from.dateChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_date_from)
        
        layout.addWidget(QLabel("到:"))
        self.search_date_to = QDateEdit()
        self.search_date_to.setCalendarPopup(True)
        self.search_date_to.setDisplayFormat("yyyy-MM-dd")
        self.search_date_to.dateChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_date_to)
        
        # 狀態
        layout.addWidget(QLabel("狀態:"))
        self.search_active = QComboBox()
        self.search_active.addItems(["全部", "有效", "過期"])
        self.search_active.currentTextChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_active)
        
        # 清除搜尋
        btn_clear = QPushButton("清除")
        btn_clear.clicked.connect(self._clear_search)
        layout.addWidget(btn_clear)
        
        layout.addStretch()
        group.setLayout(layout)
        return group
    
    def _create_alert_group(self) -> QGroupBox:
        """建立證照到期提醒區域"""
        group = QGroupBox("證照到期提醒")
        layout = QHBoxLayout()
        
        # 到期天數設定
        layout.addWidget(QLabel("到期提醒（天）:"))
        self.alert_days = QLineEdit("30")
        self.alert_days.setMaximumWidth(60)
        self.alert_days.textChanged.connect(self._on_alert_days_changed)
        layout.addWidget(self.alert_days)
        
        self.btn_check_expiring = QPushButton("🔍 檢查到期證照")
        self.btn_check_expiring.clicked.connect(self._check_expiring_certifications)
        layout.addWidget(self.btn_check_expiring)
        
        # 到期證照計數
        layout.addWidget(QLabel("到期證照數:"))
        self.lbl_expiring_count = QLabel("0")
        self.lbl_expiring_count.setStyleSheet("color: red; font-weight: bold; font-size: 16px;")
        layout.addWidget(self.lbl_expiring_count)
        
        layout.addStretch()
        group.setLayout(layout)
        return group
    
    def _create_table_group(self) -> QGroupBox:
        """建立表格區域"""
        group = QGroupBox("證照記錄列表")
        layout = QVBoxLayout()
        
        # 工具列
        toolbar = QHBoxLayout()
        
        self.btn_refresh = QPushButton("🔄 刷新")
        self.btn_refresh.clicked.connect(self._load_data)
        toolbar.addWidget(self.btn_refresh)
        
        self.btn_export = QPushButton("📊 匯出 Excel")
        self.btn_export.clicked.connect(self._export_excel)
        toolbar.addWidget(self.btn_export)
        
        self.btn_expiring_only = QPushButton("⚠️  僅顯示到期")
        self.btn_expiring_only.clicked.connect(self._show_expiring_only)
        toolbar.addWidget(self.btn_expiring_only)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # 到期提醒標籤
        alert_label = QLabel("⚠️ 紅色列：證照即將到期（30天內） | 黃色列：證照已過期")
        alert_label.setStyleSheet("color: #666; font-style: italic;")
        layout.addWidget(alert_label)
        
        # 資料表格
        self.table_model = QStandardItemModel()
        self.table_model.setHorizontalHeaderLabels([
            "證照編號", "員工編號", "員工姓名", "證照ID", "證照名稱",
            "核發日期", "證照類型", "更新日期", "狀態"
        ])
        
        self.table_view = QTableView()
        self.table_view.setModel(self.table_model)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.doubleClicked.connect(self._on_table_double_click)
        
        layout.addWidget(self.table_view)
        
        # 狀態列
        status_layout = QHBoxLayout()
        self.lbl_status = QLabel("就緒")
        status_layout.addWidget(self.lbl_status)
        
        layout.addLayout(status_layout)
        group.setLayout(layout)
        return group
    
    def _create_form_group(self) -> QGroupBox:
        """建立表單區域"""
        group = QGroupBox("證照記錄資料")
        layout = QFormLayout()
        
        # 第一行
        row1 = QHBoxLayout()
        self.certify_no = QLineEdit()
        self.certify_no.setReadOnly(True)
        self.certify_no.setPlaceholderText("系統自動產生")
        row1.addWidget(self.certify_no)
        
        self.emp_id = QComboBox()
        self.emp_id.setEditable(True)
        row1.addWidget(self.emp_id)
        
        layout.addRow("證照編號:", self.certify_no)
        layout.addRow("員工編號*:", self.emp_id)
        
        # 第二行
        self.certify_id = QComboBox()
        self.certify_id.setEditable(True)
        layout.addRow("證照ID*:", self.certify_id)
        
        # 第三行
        self.certify_name = QLineEdit()
        self.certify_name.setReadOnly(True)
        self.certify_name.setPlaceholderText("選擇證照ID後自動帶入")
        layout.addRow("證照名稱:", self.certify_name)
        
        # 第四行
        self.certify_date = QDateEdit()
        self.certify_date.setCalendarPopup(True)
        self.certify_date.setDisplayFormat("yyyy-MM-dd")
        self.certify_date.dateChanged.connect(self._calculate_expiry_date)
        layout.addRow("核發日期*:", self.certify_date)
        
        # 第五行
        self.certify_type = QLineEdit()
        self.certify_type.setReadOnly(True)
        layout.addRow("證照類型:", self.certify_type)
        
        # 第六行
        self.update_date = QDateEdit()
        self.update_date.setCalendarPopup(True)
        self.update_date.setDisplayFormat("yyyy-MM-dd")
        self.update_date.setDate(QDate.currentDate())
        layout.addRow("更新日期:", self.update_date)
        
        # 第七行
        self.active = QCheckBox("有效")
        self.active.setChecked(True)
        layout.addRow("狀態:", self.active)
        
        # 第八行 - 到期提醒（自動計算）
        self.expiry_alert = QLineEdit()
        self.expiry_alert.setReadOnly(True)
        self.expiry_alert.setStyleSheet("color: red; font-weight: bold;")
        layout.addRow("到期提醒:", self.expiry_alert)
        
        # 備註
        self.remark = QLineEdit()
        layout.addRow("備註:", self.remark)
        
        # 按鈕區
        btn_layout = QHBoxLayout()
        
        self.btn_load = QPushButton("載入")
        self.btn_load.clicked.connect(self._on_load)
        btn_layout.addWidget(self.btn_load)
        
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
        
        layout.addRow("", btn_layout)
        group.setLayout(layout)
        return group
    
    def _create_pagination_group(self) -> QGroupBox:
        """建立分頁控制區域"""
        group = QGroupBox("分頁控制")
        layout = QHBoxLayout()
        
        self.btn_first = QPushButton("⏮ 第一頁")
        self.btn_first.clicked.connect(lambda: self._goto_page(1))
        layout.addWidget(self.btn_first)
        
        self.btn_prev = QPushButton("◀ 上一頁")
        self.btn_prev.clicked.connect(self._goto_prev_page)
        layout.addWidget(self.btn_prev)
        
        self.lbl_page = QLabel("第 1 頁 / 共 1 頁")
        layout.addWidget(self.lbl_page)
        
        self.btn_next = QPushButton("下一頁 ▶")
        self.btn_next.clicked.connect(self._goto_next_page)
        layout.addWidget(self.btn_next)
        
        self.btn_last = QPushButton("最末頁 ⏭")
        self.btn_last.clicked.connect(self._goto_last_page)
        layout.addWidget(self.btn_last)
        
        layout.addStretch()
        
        # 跳轉到指定頁
        layout.addWidget(QLabel("跳轉到:"))
        self.page_input = QLineEdit()
        self.page_input.setMaximumWidth(50)
        self.page_input.returnPressed.connect(self._goto_input_page)
        layout.addWidget(self.page_input)
        
        group.setLayout(layout)
        return group
    
    def _load_comboboxes(self):
        """載入下拉選單選項"""
        try:
            with UnitOfWork() as uow:
                # 員工列表
                basic_repo = BasicRepository(uow.session)
                employees = basic_repo.get_active_employees(limit=200)  # 只載入前 200 位，避免太多
                
                self.emp_id.clear()
                for emp in employees:
                    self.emp_id.addItem(f"{emp.EMP_ID} - {emp.C_Name}", emp.EMP_ID)
                
                # 證照項目
                item_repo = CertifyItemRepository(uow.session)
                items = item_repo.list(limit=100)  # 只載入前 100 個
                
                self.certify_id.clear()
                for item in items:
                    self.certify_id.addItem(f"{item.Certify_ID} - {item.Certify_Name}", item.Certify_ID)
                
        except Exception as e:
            print(f"載入下拉選單失敗: {e}")
    
    def _load_data(self):
        """載入資料（分頁）"""
        try:
            with UnitOfWork() as uow:
                repo = TrainingRecordRepository(uow.session)
                
                # 計算總筆數
                self.total_records = repo.count(filters=self.search_filters)
                
                # 計算總頁數
                total_pages = (self.total_records + self.PAGE_SIZE - 1) // self.PAGE_SIZE
                if total_pages == 0:
                    total_pages = 1
                
                # 校正頁碼
                if self.current_page > total_pages:
                    self.current_page = total_pages
                if self.current_page < 1:
                    self.current_page = 1
                
                # 計算偏移量
                offset = (self.current_page - 1) * self.PAGE_SIZE
                
                # 查詢資料
                records = repo.list(
                    filters=self.search_filters,
                    limit=self.PAGE_SIZE,
                    offset=offset
                )
                
                # 更新表格
                self._update_table(records)
                
                # 更新分頁資訊
                self._update_pagination_info()
                
                # 更新狀態列
                self.lbl_status.setText(f"顯示 {len(records)} / {self.total_records} 筆資料")
                
                # 檢查到期證照
                self._check_expiring_certifications()
                
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"載入資料失敗:\n{str(e)}")
    
    def _update_table(self, records: List[TrainingRecord]):
        """更新表格資料"""
        self.table_model.removeRows(0, self.table_model.rowCount())
        
        # 取得員工和證照資訊以供顯示
        emp_names = {}
        certify_names = {}
        
        try:
            with UnitOfWork() as uow:
                # 取得員工姓名
                basic_repo = BasicRepository(uow.session)
                for record in records[:50]:  # 只查詢前 50 個員工，避免太多查詢
                    emp = basic_repo.get_by_pk(record.EMP_ID)
                    if emp:
                        emp_names[record.EMP_ID] = emp.C_Name
                
                # 取得證照名稱
                item_repo = CertifyItemRepository(uow.session)
                for record in records[:50]:
                    item = item_repo.get_by_pk(None, record.Certify_ID)  # 這裡需要改進
                    if item:
                        certify_names[record.Certify_ID] = item.Certify_Name
        except:
            pass
        
        expiring_count = 0
        
        for row, record in enumerate(records):
            self.table_model.insertRow(row)
            
            # 證照編號
            self.table_model.setItem(row, 0, QStandardItem(str(record.Certify_No)))
            
            # 員工編號
            self.table_model.setItem(row, 1, QStandardItem(record.EMP_ID or ""))
            
            # 員工姓名
            emp_name = emp_names.get(record.EMP_ID, "")
            self.table_model.setItem(row, 2, QStandardItem(emp_name))
            
            # 證照ID
            self.table_model.setItem(row, 3, QStandardItem(record.Certify_ID or ""))
            
            # 證照名稱
            certify_name = certify_names.get(record.Certify_ID, "")
            self.table_model.setItem(row, 4, QStandardItem(certify_name))
            
            # 核發日期
            self.table_model.setItem(row, 5, QStandardItem(record.Certify_date or ""))
            
            # 證照類型
            self.table_model.setItem(row, 6, QStandardItem(record.Certify_type or ""))
            
            # 更新日期
            self.table_model.setItem(row, 7, QStandardItem(record.update_date or ""))
            
            # 狀態
            status = "有效" if record.Active else "過期"
            self.table_model.setItem(row, 8, QStandardItem(status))
            
            # 檢查是否到期（簡化版，假設證照效期為1年）
            is_expiring = False
            is_expired = False
            
            if record.Certify_date:
                try:
                    cert_date = datetime.strptime(record.Certify_date, "%Y-%m-%d")
                    expiry_date = cert_date + timedelta(days=365)
                    today = datetime.now()
                    days_until_expiry = (expiry_date - today).days
                    
                    if days_until_expiry <= 0:
                        is_expired = True
                        # 設定背景色為黃色（已過期）
                        for col in range(self.table_model.columnCount()):
                            item = self.table_model.item(row, col)
                            if item:
                                item.setBackground(QColor("#fff3cd"))
                    elif days_until_expiry <= self._expiring_days:
                        is_expiring = True
                        expiring_count += 1
                        # 設定背景色為紅色（即將到期）
                        for col in range(self.table_model.columnCount()):
                            item = self.table_model.item(row, col)
                            if item:
                                item.setBackground(QColor("#f8d7da"))
                except:
                    pass
        
        # 更新到期證照計數
        self.lbl_expiring_count.setText(str(expiring_count))
    
    def _update_pagination_info(self):
        """更新分頁資訊"""
        total_pages = (self.total_records + self.PAGE_SIZE - 1) // self.PAGE_SIZE
        if total_pages == 0:
            total_pages = 1
        
        self.lbl_page.setText(f"第 {self.current_page} 頁 / 共 {total_pages} 頁")
        
        self.btn_first.setEnabled(self.current_page > 1)
        self.btn_prev.setEnabled(self.current_page > 1)
        self.btn_next.setEnabled(self.current_page < total_pages)
        self.btn_last.setEnabled(self.current_page < total_pages)
        
        self.page_input.setText(str(self.current_page))
    
    def _check_expiring_certifications(self):
        """檢查到期證照（背景執行）"""
        try:
            with UnitOfWork() as uow:
                repo = TrainingRecordRepository(uow.session)
                
                # 取得所有有效證照
                records = repo.list(filters={"Active": True})
                
                expiring_count = 0
                
                for record in records:
                    if record.Certify_date:
                        try:
                            cert_date = datetime.strptime(record.Certify_date, "%Y-%m-%d")
                            expiry_date = cert_date + timedelta(days=365)
                            today = datetime.now()
                            days_until_expiry = (expiry_date - today).days
                            
                            if 0 < days_until_expiry <= self._expiring_days:
                                expiring_count += 1
                        except:
                            pass
                
                self.lbl_expiring_count.setText(str(expiring_count))
                
        except Exception as e:
            print(f"檢查到期證照失敗: {e}")
    
    def _show_expiring_only(self):
        """僅顯示到期證照"""
        QMessageBox.information(self, "提示", "功能開發中...")
    
    def _on_alert_days_changed(self):
        """到期天數變更"""
        try:
            days = int(self.alert_days.text())
            self._expiring_days = days
            self._load_data()
        except:
            pass
    
    def _calculate_expiry_date(self):
        """計算到期日（簡化版）"""
        certify_date = self.certify_date.date().toPython()
        if certify_date:
            expiry_date = certify_date + timedelta(days=365)
            today = datetime.now().date()
            days_until_expiry = (expiry_date - today).days
            
            if days_until_expiry <= 0:
                self.expiry_alert.setText(f"已過期 {abs(days_until_expiry)} 天")
            elif days_until_expiry <= self._expiring_days:
                self.expiry_alert.setText(f"{days_until_expiry} 天後到期 ⚠️")
            else:
                self.expiry_alert.setText(f"{days_until_expiry} 天後到期")
    
    def _on_search_changed(self):
        """搜尋條件變更"""
        self.search_filters = {}
        
        if self.search_emp_id.text().strip():
            self.search_filters["EMP_ID"] = self.search_emp_id.text().strip()
        
        if self.search_certify.currentText():
            self.search_filters["Certify_ID"] = self.search_certify.currentText()
        
        if self.search_active.currentText() == "有效":
            self.search_filters["Active"] = True
        elif self.search_active.currentText() == "過期":
            self.search_filters["Active"] = False
        
        self.current_page = 1
        self._load_data()
    
    def _clear_search(self):
        """清除搜尋"""
        self.search_emp_id.clear()
        self.search_emp_name.clear()
        self.search_certify.setCurrentIndex(0)
        self.search_active.setCurrentIndex(0)
        self.search_date_from.clear()
        self.search_date_to.clear()
        
        self.search_filters = {}
        self.current_page = 1
        self._load_data()
    
    def _goto_page(self, page: int):
        """跳轉到指定頁碼"""
        total_pages = (self.total_records + self.PAGE_SIZE - 1) // self.PAGE_SIZE
        
        if page < 1:
            page = 1
        if page > total_pages:
            page = total_pages
        
        self.current_page = page
        self._load_data()
    
    def _goto_prev_page(self):
        """上一頁"""
        self._goto_page(self.current_page - 1)
    
    def _goto_next_page(self):
        """下一頁"""
        self._goto_page(self.current_page + 1)
    
    def _goto_last_page(self):
        """最末頁"""
        total_pages = (self.total_records + self.PAGE_SIZE - 1) // self.PAGE_SIZE
        self._goto_page(total_pages)
    
    def _goto_input_page(self):
        """跳轉到輸入的頁碼"""
        try:
            page = int(self.page_input.text())
            self._goto_page(page)
        except:
            pass
    
    def _on_table_double_click(self, index):
        """表格雙擊"""
        certify_no = self.table_model.item(index.row(), 0).text()
        if certify_no:
            self._load_record(int(certify_no))
    
    def _load_record(self, certify_no: int):
        """載入證照記錄"""
        try:
            with UnitOfWork() as uow:
                repo = TrainingRecordRepository(uow.session)
                record = repo.get_by_pk(certify_no)
                
                if record:
                    self.certify_no.setText(str(record.Certify_No))
                    
                    # 設定員工
                    index = self.emp_id.findData(record.EMP_ID)
                    if index >= 0:
                        self.emp_id.setCurrentIndex(index)
                    else:
                        self.emp_id.setCurrentText(record.EMP_ID)
                    
                    # 設定證照
                    index = self.certify_id.findData(record.Certify_ID)
                    if index >= 0:
                        self.certify_id.setCurrentIndex(index)
                    else:
                        self.certify_id.setCurrentText(record.Certify_ID)
                    
                    # 設定日期
                    if record.Certify_date:
                        date = QDate.fromString(record.Certify_date, "yyyy-MM-dd")
                        self.certify_date.setDate(date if date.isValid() else QDate.currentDate())
                    
                    self.certify_type.setText(record.Certify_type or "")
                    
                    if record.update_date:
                        date = QDate.fromString(record.update_date, "yyyy-MM-dd")
                        self.update_date.setDate(date if date.isValid() else QDate.currentDate())
                    
                    self.active.setChecked(record.Active)
                    self.remark.setText(record.Remark or "")
                    
                    self._calculate_expiry_date()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"載入證照記錄失敗:\n{str(e)}")
    
    def _on_load(self):
        """載入按鈕"""
        certify_no = self.certify_no.text().strip()
        if not certify_no:
            QMessageBox.warning(self, "警告", "請輸入證照編號")
            return
        
        try:
            self._load_record(int(certify_no))
        except ValueError:
            QMessageBox.warning(self, "警告", "證照編號必須是數字")
    
    def _validate_form(self) -> bool:
        """表單驗證"""
        errors = []
        
        if self.emp_id.currentText().strip() == "":
            errors.append("員工編號不可空白")
        
        if self.certify_id.currentText().strip() == "":
            errors.append("證照ID不可空白")
        
        if not self.certify_date.date().isValid():
            errors.append("核發日期無效")
        
        if errors:
            QMessageBox.warning(self, "資料驗證失敗", "\n".join(errors))
            return False
        
        return True
    
    def _on_save(self):
        """儲存證照記錄"""
        if not self._validate_form():
            return
        
        try:
            with UnitOfWork() as uow:
                repo = TrainingRecordRepository(uow.session)
                
                # 如果是新增，Certify_No 會自動產生
                certify_no = None
                if self.certify_no.text().strip():
                    certify_no = int(self.certify_no.text().strip())
                
                data = {
                    "EMP_ID": self.emp_id.currentText().strip(),
                    "Certify_ID": self.certify_id.currentText().strip(),
                    "Certify_date": self.certify_date.date().toString("yyyy-MM-dd"),
                    "Certify_type": self.certify_type.text().strip(),
                    "update_date": self.update_date.date().toString("yyyy-MM-dd"),
                    "Active": self.active.isChecked(),
                    "Remark": self.remark.text().strip()
                }
                
                repo.upsert(certify_no, data)
                
                QMessageBox.information(self, "成功", "證照記錄已儲存")
                self._load_data()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"儲存資料失敗:\n{str(e)}")
    
    def _on_delete(self):
        """刪除證照記錄"""
        certify_no = self.certify_no.text().strip()
        if not certify_no:
            QMessageBox.warning(self, "警告", "請先載入要刪除的證照記錄")
            return
        
        reply = QMessageBox.question(
            self,
            "確認刪除",
            f"確定要刪除證照記錄 {certify_no} 嗎?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                with UnitOfWork() as uow:
                    repo = TrainingRecordRepository(uow.session)
                    success = repo.delete(int(certify_no))
                    
                    if success:
                        QMessageBox.information(self, "成功", f"證照記錄 {certify_no} 已刪除")
                        self._clear_form()
                        self._load_data()
                    else:
                        QMessageBox.warning(self, "警告", "刪除失敗或記錄不存在")
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"刪除資料失敗:\n{str(e)}")
    
    def _clear_form(self):
        """清空表單"""
        self.certify_no.clear()
        self.emp_id.setCurrentIndex(0)
        self.certify_id.setCurrentIndex(0)
        self.certify_name.clear()
        self.certify_date.setDate(QDate.currentDate())
        self.certify_type.clear()
        self.update_date.setDate(QDate.currentDate())
        self.active.setChecked(True)
        self.remark.clear()
        self.expiry_alert.clear()
    
    def _export_excel(self):
        """匯出 Excel"""
        QMessageBox.information(self, "提示", "匯出功能開發中...")
