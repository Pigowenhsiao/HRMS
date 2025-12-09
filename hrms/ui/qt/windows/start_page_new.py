# -*- coding: utf-8 -*-
"""
主選單（SQLite 版本）
"""
from PySide6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QMessageBox, QGroupBox, QFrame
)
from PySide6.QtCore import Qt

from hrms.ui.qt.windows.basic_window_new import BasicWindow
from hrms.ui.qt.windows.dept_window_new import DeptWindow
from hrms.ui.qt.windows.area_window_new import AreaWindow
from hrms.ui.qt.windows.job_window_new import JobWindow
from hrms.ui.qt.windows.certify_items_window import CertifyItemsWindow
from hrms.ui.qt.windows.certify_record_window import CertifyRecordWindow
from hrms.ui.qt.windows.training_record_window import TrainingRecordWindow
from hrms.ui.qt.windows.shop_window import ShopWindow
from hrms.ui.qt.windows.certify_type_window import CertifyTypeWindow
from hrms.ui.qt.windows.authority_window import AuthorityWindow
from hrms.ui.qt.windows.vac_type_window import VacTypeWindow
from hrms.ui.qt.windows.shift_window_new import ShiftWindow

try:
    from hrms.ui.qt.windows.basic_csv_window import BasicCSVWindow, LookupSpec
    CSV_MODE = True
except ImportError:
    CSV_MODE = False


class StartPage(QMainWindow):
    """主選單視窗"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("HRMS - 人力資源管理系統（SQLite 版）")
        self.resize(1000, 700)
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化 UI"""
        cw = QWidget(self)
        main_layout = QVBoxLayout(cw)
        
        # 標題區域
        title_group = QGroupBox()
        title_layout = QVBoxLayout()
        
        title = QLabel("人力資源管理系統")
        title.setAlignment(Qt.AlignCenter)
        font = title.font()
        font.setPointSize(24)
        font.setBold(True)
        title.setFont(font)
        title_layout.addWidget(title)
        
        subtitle = QLabel("HRMS - Human Resource Management System")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666; font-size: 14px;")
        title_layout.addWidget(subtitle)
        
        title_group.setLayout(title_layout)
        main_layout.addWidget(title_group)
        
        # 功能按鈕區域
        func_group = QGroupBox("功能選單")
        func_layout = QVBoxLayout()
        
        # 第一列 - 核心功能
        row1 = QHBoxLayout()
        
        btn_basic = QPushButton("👥 員工基本資料管理")
        btn_basic.clicked.connect(self._open_basic_window)
        btn_basic.setStyleSheet("font-size: 16px; padding: 20px; min-width: 200px;")
        row1.addWidget(btn_basic)
        
        btn_certify = QPushButton("📜 證照管理")
        btn_certify.clicked.connect(self._open_certify_window)
        btn_certify.setStyleSheet("font-size: 16px; padding: 20px; min-width: 200px;")
        row1.addWidget(btn_certify)
        
        row1.addStretch()
        func_layout.addLayout(row1)
        
        # 第二列 - 對照表維護
        row2 = QHBoxLayout()
        
        btn_dept = QPushButton("🏢 部門管理")
        btn_dept.clicked.connect(self._open_dept_window)
        btn_dept.setMinimumSize(150, 60)
        row2.addWidget(btn_dept)
        
        btn_area = QPushButton("🗺️ 區域管理")
        btn_area.clicked.connect(self._open_area_window)
        btn_area.setMinimumSize(150, 60)
        row2.addWidget(btn_area)
        
        btn_job = QPushButton("💼 職務管理")
        btn_job.clicked.connect(self._open_job_window)
        btn_job.setMinimumSize(150, 60)
        row2.addWidget(btn_job)
        
        btn_shift = QPushButton("⏰ 班別管理")
        btn_shift.clicked.connect(self._open_shift_window)
        btn_shift.setMinimumSize(150, 60)
        row2.addWidget(btn_shift)
        
        row2.addStretch()
        func_layout.addLayout(row2)
        
        # 第三列 - 其他功能
        row3 = QHBoxLayout()
        
        btn_shop = QPushButton("🏭 工站管理")
        btn_shop.clicked.connect(self._open_shop_window)
        btn_shop.setMinimumSize(150, 60)
        row3.addWidget(btn_shop)
        
        btn_vac = QPushButton("📝 假別管理")
        btn_vac.clicked.connect(self._open_vac_type_window)
        btn_vac.setMinimumSize(150, 60)
        row3.addWidget(btn_vac)
        
        btn_auth = QPushButton("🔐 權限管理")
        btn_auth.clicked.connect(self._open_authority_window)
        btn_auth.setMinimumSize(150, 60)
        row3.addWidget(btn_auth)
        
        row3.addStretch()
        func_layout.addLayout(row3)
        
        func_group.setLayout(func_layout)
        main_layout.addWidget(func_group)
        
        # 狀態列
        status_group = QGroupBox()
        status_layout = QHBoxLayout()
        
        db_info = QLabel("資料庫: SQLite | 資料檔: hrms.db")
        db_info.setStyleSheet("color: #666; font-size: 12px;")
        status_layout.addWidget(db_info)
        
        status_layout.addStretch()
        
        version = QLabel("版本: v1.0.0 (SQLite Edition)")
        version.setStyleSheet("color: #999; font-size: 12px;")
        status_layout.addWidget(version)
        
        status_group.setLayout(status_layout)
        main_layout.addWidget(status_group)
        
        self.setCentralWidget(cw)
    
    def _open_basic_window(self):
        """開啟員工資料視窗"""
        try:
            window = BasicWindow(self)
            window.exec()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"無法開啟員工資料視窗:\n{str(e)}")
    
    def _open_dept_window(self):
        """開啟部門管理視窗"""
        try:
            window = DeptWindow(self)
            window.exec()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"無法開啟部門管理視窗:\n{str(e)}")
    
    def _open_area_window(self):
        """開啟區域管理視窗"""
        try:
            window = AreaWindow(self)
            window.exec()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"無法開啟區域管理視窗:\n{str(e)}")
    
    def _open_job_window(self):
        """開啟職務管理視窗"""
        try:
            window = JobWindow(self)
            window.exec()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"無法開啟職務管理視窗:\n{str(e)}")
    
    def _open_certify_window(self):
        """開啟證照管理視窗"""
        try:
            # 這裡可以整合多個證照相關視窗
            QMessageBox.information(self, "提示", "證照管理功能開發中...")
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"錯誤:\n{str(e)}")
    
    def _open_shift_window(self):
        """開啟班別管理視窗"""
        try:
            QMessageBox.information(self, "提示", "班別管理功能開發中...")
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"錯誤:\n{str(e)}")
    
    def _open_shop_window(self):
        """開啟工站管理視窗"""
        try:
            QMessageBox.information(self, "提示", "工站管理功能開發中...")
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"錯誤:\n{str(e)}")
    
    def _open_vac_type_window(self):
        """開啟假別管理視窗"""
        try:
            QMessageBox.information(self, "提示", "假別管理功能開發中...")
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"錯誤:\n{str(e)}")
    
    def _open_authority_window(self):
        """開啟權限管理視窗"""
        try:
            QMessageBox.information(self, "提示", "權限管理功能開發中...")
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"錯誤:\n{str(e)}")


def main():
    """測試主選單"""
    from PySide6.QtWidgets import QApplication
    import sys
    
    app = QApplication(sys.argv)
    window = StartPage()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
