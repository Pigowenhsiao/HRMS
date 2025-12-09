#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HRMS 應用程序最終測試報告
"""

import os
import sys
from pathlib import Path
from datetime import datetime

def main():
    project_root = Path(__file__).parent.parent
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    sys.path.insert(0, str(project_root))
    
    print("生成最終測試報告...")
    
    # 收集所有測試結果
    results = []
    
    # 測試 1: 數據庫
    try:
        import db
        from sqlalchemy import create_engine, inspect
        from config import settings
        
        engine = create_engine(settings.db_url)
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        
        results.append(("資料庫連接", True, f"{len(tables)} 個表格"))
    except Exception as e:
        results.append(("資料庫連接", False, str(e)))
    
    # 測試 2: Qt
    try:
        from PySide6 import QtCore, QtWidgets
        qt_version = QtCore.qVersion()
        results.append(("Qt 環境", True, f"版本 {qt_version}"))
    except Exception as e:
        results.append(("Qt 環境", False, str(e)))
    
    # 測試 3: 主窗口
    try:
        from PySide6.QtWidgets import QApplication
        from hrms.ui.qt.windows.start_page_new import StartPage
        
        app = QApplication.instance() or QApplication(sys.argv)
        window = StartPage()
        
        results.append(("主窗口", True, window.windowTitle()))
    except Exception as e:
        results.append(("主窗口", False, str(e)))
    
    # 測試 4: UI 模組
    try:
        ui_modules_count = 0
        ui_modules = [
            "hrms.ui.qt.windows.basic_window_new",
            "hrms.ui.qt.windows.dept_window_new",
            "hrms.ui.qt.windows.area_window_new",
            "hrms.ui.qt.windows.job_window_new",
        ]
        
        for module_name in ui_modules:
            __import__(module_name)
            ui_modules_count += 1
        
        results.append(("UI 模組", True, f"{ui_modules_count} 個模組"))
    except Exception as e:
        results.append(("UI 模組", False, str(e)))
    
    # 測試 5: Repository
    try:
        from repositories import BasicRepository, SectionRepository
        results.append(("Repository", True, "基本模組 OK"))
    except Exception as e:
        results.append(("Repository", False, str(e)))
    
    # 生成報告
    report = []
    report.append("=" * 80)
    report.append("HRMS 應用程序最終測試報告")
    report.append("=" * 80)
    report.append(f"生成時間: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append(f"Python版本: {sys.version}")
    report.append("=" * 80)
    report.append("")
    
    passed = 0
    failed = 0
    
    for test_name, success, message in results:
        status = "✓ 通過" if success else "✗ 失敗"
        report.append(f"{test_name:20s} {status}")
        report.append(f"  {message}")
        report.append("")
        
        if success:
            passed += 1
        else:
            failed += 1
    
    report.append("=" * 80)
    report.append(f"總計: {len(results)} 項測試")
    report.append(f"通過: {passed} 項")
    report.append(f"失敗: {failed} 項")
    report.append("")
    
    if failed == 0:
        report.append("✓ 所有測試通過！")
        report.append("")
        report.append("HRMS 應用程序可以正常啟動和運行")
        report.append("")
        report.append("啟動命令:")
        report.append("  python3 hrms/ui/qt/start_app.py")
    else:
        report.append("⚠ 部分測試失敗")
        report.append("請檢查相關模組的錯誤訊息")
    
    report.append("=" * 80)
    
    report_content = "\n".join(report)
    print(report_content)
    
    # 保存報告
    report_file = Path(__file__).parent / "application_test_report.txt"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)
    
    print(f"\n報告已保存至: {report_file}")
    
    return failed == 0

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)