#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
測試 HRMS 應用程序啟動
簡短測試應用程序是否可以正常啟動
"""

import sys
import os

# 添加專案根目錄到 sys.path
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, PROJECT_ROOT)

def test_app_import():
    """測試應用程序導入"""
    print("測試應用程序模組導入...")
    try:
        from hrms.ui.qt.start_app import main as start_app_main
        print("✅ 主應用程式模組導入成功")
        return True
    except Exception as e:
        print(f"❌ 主應用程式模組導入失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_window_creation():
    """測試視窗創建"""
    print("\n測試視窗創建...")
    try:
        from PySide6.QtWidgets import QApplication
        from hrms.ui.qt.windows.start_page_new import StartPage
        
        # 創建 QApplication 實例（僅用於測試，不執行事件循環）
        app = QApplication.instance()
        if app is None:
            app = QApplication([])
        
        # 創建主視窗（不顯示）
        window = StartPage()
        print(f"✅ 主視窗創建成功: {window.windowTitle()}")
        print(f"✅ 視窗大小: {window.size().width()}x{window.size().height()}")
        
        # 測試一些子視窗
        windows_to_test = [
            ("hrms.ui.qt.windows.certify_management_window", "CertifyManagementWindow", "證照管理視窗"),
            ("hrms.ui.qt.windows.shop_window_new", "ShopWindow", "工站管理視窗"),
        ]
        
        for module_name, class_name, description in windows_to_test:
            try:
                module = __import__(module_name, fromlist=[class_name])
                window_class = getattr(module, class_name)
                # 只測試創建實例，不顯示
                window_instance = window_class()
                print(f"✅ {description} 創建成功")
                window_instance.close()
            except Exception as e:
                print(f"❌ {description} 創建失敗: {e}")
        
        window.close()
        return True
    except Exception as e:
        print(f"❌ 視窗創建測試失敗: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """主測試函數"""
    print("=" * 60)
    print("HRMS 應用程序啟動測試")
    print("=" * 60)
    print("")
    
    success = True
    
    # 測試1: 應用程序導入
    success &= test_app_import()
    
    # 測試2: 視窗創建
    success &= test_window_creation()
    
    print("")
    print("=" * 60)
    if success:
        print("✅ 所有啟動測試通過！應用程序可以正常啟動。")
        print("\n要啟動應用程序，請執行:")
        print("  python3 hrms/ui/qt/start_app.py")
    else:
        print("❌ 部分測試失敗，請檢查錯誤訊息。")
    print("=" * 60)
    
    return success

if __name__ == "__main__":
    import sys
    success = main()
    sys.exit(0 if success else 1)
