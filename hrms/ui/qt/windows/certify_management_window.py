# -*- coding: utf-8 -*-
"""
證照管理主選單視窗
整合所有證照相關功能
"""
from PySide6.QtWidgets import (
    QDialog, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QMessageBox, QGroupBox, QFrame
)
from PySide6.QtCore import Qt

from hrms.ui.qt.windows.certify_type_window_new import CertifyTypeWindow
from hrms.ui.qt.windows.certify_window_new import CertifyWindow
from hrms.ui.qt.windows.certify_items_window_new import CertifyItemsWindow
from hrms.ui.qt.windows.certify_record_window_new import CertifyRecordWindow
from hrms.ui.qt.windows.training_record_window_new import TrainingRecordWindow
from hrms.ui.qt.windows.certify_tool_map_window import CertifyToolMapWindow


class CertifyManagementWindow(QDialog):
    """證照管理主選單視窗"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("證照管理系統")
        self.resize(900, 600)
        
        self._init_ui()
    
    def _init_ui(self):
        """初始化 UI"""
        main_layout = QVBoxLayout(self)
        
        # 標題區域
        title_group = QGroupBox()
        title_layout = QVBoxLayout()
        
        title = QLabel("證照管理系統")
        title.setAlignment(Qt.AlignCenter)
        font = title.font()
        font.setPointSize(24)
        font.setBold(True)
        title.setFont(font)
        title_layout.addWidget(title)
        
        subtitle = QLabel("整合所有證照相關管理功能")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666; font-size: 14px;")
        title_layout.addWidget(subtitle)
        
        title_group.setLayout(title_layout)
        main_layout.addWidget(title_group)
        
        # 功能按鈕區域
        func_group = QGroupBox("功能選單")
        func_layout = QVBoxLayout()
        
        # 第一列 - 基礎資料維護
        row1 = QHBoxLayout()
        
        btn_certify_type = QPushButton("🏷️ 認證類型管理")
        btn_certify_type.clicked.connect(self._open_certify_type_window)
        btn_certify_type.setStyleSheet("font-size: 16px; padding: 20px; min-width: 200px;")
        row1.addWidget(btn_certify_type)
        
        btn_certify = QPushButton("📋 認證總表管理")
        btn_certify.clicked.connect(self._open_certify_window)
        btn_certify.setStyleSheet("font-size: 16px; padding: 20px; min-width: 200px;")
        row1.addWidget(btn_certify)
        
        btn_certify_items = QPushButton("📜 認證項目管理")
        btn_certify_items.clicked.connect(self._open_certify_items_window)
        btn_certify_items.setStyleSheet("font-size: 16px; padding: 20px; min-width: 200px;")
        row1.addWidget(btn_certify_items)
        
        row1.addStretch()
        func_layout.addLayout(row1)
        
        # 第二列 - 證照記錄管理
        row2 = QHBoxLayout()
        
        btn_training_records = QPushButton("📝 訓練記錄管理")
        btn_training_records.clicked.connect(self._open_training_record_window)
        btn_training_records.setMinimumSize(150, 60)
        row2.addWidget(btn_training_records)
        
        btn_certify_records = QPushButton("📊 認證記錄管理")
        btn_certify_records.clicked.connect(self._open_certify_record_window)
        btn_certify_records.setMinimumSize(150, 60)
        row2.addWidget(btn_certify_records)
        
        btn_tool_map = QPushButton("🔧 認證工具對應")
        btn_tool_map.clicked.connect(self._open_certify_tool_map_window)
        btn_tool_map.setMinimumSize(150, 60)
        row2.addWidget(btn_tool_map)
        
        row2.addStretch()
        func_layout.addLayout(row2)
        
        func_group.setLayout(func_layout)
        main_layout.addWidget(func_group)
        
        # 分隔線
        line = QFrame()
        line.setFrameShape(QFrame.HLine)
        line.setStyleSheet("background-color: #ccc;")
        main_layout.addWidget(line)
        
        # 說明區域
        help_group = QGroupBox("使用說明")
        help_layout = QVBoxLayout()
        
        help_text = QLabel(
            "本系統提供完整的證照管理功能，包含:\n\n"
            "• 基礎資料維護：管理認證類型、認證總表、認證項目\n"
            "• 記錄管理：管理員工的訓練記錄與認證記錄\n"
            "• 工具對應：建立認證與工具的對應關係\n\n"
            "請選擇上方功能按鈕進入對應的管理介面。"
        )
        help_text.setWordWrap(True)
        help_text.setStyleSheet("color: #666; font-size: 13px; line-height: 1.5;")
        help_layout.addWidget(help_text)
        
        help_group.setLayout(help_layout)
        main_layout.addWidget(help_group)
        
        # 關閉按鈕
        btn_close = QPushButton("關閉")
        btn_close.clicked.connect(self.accept)
        btn_close.setStyleSheet("font-size: 14px; padding: 10px; min-width: 100px;")
        
        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(btn_close)
        close_layout.addStretch()
        
        main_layout.addLayout(close_layout)
    
    def _open_certify_type_window(self):
        """開啟認證類型管理視窗"""
        try:
            window = CertifyTypeWindow(self)
            window.exec()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"無法開啟認證類型管理視窗:\n{str(e)}")
    
    def _open_certify_window(self):
        """開啟認證總表管理視窗"""
        try:
            window = CertifyWindow(self)
            window.exec()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"無法開啟認證總表管理視窗:\n{str(e)}")
    
    def _open_certify_items_window(self):
        """開啟認證項目管理視窗"""
        try:
            window = CertifyItemsWindow(self)
            window.exec()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"無法開啟認證項目管理視窗:\n{str(e)}")
    
    def _open_training_record_window(self):
        """開啟訓練記錄管理視窗"""
        try:
            window = TrainingRecordWindow(self)
            window.exec()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"無法開啟訓練記錄管理視窗:\n{str(e)}")
    
    def _open_certify_record_window(self):
        """開啟認證記錄管理視窗"""
        try:
            window = CertifyRecordWindow(self)
            window.exec()
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"無法開啟認證記錄管理視窗:\n{str(e)}")
    
    def _open_certify_tool_map_window(self):
        """開啟認證工具對應視窗"""
        try:
            QMessageBox.information(self, "提示", "認證工具對應功能開發中...")
        except Exception as e:
            QMessageBox.critical(self, "錯誤", f"錯誤:\n{str(e)}")
