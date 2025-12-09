# -*- coding: utf-8 -*-
"""
員工基本資料管理視窗（SQLite 版本）
現代化 UI 設計，包含搜尋、分頁、資料驗證
"""
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QCheckBox,
    QPushButton, QMessageBox, QComboBox, QGroupBox, QLabel,
    QTableView, QHeaderView, QDateEdit
)
from PySide6.QtCore import Qt, QSortFilterProxyModel, QDate
from PySide6.QtGui import QStandardItemModel, QStandardItem
from typing import Optional, List

from hrms.core.db.unit_of_work_sqlite import UnitOfWork
from repositories import BasicRepository, LookupService
from domain.models import Basic


class BasicWindow(QDialog):
    """
    員工基本資料管理視窗
    功能：
    - 員工資料 CRUD
    - 即時搜尋（員工編號、姓名）
    - 分頁顯示（每頁 50 筆）
    - 資料驗證（必填欄位）
    """
    
    PAGE_SIZE = 50
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("員工基本資料管理（SQLite 版）")
        self.resize(1200, 800)
        
        self.current_page = 1
        self.total_records = 0
        self.search_filters = {}
        
        self._init_ui()
        self._load_data()
    
    def _init_ui(self):
        """初始化 UI"""
        main_layout = QVBoxLayout(self)
        
        # 搜尋區域
        search_group = self._create_search_group()
        main_layout.addWidget(search_group)
        
        # 資料表格區域
        table_group = self._create_table_group()
        main_layout.addWidget(table_group, 1)
        
        # 表單區域
        form_group = self._create_form_group()
        main_layout.addWidget(form_group)
        
        # 分頁控制區域
        pagination_group = self._create_pagination_group()
        main_layout.addWidget(pagination_group)
        
        # 載入表單區域的部門選項（因為表單區域剛初始化完成）
        if hasattr(self, 'dept'):
            self._load_dept_options_to_form()
    
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
        
        # 姓名
        layout.addWidget(QLabel("姓名:"))
        self.search_name = QLineEdit()
        self.search_name.setPlaceholderText("輸入姓名...")
        self.search_name.textChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_name)
        
        # 部門
        layout.addWidget(QLabel("部門:"))
        self.search_dept = QComboBox()
        self.search_dept.setEditable(True)
        self.search_dept.addItem("", "")
        self._load_dept_options()
        self.search_dept.currentTextChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_dept)
        
        # 在職狀態
        layout.addWidget(QLabel("狀態:"))
        self.search_active = QComboBox()
        self.search_active.addItems(["全部", "在職", "離職"])
        self.search_active.currentTextChanged.connect(self._on_search_changed)
        layout.addWidget(self.search_active)
        
        # 清除搜尋按鈕
        btn_clear = QPushButton("清除")
        btn_clear.clicked.connect(self._clear_search)
        layout.addWidget(btn_clear)
        
        layout.addStretch()
        group.setLayout(layout)
        return group
    
    def _create_table_group(self) -> QGroupBox:
        """建立表格區域"""
        group = QGroupBox("員工列表")
        layout = QVBoxLayout()
        
        # 工具列
        toolbar = QHBoxLayout()
        
        self.btn_refresh = QPushButton("🔄 刷新")
        self.btn_refresh.clicked.connect(self._load_data)
        toolbar.addWidget(self.btn_refresh)
        
        self.btn_export = QPushButton("📊 匯出 Excel")
        self.btn_export.clicked.connect(self._export_excel)
        toolbar.addWidget(self.btn_export)
        
        toolbar.addStretch()
        layout.addLayout(toolbar)
        
        # 資料表格
        self.table_model = QStandardItemModel()
        self.table_proxy = QSortFilterProxyModel()
        self.table_proxy.setSourceModel(self.table_model)
        
        self.table_view = QTableView()
        self.table_view.setModel(self.table_proxy)
        self.table_view.setSelectionBehavior(QTableView.SelectRows)
        self.table_view.setSelectionMode(QTableView.SingleSelection)
        self.table_view.setAlternatingRowColors(True)
        self.table_view.setSortingEnabled(True)
        self.table_view.doubleClicked.connect(self._on_table_double_click)
        
        # 設定表格標題
        self._setup_table_headers()
        
        layout.addWidget(self.table_view)
        
        # 狀態列
        self.status_bar = QHBoxLayout()
        self.lbl_status = QLabel("就緒")
        self.status_bar.addWidget(self.lbl_status)
        
        layout.addLayout(self.status_bar)
        group.setLayout(layout)
        return group
    
    def _create_form_group(self) -> QGroupBox:
        """建立表單區域"""
        group = QGroupBox("員工資料")
        layout = QFormLayout()
        
        # 第一行
        row1 = QHBoxLayout()
        self.emp_id = QLineEdit()
        self.emp_id.setMaxLength(10)
        row1.addWidget(self.emp_id)
        
        self.c_name = QLineEdit()
        self.c_name.setMaxLength(50)
        row1.addWidget(self.c_name)
        
        layout.addRow("員工編號*:", self.emp_id)
        layout.addRow("姓名*:", self.c_name)
        
        # 第二行
        self.dept = QComboBox()
        self.dept.setEditable(True)
        layout.addRow("部門*:", self.dept)
        
        # 第三行
        self.title = QLineEdit()
        layout.addRow("職稱:", self.title)
        
        # 第四行
        self.shift = QComboBox()
        self.shift.setEditable(True)
        layout.addRow("班別:", self.shift)
        
        # 第五行
        self.shop = QComboBox()
        self.shop.setEditable(True)
        layout.addRow("工站:", self.shop)
        
        # 第六行
        self.area = QComboBox()
        self.area.setEditable(True)
        layout.addRow("區域:", self.area)
        
        # 第七行
        self.function = QComboBox()
        self.function.setEditable(True)
        layout.addRow("職務:", self.function)
        
        # 第八行
        self.active = QCheckBox("在職")
        self.active.setChecked(True)
        layout.addRow("狀態:", self.active)
        
        # 第九行
        self.onboard_date = QDateEdit()
        self.onboard_date.setCalendarPopup(True)
        self.onboard_date.setDisplayFormat("yyyy-MM-dd")
        layout.addRow("到職日:", self.onboard_date)
        
        # 第十行
        self.meno = QLineEdit()
        layout.addRow("備註:", self.meno)
        
        # 按鈕區
        btn_layout = QHBoxLayout()
        
        self.btn_load = QPushButton("載入")
        self.btn_load.clicked.connect(self._on_load)
        btn_layout.addWidget(self.btn_load)
        
        self.btn_save = QPushButton("儲存")
        self.btn_save.clicked.connect(self._on_save)
        self.btn_save.setDefault(True)
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
        group.setLayout(layout)
        return group
    
    def _setup_table_headers(self):
        """設定表格標題"""
        headers = ["員工編號", "姓名", "部門", "職稱", "班別", "工站", "區域", "職務", "到職日", "狀態"]
        self.table_model.setHorizontalHeaderLabels(headers)
    
    def _load_data(self):
        """載入資料"""
        try:
            with UnitOfWork() as uow:
                repo = BasicRepository(uow.session)
                
                self.total_records = repo.count(filters=self.search_filters)
                
                total_pages = (self.total_records + self.PAGE_SIZE - 1) // self.PAGE_SIZE
                if total_pages == 0:
                    total_pages = 1
                
                if self.current_page > total_pages:
                    self.current_page = total_pages
                if self.current_page < 1:
                    self.current_page = 1
                
                offset = (self.current_page - 1) * self.PAGE_SIZE
                
                # 如果有姓名搜尋，使用特殊方法
                if self.search_name.text().strip():
                    employees = repo.search_by_name(
                        self.search_name.text().strip(),
                        only_active=(self.search_active.currentText() == "在職"),
                        limit=self.PAGE_SIZE
                    )
                else:
                    employees = repo.list(
                        filters=self.search_filters,
                        limit=self.PAGE_SIZE,
                        offset=offset
                    )
                
                self._update_table(employees)
                self._update_pagination_info()
                
                self.lbl_status.setText(f"顯示 {len(employees)} / {self.total_records} 筆資料")
                
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"載入資料失敗:\n{str(e)}")
    
    def _update_table(self, employees: List[Basic]):
        """更新表格資料"""
        self.table_model.removeRows(0, self.table_model.rowCount())
        
        for row, emp in enumerate(employees):
            self.table_model.insertRow(row)
            
            # 員工編號
            item = QStandardItem(emp.EMP_ID or "")
            item.setData(emp.EMP_ID)
            self.table_model.setItem(row, 0, item)
            
            # 姓名
            self.table_model.setItem(row, 1, QStandardItem(emp.C_Name or ""))
            
            # 部門
            self.table_model.setItem(row, 2, QStandardItem(emp.Dept_Code or ""))
            
            # 職稱
            self.table_model.setItem(row, 3, QStandardItem(emp.Title or ""))
            
            # 班別
            self.table_model.setItem(row, 4, QStandardItem(emp.SHIFT or ""))
            
            # 工站
            self.table_model.setItem(row, 5, QStandardItem(emp.Shop or ""))
            
            # 區域
            self.table_model.setItem(row, 6, QStandardItem(emp.Area or ""))
            
            # 職務
            self.table_model.setItem(row, 7, QStandardItem(emp.Function or ""))
            
            # 到職日
            self.table_model.setItem(row, 8, QStandardItem(emp.On_Board_Date or ""))
            
            # 狀態
            status = "在職" if emp.Active else "離職"
            self.table_model.setItem(row, 9, QStandardItem(status))
    
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
    
    def _load_dept_options(self):
        """載入部門選項"""
        try:
            with UnitOfWork() as uow:
                service = LookupService(uow.session)
                dept_codes = service.list_dept_codes()
                
                # 搜尋區域的部門下拉選單（一定存在）
                self.search_dept.clear()
                self.search_dept.addItem("", "")
                self.search_dept.addItems(dept_codes)
                
                # 表單區域的部門下拉選單（可能還沒初始化）
                if hasattr(self, 'dept'):
                    self.dept.clear()
                    self.dept.addItems(dept_codes)
        except Exception as e:
            QMessageBox.warning(self, "警告", f"載入部門選項失敗:\n{str(e)}")
    
    def _load_dept_options_to_form(self):
        """載入表單區域的部門選項（確保表單區域已初始化）"""
        try:
            with UnitOfWork() as uow:
                service = LookupService(uow.session)
                dept_codes = service.list_dept_codes()
                
                self.dept.clear()
                self.dept.addItems(dept_codes)
        except Exception as e:
            QMessageBox.warning(self, "警告", f"載入表單部門選項失敗:\n{str(e)}")
    
    def _on_search_changed(self):
        """搜尋條件變更時"""
        self.search_filters = {}
        
        if self.search_emp_id.text().strip():
            self.search_filters["EMP_ID"] = self.search_emp_id.text().strip()
        
        if self.search_dept.currentText():
            self.search_filters["Dept_Code"] = self.search_dept.currentText()
        
        if self.search_active.currentText() == "在職":
            self.search_filters["Active"] = True
        elif self.search_active.currentText() == "離職":
            self.search_filters["Active"] = False
        
        self.current_page = 1
        self._load_data()
    
    def _clear_search(self):
        """清除搜尋"""
        self.search_emp_id.clear()
        self.search_name.clear()
        self.search_dept.setCurrentIndex(0)
        self.search_active.setCurrentIndex(0)
        
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
    
    def _on_table_double_click(self, index):
        """表格雙擊"""
        source_index = self.table_proxy.mapToSource(index)
        emp_id_item = self.table_model.item(source_index.row(), 0)
        
        if emp_id_item:
            self._load_employee(emp_id_item.text())
    
    def _load_employee(self, emp_id: str):
        """載入員工資料"""
        try:
            with UnitOfWork() as uow:
                repo = BasicRepository(uow.session)
                employee = repo.get_by_pk(emp_id)
                
                if employee:
                    self.emp_id.setText(employee.EMP_ID or "")
                    self.c_name.setText(employee.C_Name or "")
                    
                    self.dept.setCurrentText(employee.Dept_Code or "")
                    self.shift.setCurrentText(employee.SHIFT or "")
                    self.shop.setCurrentText(employee.Shop or "")
                    self.area.setCurrentText(employee.Area or "")
                    self.function.setCurrentText(employee.Function or "")
                    
                    self.title.setText(employee.Title or "")
                    self.active.setChecked(employee.Active)
                    
                    if employee.On_Board_Date:
                        date = QDate.fromString(employee.On_Board_Date, "yyyy-MM-dd")
                        if not date.isValid():
                            date = QDate.fromString(employee.On_Board_Date, "yyyy/MM/dd")
                        self.onboard_date.setDate(date if date.isValid() else QDate.currentDate())
                    
                    self.meno.setText(employee.Meno or "")
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"載入員工資料失敗:\n{str(e)}")
    
    def _on_load(self):
        """載入按鈕"""
        emp_id = self.emp_id.text().strip()
        if not emp_id:
            QMessageBox.warning(self, "警告", "請輸入員工編號")
            return
        
        self._load_employee(emp_id)
    
    def _validate_form(self) -> bool:
        """表單驗證"""
        errors = []
        
        if not self.emp_id.text().strip():
            errors.append("員工編號不可空白")
        
        if not self.c_name.text().strip():
            errors.append("姓名不可空白")
        
        if not self.dept.currentText().strip():
            errors.append("部門不可空白")
        
        if errors:
            QMessageBox.warning(self, "資料驗證失敗", "\n".join(errors))
            return False
        
        return True
    
    def _on_save(self):
        """儲存按鈕"""
        if not self._validate_form():
            return
        
        try:
            with UnitOfWork() as uow:
                repo = BasicRepository(uow.session)
                
                emp_id = self.emp_id.text().strip()
                
                data = {
                    "EMP_ID": emp_id,
                    "C_Name": self.c_name.text().strip(),
                    "Dept_Code": self.dept.currentText().strip(),
                    "Title": self.title.text().strip(),
                    "SHIFT": self.shift.currentText().strip(),
                    "Shop": self.shop.currentText().strip(),
                    "Area": self.area.currentText().strip(),
                    "Function": self.function.currentText().strip(),
                    "Active": self.active.isChecked(),
                    "On_Board_Date": self.onboard_date.date().toString("yyyy-MM-dd"),
                    "Meno": self.meno.text().strip()
                }
                
                repo.upsert(emp_id, data)
                
                QMessageBox.information(self, "成功", "員工資料已儲存")
                self._load_data()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"儲存資料失敗:\n{str(e)}")
    
    def _on_delete(self):
        """刪除按鈕"""
        emp_id = self.emp_id.text().strip()
        if not emp_id:
            QMessageBox.warning(self, "警告", "請先載入要刪除的員工")
            return
        
        reply = QMessageBox.question(
            self,
            "確認刪除",
            f"確定要刪除員工 {emp_id} 嗎?\n此操作無法復原!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                with UnitOfWork() as uow:
                    repo = BasicRepository(uow.session)
                    success = repo.delete(emp_id)
                    
                    if success:
                        QMessageBox.information(self, "成功", f"員工 {emp_id} 已刪除")
                        self._clear_form()
                        self._load_data()
                    else:
                        QMessageBox.warning(self, "警告", "刪除失敗或員工不存在")
            except Exception as e:
                QMessageBox.critical(self, "錯誤", f"刪除資料失敗:\n{str(e)}")
    
    def _clear_form(self):
        """清空表單"""
        self.emp_id.clear()
        self.c_name.clear()
        self.title.clear()
        self.meno.clear()
        self.active.setChecked(True)
        self.dept.setCurrentIndex(0)
        self.shift.setCurrentIndex(0)
        self.shop.setCurrentIndex(0)
        self.area.setCurrentIndex(0)
        self.function.setCurrentIndex(0)
        self.onboard_date.setDate(QDate.currentDate())
    
    def _export_excel(self):
        """匯出 Excel"""
        try:
            from hrms.core.reporting.reports import df_to_excel
            import pandas as pd
            
            with UnitOfWork() as uow:
                repo = BasicRepository(uow.session)
                employees = repo.list(filters=self.search_filters)
                
                if not employees:
                    QMessageBox.warning(self, "警告", "沒有資料可匯出")
                    return
                
                # 轉換為 DataFrame
                data = []
                for emp in employees:
                    data.append({
                        "員工編號": emp.EMP_ID,
                        "姓名": emp.C_Name,
                        "部門": emp.Dept_Code,
                        "職稱": emp.Title,
                        "班別": emp.SHIFT,
                        "工站": emp.Shop,
                        "區域": emp.Area,
                        "職務": emp.Function,
                        "到職日": emp.On_Board_Date,
                        "狀態": "在職" if emp.Active else "離職",
                        "備註": emp.Meno or ""
                    })
                
                df = pd.DataFrame(data)
                
                # 匯出
                filename = f"employees_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
                df_to_excel(df, filename)
                
                QMessageBox.information(self, "成功", f"資料已匯出至:\n{filename}")
                
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"匯出失敗:\n{str(e)}")


# 測試函式
def test_basic_window():
    """測試視窗"""
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    window = BasicWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    test_basic_window()
