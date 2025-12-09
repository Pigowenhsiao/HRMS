#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
深度測試 HRMS UI 組件
測試所有 UI 窗口和組件的導入與基本功能
"""

import os
import sys
from pathlib import Path

# 設定環境
os.environ['QT_QPA_PLATFORM'] = 'offscreen'
sys.path.insert(0, str(Path(__file__).parent.parent))

def test_all_ui_components():
    """測試所有 UI 組件"""
    print("=" * 80)
    print("HRMS UI 組件深度測試")
    print("=" * 80)
    print()
    
    # 基礎 UI 模組
    base_modules = [
        ("PySide6.QtWidgets", "Qt Widgets"),
        ("PySide6.QtCore", "Qt Core"),
        ("PySide6.QtGui", "Qt GUI"),
    ]
    
    print("【基礎 Qt 模組測試】")
    for module_name, display_name in base_modules:
        try:
            module = __import__(module_name)
            print(f"  ✓ {display_name:30s} - 成功")
        except Exception as e:
            print(f"  ✗ {display_name:30s} - 失敗: {str(e)[:50]}")
    
    print()
    
    # 主窗口
    main_modules = [
        ("hrms.ui.qt.windows.start_page_new", "StartPage"),
    ]
    
    print("【主窗口模組測試】")
    for module_name, display_name in main_modules:
        try:
            module = __import__(module_name, fromlist=[display_name])
            print(f"  ✓ {display_name:30s} - 成功")
        except Exception as e:
            print(f"  ✗ {display_name:30s} - 失敗: {str(e)[:50]}")
    
    print()
    
    # 功能窗口
    ui_modules = [
        ("hrms.ui.qt.windows.basic_window_new", "BasicWindow"),
        ("hrms.ui.qt.windows.dept_window_new", "DeptWindow"),
        ("hrms.ui.qt.windows.area_window_new", "AreaWindow"),
        ("hrms.ui.qt.windows.job_window_new", "JobWindow"),
        ("hrms.ui.qt.windows.shift_window_new", "ShiftWindow"),
        ("hrms.ui.qt.windows.certify_items_window", "CertifyItemsWindow"),
        ("hrms.ui.qt.windows.certify_record_window", "CertifyRecordWindow"),
        ("hrms.ui.qt.windows.training_record_window", "TrainingRecordWindow"),
        ("hrms.ui.qt.windows.shop_window", "ShopWindow"),
        ("hrms.ui.qt.windows.certify_type_window", "CertifyTypeWindow"),
        ("hrms.ui.qt.windows.authority_window", "AuthorityWindow"),
        ("hrms.ui.qt.windows.vac_type_window", "VacTypeWindow"),
    ]
    
    print("【功能窗口模組測試】")
    failed_modules = []
    for module_name, display_name in ui_modules:
        try:
            module = __import__(module_name, fromlist=[display_name])
            print(f"  ✓ {display_name:30s} - 成功")
        except Exception as e:
            print(f"  ✗ {display_name:30s} - 失敗: {str(e)[:50]}")
            failed_modules.append((display_name, str(e)))
    
    print()
    print("=" * 80)
    print()
    
    # 統計結果
    total_modules = len(base_modules) + len(main_modules) + len(ui_modules)
    failed_count = len(failed_modules)
    success_count = total_modules - failed_count
    
    print(f"測試總結:")
    print(f"  總計測試: {total_modules} 個模組")
    print(f"  成功: {success_count} 個")
    print(f"  失敗: {failed_count} 個")
    
    if failed_modules:
        print()
        print("失敗的模組詳細資訊:")
        for name, error in failed_modules:
            print(f"  - {name}: {error[:100]}")
    
    print()
    print("=" * 80)
    
    return failed_count == 0

def test_window_instances():
    """測試窗口實例創建"""
    print("\n【窗口實例化測試】")
    print("-" * 80)
    
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    
    try:
        from PySide6.QtWidgets import QApplication
        import sys
        
        app = QApplication.instance() or QApplication(sys.argv)
        
        # 測試主窗口
        try:
            from hrms.ui.qt.windows.start_page_new import StartPage
            window = StartPage()
            print(f"  ✓ StartPage - 成功")
            print(f"    標題: {window.windowTitle()}")
            print(f"    大小: {window.size().width()}x{window.size().height()}")
            return True
        except Exception as e:
            print(f"  ✗ StartPage - 失敗: {str(e)}")
            return False
            
    except Exception as e:
        print(f"  ✗ 應用程序創建失敗: {str(e)}")
        return False

if __name__ == "__main__":
    print("HRMS UI 深度測試")
    print()
    
    try:
        # 測試所有模組
        modules_ok = test_all_ui_components()
        
        # 測試窗口實例
        window_ok = test_window_instances()
        
        print()
        print("最終結果:")
        if modules_ok and window_ok:
            print("✓ 所有測試通過")
            sys.exit(0)
        else:
            print("✗ 部分測試失敗")
            sys.exit(1)
            
    except Exception as e:
        print(f"測試執行失敗: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)